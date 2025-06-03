"""
Configuraciones del juego Nebula Uprising
"""

# Configuración de pantalla
SCREEN_WIDTH = 650
SCREEN_HEIGHT = 700
FPS = 60

# Configuración del jugador
PLAYER_SPEED = 5
PLAYER_MAX_HEALTH = 100
PLAYER_WIDTH = 80
PLAYER_HEIGHT = 60

# Configuración de enemigos
DRONE_SPEED = 2
DRONE_SIZE = 30
MARKOV_SPEED = 3
MARKOV_SIZE = 35
BOSS_HEALTH = 400
BOSS_WIDTH = 80
BOSS_HEIGHT = 60

# Configuración de proyectiles
BULLET_SPEED = 10
BULLET_WIDTH = 4
BULLET_HEIGHT = 10
MISSILE_SPEED = 2.0

# Configuración de power-ups
POWERUP_SIZE = 20
POWERUP_SPEED = 2
SHIELD_DURATION = 240
SLOW_TIME_DURATION = 180

# Sistema de narrativa
MESSAGE_DURATION = 180

# Sistema de inactividad
MAX_INACTIVITY = 600  # 10 segundos a 60 FPS

# Probabilidades Monte Carlo para power-ups
POWERUP_PROBABILITIES = {
    "slow_time": 0.15,
    "shield": 0.20,
    "extra_life": 0.10,
    "none": 0.55
}

# Configuración de oleadas
WAVE_CONFIGS = {
    1: {
        "enemies": [("drone", 5)],
        "duration": 800,
        "spawn_rate": 120,
        "narrative": "first_wave",
        "name": "Reconocimiento XARN"
    },
    2: {
        "enemies": [("drone", 3), ("markov", 2)],
        "duration": 1000,
        "spawn_rate": 100,
        "narrative": "markov_enemy",
        "name": "Protocolo Adaptativo"
    },
    3: {
        "enemies": [("drone", 2), ("markov", 4)],
        "duration": 1200,
        "spawn_rate": 80,
        "narrative": None,
        "name": "Asalto Coordinado"
    },
    4: {
        "enemies": [("boss", 1)],
        "duration": -1,
        "spawn_rate": -1,
        "narrative": "boss_spawn",
        "name": "NÚCLEO XARN DETECTADO"
    }
}