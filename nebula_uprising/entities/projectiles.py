"""
Clases de proyectiles (balas y misiles)
"""

import pygame
import math
from entities.base import Entity
from config.settings import *
from config.colors import *

class Bullet(Entity):
    """Clase de bala básica"""
    
    def __init__(self, x, y, speed):
        super().__init__(x, y, BULLET_WIDTH, BULLET_HEIGHT, BULLET_COLOR)
        self.speed = speed
    
    def update(self):
        """Actualizar posición de la bala"""
        self.y += self.speed
        super().update()

class HomingMissile(Entity):
    """Clase de misil teledirigido"""
    
    def __init__(self, x, y, target):
        super().__init__(x, y, 10, 10, BULLET_COLOR)
        self.target = target
        self.speed = MISSILE_SPEED
        self.angle = 0
    
    def update(self, target=None):
        """Actualizar posición del misil hacia el objetivo"""

        if target:
            self.target = target

        follow_distance = 250  # Distancia para dejar de seguir al objetivo

        if not hasattr(self, 'locked'):
            self.locked = False
        if not hasattr(self, 'locked_target_pos'):
            self.locked_target_pos = (0, 0)
        if not hasattr(self, 'locked_direction'):
            self.locked_direction = (0, 0)

        target_x = self.target.x + self.target.width // 2
        target_y = self.target.y + self.target.height // 2

        if not self.locked:
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance <= follow_distance:
                # Bloquear objetivo y dirección actual
                self.locked = True
                self.locked_target_pos = (target_x, target_y)
                self.locked_direction = (dx / distance, dy / distance)
            else:
                # Aún está persiguiendo
                self.locked_direction = (dx / distance, dy / distance)
        # Si ya está bloqueado, seguir la dirección fija
        dx, dy = self.locked_direction

        # Mover en dirección fija
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.angle = math.atan2(dy, dx)

        super().update()


    
    def draw(self, screen):
        """Dibujar misil como triángulo apuntando hacia el objetivo"""
        points = [
            (self.x + math.cos(self.angle) * 10, self.y + math.sin(self.angle) * 10),
            (self.x + math.cos(self.angle + 2.5) * 5, self.y + math.sin(self.angle + 2.5) * 5),
            (self.x + math.cos(self.angle - 2.5) * 5, self.y + math.sin(self.angle - 2.5) * 5)
        ]
        pygame.draw.polygon(screen, self.color, points)