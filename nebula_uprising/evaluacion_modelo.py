"""
Evaluación Independiente de Modelos de Simulación - Nebula Uprising
Este módulo permite probar cada modelo de simulación de forma aislada
siguiendo la estructura del juego original.
"""

import numpy as np
import matplotlib.pyplot as plt
import random
from collections import defaultdict, Counter
from enum import Enum
import math

# =====================================================
# MODELO 1: GENERADOR LCG (Linear Congruential Generator)
# =====================================================

class PseudoRandom:
    """
    Generador de números pseudoaleatorios usando el Método Congruencial Lineal (LCG).
    MODELO INDEPENDIENTE para evaluación.
    """
    
    def __init__(self, seed=12345):
        """
        Inicializar el generador LCG.
        
        Args:
            seed: Semilla inicial para la secuencia
        """
        # Parámetros del LCG (valores comunes para buenos generadores)
        self.seed = seed
        self.multiplier = 1664525
        self.increment = 1013904223
        self.modulus = 2**32
        
        # Estado actual del generador
        self.current = seed
        self.original_seed = seed
        self.call_count = 0

    def next(self):
        """
        Generar el siguiente número pseudoaleatorio normalizado [0,1).
        
        Returns:
            float: Número pseudoaleatorio entre 0 y 1
        """
        # Aplicar la fórmula LCG: Xn+1 = (a * Xn + c) mod m
        self.current = (self.multiplier * self.current + self.increment) % self.modulus
        self.call_count += 1
        
        # Normalizar al rango [0,1)
        return self.current / self.modulus

    def next_choice(self, choices):
        """
        Elegir un elemento aleatorio de una lista.
        
        Args:
            choices: Lista de opciones para elegir
            
        Returns:
            Elemento elegido de la lista
        """
        if not choices:
            raise ValueError("La lista de opciones no puede estar vacía")
            
        rand = self.next()
        index = int(rand * len(choices)) % len(choices)
        return choices[index]
    
    def reset(self, new_seed=None):
        """Resetear el generador con una nueva semilla o la original."""
        if new_seed is not None:
            self.seed = new_seed
            self.original_seed = new_seed
        else:
            self.seed = self.original_seed
        self.current = self.seed
        self.call_count = 0

def test_lcg_model():
    """
    Evaluación independiente del modelo LCG.
    """
    print("=" * 60)
    print("EVALUACIÓN INDEPENDIENTE: Modelo LCG")
    print("=" * 60)
    
    # Test 1: Uniformidad de distribución
    print("\n1. Test de Uniformidad:")
    prng = PseudoRandom(seed=12345)
    samples = [prng.next() for _ in range(10000)]
    
    # Dividir en 10 bins y verificar uniformidad
    bins = [0] * 10
    for sample in samples:
        bin_index = min(int(sample * 10), 9)
        bins[bin_index] += 1
    
    expected = 1000  # 10000/10
    chi_square = sum((observed - expected)**2 / expected for observed in bins)
    
    print(f"Distribución por bins: {bins}")
    print(f"Chi-cuadrado: {chi_square:.2f} (menor que 16.92 = bueno)")
    print(f"Uniformidad: {'APROBADO' if chi_square < 16.92 else 'REPROBADO'}")
    
    # Test 2: Periodo del generador
    print("\n2. Test de Periodo:")
    prng.reset()
    initial_state = prng.current
    period = 0
    
    for i in range(100000):  # Límite para evitar bucle infinito
        prng.next()
        period += 1
        if prng.current == initial_state:
            break
    
    print(f"Periodo encontrado: {period} iteraciones")
    print(f"Período teórico máximo: {2**32}")
    
    # Test 3: Reproducibilidad
    print("\n3. Test de Reproducibilidad:")
    prng1 = PseudoRandom(seed=67890)
    prng2 = PseudoRandom(seed=67890)
    
    sequence1 = [prng1.next() for _ in range(100)]
    sequence2 = [prng2.next() for _ in range(100)]
    
    reproducible = sequence1 == sequence2
    print(f"Secuencias idénticas con misma semilla: {'SÍ' if reproducible else 'NO'}")
    
    # Test 4: Uso en selección de direcciones (como en el juego)
    print("\n4. Test de Selección de Direcciones:")
    prng.reset(12345)
    directions = []
    for _ in range(1000):
        direction = prng.next_choice([-1, 1])
        directions.append(direction)
    
    left_count = directions.count(-1)
    right_count = directions.count(1)
    balance = abs(left_count - right_count) / 1000
    
    print(f"Izquierda: {left_count}, Derecha: {right_count}")
    print(f"Desbalance: {balance:.3f} (menor que 0.1 = bueno)")
    
    return {
        'uniformidad': chi_square < 16.92,
        'reproducibilidad': reproducible,
        'balance_direcciones': balance < 0.1
    }

# =====================================================
# MODELO 2: CADENAS DE MARKOV
# =====================================================

class EnemyState(Enum):
    DEAMBULAR = 0
    PATRULLAR = 1
    ATACAR = 2

class MarkovEnemyModel:
    """
    Modelo independiente de Cadenas de Markov para comportamiento enemigo.
    """
    
    def __init__(self, initial_state=EnemyState.DEAMBULAR):
        # Matriz de transición del juego original
        self.transition_matrix = np.array([
            [0.7, 0.2, 0.1],  # Desde DEAMBULAR
            [0.3, 0.5, 0.2],  # Desde PATRULLAR
            [0.1, 0.3, 0.6]   # Desde ATACAR
        ])
        
        self.current_state = initial_state
        self.state_history = [initial_state]
        self.transition_count = 0
        
    def change_state(self):
        """Cambiar estado usando matriz de transición"""
        current_state_index = self.current_state.value
        probabilities = self.transition_matrix[current_state_index]
        new_state_index = np.random.choice(3, p=probabilities)
        self.current_state = EnemyState(new_state_index)
        self.state_history.append(self.current_state)
        self.transition_count += 1
    
    def get_state_distribution(self, steps=1000):
        """Simular n pasos y obtener distribución de estados"""
        for _ in range(steps):
            self.change_state()
        
        state_counts = Counter(self.state_history)
        total = len(self.state_history)
        
        return {
            state.name: count/total 
            for state, count in state_counts.items()
        }
    
    def calculate_steady_state(self):
        """Calcular distribución estacionaria teórica"""
        # Resolver π = π * P donde π es la distribución estacionaria
        eigenvals, eigenvecs = np.linalg.eig(self.transition_matrix.T)
        steady_state = eigenvecs[:, np.argmax(eigenvals)].real
        steady_state = steady_state / steady_state.sum()
        
        return {
            'DEAMBULAR': steady_state[0],
            'PATRULLAR': steady_state[1], 
            'ATACAR': steady_state[2]
        }

def test_markov_model():
    """
    Evaluación independiente del modelo de Cadenas de Markov.
    """
    print("=" * 60)
    print("EVALUACIÓN INDEPENDIENTE: Modelo Cadenas de Markov")
    print("=" * 60)
    
    # Test 1: Convergencia a distribución estacionaria
    print("\n1. Test de Convergencia:")
    model = MarkovEnemyModel()
    
    # Distribución teórica
    theoretical = model.calculate_steady_state()
    print("Distribución estacionaria teórica:")
    for state, prob in theoretical.items():
        print(f"  {state}: {prob:.3f}")
    
    # Distribución empírica
    model_test = MarkovEnemyModel()
    empirical = model_test.get_state_distribution(10000)
    print("\nDistribución empírica (10000 pasos):")
    for state, prob in empirical.items():
        print(f"  {state}: {prob:.3f}")
    
    # Calcular diferencia
    differences = []
    for state in theoretical.keys():
        diff = abs(theoretical[state] - empirical.get(state, 0))
        differences.append(diff)
    
    max_diff = max(differences)
    converged = max_diff < 0.05
    print(f"\nMáxima diferencia: {max_diff:.4f}")
    print(f"Convergencia: {'APROBADO' if converged else 'REPROBADO'}")
    
    # Test 2: Propiedad de Markov (sin memoria)
    print("\n2. Test de Propiedad de Markov:")
    model_memory = MarkovEnemyModel()
    
    # Simular secuencias desde diferentes historias
    sequences_from_attack = []
    sequences_from_patrol = []
    
    for _ in range(1000):
        # Forzar estado ATACAR y observar siguiente
        model_memory.current_state = EnemyState.ATACAR
        model_memory.change_state()
        sequences_from_attack.append(model_memory.current_state)
        
        # Forzar estado PATRULLAR y observar siguiente  
        model_memory.current_state = EnemyState.PATRULLAR
        model_memory.change_state()
        sequences_from_patrol.append(model_memory.current_state)
    
    # Verificar que las transiciones solo dependen del estado actual
    attack_transitions = Counter(sequences_from_attack)
    patrol_transitions = Counter(sequences_from_patrol)
    
    print("Transiciones desde ATACAR:", dict(attack_transitions))
    print("Transiciones desde PATRULLAR:", dict(patrol_transitions))
    
    # Test 3: Validación de matriz estocástica
    print("\n3. Test de Matriz Estocástica:")
    matrix = model.transition_matrix
    
    # Verificar que cada fila suma 1
    row_sums = np.sum(matrix, axis=1)
    stochastic = np.allclose(row_sums, 1.0)
    
    print(f"Sumas por fila: {row_sums}")
    print(f"Matriz estocástica: {'SÍ' if stochastic else 'NO'}")
    
    # Test 4: Tiempo promedio en cada estado
    print("\n4. Test de Tiempo de Residencia:")
    model_residence = MarkovEnemyModel()
    state_durations = {state: [] for state in EnemyState}
    current_duration = 1
    
    for i in range(5000):
        prev_state = model_residence.current_state
        model_residence.change_state()
        
        if model_residence.current_state == prev_state:
            current_duration += 1
        else:
            state_durations[prev_state].append(current_duration)
            current_duration = 1
    
    print("Tiempo promedio de residencia:")
    for state, durations in state_durations.items():
        if durations:
            avg_duration = np.mean(durations)
            theoretical_duration = 1 / (1 - matrix[state.value, state.value])
            print(f"  {state.name}: {avg_duration:.2f} (teórico: {theoretical_duration:.2f})")
    
    return {
        'convergencia': converged,
        'matriz_estocástica': stochastic,
        'max_diferencia': max_diff
    }

# =====================================================
# MODELO 3: MÉTODO MONTE CARLO
# =====================================================

class MonteCarloModel:
    """
    Modelo independiente de Monte Carlo para generación de power-ups.
    """
    
    def __init__(self, seed=67890):
        # Configuración del juego original
        self.powerup_types = ["slow_time", "shield", "extra_life", "none"]
        self.powerup_probabilities = [0.15, 0.10, 0.05, 0.70]
        self.powerup_cumulative = np.cumsum(self.powerup_probabilities)
        
        # Usar el LCG del juego
        self.prng = PseudoRandom(seed=seed)
        
        # Estadísticas
        self.generation_history = []
        self.call_count = 0
        
    def generate_powerup(self):
        """Determina power-up usando secuencia pseudoaleatoria y matriz acumulativa."""
        rand = self.prng.next()
        self.call_count += 1
        
        for i, threshold in enumerate(self.powerup_cumulative):
            if rand <= threshold:
                chosen = self.powerup_types[i]
                result = None if chosen == "none" else chosen
                self.generation_history.append(result)
                return result
        
        # Fallback (no debería llegar aquí)
        self.generation_history.append(None)
        return None
    
    def simulate_drops(self, enemy_kills=1000, drop_rate=0.15):
        """Simular drops de power-ups por matar enemigos."""
        drops = []
        
        for _ in range(enemy_kills):
            # Primero verificar si dropea algo (como en el juego)
            if self.prng.next() < drop_rate:
                powerup = self.generate_powerup()
                drops.append(powerup)
            else:
                drops.append(None)  # No drop
        
        return drops
    
    def get_distribution_stats(self, samples):
        """Calcular estadísticas de distribución."""
        counter = Counter(samples)
        total = len(samples)
        
        distribution = {}
        for powerup_type in self.powerup_types:
            key = powerup_type if powerup_type != "none" else None
            count = counter.get(key, 0)
            distribution[powerup_type] = count / total if total > 0 else 0
        
        return distribution

def test_monte_carlo_model():
    """
    Evaluación independiente del modelo Monte Carlo.
    """
    print("=" * 60)
    print("EVALUACIÓN INDEPENDIENTE: Modelo Monte Carlo")
    print("=" * 60)
    
    # Test 1: Distribución de probabilidades
    print("\n1. Test de Distribución de Probabilidades:")
    model = MonteCarloModel(seed=67890)
    
    # Generar muchas muestras
    samples = []
    for _ in range(10000):
        powerup = model.generate_powerup()
        samples.append(powerup)
    
    # Calcular distribución empírica
    empirical = model.get_distribution_stats(samples)
    theoretical = dict(zip(model.powerup_types, model.powerup_probabilities))
    
    print("Distribución teórica vs empírica:")
    chi_square = 0
    for powerup_type in model.powerup_types:
        theo = theoretical[powerup_type]
        emp = empirical[powerup_type]
        diff = abs(theo - emp)
        
        # Contribución al chi-cuadrado
        expected_count = theo * len(samples)
        observed_count = emp * len(samples)
        if expected_count > 0:
            chi_square += (observed_count - expected_count)**2 / expected_count
        
        print(f"  {powerup_type}: teórico={theo:.3f}, empírico={emp:.3f}, diff={diff:.4f}")
    
    print(f"\nChi-cuadrado: {chi_square:.3f} (menor que 7.815 = bueno)")
    distribution_ok = chi_square < 7.815
    
    # Test 2: Reproducibilidad con misma semilla
    print("\n2. Test de Reproducibilidad:")
    model1 = MonteCarloModel(seed=12345)
    model2 = MonteCarloModel(seed=12345)
    
    sequence1 = [model1.generate_powerup() for _ in range(100)]
    sequence2 = [model2.generate_powerup() for _ in range(100)]
    
    reproducible = sequence1 == sequence2
    print(f"Secuencias idénticas: {'SÍ' if reproducible else 'NO'}")
    
    # Test 3: Simulación realista de juego
    print("\n3. Test de Simulación de Juego:")
    model_game = MonteCarloModel(seed=98765)
    
    # Simular 1000 enemigos muertos con 15% drop rate
    drops = model_game.simulate_drops(enemy_kills=1000, drop_rate=0.15)
    
    # Contar drops reales (excluyendo None)
    actual_drops = [drop for drop in drops if drop is not None]
    drop_rate_empirical = len(actual_drops) / 1000
    
    print(f"Enemies killed: 1000")
    print(f"Drop rate teórico: 15%")
    print(f"Drop rate empírico: {drop_rate_empirical:.1%}")
    print(f"Power-ups obtenidos: {len(actual_drops)}")
    
    # Distribución de tipos de power-ups obtenidos
    if actual_drops:
        drop_distribution = Counter(actual_drops)
        print("\nDistribución de power-ups obtenidos:")
        for powerup, count in drop_distribution.items():
            percentage = count / len(actual_drops) * 100
            print(f"  {powerup}: {count} ({percentage:.1f}%)")
    
    # Test 4: Convergencia con más muestras
    print("\n4. Test de Convergencia:")
    model_convergence = MonteCarloModel(seed=11111)
    
    sample_sizes = [100, 500, 1000, 5000, 10000]
    convergence_data = []
    
    for n in sample_sizes:
        model_convergence.prng.reset(11111)  # Reset para cada prueba
        samples_n = [model_convergence.generate_powerup() for _ in range(n)]
        dist_n = model_convergence.get_distribution_stats(samples_n)
        
        # Calcular error máximo respecto a distribución teórica
        max_error = max(abs(theoretical[ptype] - dist_n[ptype]) 
                       for ptype in model.powerup_types)
        convergence_data.append((n, max_error))
        
        print(f"  n={n:5d}: error máximo = {max_error:.4f}")
    
    # Verificar que el error decrece
    errors = [error for _, error in convergence_data]
    converging = all(errors[i] >= errors[i+1] for i in range(len(errors)-2))
    
    return {
        'distribucion_correcta': distribution_ok,
        'reproducible': reproducible,
        'drop_rate_ok': abs(drop_rate_empirical - 0.15) < 0.03,
        'convergencia': converging,
        'chi_cuadrado': chi_square
    }

# =====================================================
# MODELO 4: SIMULACIÓN BASADA EN AGENTES (BOSS)
# =====================================================

class BossAgentModel:
    """
    Modelo independiente de simulación basada en agentes para el jefe final.
    """
    
    def __init__(self, initial_health=250):
        # Estados del jefe
        self.health = initial_health
        self.max_health = initial_health
        self.behavior_state = "defensive"
        self.speed = 2
        self.corruption_level = 0
        
        # Posición simulada
        self.x = 325  # Centro de pantalla (650/2)
        self.y = 50
        
        # Timers y contadores
        self.attack_timer = 0
        self.time_elapsed = 0
        
        # Estadísticas para evaluación
        self.behavior_history = []
        self.attack_history = []
        self.decision_log = []
        
    def think_and_act(self, player_x=325, player_y=700):
        """Sistema de decisión basado en el contexto (simulado)"""
        self.time_elapsed += 1
        
        # Calcular métricas de decisión
        player_distance = abs(self.x - player_x)
        health_percentage = self.health / self.max_health
        
        # Log de decisión
        decision_context = {
            'health_percentage': health_percentage,
            'player_distance': player_distance,
            'time': self.time_elapsed
        }
        
        # Cambiar comportamiento según el contexto (lógica del juego original)
        old_behavior = self.behavior_state
        
        if health_percentage < 0.3:
            self.behavior_state = "aggressive"
            self.speed = 6
        elif health_percentage < 0.6:
            self.behavior_state = "balanced"
            self.speed = 5
        else:
            self.behavior_state = "defensive"
            self.speed = 3
        
        # Registrar cambio de comportamiento
        if old_behavior != self.behavior_state:
            self.behavior_history.append({
                'time': self.time_elapsed,
                'old_state': old_behavior,
                'new_state': self.behavior_state,
                'trigger_health': health_percentage
            })
        
        # Sistema de ataque
        attack_frequency = self._get_attack_frequency()
        self.attack_timer += 1
        
        if self.attack_timer >= attack_frequency:
            self.attack_history.append({
                'time': self.time_elapsed,
                'behavior': self.behavior_state,
                'health': health_percentage
            })
            self.attack_timer = 0
        
        # Aumentar corrupción con el tiempo
        self.corruption_level = min(100, self.corruption_level + 0.1)
        
        # Registrar decisión
        decision_context.update({
            'behavior_chosen': self.behavior_state,
            'attack_frequency': attack_frequency,
            'corruption': self.corruption_level
        })
        self.decision_log.append(decision_context)
        
        return self.behavior_state
    
    def _get_attack_frequency(self):
        """Obtener frecuencia de ataque según comportamiento"""
        if self.behavior_state == "aggressive":
            return 40  # Muy rápido
        elif self.behavior_state == "balanced":
            return 80  # Moderado
        else:
            return 120  # Lento
    
    def take_damage(self, damage=5):
        """Recibir daño y retornar si fue destruido"""
        self.health -= damage
        return self.health <= 0
    
    def get_performance_metrics(self):
        """Obtener métricas de performance del agente"""
        if not self.decision_log:
            return {}
        
        # Análisis de comportamiento
        behavior_distribution = Counter(d['behavior_chosen'] for d in self.decision_log)
        total_decisions = len(self.decision_log)
        
        # Análisis de adaptabilidad
        health_thresholds = [0.6, 0.3]
        adaptations = 0
        
        for change in self.behavior_history:
            if any(abs(change['trigger_health'] - threshold) < 0.05 
                  for threshold in health_thresholds):
                adaptations += 1
        
        # Frecuencia de ataque promedio
        avg_attack_freq = np.mean([d.get('attack_frequency', 80) for d in self.decision_log])
        
        return {
            'behavior_distribution': dict(behavior_distribution),
            'total_decisions': total_decisions,
            'behavior_changes': len(self.behavior_history),
            'adaptive_changes': adaptations,
            'attacks_performed': len(self.attack_history),
            'avg_attack_frequency': avg_attack_freq,
            'final_corruption': self.corruption_level
        }

def test_boss_agent_model():
    """
    Evaluación independiente del modelo de agentes del jefe.
    """
    print("=" * 60)
    print("EVALUACIÓN INDEPENDIENTE: Modelo Agentes (Boss)")
    print("=" * 60)
    
    # Test 1: Adaptabilidad según salud
    print("\n1. Test de Adaptabilidad según Salud:")
    boss = BossAgentModel(initial_health=250)
    
    # Simular combate con pérdida gradual de salud
    health_states = []
    behavior_states = []
    
    for step in range(1000):
        # Simular daño gradual
        if step % 20 == 0 and boss.health > 0:  # Daño cada 20 frames
            boss.take_damage(5)
        
        # Tomar decisión
        behavior = boss.think_and_act()
        
        health_states.append(boss.health / boss.max_health)
        behavior_states.append(behavior)
        
        if boss.health <= 0:
            break
    
    # Verificar transiciones de comportamiento
    behavior_changes = boss.behavior_history
    print(f"Cambios de comportamiento detectados: {len(behavior_changes)}")
    
    for change in behavior_changes:
        print(f"  Frame {change['time']}: {change['old_state']} → {change['new_state']} "
              f"(salud: {change['trigger_health']:.2f})")
    
    # Verificar umbrales correctos
    correct_transitions = 0
    for change in behavior_changes:
        health = change['trigger_health']
        new_state = change['new_state']
        
        if ((health < 0.3 and new_state == "aggressive") or
            (0.3 <= health < 0.6 and new_state == "balanced") or
            (health >= 0.6 and new_state == "defensive")):
            correct_transitions += 1
    
    adaptability_score = correct_transitions / max(len(behavior_changes), 1)
    print(f"Transiciones correctas: {correct_transitions}/{len(behavior_changes)}")
    print(f"Score de adaptabilidad: {adaptability_score:.2f}")
    
    # Test 2: Escalamiento de agresividad
    print("\n2. Test de Escalamiento de Agresividad:")
    boss2 = BossAgentModel(initial_health=250)
    
    # Probar diferentes niveles de salud
    health_levels = [1.0, 0.8, 0.5, 0.2, 0.1]
    attack_frequencies = []
    
    for health_pct in health_levels:
        boss2.health = int(boss2.max_health * health_pct)
        boss2.think_and_act()
        attack_freq = boss2._get_attack_frequency()
        attack_frequencies.append(attack_freq)
        
        print(f"  Salud {health_pct:.1%}: comportamiento={boss2.behavior_state}, "
              f"freq_ataque={attack_freq}")
    
    # Verificar que la frecuencia aumenta (números menores = más rápido)
    aggression_increases = all(attack_frequencies[i] >= attack_frequencies[i+1] 
                              for i in range(len(attack_frequencies)-1))
    print(f"Escalamiento de agresividad: {'CORRECTO' if aggression_increases else 'INCORRECTO'}")
    
    # Test 3: Consistencia de decisiones
    print("\n3. Test de Consistencia de Decisiones:")
    boss3 = BossAgentModel(initial_health=250)
    
    # Probar mismas condiciones múltiples veces
    consistent_decisions = 0
    total_tests = 100
    
    for _ in range(total_tests):
        # Establecer condiciones fijas
        boss3.health = 100  # 40% de salud
        boss3.corruption_level = 50
        boss3.time_elapsed = 500
        
        behavior1 = boss3.think_and_act(player_x=300, player_y=700)
        
        # Reset y repetir
        boss3.health = 100
        boss3.corruption_level = 50
        boss3.time_elapsed = 500
        
        behavior2 = boss3.think_and_act(player_x=300, player_y=700)
        
        if behavior1 == behavior2:
            consistent_decisions += 1
    
    consistency_rate = consistent_decisions / total_tests
    print(f"Decisiones consistentes: {consistent_decisions}/{total_tests}")
    print(f"Tasa de consistencia: {consistency_rate:.2%}")
    
    # Test 4: Métricas de performance
    print("\n4. Métricas de Performance:")
    metrics = boss.get_performance_metrics()
    
    print("Distribución de comportamientos:")
    for behavior, count in metrics['behavior_distribution'].items():
        percentage = count / metrics['total_decisions'] * 100
        print(f"  {behavior}: {count} decisiones ({percentage:.1f}%)")
    
    print(f"\nTotal de decisiones: {metrics['total_decisions']}")
    print(f"Cambios de comportamiento: {metrics['behavior_changes']}")
    print(f"Ataques realizados: {metrics['attacks_performed']}")
    print(f"Frecuencia promedio de ataque: {metrics['avg_attack_frequency']:.1f}")
    print(f"Corrupción final: {metrics['final_corruption']:.1f}%")
    
    return {
        'adaptabilidad': adaptability_score >= 0.8,
        'escalamiento_correcto': aggression_increases,
        'consistencia': consistency_rate >= 0.95,
        'cambios_comportamiento': len(behavior_changes) >= 2
    }

# =====================================================
# MODELO 5: CAMINATA ALEATORIA
# =====================================================

class RandomWalkModel:
    """
    Modelo independiente de caminata aleatoria para drones básicos.
    """
    
    def __init__(self, screen_width=650, drone_size=30, margin=15, seed=12345):
        self.screen_width = screen_width
        self.drone_size = drone_size
        self.margin = margin
        self.speed = 2
        
        # Estado del drone
        self.x = screen_width // 2
        self.direction = 1  # 1 = derecha, -1 = izquierda
        self.move_timer = 0
        self.move_interval = 30
        
        # Generador pseudoaleatorio
        self.prng = PseudoRandom(seed=seed)
        
        # Estadísticas para evaluación
        self.position_history = []
        self.direction_history = []
        self.collision_count = 0
        self.forced_direction_changes = 0
        self.random_direction_changes = 0
        
    def update(self):
        """Actualizar comportamiento del drone (lógica del juego original)"""
        # Aplicar factor de tiempo
        self.move_timer += 1
        
        if self.move_timer >= self.move_interval:
            old_direction = self.direction
            
            # Si está cerca de un borde, forzar dirección opuesta
            if self.x <= self.margin:
                self.direction = 1  # Forzar movimiento a la derecha
                self.forced_direction_changes += 1
            elif self.x >= self.screen_width - self.drone_size - self.margin:
                self.direction = -1  # Forzar movimiento a la izquierda
                self.forced_direction_changes += 1
            else:
                # Solo elegir dirección aleatoria si no está cerca de bordes
                self.direction = self.prng.next_choice([-1, 1])
                if old_direction != self.direction:
                    self.random_direction_changes += 1
            
            self.move_timer = 0
            self.move_interval = int(30 + self.prng.next() * 30)  # [30, 60]
        
        # Mover el drone
        old_x = self.x
        self.x += self.direction * self.speed
        
        # Limitar posición dentro de la pantalla
        self.x = max(0, min(self.x, self.screen_width - self.drone_size))
        
        # Detectar colisiones con bordes
        if self.x != old_x + (self.direction * self.speed):
            self.collision_count += 1
        
        # Registrar posición y dirección
        self.position_history.append(self.x)
        self.direction_history.append(self.direction)
    
    def simulate_movement(self, steps=1000):
        """Simular movimiento por n pasos"""
        for _ in range(steps):
            self.update()
    
    def get_movement_statistics(self):
        """Calcular estadísticas del movimiento"""
        if not self.position_history:
            return {}
        
        positions = np.array(self.position_history)
        directions = np.array(self.direction_history)
        
        # Estadísticas básicas
        stats = {
            'mean_position': np.mean(positions),
            'std_position': np.std(positions),
            'min_position': np.min(positions),
            'max_position': np.max(positions),
            'position_range': np.max(positions) - np.min(positions),
            'total_collisions': self.collision_count,
            'forced_changes': self.forced_direction_changes,
            'random_changes': self.random_direction_changes,
            'steps_simulated': len(positions)
        }
        
        # Análisis de direcciones
        left_steps = np.sum(directions == -1)
        right_steps = np.sum(directions == 1)
        stats['left_bias'] = left_steps / len(directions) if directions.size > 0 else 0
        stats['right_bias'] = right_steps / len(directions) if directions.size > 0 else 0
        stats['direction_balance'] = abs(stats['left_bias'] - 0.5)
        
        # Análisis de confinamiento
        center = self.screen_width // 2
        stats['center_bias'] = abs(stats['mean_position'] - center) / center
        
        # Análisis de variabilidad temporal
        if len(positions) > 1:
            position_changes = np.diff(positions)
            stats['avg_displacement'] = np.mean(np.abs(position_changes))
            stats['movement_variance'] = np.var(position_changes)
        
        return stats

def test_random_walk_model():
    """
    Evaluación independiente del modelo de caminata aleatoria.
    """
    print("=" * 60)
    print("EVALUACIÓN INDEPENDIENTE: Modelo Caminata Aleatoria")
    print("=" * 60)
    
    # Test 1: Confinamiento espacial
    print("\n1. Test de Confinamiento Espacial:")
    drone = RandomWalkModel(screen_width=650, drone_size=30, margin=15, seed=12345)
    
    # Simular movimiento largo
    drone.simulate_movement(steps=2000)
    stats = drone.get_movement_statistics()
    
    # Verificar que se mantiene dentro de límites
    within_bounds = (stats['min_position'] >= 0 and 
                    stats['max_position'] <= drone.screen_width - drone.drone_size)
    
    print(f"Posición mínima: {stats['min_position']:.1f}")
    print(f"Posición máxima: {stats['max_position']:.1f}")
    print(f"Rango válido: [0, {drone.screen_width - drone.drone_size}]")
    print(f"Confinamiento: {'CORRECTO' if within_bounds else 'INCORRECTO'}")
    
    # Test 2: Balance direccional
    print("\n2. Test de Balance Direccional:")
    print(f"Bias izquierda: {stats['left_bias']:.3f}")
    print(f"Bias derecha: {stats['right_bias']:.3f}")
    print(f"Desbalance: {stats['direction_balance']:.3f}")
    
    balanced = stats['direction_balance'] < 0.1  # Menos del 10% de sesgo
    print(f"Balance direccional: {'BUENO' if balanced else 'SESGADO'}")
    
    # Test 3: Comportamiento cerca de bordes
    print("\n3. Test de Comportamiento en Bordes:")
    drone_edge = RandomWalkModel(screen_width=650, drone_size=30, margin=15, seed=98765)
    
    # Posicionar cerca del borde izquierdo
    drone_edge.x = 10  # Dentro del margen
    edge_test_steps = 100
    
    left_edge_directions = []
    for _ in range(edge_test_steps):
        if drone_edge.x <= drone_edge.margin:
            drone_edge.update()
            left_edge_directions.append(drone_edge.direction)
        else:
            break
    
    # Verificar que fuerza movimiento a la derecha
    forced_right = all(direction == 1 for direction in left_edge_directions)
    print(f"Direcciones forzadas en borde izquierdo: {left_edge_directions[:10]}")
    print(f"Forzado hacia derecha: {'SÍ' if forced_right else 'NO'}")
    
    # Test similar para borde derecho
    drone_edge.x = drone_edge.screen_width - drone_edge.drone_size - 10
    right_edge_directions = []
    
    for _ in range(edge_test_steps):
        if drone_edge.x >= drone_edge.screen_width - drone_edge.drone_size - drone_edge.margin:
            drone_edge.update()
            right_edge_directions.append(drone_edge.direction)
        else:
            break
    
    forced_left = all(direction == -1 for direction in right_edge_directions)
    print(f"Direcciones forzadas en borde derecho: {right_edge_directions[:10]}")
    print(f"Forzado hacia izquierda: {'SÍ' if forced_left else 'NO'}")
    
    # Test 4: Variabilidad de intervalos
    print("\n4. Test de Variabilidad de Intervalos:")
    drone_interval = RandomWalkModel(seed=11111)
    
    intervals = []
    for _ in range(200):
        drone_interval.move_timer = drone_interval.move_interval  # Forzar cambio
        drone_interval.update()
        intervals.append(drone_interval.move_interval)
    
    interval_stats = {
        'min_interval': min(intervals),
        'max_interval': max(intervals),
        'mean_interval': np.mean(intervals),
        'std_interval': np.std(intervals)
    }
    
    print(f"Intervalo mínimo: {interval_stats['min_interval']}")
    print(f"Intervalo máximo: {interval_stats['max_interval']}")
    print(f"Intervalo promedio: {interval_stats['mean_interval']:.1f}")
    print(f"Desviación estándar: {interval_stats['std_interval']:.1f}")
    
    # Verificar rango esperado [30, 60]
    intervals_in_range = all(30 <= interval < 60 for interval in intervals)
    print(f"Intervalos en rango [30,60): {'SÍ' if intervals_in_range else 'NO'}")
    
    # Test 5: Análisis de distribución espacial
    print("\n5. Test de Distribución Espacial:")
    print(f"Posición promedio: {stats['mean_position']:.1f}")
    print(f"Centro teórico: {drone.screen_width // 2}")
    print(f"Sesgo hacia centro: {stats['center_bias']:.3f}")
    print(f"Desviación estándar: {stats['std_position']:.1f}")
    print(f"Rango explorado: {stats['position_range']:.1f} de {drone.screen_width}")
    
    # Verificar que explora suficiente espacio
    exploration_ratio = stats['position_range'] / drone.screen_width
    good_exploration = exploration_ratio > 0.7  # Explora al menos 70% del espacio
    
    print(f"Ratio de exploración: {exploration_ratio:.2f}")
    print(f"Exploración: {'BUENA' if good_exploration else 'LIMITADA'}")
    
    return {
        'confinamiento': within_bounds,
        'balance_direccional': balanced,
        'bordes_izquierdo': forced_right,
        'bordes_derecho': forced_left,
        'intervalos_correctos': intervals_in_range,
        'exploracion_adecuada': good_exploration,
        'estadisticas': stats
    }

# =====================================================
# FUNCIONES DE EVALUACIÓN INTEGRAL
# =====================================================

def run_all_model_tests():
    """
    Ejecutar todos los tests de modelos independientemente.
    """
    print("EVALUACIÓN INTEGRAL DE MODELOS DE SIMULACIÓN")
    print("=" * 80)
    
    # Ejecutar tests individuales
    results = {}
    
    try:
        print("\n" + "="*20 + " INICIANDO TESTS " + "="*20)
        
        # Test LCG
        print("\nEjecutando test LCG...")
        results['lcg'] = test_lcg_model()
        
        # Test Markov
        print("\nEjecutando test Markov...")
        results['markov'] = test_markov_model()
        
        # Test Monte Carlo
        print("\nEjecutando test Monte Carlo...")
        results['monte_carlo'] = test_monte_carlo_model()
        
        # Test Boss Agent
        print("\nEjecutando test Boss Agent...")
        results['boss_agent'] = test_boss_agent_model()
        
        # Test Random Walk
        print("\nEjecutando test Random Walk...")
        results['random_walk'] = test_random_walk_model()
        
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        return None
    
    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN FINAL DE EVALUACIÓN")
    print("="*80)
    
    model_names = {
        'lcg': 'Generador LCG',
        'markov': 'Cadenas de Markov', 
        'monte_carlo': 'Monte Carlo',
        'boss_agent': 'Simulación de Agentes',
        'random_walk': 'Caminata Aleatoria'
    }
    
    total_tests = 0
    passed_tests = 0
    
    for model_key, model_name in model_names.items():
        if model_key in results:
            model_results = results[model_key]
            model_tests = len(model_results)
            model_passed = sum(1 for result in model_results.values() if result == True)
            
            total_tests += model_tests
            passed_tests += model_passed
            
            success_rate = model_passed / model_tests * 100 if model_tests > 0 else 0
            status = "APROBADO" if success_rate >= 60 else "REPROBADO"
            
            print(f"{model_name:25}: {model_passed:2}/{model_tests} tests ({success_rate:5.1f}%) {status}")
            
            # Mostrar detalles de tests fallidos
            failed_tests = [test_name for test_name, result in model_results.items() 
                           if result == False]
            if failed_tests:
                print(f"                          Tests fallidos: {', '.join(failed_tests)}")
    
    overall_success = passed_tests / total_tests * 100 if total_tests > 0 else 0
    print("\n" + "-"*80)
    print(f"RESULTADO GENERAL: {passed_tests}/{total_tests} tests aprobados ({overall_success:.1f}%)")
    
    if overall_success >= 85:
        print("🎉 TODOS LOS MODELOS VALIDADOS EXITOSAMENTE")
    elif overall_success >= 70:
        print("MODELOS PARCIALMENTE VALIDADOS")
    else:
        print("VALIDACIÓN FALLIDA - Modelos requieren corrección")
    
    return results

def generate_model_comparison_report():
    """
    Generar reporte comparativo de todos los modelos.
    """
    print("\n" + "="*80)
    print("REPORTE COMPARATIVO DE MODELOS")
    print("="*80)
    
    models_info = [
        {
            'name': 'Generador LCG',
            'type': 'Determinístico/Pseudoaleatorio',
            'complexity': 'O(1)',
            'memory': 'O(1)',
            'applications': 'Base para todos los procesos aleatorios',
            'strengths': 'Reproducible, eficiente, período largo',
            'weaknesses': 'Patrones detectables a largo plazo'
        },
        {
            'name': 'Cadenas de Markov',
            'type': 'Estocástico Discreto',
            'complexity': 'O(n) estados',
            'memory': 'O(n²) matriz',
            'applications': 'Comportamiento enemigo adaptativo',
            'strengths': 'Impredecible, matemáticamente sólido',
            'weaknesses': 'Sin memoria de contexto amplio'
        },
        {
            'name': 'Monte Carlo',
            'type': 'Estocástico/Muestreo',
            'complexity': 'O(1) por muestra',
            'memory': 'O(n) distribución',
            'applications': 'Generación de power-ups balanceada',
            'strengths': 'Control preciso de probabilidades',
            'weaknesses': 'No adapta al contexto del juego'
        },
        {
            'name': 'Simulación de Agentes',
            'type': 'Continuo/Multi-criterio',
            'complexity': 'O(m) variables',
            'memory': 'O(m) estado',
            'applications': 'IA compleja del jefe final',
            'strengths': 'Adaptativo, comportamiento emergente',
            'weaknesses': 'Complejidad de tuning'
        },
        {
            'name': 'Caminata Aleatoria',
            'type': 'Estocástico Restringido',
            'complexity': 'O(1)',
            'memory': 'O(1)',
            'applications': 'Movimiento básico de drones',
            'strengths': 'Simple, orgánico, eficiente',
            'weaknesses': 'Limitado a movimiento básico'
        }
    ]
    
    print(f"{'Modelo':<25} {'Tipo':<25} {'Complejidad':<15} {'Aplicación'}")
    print("-" * 80)
    
    for model in models_info:
        print(f"{model['name']:<25} {model['type']:<25} {model['complexity']:<15} {model['applications']}")
    
    print("\nFORTALEZAS Y DEBILIDADES:")
    print("-" * 40)
    
    for model in models_info:
        print(f"\n{model['name']}:")
        print(f"  + {model['strengths']}")
        print(f"  - {model['weaknesses']}")
    
    print(f"\nSINERGIA DE MODELOS:")
    print("-" * 20)
    print("• LCG proporciona la base pseudoaleatoria para todos los demás")
    print("• Random Walk maneja enemigos básicos (drones)")
    print("• Markov añade complejidad a enemigos intermedios")
    print("• Agentes crean desafío máximo (jefe final)")
    print("• Monte Carlo equilibra la economía del juego")
    print("• Todos juntos crean progresión de dificultad coherente")

# =====================================================
# EJECUCIÓN PRINCIPAL
# =====================================================

if __name__ == "__main__":
    print("SISTEMA DE EVALUACIÓN INDEPENDIENTE DE MODELOS")
    print("Nebula Uprising - Análisis de Simulación")
    print("=" * 60)
    
    # Ejecutar todos los tests
    test_results = run_all_model_tests()
    
    # Generar reporte comparativo
    generate_model_comparison_report()
    
    print(f"\n{'='*60}")
    print("EVALUACIÓN COMPLETADA")
    print(f"{'='*60}")
    
    if test_results:
        print("Los modelos han sido evaluados independientemente.")
        print("Cada modelo puede extraerse y utilizarse en otros proyectos.")
        print("Los resultados validan la implementación teórica y práctica.")
    else:
        print("Error en la evaluación. Revisar implementación de modelos.")