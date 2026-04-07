from __future__ import annotations

import traceback
import os

from typing import Optional

import pygame
import pygame.freetype

from task1_oop_application.src.core.simulation import Simulation
from task1_oop_application.src.core.world import CellType
from task1_oop_application.src.render.camera import Camera
from task1_oop_application.src.render.renderer import Renderer
from task1_oop_application.src.render import theme
from task1_oop_application.src.ui.panels import (
    TopBar, LeftPanel, RightPanel, BottomPanel,
    HelpOverlay, StatsOverlay,
    SPEEDS, WEATHERS, LegendPanel, PopupNotifier
)

WINDOW_W = 1280
WINDOW_H = 760

TOP_H    = TopBar.HEIGHT
BOTTOM_H = BottomPanel.HEIGHT
LEFT_W   = LeftPanel.WIDTH
RIGHT_W  = RightPanel.WIDTH

MAP_X = LEFT_W
MAP_Y = TOP_H
MAP_W = WINDOW_W - LEFT_W - RIGHT_W
MAP_H = WINDOW_H - TOP_H - BOTTOM_H

CELL_SIZE = 20
GRID_W = MAP_W // CELL_SIZE
GRID_H = MAP_H // CELL_SIZE

def main() -> int:
    pygame.init()
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    font_popup = pygame.freetype.Font(font_path, 27)
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Disaster Response Simulator")
    clock = pygame.time.Clock()
    sim = Simulation(world_width=GRID_W, world_height=GRID_H, seed=42)
    viewport = pygame.Rect(MAP_X, MAP_Y, MAP_W, MAP_H)
    camera   = Camera(viewport, cell_size=CELL_SIZE)
    camera.center_on(GRID_W, GRID_H)
    renderer = Renderer(screen, viewport, camera)

    top_bar      = TopBar(WINDOW_W)
    left_panel   = LeftPanel(WINDOW_H, TOP_H, BOTTOM_H)
    right_panel  = RightPanel(WINDOW_W, WINDOW_H, TOP_H, BOTTOM_H)
    bottom_panel = BottomPanel(WINDOW_W, WINDOW_H)
    help_overlay  = HelpOverlay(WINDOW_W, WINDOW_H)

    stats_overlay = StatsOverlay(MAP_X + MAP_W - 246, MAP_Y + MAP_H - 136)

    legend_panel = LegendPanel(MAP_X + MAP_W - 180, MAP_Y + 25)
    popup_notifier = PopupNotifier(WINDOW_W, WINDOW_H, font_popup)

    speed_idx  = 0
    right_drag = False

    running = True
    while running:
        dt  = clock.tick(60) / 1000.0
        fps = clock.get_fps()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F1:
                    help_overlay.toggle()
                elif event.key == pygame.K_F2:
                    stats_overlay.toggle()
                elif event.key == pygame.K_F3:
                    speed_idx = (speed_idx + 1) % len(SPEEDS)
                    sim.speed_mult = SPEEDS[speed_idx][1]
                elif event.key == pygame.K_F4:
                    wi = (WEATHERS.index(sim.weather) + 1) % len(WEATHERS)
                    sim.set_weather(WEATHERS[wi])
                elif event.key == pygame.K_F9:
                    if not sim.running:
                        sim.start()
                    sim.demo_mode()

            elif event.type == pygame.MOUSEWHEEL:
                camera.handle_mouse_wheel(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    if viewport.collidepoint(event.pos):
                        right_drag = True
                        camera.start_drag(event.pos)
                elif event.button == 1:
                    if viewport.collidepoint(event.pos):
                        gx, gy = camera.screen_to_grid(*event.pos)
                        cell = sim.world.get_cell(gx, gy)
                        if cell:
                            renderer.selected_cell = (gx, gy)
                            if cell.type == CellType.BUILDING and not cell.burning:
                                sim.start_fire(gx, gy)
                            elif cell.type != CellType.BUILDING:
                                popup_notifier.show("This tile cannot be ignited!", duration=2.2)
                    action = left_panel.handle_event(event)
                    if action:
                        if action.startswith("speed_"):
                            speed_idx = int(action.split("_")[1])
                            sim.speed_mult = SPEEDS[speed_idx][1]
                        else:
                            _handle_action(action, sim, camera, renderer, speed_idx)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    right_drag = False
                    camera.end_drag()

            elif event.type == pygame.MOUSEMOTION:
                if right_drag:
                    camera.update_drag(event.pos)
                left_panel.handle_event(event)

        sim.update(dt)
        popup_notifier.update(dt)

        screen.fill(theme.BG_DARK)
        renderer.draw(sim, dt)
        top_bar.draw(
            screen,
            sim.sim_time,
            "running" if sim.running else "paused",
            fps,
            sim.weather,
        )
        left_panel.draw(screen, sim, speed_idx)
        right_panel.draw(screen, sim, renderer.selected_cell)
        bottom_panel.draw(screen, sim.events)
        stats_overlay.draw(screen, sim, fps)
        help_overlay.draw(screen)
        legend_panel.draw(screen)
        popup_notifier.draw(screen)

        pygame.display.flip()

    pygame.quit()
    return 0

def _handle_action(
    action: Optional[str],
    sim: Simulation,
    camera: Camera,
    renderer: Renderer,
    speed_idx: int,
) -> None:
    if action is None:
        return
    if action == "start":
        sim.start()
    elif action == "pause":
        sim.pause()
    elif action == "reset":
        sim.reset()
        camera.center_on(sim.world_width, sim.world_height)
        renderer.selected_cell = None
    elif action == "demo":
        if not sim.running:
            sim.start()
        sim.demo_mode()
    elif action.startswith("weather_"):
        wi = int(action.split("_")[1])
        sim.set_weather(WEATHERS[wi])

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write("\n=== Crash ===\n")
            f.write(traceback.format_exc())
        raise