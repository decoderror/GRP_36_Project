# -*- coding: utf-8 -*-
"""
Theme constants: colors, font helpers, and drawing utilities.

Uses only ``pygame.font.Font(None, size)`` (no SysFont) to avoid
Windows font-enumeration issues.

Color semantics (for Legend):
  Light gray  = Roads
  Green       = Parks / Green space
  Dark gray   = Residential
  Slate/Purple= Office
  Brown/Orange= Industrial
  Blue        = Fire Station
  Red→Yellow  = Fire intensity gradient
  Gray/blue   = Smoke particles
"""
from __future__ import annotations

import pygame
from typing import Tuple

# ------------------------------------------------------------------
# Color palette
# ------------------------------------------------------------------

BG_DARK:       Tuple[int, int, int] = (13, 14, 20)
PANEL_BG:      Tuple[int, int, int] = (20, 22, 32)
PANEL_BORDER:  Tuple[int, int, int] = (48, 52, 75)
PANEL_HEADER:  Tuple[int, int, int] = (28, 32, 52)

# Cell / tile colors
COLOR_EMPTY:       Tuple[int, int, int] = (18, 20, 28)
COLOR_ROAD:        Tuple[int, int, int] = (75, 80, 95)
COLOR_BUILDING:    Tuple[int, int, int] = (55, 65, 85)      # generic (legacy)
COLOR_RESIDENTIAL: Tuple[int, int, int] = (60, 65, 78)      # dark gray
COLOR_OFFICE:      Tuple[int, int, int] = (68, 58, 102)     # slate/purple
COLOR_INDUSTRIAL:  Tuple[int, int, int] = (95, 62, 38)      # brown/orange
COLOR_STATION:     Tuple[int, int, int] = (35, 105, 175)    # blue
COLOR_PARK:        Tuple[int, int, int] = (38, 100, 55)     # green

# Road detail colors
COLOR_ROAD_MARKING: Tuple[int, int, int] = (95, 100, 118)

# Fire gradient (5 levels by intensity 0.0→1.0)
FIRE_COLORS = [
    (180,  30,   0),   # 0.0–0.2: deep red
    (220,  80,   0),   # 0.2–0.4: red-orange
    (255, 140,   0),   # 0.4–0.6: orange
    (255, 210,  50),   # 0.6–0.8: yellow-orange
    (255, 245, 160),   # 0.8–1.0: yellow-white (max)
]


def fire_color(intensity: float) -> Tuple[int, int, int]:
    """Smooth fire color interpolation based on intensity 0.0–1.0."""
    t = max(0.0, min(1.0, intensity)) * (len(FIRE_COLORS) - 1)
    i = int(t)
    f = t - i
    if i >= len(FIRE_COLORS) - 1:
        return FIRE_COLORS[-1]
    a = FIRE_COLORS[i]
    b = FIRE_COLORS[i + 1]
    return (
        int(a[0] + (b[0] - a[0]) * f),
        int(a[1] + (b[1] - a[1]) * f),
        int(a[2] + (b[2] - a[2]) * f),
    )


# Unit colors
TRUCK_IDLE:          Tuple[int, int, int] = ( 70, 175, 255)
TRUCK_EN_ROUTE:      Tuple[int, int, int] = (255, 195,  40)
TRUCK_EXTINGUISHING: Tuple[int, int, int] = ( 80, 245, 120)
TRUCK_RETURNING:     Tuple[int, int, int] = (190, 190, 255)

# Text — sized for 1920×1080 projector readability
TEXT_PRIMARY:   Tuple[int, int, int] = (225, 230, 245)
TEXT_SECONDARY: Tuple[int, int, int] = (155, 162, 180)
TEXT_DIM:       Tuple[int, int, int] = ( 95, 102, 125)

# Accents
ACCENT_BLUE:   Tuple[int, int, int] = ( 65, 125, 220)
ACCENT_ORANGE: Tuple[int, int, int] = (255, 140,   0)
ACCENT_RED:    Tuple[int, int, int] = (215,  55,  55)
ACCENT_GREEN:  Tuple[int, int, int] = ( 60, 190,  95)

# Severity
SEV_INFO:     Tuple[int, int, int] = ( 90, 175, 255)
SEV_WARNING:  Tuple[int, int, int] = (255, 185,  45)
SEV_CRITICAL: Tuple[int, int, int] = (255,  85,  85)

# Legend items: (label, color)
LEGEND_ITEMS = [
    ("Roads",        COLOR_ROAD),
    ("Residential",  COLOR_RESIDENTIAL),
    ("Office",       COLOR_OFFICE),
    ("Industrial",   COLOR_INDUSTRIAL),
    ("Park",         COLOR_PARK),
    ("Fire Station", COLOR_STATION),
    ("Fire (low)",   FIRE_COLORS[0]),
    ("Fire (high)",  FIRE_COLORS[4]),
    ("Smoke",        (80, 80, 110)),
]


# ------------------------------------------------------------------
# Font helpers  (pygame must already be initialised before calling)
# ------------------------------------------------------------------

def get_font(size: int) -> pygame.font.Font:
    """Return a pygame Font using the built-in bitmap font."""
    return pygame.font.Font(None, size)


def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: Tuple,
    x: int,
    y: int,
    anchor: str = "topleft",
) -> pygame.Rect:
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    setattr(rect, anchor, (x, y))
    surface.blit(surf, rect)
    return rect


# ------------------------------------------------------------------
# Panel drawing helpers
# ------------------------------------------------------------------

def draw_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    bg: Tuple = PANEL_BG,
    border: Tuple = PANEL_BORDER,
    radius: int = 6,
) -> None:
    pygame.draw.rect(surface, bg, rect, border_radius=radius)
    pygame.draw.rect(surface, border, rect, 1, border_radius=radius)


def draw_panel_header(
    surface: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font: pygame.font.Font,
    bg: Tuple = PANEL_HEADER,
) -> None:
    header = pygame.Rect(rect.x, rect.y, rect.width, 30)
    pygame.draw.rect(surface, bg, header, border_radius=6)
    pygame.draw.rect(surface, PANEL_BORDER, header, 1, border_radius=6)
    draw_text(surface, text, font, TEXT_SECONDARY, rect.x + 10, rect.y + 7)
