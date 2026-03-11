# -*- coding: utf-8 -*-
"""
World / Grid layer.

Generates a city grid with continuous road networks, coherent building blocks,
grouped parks, and properly placed fire stations.
Pure domain logic — no pygame imports.
"""
from __future__ import annotations

import random
from enum import Enum
from typing import List, Optional, Tuple, Set


class CellType(Enum):
    EMPTY = 0
    ROAD = 1
    BUILDING = 2        # generic (legacy)
    STATION = 3
    PARK = 4
    RESIDENTIAL = 5     # dark gray
    OFFICE = 6          # slate/purple
    INDUSTRIAL = 7      # brown/orange


# Cell types that can burn
BURNABLE_TYPES: Set[CellType] = {
    CellType.BUILDING,
    CellType.RESIDENTIAL,
    CellType.OFFICE,
    CellType.INDUSTRIAL,
}


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
        self.building_hp: float = 100.0 if cell_type in BURNABLE_TYPES else 0.0


class World:
    """
    City grid.

    Road layout: horizontal and vertical roads every ROAD_INTERVAL cells,
    forming a continuous grid network. Each block between roads is assigned
    a zone type: residential, office, industrial, or park. Fire stations
    are placed at selected road intersections.
    """

    ROAD_INTERVAL: int = 8

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

        # Initialize all cells as EMPTY
        self.cells = [
            [Cell(x, y, CellType.EMPTY) for y in range(self.height)]
            for x in range(self.width)
        ]

        # ── 1. Lay down roads (continuous grid) ──────────────────────
        for x in range(self.width):
            for y in range(self.height):
                if x % interval == 0 or y % interval == 0:
                    self.cells[x][y].type = CellType.ROAD

        # ── 2. Assign zone type per block ─────────────────────────────
        # Zone probabilities: 55% residential, 15% office, 12% industrial, 18% park
        zone_weights = [
            (CellType.RESIDENTIAL, 55),
            (CellType.OFFICE,      15),
            (CellType.INDUSTRIAL,  12),
            (CellType.PARK,        18),
        ]
        zone_cumulative = []
        total = 0
        for ct, w in zone_weights:
            total += w
            zone_cumulative.append((ct, total))

        def pick_zone() -> CellType:
            r = rng.randint(1, total)
            for ct, cum in zone_cumulative:
                if r <= cum:
                    return ct
            return CellType.RESIDENTIAL

        # Assign zones for each block
        block_zones = {}
        bx = 1
        while bx < self.width:
            by = 1
            while by < self.height:
                block_zones[(bx, by)] = pick_zone()
                by += interval
            bx += interval

        # Fill block cells with zone type (with some internal variation)
        for bx, by in block_zones:
            zone = block_zones[(bx, by)]
            end_x = min(bx + interval - 1, self.width - 1)
            end_y = min(by + interval - 1, self.height - 1)
            for x in range(bx, end_x):
                for y in range(by, end_y):
                    cell = self.cells[x][y]
                    if cell.type == CellType.ROAD:
                        continue
                    if zone == CellType.PARK:
                        cell.type = CellType.PARK
                    else:
                        if rng.random() < 0.08:
                            cell.type = CellType.EMPTY
                        else:
                            cell.type = zone
                            cell.building_hp = 100.0

        # ── 3. Add park clusters ──────────────────────────────────────
        park_block_list = [k for k, v in block_zones.items() if v == CellType.PARK]
        rng.shuffle(park_block_list)
        extended = set()
        for bx, by in park_block_list[:max(1, len(park_block_list) // 3)]:
            for dxi, dyi in [(interval, 0), (0, interval)]:
                nbx, nby = bx + dxi, by + dyi
                if (nbx, nby) in block_zones and (nbx, nby) not in extended:
                    end_x = min(nbx + interval - 1, self.width - 1)
                    end_y = min(nby + interval - 1, self.height - 1)
                    for x in range(nbx, end_x):
                        for y in range(nby, end_y):
                            cell = self.cells[x][y]
                            if cell.type != CellType.ROAD:
                                cell.type = CellType.PARK
                                cell.building_hp = 0.0
                    block_zones[(nbx, nby)] = CellType.PARK
                    extended.add((nbx, nby))

        # ── 4. Place fire stations at road intersections ───────────────
        intersections: List[Tuple[int, int]] = []
        for x in range(0, self.width, interval):
            for y in range(0, self.height, interval):
                if 0 <= x < self.width and 0 <= y < self.height:
                    intersections.append((x, y))

        rng.shuffle(intersections)
        n_stations = min(4, max(3, len(intersections) // 6))
        self.stations = []
        placed: List[Tuple[int, int]] = []
        for sx, sy in intersections:
            too_close = any(abs(sx - px) + abs(sy - py) < interval * 2 for px, py in placed)
            if too_close and len(placed) > 0:
                continue
            self.cells[sx][sy].type = CellType.STATION
            self.stations.append((sx, sy))
            placed.append((sx, sy))
            if len(placed) >= n_stations:
                break

        if len(self.stations) < 3:
            for sx, sy in intersections:
                if (sx, sy) not in self.stations:
                    self.cells[sx][sy].type = CellType.STATION
                    self.stations.append((sx, sy))
                    if len(self.stations) >= 3:
                        break

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
                if c.type in BURNABLE_TYPES:
                    c.building_hp = 100.0
