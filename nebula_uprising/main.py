#!/usr/bin/env python3
"""
Nebula Uprising - Sector Zeta-9

"""

import pygame
import sys
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game.game_manager import GameManager

def main():
    """Función principal del juego"""
    # Inicializar Pygame
    pygame.init()
    
    # Configurar pantalla
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Nebula Uprising - Sector Zeta-9")
    
    # Inicializar el gestor del juego
    game_manager = GameManager(screen)
    
    # Bucle principal del juego
    running = True
    
    while running:
        # Obtener delta time
        dt = game_manager.clock.tick(FPS) / 1000.0
        
        # Manejar eventos
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        # Pasar eventos al game manager
        game_manager.handle_events(events)
        
        # Manejar input continuo
        keys = pygame.key.get_pressed()
        game_manager.handle_continuous_input(keys)
        
        # Actualizar juego
        game_manager.update(dt)
        
        # Dibujar
        game_manager.draw()
    
    # Limpiar y salir
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()