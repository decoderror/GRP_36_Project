# -*- coding: utf-8 -*-
from __future__ import annotations

import traceback
import pygame

from task1_oop_application.src.visualization.gui_manager import GUIManager


def main() -> int:
    pygame.init()

    window_size = (1100, 720)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Disaster Response Simulator (GUI)")
    clock = pygame.time.Clock()

    gui = GUIManager(window_size)

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        fps = clock.get_fps()

        for event in pygame.event.get():
            if gui.process_event(event):
                running = False

        gui.update(time_delta=time_delta, fps=fps)

        # Background
        screen.fill((18, 18, 22))

        # Simulation area placeholder (right side)
        pygame.draw.rect(screen, (35, 35, 42), pygame.Rect(400, 20, 680, 680))
        pygame.draw.rect(screen, (90, 90, 110), pygame.Rect(400, 20, 680, 680), 2)

        gui.draw(screen)
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        # Write crash log for debugging on other machines
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write("\n=== Crash ===\n")
            f.write(traceback.format_exc())
        raise
