"""
Clase de Power-Ups
"""

from entities.base import Entity
from config.settings import *
from config.colors import *

class PowerUp(Entity):
    """Clase de power-up con método Monte Carlo"""
    
    def __init__(self, x, y, power_type):
        super().__init__(x, y, POWERUP_SIZE, POWERUP_SIZE, POWERUP_COLORS[power_type])
        self.power_type = power_type
        self.speed = POWERUP_SPEED
    
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