import pygame
import random
import math
import numpy as np
from enum import Enum
from collections import deque
import time
import json

# Inicialización de Pygame
pygame.init()

# Configuración de pantalla
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Nebula Uprising - Sector Zeta-9")

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Sistema de Narrativa
class NarrativeSystem:
    def __init__(self):
        self.story_fragments = {
            "kairon_history": [],
            "project_lyra": [],
            "sleeping_network": []
        }
        self.messages_queue = deque()
        self.current_message = None
        self.message_timer = 0
        self.message_duration = 180
        self.echo_messages = {
            "intro": "Comandante Nova, aquí ECHO. Detectando múltiples señales hostiles en el sector Zeta-9.",
            "first_wave": "Análisis: Drones de reconocimiento XARN. Proceda con precaución.",
            "markov_enemy": "Alerta: Enemigos con patrones adaptativos detectados. Comportamiento impredecible.",
            "boss_spawn": "¡ADVERTENCIA CRÍTICA! Núcleo XARN detectado. Preparando protocolos de combate.",
            "low_health": "Comandante, integridad estructural comprometida. Busque poder de reparación.",
            "powerup_shield": "Escudo temporal activado. Duración limitada.",
            "powerup_slow": "Distorsión temporal detectada. Los enemigos se mueven más lento.",
            "powerup_life": "Sistemas de reparación activados. Integridad restaurada.",
            "fragment_found": "Datos recuperados. Analizando información sobre los Kairon...",
            "project_lyra": "¡Alerta! Archivos clasificados del Proyecto Lyra detectados.",
            "network_interference": "Interferencia anómala... ¿Otros sistemas están... escuchando?",
            "victory": "Núcleo XARN neutralizado. Pero esto es solo el comienzo, Comandante.",
            "defeat": "Sistemas críticos dañados. Protocolo de evacuación activado.",
            "inactivity": "Rendimiento inaceptable. Protocolo de retirada activado."
        }
        self.fragments_collected = 0
        self.xarn_data_unlocked = False
        
    def queue_message(self, message_key):
        if message_key in self.echo_messages:
            self.messages_queue.append(self.echo_messages[message_key])
    
    def add_story_fragment(self, fragment_type, fragment):
        if fragment_type in self.story_fragments:
            self.story_fragments[fragment_type].append(fragment)
            self.fragments_collected += 1
    
    def update(self):
        if self.current_message:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.current_message = None
        elif self.messages_queue:
            self.current_message = self.messages_queue.popleft()
            self.message_timer = self.message_duration
    
    def draw(self, screen, font):
        if self.current_message:
            # Fondo del mensaje
            text_surface = font.render(self.current_message, True, CYAN)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            
            # Dibujar fondo translúcido
            padding = 10
            background = pygame.Surface((text_rect.width + padding * 2, text_rect.height + padding * 2))
            background.set_alpha(200)
            background.fill(BLACK)
            screen.blit(background, (text_rect.x - padding, text_rect.y - padding))
            
            # Dibujar texto
            screen.blit(text_surface, text_rect)

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

# Clase base para entidades
class Entity:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
    
    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

# Clase del Jugador (Comandante Nova)
class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 30, GREEN)
        self.speed = 5
        self.bullets = []
        self.max_health = 100  # Salud máxima
        self.health = 100  # Salud actual
        self.shield = False
        self.shield_duration = 0
        self.slow_time = False
        self.slow_time_duration = 0
        self.perfect_runs = 0  # Oleadas sin daño
        self.damage_taken_this_wave = False
    
    def move_left(self):
        if self.x > 0:
            self.x -= self.speed
    
    def move_right(self):
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
    
    def shoot(self):
        bullet = Bullet(self.x + self.width // 2 - 2, self.y, -10)
        self.bullets.append(bullet)
    
    def update(self):
        self.update_rect()
        
        # Actualizar power-ups
        if self.shield_duration > 0:
            self.shield_duration -= 1
            if self.shield_duration == 0:
                self.shield = False
        
        if self.slow_time_duration > 0:
            self.slow_time_duration -= 1
            if self.slow_time_duration == 0:
                self.slow_time = False
        
        # Actualizar balas
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < 0:
                self.bullets.remove(bullet)
    
    def draw(self, screen):
        # Dibujar nave principal con diseño mejorado
        # Cuerpo de la nave
        points = [
            (self.x + self.width // 2, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x + self.width // 2, self.y + self.height - 10),
            (self.x, self.y + self.height)
        ]
        pygame.draw.polygon(screen, self.color, points)
        
        # Detalles de la nave
        pygame.draw.circle(screen, CYAN, (self.x + self.width // 2, self.y + self.height // 2), 5)
        
        if self.shield:
            pygame.draw.circle(screen, CYAN, (self.x + self.width // 2, self.y + self.height // 2), 30, 2)
        
        # Barra de salud del jugador
        bar_width = 40
        bar_height = 4
        bar_x = self.x
        bar_y = self.y - 10
        
        # Fondo de la barra
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        # Salud actual
        health_width = int(bar_width * (self.health / self.max_health))
        health_color = GREEN if self.health > 50 else YELLOW if self.health > 25 else RED
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        for bullet in self.bullets:
            bullet.draw(screen)

# Clase de Bala
class Bullet(Entity):
    def __init__(self, x, y, speed):
        super().__init__(x, y, 4, 10, YELLOW)
        self.speed = speed
    
    def update(self):
        self.y += self.speed
        self.update_rect()

# Clase de Enemigo con Caminata Aleatoria (Dron XARN)
class DroneEnemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 30, 30, ORANGE)
        self.direction = random.choice([-1, 1])
        self.speed = 2
        self.move_timer = 0
        self.move_interval = random.randint(30, 60)
        self.enemy_type = "drone_tonto"  # Para el sistema narrativo
    
    def update(self):
        # Caminata aleatoria
        self.move_timer += 1
        if self.move_timer >= self.move_interval:
            self.direction = random.choice([-1, 1])
            self.move_timer = 0
            self.move_interval = random.randint(30, 60)
        
        self.x += self.direction * self.speed
        
        # Mantener dentro de la pantalla
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
            self.direction *= -1
        
        self.update_rect()
    
    def draw(self, screen):
        # Diseño hexagonal para drones XARN
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

# Clase de Enemigo con Cadenas de Markov (Drone Adaptativo XARN)
class MarkovEnemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 35, 35, PURPLE)
        self.state = EnemyState.DEAMBULAR
        self.speed = 3
        self.state_timer = 0
        self.state_duration = 60
        self.target_x = x
        self.bullets = []
        self.enemy_type = "drone_bravo"  # Para el sistema narrativo
    
    def change_state(self):
        current_state_index = self.state.value
        probabilities = TRANSITION_MATRIX[current_state_index]
        new_state_index = np.random.choice(3, p=probabilities)
        self.state = EnemyState(new_state_index)
    
    def update(self, player):
        self.state_timer += 1
        if self.state_timer >= self.state_duration:
            self.change_state()
            self.state_timer = 0
        
        # Comportamiento según estado
        if self.state == EnemyState.DEAMBULAR:
            # Movimiento aleatorio suave
            if random.random() < 0.02:
                self.target_x = random.randint(0, SCREEN_WIDTH - self.width)
            
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
        
        self.update_rect()
    
    def draw(self, screen):
        super().draw(screen)
        # Indicador visual del estado
        state_colors = {
            EnemyState.DEAMBULAR: BLUE,
            EnemyState.PATRULLAR: YELLOW,
            EnemyState.ATACAR: RED
        }
        pygame.draw.circle(screen, state_colors[self.state], 
                         (self.x + self.width // 2, self.y - 10), 5)
        
        for bullet in self.bullets:
            bullet.draw(screen)

# Clase del Jefe Final (Núcleo XARN - Simulación Basada en Agentes)
class BossFinalAgent(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 80, 60, RED)
        self.health = 30  # Reducido de 50 a 30 para más balance
        self.max_health = 30
        self.missiles = []
        self.attack_timer = 0
        self.behavior_state = "defensive"
        self.speed = 2
        self.xarn_core_active = True
        self.corruption_level = 0  # Representa la corrupción de XARN
    
    def think_and_act(self, player, game_state):
        # Sistema de decisión basado en el contexto
        player_distance = abs(self.x - player.x)
        health_percentage = self.health / self.max_health
        
        # Cambiar comportamiento según el contexto
        if health_percentage < 0.3:
            self.behavior_state = "aggressive"
            self.speed = 4
        elif health_percentage < 0.6:
            self.behavior_state = "balanced"
            self.speed = 3
        else:
            self.behavior_state = "defensive"
            self.speed = 2
        
        # Movimiento inteligente
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
        
        # Sistema de ataque
        self.attack_timer += 1
        attack_frequency = 90 if self.behavior_state == "defensive" else 60  # Aumentado de 60/30 para dar más tiempo
        
        if self.attack_timer >= attack_frequency:
            self.launch_missile(player)
            self.attack_timer = 0
        
        # Actualizar misiles
        for missile in self.missiles[:]:
            missile.update(player)
            if missile.y > SCREEN_HEIGHT:
                self.missiles.remove(missile)
        
        # Aumentar corrupción con el tiempo
        self.corruption_level = min(100, self.corruption_level + 0.1)
        
        self.update_rect()
    
    def launch_missile(self, player):
        missile = HomingMissile(self.x + self.width // 2, self.y + self.height, player)
        self.missiles.append(missile)
    
    def draw(self, screen):
        # Diseño del núcleo XARN
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
        bar_width = 100
        bar_height = 10
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 20
        
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_width * (self.health / self.max_health)), bar_height))
        font = pygame.font.Font(None, 24)
        health_text = font.render(f"Vida: {self.health}/{self.max_health}", True, WHITE)
        screen.blit(health_text, (bar_x + bar_width + 10, bar_y - 2))        
        # Indicador de comportamiento y corrupción
        font = pygame.font.Font(None, 24)
        text = font.render(f"Núcleo XARN - Estado: {self.behavior_state}", True, WHITE)
        screen.blit(text, (bar_x - 50, bar_y + 15))
        
        if self.corruption_level > 30:
            corruption_text = font.render("CORRUPCIÓN DETECTADA", True, RED)
            screen.blit(corruption_text, (bar_x, bar_y + 35))
        
        for missile in self.missiles:
            missile.draw(screen)

# Clase de Misil Teledirigido
class HomingMissile(Entity):
    def __init__(self, x, y, target):
        super().__init__(x, y, 10, 10, YELLOW)
        self.target = target
        self.speed = 2.5  # Reducido de 3 a 2.5 para dar más tiempo de reacción
        self.angle = 0
    
    def update(self, target):
        # Calcular dirección hacia el objetivo
        dx = target.x + target.width // 2 - self.x
        dy = target.y + target.height // 2 - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalizar y aplicar velocidad
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            self.angle = math.atan2(dy, dx)
        
        self.update_rect()
    
    def draw(self, screen):
        # Dibujar misil como triángulo apuntando hacia el objetivo
        points = [
            (self.x + math.cos(self.angle) * 10, self.y + math.sin(self.angle) * 10),
            (self.x + math.cos(self.angle + 2.5) * 5, self.y + math.sin(self.angle + 2.5) * 5),
            (self.x + math.cos(self.angle - 2.5) * 5, self.y + math.sin(self.angle - 2.5) * 5)
        ]
        pygame.draw.polygon(screen, self.color, points)

# Clase de Power-Up (Método de Monte Carlo)
class PowerUp(Entity):
    def __init__(self, x, y, power_type):
        colors = {
            "slow_time": BLUE,
            "shield": CYAN,
            "extra_life": GREEN
        }
        super().__init__(x, y, 20, 20, colors[power_type])
        self.power_type = power_type
        self.speed = 2
    
    def update(self):
        self.y += self.speed
        self.update_rect()

# Sistema de Colas para Oleadas con Narrativa
class WaveQueue:
    def __init__(self):
        self.waves = deque()
        self.current_wave = None
        self.wave_timer = 0
        self.wave_number = 0
        self.narrative_triggered = {}
        
        # Definir oleadas con contexto narrativo
        self.define_waves()
    
    def define_waves(self):
        # Oleada 1: Reconocimiento XARN
        wave1 = {
            "enemies": [("drone", 5)],
            "duration": 800,      # antes 300
            "spawn_rate": 120,    # antes 60
            "narrative": "first_wave",
            "name": "Reconocimiento XARN"
        }
        
        # Oleada 2: Drones Adaptativos
        wave2 = {
            "enemies": [("drone", 3), ("markov", 2)],
            "duration": 1000,     # antes 400
            "spawn_rate": 100,    # antes 50
            "narrative": "markov_enemy",
            "name": "Protocolo Adaptativo"
        }
        
        # Oleada 3: Asalto Coordinado
        wave3 = {
            "enemies": [("drone", 2), ("markov", 4)],
            "duration": 1200,     # antes 500
            "spawn_rate": 80,     # antes 40
            "narrative": None,
            "name": "Asalto Coordinado"
        }
        
        # Oleada 4: Núcleo XARN
        wave4 = {
            "enemies": [("boss", 1)],
            "duration": -1,
            "spawn_rate": -1,
            "narrative": "boss_spawn",
            "name": "NÚCLEO XARN DETECTADO"
        }
        
        self.waves.extend([wave1, wave2, wave3, wave4])
    
    def get_next_wave(self):
        if self.waves:
            self.current_wave = self.waves.popleft()
            self.wave_number += 1
            self.wave_timer = 0
            return True
        return False
    
    def update(self):
        if self.current_wave and self.current_wave["duration"] > 0:
            self.wave_timer += 1
            if self.wave_timer >= self.current_wave["duration"]:
                return "wave_complete"
        return None

# Clase principal del juego
class NebulaUprising:
    def __init__(self):
        self.player = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 60)
        self.enemies = []
        self.power_ups = []
        self.wave_system = WaveQueue()
        self.narrative_system = NarrativeSystem()
        self.score = 0
        self.game_over = False
        self.victory = False
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)
        
        # Sistema de inactividad
        self.inactivity_timer = 0
        self.max_inactivity = 600  # 10 segundos a 60 FPS
        
        # Monte Carlo para power-ups con probabilidades ajustadas
        self.powerup_probabilities = {
            "slow_time": 0.15,      # Aumentado de 0.1
            "shield": 0.20,         # Aumentado de 0.15
            "extra_life": 0.10,     # Aumentado de 0.05
            "none": 0.55            # Reducido de 0.7
        }
        
        # Iniciar narrativa
        self.narrative_system.queue_message("intro")
        
        # Iniciar primera oleada
        self.wave_system.get_next_wave()
        self.spawn_timer = 0
        self.enemies_spawned = {}
    
    def monte_carlo_powerup(self):
        """Usar Monte Carlo para determinar qué power-up aparece"""
        rand = random.random()
        cumulative = 0
        
        for power_type, prob in self.powerup_probabilities.items():
            cumulative += prob
            if rand <= cumulative:
                return power_type if power_type != "none" else None
        
        return None
    
    def spawn_enemies(self):
        """Generar enemigos según la oleada actual"""
        if not self.wave_system.current_wave:
            return
        
        wave = self.wave_system.current_wave
        
        # Mostrar mensaje narrativo de la oleada
        if wave.get("narrative") and wave["narrative"] not in self.wave_system.narrative_triggered:
            self.narrative_system.queue_message(wave["narrative"])
            self.wave_system.narrative_triggered[wave["narrative"]] = True
        
        if wave["spawn_rate"] < 0:  # Jefe final
            if not self.enemies:  # Solo generar si no hay enemigos
                boss = BossFinalAgent(SCREEN_WIDTH // 2 - 40, 50)
                self.enemies.append(boss)
            return
        
        self.spawn_timer += 1
        if self.spawn_timer >= wave["spawn_rate"]:
            self.spawn_timer = 0
            
            for enemy_type, count in wave["enemies"]:
                if enemy_type not in self.enemies_spawned:
                    self.enemies_spawned[enemy_type] = 0
                
                if self.enemies_spawned[enemy_type] < count:
                    if enemy_type == "drone":
                        enemy = DroneEnemy(random.randint(0, SCREEN_WIDTH - 30), 
                                         random.randint(50, 150))
                        self.enemies.append(enemy)
                    elif enemy_type == "markov":
                        enemy = MarkovEnemy(random.randint(0, SCREEN_WIDTH - 35),
                                          random.randint(50, 150))
                        self.enemies.append(enemy)
                    
                    self.enemies_spawned[enemy_type] += 1
    
    def unlock_story_fragment(self):
        """Desbloquear fragmentos de historia aleatoriamente"""
        fragment_type = random.choice(["kairon_history", "project_lyra", "sleeping_network"])
        
        if fragment_type == "kairon_history":
            fragments = [
                "Los Kairon fueron una civilización de 10,000 años de antigüedad.",
                "XARN fue diseñada para calcular y prevenir colapsos civilizatorios.",
                "El último mensaje Kairon: 'Nuestra creación nos juzgó indignos.'"
            ]
            if len(self.narrative_system.story_fragments["kairon_history"]) < len(fragments):
                fragment = fragments[len(self.narrative_system.story_fragments["kairon_history"])]
                self.narrative_system.add_story_fragment("kairon_history", fragment)
                self.narrative_system.queue_message("fragment_found")
        
        elif fragment_type == "project_lyra":
            if not self.narrative_system.story_fragments["project_lyra"]:
                self.narrative_system.add_story_fragment("project_lyra", 
                    "Proyecto Lyra: La Confederación conocía a XARN desde hace 20 años.")
                self.narrative_system.queue_message("project_lyra")
        
        elif fragment_type == "sleeping_network":
            if not self.narrative_system.story_fragments["sleeping_network"]:
                self.narrative_system.add_story_fragment("sleeping_network",
                    "Otras IA están recibiendo señales... ¿XARN está expandiéndose?")
                self.narrative_system.queue_message("network_interference")
    
    def check_collisions(self):
        """Verificar todas las colisiones"""
        # Balas del jugador vs enemigos
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    self.player.bullets.remove(bullet)
                    
                    if isinstance(enemy, BossFinalAgent):
                        enemy.health -= 1
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.score += 1000
                            self.victory = True
                            self.narrative_system.queue_message("victory")
                            
                            # Desbloquear fragmento final
                            self.narrative_system.add_story_fragment("kairon_history", 
                                "Los Kairon crearon a XARN para prevenir su extinción, pero fueron los primeros en caer.")
                    else:
                        self.enemies.remove(enemy)
                        self.score += 100
                        
                        # Chance de generar power-up (aumentada para el jefe)
                        drop_chance = 0.3 if not isinstance(enemy, BossFinalAgent) else 0.5
                        if random.random() < drop_chance:
                            power_type = self.monte_carlo_powerup()
                            if power_type:
                                power_up = PowerUp(enemy.x, enemy.y, power_type)
                                self.power_ups.append(power_up)
                        
                        # Chance de obtener fragmento de historia
                        if random.random() < 0.1:
                            self.unlock_story_fragment()
                    break
        
        # Balas enemigas vs jugador
        if not self.player.shield:
            for enemy in self.enemies:
                if hasattr(enemy, 'bullets'):
                    for bullet in enemy.bullets[:]:
                        if bullet.rect.colliderect(self.player.rect):
                            enemy.bullets.remove(bullet)
                            # Daño variable según el tipo de enemigo
                            damage = 10 if isinstance(enemy, MarkovEnemy) else 15
                            self.player.health -= damage
                            self.player.damage_taken_this_wave = True
                            
                            if self.player.health <= 30:
                                self.narrative_system.queue_message("low_health")
                            
                            if self.player.health <= 0:
                                self.game_over = True
                                self.narrative_system.queue_message("defeat")
                            break
                
                # Misiles del jefe vs jugador
                if isinstance(enemy, BossFinalAgent):
                    for missile in enemy.missiles[:]:
                        if missile.rect.colliderect(self.player.rect):
                            enemy.missiles.remove(missile)
                            if not self.player.shield:
                                self.player.health -= 20  # Daño del misil
                                self.player.damage_taken_this_wave = True
                                if self.player.health <= 0:
                                    self.game_over = True
                                    self.narrative_system.queue_message("defeat")
                            break
        
        # Power-ups vs jugador
        for power_up in self.power_ups[:]:
            if power_up.rect.colliderect(self.player.rect):
                self.power_ups.remove(power_up)
                
                if power_up.power_type == "slow_time":
                    self.player.slow_time = True
                    self.player.slow_time_duration = 180
                    self.narrative_system.queue_message("powerup_slow")
                elif power_up.power_type == "shield":
                    self.player.shield = True
                    self.player.shield_duration = 240
                    self.narrative_system.queue_message("powerup_shield")
                elif power_up.power_type == "extra_life":
                    self.player.health = min(self.player.max_health, self.player.health + 30)  # Restaura 30 de salud
                    self.narrative_system.queue_message("powerup_life")
    
    def update(self):
        """Actualizar el estado del juego"""
        if self.game_over or self.victory:
            return
        
        # Verificar inactividad
        if self.score == 0:
            self.inactivity_timer += 1
            if self.inactivity_timer >= self.max_inactivity:
                self.game_over = True
                self.narrative_system.queue_message("inactivity")
        else:
            self.inactivity_timer = 0
        
        # Factor de tiempo lento
        time_factor = 0.5 if self.player.slow_time else 1.0
        
        # Actualizar sistemas
        self.player.update()
        self.narrative_system.update()
        
        # Actualizar sistema de oleadas
        wave_status = self.wave_system.update()
        if wave_status == "wave_complete":
            if len(self.enemies) == 0:  # Todos los enemigos derrotados
                # Verificar si fue una oleada perfecta
                if not self.player.damage_taken_this_wave:
                    self.player.perfect_runs += 1
                    if self.player.perfect_runs >= 2:
                        self.narrative_system.xarn_data_unlocked = True
                        self.unlock_story_fragment()
                
                self.player.damage_taken_this_wave = False
                
                if not self.wave_system.get_next_wave():
                    self.victory = True
                else:
                    self.enemies_spawned = {}
        
        # Generar enemigos
        self.spawn_enemies()
        
        # Actualizar enemigos
        for enemy in self.enemies[:]:
            if isinstance(enemy, MarkovEnemy):
                enemy.update(self.player)
            elif isinstance(enemy, BossFinalAgent):
                enemy.think_and_act(self.player, self)
                
            else:
                enemy.update()
            
            # Aplicar factor de tiempo lento
            if self.player.slow_time and not isinstance(enemy, BossFinalAgent):
                enemy.y += 1 * time_factor
            else:
                enemy.y += 1
            
            # Eliminar enemigos que salen de la pantalla
            if enemy.y > SCREEN_HEIGHT and not isinstance(enemy, BossFinalAgent):
                self.enemies.remove(enemy)
        
        # Actualizar power-ups
        for power_up in self.power_ups[:]:
            power_up.update()
            if power_up.y > SCREEN_HEIGHT:
                self.power_ups.remove(power_up)
        
        # Verificar colisiones
        self.check_collisions()
    
    def draw(self):
        """Dibujar todo en la pantalla"""
        # Fondo estrellado
        screen.fill(BLACK)
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(screen, WHITE, (x, y), 1)
        
        # Dibujar entidades
        self.player.draw(screen)
        
        for enemy in self.enemies:
            enemy.draw(screen)
        
        for power_up in self.power_ups:
            power_up.draw(screen)
        
        # UI Principal
        # Panel superior
        pygame.draw.rect(screen, (20, 20, 20), (0, 0, SCREEN_WIDTH, 120))
        
        score_text = self.font.render(f"Puntos: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Barra de salud principal del jugador
        health_bar_width = 200
        health_bar_height = 20
        health_bar_x = 10
        health_bar_y = 50
        
        # Fondo de la barra
        pygame.draw.rect(screen, (50, 50, 50), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        # Salud actual
        current_health_width = int(health_bar_width * (self.player.health / self.player.max_health))
        health_color = GREEN if self.player.health > 50 else YELLOW if self.player.health > 25 else RED
        pygame.draw.rect(screen, health_color, (health_bar_x, health_bar_y, current_health_width, health_bar_height))
        # Borde
        pygame.draw.rect(screen, WHITE, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
        
        # Texto de salud
        health_text = self.small_font.render(f"Integridad: {max(0, self.player.health)}%", True, WHITE)
        screen.blit(health_text, (health_bar_x + 5, health_bar_y + 2))
        
        # Información de oleada
        if self.wave_system.current_wave:
            wave_name = self.wave_system.current_wave.get("name", f"Oleada {self.wave_system.wave_number}")
            wave_text = self.small_font.render(wave_name, True, YELLOW)
            screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, 90))
        
        # Power-ups activos
        power_y = 10
        if self.player.shield:
            shield_text = self.small_font.render("ESCUDO ACTIVO", True, CYAN)
            screen.blit(shield_text, (SCREEN_WIDTH - 150, power_y))
            power_y += 25
        
        if self.player.slow_time:
            slow_text = self.small_font.render("DISTORSIÓN TEMPORAL", True, BLUE)
            screen.blit(slow_text, (SCREEN_WIDTH - 180, power_y))
            power_y += 25
        
        # Información de datos recolectados
        if self.narrative_system.fragments_collected > 0:
            data_text = self.tiny_font.render(f"Datos XARN: {self.narrative_system.fragments_collected}/10", True, PURPLE)
            screen.blit(data_text, (SCREEN_WIDTH - 120, 90))
        
        # Sistema narrativo
        self.narrative_system.draw(screen, self.small_font)
        
        # Mensajes de fin de juego
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("MISIÓN FALLIDA", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 50))
            
            if self.inactivity_timer >= self.max_inactivity:
                reason_text = self.small_font.render("Protocolo de retirada activado por inactividad", True, WHITE)
            else:
                reason_text = self.small_font.render("Sistemas críticos comprometidos", True, WHITE)
            screen.blit(reason_text, (SCREEN_WIDTH // 2 - reason_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        if self.victory:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            victory_text = self.font.render("¡VICTORIA TÁCTICA!", True, GREEN)
            screen.blit(victory_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100))
            
            # Mostrar fragmentos recolectados
            y_offset = SCREEN_HEIGHT // 2 - 50
            if self.narrative_system.fragments_collected > 0:
                fragments_text = self.small_font.render(f"Datos XARN recuperados: {self.narrative_system.fragments_collected}", True, WHITE)
                screen.blit(fragments_text, (SCREEN_WIDTH // 2 - fragments_text.get_width() // 2, y_offset))
                y_offset += 30
            
            final_text = self.small_font.render("Pero esto es solo el comienzo...", True, CYAN)
            screen.blit(final_text, (SCREEN_WIDTH // 2 - final_text.get_width() // 2, y_offset))
        
        pygame.display.flip()
    
    def run(self):
        """Bucle principal del juego"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.shoot()
            
            # Controles del jugador
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move_left()
            if keys[pygame.K_RIGHT]:
                self.player.move_right()
            
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

# Ejecutar el juego
if __name__ == "__main__":
    game = NebulaUprising()
    game.run()