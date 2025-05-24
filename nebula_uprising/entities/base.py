"""
Clase base para todas las entidades del juego
"""

import pygame

class Entity:
    """Clase base para todas las entidades del juego"""
    
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, screen):
        """Dibujar la entidad en pantalla"""
        pygame.draw.rect(screen, self.color, self.rect)
    
    def update_rect(self):
        """Actualizar el rectángulo de colisión"""
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self):
        """Actualizar la entidad (implementar en subclases)"""
        self.update_rect()