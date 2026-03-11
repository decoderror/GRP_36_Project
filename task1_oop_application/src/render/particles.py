# -*- coding: utf-8 -*-
"""
Particle system for weather and fire effects.

Classes:
    Particle      — individual particle data
    ParticleSystem — manages and renders all particles

Usage:
    ps = ParticleSystem(max_particles=1200)
    ps.update(dt, wind_angle_deg, weather, burning_cells, camera, viewport)
    ps.draw(surface, viewport)
"""
from __future__ import annotations

import math
import random
from typing import List, Tuple

import pygame


# ---------------------------------------------------------------------------
# Particle  (lightweight data object, no methods)
# ---------------------------------------------------------------------------

class Particle:
    """Single particle: position, velocity, life, appearance."""

    __slots__ = (
        "x", "y", "vx", "vy",
        "life", "max_life",
        "size", "color", "alpha",
        "kind",     # "snow"|"rain"|"wind"|"smoke"|"ember"
    )

    def __init__(
        self,
        x: float, y: float,
        vx: float, vy: float,
        life: float,
        size: float,
        color: Tuple[int, int, int],
        alpha: int = 220,
        kind: str = "snow",
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color
        self.alpha = alpha
        self.kind = kind


# ---------------------------------------------------------------------------
# ParticleSystem
# ---------------------------------------------------------------------------

class ParticleSystem:
    """
    Manages all active particles.

    Call update() every frame, then draw() to render onto the viewport.
    """

    # Maximum particles of each type to cap performance
    MAX_WEATHER = 600
    MAX_FIRE    = 400

    def __init__(self, max_particles: int = 1200) -> None:
        self.max_particles = max_particles
        self._particles: List[Particle] = []
        self._rng = random.Random(99)
        self._weather_timer: float = 0.0
        self._fire_timer:    float = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(
        self,
        dt: float,
        wind_angle_deg: float,
        weather: str,
        burning_cells: list,   # List[Cell]
        camera,                # Camera instance
        viewport: pygame.Rect,
    ) -> None:
        """Update all particles and spawn new ones."""
        # Wind vector (screen space: positive X = right, positive Y = down)
        wind_rad = math.radians(wind_angle_deg)
        wind_sx =  math.cos(wind_rad)   # east = positive screen-X
        wind_sy = -math.sin(wind_rad)   # north = negative screen-Y (up)

        self._spawn_weather(dt, weather, wind_sx, wind_sy, viewport)
        self._spawn_fire(dt, burning_cells, camera, viewport)
        self._tick(dt, wind_sx, wind_sy)

    def draw(self, surface: pygame.Surface, viewport: pygame.Rect) -> None:
        """Draw all particles, clipped to the viewport."""
        old_clip = surface.get_clip()
        surface.set_clip(viewport)

        for p in self._particles:
            if p.kind == "rain":
                self._draw_rain(surface, p)
            elif p.kind == "wind":
                self._draw_wind(surface, p)
            else:
                self._draw_circle(surface, p)

        surface.set_clip(old_clip)

    # ------------------------------------------------------------------
    # Spawning
    # ------------------------------------------------------------------

    def _count_weather(self) -> int:
        return sum(1 for p in self._particles if p.kind in ("snow", "rain", "wind"))

    def _count_fire(self) -> int:
        return sum(1 for p in self._particles if p.kind in ("smoke", "ember"))

    def _spawn_weather(
        self,
        dt: float,
        weather: str,
        wind_sx: float,
        wind_sy: float,
        viewport: pygame.Rect,
    ) -> None:
        if weather == "sun":
            return

        self._weather_timer += dt
        rates = {"rain": 80, "snow": 40, "wind": 30}
        rate = rates.get(weather, 0)
        interval = 1.0 / rate if rate > 0 else 999.0

        while self._weather_timer >= interval and self._count_weather() < self.MAX_WEATHER:
            self._weather_timer -= interval
            rx = self._rng.uniform(viewport.left - 20, viewport.right + 20)
            ry = self._rng.uniform(viewport.top - 40, viewport.top - 5)

            if weather == "snow":
                size  = self._rng.uniform(2.0, 5.0)
                speed = self._rng.uniform(60.0, 120.0)
                vx = wind_sx * self._rng.uniform(15.0, 45.0)
                vy = speed
                life  = self._rng.uniform(3.0, 7.0)
                gray  = self._rng.randint(210, 255)
                blue  = self._rng.randint(230, 255)
                color = (gray, gray, blue)
                self._emit(rx, ry, vx, vy, life, size, color, 200, "snow")

            elif weather == "rain":
                speed = self._rng.uniform(400.0, 600.0)
                vx = wind_sx * self._rng.uniform(40.0, 120.0)
                vy = speed
                life = self._rng.uniform(0.4, 0.8)
                color = (160, 185, 220)
                self._emit(rx, ry, vx, vy, life, 1.0, color, 160, "rain")

            elif weather == "wind":
                ry = self._rng.uniform(viewport.top, viewport.bottom)
                rx = viewport.left - 10
                speed = self._rng.uniform(200.0, 350.0)
                vx = speed * (wind_sx if abs(wind_sx) > 0.1 else 1.0)
                vy = wind_sy * self._rng.uniform(20.0, 60.0)
                life = self._rng.uniform(0.6, 1.4)
                gray = self._rng.randint(140, 180)
                color = (gray, gray + 5, gray + 10)
                self._emit(rx, ry, vx, vy, life, 1.0, color, 80, "wind")

    def _spawn_fire(
        self,
        dt: float,
        burning_cells: list,
        camera,
        viewport: pygame.Rect,
    ) -> None:
        if not burning_cells:
            return

        self._fire_timer += dt
        n = min(len(burning_cells), 20)
        interval = max(0.02, 0.15 / max(1, n))

        while self._fire_timer >= interval and self._count_fire() < self.MAX_FIRE:
            self._fire_timer -= interval
            cell = self._rng.choice(burning_cells)
            cs = camera.cell_pixel_size()
            sx, sy = camera.world_to_screen(cell.gx, cell.gy)
            cx = sx + cs // 2
            cy = sy + cs // 2

            if not viewport.collidepoint(cx, cy):
                continue

            intensity = cell.fire_intensity

            # Smoke particles
            if self._rng.random() < 0.65:
                ox = self._rng.uniform(-cs * 0.3, cs * 0.3)
                oy = self._rng.uniform(-cs * 0.3, cs * 0.3)
                vx = self._rng.uniform(-18.0, 18.0)
                vy = -self._rng.uniform(25.0, 55.0 + 40.0 * intensity)
                life = self._rng.uniform(1.5, 3.5) * (0.6 + 0.4 * intensity)
                size = self._rng.uniform(3.0, 8.0 + 8.0 * intensity)
                v = self._rng.randint(60, 100)
                b = self._rng.randint(80, 110)
                color = (v, v, b)
                self._emit(cx + ox, cy + oy, vx, vy, life, size, color, 120, "smoke")

            # Ember particles
            if intensity > 0.3 and self._rng.random() < 0.35 * intensity:
                ox = self._rng.uniform(-cs * 0.2, cs * 0.2)
                vx = self._rng.uniform(-40.0, 40.0)
                vy = -self._rng.uniform(60.0, 120.0 + 80.0 * intensity)
                life = self._rng.uniform(0.5, 1.2)
                size = self._rng.uniform(1.5, 3.0)
                r = self._rng.randint(220, 255)
                g = self._rng.randint(80, 180)
                color = (r, g, 0)
                self._emit(cx + ox, cy, vx, vy, life, size, color, 230, "ember")

    def _emit(
        self,
        x: float, y: float,
        vx: float, vy: float,
        life: float,
        size: float,
        color: Tuple[int, int, int],
        alpha: int,
        kind: str,
    ) -> None:
        if len(self._particles) < self.max_particles:
            self._particles.append(
                Particle(x, y, vx, vy, life, size, color, alpha, kind)
            )

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def _tick(self, dt: float, wind_sx: float, wind_sy: float) -> None:
        alive = []
        for p in self._particles:
            p.life -= dt
            if p.life <= 0:
                continue

            if p.kind == "snow":
                p.vx += wind_sx * 10.0 * dt
            elif p.kind == "smoke":
                p.vx += wind_sx * 8.0 * dt
                p.size += 2.5 * dt           # smoke expands
            elif p.kind == "ember":
                p.vy += 80.0 * dt            # gravity pulls embers down

            p.x += p.vx * dt
            p.y += p.vy * dt
            alive.append(p)
        self._particles = alive

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _draw_circle(surface: pygame.Surface, p: Particle) -> None:
        """Draw snow, smoke, ember as alpha circle."""
        alpha = int(p.alpha * (p.life / p.max_life))
        alpha = max(0, min(255, alpha))
        r = max(1, int(p.size))
        try:
            s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p.color, alpha), (r + 1, r + 1), r)
            surface.blit(s, (int(p.x) - r - 1, int(p.y) - r - 1))
        except Exception:
            pass

    @staticmethod
    def _draw_rain(surface: pygame.Surface, p: Particle) -> None:
        """Draw rain as a short streak using a minimal bounding surface."""
        alpha = int(160 * (p.life / p.max_life))
        alpha = max(0, min(255, alpha))
        speed = math.hypot(p.vx, p.vy)
        if speed < 1:
            return
        length = min(12, int(speed * 0.025))
        x0, y0 = int(p.x), int(p.y)
        ex = int(p.x - p.vx / speed * length)
        ey = int(p.y - p.vy / speed * length)
        try:
            # Use a small bounding box instead of a full-screen surface
            min_x = min(x0, ex) - 1
            min_y = min(y0, ey) - 1
            w = abs(x0 - ex) + 3
            h = abs(y0 - ey) + 3
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.line(s, (*p.color, alpha),
                             (x0 - min_x, y0 - min_y), (ex - min_x, ey - min_y), 1)
            surface.blit(s, (min_x, min_y))
        except Exception:
            pass

    @staticmethod
    def _draw_wind(surface: pygame.Surface, p: Particle) -> None:
        """Draw wind as a thin translucent streak using a minimal bounding surface."""
        alpha = int(70 * (p.life / p.max_life))
        alpha = max(0, min(255, alpha))
        length = min(30, int(math.hypot(p.vx, p.vy) * 0.06))
        speed = math.hypot(p.vx, p.vy)
        if speed < 1:
            return
        x0, y0 = int(p.x), int(p.y)
        ex = int(p.x - p.vx / speed * length)
        ey = int(p.y - p.vy / speed * length)
        try:
            # Use a small bounding box instead of a full-screen surface
            min_x = min(x0, ex) - 1
            min_y = min(y0, ey) - 1
            w = abs(x0 - ex) + 3
            h = abs(y0 - ey) + 3
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.line(s, (*p.color, alpha),
                             (x0 - min_x, y0 - min_y), (ex - min_x, ey - min_y), 1)
            surface.blit(s, (min_x, min_y))
        except Exception:
            pass
