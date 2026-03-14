# -*- coding: utf-8 -*-
"""
Simulation orchestrator.

Wires together World, entities, pathfinding, and event emission.
Pure domain logic — no pygame imports.
"""
from __future__ import annotations

import random
from typing import Callable, List, Optional, Tuple

from task1_oop_application.src.core.world import World, CellType
from task1_oop_application.src.core.entities import FireStation, FireTruck, TruckState
from task1_oop_application.src.core.events import SimEvent, EventType, Severity
from task1_oop_application.src.core.pathfinding import astar, nearest_road


# Named constants for simulation tuning
_SPREAD_NORMALIZE: float = 60.0   # converts per-second probability to per-frame (at ~60 ticks/s)

_EIGHT_DIRECTIONS = (
    (-1,  0), (1,  0), (0, -1), (0,  1),
    (-1, -1), (-1, 1), (1, -1), (1,  1),
)
WEATHER_SPREAD_MULT = {
    "sun":  1.0,
    "rain": 0.25,
    "wind": 2.8,
    "snow": 0.45,
}


class Simulation:
    """
    Top-level simulation object.

    Call :meth:`update` once per frame (with wall-clock *dt* in seconds).
    All real-time events are emitted via registered callbacks.
    """

    FIRE_INTENSITY_GROW: float = 0.12   # intensity units / second
    FIRE_SPREAD_CHANCE:  float = 0.025  # base probability / second
    MAX_EVENTS: int = 300

    def __init__(
        self,
        world_width: int = 40,
        world_height: int = 28,
        seed: int = 42,
    ) -> None:
        self.world_width = world_width
        self.world_height = world_height
        self.seed = seed

        self.world: World = World(world_width, world_height, seed)
        self.stations: List[FireStation] = []
        self.trucks: List[FireTruck] = []
        self.events: List[SimEvent] = []

        self.running: bool = False
        self.sim_time: float = 0.0
        self.weather: str = "sun"
        self.speed_mult: float = 1.0

        self.active_fires_history: List[int] = [0] * 10  # pre-fill so chart renders immediately
        self._history_timer: float = 0.0
        self._history_interval: float = 1.0  # record one data point per second

        self._rng: random.Random = random.Random(seed + 1)
        self._callbacks: List[Callable[[SimEvent], None]] = []

        self._setup_units()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _setup_units(self) -> None:
        self.stations = []
        self.trucks = []
        truck_id = 0
        for i, (sx, sy) in enumerate(self.world.stations):
            station = FireStation(i, sx, sy)
            for _ in range(2):              # 2 trucks per station
                truck = FireTruck(truck_id, station)
                station.trucks.append(truck)
                self.trucks.append(truck)
                truck_id += 1
            self.stations.append(station)

    def add_event_callback(self, cb: Callable[[SimEvent], None]) -> None:
        self._callbacks.append(cb)

    def _emit(self, event: SimEvent) -> None:
        event.sim_time = self.sim_time
        self.events.append(event)
        if len(self.events) > self.MAX_EVENTS:
            self.events = self.events[-self.MAX_EVENTS :]
        for cb in self._callbacks:
            cb(event)

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    def start(self) -> None:
        self.running = True
        self._emit(SimEvent(EventType.SIMULATION_STARTED, "Simulation started", Severity.INFO))

    def pause(self) -> None:
        self.running = False
        self._emit(SimEvent(EventType.SIMULATION_PAUSED, "Simulation paused", Severity.INFO))

    def reset(self) -> None:
        self.running = False
        self.sim_time = 0.0
        self.world = World(self.world_width, self.world_height, self.seed)
        self._rng = random.Random(self.seed + 1)
        self.active_fires_history = [0] * 10
        self._history_timer = 0.0
        self.events = []
        self._setup_units()
        self._emit(SimEvent(EventType.SIMULATION_RESET, "Simulation reset", Severity.INFO))

    def set_weather(self, weather: str) -> None:
        self.weather = weather
        self._emit(SimEvent(EventType.WEATHER_CHANGED, f"Weather → {weather}", Severity.INFO))

    def demo_mode(self) -> None:
        """Start 3 fires in spread-out locations to showcase the system."""
        self._emit(SimEvent(EventType.DEMO_MODE, "Demo mode activated!", Severity.WARNING))

        buildings: List[Tuple[int, int]] = []
        for x in range(self.world_width):
            for y in range(self.world_height):
                c = self.world.get_cell(x, y)
                if (c and c.type in (CellType.BUILDING, CellType.COMMERCIAL)
                        and not c.burning):
                    buildings.append((x, y))

        self._rng.shuffle(buildings)
        started = 0
        # Spread fires across the grid by filtering on distance
        last_fire: Optional[Tuple[int, int]] = None
        for bx, by in buildings:
            if last_fire and abs(bx - last_fire[0]) + abs(by - last_fire[1]) < 8:
                continue
            if self.start_fire(bx, by):
                last_fire = (bx, by)
                started += 1
            if started >= 3:
                break

    # ------------------------------------------------------------------
    # Fire management
    # ------------------------------------------------------------------

    def start_fire(self, gx: int, gy: int) -> bool:
        """Ignite a building or commercial cell. Returns True if successful."""
        cell = self.world.get_cell(gx, gy)
        if (cell and cell.type in (CellType.BUILDING, CellType.COMMERCIAL)
                and not cell.burning):
            cell.burning = True
            cell.fire_intensity = 0.3
            self._emit(SimEvent(
                EventType.FIRE_STARTED,
                f"Fire started at ({gx},{gy})",
                Severity.CRITICAL,
            ))
            self._dispatch_to_fire(gx, gy)
            return True
        return False

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def _dispatch_to_fire(self, fire_gx: int, fire_gy: int) -> None:
        """Find the nearest idle truck and send it to the fire."""
        fire_road = nearest_road(self.world, fire_gx, fire_gy)
        if fire_road is None:
            return

        best_truck: Optional[FireTruck] = None
        best_dist = float("inf")

        for station in self.stations:
            truck = station.get_available_truck()
            if truck is None:
                continue
            tr = (round(truck.x), round(truck.y))
            dist = abs(tr[0] - fire_road[0]) + abs(tr[1] - fire_road[1])
            if dist < best_dist:
                best_dist = dist
                best_truck = truck

        if best_truck is None:
            return

        tr = (round(best_truck.x), round(best_truck.y))
        path = astar(self.world, tr, fire_road)
        if path:
            best_truck.dispatch(path, fire_gx, fire_gy)
            self._emit(SimEvent(
                EventType.UNIT_DISPATCHED,
                f"Truck {best_truck.id} → ({fire_gx},{fire_gy})",
                Severity.WARNING,
            ))

    # ------------------------------------------------------------------
    # Main update loop
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        if not self.running:
            return

        eff_dt = dt * self.speed_mult
        self.sim_time += eff_dt

        self._update_fire(eff_dt)
        self._update_trucks(eff_dt)
        self._auto_dispatch()
        self._record_history(eff_dt)

    # ------------------------------------------------------------------
    # Private update helpers
    # ------------------------------------------------------------------

    def _update_fire(self, dt: float) -> None:
        spread_mult = WEATHER_SPREAD_MULT.get(self.weather, 1.0)

        burning = self.world.get_burning_cells()

        # Grow intensity of existing fires
        for cell in burning:
            cell.fire_intensity = min(1.0, cell.fire_intensity + self.FIRE_INTENSITY_GROW * dt)
            cell.fire_timer += dt

        # Attempt to spread
        new_fires: List[Tuple[int, int]] = []
        for cell in burning:
            prob = cell.fire_intensity * self.FIRE_SPREAD_CHANCE * spread_mult
            if self._rng.random() < prob * _SPREAD_NORMALIZE * dt:
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nx, ny = cell.gx + dx, cell.gy + dy
                    nb = self.world.get_cell(nx, ny)
                    if (
                        nb
                        and nb.type in (CellType.BUILDING, CellType.COMMERCIAL)
                        and not nb.burning
                        and self._rng.random() < 0.35
                    ):
                        new_fires.append((nx, ny))

        for fx, fy in new_fires:
            c = self.world.get_cell(fx, fy)
            if c and not c.burning:
                c.burning = True
                c.fire_intensity = 0.2
                self._emit(SimEvent(
                    EventType.FIRE_SPREAD,
                    f"Fire spread to ({fx},{fy})",
                    Severity.CRITICAL,
                ))

    def _update_trucks(self, dt: float) -> None:
        for truck in self.trucks:
            token = truck.update(dt)

            if token == "arrived":
                self._emit(SimEvent(
                    EventType.UNIT_ARRIVED,
                    f"Truck {truck.id} arrived at ({truck.target_gx},{truck.target_gy})",
                    Severity.INFO,
                ))

            elif token == "extinguished":
                # Extinguish the target cell and adjacent cells
                if truck.target_gx is not None and truck.target_gy is not None:
                    tgx, tgy = truck.target_gx, truck.target_gy
                    c = self.world.get_cell(tgx, tgy)
                    if c:
                        c.burning = False
                        c.fire_intensity = 0.0
                    for dx, dy in _EIGHT_DIRECTIONS:
                        nb = self.world.get_cell(tgx + dx, tgy + dy)
                        if nb and nb.burning:
                            nb.burning = False
                            nb.fire_intensity = 0.0
                self._emit(SimEvent(
                    EventType.FIRE_CONTAINED,
                    f"Fire contained at ({truck.target_gx},{truck.target_gy})",
                    Severity.INFO,
                ))

            elif token == "returned":
                self._emit(SimEvent(
                    EventType.UNIT_RETURNING,
                    f"Truck {truck.id} returned to station {truck.station.id}",
                    Severity.INFO,
                ))

    def _auto_dispatch(self) -> None:
        """Continuously re-dispatch idle trucks to unattended fires."""
        burning = self.world.get_burning_cells()
        if not burning:
            return

        already_targeted = {
            (t.target_gx, t.target_gy)
            for t in self.trucks
            if t.state in (TruckState.EN_ROUTE, TruckState.EXTINGUISHING)
        }

        for station in self.stations:
            truck = station.get_available_truck()
            if truck is None:
                continue

            tr = (round(truck.x), round(truck.y))
            best_fire = None
            best_dist = float("inf")

            for fc in burning:
                if (fc.gx, fc.gy) in already_targeted:
                    continue
                dist = abs(fc.gx - tr[0]) + abs(fc.gy - tr[1])
                if dist < best_dist:
                    best_dist = dist
                    best_fire = fc

            if best_fire is None:
                continue

            fire_road = nearest_road(self.world, best_fire.gx, best_fire.gy)
            if fire_road is None:
                continue

            path = astar(self.world, tr, fire_road)
            if path:
                truck.dispatch(path, best_fire.gx, best_fire.gy)
                already_targeted.add((best_fire.gx, best_fire.gy))
                self._emit(SimEvent(
                    EventType.UNIT_DISPATCHED,
                    f"Truck {truck.id} auto-dispatched to ({best_fire.gx},{best_fire.gy})",
                    Severity.WARNING,
                ))

    def _record_history(self, dt: float) -> None:
        self._history_timer += dt
        if self._history_timer >= self._history_interval:
            self._history_timer = 0.0
            self.active_fires_history.append(len(self.world.get_burning_cells()))
            if len(self.active_fires_history) > 60:
                self.active_fires_history = self.active_fires_history[-60:]

    # ------------------------------------------------------------------
    # Convenience queries
    # ------------------------------------------------------------------

    def get_active_fires(self) -> int:
        return len(self.world.get_burning_cells())

    def get_deployed_units(self) -> int:
        return sum(1 for t in self.trucks if t.state != TruckState.IDLE)
