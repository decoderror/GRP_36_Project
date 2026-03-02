"""
Task 1 - Preliminary code (OOP scaffold)

This file is a pre-submission skeleton to demonstrate OOP design:
- classes
- inheritance
- polymorphism (method overriding)
- composition (City contains buildings/units/weather)
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class WeatherType(Enum):
    NO_WIND = auto()
    STRONG_WIND = auto()
    LIGHT_RAIN = auto()


class Weather:
    def __init__(self, weather_type: WeatherType = WeatherType.NO_WIND):
        self._type = weather_type  # encapsulation

    @property
    def weather_type(self) -> WeatherType:
        return self._type

    def set_weather(self, weather_type: WeatherType) -> None:
        self._type = weather_type

    def fire_spread_multiplier(self) -> float:
        if self._type == WeatherType.STRONG_WIND:
            return 2.0
        if self._type == WeatherType.LIGHT_RAIN:
            return 0.5
        return 1.0


class Building:
    def __init__(self, pos: Point):
        self._pos = pos
        self._on_fire = False

    @property
    def pos(self) -> Point:
        return self._pos

    @property
    def on_fire(self) -> bool:
        return self._on_fire

    def ignite(self) -> None:
        self._on_fire = True

    def extinguish(self) -> None:
        self._on_fire = False

    def flammability(self) -> float:
        return 1.0


class FlammableBuilding(Building):
    # inheritance: specialized building type
    def flammability(self) -> float:
        return 1.5


class EmergencyUnit:
    def __init__(self, unit_id: str, pos: Point):
        self._unit_id = unit_id
        self._pos = pos

    @property
    def unit_id(self) -> str:
        return self._unit_id

    @property
    def pos(self) -> Point:
        return self._pos

    def step(self) -> None:
        """Polymorphic behavior hook."""
        raise NotImplementedError


class FireTruck(EmergencyUnit):
    def __init__(self, unit_id: str, pos: Point, speed: int = 2):
        super().__init__(unit_id, pos)
        self._speed = speed

    def step(self) -> None:
        # placeholder for movement/pathfinding logic
        print(f"[FireTruck {self.unit_id}] step at {self.pos} (speed={self._speed})")

    def extinguish(self, building: Building) -> None:
        if building.on_fire:
            building.extinguish()
            print(f"[FireTruck {self.unit_id}] extinguished fire at {building.pos}")


class City:
    def __init__(self, width: int, height: int, weather: Weather):
        self.width = width
        self.height = height
        self.weather = weather  # composition
        self.buildings: list[Building] = []
        self.units: list[EmergencyUnit] = []

    def add_building(self, building: Building) -> None:
        self.buildings.append(building)

    def add_unit(self, unit: EmergencyUnit) -> None:
        self.units.append(unit)

    def tick(self) -> None:
        for unit in self.units:
            unit.step()


if __name__ == "__main__":
    weather = Weather(WeatherType.NO_WIND)
    city = City(width=20, height=20, weather=weather)

    b1 = FlammableBuilding(Point(10, 10))
    b1.ignite()
    city.add_building(b1)

    truck = FireTruck("Engine-01", Point(0, 0))
    city.add_unit(truck)

    city.tick()
    truck.extinguish(b1)
