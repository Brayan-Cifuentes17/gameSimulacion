"""
Sistema de Colisiones - Nebula Uprising
Maneja todas las detecciones y resoluciones de colisiones
"""

import pygame
import random

class CollisionSystem:
    def __init__(self, game_instance):
        self.game = game_instance
    
    def check_all_collisions(self):
        """Verificar todas las colisiones del juego"""
        self.check_player_bullets_vs_enemies()
        self.check_enemy_projectiles_vs_player()
        self.check_powerups_vs_player()
    
    def check_player_bullets_vs_enemies(self):
        """Verificar colisiones entre balas del jugador y enemigos"""
        for bullet in self.game.player.bullets[:]:
            for enemy in self.game.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    self.game.player.bullets.remove(bullet)
                    self._handle_enemy_hit(enemy)
                    break
    
    def check_enemy_projectiles_vs_player(self):
        """Verificar colisiones entre proyectiles enemigos y el jugador"""
        if self.game.player.shield:
            return
        
        for enemy in self.game.enemies:
            # Verificar balas de enemigos regulares
            if hasattr(enemy, 'bullets'):
                for bullet in enemy.bullets[:]:
                    if bullet.rect.colliderect(self.game.player.rect):
                        enemy.bullets.remove(bullet)
                        damage = self._get_enemy_damage(enemy)
                        self._damage_player(damage)
                        break
            
            # Verificar misiles del jefe
            if hasattr(enemy, 'missiles'):
                for missile in enemy.missiles[:]:
                    if missile.rect.colliderect(self.game.player.rect):
                        enemy.missiles.remove(missile)
                        self._damage_player(20)  # Daño del misil
                        break
    
    def check_powerups_vs_player(self):
        """Verificar colisiones entre power-ups y el jugador"""
        for power_up in self.game.power_ups[:]:
            if power_up.rect.colliderect(self.game.player.rect):
                self.game.power_ups.remove(power_up)
                self._apply_powerup_effect(power_up)
    
    def _handle_enemy_hit(self, enemy):
        """Manejar cuando un enemigo es golpeado"""
        from entities.enemies import BossFinalAgent
        
        if isinstance(enemy, BossFinalAgent):
            enemy.health -= 5
            if enemy.health <= 0:
                self.game.enemies.remove(enemy)
                self.game.score += 1000
                self.game.victory = True
                self.game.narrative_system.queue_message("victory")
                
                # Desbloquear fragmento final
                self.game.narrative_system.add_story_fragment("kairon_history", 
                    "Los Kairon crearon a XARN para prevenir su extinción, pero fueron los primeros en caer.")
        else:
            self.game.enemies.remove(enemy)
            self.game.score += 100
            
            # Chance de generar power-up
            if random.random() < 0.3:
                power_type = self.game.monte_carlo_powerup()
                if power_type:
                    from entities.powerups import PowerUp
                    power_up = PowerUp(enemy.x, enemy.y, power_type)
                    self.game.power_ups.append(power_up)
            
            # Chance de obtener fragmento de historia
            if random.random() < 0.1:
                self.game.unlock_story_fragment()
    
    def _get_enemy_damage(self, enemy):
        """Obtener el daño que causa un enemigo"""
        from entities.enemies import MarkovEnemy
        return 10 if isinstance(enemy, MarkovEnemy) else 15
    
    def _damage_player(self, damage):
        """Aplicar daño al jugador"""
        self.game.player.health -= damage
        self.game.player.damage_taken_this_wave = True
        
        if self.game.player.health <= 30:
            self.game.narrative_system.queue_message("low_health")
        
        if self.game.player.health <= 0:
            self.game.game_over = True
            self.game.narrative_system.queue_message("defeat")
    
    def _apply_powerup_effect(self, power_up):
        """Aplicar el efecto de un power-up"""
        if power_up.power_type == "slow_time":
            self.game.player.slow_time = True
            self.game.player.slow_time_duration = 180
            self.game.narrative_system.queue_message("powerup_slow")
        elif power_up.power_type == "shield":
            self.game.player.shield = True
            self.game.player.shield_duration = 800
            self.game.narrative_system.queue_message("powerup_shield")
        elif power_up.power_type == "extra_life":
            self.game.player.health = min(self.game.player.max_health, 
                                        self.game.player.health + 30)
            self.game.narrative_system.queue_message("powerup_life")