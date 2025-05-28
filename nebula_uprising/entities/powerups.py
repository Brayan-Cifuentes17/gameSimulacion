"""
Clase de Power-Ups
"""

import pygame
from entities.base import Entity
from config.settings import *
from config.colors import *
import os

class PowerUp(Entity):
    """Clase de power-up con método Monte Carlo"""
    
    def __init__(self, x, y, power_type):
        self.power_type = power_type
        self.speed = POWERUP_SPEED

         # Ruta y carga del sprite (dentro del constructor)
        image_path = {
            "shield": os.path.join("nebula_uprising", "assets", "images", "PowerUps", "ArmorBonus.png"),
            "extra_life": os.path.join("nebula_uprising", "assets", "images", "PowerUps", "HP_Bonus.png"),
            "slow_time": os.path.join("nebula_uprising", "assets", "images", "PowerUps", "SlowMotion.png")
        }

        image = pygame.image.load(image_path[power_type]).convert_alpha()
        image = pygame.transform.scale(image, (POWERUP_SIZE, POWERUP_SIZE))

        # Llama al constructor base con la imagen
        super().__init__(x, y, POWERUP_SIZE, POWERUP_SIZE, image=image)
    
    def update(self):
        """Actualizar posición del power-up"""
        self.y += self.speed
        super().update()
    
    def apply_effect(self, player, narrative_system):
        """Aplicar efecto del power-up al jugador"""
        if self.power_type == "slow_time":
            player.activate_slow_time()
            narrative_system.queue_message("powerup_slow")
        elif self.power_type == "shield":
            player.activate_shield()
            narrative_system.queue_message("powerup_shield")
        elif self.power_type == "extra_life":
            player.heal(30)
            narrative_system.queue_message("powerup_life")