"""
Definición de colores para Nebula Uprising
"""

# Colores básicos
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Colores específicos del juego
PLAYER_COLOR = GREEN
DRONE_COLOR = ORANGE
MARKOV_COLOR = PURPLE
BOSS_COLOR = RED
BULLET_COLOR = YELLOW
SHIELD_COLOR = CYAN

# Colores de UI
UI_BACKGROUND = (20, 20, 20)
HEALTH_BAR_BACKGROUND = (50, 50, 50)
HEALTH_GREEN = GREEN
HEALTH_YELLOW = YELLOW
HEALTH_RED = RED

# Colores de power-ups
POWERUP_COLORS = {
    "slow_time": BLUE,
    "shield": CYAN,
    "extra_life": GREEN
}

# Colores de estados de enemigos Markov
STATE_COLORS = {
    "DEAMBULAR": BLUE,
    "PATRULLAR": YELLOW,
    "ATACAR": RED
}