"""
Clases de enemigos
"""

import pygame
import random
import math
import numpy as np
from utils.random_loader import PseudoRandom
from enum import Enum
from entities.base import Entity
from entities.projectiles import Bullet, HomingMissile
from config.settings import *
from config.colors import *
import os

PRNG = PseudoRandom("nebula_uprising/data/pseudo_random_sequence.csv")
# Estados para Cadenas de Markov
class EnemyState(Enum):
    DEAMBULAR = 0
    PATRULLAR = 1
    ATACAR = 2

# Matriz de transición para Cadenas de Markov
TRANSITION_MATRIX = np.array([
    [0.7, 0.2, 0.1],  # Desde DEAMBULAR
    [0.3, 0.5, 0.2],  # Desde PATRULLAR
    [0.1, 0.3, 0.6]   # Desde ATACAR
])

class DroneEnemy(Entity):
    """Enemigo básico con caminata aleatoria (Dron XARN)"""
    
    def __init__(self, x, y):
        super().__init__(x, y, DRONE_SIZE, DRONE_SIZE, DRONE_COLOR)
        self.direction = PRNG.next_choice([-1, 1])
        self.speed = DRONE_SPEED
        self.move_timer = 0
        self.move_interval = int(30 + PRNG.next() * 30)
        self.enemy_type = "drone_tonto"
        # Estado actual del dron (solo deambular para el dron básico)
        self.current_state = "deambular"
        
        # Cargar imágenes para todos los estados
        self.images = {}
        self.load_images()
    
    def load_images(self):
        """Cargar las imágenes para todos los estados del dron"""
        image_paths = {
            "deambular": os.path.join("nebula_uprising", "assets", "images", "Drones", "Enemigo1.png"),
            "atacar": os.path.join("nebula_uprising", "assets", "images", "Drones", "Enemigo1Atacar.png"),
            "patrullar": os.path.join("nebula_uprising", "assets", "images", "Drones", "Enemigo1Patrullando.png")
        }
        
        for state, path in image_paths.items():
            try:
                image = pygame.image.load(path)
                # Escalar la imagen 80% más grande que el tamaño original del dron
                new_width = int(self.width * 3.0)
                new_height = int(self.height * 3.0)
                self.images[state] = pygame.transform.scale(image, (new_width, new_height))
            except pygame.error as e:
                print(f"No se pudo cargar la imagen {path}: {e}")
                self.images[state] = None
    
    def update(self):
        """Actualizar comportamiento del dron"""
        # Caminata aleatoria
        self.move_timer += 1
        if self.move_timer >= self.move_interval:
            self.direction = random.choice([-1, 1])
            self.move_timer = 0
            self.move_interval = random.randint(30, 60)
        
        self.x += self.direction * self.speed
        
        # Mantener dentro de la pantalla con margen de 50 píxeles
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
            self.direction *= -1
        
        super().update()
    
    def draw(self, screen):
        """Dibujar dron con imagen según su estado o diseño hexagonal como respaldo"""
        current_image = self.images.get(self.current_state)
        if current_image:
            # Centrar la imagen más grande en la posición original del dron
            image_rect = current_image.get_rect()
            image_rect.center = (self.x + self.width // 2, self.y + self.height // 2)
            screen.blit(current_image, image_rect)
        else:
            # Diseño hexagonal como respaldo si no se puede cargar la imagen
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            size = self.width // 2
            
            points = []
            for i in range(6):
                angle = math.pi / 3 * i
                x = center_x + size * math.cos(angle)
                y = center_y + size * math.sin(angle)
                points.append((x, y))
            
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, RED, points, 2)

class MarkovEnemy(Entity):
    """Enemigo con comportamiento basado en Cadenas de Markov"""
    
    def __init__(self, x, y):
        super().__init__(x, y, MARKOV_SIZE, MARKOV_SIZE, MARKOV_COLOR)
        self.state = EnemyState.DEAMBULAR
        self.speed = MARKOV_SPEED
        self.direction = random.choice([-1, 1])  # AGREGADO: atributo direction faltante
        self.state_timer = 0
        self.state_duration = 60
        self.target_x = x
        self.bullets = []
        self.enemy_type = "drone_bravo"
        
        # Cargar imágenes para todos los estados
        self.images = {}
        self.load_images()
    
    def load_images(self):
        """Cargar las imágenes para todos los estados del enemigo Markov"""
        image_paths = {
            EnemyState.DEAMBULAR: os.path.join("nebula_uprising", "assets", "images", "Drones", "Enemigo2.png"),
            EnemyState.ATACAR: os.path.join("nebula_uprising", "assets", "images", "Drones", "Enemigo2Atacar.png"),
            EnemyState.PATRULLAR: os.path.join("nebula_uprising", "assets", "images", "Drones", "Enemigo2Patrullando.png")
        }
        
        for state, path in image_paths.items():
            try:
                image = pygame.image.load(path)
                # Escalar la imagen 80% más grande que el tamaño original del enemigo
                new_width = int(self.width * 3.0)
                new_height = int(self.height * 3.0)
                self.images[state] = pygame.transform.scale(image, (new_width, new_height))
            except pygame.error as e:
                print(f"No se pudo cargar la imagen {path}: {e}")
                self.images[state] = None
    
    def change_state(self):
        """Cambiar estado usando matriz de transición"""
        current_state_index = self.state.value
        probabilities = TRANSITION_MATRIX[current_state_index]
        new_state_index = np.random.choice(3, p=probabilities)
        self.state = EnemyState(new_state_index)
    
    def update(self, player):
        """Actualizar comportamiento del enemigo Markov"""
        self.state_timer += 1
        if self.state_timer >= self.state_duration:
            self.change_state()
            self.state_timer = 0
        
        # Comportamiento según estado
        if self.state == EnemyState.DEAMBULAR:
            # Movimiento aleatorio suave con límites
            if random.random() < 0.02:
                MARGIN = 50
                self.target_x = random.randint(MARGIN, SCREEN_WIDTH - self.width - MARGIN)
            
            if abs(self.x - self.target_x) > 5:
                self.x += (self.target_x - self.x) * 0.05
        
        elif self.state == EnemyState.PATRULLAR:
            # Movimiento horizontal
            self.x += math.sin(self.state_timer * 0.05) * self.speed
            
        elif self.state == EnemyState.ATACAR:
            # Disparar hacia el jugador
            if self.state_timer % 30 == 0:
                bullet = Bullet(self.x + self.width // 2, self.y + self.height, 5)
                self.bullets.append(bullet)
        
        # Actualizar balas
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y > SCREEN_HEIGHT:
                self.bullets.remove(bullet)

        # Mantener dentro de los límites de la pantalla con margen
        if self.x <= 0:
            self.x = 0
            self.direction = 1
        elif self.x >= SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            self.direction = -1

        super().update()
        
    def draw(self, screen):
        """Dibujar enemigo Markov con imagen según su estado"""
        current_image = self.images.get(self.state)
        if current_image:
            # Centrar la imagen más grande en la posición original del enemigo
            image_rect = current_image.get_rect()
            image_rect.center = (self.x + self.width // 2, self.y + self.height // 2)
            screen.blit(current_image, image_rect)
        else:
            # Dibujar rectángulo como respaldo si no se puede cargar la imagen
            super().draw(screen)
        
        # Dibujar las balas
        for bullet in self.bullets:
            bullet.draw(screen)

class BossFinalAgent(Entity):
    """Jefe final con simulación basada en agentes"""
    
    def __init__(self, x, y):
        super().__init__(x, y, BOSS_WIDTH, BOSS_HEIGHT, BOSS_COLOR)
        self.health = BOSS_HEALTH
        self.max_health = BOSS_HEALTH
        self.missiles = []
        self.attack_timer = 0
        self.behavior_state = "defensive"
        self.speed = 2
        self.xarn_core_active = True
        self.corruption_level = 0
        # NUEVO: Lista de drones y temporizador
        self.spawned_drones = []
        self.drone_spawn_timer = 0
        self.drone_spawn_interval = 180  # cada 3 segundos aprox (60 FPS)
        
        # Cargar imagen del jefe final
        self.image = None
        self.load_image()

    def load_image(self):
        """Cargar la imagen del jefe final"""
        try:
            image_path = os.path.join("nebula_uprising", "assets", "images", "Drones", "FinalBoss.png")
            self.image = pygame.image.load(image_path)
            # Escalar la imagen 80% más grande que el tamaño original del jefe
            new_width = int(self.width * 5.0)
            new_height = int(self.height * 5.0)
            self.image = pygame.transform.scale(self.image, (new_width, new_height))
        except pygame.error as e:
            print(f"No se pudo cargar la imagen del BossFinalAgent: {e}")
            self.image = None

    def think_and_act(self, player, game_state):
        """Sistema de decisión basado en el contexto"""
        player_distance = abs(self.x - player.x)
        health_percentage = self.health / self.max_health
        
        #Verificar si el jefe llegó a la posición del jugador o muy abajo
        if self.y >= player.y - 50:  # Si el jefe está muy cerca o debajo del jugador
            # El jefe ha alcanzado las colonias - GAME OVER
            game_state.game_over = True
            game_state.narrative_system.queue_message("colony_breached")
            return
        
        # Verificar si el jefe está muy abajo en la pantalla
        if self.y >= SCREEN_HEIGHT - 150:
            # El jefe está peligrosamente cerca de las colonias
            game_state.game_over = True
            game_state.narrative_system.queue_message("colony_breached")
            return
        
        # Cambiar comportamiento según el contexto
        if health_percentage < 0.3:
            self.behavior_state = "aggressive"
            self.speed = 6
            # En modo agresivo, el jefe también avanza hacia abajo
            self.y += 0.5
        elif health_percentage < 0.6:
            self.behavior_state = "balanced"
            self.speed = 5
            # Avance moderado
            self.y += 0.3
        else:
            self.behavior_state = "defensive"
            self.speed = 3
            # Avance lento
            self.y += 0.1
        
        # Movimiento inteligente horizontal
        if self.behavior_state == "aggressive":
            # Perseguir al jugador
            if player.x < self.x:
                self.x -= self.speed
            else:
                self.x += self.speed
        elif self.behavior_state == "defensive":
            # Mantener distancia
            if player_distance < 200:
                if player.x < self.x:
                    self.x += self.speed
                else:
                    self.x -= self.speed
                    
        # Limitar posición del jefe dentro de la pantalla
        MARGIN = 30 
        self.x = max(MARGIN, min(self.x, SCREEN_WIDTH - self.width - MARGIN))
        
        # Sistema de ataque
        self.attack_timer += 1
        attack_frequency = 120 if self.behavior_state == "defensive" else 60
        
        if self.attack_timer >= attack_frequency:
            self.launch_missile(player)
            self.attack_timer = 0
        
        # Actualizar misiles
        for missile in self.missiles[:]:
            missile.update(player)
            if missile.y > SCREEN_HEIGHT:
                self.missiles.remove(missile)
        
        # NUEVO: Invocar drones cada cierto tiempo
        self.drone_spawn_timer += 1
        if self.drone_spawn_timer >= self.drone_spawn_interval:
            self.spawn_drone()
            self.drone_spawn_timer = 0

        # Actualizar drones invocados
        for drone in self.spawned_drones[:]:
            if isinstance(drone, MarkovEnemy):
                drone.update(player)
            else:
                drone.update()
            if drone.y > SCREEN_HEIGHT:
                self.spawned_drones.remove(drone)

        # Aumentar corrupción con el tiempo
        self.corruption_level = min(100, self.corruption_level + 0.1)
        
        super().update()
    
    def launch_missile(self, player):
        """Lanzar misil teledirigido"""
        missile = HomingMissile(self.x + self.width // 2, self.y + self.height, player)
        self.missiles.append(missile)
    
    def spawn_drone(self):
        """Invoca un dron aliado (básico o Markov) en una posición aleatoria cerca del jefe"""
        from entities.enemies import DroneEnemy, MarkovEnemy  # Importación local para evitar ciclos
        spawn_x = int(self.x + self.width // 2 + random.randint(-60, 60))
        spawn_x = max(0, min(spawn_x, SCREEN_WIDTH - DRONE_SIZE))
        spawn_y = int(self.y + self.height + 10)
        # 50% de probabilidad de invocar cada tipo
        if random.random() < 0.5:
            drone = DroneEnemy(spawn_x, spawn_y)
        else:
            drone = MarkovEnemy(spawn_x, spawn_y)
        self.spawned_drones.append(drone)
    
    def draw(self, screen):
        """Dibujar jefe final con imagen o diseño del núcleo XARN como respaldo"""
        if self.image:
            # Centrar la imagen más grande en la posición original del jefe
            image_rect = self.image.get_rect()
            image_rect.center = (self.x + self.width // 2, self.y + self.height // 2)
            screen.blit(self.image, image_rect)
        else:
            # Diseño del núcleo XARN como respaldo si no se puede cargar la imagen
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            
            # Núcleo central
            pygame.draw.circle(screen, self.color, (center_x, center_y), 30)
            pygame.draw.circle(screen, PURPLE, (center_x, center_y), 30, 3)
            
            # Anillos rotatorios
            angle = pygame.time.get_ticks() / 100
            for i in range(3):
                offset_x = math.cos(angle + i * 2.094) * 20
                offset_y = math.sin(angle + i * 2.094) * 20
                pygame.draw.circle(screen, ORANGE, (int(center_x + offset_x), int(center_y + offset_y)), 8)
        
        # Barra de vida
        self._draw_health_bar(screen)
        
        # Indicador de comportamiento y corrupción
        self._draw_status_text(screen)
        
        # Dibujar misiles
        for missile in self.missiles:
            missile.draw(screen)

        # Dibujar drones invocados
        for drone in self.spawned_drones:
            drone.draw(screen)
    
    def _draw_health_bar(self, screen):
        """Dibujar barra de vida del jefe"""
        bar_width = 100
        bar_height = 10
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 20
        
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_width * (self.health / self.max_health)), bar_height))
        
        font = pygame.font.Font(None, 24)
        health_text = font.render(f"Vida: {self.health}/{self.max_health}", True, WHITE)
        screen.blit(health_text, (bar_x + bar_width + 10, bar_y - 2))
    
    def _draw_status_text(self, screen):
        """Dibujar texto de estado del jefe"""
        font = pygame.font.Font(None, 24)
        bar_x = SCREEN_WIDTH // 2 - 50
        bar_y = 35
        
        text = font.render(f"Núcleo XARN - Estado: {self.behavior_state}", True, WHITE)
        screen.blit(text, (bar_x - 50, bar_y))
        
        if self.corruption_level > 30:
            corruption_text = font.render("CORRUPCIÓN DETECTADA", True, RED)
            screen.blit(corruption_text, (bar_x, bar_y + 20))
    
    def take_damage(self, damage=2):
        """Recibir daño"""
        self.health -= damage
        return self.health <= 0
