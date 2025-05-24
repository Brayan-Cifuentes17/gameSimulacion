"""
Clase del jugador (Comandante Nova)
"""

import pygame
from entities.base import Entity
from entities.projectiles import Bullet
from config.settings import *
from config.colors import *

class Player(Entity):
    """Clase del jugador principal"""
    
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_COLOR)
        self.speed = PLAYER_SPEED
        self.bullets = []
        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_MAX_HEALTH
        self.shield = False
        self.shield_duration = 0
        self.slow_time = False
        self.slow_time_duration = 0
        self.perfect_runs = 0
        self.damage_taken_this_wave = False
    
    def move_left(self):
        """Mover jugador hacia la izquierda"""
        if self.x > 0:
            self.x -= self.speed
    
    def move_right(self):
        """Mover jugador hacia la derecha"""
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
    
    def shoot(self):
        """Disparar una bala"""
        bullet = Bullet(self.x + self.width // 2 - 2, self.y, -BULLET_SPEED)
        self.bullets.append(bullet)
    
    def update(self):
        """Actualizar estado del jugador"""
        super().update()
        
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
        """Dibujar jugador en pantalla"""
        # Dibujar nave con diseño mejorado
        points = [
            (self.x + self.width // 2, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x + self.width // 2, self.y + self.height - 10),
            (self.x, self.y + self.height)
        ]
        pygame.draw.polygon(screen, self.color, points)
        
        # Detalles de la nave
        pygame.draw.circle(screen, CYAN, (self.x + self.width // 2, self.y + self.height // 2), 5)
        
        # Escudo visual
        if self.shield:
            pygame.draw.circle(screen, CYAN, (self.x + self.width // 2, self.y + self.height // 2), 30, 2)
        
        # Barra de salud
        self._draw_health_bar(screen)
        
        # Dibujar balas
        for bullet in self.bullets:
            bullet.draw(screen)
    
    def _draw_health_bar(self, screen):
        """Dibujar barra de salud del jugador"""
        bar_width = 40
        bar_height = 4
        bar_x = self.x
        bar_y = self.y - 10
        
        # Fondo de la barra
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        
        # Salud actual
        health_width = int(bar_width * (self.health / self.max_health))
        if self.health > 50:
            health_color = GREEN
        elif self.health > 25:
            health_color = YELLOW
        else:
            health_color = RED
        
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
    
    def take_damage(self, damage):
        """Recibir daño"""
        if not self.shield:
            self.health -= damage
            self.damage_taken_this_wave = True
            return True
        return False
    
    def heal(self, amount):
        """Curar al jugador"""
        self.health = min(self.max_health, self.health + amount)
    
    def activate_shield(self):
        """Activar escudo"""
        self.shield = True
        self.shield_duration = SHIELD_DURATION
    
    def activate_slow_time(self):
        """Activar tiempo lento"""
        self.slow_time = True
        self.slow_time_duration = SLOW_TIME_DURATION