# -*- coding: utf-8 -*-
"""
Theme constants: colors, font helpers, and drawing utilities.

Uses only ``pygame.font.Font(None, size)`` (no SysFont) to avoid
Windows font-enumeration issues.
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
COLOR_EMPTY:    Tuple[int, int, int] = (22, 24, 34)
COLOR_ROAD:     Tuple[int, int, int] = (52, 56, 70)
COLOR_BUILDING: Tuple[int, int, int] = (42, 68, 95)
COLOR_STATION:  Tuple[int, int, int] = (55, 140, 70)
COLOR_PARK:     Tuple[int, int, int] = (35, 75, 48)

# Fire colors indexed by intensity quartile
FIRE_COLORS = [
    (160,  70,   0),   # low
    (215, 110,   0),   # medium
    (255, 165,   0),   # high
    (255,  50,   0),   # intense
]

# Unit colors
TRUCK_IDLE:          Tuple[int, int, int] = ( 70, 175, 255)
TRUCK_EN_ROUTE:      Tuple[int, int, int] = (255, 195,  40)
TRUCK_EXTINGUISHING: Tuple[int, int, int] = ( 80, 245, 120)
TRUCK_RETURNING:     Tuple[int, int, int] = (190, 190, 255)

# Text
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
    radius: int = 4,
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
    header = pygame.Rect(rect.x, rect.y, rect.width, 26)
    pygame.draw.rect(surface, bg, header, border_radius=4)
    pygame.draw.rect(surface, PANEL_BORDER, header, 1, border_radius=4)
    draw_text(surface, text, font, TEXT_SECONDARY, rect.x + 8, rect.y + 5)
