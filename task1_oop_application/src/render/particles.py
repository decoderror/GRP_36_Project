# -*- coding: utf-8 -*-
"""
Particle effects for weather visualization.

Renders animated particles for rain, snow, and wind effects
on the map viewport. Each weather type has distinct visual behavior:
  - rain:  fast blue droplets falling at an angle
  - snow:  slow white flakes drifting with gentle horizontal sway
  - wind:  fast horizontal streaks / dust motes
  - sun:   no particles (clear sky)
"""
from __future__ import annotations

import math
import random
from typing import List, Tuple

import pygame


# ------------------------------------------------------------------
# Particle dataclass (lightweight, no __dict__)
# ------------------------------------------------------------------

class Particle:
    """A single visual particle."""

    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "color", "alpha")

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        life: float,
        size: float,
        color: Tuple[int, int, int],
        alpha: int = 255,
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


# ------------------------------------------------------------------
# Particle System
# ------------------------------------------------------------------

class ParticleSystem:
    """
    Manages and renders weather-dependent particle effects.

    Call :meth:`update` each frame with the current weather string
    and delta-time, then :meth:`draw` to render onto a surface.
    """

    # Maximum simultaneous particles per weather type
    MAX_RAIN_PARTICLES: int = 600
    MAX_SNOW_PARTICLES: int = 400
    MAX_WIND_PARTICLES: int = 350

    # Spawn rates (particles per second)
    RAIN_SPAWN_RATE: float = 300.0
    SNOW_SPAWN_RATE: float = 120.0
    WIND_SPAWN_RATE: float = 100.0

    def __init__(self, viewport: pygame.Rect) -> None:
        self.viewport = viewport
        self.particles: List[Particle] = []
        self._rng = random.Random()
        self._spawn_accum: float = 0.0  # fractional spawn accumulator

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float, weather: str) -> None:
        """Advance all particles and spawn new ones for the current weather."""
        # Remove sun particles or switch weather
        if weather == "sun":
            # Fade out existing particles quickly
            for p in self.particles:
                p.life -= dt * 3.0
            self.particles = [p for p in self.particles if p.life > 0]
            self._spawn_accum = 0.0
            return

        # Update existing particles
        alive: List[Particle] = []
        vp = self.viewport
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt

            # Add slight sway for snow
            if weather == "snow":
                p.x += math.sin(p.life * 3.0) * 8.0 * dt

            # Recycle particles that leave the viewport (wrap around)
            if p.y > vp.bottom:
                p.y = vp.y - 2
                p.x = vp.x + self._rng.random() * vp.width
            if p.x > vp.right + 20:
                p.x = vp.x - 5
                p.y = vp.y + self._rng.random() * vp.height
            if p.x < vp.x - 20:
                p.x = vp.right + 5

            alive.append(p)
        self.particles = alive

        # Spawn new particles
        max_particles, spawn_rate = self._get_weather_params(weather)
        self._spawn_accum += spawn_rate * dt
        to_spawn = int(self._spawn_accum)
        self._spawn_accum -= to_spawn

        for _ in range(to_spawn):
            if len(self.particles) >= max_particles:
                break
            self.particles.append(self._create_particle(weather))

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface, weather: str) -> None:
        """Render all particles onto the surface."""
        if not self.particles:
            return

        old_clip = surface.get_clip()
        surface.set_clip(self.viewport)

        if weather == "rain":
            self._draw_rain(surface)
        elif weather == "snow":
            self._draw_snow(surface)
        elif weather == "wind":
            self._draw_wind(surface)
        else:
            self._draw_generic(surface)

        surface.set_clip(old_clip)

    # ------------------------------------------------------------------
    # Private: weather-specific drawing
    # ------------------------------------------------------------------

    def _draw_rain(self, surface: pygame.Surface) -> None:
        """Draw rain as short diagonal lines (fast droplets)."""
        for p in self.particles:
            fade = min(1.0, p.life / max(p.max_life * 0.3, 0.01))
            alpha = int(p.alpha * fade)
            if alpha < 10:
                continue
            x1 = int(p.x)
            y1 = int(p.y)
            # Rain streak: short line in the fall direction
            x2 = int(p.x - p.vx * 0.02)
            y2 = int(p.y - p.vy * 0.02)
            col = (
                min(255, p.color[0]),
                min(255, p.color[1]),
                min(255, p.color[2]),
            )
            pygame.draw.line(surface, col, (x1, y1), (x2, y2), max(1, int(p.size)))

    def _draw_snow(self, surface: pygame.Surface) -> None:
        """Draw snow as small circles with gentle fade."""
        for p in self.particles:
            fade = min(1.0, p.life / max(p.max_life * 0.3, 0.01))
            alpha_val = int(p.alpha * fade)
            if alpha_val < 10:
                continue
            r = max(1, int(p.size))
            col = (
                min(255, p.color[0]),
                min(255, p.color[1]),
                min(255, p.color[2]),
            )
            pygame.draw.circle(surface, col, (int(p.x), int(p.y)), r)
            # Add a subtle glow for larger flakes
            if r >= 2:
                glow_col = (
                    min(255, col[0] // 2),
                    min(255, col[1] // 2),
                    min(255, col[2] // 2),
                )
                pygame.draw.circle(surface, glow_col, (int(p.x), int(p.y)), r + 1, 1)

    def _draw_wind(self, surface: pygame.Surface) -> None:
        """Draw wind as horizontal streaks / dust lines."""
        for p in self.particles:
            fade = min(1.0, p.life / max(p.max_life * 0.3, 0.01))
            alpha_val = int(p.alpha * fade)
            if alpha_val < 10:
                continue
            x1 = int(p.x)
            y1 = int(p.y)
            # Wind streak: longer horizontal line
            streak_len = int(abs(p.vx) * 0.04)
            x2 = x1 - streak_len
            y2 = y1 - int(p.vy * 0.01)
            col = (
                min(255, p.color[0]),
                min(255, p.color[1]),
                min(255, p.color[2]),
            )
            pygame.draw.line(surface, col, (x1, y1), (x2, y2), max(1, int(p.size)))

    def _draw_generic(self, surface: pygame.Surface) -> None:
        """Fallback: draw as circles."""
        for p in self.particles:
            r = max(1, int(p.size))
            pygame.draw.circle(surface, p.color, (int(p.x), int(p.y)), r)

    # ------------------------------------------------------------------
    # Private: particle creation
    # ------------------------------------------------------------------

    def _create_particle(self, weather: str) -> Particle:
        """Create a new particle appropriate for the given weather type."""
        vp = self.viewport
        rng = self._rng

        if weather == "rain":
            return self._create_rain_particle(vp, rng)
        elif weather == "snow":
            return self._create_snow_particle(vp, rng)
        elif weather == "wind":
            return self._create_wind_particle(vp, rng)
        else:
            return self._create_rain_particle(vp, rng)

    def _create_rain_particle(
        self, vp: pygame.Rect, rng: random.Random
    ) -> Particle:
        """Rain: fast downward diagonal drops, various blues."""
        x = vp.x + rng.random() * vp.width
        y = vp.y + rng.random() * vp.height * 0.1 - vp.height * 0.05
        # Slight angle (wind-like tilt)
        vx = rng.uniform(20, 60)
        vy = rng.uniform(350, 550)
        life = rng.uniform(0.6, 1.5)
        size = rng.uniform(1.0, 2.0)
        blue = rng.randint(170, 240)
        color = (100 + rng.randint(0, 40), 140 + rng.randint(0, 50), blue)
        alpha = rng.randint(120, 200)
        return Particle(x, y, vx, vy, life, size, color, alpha)

    def _create_snow_particle(
        self, vp: pygame.Rect, rng: random.Random
    ) -> Particle:
        """Snow: slow drifting flakes, white/light-blue tones."""
        x = vp.x + rng.random() * vp.width
        y = vp.y - rng.random() * 30
        vx = rng.uniform(-15, 15)
        vy = rng.uniform(30, 80)
        life = rng.uniform(3.0, 7.0)
        size = rng.uniform(1.5, 3.5)
        brightness = rng.randint(200, 255)
        color = (brightness, brightness, min(255, brightness + rng.randint(0, 20)))
        alpha = rng.randint(150, 230)
        return Particle(x, y, vx, vy, life, size, color, alpha)

    def _create_wind_particle(
        self, vp: pygame.Rect, rng: random.Random
    ) -> Particle:
        """Wind: fast horizontal streaks, gray/dusty tones."""
        x = vp.x - rng.random() * 40
        y = vp.y + rng.random() * vp.height
        vx = rng.uniform(250, 500)
        vy = rng.uniform(-20, 20)
        life = rng.uniform(0.8, 2.0)
        size = rng.uniform(1.0, 1.5)
        gray = rng.randint(140, 200)
        color = (gray, gray + rng.randint(-10, 10), gray + rng.randint(-5, 15))
        alpha = rng.randint(80, 160)
        return Particle(x, y, vx, vy, life, size, color, alpha)

    # ------------------------------------------------------------------
    # Private: config lookup
    # ------------------------------------------------------------------

    def _get_weather_params(self, weather: str) -> Tuple[int, float]:
        """Return (max_particles, spawn_rate) for the given weather."""
        if weather == "rain":
            return self.MAX_RAIN_PARTICLES, self.RAIN_SPAWN_RATE
        elif weather == "snow":
            return self.MAX_SNOW_PARTICLES, self.SNOW_SPAWN_RATE
        elif weather == "wind":
            return self.MAX_WIND_PARTICLES, self.WIND_SPAWN_RATE
        else:
            return 0, 0.0
