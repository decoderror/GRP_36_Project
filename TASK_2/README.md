# Task 2 — Self-study: Currency Arbitrage Detection (Graph + Bellman–Ford)

## Chosen Topics

- **Data Structure:** Directed Weighted Graph (Adjacency List)
- **Algorithm:** Bellman–Ford (with Negative Cycle Detection)
- **Application Scenario:** Currency exchange **arbitrage detection**

---

## 1. Problem Background: What Is Currency Arbitrage?

In a real foreign exchange (FX) market, exchange rates between different currency pairs are not always perfectly consistent. Sometimes price mismatches create a **risk-free arbitrage** opportunity.

**Intuition:**

- Start with some amount of a base currency (e.g., `GBP`).
- Sequentially exchange it through several other currencies.
- Return to the original currency (e.g., `GBP` again).
- If the **product of the exchange rates along this cycle is > 1**, you end up with more of the original currency than you started with. This is a theoretical arbitrage opportunity (ignoring fees, slippage, etc.).

**Example in this project:**

We construct a 3-currency cycle:

- GBP → EUR: `1.20`  (`£1` → `€1.20`)
- EUR → USD: `1.10`  (`€1` → `$1.10`)
- USD → GBP: `0.90`  (`$1` → `£0.90`)

The product is:

```text
1.20 * 1.10 * 0.90 = 1.188
```

This means an **18.8% profit** if you traverse this loop once.

Our goal is to:

1. Model the currency market as a **directed weighted graph**.
2. Use **Bellman–Ford** to detect negative cycles in a transformed graph.
3. Map these negative cycles back to profitable arbitrage loops and compute the profit multiplier.

---

## 2. Data Structure: `ArbitrageGraph` (Directed Weighted Graph)

### 2.1 Overview

The core data structure is the `ArbitrageGraph` class:

```python
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
```

- **`graph`**  
  - Implements a **directed adjacency list**.
  - Keys are base currency codes (e.g., `'GBP'`, `'EUR'`, `'USD'`).
  - Values are dictionaries `{target_currency: weight}`, where `weight` is the transformed edge weight (see below).

- **`currencies`**  
  - A `set` containing all currencies (nodes) that appear in the graph.
  - Used to initialize the Bellman–Ford distance array.

- **`original_rates`**  
  - A dictionary keyed by `(base_currency, target_currency)` storing the **raw exchange rates** (not transformed).
  - This is used later to compute the **actual profit multiplier** for a detected arbitrage cycle.

### 2.2 Adding Exchange Rates: `add_exchange_rate`

```python
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
```

Key points:

1. **Directed edge**  
   - We add a directed edge from `base_currency` to `target_currency` only.
   - If you want bidirectional trading, you must add both directions explicitly with their own rates.

2. **Node management**  
   - Ensure both currencies exist in `self.graph` and `self.currencies`.

3. **Mathematical transformation: `-log(rate)`**  
   - Raw arbitrage condition: product of rates along a cycle > 1.
   - Taking logs converts products into sums:

     ```text
     log(a * b * c) = log(a) + log(b) + log(c)
     ```

   - To turn “product > 1” into a shortest-path style problem, we define:

     ```text
     weight = -log(rate)
     ```

   - Then:

     - `rate_product > 1`  
       ⇔ `log(rate_product) > 0`  
       ⇔ `-log(rate_product) < 0`  
       ⇔ sum of `-log(rate)` along the cycle is **negative**.

   - So a **profitable arbitrage cycle** in terms of raw rates corresponds to a **negative-weight cycle** in the transformed graph. This is exactly what Bellman–Ford can detect.

---

## 3. Algorithm: Bellman–Ford with Negative Cycle Detection

### 3.1 Method: `detect_arbitrage`

```python
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
```

#### Step-by-step explanation

1. **Initialization**
   - `distances`: maps each currency to a distance value. Initially:
     - `distances[source_currency] = 0`
     - all others = `+∞`
   - `predecessor`: maps each currency to the previous node in the shortest path (used to reconstruct paths/cycles).

2. **Relaxation (|V| − 1 rounds)**
   - Standard Bellman–Ford:
     - For each edge `u → v` with weight `w`:
       ```python
       if distances[u] + weight < distances[v]:
           distances[v] = distances[u] + weight
           predecessor[v] = u
       ```
   - Repeating this `|V| - 1` times guarantees shortest paths if there are no negative cycles reachable from the source.

3. **Negative cycle detection**
   - Run one additional pass over all edges:
     ```python
     if distances[u] + weight < distances[v]:
         # Detected a negative cycle
     ```
   - If any distance can still be improved, then a **negative cycle** exists.
   - Because of the `-log(rate)` transformation, this negative cycle corresponds to a **profitable arbitrage loop**.
   - Once detected, we call `_reconstruct_cycle(predecessor, v)` to:
     - find the actual cycle of currencies,
     - compute the true profit multiplier using original rates,
     - and print the trading route plus sample profit.

---

## 4. Reconstructing the Arbitrage Cycle & Computing Profit

### 4.1 Method: `_reconstruct_cycle`

```python
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
```

#### How the reconstruction works

1. **Jump inside the cycle**
   - Start from `start_node` (a node affected by the negative cycle).
   - Move backwards via `predecessor` for `|V|` steps:
     ```python
     for _ in range(len(self.currencies)):
         current = predecessor[current]
     ```
   - After enough steps, we are guaranteed to be somewhere **inside** the cycle. Call this `cycle_start`.

2. **Collect the full cycle**
   - Starting at `cycle_start`, move backwards through predecessors until we come back to `cycle_start` again:
     ```python
     cycle = [cycle_start]
     current = predecessor[cycle_start]
     while current != cycle_start:
         cycle.append(current)
         current = predecessor[current]
     cycle.append(cycle_start)
     ```
   - Now `cycle` contains all currencies on the cycle, but in **reverse** order of traversal.

3. **Reverse to chronological trading order**
   - `cycle.reverse()` to get the actual trading route in the order you would execute the exchanges.

4. **Print the trading route**
   - Example:
     ```text
     Trading Route: GBP -> EUR -> USD -> GBP
     ```

5. **Compute real profit using original rates**
   - Iterate over consecutive currency pairs in `cycle` and multiply the saved original rates:
     ```python
     profit_multiplier = 1.0
     for i in range(len(cycle) - 1):
         base = cycle[i]
         quote = cycle[i+1]
         rate = self.original_rates[(base, quote)]
         profit_multiplier *= rate
     ```
   - Print a human-readable summary, including a sample with `$1000` starting capital.

---

## 5. Example Usage (Demo)

At the bottom of the file there is a demo scenario:

```python
if __name__ == "__main__":
    market = ArbitrageGraph()

    # Create a loop: GBP -> EUR -> USD -> GBP
    market.add_exchange_rate('GBP', 'EUR', 1.20)  # £1 -> €1.20
    market.add_exchange_rate('EUR', 'USD', 1.10)  # €1 -> $1.10  
    
    market.add_exchange_rate('USD', 'GBP', 0.90)  # $1 -> £0.90 (A very high rate!)

    # Product: 1.20 * 1.10 * 0.90 = 1.188 (18.8% Profit!)

    # Start looking for arbitrage from GBP
    market.detect_arbitrage('GBP')
```

### How to run

Assume your file is named `arbitrage_graph.py` and you have Python installed:

```bash
python arbitrage_graph.py
```

### Expected output (conceptually)

```text
🚨 ARBITRAGE OPPORTUNITY DETECTED! 🚨
Trading Route: GBP -> EUR -> USD -> GBP
Profit Multiplier: 1.1880 (If you start with $1000, you end with $1188.00)
```

This confirms that the detected negative cycle in the transformed graph corresponds to a profitable arbitrage loop in terms of original exchange rates.

---

## 6. Time and Space Complexity

Let:

- `V = |currencies|` be the number of currencies (nodes).
- `E` be the number of directed exchange edges.

### 6.1 Bellman–Ford complexity

- **Time Complexity:**
  - The main relaxation loop runs `V - 1` iterations.
  - In each iteration, we scan all edges `E`.
  - Therefore, time complexity is:
    ```text
    O(V * E)
    ```

- **Space Complexity:**
  - `distances`: `O(V)`
  - `predecessor`: `O(V)`
  - Graph storage (`graph` as adjacency list): `O(V + E)`
  - `original_rates`: `O(E)`

For small to medium-sized currency sets, this complexity is acceptable and easy to reason about.

---

## 7. Potential Extensions and Real-World Considerations

This project is a simplified educational prototype. In a real-world or more advanced setting, you might consider:

1. **Bid-ask spread and transaction costs**
   - Real FX markets have different buy/sell prices and various fees.
   - You could model separate edges for “buy” and “sell” and include transaction costs in the rates.

2. **Real-time data integration**
   - Fetch live exchange rates from financial data APIs.
   - Rebuild the graph and run arbitrage detection periodically.

3. **Multiple-source detection**
   - Instead of starting from a single source currency, you could:
     - Add a super-source node connected to all currencies with zero-weight edges, or
     - Run detection from each currency separately.

4. **Visualization**
   - Use libraries like `networkx` and `matplotlib` to visualize:
     - Currency nodes.
     - Exchange-rate edges.
     - Highlighted arbitrage cycles.

5. **Robustness and validation**
   - Check for invalid or zero/negative rates before applying `log`.
   - Add tests to ensure no KeyErrors occur when reconstructing cycles.

---

## 8. Summary

This project demonstrates how to:

- Model a currency exchange market as a **directed weighted graph** using an **adjacency list**.
- Apply the **`-log(rate)` transformation** to convert a “maximum product along a cycle” problem into a **negative cycle detection** problem.
- Use the **Bellman–Ford algorithm** to detect negative cycles that correspond to **arbitrage opportunities**.
- Reconstruct the arbitrage cycle and compute the **actual profit multiplier** using the original (untransformed) exchange rates.

It connects concepts from:

- Graph theory (directed weighted graphs, cycles),
- Classic shortest-path algorithms (Bellman–Ford),
- And practical financial applications (currency arbitrage detection).