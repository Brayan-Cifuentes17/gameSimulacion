import pygame

class Entity:
    """Clase base para todas las entidades del juego"""

    def __init__(self, x, y, width, height, color=None, image=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.image = None  # 🔧 Inicializar siempre

        # Si se proporciona imagen, se escala y se asigna
        if image is not None:
            self.image = pygame.transform.scale(image, (width, height))

        # Crear el rectángulo de colisión
        self.rect = pygame.Rect(x, y, width, height)
        if self.image:
            self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        """Dibujar la entidad en pantalla"""
        if self.image:
            screen.blit(self.image, self.rect)
        elif self.color is not None:
            pygame.draw.rect(screen, self.color, self.rect)

    def update_rect(self):
        """Actualizar el rectángulo de colisión"""
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if self.image:
            self.rect.topleft = (self.x, self.y)

    def update(self):
        """Actualizar la entidad (puede ser extendida)"""
        self.update_rect()
