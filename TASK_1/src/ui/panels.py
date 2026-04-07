from __future__ import annotations
import os
from typing import List, Optional, Tuple

import pygame
import pygame.freetype

from task1_oop_application.src.core.simulation import Simulation
from task1_oop_application.src.core.entities import TruckState
from task1_oop_application.src.core.events import Severity, SimEvent
from task1_oop_application.src.render import theme

SPEEDS = [("1x", 1.0), ("2x", 2.0), ("4x", 4.0), ("8x", 8.0)]
WEATHERS = ["sun", "rain", "wind", "snow"]
WEATHER_LABELS = {"sun": "Sun", "rain": "Rain", "wind": "Wind", "snow": "Snow"}

HOVER_BRIGHTNESS_DELTA = 25

class Button:
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
        self._font = theme.get_font(19)

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

class TopBar:
    HEIGHT = 40

    def __init__(self, window_width: int) -> None:
        self.rect = pygame.Rect(0, 0, window_width, self.HEIGHT)
        self._f_title = theme.get_font(22)
        self._f_info  = theme.get_font(18)

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
        theme.draw_text(surface, "DISASTER RESPONSE SIMULATOR",
                        self._f_title, theme.ACCENT_BLUE, 12, 10)
        mm, ss = int(sim_time // 60), int(sim_time % 60)
        theme.draw_text(surface, f"T+{mm:02d}:{ss:02d}",
                        self._f_info, theme.TEXT_PRIMARY, 395, 12)
        s_col = theme.ACCENT_GREEN if state == "running" else theme.TEXT_SECONDARY
        theme.draw_text(surface, f"[{state.upper()}]",
                        self._f_info, s_col, 470, 12)
        theme.draw_text(surface, WEATHER_LABELS.get(weather, weather),
                        self._f_info, theme.TEXT_SECONDARY, 580, 12)
        fps_col = (theme.ACCENT_GREEN if fps >= 50
                   else theme.SEV_WARNING if fps >= 30
                   else theme.SEV_CRITICAL)
        theme.draw_text(surface, f"FPS: {fps:.0f}",
                        self._f_info, fps_col, self.rect.right - 95, 12)

class LeftPanel:
    WIDTH = 220

    def __init__(self, window_height: int, top_h: int, bottom_h: int) -> None:
        y0 = top_h
        h  = window_height - top_h - bottom_h
        self.rect = pygame.Rect(0, y0, self.WIDTH, h)
        self._f_h  = theme.get_font(17)
        self._f    = theme.get_font(15)
        self._f_sm = theme.get_font(13)
        bx = self.rect.x + 8
        bw = 95
        bh = 30
        self.buttons: List[Button] = [
            Button(pygame.Rect(bx,        y0 + 33, bw, bh), "START",  "start",  theme.ACCENT_GREEN),
            Button(pygame.Rect(bx + bw + 8, y0 + 33, bw, bh), "PAUSE",  "pause",  (60, 80, 130)),
            Button(pygame.Rect(bx,        y0 + 70, bw, bh), "RESET",  "reset",  (90, 45, 45)),
            Button(pygame.Rect(bx + bw + 8, y0 + 70, bw, bh), "DEMO",   "demo",   theme.ACCENT_ORANGE),
        ]
        spd_bw = 44
        self.speed_buttons: List[Button] = [
            Button(
                pygame.Rect(bx + i * (spd_bw + 4), y0 + 130, spd_bw, 26),
                label, f"speed_{i}",
            )
            for i, (label, _) in enumerate(SPEEDS)
        ]
        wbw = 47
        self.weather_buttons: List[Button] = [
            Button(
                pygame.Rect(bx + i * (wbw + 3), y0 + 185, wbw, 26),
                w[:4].capitalize(), f"weather_{i}",
            )
            for i, w in enumerate(WEATHERS)
        ]
        self._all_btns = self.buttons + self.speed_buttons + self.weather_buttons

    def draw(self, surface: pygame.Surface, sim: Simulation, speed_idx: int) -> None:
        theme.draw_panel(surface, self.rect)
        theme.draw_panel_header(surface, self.rect, "CONTROLS", self._f_h)
        for btn in self.buttons:
            btn.draw(surface)
        y0 = self.rect.y
        theme.draw_text(surface, "SPEED", self._f_sm, theme.TEXT_DIM,
                        self.rect.x + 8, y0 + 116)
        for i, btn in enumerate(self.speed_buttons):
            btn.color = theme.ACCENT_BLUE if i == speed_idx else (40, 46, 68)
            btn.draw(surface)
        theme.draw_text(surface, "WEATHER", self._f_sm, theme.TEXT_DIM,
                        self.rect.x + 8, y0 + 171)
        for i, btn in enumerate(self.weather_buttons):
            btn.color = (70, 115, 175) if WEATHERS[i] == sim.weather else (40, 46, 68)
            btn.draw(surface)
        y = y0 + 222
        pygame.draw.line(surface, theme.PANEL_BORDER,
                         (self.rect.x + 6, y), (self.rect.right - 6, y))
        y += 6
        stats = [
            ("Sim Time",     f"{int(sim.sim_time // 60):02d}:{int(sim.sim_time % 60):02d}"),
            ("Active Fires", str(sim.get_active_fires())),
            ("Deployed",     str(sim.get_deployed_units())),
            ("Total Units",  str(len(sim.trucks))),
            ("Weather",      sim.weather.capitalize()),
        ]
        for label, value in stats:
            theme.draw_text(surface, label, self._f_sm, theme.TEXT_DIM,
                            self.rect.x + 8, y)
            val_color = (theme.SEV_CRITICAL
                         if label == "Active Fires" and sim.get_active_fires() > 0
                         else theme.TEXT_PRIMARY)
            theme.draw_text(surface, value, self._f_sm, val_color,
                            self.rect.x + 120, y)
            y += 20
        y = self.rect.bottom - 155
        pygame.draw.line(surface, theme.PANEL_BORDER,
                         (self.rect.x + 6, y), (self.rect.right - 6, y))
        y += 4
        hotkeys = [
            "F1  Toggle help",
            "F2  Toggle stats",
            "F3  Cycle speed",
            "F4  Cycle weather",
            "F9  Demo mode",
            "ESC  Quit",
            "",
            "LMB  Select / ignite",
            "RMB drag  Pan map",
            "Wheel  Zoom map",
        ]
        for hk in hotkeys:
            if hk:
                theme.draw_text(surface, hk, self._f_sm, theme.TEXT_DIM,
                                self.rect.x + 8, y)
            y += 14

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        for btn in self._all_btns:
            result = btn.handle_event(event)
            if result:
                return result
        return None

class RightPanel:
    WIDTH = 220
    def __init__(
        self,
        window_width: int,
        window_height: int,
        top_h: int,
        bottom_h: int,
    ) -> None:
        y0 = top_h
        h = window_height - top_h - bottom_h
        self.rect = pygame.Rect(window_width - self.WIDTH, y0, self.WIDTH, h)
        self._f_h  = theme.get_font(17)
        self._f    = theme.get_font(15)
        self._f_sm = theme.get_font(13)

    def draw(
        self,
        surface: pygame.Surface,
        sim: Simulation,
        selected_cell: Optional[Tuple[int, int]],
    ) -> None:
        theme.draw_panel(surface, self.rect)
        theme.draw_panel_header(surface, self.rect, "INSPECTOR", self._f_h)
        y = self.rect.y + 32
        if selected_cell:
            gx, gy = selected_cell
            cell = sim.world.get_cell(gx, gy)
            if cell:
                rows = [
                    ("Cell",      f"({gx}, {gy})"),
                    ("Type",      cell.type.name),
                    ("On Fire",   "YES" if cell.burning else "No"),
                ]
                if cell.burning:
                    rows += [
                        ("Intensity", f"{cell.fire_intensity:.2f}"),
                        ("Fire Time", f"{cell.fire_timer:.1f}s"),
                    ]
                for lbl, val in rows:
                    theme.draw_text(surface, lbl, self._f_sm, theme.TEXT_DIM,
                                    self.rect.x + 8, y)
                    vc = (theme.SEV_CRITICAL
                          if lbl == "On Fire" and val == "YES"
                          else theme.TEXT_PRIMARY)
                    theme.draw_text(surface, val, self._f_sm, vc,
                                    self.rect.x + 100, y)
                    y += 17
        else:
            theme.draw_text(surface, "Click map to select", self._f_sm,
                            theme.TEXT_DIM, self.rect.x + 8, y)
            y += 18
        y += 4
        pygame.draw.line(surface, theme.PANEL_BORDER,
                         (self.rect.x + 5, y), (self.rect.right - 5, y))
        y += 5
        theme.draw_text(surface, "UNITS", self._f_sm, theme.TEXT_SECONDARY,
                        self.rect.x + 8, y)
        y += 17
        _state_color = {
            TruckState.IDLE:          theme.TRUCK_IDLE,
            TruckState.EN_ROUTE:      theme.TRUCK_EN_ROUTE,
            TruckState.EXTINGUISHING: theme.TRUCK_EXTINGUISHING,
            TruckState.RETURNING:     theme.TRUCK_RETURNING,
        }
        chart_top = self.rect.bottom - 140
        for truck in sim.trucks:
            if y >= chart_top - 4:
                break
            col = _state_color.get(truck.state, theme.TEXT_PRIMARY)
            theme.draw_text(
                surface,
                f"T{truck.id}  {truck.state.value}",
                self._f_sm,
                col,
                self.rect.x + 8,
                y,
            )
            y += 15
        chart_margin = 8
        chart_h = 130
        chart_rect = pygame.Rect(
            self.rect.x + chart_margin,
            self.rect.bottom - chart_h - chart_margin,
            self.rect.width - 2 * chart_margin,
            chart_h,
        )
        self._draw_fire_chart(surface, sim, chart_rect)

    def _draw_fire_chart(
        self,
        surface: pygame.Surface,
        sim: Simulation,
        chart_rect: pygame.Rect,
    ) -> None:
        pygame.draw.rect(surface, (15, 18, 28), chart_rect, border_radius=3)
        pygame.draw.rect(surface, theme.PANEL_BORDER, chart_rect, 1, border_radius=3)
        theme.draw_text(surface, "Active Fires / Time", self._f_sm, theme.TEXT_SECONDARY,
                        chart_rect.x + 4, chart_rect.y + 3)
        data = sim.active_fires_history
        if not data:
            theme.draw_text(surface, "Waiting for data...", self._f_sm, theme.TEXT_DIM,
                            chart_rect.x + 4, chart_rect.centery - 6)
            return
        ca_x = chart_rect.x + 4
        ca_y = chart_rect.y + 18
        ca_w = chart_rect.width - 8
        ca_h = chart_rect.height - 24
        max_val = max(max(data), 1)
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
        theme.draw_text(surface, str(cur), self._f_sm, val_col,
                        chart_rect.right - 22, chart_rect.y + 3)

class BottomPanel:
    HEIGHT = 120

    def __init__(self, window_width: int, window_height: int) -> None:
        self.rect = pygame.Rect(0, window_height - self.HEIGHT, window_width, self.HEIGHT)
        self._f_h  = theme.get_font(16)
        self._f    = theme.get_font(14)

    def draw(self, surface: pygame.Surface, events: List[SimEvent]) -> None:
        theme.draw_panel(surface, self.rect)
        theme.draw_panel_header(surface, self.rect, "EVENT LOG", self._f_h)
        row_h = 16
        visible = (self.rect.height - 30) // row_h
        recent = events[-visible:] if len(events) > visible else events
        y = self.rect.y + 29
        for evt in recent:
            sev_col = {
                Severity.CRITICAL: theme.SEV_CRITICAL,
                Severity.WARNING:  theme.SEV_WARNING,
                Severity.INFO:     theme.SEV_INFO,
            }.get(evt.severity, theme.TEXT_SECONDARY)
            mm, ss = int(evt.sim_time // 60), int(evt.sim_time % 60)
            theme.draw_text(surface, f"[{mm:02d}:{ss:02d}]", self._f, theme.TEXT_DIM,
                            self.rect.x + 8, y)
            theme.draw_text(surface, f"[{evt.type.value}]", self._f, sev_col,
                            self.rect.x + 68, y)
            theme.draw_text(surface, evt.message, self._f, theme.TEXT_SECONDARY,
                            self.rect.x + 215, y)
            y += row_h

class HelpOverlay:
    def __init__(self, window_width: int, window_height: int) -> None:
        w, h = 500, 400
        self.rect = pygame.Rect((window_width - w) // 2, (window_height - h) // 2, w, h)
        self.visible = False
        self._f_h = theme.get_font(21)
        self._f   = theme.get_font(16)

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
        y = self.rect.y + 36
        entries = [
            ("F1",         "Toggle this help overlay"),
            ("F2",         "Toggle stats HUD"),
            ("F3",         "Cycle simulation speed"),
            ("F4",         "Cycle weather"),
            ("F9",         "Demo mode - auto scenario"),
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
                y += 5
                continue
            theme.draw_text(surface, key,  self._f, theme.ACCENT_BLUE,
                            self.rect.x + 16, y)
            theme.draw_text(surface, desc, self._f, theme.TEXT_PRIMARY,
                            self.rect.x + 145, y)
            y += 21

class StatsOverlay:
    def __init__(self, left: int, top: int) -> None:
        
        self.rect = pygame.Rect(left, top, 230, 110)
        self.visible = True
        self._f_h = theme.get_font(16)
        self._f   = theme.get_font(14)

    def toggle(self) -> None:
        self.visible = not self.visible

    def draw(self, surface: pygame.Surface, sim: Simulation, fps: float) -> None:
        if not self.visible:
            return
        theme.draw_panel(surface, self.rect, bg=(18, 20, 35))
        theme.draw_panel_header(surface, self.rect, "STATS", self._f_h)
        y = self.rect.y + 29
        rows = [
            ("FPS",          f"{fps:.0f}"),
            ("Sim Time",     f"{sim.sim_time:.1f}s"),
            ("Active Fires", str(sim.get_active_fires())),
            ("Deployed",     str(sim.get_deployed_units())),
        ]
        for lbl, val in rows:
            theme.draw_text(surface, f"{lbl}:", self._f, theme.TEXT_DIM,
                            self.rect.x + 8, y)
            theme.draw_text(surface, val, self._f, theme.TEXT_PRIMARY,
                            self.rect.x + 120, y)
            y += 19

# ---- Modern UI enhancements below ----


LEGEND_BG = (255, 255, 20, 220)  
FONT_COLOR = (20, 20, 20)        
ACCENT_ORANGE = (255, 120, 0)
ACCENT_RED = (255, 0, 0)
ACCENT_GREEN = (0, 255, 0)
ACCENT_BLUE = (0, 150, 255)
PANEL_RADIUS = 16
SHADOW_COLOR = (0, 0, 0, 86)
LEGEND_ENTRIES = [
    ("Building", (52, 74, 97)),
    ("Park", (35, 62, 43)),
    ("Street", (56, 70, 72)),
    ("Fire Station", (71, 170, 249)),
    ("Non-flammable", (29, 30, 37)),
]

def draw_shadowed_round_rect(screen, rect, color, shadow_color, radius, offset=(3, 3)):
    shadow_rect = rect.move(offset)
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    s_shadow = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(s_shadow, shadow_color, s_shadow.get_rect(), border_radius=radius)
    pygame.draw.rect(s, color, s.get_rect(), border_radius=radius)
    screen.blit(s_shadow, shadow_rect)
    screen.blit(s, rect)

class LegendPanel:
    WIDTH = 170
    HEIGHT = 42 + 38 * len(LEGEND_ENTRIES)
    FONT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "DejaVuSans.ttf"))
    def __init__(self, left: int, top: int, margin=0):
        self.rect = pygame.Rect(left, top, self.WIDTH, self.HEIGHT)
        self.font = pygame.freetype.Font(self.FONT_PATH, 17)

    def draw(self, screen):
        print(f"LegendPanel is being drawn at: {self.rect.x}, {self.rect.y}")
        draw_shadowed_round_rect(screen, self.rect, LEGEND_BG, SHADOW_COLOR, 14, (2, 2))
        title, _ = self.font.render("MAP LEGEND", (0, 0, 0))
        screen.blit(title, (self.rect.x + 18, self.rect.y + 12))
        y = self.rect.y + 38
        for label, color in LEGEND_ENTRIES:
            pygame.draw.rect(screen, color, (self.rect.x + 20, y + 4, 25, 25), border_radius=6)
            lab_surf, _ = self.font.render(label, FONT_COLOR)
            screen.blit(lab_surf, (self.rect.x + 54, y + 7))
            y += 34

class PopupNotifier:
    def __init__(self, win_w, win_h, font):
        self.text = ""
        self.visible = False
        self.alpha = 0
        self.timer = 0
        self.rect = pygame.Rect(0, 0, 410, 78)
        self.win_w = win_w
        self.win_h = win_h
        self.font = font
    def show(self, msg, color=ACCENT_RED, duration=2.2):
        self.text = msg
        self.visible = True
        self.alpha = 255
        self.timer = duration
        self.color = color
    def update(self, dt):
        if self.visible:
            self.timer -= dt
            if self.timer < 0:
                self.alpha -= 400 * dt
                if self.alpha < 0:
                    self.visible = False
                    self.alpha = 0
    def draw(self, screen):
        if not self.visible or self.alpha <= 0:
            return
        surf = pygame.Surface((410, 78), pygame.SRCALPHA)
        pygame.draw.rect(surf, SHADOW_COLOR, surf.get_rect(), border_radius=18)
        pygame.draw.rect(surf, self.color + (min(210, int(self.alpha)),), pygame.Rect(0, 0, 410, 78), border_radius=18)
        text_s, _ = self.font.render(self.text, FONT_COLOR)
        text_r = text_s.get_rect(center=(205, 39))
        surf.blit(text_s, text_r)
        surf.set_alpha(int(self.alpha))
        cx, cy = self.win_w // 2, self.win_h // 2
        screen.blit(surf, (cx - 205, cy - 39))