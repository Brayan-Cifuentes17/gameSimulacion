"""
Clases de proyectiles (balas y misiles)
"""

import pygame
import math
import os
from entities.base import Entity
from config.settings import *
from config.colors import *

class Bullet(Entity):
    """Clase de bala básica"""
    
    def __init__(self, x, y, speed):
        super().__init__(x, y, BULLET_WIDTH, BULLET_HEIGHT, BULLET_COLOR)
        self.speed = speed

            # Cargar sprite del disparo
        image_path = os.path.join("nebula_uprising", "assets", "images", "Nave", "Disparo2.png")
        self.sprite = pygame.image.load(image_path).convert_alpha()

        # Escalar sprite si es necesario (ajústalo a lo que se vea bien en pantalla)
        self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
    
    def update(self):
        """Actualizar posición de la bala"""
        self.y += self.speed
        super().update()
        
    def draw(self, screen):
     screen.blit(self.sprite, (self.x, self.y))


class HomingMissile(Entity):
      """Clase de misil teledirigido"""
    
      def __init__(self, x, y, target):
            super().__init__(x, y, 10, 10, BULLET_COLOR)
            self.target = target
            self.speed = MISSILE_SPEED
            self.angle = 0

            # ✅ Cargar el sprite
            image_path = os.path.join("nebula_uprising", "assets", "images", "Nave", "Disparo2.png")
            self.sprite = pygame.image.load(image_path).convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))

            # Inicializar atributos de seguimiento
            self.locked = False
            self.locked_target_pos = (0, 0)
            self.locked_direction = (0, 0)
        
      def update(self, target=None):
            """Actualizar posición del misil hacia el objetivo"""
            if target:
                self.target = target

            follow_distance = 250
            target_x = self.target.x + self.target.width // 2
            target_y = self.target.y + self.target.height // 2

            if not self.locked:
                dx = target_x - self.x
                dy = target_y - self.y
                distance = math.sqrt(dx**2 + dy**2)

                if distance <= follow_distance:
                    self.locked = True
                    self.locked_target_pos = (target_x, target_y)
                    self.locked_direction = (dx / distance, dy / distance)
                else:
                    self.locked_direction = (dx / distance, dy / distance)

            dx, dy = self.locked_direction
            self.x += dx * self.speed
            self.y += dy * self.speed
            self.angle = math.atan2(dy, dx)

            super().update()
        
      def draw(self, screen):
            """Dibujar el misil como sprite"""
            screen.blit(self.sprite, (self.x, self.y))
    
    #    """Dibujar misil como triángulo apuntando hacia el objetivo"""
     #   points = [
      #      (self.x + math.cos(self.angle) * 10, self.y + math.sin(self.angle) * 10),
       #     (self.x + math.cos(self.angle + 2.5) * 5, self.y + math.sin(self.angle + 2.5) * 5),
        #    (self.x + math.cos(self.angle - 2.5) * 5, self.y + math.sin(self.angle - 2.5) * 5)
        #]
        #pygame.draw.polygon(screen, self.color, points)