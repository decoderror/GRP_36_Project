# -*- coding: utf-8 -*-
"""
UI layer: all panels rendered with pure pygame (no pygame_gui).

Panels:
  TopBar       — title, sim-time, state, FPS, weather
  LeftPanel    — simulation controls (start/pause/reset/demo), speed, weather,
                 live stats, legend, hotkey hints
  RightPanel   — selected-cell inspector + unit list + mini line-chart
  BottomPanel  — color-coded event log
  HelpOverlay  — modal help overlay (F1)
  StatsOverlay — small stats HUD (F2)

Layout targets 1920x1080.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import pygame

from task1_oop_application.src.core.simulation import Simulation
from task1_oop_application.src.core.entities import TruckState
from task1_oop_application.src.core.events import Severity, SimEvent
from task1_oop_application.src.render import theme


# Speed presets: (label, multiplier)
SPEEDS = [("1x", 1.0), ("2x", 2.0), ("4x", 4.0), ("8x", 8.0)]

# Weather cycle
WEATHERS = ["sun", "rain", "wind", "snow"]

# Weather display labels
WEATHER_LABELS = {"sun": "Sun", "rain": "Rain", "wind": "Wind", "snow": "Snow"}
WEATHER_ICONS  = {"sun": "☀", "rain": "☂", "wind": "~", "snow": "*"}


# ======================================================================
# Helper: Button
# ======================================================================

HOVER_BRIGHTNESS_DELTA = 25


class Button:
    """A simple clickable button drawn with pygame primitives."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        action: str,
        color: Tuple = theme.ACCENT_BLUE,
        text_color: Tuple = theme.TEXT_PRIMARY,
    ) -> None:
        self.rect = rect
        self.text = text
        self.action = action
        self.color = color
        self.text_color = text_color
        self.hovered = False
        self._font = theme.get_font(24)

    def draw(self, surface: pygame.Surface) -> None:
        col = tuple(min(255, c + HOVER_BRIGHTNESS_DELTA) for c in self.color) if self.hovered else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=4)
        pygame.draw.rect(surface, theme.PANEL_BORDER, self.rect, 1, border_radius=4)
        surf = self._font.render(self.text, True, self.text_color)
        surface.blit(surf, surf.get_rect(center=self.rect.center))

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return self.action
        return None


# ======================================================================
# Top bar
# ======================================================================

class TopBar:
    """Thin strip at the very top: title | sim-time | state | weather | FPS."""

    HEIGHT = 56

    def __init__(self, window_width: int) -> None:
        self.rect = pygame.Rect(0, 0, window_width, self.HEIGHT)
        self._f_title = theme.get_font(30)
        self._f_info  = theme.get_font(24)

    def draw(
        self,
        surface: pygame.Surface,
        sim_time: float,
        state: str,
        fps: float,
        weather: str,
    ) -> None:
        pygame.draw.rect(surface, theme.PANEL_HEADER, self.rect)
        pygame.draw.rect(surface, theme.PANEL_BORDER, self.rect, 1)

        # Title
        theme.draw_text(surface, "DISASTER RESPONSE SIMULATOR",
                        self._f_title, theme.ACCENT_BLUE, 14, 12)

        # Sim time
        mm, ss = int(sim_time // 60), int(sim_time % 60)
        theme.draw_text(surface, f"T+{mm:02d}:{ss:02d}",
                        self._f_info, theme.TEXT_PRIMARY, 520, 16)

        # State
        s_col = theme.ACCENT_GREEN if state == "running" else theme.TEXT_SECONDARY
        theme.draw_text(surface, f"[{state.upper()}]",
                        self._f_info, s_col, 630, 16)

        # Weather
        wlabel = WEATHER_ICONS.get(weather, "") + " " + WEATHER_LABELS.get(weather, weather)
        theme.draw_text(surface, wlabel,
                        self._f_info, theme.TEXT_SECONDARY, 790, 16)

        # FPS
        fps_col = (theme.ACCENT_GREEN if fps >= 50
                   else theme.SEV_WARNING if fps >= 30
                   else theme.SEV_CRITICAL)
        theme.draw_text(surface, f"FPS: {fps:.0f}",
                        self._f_info, fps_col, self.rect.right - 130, 16)


# ======================================================================
# Left panel — controls
# ======================================================================

class LeftPanel:
    """Left sidebar with simulation controls, speed/weather selectors, stats, and legend."""

    WIDTH = 300

    def __init__(self, window_height: int, top_h: int, bottom_h: int) -> None:
        y0 = top_h
        h  = window_height - top_h - bottom_h
        self.rect = pygame.Rect(0, y0, self.WIDTH, h)

        self._f_h  = theme.get_font(23)
        self._f    = theme.get_font(21)
        self._f_sm = theme.get_font(19)
        self._f_xs = theme.get_font(17)

        bx = self.rect.x + 10
        bw = 128
        bh = 38

        # Main control buttons (2x2 grid)
        self.buttons: List[Button] = [
            Button(pygame.Rect(bx,          y0 + 38,  bw, bh), "START", "start", theme.ACCENT_GREEN),
            Button(pygame.Rect(bx + bw + 8, y0 + 38,  bw, bh), "PAUSE", "pause", (60, 80, 130)),
            Button(pygame.Rect(bx,          y0 + 82,  bw, bh), "RESET", "reset", (90, 45, 45)),
            Button(pygame.Rect(bx + bw + 8, y0 + 82,  bw, bh), "DEMO",  "demo",  theme.ACCENT_ORANGE),
        ]

        # Speed toggle buttons
        spd_bw = 60
        self.speed_buttons: List[Button] = [
            Button(
                pygame.Rect(bx + i * (spd_bw + 5), y0 + 148, spd_bw, 30),
                label, f"speed_{i}",
            )
            for i, (label, _) in enumerate(SPEEDS)
        ]

        # Weather toggle buttons
        wbw = 63
        self.weather_buttons: List[Button] = [
            Button(
                pygame.Rect(bx + i * (wbw + 4), y0 + 208, wbw, 30),
                w[:4].capitalize(), f"weather_{i}",
            )
            for i, w in enumerate(WEATHERS)
        ]

        self._all_btns = self.buttons + self.speed_buttons + self.weather_buttons

    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface, sim: Simulation, speed_idx: int) -> None:
        theme.draw_panel(surface, self.rect)
        theme.draw_panel_header(surface, self.rect, "CONTROLS", self._f_h)

        for btn in self.buttons:
            btn.draw(surface)

        y0 = self.rect.y

        # Speed section
        theme.draw_text(surface, "SPEED", self._f_xs, theme.TEXT_DIM,
                        self.rect.x + 10, y0 + 134)
        for i, btn in enumerate(self.speed_buttons):
            btn.color = theme.ACCENT_BLUE if i == speed_idx else (40, 46, 68)
            btn.draw(surface)

        # Weather section
        theme.draw_text(surface, "WEATHER", self._f_xs, theme.TEXT_DIM,
                        self.rect.x + 10, y0 + 194)
        for i, btn in enumerate(self.weather_buttons):
            btn.color = (70, 115, 175) if WEATHERS[i] == sim.weather else (40, 46, 68)
            btn.draw(surface)

        # ── Live stats ──────────────────────────────────────────────
        y = y0 + 252
        pygame.draw.line(surface, theme.PANEL_BORDER,
                         (self.rect.x + 6, y), (self.rect.right - 6, y))
        y += 8
        stats = [
            ("Sim Time",     f"{int(sim.sim_time // 60):02d}:{int(sim.sim_time % 60):02d}"),
            ("Active Fires", str(sim.get_active_fires())),
            ("Deployed",     str(sim.get_deployed_units())),
            ("Total Units",  str(len(sim.trucks))),
            ("Weather",      sim.weather.capitalize()),
            ("Wind Angle",   f"{sim.wind_angle:.0f}°"),
        ]
        for label, value in stats:
            theme.draw_text(surface, label, self._f_xs, theme.TEXT_DIM,
                            self.rect.x + 10, y)
            val_color = (theme.SEV_CRITICAL
                         if label == "Active Fires" and sim.get_active_fires() > 0
                         else theme.TEXT_PRIMARY)
            theme.draw_text(surface, value, self._f_xs, val_color,
                            self.rect.x + 160, y)
            y += 24

        # ── Legend ──────────────────────────────────────────────────
        y += 4
        pygame.draw.line(surface, theme.PANEL_BORDER,
                         (self.rect.x + 6, y), (self.rect.right - 6, y))
        y += 8
        theme.draw_text(surface, "LEGEND", self._f_xs, theme.TEXT_SECONDARY,
                        self.rect.x + 10, y)
        y += 22
        swatch_size = 14
        for label, color in theme.LEGEND_ITEMS:
            if y + swatch_size + 2 > self.rect.bottom - 5:
                break
            pygame.draw.rect(surface, color,
                             pygame.Rect(self.rect.x + 10, y, swatch_size, swatch_size),
                             border_radius=2)
            pygame.draw.rect(surface, theme.PANEL_BORDER,
                             pygame.Rect(self.rect.x + 10, y, swatch_size, swatch_size), 1,
                             border_radius=2)
            theme.draw_text(surface, label, self._f_xs, theme.TEXT_DIM,
                            self.rect.x + 30, y)
            y += 20

        # ── Hotkeys (only if space remains) ─────────────────────────
        hotkey_y = self.rect.bottom - 170
        if y < hotkey_y:
            pygame.draw.line(surface, theme.PANEL_BORDER,
                             (self.rect.x + 6, hotkey_y), (self.rect.right - 6, hotkey_y))
            hy = hotkey_y + 6
            hotkeys = [
                "F1  Toggle help",
                "F2  Toggle stats",
                "F3  Cycle speed",
                "F4  Cycle weather",
                "F9  Demo mode",
                "ESC  Quit",
                "LMB  Select / ignite",
                "RMB drag  Pan map",
                "Wheel  Zoom map",
            ]
            for hk in hotkeys:
                if hy + 18 > self.rect.bottom - 4:
                    break
                theme.draw_text(surface, hk, self._f_xs, theme.TEXT_DIM,
                                self.rect.x + 10, hy)
                hy += 18

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        for btn in self._all_btns:
            result = btn.handle_event(event)
            if result:
                return result
        return None


# ======================================================================
# Right panel — inspector + chart
# ======================================================================

class RightPanel:
    """
    Right sidebar:
      - Selected cell/entity inspector
      - Unit status list
      - Mini line chart of active fires over time
    """

    WIDTH = 340

    def __init__(
        self,
        window_width: int,
        window_height: int,
        top_h: int,
        bottom_h: int,
    ) -> None:
        y0 = top_h
        h  = window_height - top_h - bottom_h
        self.rect = pygame.Rect(window_width - self.WIDTH, y0, self.WIDTH, h)

        self._f_h  = theme.get_font(23)
        self._f    = theme.get_font(21)
        self._f_sm = theme.get_font(19)
        self._f_xs = theme.get_font(17)

    # ------------------------------------------------------------------

    def draw(
        self,
        surface: pygame.Surface,
        sim: Simulation,
        selected_cell: Optional[Tuple[int, int]],
    ) -> None:
        theme.draw_panel(surface, self.rect)
        theme.draw_panel_header(surface, self.rect, "INSPECTOR", self._f_h)

        y = self.rect.y + 36

        # --- Selected cell info ---
        if selected_cell:
            gx, gy = selected_cell
            cell = sim.world.get_cell(gx, gy)
            if cell:
                rows = [
                    ("Cell",       f"({gx}, {gy})"),
                    ("Type",       cell.type.name),
                    ("On Fire",    "YES" if cell.burning else "No"),
                ]
                if cell.burning:
                    rows += [
                        ("Intensity", f"{cell.fire_intensity:.2f}"),
                        ("Fire Time", f"{cell.fire_timer:.1f}s"),
                    ]
                for lbl, val in rows:
                    theme.draw_text(surface, lbl, self._f_xs, theme.TEXT_DIM,
                                    self.rect.x + 10, y)
                    vc = (theme.SEV_CRITICAL
                          if lbl == "On Fire" and val == "YES"
                          else theme.TEXT_PRIMARY)
                    theme.draw_text(surface, val, self._f_xs, vc,
                                    self.rect.x + 130, y)
                    y += 22
        else:
            theme.draw_text(surface, "Click map to select", self._f_xs,
                            theme.TEXT_DIM, self.rect.x + 10, y)
            y += 24

        y += 6
        pygame.draw.line(surface, theme.PANEL_BORDER,
                         (self.rect.x + 5, y), (self.rect.right - 5, y))
        y += 8

        # --- Unit status list ---
        theme.draw_text(surface, "UNITS", self._f_xs, theme.TEXT_SECONDARY,
                        self.rect.x + 10, y)
        y += 22

        _state_color = {
            TruckState.IDLE:          theme.TRUCK_IDLE,
            TruckState.EN_ROUTE:      theme.TRUCK_EN_ROUTE,
            TruckState.EXTINGUISHING: theme.TRUCK_EXTINGUISHING,
            TruckState.RETURNING:     theme.TRUCK_RETURNING,
        }
        chart_top = self.rect.bottom - 180
        for truck in sim.trucks:
            if y >= chart_top - 6:
                break
            col = _state_color.get(truck.state, theme.TEXT_PRIMARY)
            theme.draw_text(
                surface,
                f"T{truck.id}  {truck.state.value}",
                self._f_xs,
                col,
                self.rect.x + 10,
                y,
            )
            y += 20

        # --- Mini chart: active fires over time ---
        chart_margin = 10
        chart_h = 165
        chart_rect = pygame.Rect(
            self.rect.x + chart_margin,
            self.rect.bottom - chart_h - chart_margin,
            self.rect.width - 2 * chart_margin,
            chart_h,
        )
        self._draw_fire_chart(surface, sim, chart_rect)

    # ------------------------------------------------------------------

    def _draw_fire_chart(
        self,
        surface: pygame.Surface,
        sim: Simulation,
        chart_rect: pygame.Rect,
    ) -> None:
        """Mini line chart showing active-fire count over the last 60 seconds."""
        pygame.draw.rect(surface, (15, 18, 28), chart_rect, border_radius=3)
        pygame.draw.rect(surface, theme.PANEL_BORDER, chart_rect, 1, border_radius=3)

        theme.draw_text(surface, "Active Fires / Time", self._f_xs, theme.TEXT_SECONDARY,
                        chart_rect.x + 6, chart_rect.y + 5)

        data = sim.active_fires_history
        if not data:
            theme.draw_text(surface, "Waiting for data...", self._f_xs, theme.TEXT_DIM,
                            chart_rect.x + 6, chart_rect.centery - 8)
            return

        ca_x = chart_rect.x + 6
        ca_y = chart_rect.y + 24
        ca_w = chart_rect.width - 12
        ca_h = chart_rect.height - 32
        max_val = max(max(data), 1)

        # Faint horizontal grid lines
        for i in range(1, 3):
            gy2 = ca_y + int(ca_h * i / 2)
            pygame.draw.line(surface, (30, 36, 55), (ca_x, gy2), (ca_x + ca_w, gy2))

        n = len(data)
        points = [
            (
                ca_x + int(i / max(n - 1, 1) * ca_w),
                ca_y + ca_h - max(0, int(v / max_val * ca_h)),
            )
            for i, v in enumerate(data)
        ]

        if len(points) >= 2:
            fill_pts = [(ca_x, ca_y + ca_h)] + points + [(points[-1][0], ca_y + ca_h)]
            tmp = pygame.Surface((chart_rect.width, chart_rect.height), pygame.SRCALPHA)
            adj = [(p[0] - chart_rect.x, p[1] - chart_rect.y) for p in fill_pts]
            pygame.draw.polygon(tmp, (220, 80, 40, 55), adj)
            surface.blit(tmp, chart_rect.topleft)
            pygame.draw.lines(surface, theme.SEV_WARNING, False, points, 2)
        elif len(points) == 1:
            pygame.draw.circle(surface, theme.SEV_WARNING, points[0], 3)

        cur = data[-1]
        val_col = theme.SEV_CRITICAL if cur > 0 else theme.ACCENT_GREEN
        theme.draw_text(surface, str(cur), self._f_xs, val_col,
                        chart_rect.right - 28, chart_rect.y + 5)


# ======================================================================
# Bottom panel — event log
# ======================================================================

class BottomPanel:
    """Scrolling event log at the bottom of the window."""

    HEIGHT = 200

    def __init__(self, window_width: int, window_height: int) -> None:
        self.rect = pygame.Rect(0, window_height - self.HEIGHT, window_width, self.HEIGHT)
        self._f_h = theme.get_font(22)
        self._f   = theme.get_font(20)

    def draw(self, surface: pygame.Surface, events: List[SimEvent]) -> None:
        theme.draw_panel(surface, self.rect)
        theme.draw_panel_header(surface, self.rect, "EVENT LOG", self._f_h)

        row_h = 20
        visible = (self.rect.height - 34) // row_h
        recent = events[-visible:] if len(events) > visible else events

        y = self.rect.y + 34
        for evt in recent:
            sev_col = {
                Severity.CRITICAL: theme.SEV_CRITICAL,
                Severity.WARNING:  theme.SEV_WARNING,
                Severity.INFO:     theme.SEV_INFO,
            }.get(evt.severity, theme.TEXT_SECONDARY)

            mm, ss = int(evt.sim_time // 60), int(evt.sim_time % 60)
            theme.draw_text(surface, f"[{mm:02d}:{ss:02d}]", self._f, theme.TEXT_DIM,
                            self.rect.x + 10, y)
            theme.draw_text(surface, f"[{evt.type.value}]", self._f, sev_col,
                            self.rect.x + 88, y)
            theme.draw_text(surface, evt.message, self._f, theme.TEXT_SECONDARY,
                            self.rect.x + 280, y)
            y += row_h


# ======================================================================
# Help overlay  (F1)
# ======================================================================

class HelpOverlay:
    """Full-screen semi-transparent help modal."""

    def __init__(self, window_width: int, window_height: int) -> None:
        w, h = 580, 480
        self.rect = pygame.Rect((window_width - w) // 2, (window_height - h) // 2, w, h)
        self.visible = False
        self._f_h = theme.get_font(27)
        self._f   = theme.get_font(22)

    def toggle(self) -> None:
        self.visible = not self.visible

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        surface.blit(overlay, (0, 0))

        theme.draw_panel(surface, self.rect, bg=(26, 30, 50))
        theme.draw_panel_header(surface, self.rect, "HELP   (F1 to close)", self._f_h)

        y = self.rect.y + 40
        entries = [
            ("F1",         "Toggle this help overlay"),
            ("F2",         "Toggle stats HUD"),
            ("F3",         "Cycle simulation speed"),
            ("F4",         "Cycle weather"),
            ("F9",         "Demo mode – auto scenario"),
            ("ESC",        "Quit"),
            ("",           ""),
            ("Left Click", "Select cell  /  ignite building"),
            ("Right Drag", "Pan the map"),
            ("Wheel",      "Zoom in / out"),
            ("",           ""),
            ("START",      "Start / resume simulation"),
            ("PAUSE",      "Pause simulation"),
            ("RESET",      "Reset everything"),
            ("DEMO",       "Start demo scenario"),
        ]
        for key, desc in entries:
            if not key:
                y += 6
                continue
            theme.draw_text(surface, key,  self._f, theme.ACCENT_BLUE,
                            self.rect.x + 18, y)
            theme.draw_text(surface, desc, self._f, theme.TEXT_PRIMARY,
                            self.rect.x + 170, y)
            y += 26


# ======================================================================
# Stats overlay  (F2)
# ======================================================================

class StatsOverlay:
    """Small floating HUD with live stats."""

    def __init__(self, map_x: int, map_y: int) -> None:
        self.rect = pygame.Rect(map_x + 6, map_y + 6, 280, 130)
        self.visible = True
        self._f_h = theme.get_font(22)
        self._f   = theme.get_font(20)

    def toggle(self) -> None:
        self.visible = not self.visible

    def draw(self, surface: pygame.Surface, sim: Simulation, fps: float) -> None:
        if not self.visible:
            return

        theme.draw_panel(surface, self.rect, bg=(18, 20, 35))
        theme.draw_panel_header(surface, self.rect, "STATS", self._f_h)

        y = self.rect.y + 34
        rows = [
            ("FPS",          f"{fps:.0f}"),
            ("Sim Time",     f"{sim.sim_time:.1f}s"),
            ("Active Fires", str(sim.get_active_fires())),
            ("Deployed",     str(sim.get_deployed_units())),
        ]
        for lbl, val in rows:
            theme.draw_text(surface, f"{lbl}:", self._f, theme.TEXT_DIM,
                            self.rect.x + 10, y)
            theme.draw_text(surface, val, self._f, theme.TEXT_PRIMARY,
                            self.rect.x + 155, y)
            y += 22
