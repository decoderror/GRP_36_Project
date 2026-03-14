# -*- coding: utf-8 -*-
"""
World / Grid layer.

Generates a city grid modelled on Hong Kong's Hung Hom (红磡) district:
irregular road network, dense residential blocks, a commercial/PolyU area,
waterfront parks, and Victoria Harbour to the south.

Pure domain logic — no pygame imports.
"""
from __future__ import annotations

import random
from enum import Enum
from typing import List, Optional, Tuple


class CellType(Enum):
    EMPTY      = 0
    ROAD       = 1
    BUILDING   = 2   # residential
    STATION    = 3   # fire station
    PARK       = 4
    WATER      = 5   # Victoria Harbour / waterfront
    COMMERCIAL = 6   # commercial / office / campus


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
        if cell_type == CellType.BUILDING:
            self.building_hp: float = 100.0
        elif cell_type == CellType.COMMERCIAL:
            self.building_hp = 150.0       # sturdier commercial buildings
        else:
            self.building_hp = 0.0


# Reference grid size used for the Hung Hom layout template.
# The generator scales to the actual world dimensions.
_REF_W: int = 33
_REF_H: int = 24


class World:
    """
    City grid modelled on Hong Kong's Hung Hom district.

    Key features of the generated layout:
      - Major east-west roads: Hung Hom Road, Ma Tau Wai Road, etc.
      - Irregular block pattern — small tenement blocks in the north/center,
        larger commercial blocks near the PolyU campus (north-west).
      - Waterfront (Victoria Harbour) along the southern edge.
      - Hung Hom Promenade park strip on the south-east waterfront.
      - Three fire stations placed at realistic road intersections.
    """

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
        """Generate the Hung Hom district layout, scaled to self.width × self.height."""
        W, H = self.width, self.height

        # Helper: scale a reference coordinate to the actual grid size
        def rx(v: float) -> int:
            return min(int(round(v * W / _REF_W)), W - 1)

        def ry(v: float) -> int:
            return min(int(round(v * H / _REF_H)), H - 1)

        # ── Initialise all cells as empty ──────────────────────────────
        self.cells = [
            [Cell(x, y, CellType.EMPTY) for y in range(H)]
            for x in range(W)
        ]

        # ── Victoria Harbour / waterfront (southernmost rows) ──────────
        water_y = ry(21)
        for y in range(water_y, H):
            for x in range(W):
                self.cells[x][y].type = CellType.WATER

        # ── Road-drawing helpers ────────────────────────────────────────
        def hroad(y_ref: float, x0_ref: float = 0, x1_ref: float = _REF_W) -> None:
            """Draw a horizontal road segment (full width by default)."""
            y = ry(y_ref)
            for x in range(rx(x0_ref), min(rx(x1_ref) + 1, W)):
                if self.cells[x][y].type != CellType.WATER:
                    self.cells[x][y].type = CellType.ROAD

        def vroad(x_ref: float, y0_ref: float = 0, y1_ref: float = 21) -> None:
            """Draw a vertical road segment."""
            x = rx(x_ref)
            for y in range(ry(y0_ref), min(ry(y1_ref) + 1, H)):
                if self.cells[x][y].type != CellType.WATER:
                    self.cells[x][y].type = CellType.ROAD

        # ── Major east-west roads (full width) ─────────────────────────
        # Inspired by: Ma Tau Wai Road, Hung Hom Road, Wuhu St, Laguna Verde Ave
        for y_ref in [0, 8, 14, 20]:
            hroad(y_ref)

        # ── Minor east-west roads (partial — irregular Kowloon blocks) ─
        hroad(3,  0,  14)    # short northern alley (west side)
        hroad(5,  7,  33)    # internal connector (central-east)
        hroad(11, 0,  21)    # mid-level connector
        hroad(17, 7,  33)    # south-east internal road

        # ── Major north-south roads (full height) ──────────────────────
        # Inspired by: Chatham Rd South, Gillies Ave S, Bailey St, eastern boundary
        for x_ref in [0, 7, 21, 32]:
            vroad(x_ref)

        # ── Minor north-south roads (partial) ──────────────────────────
        vroad(4,  0,  14)    # short western alley
        vroad(14, 0,  20)    # Wing Kwong Street (central)
        vroad(28, 5,  20)    # far-east connector

        # ── Parks ──────────────────────────────────────────────────────
        def fill(x0r: float, y0r: float, x1r: float, y1r: float,
                 ct: CellType, hp: float = 0.0) -> None:
            """Fill a rectangular area with a cell type (skip roads/water)."""
            for x in range(rx(x0r), min(rx(x1r) + 1, W)):
                for y in range(ry(y0r), min(ry(y1r) + 1, H)):
                    if self.cells[x][y].type not in (CellType.ROAD, CellType.WATER):
                        self.cells[x][y].type = ct
                        self.cells[x][y].building_hp = hp

        # Hung Hom Promenade — waterfront park strip (south-east)
        fill(21, 19, 32, 20, CellType.PARK)
        # Small pocket park — north central
        fill(8,  1,  13,  3, CellType.PARK)
        # Small pocket park — west mid
        fill(1,  9,   6, 11, CellType.PARK)

        # ── PolyU / commercial campus (north-west corner) ──────────────
        fill(1,  1,   6,  7, CellType.COMMERCIAL)

        # ── Waterfront commercial / hotel zone (south-east) ────────────
        fill(22, 15,  31, 19, CellType.COMMERCIAL)

        # ── Fill remaining EMPTY cells with residential buildings ───────
        for x in range(W):
            for y in range(H):
                c = self.cells[x][y]
                if c.type == CellType.EMPTY:
                    c.type = CellType.BUILDING
                    c.building_hp = 100.0

        # Fix building_hp for any COMMERCIAL cells already placed by fill()
        for x in range(W):
            for y in range(H):
                if self.cells[x][y].type == CellType.COMMERCIAL:
                    self.cells[x][y].building_hp = 150.0

        # ── Fire stations at road intersections ────────────────────────
        # Approximate real Hung Hom fire station / police station positions
        station_refs = [
            (rx(7),  ry(8)),    # Hung Hom Road / Gillies Ave South
            (rx(21), ry(14)),   # Mid-level road / Bailey Street
            (rx(14), ry(0)),    # Ma Tau Wai Road / Wing Kwong Street
        ]

        self.stations = []
        for sx, sy in station_refs:
            placed = False
            # Try to snap to an existing road cell within a small radius
            for dist in range(4):
                for dx in range(-dist, dist + 1):
                    for dy in range(-dist, dist + 1):
                        if abs(dx) + abs(dy) != dist:
                            continue
                        nx, ny = sx + dx, sy + dy
                        if (0 <= nx < W and 0 <= ny < H
                                and self.cells[nx][ny].type == CellType.ROAD):
                            self.cells[nx][ny].type = CellType.STATION
                            self.stations.append((nx, ny))
                            placed = True
                            break
                    if placed:
                        break
                if placed:
                    break
            if not placed:
                # Force-place even if not on a road
                if 0 <= sx < W and 0 <= sy < H:
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
