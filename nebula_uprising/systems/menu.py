"""
Sistema de Menú Principal - Nebula Uprising
"""

import random
import pygame
from config.colors import *
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class MenuScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_subtitle = pygame.font.Font(None, 36)
        self.font_menu = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 24)
        
        # Opciones del menú
        self.menu_options = ["INICIAR MISIÓN", "SALIR"]
        self.selected_option = 0
        
        # Estado del menú
        self.active = True
        self.game_started = False
        
        # Animación
        self.animation_timer = 0
        self.star_positions = [(random.randint(0, SCREEN_WIDTH), 
                               random.randint(0, SCREEN_HEIGHT)) 
                              for _ in range(100)]
    
    def handle_events(self, events):
        """Manejar eventos del menú"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.selected_option == 0:  # Iniciar
                        self.game_started = True
                        self.active = False
                    elif self.selected_option == 1:  # Salir
                        return "quit"
        return None
    
    def update(self):
        """Actualizar animaciones del menú"""
        self.animation_timer += 1
        
        # Actualizar posición de estrellas
        for i in range(len(self.star_positions)):
            x, y = self.star_positions[i]
            y += 1
            if y > SCREEN_HEIGHT:
                y = 0
                x = random.randint(0, SCREEN_WIDTH)
            self.star_positions[i] = (x, y)
    
    def draw(self):
        """Dibujar el menú principal"""
        # Fondo
        self.screen.fill(BLACK)
        
        # Estrellas animadas
        for x, y in self.star_positions:
            size = random.choice([1, 2])
            pygame.draw.circle(self.screen, WHITE, (int(x), int(y)), size)
        
        # Título con efecto de brillo
        title_color = CYAN if self.animation_timer % 60 < 30 else WHITE
        title_text = self.font_title.render("NEBULA UPRISING", True, title_color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Subtítulo
        subtitle_text = self.font_subtitle.render("Sector Zeta-9", True, YELLOW)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 160))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Línea decorativa
        pygame.draw.line(self.screen, PURPLE, (150, 200), (SCREEN_WIDTH - 150, 200), 2)
        
        # Año y contexto
        context_text = self.font_small.render("Año 3172 - Confederación de Orión", True, WHITE)
        context_rect = context_text.get_rect(center=(SCREEN_WIDTH // 2, 230))
        self.screen.blit(context_text, context_rect)
        
        # Opciones del menú
        menu_y = 320
        for i, option in enumerate(self.menu_options):
            # Color según selección
            if i == self.selected_option:
                color = GREEN
                # Indicador de selección
                arrow = ">" if self.animation_timer % 30 < 15 else "»"
                arrow_text = self.font_menu.render(arrow, True, GREEN)
                self.screen.blit(arrow_text, (200, menu_y))
            else:
                color = WHITE
            
            option_text = self.font_menu.render(option, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, menu_y))
            self.screen.blit(option_text, option_rect)
            
            menu_y += 60
        
        # Instrucciones
        instructions = [
            "↑↓ - Navegar",
            "ENTER - Seleccionar",
            "← → - Mover nave",
            "ESPACIO - Disparar"
        ]
        
        inst_y = 480
        for instruction in instructions:
            inst_text = self.font_small.render(instruction, True, CYAN)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, inst_y))
            self.screen.blit(inst_text, inst_rect)
            inst_y += 25
        
        # Créditos
        credit_text = self.font_small.render("Comandante Nova - Escuadrón Centella", True, PURPLE)
        credit_rect = credit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(credit_text, credit_rect)
    
    def reset(self):
        """Resetear el estado del menú"""
        self.active = True
        self.game_started = False
        self.selected_option = 0