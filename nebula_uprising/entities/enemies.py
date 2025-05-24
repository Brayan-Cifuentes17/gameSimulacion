"""
Clases de enemigos
"""

import pygame
import random
import math
import numpy as np
from enum import Enum
from entities.base import Entity
from entities.projectiles import Bullet, HomingMissile
from config.settings import *
from config.colors import *

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
        self.direction = random.choice([-1, 1])
        self.speed = DRONE_SPEED
        self.move_timer = 0
        self.move_interval = random.randint(30, 60)
        self.enemy_type = "drone_tonto"
    
    def update(self):
        """Actualizar comportamiento del dron"""
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
        
        super().update()
    
    def draw(self, screen):
        """Dibujar dron con diseño hexagonal"""
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
        self.state_timer = 0
        self.state_duration = 60
        self.target_x = x
        self.bullets = []
        self.enemy_type = "drone_bravo"
    
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
        
        super().update()
    
    def draw(self, screen):
        """Dibujar enemigo Markov con indicador de estado"""
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
    
    def think_and_act(self, player, game_state):
        """Sistema de decisión basado en el contexto"""
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
                    
        #Limitar posicion del jefe dentro de la pantalla
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        
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
        
        # Aumentar corrupción con el tiempo
        self.corruption_level = min(100, self.corruption_level + 0.1)
        
        super().update()
    
    def launch_missile(self, player):
        """Lanzar misil teledirigido"""
        missile = HomingMissile(self.x + self.width // 2, self.y + self.height, player)
        self.missiles.append(missile)
    
    def draw(self, screen):
        """Dibujar jefe final con diseño del núcleo XARN"""
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
    
    def take_damage(self, damage=1):
        """Recibir daño"""
        self.health -= damage
        return self.health <= 0