# -*- coding: utf-8 -*-
"""
World / Grid layer.

Generates a city grid with roads, buildings, parks, and fire stations.
Pure domain logic — no pygame imports.
"""
from __future__ import annotations

import random
from enum import Enum
from typing import List, Optional, Tuple


class CellType(Enum):
    EMPTY = 0
    ROAD = 1
    BUILDING = 2
    STATION = 3
    PARK = 4


class Cell:
    """A single cell in the simulation grid."""

    __slots__ = (
        "gx", "gy", "type",
        "burning", "fire_intensity", "fire_timer",
        "building_hp",
    )

    def __init__(self, gx: int, gy: int, cell_type: CellType = CellType.EMPTY) -> None:
        self.gx: int = gx
        self.gy: int = gy
        self.type: CellType = cell_type
        self.burning: bool = False
        self.fire_intensity: float = 0.0   # 0.0–1.0
        self.fire_timer: float = 0.0       # seconds since ignition
        self.building_hp: float = 100.0 if cell_type == CellType.BUILDING else 0.0


class World:
    """
    City grid.

    Road layout: horizontal and vertical roads every ROAD_INTERVAL cells.
    Buildings fill the blocks between roads.
    Fire stations are placed at selected road intersections.
    """

    ROAD_INTERVAL: int = 7

    def __init__(self, width: int, height: int, seed: int = 42) -> None:
        self.width: int = width
        self.height: int = height
        self.seed: int = seed
        self.cells: List[List[Cell]] = []
        self.stations: List[Tuple[int, int]] = []
        self._generate(seed)

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def _generate(self, seed: int) -> None:
        rng = random.Random(seed)
        interval = self.ROAD_INTERVAL

        self.cells = [
            [Cell(x, y, CellType.EMPTY) for y in range(self.height)]
            for x in range(self.width)
        ]

        for x in range(self.width):
            for y in range(self.height):
                if x % interval == 0 or y % interval == 0:
                    self.cells[x][y].type = CellType.ROAD
                else:
                    r = rng.random()
                    if r < 0.72:
                        self.cells[x][y].type = CellType.BUILDING
                        self.cells[x][y].building_hp = 100.0
                    elif r < 0.85:
                        self.cells[x][y].type = CellType.PARK
                    else:
                        self.cells[x][y].type = CellType.EMPTY

        # Place fire stations at road intersections
        intersections: List[Tuple[int, int]] = []
        for x in range(0, self.width, interval):
            for y in range(0, self.height, interval):
                intersections.append((x, y))

        rng.shuffle(intersections)
        n_stations = min(3, len(intersections))
        self.stations = []
        for sx, sy in intersections[:n_stations]:
            self.cells[sx][sy].type = CellType.STATION
            self.stations.append((sx, sy))

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_cell(self, gx: int, gy: int) -> Optional[Cell]:
        if 0 <= gx < self.width and 0 <= gy < self.height:
            return self.cells[gx][gy]
        return None

    def get_burning_cells(self) -> List[Cell]:
        return [
            self.cells[x][y]
            for x in range(self.width)
            for y in range(self.height)
            if self.cells[x][y].burning
        ]

    def road_neighbors(self, gx: int, gy: int) -> List[Tuple[int, int]]:
        """Adjacent road/station cells — used by A* pathfinding."""
        result = []
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = gx + dx, gy + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                ct = self.cells[nx][ny].type
                if ct in (CellType.ROAD, CellType.STATION):
                    result.append((nx, ny))
        return result

    def reset_fires(self) -> None:
        for x in range(self.width):
            for y in range(self.height):
                c = self.cells[x][y]
                c.burning = False
                c.fire_intensity = 0.0
                c.fire_timer = 0.0
                if c.type == CellType.BUILDING:
                    c.building_hp = 100.0
