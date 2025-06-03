import csv

class PseudoRandom:
    def __init__(self, csv_path):
        self.sequence = []
        self.index = 0
        self.load_sequence(csv_path)

    def load_sequence(self, path):
        with open(path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            self.sequence = [float(row['value']) for row in reader]

    def next(self):
        if not self.sequence:
            raise ValueError("Pseudo-random sequence not loaded.")
        value = self.sequence[self.index]
        self.index = (self.index + 1) % len(self.sequence)
        return value

    def next_choice(self, choices):
        """Devuelve una elección binaria o múltiple basada en el valor."""
        rand = self.next()
        index = int(rand * len(choices)) % len(choices)
        return choices[index]
