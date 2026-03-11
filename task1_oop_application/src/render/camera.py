# -*- coding: utf-8 -*-
"""
Camera: viewport pan and zoom for the map display.

Supports:
  - Mouse-wheel zoom (zooming towards the cursor position)
  - Right-mouse-drag pan
  - Programmatic centering on the world
"""
from __future__ import annotations

from typing import Optional, Tuple

import pygame


class Camera:
    """Maps grid coordinates to/from screen pixels within a viewport rectangle."""

    MIN_ZOOM: float = 0.4
    MAX_ZOOM: float = 4.0
    ZOOM_FACTOR: float = 0.15   # fractional step per scroll tick

    def __init__(self, viewport: pygame.Rect, cell_size: int = 20) -> None:
        self.viewport: pygame.Rect = viewport
        self.cell_size: int = cell_size
        self.zoom: float = 1.0
        self.offset_x: float = 0.0   # world-space offset (pixels / zoom)
        self.offset_y: float = 0.0

        self._drag_start: Optional[Tuple[int, int]] = None
        self._drag_offset_start: Tuple[float, float] = (0.0, 0.0)

    # ------------------------------------------------------------------
    # Coordinate transforms
    # ------------------------------------------------------------------

    def world_to_screen(self, gx: float, gy: float) -> Tuple[int, int]:
        sx = int(self.viewport.x + (gx * self.cell_size + self.offset_x) * self.zoom)
        sy = int(self.viewport.y + (gy * self.cell_size + self.offset_y) * self.zoom)
        return sx, sy

    def screen_to_grid(self, sx: int, sy: int) -> Tuple[int, int]:
        lx = (sx - self.viewport.x) / self.zoom
        ly = (sy - self.viewport.y) / self.zoom
        gx = int(lx / self.cell_size - self.offset_x / self.cell_size)
        gy = int(ly / self.cell_size - self.offset_y / self.cell_size)
        return gx, gy

    def cell_pixel_size(self) -> int:
        return max(1, int(self.cell_size * self.zoom))

    # ------------------------------------------------------------------
    # Zoom (towards mouse cursor)
    # ------------------------------------------------------------------

    def zoom_at(self, screen_pos: Tuple[int, int], factor: float) -> None:
        old_zoom = self.zoom
        new_zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, self.zoom * factor))
        if new_zoom == old_zoom:
            return

        # Keep the world point under the cursor stationary.
        # In viewport-local coordinates at the OLD zoom:
        #   world_x = (screen_x - viewport_x) / old_zoom - offset_x
        # We want world_x to remain the same after the zoom change, so:
        #   (screen_x - viewport_x) / new_zoom - new_offset_x  ==  world_x
        # Solving: new_offset_x = (screen_x - viewport_x) / new_zoom - world_x
        vx = screen_pos[0] - self.viewport.x
        vy = screen_pos[1] - self.viewport.y
        world_x = vx / old_zoom - self.offset_x
        world_y = vy / old_zoom - self.offset_y

        self.zoom = new_zoom
        self.offset_x = vx / new_zoom - world_x
        self.offset_y = vy / new_zoom - world_y

    def handle_mouse_wheel(self, event: pygame.event.Event) -> None:
        if not self.viewport.collidepoint(pygame.mouse.get_pos()):
            return
        factor = (1 + self.ZOOM_FACTOR) if event.y > 0 else 1 / (1 + self.ZOOM_FACTOR)
        self.zoom_at(pygame.mouse.get_pos(), factor)

    # ------------------------------------------------------------------
    # Pan (right-mouse drag)
    # ------------------------------------------------------------------

    def start_drag(self, screen_pos: Tuple[int, int]) -> None:
        self._drag_start = screen_pos
        self._drag_offset_start = (self.offset_x, self.offset_y)

    def update_drag(self, screen_pos: Tuple[int, int]) -> None:
        if self._drag_start is None:
            return
        dx = (screen_pos[0] - self._drag_start[0]) / self.zoom
        dy = (screen_pos[1] - self._drag_start[1]) / self.zoom
        self.offset_x = self._drag_offset_start[0] + dx
        self.offset_y = self._drag_offset_start[1] + dy

    def end_drag(self) -> None:
        self._drag_start = None

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def center_on(self, world_width: int, world_height: int) -> None:
        """Centre the world in the viewport at current zoom."""
        vw = self.viewport.width
        vh = self.viewport.height
        world_px = world_width * self.cell_size
        world_py = world_height * self.cell_size
        self.offset_x = (vw / self.zoom - world_px) / 2
        self.offset_y = (vh / self.zoom - world_py) / 2
