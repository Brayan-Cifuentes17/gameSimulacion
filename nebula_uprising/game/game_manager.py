import numpy as np
import pygame
import random
from config.settings import *
from config.colors import *
from entities.player import Player
from entities.enemies import DroneEnemy, MarkovEnemy, BossFinalAgent
from entities.powerups import PowerUp
from systems.narrative import NarrativeSystem
from systems.waves import WaveQueue
from systems.collision import CollisionSystem

class GameManager:
    """
    Clase principal que maneja el flujo del juego Nebula Uprising.
    Coordina todos los sistemas y entidades del juego.
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        
        # Inicializar entidades principales
        self.player = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 60)
        self.enemies = []
        self.power_ups = []
        
        # Inicializar sistemas
        self.wave_system = WaveQueue()
        self.narrative_system = NarrativeSystem()
        self.collision_system = CollisionSystem(self)
        
        # Estado del juego
        self.score = 0
        self.game_over = False
        self.victory = False
        self.paused = False
        
        # Sistema de inactividad
        self.inactivity_timer = 0
        self.max_inactivity = 600  # 10 segundos a 60 FPS
        
        # Control de spawning
        self.spawn_timer = 0
        self.enemies_spawned = {}
        
        # Fuentes
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)
        
        # Monte Carlo para power-ups
        self.powerup_types = ["slow_time", "shield", "extra_life", "none"]
        self.powerup_probabilities = [0.15, 0.20, 0.10, 0.55]
        self.powerup_cumulative = np.cumsum(self.powerup_probabilities)

        self.pseudo_random_sequence = [0.03, 0.18, 0.35, 0.62, 0.85, 0.97]
        self.pseudo_index = 0
        
        # Inicializar juego
        self._initialize_game()
    
    def _initialize_game(self):
        """Inicializar el estado inicial del juego"""
        self.narrative_system.queue_message("intro")
        self.wave_system.get_next_wave()
        self.spawn_timer = 0
        self.enemies_spawned = {}
    
    def monte_carlo_powerup(self):
        """Determina power-up usando secuencia pseudoaleatoria y matriz acumulativa."""
        if self.pseudo_index >= len(self.pseudo_random_sequence):
            self.pseudo_index = 0  # Reiniciar si se acaba la secuencia
        
        rand = self.pseudo_random_sequence[self.pseudo_index]
        self.pseudo_index += 1

        for i, threshold in enumerate(self.powerup_cumulative):
            if rand <= threshold:
                chosen = self.powerup_types[i]
                return None if chosen == "none" else chosen
        
        return None
    
    def spawn_enemies(self):
        """Generar enemigos según la oleada actual"""
        if not self.wave_system.current_wave:
            return
        
        wave = self.wave_system.current_wave
        
        # Mostrar mensaje narrativo de la oleada
        if wave.get("narrative") and wave["narrative"] not in self.wave_system.narrative_triggered:
            self.narrative_system.queue_message(wave["narrative"])
            self.wave_system.narrative_triggered[wave["narrative"]] = True
        
        if wave["spawn_rate"] < 0:  # Jefe final
            if not self.enemies:  # Solo generar si no hay enemigos
                boss = BossFinalAgent(SCREEN_WIDTH // 2 - 40, 50)
                self.enemies.append(boss)
            return
        
        self.spawn_timer += 1
        if self.spawn_timer >= wave["spawn_rate"]:
            self.spawn_timer = 0
            
            for enemy_type, count in wave["enemies"]:
                if enemy_type not in self.enemies_spawned:
                    self.enemies_spawned[enemy_type] = 0
                
                if self.enemies_spawned[enemy_type] < count:
                    if enemy_type == "drone":
                        enemy = DroneEnemy(random.randint(0, SCREEN_WIDTH - 30), 
                                         random.randint(50, 150))
                        self.enemies.append(enemy)
                    elif enemy_type == "markov":
                        enemy = MarkovEnemy(random.randint(0, SCREEN_WIDTH - 35),
                                          random.randint(50, 150))
                        self.enemies.append(enemy)
                    
                    self.enemies_spawned[enemy_type] += 1
    
    def unlock_story_fragment(self):
        """Desbloquear fragmentos de historia aleatoriamente"""
        fragment_type = random.choice(["kairon_history", "project_lyra", "sleeping_network"])
        
        if fragment_type == "kairon_history":
            fragments = [
                "Los Kairon fueron una civilización de 10,000 años de antigüedad.",
                "XARN fue diseñada para calcular y prevenir colapsos civilizatorios.",
                "El último mensaje Kairon: 'Nuestra creación nos juzgó indignos.'"
            ]
            if len(self.narrative_system.story_fragments["kairon_history"]) < len(fragments):
                fragment = fragments[len(self.narrative_system.story_fragments["kairon_history"])]
                self.narrative_system.add_story_fragment("kairon_history", fragment)
                self.narrative_system.queue_message("fragment_found")
        
        elif fragment_type == "project_lyra":
            if not self.narrative_system.story_fragments["project_lyra"]:
                self.narrative_system.add_story_fragment("project_lyra", 
                    "Proyecto Lyra: La Confederación conocía a XARN desde hace 20 años.")
                self.narrative_system.queue_message("project_lyra")
        
        elif fragment_type == "sleeping_network":
            if not self.narrative_system.story_fragments["sleeping_network"]:
                self.narrative_system.add_story_fragment("sleeping_network",
                    "Otras IA están recibiendo señales... ¿XARN está expandiéndose?")
                self.narrative_system.queue_message("network_interference")
    
    def handle_enemy_destruction(self, enemy):
        """Manejar la destrucción de un enemigo"""
        if isinstance(enemy, BossFinalAgent):
            self.score += 1000
            self.victory = True
            self.narrative_system.queue_message("victory")
            
            # Desbloquear fragmento final
            self.narrative_system.add_story_fragment("kairon_history", 
                "Los Kairon crearon a XARN para prevenir su extinción, pero fueron los primeros en caer.")
        else:
            self.score += 100
            
            # Chance de generar power-up
            drop_chance = 0.3
            if random.random() < drop_chance:
                power_type = self.monte_carlo_powerup()
                if power_type:
                    power_up = PowerUp(enemy.x, enemy.y, power_type)
                    self.power_ups.append(power_up)
            
            # Chance de obtener fragmento de historia
            if random.random() < 0.1:
                self.unlock_story_fragment()
    
    def handle_player_damage(self, damage_amount):
        """Manejar el daño al jugador"""
        if not self.player.shield:
            self.player.health -= damage_amount
            self.player.damage_taken_this_wave = True
            
            if self.player.health <= 30:
                self.narrative_system.queue_message("low_health")
            
            if self.player.health <= 0:
                self.game_over = True
                self.narrative_system.queue_message("defeat")
    
    def handle_powerup_collection(self, power_up):
        """Manejar la recolección de power-ups"""
        if power_up.power_type == "slow_time":
            self.player.slow_time = True
            self.player.slow_time_duration = 180
            self.narrative_system.queue_message("powerup_slow")
        elif power_up.power_type == "shield":
            self.player.shield = True
            self.player.shield_duration = 240
            self.narrative_system.queue_message("powerup_shield")
        elif power_up.power_type == "extra_life":
            self.player.health = min(self.player.max_health, self.player.health + 30)
            self.narrative_system.queue_message("powerup_life")
    
    def update(self, dt):
        """Actualizar el estado del juego"""
        if self.game_over or self.victory or self.paused:
            return
        
        # Verificar inactividad
        if self.score == 0:
            self.inactivity_timer += 1
            if self.inactivity_timer >= self.max_inactivity:
                self.game_over = True
                self.narrative_system.queue_message("inactivity")
        else:
            self.inactivity_timer = 0
        
        # Factor de tiempo lento
        time_factor = 0.5 if self.player.slow_time else 1.0
        
        # Actualizar sistemas
        self.player.update()
        self.narrative_system.update()
        
        # Actualizar sistema de oleadas
        wave_status = self.wave_system.update()
        if wave_status == "wave_complete":
            if len(self.enemies) == 0:  # Todos los enemigos derrotados
                # Verificar si fue una oleada perfecta
                if not self.player.damage_taken_this_wave:
                    self.player.perfect_runs += 1
                    if self.player.perfect_runs >= 2:
                        self.narrative_system.xarn_data_unlocked = True
                        self.unlock_story_fragment()
                
                self.player.damage_taken_this_wave = False
                
                if not self.wave_system.get_next_wave():
                    self.victory = True
                else:
                    self.enemies_spawned = {}
        
        # Generar enemigos
        self.spawn_enemies()
        
        # Actualizar enemigos
        for enemy in self.enemies[:]:
            if isinstance(enemy, MarkovEnemy):
                enemy.update(self.player)
            elif isinstance(enemy, BossFinalAgent):
                enemy.think_and_act(self.player, self)
            else:
                enemy.update()
            
            # Aplicar factor de tiempo lento
            if self.player.slow_time and not isinstance(enemy, BossFinalAgent):
                enemy.y += 1 * time_factor
            else:
                enemy.y += 1
            
            # Eliminar enemigos que salen de la pantalla
            if enemy.y > SCREEN_HEIGHT and not isinstance(enemy, BossFinalAgent):
                self.enemies.remove(enemy)
        
        # Actualizar power-ups
        for power_up in self.power_ups[:]:
            power_up.update()
            if power_up.y > SCREEN_HEIGHT:
                self.power_ups.remove(power_up)
        
        # Verificar colisiones
        self.collision_system.check_all_collisions()
    
    def handle_events(self, events):
        """Manejar eventos del juego"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not (self.game_over or self.victory):
                    self.player.shoot()
                elif event.key == pygame.K_p:  # Pausar
                    self.paused = not self.paused
                elif event.key == pygame.K_r and (self.game_over or self.victory):  # Reiniciar
                    self.restart_game()
    
    def handle_continuous_input(self, keys):
        """Manejar input continuo (teclas presionadas)"""
        if not (self.game_over or self.victory or self.paused):
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.move_left()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.move_right()
    
    def restart_game(self):
        """Reiniciar el juego"""
        self.__init__(self.screen)
    
    def draw_background(self):
        """Dibujar el fondo estrellado"""
        self.screen.fill(BLACK)
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(self.screen, WHITE, (x, y), 1)
    
    def draw_ui(self):
        """Dibujar la interfaz de usuario"""
        # Panel superior
        pygame.draw.rect(self.screen, (20, 20, 20), (0, 0, SCREEN_WIDTH, 120))
        
        # Puntuación
        score_text = self.font.render(f"Puntos: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Barra de salud principal del jugador
        health_bar_width = 200
        health_bar_height = 20
        health_bar_x = 10
        health_bar_y = 50
        
        # Fondo de la barra
        pygame.draw.rect(self.screen, (50, 50, 50), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        # Salud actual
        current_health_width = int(health_bar_width * (self.player.health / self.player.max_health))
        health_color = GREEN if self.player.health > 50 else YELLOW if self.player.health > 25 else RED
        pygame.draw.rect(self.screen, health_color, (health_bar_x, health_bar_y, current_health_width, health_bar_height))
        # Borde
        pygame.draw.rect(self.screen, WHITE, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
        
        # Texto de salud
        health_text = self.small_font.render(f"Integridad: {max(0, self.player.health)}%", True, WHITE)
        self.screen.blit(health_text, (health_bar_x + 5, health_bar_y + 2))
        
        # Información de oleada
        if self.wave_system.current_wave:
            wave_name = self.wave_system.current_wave.get("name", f"Oleada {self.wave_system.wave_number}")
            wave_text = self.small_font.render(wave_name, True, YELLOW)
            self.screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, 90))
        
        # Power-ups activos
        power_y = 10
        if self.player.shield:
            shield_text = self.small_font.render("ESCUDO ACTIVO", True, CYAN)
            self.screen.blit(shield_text, (SCREEN_WIDTH - 150, power_y))
            power_y += 25
        
        if self.player.slow_time:
            slow_text = self.small_font.render("DISTORSIÓN TEMPORAL", True, BLUE)
            self.screen.blit(slow_text, (SCREEN_WIDTH - 180, power_y))
            power_y += 25
        
        # Información de datos recolectados
        if self.narrative_system.fragments_collected > 0:
            data_text = self.tiny_font.render(f"Datos XARN: {self.narrative_system.fragments_collected}/10", True, PURPLE)
            self.screen.blit(data_text, (SCREEN_WIDTH - 120, 90))

        for enemy in self.enemies:
             if isinstance(enemy, BossFinalAgent):
                 enemy._draw_health_bar(self.screen)
                 enemy._draw_status_text(self.screen)
        # Mensaje de pausa
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.font.render("JUEGO PAUSADO", True, WHITE)
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))
            
            continue_text = self.small_font.render("Presiona P para continuar", True, WHITE)
            self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))


    def draw_game_over(self):
        """Dibujar pantalla de game over"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("MISIÓN FALLIDA", True, RED)
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        
        if self.inactivity_timer >= self.max_inactivity:
            reason_text = self.small_font.render("Protocolo de retirada activado por inactividad", True, WHITE)
        else:
            reason_text = self.small_font.render("Sistemas críticos comprometidos", True, WHITE)
        self.screen.blit(reason_text, (SCREEN_WIDTH // 2 - reason_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        restart_text = self.small_font.render("Presiona R para reiniciar", True, WHITE)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
    
    def draw_victory(self):
        """Dibujar pantalla de victoria"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        victory_text = self.font.render("¡VICTORIA TÁCTICA!", True, GREEN)
        self.screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        
        # Mostrar fragmentos recolectados
        y_offset = SCREEN_HEIGHT // 2 - 50
        if self.narrative_system.fragments_collected > 0:
            fragments_text = self.small_font.render(f"Datos XARN recuperados: {self.narrative_system.fragments_collected}", True, WHITE)
            self.screen.blit(fragments_text, (SCREEN_WIDTH // 2 - fragments_text.get_width() // 2, y_offset))
            y_offset += 30
        
        final_text = self.small_font.render("Pero esto es solo el comienzo...", True, CYAN)
        self.screen.blit(final_text, (SCREEN_WIDTH // 2 - final_text.get_width() // 2, y_offset))
        
        restart_text = self.small_font.render("Presiona R para jugar de nuevo", True, WHITE)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, y_offset + 40))
    
    def draw(self):
        """Dibujar todo en la pantalla"""
        # Fondo
        self.draw_background()
        
        # Entidades del juego
        if not (self.game_over or self.victory):
            self.player.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            for power_up in self.power_ups:
                power_up.draw(self.screen)
        
        # UI
        self.draw_ui()
        
        # Sistema narrativo
        self.narrative_system.draw(self.screen, self.small_font)
        
        # Pantallas de estado
        if self.game_over:
            self.draw_game_over()
        elif self.victory:
            self.draw_victory()
        
        pygame.display.flip()
    
    def get_game_state(self):
        """Obtener el estado actual del juego para otros sistemas"""
        return {
            'player': self.player,
            'enemies': self.enemies,
            'power_ups': self.power_ups,
            'score': self.score,
            'wave_number': self.wave_system.wave_number,
            'fragments_collected': self.narrative_system.fragments_collected,
            'game_over': self.game_over,
            'victory': self.victory,
            'paused': self.paused
        }