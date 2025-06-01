"""
Clase del jugador (Comandante Nova)
"""

import pygame
import os
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

        # Cargar sprites
        self.sprite_idle = pygame.image.load(os.path.join("nebula_uprising", "assets", "images", "Nave", "Nave2.png")).convert_alpha()
        self.sprite_moving = pygame.image.load(os.path.join("nebula_uprising", "assets", "images", "Nave", "Nave2Movimiento.png")).convert_alpha()
        self.current_sprite = self.sprite_idle

        # Ajustar tamaño del sprite
        self.sprite_idle = pygame.transform.scale(self.sprite_idle, (self.width, self.height))
        self.sprite_moving = pygame.transform.scale(self.sprite_moving, (self.width, self.height))

        self.is_moving = False
        
        # Cargar sonidos
        try:
            self.shoot_sound = pygame.mixer.Sound(os.path.join("nebula_uprising", "assets", "Sonido", "DisparosSFX.mp3"))
            self.power_sound = pygame.mixer.Sound(os.path.join("nebula_uprising", "assets", "Sonido", "PoderSFX.mp3"))
            # Ajustar volúmenes
            self.shoot_sound.set_volume(0.3)  # Reducir volumen del disparo
            self.power_sound.set_volume(0.7)  # Volumen moderado para poderes
        except pygame.error as e:
            print(f"Error cargando sonidos: {e}")
            self.shoot_sound = None
            self.power_sound = None
    
    def move_left(self):
        """Mover jugador hacia la izquierda"""
        if self.x > 0:
            self.x -= self.speed
            self.is_moving = True
    
    def move_right(self):
        """Mover jugador hacia la derecha"""
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
            self.is_moving = True
    
    def shoot(self):
        """Disparar una bala"""
        bullet = Bullet(self.x + self.width // 2 - 2, self.y, -BULLET_SPEED)
        self.bullets.append(bullet)
        
        # Reproducir sonido de disparo
        if self.shoot_sound:
            self.shoot_sound.play()
    
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
        # Cambiar sprite si se está moviendo
        self.current_sprite = self.sprite_moving if self.is_moving else self.sprite_idle
        screen.blit(self.current_sprite, (self.x, self.y))

        self.is_moving = False
        
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
    
    def play_power_sound(self):
        """Reproducir sonido de poder (para uso externo)"""
        if self.power_sound:
            self.power_sound.play()
