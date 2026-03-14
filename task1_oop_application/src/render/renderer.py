# -*- coding: utf-8 -*-
"""
Rendering layer.

Draws the simulation world, fires (with particle effects), fire-truck paths,
and units onto a pygame Surface, clipped to the map viewport.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import pygame

from task1_oop_application.src.core.world import World, CellType
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
        self.particles = ParticleSystem()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def draw(self, sim: Simulation, dt: float = 0.016) -> None:
        """Draw all world layers (including particles), clipped to the viewport."""
        old_clip = self.surface.get_clip()
        self.surface.set_clip(self.viewport)

        # Clear viewport background
        pygame.draw.rect(self.surface, (16, 18, 28), self.viewport)

        self._draw_cells(sim.world)
        self._draw_fires(sim.world)

        # Update and draw particles (fire/smoke effects)
        self.particles.update(dt)
        self._emit_particles(sim.world, dt)
        self.particles.draw(self.surface, self.viewport)

        # Draw path overlays for moving trucks
        for truck in sim.trucks:
            if truck.state in (TruckState.EN_ROUTE, TruckState.EXTINGUISHING, TruckState.RETURNING):
                if truck.path:
                    self._draw_path(truck.path, truck.path_index)

        # Draw entities
        for truck in sim.trucks:
            self._draw_truck(truck)

        # Selection highlight
        if self.selected_cell:
            self._draw_selection(self.selected_cell)

        # Viewport border
        pygame.draw.rect(self.surface, theme.PANEL_BORDER, self.viewport, 2)

        self.surface.set_clip(old_clip)

    # ------------------------------------------------------------------
    # Private draw helpers
    # ------------------------------------------------------------------

    def _draw_cells(self, world: World) -> None:
        cs = self.camera.cell_pixel_size()
        vp = self.viewport

        for x in range(world.width):
            for y in range(world.height):
                sx, sy = self.camera.world_to_screen(x, y)
                # Cull off-screen cells
                if sx + cs < vp.x or sx > vp.right:
                    continue
                if sy + cs < vp.y or sy > vp.bottom:
                    continue

                cell = world.cells[x][y]
                if cell.type == CellType.ROAD:
                    color = theme.COLOR_ROAD
                elif cell.type == CellType.BUILDING:
                    color = theme.COLOR_BUILDING
                elif cell.type == CellType.COMMERCIAL:
                    color = theme.COLOR_COMMERCIAL
                elif cell.type == CellType.STATION:
                    color = theme.COLOR_STATION
                elif cell.type == CellType.PARK:
                    color = theme.COLOR_PARK
                elif cell.type == CellType.WATER:
                    color = theme.COLOR_WATER
                else:
                    color = theme.COLOR_EMPTY

                rect = pygame.Rect(sx, sy, cs, cs)
                pygame.draw.rect(self.surface, color, rect)

                # Subtle grid lines at higher zoom levels
                if self.camera.zoom >= 1.2:
                    pygame.draw.rect(self.surface, (8, 10, 18), rect, 1)

                # Station cross marker
                if cell.type == CellType.STATION and cs >= 8:
                    ctr = rect.center
                    arm = max(2, cs // 3)
                    pygame.draw.line(self.surface, (220, 240, 255),
                                     (ctr[0] - arm, ctr[1]), (ctr[0] + arm, ctr[1]), 2)
                    pygame.draw.line(self.surface, (220, 240, 255),
                                     (ctr[0], ctr[1] - arm), (ctr[0], ctr[1] + arm), 2)

                # Water ripple hint (subtle horizontal lines)
                if cell.type == CellType.WATER and cs >= 6:
                    mid = sy + cs // 2
                    pygame.draw.line(
                        self.surface, (50, 110, 190),
                        (sx + 1, mid), (sx + cs - 2, mid), 1,
                    )

    def _draw_fires(self, world: World) -> None:
        cs = self.camera.cell_pixel_size()
        tick = pygame.time.get_ticks()

        for x in range(world.width):
            for y in range(world.height):
                cell = world.cells[x][y]
                if not cell.burning:
                    continue

                sx, sy = self.camera.world_to_screen(x, y)
                rect = pygame.Rect(sx, sy, cs, cs)

                # Fire base color by intensity
                intensity = cell.fire_intensity
                if intensity < 0.33:
                    base = theme.FIRE_COLORS[0]
                elif intensity < 0.66:
                    base = theme.FIRE_COLORS[1]
                elif intensity < 0.90:
                    base = theme.FIRE_COLORS[2]
                else:
                    base = theme.FIRE_COLORS[3]

                # Animated flicker
                flicker = int(abs((tick % 350) - 175) / 175 * 35)
                color = (
                    min(255, base[0] + flicker),
                    min(255, base[1] + flicker // 2),
                    max(0,   base[2] - flicker),
                )
                pygame.draw.rect(self.surface, color, rect)

                # Flame tip triangle (visible at higher zoom)
                if cs >= 8:
                    ctr = rect.centerx
                    tip_y = sy - max(3, int(cs * 0.65 * intensity))
                    half = max(2, cs // 3)
                    pygame.draw.polygon(
                        self.surface,
                        (255, 235, 80),
                        [(ctr, tip_y), (ctr - half, sy + cs // 2), (ctr + half, sy + cs // 2)],
                    )

    def _emit_particles(self, world: World, dt: float) -> None:
        """Emit fire/smoke particles for all visible burning cells."""
        cs = self.camera.cell_pixel_size()
        vp = self.viewport

        for x in range(world.width):
            for y in range(world.height):
                cell = world.cells[x][y]
                if not cell.burning:
                    continue
                sx, sy = self.camera.world_to_screen(x, y)
                # Only emit for visible cells
                if sx + cs < vp.x or sx > vp.right:
                    continue
                if sy + cs < vp.y or sy > vp.bottom:
                    continue
                self.particles.emit(sx, sy, cs, cell.fire_intensity, (x, y), dt)

    def _draw_path(
        self,
        path: List[Tuple[int, int]],
        from_index: int = 0,
    ) -> None:
        """Draw the remaining portion of a truck's path."""
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
        pygame.draw.rect(self.surface, color, body, border_radius=2)
        pygame.draw.rect(self.surface, (255, 255, 255), body, 1, border_radius=2)

        # Small ID label at higher zoom
        if self.camera.zoom >= 1.5 and cs >= 14:
            font = theme.get_font(14)
            lbl = font.render(str(truck.id), True, (0, 0, 0))
            self.surface.blit(lbl, lbl.get_rect(center=(cx, cy)))

    def _draw_selection(self, cell_pos: Tuple[int, int]) -> None:
        gx, gy = cell_pos
        cs = self.camera.cell_pixel_size()
        sx, sy = self.camera.world_to_screen(gx, gy)
        rect = pygame.Rect(sx, sy, cs, cs)
        pygame.draw.rect(self.surface, (255, 255, 90), rect, 2)
        # Corner accents
        corner = max(3, cs // 5)
        for cx2, cy2 in [(rect.left, rect.top), (rect.right - corner, rect.top),
                         (rect.left, rect.bottom - corner), (rect.right - corner, rect.bottom - corner)]:
            pygame.draw.rect(self.surface, (255, 255, 200),
                             pygame.Rect(cx2, cy2, corner, corner))
