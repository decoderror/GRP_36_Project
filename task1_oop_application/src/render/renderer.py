# -*- coding: utf-8 -*-
"""
Rendering layer.

Draws the simulation world, fires (with glow + gradient), fire-truck paths,
units, and the particle layer onto the pygame viewport surface.
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

import pygame

from task1_oop_application.src.core.world import World, CellType, BURNABLE_TYPES
from task1_oop_application.src.core.entities import FireTruck, TruckState
from task1_oop_application.src.core.simulation import Simulation
from task1_oop_application.src.render.camera import Camera
from task1_oop_application.src.render import theme
from task1_oop_application.src.render.particles import ParticleSystem


class Renderer:
    """Renders the simulation world to a pygame Surface."""

    def __init__(
        self,
        surface: pygame.Surface,
        viewport: pygame.Rect,
        camera: Camera,
    ) -> None:
        self.surface = surface
        self.viewport = viewport
        self.camera = camera
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.particles = ParticleSystem(max_particles=1400)

        # Pre-cache glow surfaces for performance (5 intensity levels)
        self._glow_cache: dict = {}

    def clear_cache(self) -> None:
        """Discard cached glow surfaces (call after a simulation reset)."""
        self._glow_cache.clear()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def draw(self, sim: Simulation, dt: float = 1 / 60.0) -> None:
        """Draw all world layers, clipped to the viewport."""
        old_clip = self.surface.get_clip()
        self.surface.set_clip(self.viewport)

        # Clear viewport background
        pygame.draw.rect(self.surface, (15, 17, 25), self.viewport)

        # ── 1. World tiles ──────────────────────────────────────────
        self._draw_cells(sim.world)

        # ── 2. Glow layer (before fire cells, behind units) ─────────
        self._draw_fire_glow(sim.world)

        # ── 3. Fire cells ───────────────────────────────────────────
        self._draw_fires(sim.world)

        # ── 4. Truck paths ──────────────────────────────────────────
        for truck in sim.trucks:
            if truck.state in (TruckState.EN_ROUTE, TruckState.EXTINGUISHING, TruckState.RETURNING):
                if truck.path:
                    self._draw_path(truck.path, truck.path_index)

        # ── 5. Units ────────────────────────────────────────────────
        for truck in sim.trucks:
            self._draw_truck(truck)

        # ── 6. Selection highlight ──────────────────────────────────
        if self.selected_cell:
            self._draw_selection(self.selected_cell)

        # ── 7. Particles (weather + fire smoke/embers) ──────────────
        burning = sim.world.get_burning_cells()
        self.particles.update(
            dt=dt,
            wind_angle_deg=sim.wind_angle,
            weather=sim.weather,
            burning_cells=burning,
            camera=self.camera,
            viewport=self.viewport,
        )
        self.particles.draw(self.surface, self.viewport)

        # ── 8. Wind direction arrow ──────────────────────────────────
        if sim.weather == "wind":
            self._draw_wind_arrow(sim.wind_angle)

        # ── 9. Viewport border ───────────────────────────────────────
        pygame.draw.rect(self.surface, theme.PANEL_BORDER, self.viewport, 1)

        self.surface.set_clip(old_clip)

    # ------------------------------------------------------------------
    # Private draw helpers
    # ------------------------------------------------------------------

    def _draw_cells(self, world: World) -> None:
        cs = self.camera.cell_pixel_size()
        vp = self.viewport

        color_map = {
            CellType.ROAD:        theme.COLOR_ROAD,
            CellType.BUILDING:    theme.COLOR_BUILDING,
            CellType.RESIDENTIAL: theme.COLOR_RESIDENTIAL,
            CellType.OFFICE:      theme.COLOR_OFFICE,
            CellType.INDUSTRIAL:  theme.COLOR_INDUSTRIAL,
            CellType.STATION:     theme.COLOR_STATION,
            CellType.PARK:        theme.COLOR_PARK,
            CellType.EMPTY:       theme.COLOR_EMPTY,
        }

        for x in range(world.width):
            for y in range(world.height):
                sx, sy = self.camera.world_to_screen(x, y)
                # Cull off-screen cells
                if sx + cs < vp.x or sx > vp.right:
                    continue
                if sy + cs < vp.y or sy > vp.bottom:
                    continue

                cell = world.cells[x][y]
                if cell.burning:
                    continue  # fire cells drawn separately

                color = color_map.get(cell.type, theme.COLOR_EMPTY)
                rect = pygame.Rect(sx, sy, cs, cs)
                pygame.draw.rect(self.surface, color, rect)

                # Subtle grid lines at higher zoom
                if cs >= 12:
                    pygame.draw.rect(self.surface, (8, 10, 16), rect, 1)

                # Station: blue cross + badge
                if cell.type == CellType.STATION and cs >= 8:
                    self._draw_station_marker(rect, cs)

                # Park: green dot detail
                elif cell.type == CellType.PARK and cs >= 10:
                    dot_r = max(1, cs // 5)
                    ctr = rect.center
                    pygame.draw.circle(self.surface, (50, 130, 70), ctr, dot_r)

                # Road centerline at high zoom
                elif cell.type == CellType.ROAD and cs >= 14:
                    mx, my = rect.centerx, rect.centery
                    hl = cs // 3
                    pygame.draw.line(
                        self.surface, (90, 95, 110),
                        (mx - hl, my), (mx + hl, my), 1,
                    )

    def _draw_station_marker(self, rect: pygame.Rect, cs: int) -> None:
        """Draw a fire station cross + blue background."""
        ctr = rect.center
        arm = max(3, cs // 3)
        pygame.draw.line(self.surface, (120, 200, 255),
                         (ctr[0] - arm, ctr[1]), (ctr[0] + arm, ctr[1]), max(2, cs // 6))
        pygame.draw.line(self.surface, (120, 200, 255),
                         (ctr[0], ctr[1] - arm), (ctr[0], ctr[1] + arm), max(2, cs // 6))

    def _draw_fire_glow(self, world: World) -> None:
        """Draw soft glow halos behind fire cells for ambient light effect."""
        cs = self.camera.cell_pixel_size()
        if cs < 8:
            return

        vp = self.viewport
        for x in range(world.width):
            for y in range(world.height):
                cell = world.cells[x][y]
                if not cell.burning:
                    continue
                sx, sy = self.camera.world_to_screen(x, y)
                if sx + cs < vp.x or sx > vp.right or sy + cs < vp.y or sy > vp.bottom:
                    continue

                intensity = cell.fire_intensity
                glow_r = int(cs * (1.2 + 1.8 * intensity))
                glow_r = min(glow_r, 80)
                cx = sx + cs // 2
                cy = sy + cs // 2

                bucket = int(intensity * 4)  # 0–4
                key = (bucket, glow_r)
                if key not in self._glow_cache:
                    d = glow_r * 2 + 2
                    gsurf = pygame.Surface((d, d), pygame.SRCALPHA)
                    r_val, g_val = (255, 60 + bucket * 40)
                    # Outer soft fill
                    pygame.draw.circle(gsurf, (r_val, g_val, 0, 40),
                                       (glow_r + 1, glow_r + 1), glow_r)
                    # Bright inner ring outline for visual depth
                    pygame.draw.circle(gsurf, (r_val, min(255, g_val + 40), 0, 60),
                                       (glow_r + 1, glow_r + 1), max(1, glow_r // 2), 2)
                    self._glow_cache[key] = gsurf

                gsurf = self._glow_cache[key]
                self.surface.blit(gsurf, (cx - glow_r - 1, cy - glow_r - 1))

    def _draw_fires(self, world: World) -> None:
        cs = self.camera.cell_pixel_size()
        tick = pygame.time.get_ticks()
        vp = self.viewport

        for x in range(world.width):
            for y in range(world.height):
                cell = world.cells[x][y]
                if not cell.burning:
                    continue

                sx, sy = self.camera.world_to_screen(x, y)
                if sx + cs < vp.x or sx > vp.right or sy + cs < vp.y or sy > vp.bottom:
                    continue

                rect = pygame.Rect(sx, sy, cs, cs)
                intensity = cell.fire_intensity

                base = theme.fire_color(intensity)

                # Animated flicker
                flicker = int(abs((tick % 350) - 175) / 175 * 30)
                color = (
                    min(255, base[0] + flicker),
                    min(255, base[1] + flicker // 2),
                    max(0,   base[2] - flicker // 3),
                )
                pygame.draw.rect(self.surface, color, rect)

                if cs >= 10:
                    self._draw_flame_tip(rect, cs, intensity, tick)

    def _draw_flame_tip(
        self,
        rect: pygame.Rect,
        cs: int,
        intensity: float,
        tick: int,
    ) -> None:
        """Draw flickering flame triangle above a burning cell."""
        ctr = rect.centerx
        wave = math.sin(tick * 0.008 + rect.x * 0.3) * 0.25
        tip_h = max(3, int(cs * (0.5 + 0.5 * intensity + wave * intensity)))
        tip_y = rect.top - tip_h
        half = max(2, cs // 3)

        pygame.draw.polygon(
            self.surface,
            (255, int(130 + 80 * intensity), 0),
            [(ctr, tip_y), (ctr - half, rect.top), (ctr + half, rect.top)],
        )
        inner_h = tip_h // 2
        pygame.draw.polygon(
            self.surface,
            (255, min(255, int(200 + 55 * intensity)), int(80 * intensity)),
            [(ctr, tip_y + inner_h), (ctr - half // 2, rect.top), (ctr + half // 2, rect.top)],
        )

    def _draw_path(
        self,
        path: List[Tuple[int, int]],
        from_index: int = 0,
    ) -> None:
        if len(path) < 2:
            return
        cs = self.camera.cell_pixel_size()
        half = cs // 2

        remaining = path[max(0, from_index - 1):]
        points = [
            (self.camera.world_to_screen(gx, gy)[0] + half,
             self.camera.world_to_screen(gx, gy)[1] + half)
            for gx, gy in remaining
        ]
        if len(points) >= 2:
            pygame.draw.lines(self.surface, (80, 190, 255), False, points, 2)
        for pt in points:
            pygame.draw.circle(self.surface, (60, 150, 220), pt, max(2, cs // 6))

    def _draw_truck(self, truck: FireTruck) -> None:
        cs = self.camera.cell_pixel_size()
        sx, sy = self.camera.world_to_screen(truck.x, truck.y)

        color_map = {
            TruckState.IDLE:          theme.TRUCK_IDLE,
            TruckState.EN_ROUTE:      theme.TRUCK_EN_ROUTE,
            TruckState.EXTINGUISHING: theme.TRUCK_EXTINGUISHING,
            TruckState.RETURNING:     theme.TRUCK_RETURNING,
        }
        color = color_map.get(truck.state, theme.TEXT_PRIMARY)

        size = max(6, cs * 3 // 5)
        cx = sx + cs // 2
        cy = sy + cs // 2
        body = pygame.Rect(cx - size // 2, cy - size // 2, size, size)
        pygame.draw.rect(self.surface, color, body, border_radius=3)
        pygame.draw.rect(self.surface, (255, 255, 255), body, 1, border_radius=3)

        if self.camera.zoom >= 1.5 and cs >= 14:
            font = theme.get_font(16)
            lbl = font.render(str(truck.id), True, (0, 0, 0))
            self.surface.blit(lbl, lbl.get_rect(center=(cx, cy)))

    def _draw_selection(self, cell_pos: Tuple[int, int]) -> None:
        gx, gy = cell_pos
        cs = self.camera.cell_pixel_size()
        sx, sy = self.camera.world_to_screen(gx, gy)
        rect = pygame.Rect(sx, sy, cs, cs)
        pygame.draw.rect(self.surface, (255, 255, 90), rect, 2)
        corner = max(3, cs // 5)
        for cx2, cy2 in [(rect.left, rect.top), (rect.right - corner, rect.top),
                         (rect.left, rect.bottom - corner), (rect.right - corner, rect.bottom - corner)]:
            pygame.draw.rect(self.surface, (255, 255, 200),
                             pygame.Rect(cx2, cy2, corner, corner))

    def _draw_wind_arrow(self, wind_angle_deg: float) -> None:
        """Draw a small wind direction indicator in the top-right of the viewport."""
        vp = self.viewport
        cx = vp.right - 40
        cy = vp.top + 40
        r = 20

        rad = math.radians(wind_angle_deg)
        ex = cx + int(r * math.cos(rad))
        ey = cy - int(r * math.sin(rad))

        pygame.draw.circle(self.surface, (40, 45, 60), (cx, cy), r + 4)
        pygame.draw.circle(self.surface, (60, 65, 80), (cx, cy), r + 4, 1)
        pygame.draw.line(self.surface, (180, 200, 255), (cx, cy), (ex, ey), 2)
        pygame.draw.circle(self.surface, (120, 180, 255), (ex, ey), 4)
        font = theme.get_font(16)
        theme.draw_text(self.surface, "W", font, theme.TEXT_DIM, cx - 5, cy + r + 6)
