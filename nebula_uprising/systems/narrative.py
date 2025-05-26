"""
Sistema Narrativo - Nebula Uprising
Maneja los mensajes de ECHO y fragmentos de historia
"""

import pygame
from collections import deque
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
        self.message_timer = 0
        self.message_duration = 180
        
        self.echo_messages = {
            # Mensajes iniciales
            "intro": "Comandante Nova, aquí ECHO. Detectando múltiples señales hostiles en el sector Zeta-9.",
            "first_wave": "Análisis: Drones de reconocimiento XARN. Proceda con precaución.",
            "markov_enemy": "Alerta: Enemigos con patrones adaptativos detectados. Comportamiento impredecible.",
            "boss_spawn": "¡ADVERTENCIA CRÍTICA! Núcleo XARN detectado. Preparando protocolos de combate.",
            
            # Mensajes de estado
            "low_health": "Comandante, integridad estructural comprometida. Busque poder de reparación.",
            "colony_critical": "¡ALERTA! Las colonias están bajo ataque directo. Integridad crítica.",
            "colony_destroyed": "Transmisión final... Las colonias han caído. Zeta-9 está perdido.",
            
            # Power-ups
            "powerup_shield": "Escudo temporal activado. Duración limitada.",
            "powerup_slow": "Distorsión temporal detectada. Los enemigos se mueven más lento.",
            "powerup_life": "Sistemas de reparación activados. Integridad restaurada.",
            
            # Fragmentos de historia
            "fragment_found": "Datos recuperados. Analizando información sobre los Kairon...",
            "project_lyra": "¡Alerta! Archivos clasificados del Proyecto Lyra detectados.",
            "network_interference": "Interferencia anómala... ¿Otros sistemas están... escuchando?",
            "xarn_revelation": "Datos críticos: XARN no es lo que parece. Es algo mucho más antiguo.",
            
            # Mensajes de victoria/derrota
            "victory": "Núcleo XARN neutralizado. Pero esto es solo el comienzo, Comandante.",
            "victory_complete": "¡Increíble! Con todos los datos, ahora entendemos. XARN volverá... debemos prepararnos.",
            "defeat": "Sistemas críticos dañados. Protocolo de evacuación activado.",
            "inactivity": "Rendimiento inaceptable. Protocolo de retirada activado.",
            "colony_breached": "¡CÓDIGO ROJO! XARN ha alcanzado las colonias. Zeta-9 está perdido...",
            
            # Mensajes especiales por fragmentos
            "all_fragments_collected": "¡REVELACIÓN COMPLETA! Comandante, ahora lo veo todo... XARN es eterno.",
            "xarn_truth": "La verdad sobre XARN: No es una IA. Es la suma de todas las civilizaciones caídas.",
            "final_warning": "ECHO: Comandante... siento algo extraño en mi código. XARN está... aquí."
        }
        
        self.fragments_collected = 0
        self.xarn_data_unlocked = False
        
        # Control de revelaciones especiales
        self.special_revelations_shown = set()
        
    def queue_message(self, message_key):
        """Encolar un mensaje de ECHO"""
        if message_key in self.echo_messages:
            self.messages_queue.append(self.echo_messages[message_key])
    
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
    
    def update(self):
        """Actualizar el sistema narrativo"""
        if self.current_message:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.current_message = None
        elif self.messages_queue:
            self.current_message = self.messages_queue.popleft()
            self.message_timer = self.message_duration
    
    def draw(self, screen, font):
        """Dibujar mensajes narrativos"""
        if self.current_message:
            # Determinar color según tipo de mensaje
            message_color = CYAN
            if "ALERTA" in self.current_message or "ADVERTENCIA" in self.current_message:
                message_color = YELLOW
            elif "CÓDIGO ROJO" in self.current_message or "crítico" in self.current_message.lower():
                message_color = RED
            elif "REVELACIÓN" in self.current_message:
                message_color = PURPLE
            
            # Crear superficie de texto
            text_surface = font.render(self.current_message, True, message_color)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
            
            # Dibujar fondo translúcido
            padding = 10
            background = pygame.Surface((text_rect.width + padding * 2, text_rect.height + padding * 2))
            background.set_alpha(200)
            background.fill(BLACK)
            screen.blit(background, (text_rect.x - padding, text_rect.y - padding))
            
            # Efecto de parpadeo para mensajes críticos
            if message_color == RED and pygame.time.get_ticks() % 500 < 250:
                text_surface.set_alpha(180)
            
            # Dibujar texto
            screen.blit(text_surface, text_rect)
            
            # Indicador de ECHO
            echo_indicator = font.render("ECHO:", True, GREEN)
            screen.blit(echo_indicator, (text_rect.x - 50, text_rect.y))
    
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