# -*- coding: utf-8 -*-
"""
Entity layer: FireStation and FireTruck with state-machine logic.

Pure domain logic — no pygame imports.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional, Tuple


class TruckState(Enum):
    IDLE = "IDLE"
    EN_ROUTE = "EN_ROUTE"
    EXTINGUISHING = "EXTINGUISHING"
    RETURNING = "RETURNING"


class FireStation:
    """A fire station that owns one or more FireTrucks."""

    def __init__(self, sid: int, gx: int, gy: int) -> None:
        self.id: int = sid
        self.gx: int = gx
        self.gy: int = gy
        self.trucks: List[FireTruck] = []

    def get_available_truck(self) -> Optional["FireTruck"]:
        for truck in self.trucks:
            if truck.state == TruckState.IDLE:
                return truck
        return None


class FireTruck:
    """
    A fire truck with a 4-state FSM:

        IDLE ─► EN_ROUTE ─► EXTINGUISHING ─► RETURNING ─► IDLE
    """

    SPEED: float = 5.0               # grid cells per second
    EXTINGUISH_DURATION: float = 2.5  # seconds to extinguish a fire

    def __init__(self, tid: int, station: FireStation) -> None:
        self.id: int = tid
        self.station: FireStation = station
        self.state: TruckState = TruckState.IDLE

        # Floating-point grid position
        self.x: float = float(station.gx)
        self.y: float = float(station.gy)

        # Dispatch target
        self.target_gx: Optional[int] = None
        self.target_gy: Optional[int] = None

        # Road path (list of (gx, gy) waypoints)
        self.path: List[Tuple[int, int]] = []
        self.path_index: int = 0

        # Extinguish progress
        self.extinguish_timer: float = 0.0

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    def dispatch(
        self,
        path: List[Tuple[int, int]],
        target_gx: int,
        target_gy: int,
    ) -> None:
        """Send the truck to *target* via *path*."""
        if not path:
            return
        self.path = path
        self.path_index = 0
        self.target_gx = target_gx
        self.target_gy = target_gy
        self.state = TruckState.EN_ROUTE

    # ------------------------------------------------------------------
    # Simulation tick
    # ------------------------------------------------------------------

    def update(self, dt: float) -> str:
        """
        Advance the state machine by *dt* seconds.

        Returns a string event token:
          ``"arrived"``       – reached the fire
          ``"extinguished"``  – finished extinguishing
          ``"returned"``      – back at station
          ``""``              – nothing notable
        """
        if self.state == TruckState.IDLE:
            return ""

        if self.state == TruckState.EN_ROUTE:
            return self._move_along_path(dt, on_arrive="arrived")

        if self.state == TruckState.EXTINGUISHING:
            self.extinguish_timer += dt
            if self.extinguish_timer >= self.EXTINGUISH_DURATION:
                # Start heading back
                self.state = TruckState.RETURNING
                self.path = list(reversed(self.path))
                self.path_index = 0
                return "extinguished"
            return ""

        if self.state == TruckState.RETURNING:
            return self._move_along_path(dt, on_arrive="returned")

        return ""

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _move_along_path(self, dt: float, on_arrive: str) -> str:
        if self.path_index >= len(self.path):
            self._on_path_end(on_arrive)
            return on_arrive

        tx, ty = float(self.path[self.path_index][0]), float(self.path[self.path_index][1])
        dx, dy = tx - self.x, ty - self.y
        dist = (dx * dx + dy * dy) ** 0.5
        step = self.SPEED * dt

        if dist <= step:
            self.x, self.y = tx, ty
            self.path_index += 1
            if self.path_index >= len(self.path):
                self._on_path_end(on_arrive)
                return on_arrive
        else:
            self.x += dx / dist * step
            self.y += dy / dist * step

        return ""

    def _on_path_end(self, token: str) -> None:
        if token == "arrived":
            self.state = TruckState.EXTINGUISHING
            self.extinguish_timer = 0.0
        elif token == "returned":
            self.state = TruckState.IDLE
            self.x = float(self.station.gx)
            self.y = float(self.station.gy)
            self.path = []
            self.target_gx = None
            self.target_gy = None
