"""
Nebula Uprising - Sector Zeta-9
Archivo principal con interfaz gráfica mejorada usando imágenes PNG
"""

import pygame
import sys
import random
import os
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game.game_manager import GameManager

class SoundManager:
    def __init__(self):
        """Gestor de sonidos del juego"""
        self.sounds = {}
        self.load_sounds()
    
    def load_sounds(self):
        """Cargar todos los efectos de sonido"""
        try:
            # Sonido para obtener poder
            power_sound_path = os.path.join("nebula_uprising", "assets", "Sonido", "PoderSFX.mp3")
            if os.path.exists(power_sound_path):
                self.sounds['power'] = pygame.mixer.Sound(power_sound_path)
                self.sounds['power'].set_volume(0.8)
            
            # Sonido para botones del menú
            button_sound_path = os.path.join("nebula_uprising", "assets", "Sonido", "BotonMenu.mp3")
            if os.path.exists(button_sound_path):
                self.sounds['button'] = pygame.mixer.Sound(button_sound_path)
                self.sounds['button'].set_volume(0.6)
                
        except pygame.error as e:
            print(f"Error cargando sonidos: {e}")
    
    def play_sound(self, sound_name):
        """Reproducir un sonido específico"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass  # Si hay error, continuar sin sonido
    
    def play_power_sound(self):
        """Reproducir sonido de poder obtenido"""
        self.play_sound('power')
    
    def play_button_sound(self):
        """Reproducir sonido de botón del menú"""
        self.play_sound('button')

class StaticBackgroundWithStars:
    def __init__(self, image_path, num_stars=150, star_speed=30):
        """Clase para manejar fondo estático con estrellas animadas"""
        try:
            # Cargar imagen original
            original_image = pygame.image.load(image_path).convert()
            
            # Obtener dimensiones originales
            orig_width, orig_height = original_image.get_size()
            
            # Calcular escala manteniendo proporción
            scale_x = SCREEN_WIDTH / orig_width
            scale_y = SCREEN_HEIGHT / orig_height
            
            # Usar la escala mayor para que cubra toda la pantalla
            scale = max(scale_x, scale_y)
            
            # Calcular nuevas dimensiones
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)
            
            # Escalar imagen manteniendo proporción
            scaled_image = pygame.transform.scale(original_image, (new_width, new_height))
            
            # Si la imagen es más grande que la pantalla, centrarla
            if new_width > SCREEN_WIDTH or new_height > SCREEN_HEIGHT:
                # Crear superficie del tamaño de pantalla
                self.background_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                
                # Calcular posición para centrar
                x_offset = (SCREEN_WIDTH - new_width) // 2
                y_offset = (SCREEN_HEIGHT - new_height) // 2
                
                # Dibujar imagen centrada
                self.background_image.blit(scaled_image, (x_offset, y_offset))
            else:
                self.background_image = scaled_image
                
        except pygame.error:
            # Si no se puede cargar la imagen, crear un fondo de color sólido
            print(f"No se pudo cargar {image_path}, usando fondo por defecto")
            self.background_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background_image.fill((10, 10, 30))  # Azul oscuro espacial
        
        # Configuración de estrellas
        self.star_speed = star_speed
        self.stars = []
        
        # Generar estrellas iniciales
        for _ in range(num_stars):
            star = {
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.choice([1, 1, 2, 2, 3]),  # Más estrellas pequeñas
                'brightness': random.randint(150, 255),
                'twinkle_timer': random.randint(0, 120),
                'twinkle_speed': random.uniform(0.5, 2.0)
            }
            self.stars.append(star)
    
    def update(self, dt):
        """Actualizar animación de estrellas"""
        for star in self.stars:
            # Mover estrella hacia abajo
            star['y'] += self.star_speed * dt
            
            # Si la estrella sale de la pantalla, reposicionarla arriba
            if star['y'] > SCREEN_HEIGHT:
                star['y'] = -5
                star['x'] = random.randint(0, SCREEN_WIDTH)
                star['size'] = random.choice([1, 1, 2, 2, 3])
                star['brightness'] = random.randint(150, 255)
            
            # Efecto de parpadeo
            star['twinkle_timer'] += star['twinkle_speed']
            if star['twinkle_timer'] > 120:
                star['twinkle_timer'] = 0
                star['brightness'] = random.randint(150, 255)
    
    def draw(self, screen):
        """Dibujar el fondo estático y las estrellas animadas"""
        # Dibujar fondo estático
        screen.blit(self.background_image, (0, 0))
        
        # Dibujar estrellas con efecto de parpadeo
        for star in self.stars:
            # Calcular brillo con efecto de parpadeo suave
            twinkle_factor = abs(pygame.math.Vector2(1, 0).rotate(star['twinkle_timer'] * 3).x)
            current_brightness = int(star['brightness'] * (0.7 + 0.3 * twinkle_factor))
            
            # Crear color de la estrella
            color = (current_brightness, current_brightness, current_brightness)
            
            # Dibujar estrella
            pygame.draw.circle(screen, color, (int(star['x']), int(star['y'])), star['size'])
            
            # Agregar pequeño halo para estrellas más grandes
            if star['size'] >= 2:
                halo_color = (current_brightness // 3, current_brightness // 3, current_brightness // 3)
                pygame.draw.circle(screen, halo_color, (int(star['x']), int(star['y'])), star['size'] + 1)
    
    def set_star_speed(self, new_speed):
        """Cambiar la velocidad de las estrellas"""
        self.star_speed = new_speed

class ImprovedMenuScreen:
    def __init__(self, screen, sound_manager):
        self.screen = screen
        self.sound_manager = sound_manager
        self.game_started = False
        self.show_story = False
        
        # Cargar imágenes de la interfaz
        self.load_ui_images()
        
        # Configurar botones
        self.setup_buttons()
        
        # Efectos visuales
        self.title_pulse = 0
        self.button_hover_effects = {'start': 0, 'info': 0}
        
    def load_ui_images(self):
        """Cargar todas las imágenes de la interfaz"""
        ui_path = os.path.join("nebula_uprising", "assets", "UI")
        
        try:
            # Cargar título
            self.header_image = pygame.image.load(os.path.join(ui_path, "Header.png")).convert_alpha()
            # Escalar título si es necesario (opcional)
            header_width = min(self.header_image.get_width(), SCREEN_WIDTH - 100)
            header_height = int(self.header_image.get_height() * (header_width / self.header_image.get_width()))
            self.header_image = pygame.transform.scale(self.header_image, (header_width, header_height))
            
            # Cargar botones
            self.start_btn_image = pygame.image.load(os.path.join(ui_path, "Start_BTN.png")).convert_alpha()
            self.info_btn_image = pygame.image.load(os.path.join(ui_path, "Info_BTN.png")).convert_alpha()
            
            # Cargar ventana de historia
            self.story_window_image = pygame.image.load(os.path.join(ui_path, "VentanaHistoria.png")).convert_alpha()
            
            # Cargar imagen de derrota (para uso futuro)
            self.lose_image = pygame.image.load(os.path.join(ui_path, "Lose.png")).convert_alpha()
            
        except pygame.error as e:
            print(f"Error cargando imágenes de UI: {e}")
            # Crear imágenes de respaldo
            self.create_fallback_images()
    
    def create_fallback_images(self):
        """Crear imágenes de respaldo si no se pueden cargar las originales"""
        # Título de respaldo
        font_large = pygame.font.Font(None, 72)
        title_text = font_large.render("NEBULA UPRISING", True, (255, 255, 255))
        self.header_image = title_text
        
        # Botones de respaldo
        font_button = pygame.font.Font(None, 48)
        
        # Botón Start
        start_surface = pygame.Surface((200, 60))
        start_surface.fill((50, 150, 50))
        start_text = font_button.render("START", True, (255, 255, 255))
        start_rect = start_text.get_rect(center=(100, 30))
        start_surface.blit(start_text, start_rect)
        self.start_btn_image = start_surface
        
        # Botón Info
        info_surface = pygame.Surface((200, 60))
        info_surface.fill((50, 50, 150))
        info_text = font_button.render("INFO", True, (255, 255, 255))
        info_rect = info_text.get_rect(center=(100, 30))
        info_surface.blit(info_text, info_rect)
        self.info_btn_image = info_surface
        
        # Ventana de historia de respaldo
        story_surface = pygame.Surface((600, 400))
        story_surface.fill((20, 20, 40))
        pygame.draw.rect(story_surface, (100, 100, 150), story_surface.get_rect(), 3)
        self.story_window_image = story_surface
        
        # Imagen de derrota de respaldo
        lose_surface = pygame.Surface((300, 100))
        lose_surface.fill((150, 50, 50))
        lose_text = font_button.render("GAME OVER", True, (255, 255, 255))
        lose_rect = lose_text.get_rect(center=(150, 50))
        lose_surface.blit(lose_text, lose_rect)
        self.lose_image = lose_surface
    
    def setup_buttons(self):
        """Configurar posiciones y áreas de los botones"""
        # Posición del título
        self.header_rect = self.header_image.get_rect()
        self.header_rect.centerx = SCREEN_WIDTH // 2
        self.header_rect.y = 50
        
        # Posición del botón Start
        self.start_btn_rect = self.start_btn_image.get_rect()
        self.start_btn_rect.centerx = SCREEN_WIDTH // 2
        self.start_btn_rect.y = SCREEN_HEIGHT // 2 + 50
        
        # Posición del botón Info
        self.info_btn_rect = self.info_btn_image.get_rect()
        self.info_btn_rect.centerx = SCREEN_WIDTH // 2
        self.info_btn_rect.y = self.start_btn_rect.bottom + 20
        
        # Posición de la ventana de historia
        self.story_window_rect = self.story_window_image.get_rect()
        self.story_window_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    def handle_events(self, events):
        """Manejar eventos del menú"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Actualizar efectos hover
        self.update_hover_effects(mouse_pos)
        
        for event in events:
            if event.type == pygame.QUIT:
                return "quit"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click izquierdo
                    if self.show_story:
                        # Si está mostrando la historia, cualquier click la cierra
                        self.show_story = False
                    else:
                        # Verificar clicks en botones
                        if self.start_btn_rect.collidepoint(mouse_pos):
                            self.sound_manager.play_button_sound()  # Reproducir sonido de botón
                            self.game_started = True
                        elif self.info_btn_rect.collidepoint(mouse_pos):
                            self.sound_manager.play_button_sound()  # Reproducir sonido de botón
                            self.show_story = True
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.show_story:
                    self.show_story = False
        
        return None
    
    def update_hover_effects(self, mouse_pos):
        """Actualizar efectos de hover en botones"""
        # Efecto hover para botón Start
        if self.start_btn_rect.collidepoint(mouse_pos):
            self.button_hover_effects['start'] = min(10, self.button_hover_effects['start'] + 1)
        else:
            self.button_hover_effects['start'] = max(0, self.button_hover_effects['start'] - 1)
        
        # Efecto hover para botón Info
        if self.info_btn_rect.collidepoint(mouse_pos):
            self.button_hover_effects['info'] = min(10, self.button_hover_effects['info'] + 1)
        else:
            self.button_hover_effects['info'] = max(0, self.button_hover_effects['info'] - 1)
    
    def update(self):
        """Actualizar animaciones del menú"""
        # Efecto de pulsación en el título
        self.title_pulse += 0.1
        if self.title_pulse > 6.28:  # 2π
            self.title_pulse = 0
    
    def draw(self):
        """Dibujar el menú mejorado"""
        if not self.show_story:
            self.draw_main_menu()
        else:
            self.draw_story_window()
    
    def draw_main_menu(self):
        """Dibujar menú principal"""
        # Dibujar título con efecto de pulsación
        pulse_offset = int(5 * abs(pygame.math.Vector2(1, 0).rotate(self.title_pulse * 60).x))
        title_pos = (self.header_rect.x, self.header_rect.y - pulse_offset)
        
        # Agregar brillo al título
        title_glow = self.header_image.copy()
        title_glow.set_alpha(100)
        for i in range(3):
            glow_pos = (title_pos[0] + i - 1, title_pos[1] + i - 1)
            self.screen.blit(title_glow, glow_pos)
        
        # Dibujar título principal
        self.screen.blit(self.header_image, title_pos)
        
        # Dibujar botón Start con efecto hover
        start_hover = self.button_hover_effects['start']
        start_pos = (self.start_btn_rect.x - start_hover, self.start_btn_rect.y - start_hover)
        
        if start_hover > 0:
            # Efecto de resplandor
            start_glow = self.start_btn_image.copy()
            start_glow.set_alpha(50)
            self.screen.blit(start_glow, (start_pos[0] - 2, start_pos[1] - 2))
        
        self.screen.blit(self.start_btn_image, start_pos)
        
        # Dibujar botón Info con efecto hover
        info_hover = self.button_hover_effects['info']
        info_pos = (self.info_btn_rect.x - info_hover, self.info_btn_rect.y - info_hover)
        
        if info_hover > 0:
            # Efecto de resplandor
            info_glow = self.info_btn_image.copy()
            info_glow.set_alpha(50)
            self.screen.blit(info_glow, (info_pos[0] - 2, info_pos[1] - 2))
        
        self.screen.blit(self.info_btn_image, info_pos)
        
        # Texto de instrucciones
        font_small = pygame.font.Font(None, 24)
        instruction_text = font_small.render("Haz click en los botones para interactuar", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(instruction_text, instruction_rect)
    
    def draw_story_window(self):
        """Dibujar ventana de historia"""
        # Dibujar overlay semitransparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Dibujar ventana de historia
        self.screen.blit(self.story_window_image, self.story_window_rect)
        
        # Agregar texto de historia
        self.draw_story_text()
        
        # Instrucciones para cerrar
        font_small = pygame.font.Font(None, 24)
        close_text = font_small.render("Presiona ESC o haz click para cerrar", True, (255, 255, 255))
        close_rect = close_text.get_rect(center=(SCREEN_WIDTH // 2, self.story_window_rect.bottom + 30))
        self.screen.blit(close_text, close_rect)
    
    def draw_story_text(self):
        """Dibujar texto de la historia del juego"""
        story_text = [
            "NEBULA UPRISING - SECTOR ZETA-9",
            "",
            "En el año 2387, la humanidad ha colonizado",
            "múltiples sectores de la galaxia. El Sector",
            "Zeta-9 era conocido por su tranquilidad hasta",
            "que una misteriosa señal alienígena fue",
            "detectada en sus confines.",
            "",
            "Como piloto de élite de la Federación",
            "Galáctica, tu misión es investigar esta",
            "anomalía y defender el sector de cualquier",
            "amenaza que pueda surgir.",
            "",
            "Prepárate para el combate, piloto.",
            "El destino de Zeta-9 está en tus manos."
        ]
        
        font_story = pygame.font.Font(None, 28)
        y_offset = self.story_window_rect.y + 500
        
        for line in story_text:
            if line:  # Si la línea no está vacía
                text_surface = font_story.render(line, True, (255, 255, 255))
                text_rect = text_surface.get_rect(centerx=self.story_window_rect.centerx, y=y_offset)
                self.screen.blit(text_surface, text_rect)
            y_offset += 25
    
    def reset(self):
        """Resetear el estado del menú"""
        self.game_started = False
        self.show_story = False
        self.title_pulse = 0
        self.button_hover_effects = {'start': 0, 'info': 0}

class NebulaUprisingGame:
    def __init__(self):
        # Inicializar Pygame
        pygame.init()
        
        # Configurar pantalla
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Nebula Uprising - Sector Zeta-9")

        # Inicializar gestor de sonidos
        self.sound_manager = SoundManager()

        # Fondos estáticos con estrellas animadas
        self.menu_background = StaticBackgroundWithStars(
            os.path.join("nebula_uprising", "assets", "Fondo", "GalaxiaMenu.jpg"), 
            num_stars=100,  # Menos estrellas para el menú
            star_speed=20   # Velocidad suave para el menú
        )
        self.game_background = StaticBackgroundWithStars(
            os.path.join("nebula_uprising", "assets", "Fondo", "Galaxia1.jpg"),
            num_stars=200,  # Más estrellas para el juego
            star_speed=40   # Velocidad más rápida para sensación de movimiento
        )
        
        # Estados del juego
        self.game_state = "MENU"  # MENU, PLAYING, GAME_OVER
        
        # Inicializar sistemas con nueva interfaz y sonidos
        self.menu_screen = ImprovedMenuScreen(self.screen, self.sound_manager)
        self.game_manager = None
        self.clock = pygame.time.Clock()
        
        # Música y sonidos (opcional)
        self.setup_audio()
    
    def setup_audio(self):
         """Configurar audio del juego"""
         try:
             pygame.mixer.init()
             self.menu_music = os.path.join("nebula_uprising", "assets", "Sonido", "Menú.mp3")
             self.game_music = os.path.join("nebula_uprising", "assets", "Sonido", "MusicaJuego.mp3")
        
             # Iniciar música del menú en bucle
             if os.path.exists(self.menu_music):
                 pygame.mixer.music.load(self.menu_music)
                 pygame.mixer.music.set_volume(0.7)
                 pygame.mixer.music.play(-1)  # -1 = bucle infinito
         except:
             print("No se pudo cargar la música")
    
    def run(self):
        """Bucle principal del juego"""
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            
            # Manejar eventos según el estado
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
            
            # Lógica según estado del juego
            if self.game_state == "MENU":
                # Actualizar estrellas del menú
                self.menu_background.update(dt)
                
                # Manejar menú
                result = self.menu_screen.handle_events(events)
                if result == "quit":
                    running = False
                
                self.menu_screen.update()
                
                # Dibujar fondo con estrellas
                self.menu_background.draw(self.screen)
                
                # Dibujar menú encima (con nueva interfaz)
                self.menu_screen.draw()
                
                # Verificar si se inició el juego
                if self.menu_screen.game_started:
                    self.start_new_game()
                    self.game_state = "PLAYING"
            
            elif self.game_state == "PLAYING":
                # Actualizar estrellas del juego
                self.game_background.update(dt)
                
                # Manejar juego
                self.game_manager.handle_events(events)
                
                # Manejar input continuo
                keys = pygame.key.get_pressed()
                self.game_manager.handle_continuous_input(keys)
                
                # Actualizar juego
                self.game_manager.update(dt)
                
                # Verificar si el juego terminó
                if self.game_manager.game_over or self.game_manager.victory:
                    self.game_state = "GAME_OVER"
                
                # Dibujar fondo con estrellas y juego
                self.game_background.draw(self.screen)
                self.game_manager.draw()
            
            elif self.game_state == "GAME_OVER":
                # Continuar actualizando estrellas (más lento)
                self.game_background.set_star_speed(15)  # Ralentizar estrellas
                self.game_background.update(dt)
                
               
                # Solo pasamos los eventos al game_manager
                self.game_manager.handle_events(events)
                
                
                self.game_manager.update(dt)
                
                # Dibujar fondo y game manager
                self.game_background.draw(self.screen)
                self.game_manager.draw()
                
                # Si el juego terminó en derrota, mostrar imagen de Lose
                if self.game_manager.game_over:
                    lose_rect = self.menu_screen.lose_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
                    self.screen.blit(self.menu_screen.lose_image, lose_rect)
                
                
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        # Solo permitir ESCAPE para volver al menú después del delay
                        if event.key == pygame.K_ESCAPE:
                            # Verificar si el delay ha terminado antes de permitir escape
                            delay_finished = False
                            if self.game_manager.victory and self.game_manager.victory_input_delay <= 0:
                                delay_finished = True
                            elif self.game_manager.game_over and self.game_manager.game_over_input_delay <= 0:
                                delay_finished = True
                            
                            if delay_finished:
                                self.return_to_menu()
                        
                        # ENTER también puede volver al menú después del delay
                        elif event.key == pygame.K_RETURN:
                            delay_finished = False
                            if self.game_manager.victory and self.game_manager.victory_input_delay <= 0:
                                delay_finished = True
                            elif self.game_manager.game_over and self.game_manager.game_over_input_delay <= 0:
                                delay_finished = True
                            
                            if delay_finished:
                                self.return_to_menu()
                
                # Mostrar instrucción adicional solo después del delay
                delay_finished = False
                if self.game_manager.victory and self.game_manager.victory_input_delay <= 0:
                    delay_finished = True
                elif self.game_manager.game_over and self.game_manager.game_over_input_delay <= 0:
                    delay_finished = True
                
                if delay_finished:
                    font = pygame.font.Font(None, 24)
                    text = font.render("Presiona ENTER o ESC para volver al menú", True, (255, 255, 255))
                    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
                    self.screen.blit(text, text_rect)
            
            pygame.display.flip()
        
        # Limpiar y salir
        pygame.quit()
        sys.exit()
    
    def start_new_game(self):
        """Iniciar una nueva partida"""
        try:
            if os.path.exists(self.game_music):
                pygame.mixer.music.load(self.game_music)
                pygame.mixer.music.set_volume(0.6)
                pygame.mixer.music.play(-1)  # bucle
        except:
            pass

        # Restaurar velocidad normal de estrellas
        self.game_background.set_star_speed(40)
        # Crear GameManager normalmente
        self.game_manager = GameManager(self.screen)
        # Asignar el sound_manager después de crear el GameManager
        self.game_manager.sound_manager = self.sound_manager
        self.menu_screen.game_started = False
    
    def return_to_menu(self):
        """Volver al menú principal"""
        self.game_state = "MENU"
        self.menu_screen.reset()
        self.game_manager = None

        try:
            if os.path.exists(self.menu_music):
                pygame.mixer.music.load(self.menu_music)
                pygame.mixer.music.set_volume(0.7)
                pygame.mixer.music.play(-1)
        except:
            pass

def main():
    """Función principal"""
    game = NebulaUprisingGame()
    game.run()

if __name__ == "__main__":
    main()
