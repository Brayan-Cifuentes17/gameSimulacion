"""
Utilidades Matemáticas - Nebula Uprising
Funciones auxiliares para cálculos matemáticos
"""

import math
import random
import numpy as np

def calculate_distance(x1, y1, x2, y2):
    """Calcular la distancia euclidiana entre dos puntos"""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def normalize_vector(dx, dy):
    """Normalizar un vector 2D"""
    distance = math.sqrt(dx**2 + dy**2)
    if distance == 0:
        return 0, 0
    return dx / distance, dy / distance

def angle_between_points(x1, y1, x2, y2):
    """Calcular el ángulo entre dos puntos"""
    return math.atan2(y2 - y1, x2 - x1)

def point_in_circle(px, py, cx, cy, radius):
    """Verificar si un punto está dentro de un círculo"""
    return calculate_distance(px, py, cx, cy) <= radius

def clamp(value, min_value, max_value):
    """Limitar un valor entre un mínimo y máximo"""
    return max(min_value, min(value, max_value))

def lerp(start, end, t):
    """Interpolación lineal entre dos valores"""
    return start + (end - start) * t

def random_point_in_circle(center_x, center_y, radius):
    """Generar un punto aleatorio dentro de un círculo"""
    angle = random.uniform(0, 2 * math.pi)
    r = random.uniform(0, radius)
    x = center_x + r * math.cos(angle)
    y = center_y + r * math.sin(angle)
    return x, y

def monte_carlo_choice(probabilities):
    """Hacer una elección usando Monte Carlo con probabilidades dadas"""
    rand = random.random()
    cumulative = 0
    
    for choice, prob in probabilities.items():
        cumulative += prob
        if rand <= cumulative:
            return choice if choice != "none" else None
    
    return None

def smooth_step(edge0, edge1, x):
    """Función de suavizado hermite"""
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def oscillate(time, frequency, amplitude=1.0, offset=0.0):
    """Generar una oscilación sinusoidal"""
    return offset + amplitude * math.sin(time * frequency)

def rotate_point(x, y, cx, cy, angle):
    """Rotar un punto alrededor de un centro"""
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    
    # Trasladar al origen
    tx = x - cx
    ty = y - cy
    
    # Rotar
    rx = tx * cos_angle - ty * sin_angle
    ry = tx * sin_angle + ty * cos_angle
    
    # Trasladar de vuelta
    return rx + cx, ry + cy

def create_polygon_points(center_x, center_y, radius, sides):
    """Crear puntos para un polígono regular"""
    points = []
    angle_step = 2 * math.pi / sides
    
    for i in range(sides):
        angle = i * angle_step
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    
    return points

# Matrices de transición para Cadenas de Markov
ENEMY_TRANSITION_MATRIX = np.array([
    [0.7, 0.2, 0.1],  # Desde DEAMBULAR
    [0.3, 0.5, 0.2],  # Desde PATRULLAR
    [0.1, 0.3, 0.6]   # Desde ATACAR
])

def markov_state_transition(current_state_index, transition_matrix):
    """Realizar transición de estado usando Cadenas de Markov"""
    probabilities = transition_matrix[current_state_index]
    return np.random.choice(len(probabilities), p=probabilities)

def gaussian_random(mean=0, std_dev=1):
    """Generar número aleatorio con distribución gaussiana"""
    return random.gauss(mean, std_dev)

def exponential_decay(initial_value, decay_rate, time):
    """Calcular decaimiento exponencial"""
    return initial_value * math.exp(-decay_rate * time)