"""
Sistema de Oleadas - Nebula Uprising
Maneja la progresión de oleadas y spawn de enemigos
"""

from collections import deque

class WaveQueue:
    def __init__(self):
        self.waves = deque()
        self.current_wave = None
        self.wave_timer = 0
        self.wave_number = 0
        self.narrative_triggered = {}
        
        # Definir oleadas con contexto narrativo
        self.define_waves()
    
    def define_waves(self):
        """Definir todas las oleadas del juego"""
        # Oleada 1: Reconocimiento XARN
        wave1 = {
            "enemies": [("drone", 5)],
            "duration": 3600,
            "spawn_rate": 50,
            "narrative": "first_wave",
            "name": "Reconocimiento XARN"
        }

        # Oleada 2: Drones Adaptativos
        wave2 = {
            "enemies": [("drone", 400), ("markov",200 )],
            "duration": 3600,
            "spawn_rate": 50,
            "narrative": "markov_enemy",
            "name": "Protocolo Adaptativo"
        }
        
        # Oleada 3: Asalto Coordinado
        wave3 = {
            "enemies": [("drone", 250), ("markov", 209)],
            "duration": 3600,
            "spawn_rate": 30,
            "narrative": None,
            "name": "Asalto Coordinado"
        }
        
        # Oleada 4: Núcleo XARN
        wave4 = {
            "enemies": [("boss", 1)],
            "duration": -1,
            "spawn_rate": -1,
            "narrative": "boss_spawn",
            "name": "NÚCLEO XARN DETECTADO"
        }
        
        self.waves.extend([wave1, wave2, wave3, wave4])
    
    def get_next_wave(self):
        """Obtener la siguiente oleada"""
        if self.waves:
            self.current_wave = self.waves.popleft()
            self.wave_number += 1
            self.wave_timer = 0
            return True
        return False
    
    def update(self):
        """Actualizar el sistema de oleadas"""
        if self.current_wave and self.current_wave["duration"] > 0:
            self.wave_timer += 1
            if self.wave_timer >= self.current_wave["duration"]:
                return "wave_complete"
        return None
    
    def get_current_wave_info(self):
        """Obtener información de la oleada actual"""
        if self.current_wave:
            return {
                "name": self.current_wave.get("name", f"Oleada {self.wave_number}"),
                "number": self.wave_number,
                "enemies": self.current_wave["enemies"],
                "spawn_rate": self.current_wave["spawn_rate"],
                "narrative": self.current_wave.get("narrative")
            }
        return None
    
    def is_boss_wave(self):
        """Verificar si la oleada actual es de jefe"""
        if self.current_wave:
            return any(enemy_type == "boss" for enemy_type, _ in self.current_wave["enemies"])
        return False
    
    def reset(self):
        """Reiniciar el sistema de oleadas"""
        self.waves.clear()
        self.current_wave = None
        self.wave_timer = 0
        self.wave_number = 0
        self.narrative_triggered.clear()
        self.define_waves()