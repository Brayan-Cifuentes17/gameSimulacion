class PseudoRandom:
    """
    Generador de números pseudoaleatorios usando el Método Congruencial Lineal (LCG).
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

    def next(self):
        """
        Generar el siguiente número pseudoaleatorio normalizado [0,1).
        
        Returns:
            float: Número pseudoaleatorio entre 0 y 1
        """
        # Aplicar la fórmula LCG: Xn+1 = (a * Xn + c) mod m
        self.current = (self.multiplier * self.current + self.increment) % self.modulus
        
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