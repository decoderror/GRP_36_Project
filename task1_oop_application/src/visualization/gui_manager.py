# -*- coding: utf-8 -*-
from __future__ import annotations

import pygame
import pygame_gui


class GUIManager:
    """
    pygame_gui UI layer.

    Hotkeys:
      - F1: Toggle Help
      - F2: Toggle Stats
      - F3: Toggle Speed (1x/2x/4x/8x)
      - F4: Toggle Weather (sun/rain/wind/snow)
      - ESC: Quit
    """

    def __init__(self, window_size: tuple[int, int]):
        self.window_size = window_size
        self.ui = pygame_gui.UIManager(window_size)

        # State exposed to main loop
        self.sim_running: bool = False
        self.speed_idx: int = 0
        self.speeds = ["1x", "2x", "4x", "8x"]
        self.weather_idx: int = 0
        self.weathers = ["sun", "rain", "wind", "snow"]

        self.help_visible = False
        self.stats_visible = True

        self._build_ui()

    def _build_ui(self) -> None:
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((20, 20), (360, 260)),
            starting_layer_height=1,
            manager=self.ui,
        )

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (340, 30)),
            text="Disaster Response Simulator",
            manager=self.ui,
            container=self.panel,
        )

        self.btn_start = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 50), (160, 40)),
            text="Start",
            manager=self.ui,
            container=self.panel,
        )
        self.btn_pause = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((190, 50), (160, 40)),
            text="Pause",
            manager=self.ui,
            container=self.panel,
        )
        self.btn_reset = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 100), (160, 40)),
            text="Reset",
            manager=self.ui,
            container=self.panel,
        )
        self.btn_quit = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((190, 100), (160, 40)),
            text="Quit",
            manager=self.ui,
            container=self.panel,
        )

        self.status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 160), (340, 30)),
            text="Status: paused | Speed: 1x | Weather: sun",
            manager=self.ui,
            container=self.panel,
        )
        self.hint_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 200), (340, 50)),
            text="F1 Help | F2 Stats | F3 Speed | F4 Weather | ESC Quit",
            manager=self.ui,
            container=self.panel,
        )

        # Help panel
        self.help_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((20, 300), (360, 220)),
            starting_layer_height=1,
            manager=self.ui,
            visible=self.help_visible,
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (340, 30)),
            text="Help",
            manager=self.ui,
            container=self.help_panel,
        )
        pygame_gui.elements.UITextBox(
            html_text=(
                "<b>Hotkeys</b><br>"
                "F1: Toggle Help<br>"
                "F2: Toggle Stats<br>"
                "F3: Toggle Speed<br>"
                "F4: Toggle Weather<br>"
                "ESC: Quit<br><br>"
                "<b>Buttons</b><br>"
                "Start / Pause / Reset / Quit"
            ),
            relative_rect=pygame.Rect((10, 50), (340, 160)),
            manager=self.ui,
            container=self.help_panel,
        )

        # Stats panel
        self.stats_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((20, 540), (360, 140)),
            starting_layer_height=1,
            manager=self.ui,
            visible=self.stats_visible,
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (340, 30)),
            text="Stats",
            manager=self.ui,
            container=self.stats_panel,
        )
        self.stats_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 50), (340, 80)),
            text="FPS: -- | State: paused",
            manager=self.ui,
            container=self.stats_panel,
        )

    def process_event(self, event: pygame.event.Event) -> bool:
        """Return True if the app should quit."""
        if event.type == pygame.QUIT:
            return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True
            if event.key == pygame.K_F1:
                self.help_visible = not self.help_visible
                self.help_panel.show() if self.help_visible else self.help_panel.hide()
            elif event.key == pygame.K_F2:
                self.stats_visible = not self.stats_visible
                self.stats_panel.show() if self.stats_visible else self.stats_panel.hide()
            elif event.key == pygame.K_F3:
                self.speed_idx = (self.speed_idx + 1) % len(self.speeds)
            elif event.key == pygame.K_F4:
                self.weather_idx = (self.weather_idx + 1) % len(self.weathers)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_start:
                self.sim_running = True
            elif event.ui_element == self.btn_pause:
                self.sim_running = False
            elif event.ui_element == self.btn_reset:
                self.sim_running = False
                self.speed_idx = 0
                self.weather_idx = 0
            elif event.ui_element == self.btn_quit:
                return True

        self.ui.process_events(event)
        return False

    def update(self, time_delta: float, fps: float) -> None:
        self.ui.update(time_delta)

        state = "running" if self.sim_running else "paused"
        self.status_label.set_text(
            f"Status: {state} | Speed: {self.speeds[self.speed_idx]} | Weather: {self.weathers[self.weather_idx]}"
        )
        if self.stats_visible:
            self.stats_label.set_text(f"FPS: {fps:.1f} | State: {state}")

    def draw(self, screen: pygame.Surface) -> None:
        self.ui.draw_ui(screen)
