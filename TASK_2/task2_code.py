import math

class ArbitrageGraph:
    """
    A Directed Graph implementation using an Adjacency List.
    """
    def __init__(self):
        # The Adjacency List storing currencies and their transformed rates
        self.graph = {}
        self.currencies = set()
        # Storing original rates just for final output display
        self.original_rates = {}

    def add_exchange_rate(self, base_currency, target_currency, rate):
        """Adds a directed, weighted edge to the graph."""
        if base_currency not in self.graph:
            self.graph[base_currency] = {}
        if target_currency not in self.graph:
            self.graph[target_currency] = {}
            
        self.currencies.add(base_currency)
        self.currencies.add(target_currency)
        
        # The mathematical transformation: convert to negative log
        weight = -math.log(rate)
        self.graph[base_currency][target_currency] = weight
        self.original_rates[(base_currency, target_currency)] = rate

    def detect_arbitrage(self, source_currency):
        """
        The Bellman-Ford Algorithm modified to detect negative weight cycles.
        """
        # Step 1: Initialize distances from the source to all other nodes as infinity
        distances = {currency: float('inf') for currency in self.currencies}
        distances[source_currency] = 0
        
        # We also need a predecessor map to reconstruct the arbitrage loop later
        predecessor = {currency: None for currency in self.currencies}

        # Step 2: Relax all edges |V| - 1 times
        # |V| is the total number of vertices (currencies)
        for _ in range(len(self.currencies) - 1):
            for u in self.graph:
                for v, weight in self.graph[u].items():
                    if distances[u] + weight < distances[v]:
                        distances[v] = distances[u] + weight
                        predecessor[v] = u

        # Step 3: Run one final check to detect negative weight cycles
        # If we can STILL find a shorter path, a negative cycle (arbitrage) exists
        for u in self.graph:
            for v, weight in self.graph[u].items():
                if distances[u] + weight < distances[v]:
                    print("🚨 ARBITRAGE OPPORTUNITY DETECTED! 🚨")
                    self._reconstruct_cycle(predecessor, v)
                    return True
                    
        print("No arbitrage opportunity found from this source.")
        return False

    def _reconstruct_cycle(self, predecessor, start_node):
        """Helper method to trace back the loop and calculate the exact profit."""
        cycle = []
        current = start_node
        
        # Trace backwards to find the loop
        for _ in range(len(self.currencies)):
            current = predecessor[current]
            
        cycle_start = current
        cycle.append(cycle_start)
        current = predecessor[cycle_start]
        
        while current != cycle_start:
            cycle.append(current)
            current = predecessor[current]
        cycle.append(cycle_start)
        
        # Reverse to get the correct chronological trading order
        cycle.reverse()
        
        print(f"Trading Route: {' -> '.join(cycle)}")
        
        # Calculate the actual profit using the original raw rates
        profit_multiplier = 1.0
        for i in range(len(cycle) - 1):
            base = cycle[i]
            quote = cycle[i+1]
            rate = self.original_rates[(base, quote)]
            profit_multiplier *= rate
            
        print(f"Profit Multiplier: {profit_multiplier:.4f} (If you start with $1000, you end with ${1000 * profit_multiplier:.2f})")

# ==========================================
# TEST CASE AND DEMONSTRATION
# ==========================================
if __name__ == "__main__":
    market = ArbitrageGraph()

    # Create a loop: GBP -> EUR -> USD -> GBP
    market.add_exchange_rate('GBP', 'EUR', 1.20)  # £1 -> €1.20
    market.add_exchange_rate('EUR', 'USD', 1.10)  # €1 -> $1.10  
    
    market.add_exchange_rate('USD', 'GBP', 0.90)  # $1 -> £0.90 (A very high rate!)


    # Product: 1.20 * 1.10 * 0.90 = 1.188 (18.8% Profit!)

    # Start looking for arbitrage from GBP
    market.detect_arbitrage('GBP')
