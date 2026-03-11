# -*- coding: utf-8 -*-
"""Typed event system for the Disaster Response Simulator."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class EventType(Enum):
    FIRE_STARTED = "FIRE_STARTED"
    FIRE_SPREAD = "FIRE_SPREAD"
    FIRE_CONTAINED = "FIRE_CONTAINED"
    UNIT_DISPATCHED = "UNIT_DISPATCHED"
    UNIT_ARRIVED = "UNIT_ARRIVED"
    UNIT_RETURNING = "UNIT_RETURNING"
    WEATHER_CHANGED = "WEATHER_CHANGED"
    SIMULATION_STARTED = "SIMULATION_STARTED"
    SIMULATION_PAUSED = "SIMULATION_PAUSED"
    SIMULATION_RESET = "SIMULATION_RESET"
    DEMO_MODE = "DEMO_MODE"


class Severity(Enum):
    INFO = 0
    WARNING = 1
    CRITICAL = 2


@dataclass
class SimEvent:
    type: EventType
    message: str
    severity: Severity = Severity.INFO
    timestamp: float = field(default_factory=time.time)
    sim_time: float = 0.0
