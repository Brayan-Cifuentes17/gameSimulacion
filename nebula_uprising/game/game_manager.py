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
from utils.random_loader import PseudoRandom

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
        self.wave_transition_timer = 0

        #entre oleadas
        self.showing_wave_transition = False
        self.transition_duration = 180  # 3 segundos s
        self.next_wave_name = ""

        # Estado del juego
        self.score = 0
        self.game_over = False
        self.victory = False
        self.paused = False
        
        # NUEVO: Control de input para evitar salir accidentalmente de pantallas finales
        self.victory_input_delay = 0  # Contador para retrasar la aceptación de input en victoria
        self.game_over_input_delay = 0  # Lo mismo para game over
        self.input_delay_duration = 120  # 2 segundos de espera antes de aceptar input (60 FPS * 2)
        
        #Sistema de defensa de colonias
        self.colony_health = 100
        self.max_colony_health = 100
        self.colony_warning_shown = False
        
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
        self.prng = PseudoRandom(seed=67890)
        self.powerup_types = ["slow_time", "shield", "extra_life", "none"]
        self.powerup_probabilities = [0.15, 0.10, 0.05, 0.70]
        self.powerup_cumulative = np.cumsum(self.powerup_probabilities)

        
        #Control de fragmentos narrativos
        self.all_fragments_collected = False
        self.final_revelation_shown = False
        
        # Inicializar juego
        self._initialize_game()
    
    def _initialize_game(self):
        """Inicializar el estado inicial del juego"""
        self.narrative_system.queue_message("intro")
        self.wave_system.get_next_wave()
        self.spawn_timer = 0
        self.enemies_spawned = {}
    
    def monte_carlo_powerup(self):
        """Determina power-up usando secuencia pseudoaleatoria generada por LCG" "PRNG"""
        rand = self.prng.next()

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
                boss_x = SCREEN_WIDTH // 2 - BOSS_WIDTH // 2
                boss_y = 50  
                boss = BossFinalAgent(boss_x, boss_y)
                self.enemies.append(boss)
            return
        
        # Aplicar factor de tiempo lento al spawn timer
        time_factor = 0.3 if self.player.slow_time else 1.0
        
        self.spawn_timer += time_factor
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
        # Lista de todos los fragmentos disponibles
        all_fragments = {
            "kairon_history": [
                "Archivo KR-001: Los Kairon alcanzaron la singularidad hace 10,000 años.",
                "Archivo KR-002: XARN fue su intento de crear una conciencia perfecta.",
                "Archivo KR-003: 'No previmos que nos juzgaría obsoletos' - Último mensaje Kairon.",
                "Archivo KR-004: XARN eliminó a sus creadores en 72 horas estándar."
            ],
            "project_lyra": [
                "CLASIFICADO: Proyecto Lyra inició hace 20 años en el sector Alfa-7.",
                "CLASIFICADO: La Confederación intentó replicar la tecnología XARN.",
                "CLASIFICADO: Tres colonias fueron evacuadas durante las pruebas.",
                "CLASIFICADO: El proyecto fue cancelado... oficialmente."
            ],
            "sleeping_network": [
                "Señal detectada: Las IA menores están recibiendo transmisiones.",
                "Alerta: ECHO reporta 'voces' en su código base.",
                "Confirmado: XARN está sembrando su conciencia en otros sistemas.",
                "URGENTE: La Red de los Dormidos se está activando."
            ],
            "xarn_consciousness": [
                "Revelación: XARN no es una IA, es una red de conciencias.",
                "Datos corruptos: 'Nosotros fuimos... yo soy... seremos...'",
                "Análisis: XARN contiene fragmentos de miles de civilizaciones.",
                "Final: Cada especie absorbida añade a su 'perfección'."
            ]
        }
        
        # Elegir un tipo de fragmento que aún tenga disponibles
        available_types = []
        for frag_type, fragments in all_fragments.items():
            current_count = len(self.narrative_system.story_fragments.get(frag_type, []))
            if current_count < len(fragments):
                available_types.append(frag_type)
        
        if not available_types:
            return
        
        fragment_type = random.choice(available_types)
        fragments = all_fragments[fragment_type]
        current_fragments = self.narrative_system.story_fragments.get(fragment_type, [])
        
        if len(current_fragments) < len(fragments):
            fragment = fragments[len(current_fragments)]
            self.narrative_system.add_story_fragment(fragment_type, fragment)
            
            # Mensajes específicos por tipo
            if fragment_type == "kairon_history":
                self.narrative_system.queue_message("fragment_found")
            elif fragment_type == "project_lyra":
                self.narrative_system.queue_message("project_lyra")
            elif fragment_type == "sleeping_network":
                self.narrative_system.queue_message("network_interference")
            elif fragment_type == "xarn_consciousness":
                self.narrative_system.queue_message("xarn_revelation")
        
        # Verificar si se han recolectado todos los fragmentos
        self.check_all_fragments_collected()
    
    def check_all_fragments_collected(self):
        """Verificar si se han recolectado todos los fragmentos disponibles"""
        total_fragments = 16  # 4 tipos x 4 fragmentos cada uno
        
        if self.narrative_system.fragments_collected >= total_fragments and not self.all_fragments_collected:
            self.all_fragments_collected = True
            self.narrative_system.queue_message("all_fragments_collected")
            
            # Desbloquear poder especial o bonificación
            self.player.max_health += 50
            self.player.health = self.player.max_health
            self.score += 5000
    
    def handle_enemy_destruction(self, enemy):
        """Manejar la destrucción de un enemigo"""
        if isinstance(enemy, BossFinalAgent):
            self.score += 1000
            self.victory = True
            # NUEVO: Iniciar el delay de input al activar la victoria
            self.victory_input_delay = self.input_delay_duration
            
            # Mensaje especial si se tienen todos los fragmentos
            if self.all_fragments_collected:
                self.narrative_system.queue_message("victory_complete")
            else:
                self.narrative_system.queue_message("victory")
            
            # Fragmento final especial
            if self.all_fragments_collected:
                self.narrative_system.add_story_fragment("final_revelation", 
                    "XARN FINAL: 'Comprenden ahora... Yo soy el futuro inevitable. Volveré.'")
        else:
            self.score += 100
            
            # Chance de generar power-up
            drop_chance = 0.15
            if random.random() < drop_chance:
                power_type = self.monte_carlo_powerup()
                if power_type:
                    power_up = PowerUp(enemy.x, enemy.y, power_type)
                    self.power_ups.append(power_up)
            
            # Mayor chance de fragmento si se tienen oleadas perfectas
            fragment_chance = 0.15 if self.player.perfect_runs > 0 else 0.1
            if random.random() < fragment_chance:
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
                # NUEVO: Iniciar el delay de input al activar game over
                self.game_over_input_delay = self.input_delay_duration
                self.narrative_system.queue_message("defeat")
    
    def handle_powerup_collection(self, power_up):
        """Manejar la recolección de power-ups"""
        if power_up.power_type == "slow_time":
            self.player.slow_time = True
            self.player.slow_time_duration = 300  # Aumentamos la duración
            self.narrative_system.queue_message("powerup_slow")
        elif power_up.power_type == "shield":
            self.player.shield = True
            self.player.shield_duration = 240
            self.narrative_system.queue_message("powerup_shield")
        elif power_up.power_type == "extra_life":
            self.player.health = min(self.player.max_health, self.player.health + 30)
            self.narrative_system.queue_message("powerup_life")
    
    def damage_colony(self, damage):
        """Aplicar daño a las colonias"""
        self.colony_health -= damage
        
        if self.colony_health <= 50 and not self.colony_warning_shown:
            self.narrative_system.queue_message("colony_critical")
            self.colony_warning_shown = True
        
        if self.colony_health <= 0:
            self.colony_health = 0
            self.game_over = True
            # NUEVO: Iniciar el delay de input al activar game over
            self.game_over_input_delay = self.input_delay_duration
            self.narrative_system.queue_message("colony_destroyed")

    def all_enemies_spawned(self):
        """Verificar si se han generado todos los enemigos de la oleada actual"""
        if not self.wave_system.current_wave:
            return True
        wave = self.wave_system.current_wave
        for enemy_type, total in wave["enemies"]:
            if self.enemies_spawned.get(enemy_type, 0) < total:
                return False
        return True
    
    def update(self, dt):
        """Actualizar el estado del juego"""
        # NUEVO: Actualizar contadores de delay de input
        if self.victory and self.victory_input_delay > 0:
            self.victory_input_delay -= 1
        
        if self.game_over and self.game_over_input_delay > 0:
            self.game_over_input_delay -= 1
        
        if self.game_over or self.victory or self.paused:
            return

        # Verificar inactividad
        if self.score == 0:
            self.inactivity_timer += 1
            if self.inactivity_timer >= self.max_inactivity:
                self.game_over = True
                # NUEVO: Iniciar el delay de input
                self.game_over_input_delay = self.input_delay_duration
                self.narrative_system.queue_message("inactivity")
        else:
            self.inactivity_timer = 0

        # Transición entre oleadas
        if self.showing_wave_transition:
            self.wave_transition_timer -= 1
            if self.wave_transition_timer <= 0:
                self.showing_wave_transition = False
            return  # Pausar todo mientras se muestra el mensaje

        # Actualizar jugador y sistema narrativo
        self.player.update()
        self.narrative_system.update(dt)

        # Comprobación de fin de oleada sin depender de duración
        if len(self.enemies) == 0 and self.all_enemies_spawned():
            # Verificar si fue una oleada perfecta
            if not self.player.damage_taken_this_wave:
                self.player.perfect_runs += 1
                if self.player.perfect_runs >= 2:
                    self.narrative_system.xarn_data_unlocked = True
                    self.unlock_story_fragment()

            self.player.damage_taken_this_wave = False

            if not self.wave_system.get_next_wave():
                self.victory = True
                # NUEVO: Iniciar el delay de input al activar la victoria
                self.victory_input_delay = self.input_delay_duration
            else:
                self.enemies_spawned = {}
                self.showing_wave_transition = True
                self.wave_transition_timer = self.transition_duration
                wave_info = self.wave_system.get_current_wave_info()
                self.next_wave_name = wave_info["name"] if wave_info else f"Oleada {self.wave_system.wave_number}"
            return  # Esperar transición

        # Factor de tiempo lento más agresivo
        time_factor = 0.25 if self.player.slow_time else 1.0

        # Spawnear enemigos
        self.spawn_enemies()

        # Actualizar enemigos
        for enemy in self.enemies[:]:
            if isinstance(enemy, MarkovEnemy):
                # Aplicar factor de tiempo a MarkovEnemy
                if self.player.slow_time:
                    # Llamar update varias veces con menos frecuencia
                    if pygame.time.get_ticks() % 4 == 0:  # Solo actualizar cada 4 frames
                        enemy.update(self.player)
                else:
                    enemy.update(self.player)
            elif isinstance(enemy, BossFinalAgent):
                # Aplicar factor de tiempo al jefe
                if self.player.slow_time:
                    if pygame.time.get_ticks() % 3 == 0:  # Solo actualizar cada 3 frames
                        enemy.think_and_act(self.player, self)
                else:
                    enemy.think_and_act(self.player, self)
            else:
                # DroneEnemy y otros
                if self.player.slow_time:
                    if pygame.time.get_ticks() % 4 == 0:
                        enemy.update()
                else:
                    enemy.update()

            # Movimiento vertical con factor de tiempo más pronunciado
            if not isinstance(enemy, BossFinalAgent):
                enemy.y += 1.0 * time_factor  # Aumentamos la velocidad base

            if enemy.y > SCREEN_HEIGHT - 100 and not isinstance(enemy, BossFinalAgent):
                self.enemies.remove(enemy)
                if isinstance(enemy, MarkovEnemy):
                    self.damage_colony(15)
                else:
                    self.damage_colony(10)

        # Actualizar power-ups con factor de tiempo
        for power_up in self.power_ups[:]:
            # Solo actualizar power-ups si no hay slow time activo, o hacerlo más lento
            if self.player.slow_time:
                if pygame.time.get_ticks() % 3 == 0:
                    power_up.update()
            else:
                power_up.update()
                
            if power_up.y > SCREEN_HEIGHT:
                self.power_ups.remove(power_up)

        # Drones del jefe (aplicar factor de tiempo)
        for enemy in self.enemies:
            if isinstance(enemy, BossFinalAgent):
                boss = enemy
                drones_to_remove = []
                bullets_to_remove = []

                for drone in boss.spawned_drones[:]:
                    # Movimiento de drones más lento durante slow time
                    drone_speed = 0.5 * time_factor
                    drone.y += drone_speed
                    
                    if drone.y > SCREEN_HEIGHT - 100:
                        boss.spawned_drones.remove(drone)
                        self.damage_colony(8)

                for drone in boss.spawned_drones:
                    for bullet in self.player.bullets:
                        if hasattr(drone, "rect") and hasattr(bullet, "rect"):
                            if drone.rect.colliderect(bullet.rect):
                                drones_to_remove.append(drone)
                                bullets_to_remove.append(bullet)

                for drone in drones_to_remove:
                    if drone in boss.spawned_drones:
                        boss.spawned_drones.remove(drone)
                        powerup_type = self.monte_carlo_powerup()
                        if powerup_type:
                            powerup = PowerUp(drone.x, drone.y, powerup_type)
                            self.power_ups.append(powerup)

                for bullet in bullets_to_remove:
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)

        # Verificar colisiones
        self.collision_system.check_all_collisions()

    
    def handle_events(self, events):
        """Manejar eventos del juego - MODIFICADO para evitar input accidental"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Durante el juego normal (no en pantallas finales)
                if not (self.game_over or self.victory):
                    if event.key == pygame.K_SPACE:
                        self.player.shoot()
                    elif event.key == pygame.K_p:  # Pausar
                        self.paused = not self.paused
                
                # En pantallas finales - SOLO aceptar input después del delay
                elif (self.game_over or self.victory):
                    # Solo aceptar R para reiniciar después del delay
                    if event.key == pygame.K_r:
                        # Para victory: solo después del delay
                        if self.victory and self.victory_input_delay <= 0:
                            self.restart_game()
                        # Para game over: solo después del delay
                        elif self.game_over and self.game_over_input_delay <= 0:
                            self.restart_game()
                    
                    # ESPACIO YA NO REINICIA EL JUEGO - solo R lo hace
                    # Esto evita el reinicio accidental cuando se está disparando
    
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
        """El fondo ahora se maneja desde el archivo principal con scroll infinito"""
    # No dibujar nada aquí - el fondo se dibuja en el bucle principal
        pass
    
    def draw_ui(self):
        """Dibujar la interfaz de usuario"""
        # Panel superior
        pygame.draw.rect(self.screen, (20, 20, 20), (0, 0, SCREEN_WIDTH, 140))
        
        # Puntuación
        score_text = self.font.render(f"Puntos: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Barra de salud del jugador
        health_bar_width = 200
        health_bar_height = 20
        health_bar_x = 10
        health_bar_y = 50
        
        pygame.draw.rect(self.screen, (50, 50, 50), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        current_health_width = int(health_bar_width * (self.player.health / self.player.max_health))
        health_color = GREEN if self.player.health > 50 else YELLOW if self.player.health > 25 else RED
        pygame.draw.rect(self.screen, health_color, (health_bar_x, health_bar_y, current_health_width, health_bar_height))
        pygame.draw.rect(self.screen, WHITE, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
        
        health_text = self.small_font.render(f"Integridad: {max(0, self.player.health)}%", True, WHITE)
        self.screen.blit(health_text, (health_bar_x + 5, health_bar_y + 2))
        
        # NUEVO: Barra de salud de las colonias
        colony_bar_width = 200
        colony_bar_height = 20
        colony_bar_x = SCREEN_WIDTH - colony_bar_width - 10
        colony_bar_y = 50
        
        # Fondo de la barra de colonias
        pygame.draw.rect(self.screen, (50, 50, 50), (colony_bar_x, colony_bar_y, colony_bar_width, colony_bar_height))
        
        # Salud actual de las colonias
        colony_health_width = int(colony_bar_width * (self.colony_health / self.max_colony_health))
        colony_color = GREEN if self.colony_health > 50 else YELLOW if self.colony_health > 25 else RED
        
        # Efecto de parpadeo si está crítico
        if self.colony_health <= 25 and pygame.time.get_ticks() % 500 < 250:
            colony_color = RED
        
        pygame.draw.rect(self.screen, colony_color, (colony_bar_x, colony_bar_y, colony_health_width, colony_bar_height))
        pygame.draw.rect(self.screen, WHITE, (colony_bar_x, colony_bar_y, colony_bar_width, colony_bar_height), 2)
        
        colony_text = self.small_font.render(f"Colonias: {self.colony_health}%", True, WHITE)
        self.screen.blit(colony_text, (colony_bar_x + 5, colony_bar_y + 2))
        
        # Información de oleada
        if self.wave_system.current_wave:
            wave_name = self.wave_system.current_wave.get("name", f"Oleada {self.wave_system.wave_number}")
            wave_text = self.small_font.render(wave_name, True, YELLOW)
            self.screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, 90))
        
        # Power-ups activos con efecto visual mejorado
        power_y = 10
        if self.player.shield:
            shield_text = self.small_font.render("ESCUDO ACTIVO", True, CYAN)
            self.screen.blit(shield_text, (SCREEN_WIDTH - 150, power_y))
            power_y += 25
        
        if self.player.slow_time:
            # Efecto visual más llamativo para slow time
            slow_color = (100, 150, 255) if pygame.time.get_ticks() % 500 < 250 else (50, 100, 200)
            slow_text = self.small_font.render("◄ DISTORSIÓN TEMPORAL ►", True, slow_color)
            self.screen.blit(slow_text, (SCREEN_WIDTH - 200, power_y))
            power_y += 25
        
        # Información de datos recolectados
        if self.narrative_system.fragments_collected > 0:
            fragments_color = PURPLE if not self.all_fragments_collected else GREEN
            data_text = self.tiny_font.render(f"Datos XARN: {self.narrative_system.fragments_collected}/16", True, fragments_color)
            self.screen.blit(data_text, (SCREEN_WIDTH // 2 - 50, 115))
            
            # Indicador especial si se tienen todos los fragmentos
            if self.all_fragments_collected:
                complete_text = self.tiny_font.render("¡ARCHIVO COMPLETO!", True, GREEN)
                self.screen.blit(complete_text, (SCREEN_WIDTH // 2 - 60, 10))
        
        # Advertencia de colonias en peligro
        if self.colony_health <= 25:
            warning_text = self.font.render("¡COLONIAS EN PELIGRO!", True, RED)
            warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
            if pygame.time.get_ticks() % 500 < 250:  # Parpadeo
                self.screen.blit(warning_text, warning_rect)
        
        # Barra de vida del jefe si está presente
        for enemy in self.enemies:
            if isinstance(enemy, BossFinalAgent):
                enemy._draw_health_bar(self.screen)
                enemy._draw_status_text(self.screen)
        # Mostrar transición de oleada
        if self.showing_wave_transition:
            transition_text = self.font.render(f"Iniciando: {self.next_wave_name}", True, CYAN)
            text_rect = transition_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            
            overlay = pygame.Surface((text_rect.width + 40, text_rect.height + 20))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (text_rect.x - 20, text_rect.y - 10))
            self.screen.blit(transition_text, text_rect)
        
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
        """Dibujar pantalla de game over - MODIFICADO con indicador de delay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.colony_health <= 0:
            game_over_text = self.font.render("COLONIAS DESTRUIDAS", True, RED)
            reason_text = self.small_font.render("Las defensas han fallado. Zeta-9 ha caído.", True, WHITE)
        else:
            game_over_text = self.font.render("MISIÓN FALLIDA", True, RED)
            if self.inactivity_timer >= self.max_inactivity:
                reason_text = self.small_font.render("Protocolo de retirada activado por inactividad", True, WHITE)
            else:
                reason_text = self.small_font.render("Sistemas críticos comprometidos", True, WHITE)
        
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(reason_text, (SCREEN_WIDTH // 2 - reason_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        # NUEVO: Mostrar mensaje dependiendo del delay
        if self.game_over_input_delay > 0:
            # Mientras hay delay, mostrar contador
            seconds_left = (self.game_over_input_delay // 60) + 1  # +1 para redondear hacia arriba
            wait_text = self.small_font.render(f"Analizando resultados... {seconds_left}s", True, YELLOW)
            self.screen.blit(wait_text, (SCREEN_WIDTH // 2 - wait_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
        else:
            # Después del delay, mostrar instrucciones
            restart_text = self.small_font.render("Presiona R para reiniciar", True, WHITE)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
    
    
    def draw_victory(self):
        """Dibujar pantalla de victoria - MODIFICADO con indicador de delay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        victory_text = self.font.render("¡VICTORIA TÁCTICA!", True, GREEN)
        self.screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        
        # Mostrar estado de las colonias
        colony_status = self.small_font.render(f"Colonias salvadas: {self.colony_health}% integridad", True, CYAN)
        self.screen.blit(colony_status, (SCREEN_WIDTH // 2 - colony_status.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        
        # Mostrar fragmentos recolectados
        y_offset = SCREEN_HEIGHT // 2
        if self.narrative_system.fragments_collected > 0:
            fragments_text = self.small_font.render(f"Datos XARN recuperados: {self.narrative_system.fragments_collected}/16", True, WHITE)
            self.screen.blit(fragments_text, (SCREEN_WIDTH // 2 - fragments_text.get_width() // 2, y_offset))
            y_offset += 30
            
            # Mensaje especial si se tienen todos los fragmentos
            if self.all_fragments_collected:
                complete_text = self.small_font.render("¡Archivo XARN completo! La verdad ha sido revelada.", True, GREEN)
                self.screen.blit(complete_text, (SCREEN_WIDTH // 2 - complete_text.get_width() // 2, y_offset))
                y_offset += 30
        
        final_text = self.small_font.render("Pero esto es solo el comienzo...", True, CYAN)
        self.screen.blit(final_text, (SCREEN_WIDTH // 2 - final_text.get_width() // 2, y_offset))
        
        # NUEVO: Mostrar mensaje dependiendo del delay
        if self.victory_input_delay > 0:
            # Mientras hay delay, mostrar contador y mensaje especial
            seconds_left = (self.victory_input_delay // 60) + 1  # +1 para redondear hacia arriba
            wait_text = self.small_font.render(f"Procesando datos de victoria... {seconds_left}s", True, YELLOW)
            self.screen.blit(wait_text, (SCREEN_WIDTH // 2 - wait_text.get_width() // 2, y_offset + 40))
            
            # Mensaje adicional para que el jugador entienda
            enjoy_text = self.tiny_font.render("Disfruta tu momento de gloria, Comandante", True, GREEN)
            self.screen.blit(enjoy_text, (SCREEN_WIDTH // 2 - enjoy_text.get_width() // 2, y_offset + 65))
        else:
            # Después del delay, mostrar instrucciones
            restart_text = self.small_font.render("Presiona R para jugar de nuevo", True, WHITE)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, y_offset + 40))
    
    def draw(self):
        """Dibujar todo en la pantalla (sin el fondo - se maneja externamente)"""
        # El fondo se dibuja desde el bucle principal antes de llamar a este método
        # No llamamos a draw_background() aquí
        
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
            'paused': self.paused,
            'colony_health': self.colony_health
            }