# -*- coding: utf-8 -*-
"""
core — Domain layer.

Contains all pure simulation logic (no pygame imports):
  world.py        City grid with Hung Hom district layout (CellType, Cell, World)
  entities.py     FireStation, FireTruck and TruckState FSM
  simulation.py   Simulation orchestrator — fire spread, dispatch, event emission
  events.py       SimEvent, EventType, Severity
  pathfinding.py  A* shortest path + nearest-road BFS helper
"""
