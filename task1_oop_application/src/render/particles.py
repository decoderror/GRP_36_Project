# -*- coding: utf-8 -*-
"""
Fire and smoke particle system.

Provides animated particles that rise from burning cells to make fires
clearly visible and dramatic.  Each burning cell emits:
  - Fire particles — flickering orange/yellow/red, rise quickly.
  - Smoke particles — gray, semi-transparent, drift upward slowly.

Particle count and size scale with the fire intensity (0.0–1.0).

Usage (called by Renderer.draw every frame):
    particles = ParticleSystem()
    # inside draw loop:
    particles.update(dt)
    for burning_cell:
        particles.emit(screen_x, screen_y, cell_size, intensity)
    particles.draw(surface, viewport_rect)
"""
from __future__ import annotations

import math
import random
from typing import List, Optional, Tuple

import pygame


# ------------------------------------------------------------------
# Tuning constants
# ------------------------------------------------------------------
MAX_PARTICLES: int = 600          # hard cap to keep performance reasonable
FIRE_EMIT_RATE: float = 0.05      # seconds between fire-particle bursts per cell
SMOKE_EMIT_RATE: float = 0.12     # seconds between smoke-particle bursts per cell


class Particle:
    """A single particle with position, velocity, color, and lifetime."""

    __slots__ = (
        "x", "y", "vx", "vy",
        "life", "max_life",
        "color", "size",
        "alpha",
    )

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        life: float,
        color: Tuple[int, int, int],
        size: float,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.alpha: int = 220

    def update(self, dt: float) -> None:
        """Advance the particle by dt seconds."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Slight horizontal drift (turbulence)
        self.vx *= (1.0 - dt * 2.0)
        self.life -= dt
        # Fade out as life expires
        ratio = max(0.0, self.life / self.max_life)
        self.alpha = int(ratio * 220)

    @property
    def alive(self) -> bool:
        return self.life > 0.0


class ParticleSystem:
    """
    Manages all active fire and smoke particles for the simulation.

    Call :meth:`update` once per frame, then :meth:`emit` for each
    burning cell visible on screen, then :meth:`draw`.
    """

    def __init__(self) -> None:
        self._particles: List[Particle] = []
        self._rng: random.Random = random.Random()
        # Per-cell emission timers keyed by (gx, gy)
        self._fire_timers: dict = {}
        self._smoke_timers: dict = {}
        # Cached draw surface (recreated only when viewport size changes)
        self._draw_surf: Optional[pygame.Surface] = None
        self._draw_surf_size: Tuple[int, int] = (0, 0)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """Update all particles (call once per frame before emit/draw)."""
        self._particles = [p for p in self._particles if p.alive]
        for p in self._particles:
            p.update(dt)

    def emit(
        self,
        screen_x: int,
        screen_y: int,
        cell_size: int,
        intensity: float,
        cell_key: Tuple[int, int],
        dt: float,
    ) -> None:
        """
        Emit fire and smoke particles for a burning cell.

        :param screen_x:  Top-left x of the cell in screen coordinates.
        :param screen_y:  Top-left y of the cell in screen coordinates.
        :param cell_size: Pixel width/height of one cell (varies with zoom).
        :param intensity: Fire intensity 0.0–1.0 (affects count and size).
        :param cell_key:  (gx, gy) used for per-cell rate limiting.
        :param dt:        Frame delta-time in seconds.
        """
        if len(self._particles) >= MAX_PARTICLES:
            return

        cs = max(4, cell_size)
        rng = self._rng

        # ── Fire particles ─────────────────────────────────────────
        ft = self._fire_timers.get(cell_key, 0.0) - dt
        if ft <= 0.0:
            count = int(2 + 4 * intensity)
            for _ in range(count):
                if len(self._particles) >= MAX_PARTICLES:
                    break
                px = screen_x + rng.uniform(0.15, 0.85) * cs
                py = screen_y + rng.uniform(0.4, 0.9) * cs
                speed = rng.uniform(30, 80) * (0.5 + intensity)
                angle = rng.uniform(-0.45, 0.45) * math.pi  # mostly upward
                vx = math.sin(angle) * speed
                vy = -abs(math.cos(angle)) * speed         # always rises
                life = rng.uniform(0.25, 0.6 + 0.4 * intensity)
                r = rng.randint(210, 255)
                g = rng.randint(int(60 * (1 - intensity)), 170)
                b = rng.randint(0, 40)
                size = rng.uniform(2, max(3.0, cs * 0.35 * intensity))
                self._particles.append(Particle(px, py, vx, vy, life, (r, g, b), size))
            ft = FIRE_EMIT_RATE
        self._fire_timers[cell_key] = ft

        # ── Smoke particles ────────────────────────────────────────
        st = self._smoke_timers.get(cell_key, 0.0) - dt
        if st <= 0.0:
            smoke_count = int(1 + 2 * intensity)
            for _ in range(smoke_count):
                if len(self._particles) >= MAX_PARTICLES:
                    break
                px = screen_x + rng.uniform(0.2, 0.8) * cs
                py = screen_y + rng.uniform(0.0, 0.3) * cs
                speed = rng.uniform(8, 22) * (0.4 + 0.6 * intensity)
                angle = rng.uniform(-0.25, 0.25) * math.pi
                vx = math.sin(angle) * speed
                vy = -abs(math.cos(angle)) * speed
                life = rng.uniform(0.6, 1.4)
                gray = rng.randint(110, 175)
                size = rng.uniform(3, max(5.0, cs * 0.55 * (0.5 + 0.5 * intensity)))
                self._particles.append(Particle(px, py, vx, vy, life, (gray, gray, gray), size))
            st = SMOKE_EMIT_RATE
        self._smoke_timers[cell_key] = st

    def draw(self, surface: pygame.Surface, viewport: pygame.Rect) -> None:
        """
        Render all particles to *surface*, clipped to *viewport*.

        Uses a cached SRCALPHA surface to allow per-particle transparency
        without creating a new Surface per particle.
        """
        if not self._particles:
            return

        vsize = (viewport.width, viewport.height)
        if self._draw_surf is None or self._draw_surf_size != vsize:
            self._draw_surf = pygame.Surface(vsize, pygame.SRCALPHA)
            self._draw_surf_size = vsize

        self._draw_surf.fill((0, 0, 0, 0))  # clear to transparent

        vx0, vy0 = viewport.x, viewport.y
        for p in self._particles:
            lx = int(p.x - vx0)
            ly = int(p.y - vy0)
            if lx < 0 or ly < 0 or lx >= vsize[0] or ly >= vsize[1]:
                continue
            radius = max(1, int(p.size))
            pygame.draw.circle(
                self._draw_surf,
                (*p.color, p.alpha),
                (lx, ly),
                radius,
            )

        surface.blit(self._draw_surf, viewport.topleft)

    def clear(self) -> None:
        """Remove all particles (call on simulation reset)."""
        self._particles.clear()
        self._fire_timers.clear()
        self._smoke_timers.clear()
