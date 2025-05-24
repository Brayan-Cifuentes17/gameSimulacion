"""
Sistema Narrativo - Nebula Uprising
Maneja los mensajes de ECHO y fragmentos de historia
"""

import pygame
from collections import deque
from config.colors import BLACK, CYAN, WHITE

class NarrativeSystem:
    def __init__(self):
        self.story_fragments = {
            "kairon_history": [],
            "project_lyra": [],
            "sleeping_network": []
        }
        self.messages_queue = deque()
        self.current_message = None
        self.message_timer = 0
        self.message_duration = 180
        
        self.echo_messages = {
            "intro": "Comandante Nova, aquí ECHO. Detectando múltiples señales hostiles en el sector Zeta-9.",
            "first_wave": "Análisis: Drones de reconocimiento XARN. Proceda con precaución.",
            "markov_enemy": "Alerta: Enemigos con patrones adaptativos detectados. Comportamiento impredecible.",
            "boss_spawn": "¡ADVERTENCIA CRÍTICA! Núcleo XARN detectado. Preparando protocolos de combate.",
            "low_health": "Comandante, integridad estructural comprometida. Busque poder de reparación.",
            "powerup_shield": "Escudo temporal activado. Duración limitada.",
            "powerup_slow": "Distorsión temporal detectada. Los enemigos se mueven más lento.",
            "powerup_life": "Sistemas de reparación activados. Integridad restaurada.",
            "fragment_found": "Datos recuperados. Analizando información sobre los Kairon...",
            "project_lyra": "¡Alerta! Archivos clasificados del Proyecto Lyra detectados.",
            "network_interference": "Interferencia anómala... ¿Otros sistemas están... escuchando?",
            "victory": "Núcleo XARN neutralizado. Pero esto es solo el comienzo, Comandante.",
            "defeat": "Sistemas críticos dañados. Protocolo de evacuación activado.",
            "inactivity": "Rendimiento inaceptable. Protocolo de retirada activado."
        }
        
        self.fragments_collected = 0
        self.xarn_data_unlocked = False
        
    def queue_message(self, message_key):
        """Encolar un mensaje de ECHO"""
        if message_key in self.echo_messages:
            self.messages_queue.append(self.echo_messages[message_key])
    
    def add_story_fragment(self, fragment_type, fragment):
        """Agregar un fragmento de historia"""
        if fragment_type in self.story_fragments:
            self.story_fragments[fragment_type].append(fragment)
            self.fragments_collected += 1
    
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
            # Crear superficie de texto
            text_surface = font.render(self.current_message, True, CYAN)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
            
            # Dibujar fondo translúcido
            padding = 10
            background = pygame.Surface((text_rect.width + padding * 2, text_rect.height + padding * 2))
            background.set_alpha(200)
            background.fill(BLACK)
            screen.blit(background, (text_rect.x - padding, text_rect.y - padding))
            
            # Dibujar texto
            screen.blit(text_surface, text_rect)
    
    def get_story_fragments(self):
        """Obtener todos los fragmentos de historia recolectados"""
        return self.story_fragments
    
    def get_fragments_count(self):
        """Obtener el número total de fragmentos recolectados"""
        return self.fragments_collected