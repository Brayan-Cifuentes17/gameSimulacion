
"""
Nebula Uprising - Sector Zeta-9
Archivo principal con sistema de menú
"""

import pygame
import sys
import random
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game.game_manager import GameManager
from systems.menu import MenuScreen

class NebulaUprisingGame:
    def __init__(self):
        # Inicializar Pygame
        pygame.init()
        
        # Configurar pantalla
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Nebula Uprising - Sector Zeta-9")
        
        # Estados del juego
        self.game_state = "MENU"  # MENU, PLAYING, GAME_OVER
        
        # Inicializar sistemas
        self.menu_screen = MenuScreen(self.screen)
        self.game_manager = None
        self.clock = pygame.time.Clock()
        
        # Música y sonidos (opcional)
        self.setup_audio()
    
    def setup_audio(self):
        """Configurar audio del juego (opcional)"""
        # pygame.mixer.init()
        # Aquí puedes cargar música y efectos de sonido
        pass
    
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
                # Manejar menú
                result = self.menu_screen.handle_events(events)
                if result == "quit":
                    running = False
                
                self.menu_screen.update()
                self.menu_screen.draw()
                
                # Verificar si se inició el juego
                if self.menu_screen.game_started:
                    self.start_new_game()
                    self.game_state = "PLAYING"
            
            elif self.game_state == "PLAYING":
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
                
                # Dibujar
                self.game_manager.draw()
            
            elif self.game_state == "GAME_OVER":
                # Mostrar pantalla de game over
                self.game_manager.draw()
                
                # Manejar eventos de game over
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            # Volver al menú
                            self.return_to_menu()
                        elif event.key == pygame.K_ESCAPE:
                            # Volver al menú
                            self.return_to_menu()
                
                # Mostrar instrucción adicional
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
        self.game_manager = GameManager(self.screen)
        self.menu_screen.game_started = False
    
    def return_to_menu(self):
        """Volver al menú principal"""
        self.game_state = "MENU"
        self.menu_screen.reset()
        self.game_manager = None

def main():
    """Función principal"""
    game = NebulaUprisingGame()
    game.run()

if __name__ == "__main__":
    main()