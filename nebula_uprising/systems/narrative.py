"""
Sistema Narrativo - Nebula Uprising
Maneja los mensajes de ECHO con interfaz gráfica mejorada usando imágenes PNG
"""

import pygame
import math
from collections import deque
import os
from config.colors import BLACK, CYAN, WHITE, GREEN, RED, PURPLE, YELLOW

class NarrativeSystem:
    def __init__(self):
        self.story_fragments = {
            "kairon_history": [],
            "project_lyra": [],
            "sleeping_network": [],
            "xarn_consciousness": [],
            "final_revelation": []
        }
        self.messages_queue = deque()
        self.current_message = None
        self.current_message_type = "normal"  # normal, alert, code_red, revelation
        self.message_timer = 0
        self.message_duration = 300  # Más tiempo para leer con la nueva interfaz
        
        # Cargar imágenes de Echo
        self.load_echo_images()
        
        # Configurar posiciones
        self.setup_ui_positions()
        
        # Efectos visuales
        self.text_scroll_offset = 0
        self.echo_animation_timer = 0
        self.alert_blink_timer = 0
        
        self.echo_messages = {
            # Mensajes iniciales
            "intro": ("Comandante Nova, aquí ECHO. Detectando múltiples señales hostiles en el sector Zeta-9.", "normal"),
            "first_wave": ("Análisis: Drones de reconocimiento XARN. Proceda con precaución.", "normal"),
            "markov_enemy": ("Alerta: Enemigos con patrones adaptativos detectados. Comportamiento impredecible.", "alert"),
            "boss_spawn": ("¡ADVERTENCIA CRÍTICA! Núcleo XARN detectado. Preparando protocolos de combate.", "code_red"),
            
            # Mensajes de estado
            "low_health": ("Comandante, integridad estructural comprometida. Busque poder de reparación.", "alert"),
            "colony_critical": ("¡ALERTA! Las colonias están bajo ataque directo. Integridad crítica.", "alert"),
            "colony_destroyed": ("Transmisión final... Las colonias han caído. Zeta-9 está perdido.", "code_red"),
            
            # Power-ups
            "powerup_shield": ("Escudo temporal activado. Duración limitada.", "normal"),
            "powerup_slow": ("Distorsión temporal detectada. Los enemigos se mueven más lento.", "normal"),
            "powerup_life": ("Sistemas de reparación activados. Integridad restaurada.", "normal"),
            
            # Fragmentos de historia
            "fragment_found": ("Datos recuperados. Analizando información sobre los Kairon...", "revelation"),
            "project_lyra": ("¡Alerta! Archivos clasificados del Proyecto Lyra detectados.", "revelation"),
            "network_interference": ("Interferencia anómala... ¿Otros sistemas están... escuchando?", "revelation"),
            "xarn_revelation": ("Datos críticos: XARN no es lo que parece. Es algo mucho más antiguo.", "revelation"),
            
            # Mensajes de victoria/derrota
            "victory": ("Núcleo XARN neutralizado. Pero esto es solo el comienzo, Comandante.", "normal"),
            "victory_complete": ("¡Increíble! Con todos los datos, ahora entendemos. XARN volverá... debemos prepararnos.", "revelation"),
            "defeat": ("Sistemas críticos dañados. Protocolo de evacuación activado.", "code_red"),
            "inactivity": ("Rendimiento inaceptable. Protocolo de retirada activado.", "alert"),
            "colony_breached": ("¡CÓDIGO ROJO! XARN ha alcanzado las colonias. Zeta-9 está perdido...", "code_red"),
            
            # Mensajes especiales por fragmentos
            "all_fragments_collected": ("¡REVELACIÓN COMPLETA! Comandante, ahora lo veo todo... XARN es eterno.", "revelation"),
            "xarn_truth": ("La verdad sobre XARN: No es una IA. Es la suma de todas las civilizaciones caídas.", "revelation"),
            "final_warning": ("ECHO: Comandante... siento algo extraño en mi código. XARN está... aquí.", "code_red")
        }
        
        self.fragments_collected = 0
        self.xarn_data_unlocked = False
        
        # Control de revelaciones especiales
        self.special_revelations_shown = set()
        
    def load_echo_images(self):
        """Cargar imágenes de Echo y cuadros de diálogo"""
        ui_path = os.path.join("nebula_uprising", "assets", "UI")
        
        try:
            # Cargar imagen de Echo normal
            self.echo_normal = pygame.image.load(os.path.join(ui_path, "Echo.png")).convert_alpha()
            
            # Cargar imagen de Echo problema (solo para alertas)
            self.echo_problem = pygame.image.load(os.path.join(ui_path, "EchoProblema.png")).convert_alpha()
            
            # Cargar cuadro de diálogo
            self.dialog_box = pygame.image.load(os.path.join(ui_path, "Aviso2Echo.png")).convert_alpha()
            
            # Escalar imágenes de Echo - MUY PEQUEÑO
            echo_scale = 0.08  # Mucho más pequeño
            new_echo_width = int(self.echo_normal.get_width() * echo_scale)
            new_echo_height = int(self.echo_normal.get_height() * echo_scale)
            
            self.echo_normal = pygame.transform.scale(self.echo_normal, (new_echo_width, new_echo_height))
            self.echo_problem = pygame.transform.scale(self.echo_problem, (new_echo_width, new_echo_height))
            
            # Escalar cuadro de diálogo - muy pequeño
            dialog_scale = 0.3
            new_dialog_width = int(self.dialog_box.get_width() * dialog_scale)
            new_dialog_height = int(self.dialog_box.get_height() * dialog_scale)
            self.dialog_box = pygame.transform.scale(self.dialog_box, (new_dialog_width, new_dialog_height))
            
            print(f"Echo images loaded successfully. Echo size: {new_echo_width}x{new_echo_height}")
            
        except pygame.error as e:
            print(f"Error cargando imágenes de Echo: {e}")
            self.create_fallback_echo_images()
    
    def create_fallback_echo_images(self):
        """Crear imágenes de respaldo si no se pueden cargar las originales"""
        # Echo normal (círculo azul) - muy pequeño
        self.echo_normal = pygame.Surface((35, 35), pygame.SRCALPHA)
        pygame.draw.circle(self.echo_normal, CYAN, (17, 17), 15)
        pygame.draw.circle(self.echo_normal, WHITE, (17, 17), 15, 2)
        
        # Echo problema (círculo rojo) - muy pequeño
        self.echo_problem = pygame.Surface((35, 35), pygame.SRCALPHA)
        pygame.draw.circle(self.echo_problem, RED, (17, 17), 15)
        pygame.draw.circle(self.echo_problem, WHITE, (17, 17), 15, 2)
        
        # Cuadro de diálogo - muy pequeño
        self.dialog_box = pygame.Surface((200, 60), pygame.SRCALPHA)
        pygame.draw.rect(self.dialog_box, (20, 20, 40, 200), self.dialog_box.get_rect())
        pygame.draw.rect(self.dialog_box, WHITE, self.dialog_box.get_rect(), 2)
    
    def setup_ui_positions(self):
        """Configurar posiciones de los elementos UI"""
        # Obtener dimensiones de la pantalla
        screen = pygame.display.get_surface()
        if screen:
            screen_width = screen.get_width()
            screen_height = screen.get_height()
        else:
            # Valores por defecto si no hay pantalla disponible
            screen_width = 800
            screen_height = 600
        
        # Posición de Echo (parte media derecha de la pantalla)
        self.echo_x = screen_width - 250  # Desde el borde derecho
        self.echo_y = screen_height // 2 - 50  # Centro vertical
        
        # POSICIÓN MÁXIMA A LA IZQUIERDA: Pegado al borde izquierdo
        self.dialog_x = 10  # Solo 10 píxeles del borde para evitar que se corte
        self.dialog_y = self.echo_y - 10  # Alineado con Echo
        
        # Área de texto dentro del cuadro - ajustada para cuadro pequeño
        self.text_area_x = self.dialog_x + 10
        self.text_area_y = self.dialog_y + 8
        self.text_area_width = self.dialog_box.get_width() - 20
        self.text_area_height = self.dialog_box.get_height() - 16
    
    def queue_message(self, message_key):
        """Encolar un mensaje de ECHO"""
        if message_key in self.echo_messages:
            message_text, message_type = self.echo_messages[message_key]
            self.messages_queue.append((message_text, message_type))
    
    def add_story_fragment(self, fragment_type, fragment):
        """Agregar un fragmento de historia"""
        if fragment_type in self.story_fragments:
            self.story_fragments[fragment_type].append(fragment)
            self.fragments_collected += 1
            
            # Mostrar revelaciones especiales en ciertos hitos
            self._check_special_revelations()
    
    def _check_special_revelations(self):
        """Verificar y mostrar revelaciones especiales según los fragmentos recolectados"""
        # Primera revelación: 5 fragmentos
        if self.fragments_collected >= 5 and "first_revelation" not in self.special_revelations_shown:
            self.queue_message("xarn_truth")
            self.special_revelations_shown.add("first_revelation")
        
        # Segunda revelación: 10 fragmentos
        elif self.fragments_collected >= 10 and "second_revelation" not in self.special_revelations_shown:
            self.queue_message("final_warning")
            self.special_revelations_shown.add("second_revelation")
        
        # Revelación final: todos los fragmentos
        elif self.fragments_collected >= 16 and "final_revelation" not in self.special_revelations_shown:
            self.queue_message("all_fragments_collected")
            self.special_revelations_shown.add("final_revelation")
    
    def update(self, dt):
        """Actualizar el sistema narrativo"""
        # Actualizar timers de animación
        self.echo_animation_timer += dt * 60
        self.alert_blink_timer += dt * 60
        
        # Actualizar posiciones dinámicamente
        self.update_positions()
        
        if self.current_message:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.current_message = None
                self.current_message_type = "normal"
        elif self.messages_queue:
            message_data = self.messages_queue.popleft()
            self.current_message = message_data[0]
            self.current_message_type = message_data[1]
            self.message_timer = self.message_duration
            self.text_scroll_offset = 0
    
    def update_positions(self):
        """Actualizar posiciones basadas en el tamaño actual de la pantalla"""
        screen = pygame.display.get_surface()
        if screen:
            screen_width = screen.get_width()
            screen_height = screen.get_height()
            
            # Actualizar posiciones - parte media derecha
            self.echo_x = screen_width - 250
            self.echo_y = screen_height // 2 - 50
            
            # POSICIÓN MÁXIMA A LA IZQUIERDA: Pegado al borde izquierdo
            self.dialog_x = 10  # Solo 10 píxeles del borde para evitar que se corte
            self.dialog_y = self.echo_y - 10
            self.text_area_x = self.dialog_x + 10
            self.text_area_y = self.dialog_y + 8
    
    def draw(self, screen, font):
        """Dibujar mensajes narrativos con interfaz gráfica mejorada"""
        if not self.current_message:
            return
        
        # Seleccionar imagen de Echo según el tipo de mensaje
        if self.current_message_type in ["alert", "code_red"]:
            echo_image = self.echo_problem
        else:
            echo_image = self.echo_normal
        
        # Crear una copia del cuadro de diálogo con transparencia
        dialog_transparent = self.dialog_box.copy()
        dialog_transparent.set_alpha(128)
        
        # Dibujar cuadro de diálogo
        screen.blit(dialog_transparent, (self.dialog_x, self.dialog_y))
        
        # DIBUJAR ECHO AL LADO DERECHO DEL CUADRO DE DIÁLOGO
        # Posición de Echo: a la derecha del cuadro, centrado verticalmente
        echo_x_pos = self.dialog_x + self.dialog_box.get_width() - echo_image.get_width() - 10  # Cerca del borde derecho
        echo_y_pos = self.dialog_y + self.dialog_box.get_height() - 5
        
        # Aplicar animación sutil
        echo_bob = int(1.5 * math.sin(self.echo_animation_timer / 40))  # Animación muy sutil
        echo_final_pos = (echo_x_pos, echo_y_pos + echo_bob)
        
        # Dibujar Echo
        screen.blit(echo_image, echo_final_pos)
        
        # Efecto de brillo para mensajes críticos
        if self.current_message_type in ["alert", "code_red"] and int(self.alert_blink_timer) % 60 < 30:
            echo_glow = echo_image.copy()
            echo_glow.set_alpha(100)
            screen.blit(echo_glow, (echo_final_pos[0] - 1, echo_final_pos[1] - 1))
        
        # Dibujar texto
        self.draw_wrapped_text(screen, font, self.current_message)
        
        # Dibujar indicador de tipo de mensaje
        self.draw_message_indicator(screen, font)
    
    def draw_wrapped_text(self, screen, font, text):
        """Dibujar texto con ajuste de línea dentro del cuadro de diálogo"""
        # Dividir texto en palabras
        words = text.split(' ')
        lines = []
        current_line = ""
        
        # Crear líneas que quepan en el ancho del cuadro
        for word in words:
            test_line = current_line + word + " "
            test_surface = font.render(test_line, True, WHITE)
            
            if test_surface.get_width() <= self.text_area_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        # Dibujar líneas de texto
        line_height = font.get_height() + 1  # Reducido espacio entre líneas
        start_y = self.text_area_y
        
        # Determinar color según tipo de mensaje
        text_color = WHITE
        if self.current_message_type == "alert":
            text_color = YELLOW
        elif self.current_message_type == "code_red":
            text_color = RED
        elif self.current_message_type == "revelation":
            text_color = PURPLE
        
        for i, line in enumerate(lines):
            y_pos = start_y + (i * line_height)
            
            # Solo dibujar si la línea está dentro del área visible
            if y_pos + line_height <= self.text_area_y + self.text_area_height:
                text_surface = font.render(line, True, text_color)
                screen.blit(text_surface, (self.text_area_x, y_pos))
    
    def draw_message_indicator(self, screen, font):
        """Dibujar indicador del tipo de mensaje"""
        indicator_text = ""
        indicator_color = WHITE
        
        if self.current_message_type == "alert":
            indicator_text = "ALERTA"  # Solo símbolo para ahorrar espacio
            indicator_color = YELLOW
        elif self.current_message_type == "code_red":
            indicator_text = "IMPORTANTE"  # Solo símbolo
            indicator_color = RED
        elif self.current_message_type == "revelation":
            indicator_text = "REVELACIÓN"  # Solo símbolo
            indicator_color = PURPLE
        else:
            indicator_text = "ECHO"
            indicator_color = CYAN
        
        # Dibujar indicador en la parte superior del cuadro (muy pequeño)
        indicator_surface = font.render(indicator_text, True, indicator_color)
        indicator_x = self.dialog_x + 5
        indicator_y = self.dialog_y - 15
        
        # Fondo para el indicador - mínimo
        padding = 2
        indicator_bg = pygame.Surface((indicator_surface.get_width() + padding * 2, 
                                     indicator_surface.get_height() + padding))
        indicator_bg.set_alpha(180)
        indicator_bg.fill(BLACK)
        screen.blit(indicator_bg, (indicator_x - padding, indicator_y - padding // 2))
        
        # Texto del indicador
        screen.blit(indicator_surface, (indicator_x, indicator_y))
    
    def draw_fragment_summary(self, screen, font):
        """Dibujar resumen de fragmentos recolectados (para pantalla de victoria)"""
        y_offset = 200
        x_center = screen.get_width() // 2
        
        title = font.render("=== DATOS XARN RECUPERADOS ===", True, PURPLE)
        screen.blit(title, (x_center - title.get_width() // 2, y_offset))
        y_offset += 30
        
        # Mostrar fragmentos por categoría
        categories = {
            "kairon_history": "Historia Kairon",
            "project_lyra": "Proyecto Lyra",
            "sleeping_network": "Red de los Dormidos",
            "xarn_consciousness": "Conciencia XARN",
            "final_revelation": "Revelación Final"
        }
        
        for key, name in categories.items():
            count = len(self.story_fragments.get(key, []))
            if count > 0:
                text = font.render(f"{name}: {count} fragmentos", True, WHITE)
                screen.blit(text, (x_center - text.get_width() // 2, y_offset))
                y_offset += 25
        
        # Mostrar progreso total
        total_text = font.render(f"Total: {self.fragments_collected} fragmentos recuperados", True, GREEN)
        screen.blit(total_text, (x_center - total_text.get_width() // 2, y_offset + 10))
        
        # Mensaje especial si se tienen todos
        if self.fragments_collected >= 16:
            complete_text = font.render("¡ARCHIVO COMPLETO! La verdad ha sido revelada.", True, GREEN)
            screen.blit(complete_text, (x_center - complete_text.get_width() // 2, y_offset + 40))
    
    def draw_echo_portrait(self, screen):
        """Dibujar solo el retrato de Echo (para uso en otras pantallas)"""
        echo_image = self.echo_normal
        if self.current_message_type in ["alert", "code_red"]:
            echo_image = self.echo_problem
        
        # Posición fija para retrato
        portrait_x = 50
        portrait_y = 50
        screen.blit(echo_image, (portrait_x, portrait_y))
    
    def get_story_fragments(self):
        """Obtener todos los fragmentos de historia recolectados"""
        return self.story_fragments
    
    def get_fragments_count(self):
        """Obtener el número total de fragmentos recolectados"""
        return self.fragments_collected
    
    def get_narrative_summary(self):
        """Obtener un resumen narrativo basado en los fragmentos recolectados"""
        if self.fragments_collected == 0:
            return "Sin datos recuperados. La historia de XARN permanece oculta."
        elif self.fragments_collected < 5:
            return "Fragmentos iniciales recuperados. La historia comienza a revelarse."
        elif self.fragments_collected < 10:
            return "Datos significativos obtenidos. Los Kairon y su destino se hacen claros."
        elif self.fragments_collected < 16:
            return "Casi completo. La verdadera naturaleza de XARN está a punto de revelarse."
        else:
            return "Archivo completo. XARN es la culminación de incontables civilizaciones. El ciclo continúa."
    
    def has_active_message(self):
        """Verificar si hay un mensaje actualmente activo"""
        return self.current_message is not None
    
    def clear_current_message(self):
        """Limpiar mensaje actual (para uso manual)"""
        self.current_message = None
        self.current_message_type = "normal"
        self.message_timer = 0