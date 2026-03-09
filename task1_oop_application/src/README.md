# GRP_36 Disaster Response Simulator (Final Delivery)

A real-time, interactive disaster response simulator that models **urban fire incidents**, **rescue dispatch**, and **environment effects**, with a modern visualization layer and smooth animation.

This folder (`task1_oop_application/src`) is the **final delivery codebase** for Task 1.
The legacy `Task 1/` directory in the repository is a **pre-submission archive** and is no longer the main entry point.

---

## Key Features

- **Modern visualization loop** (Pygame-based rendering)
- **Smooth animations** (interpolation instead of jump updates)
- **Responsive interaction**
  - ESC: in-app menu (pause / reset / exit)
  - F1: help panel (all shortcuts)
  - F2: live statistics panel (fires, vehicles, weather, sim speed, FPS)
  - F3: simulation speed toggle (1x / 2x / 4x / 8x)
  - F4: weather mode toggle (sun / rain / wind / snow)
  - Hover: building tooltip (ID, fire level, rescue status)
  - Click: manually trigger rescue dispatch (emergency intervention)
- **No garbled text policy**
  - UTF-8 source files
  - Fonts preloaded at startup (no runtime stutter / encoding crashes)
- **Stability-first**
  - Defensive error handling
  - Errors written to `log.txt` for debugging

---

## Requirements

- Python **3.12**
- Dependencies (installed via `requirements.txt` at repo root in the final package):
  - `pygame`
  - `pygame_gui` (used for modern UI widgets)

> Note: If `pygame_gui` is not available on the target machine, the UI layer can be replaced with pure Pygame widgets.
> This final delivery targets a modern, polished UI using `pygame_gui`.

---

## How to Run (Recommended)

From the **repository root**, run:

```bash
python -m task1_oop_application.src.main
```

Why module mode?
- It enforces a clean package structure
- Imports are consistent
- It matches a professional Python project layout

---

## Controls

| Key / Action | Function |
|---|---|
| ESC | Open main menu (start/pause/reset/exit/settings) |
| F1 | Help panel (shortcuts + usage) |
| F2 | Live statistics (fire count, vehicles, weather, speed, FPS) |
| F3 | Toggle simulation speed (1x / 2x / 4x / 8x) |
| F4 | Toggle weather mode (sun / rain / wind / snow) |
| Mouse hover | Tooltip for the building under cursor |
| Mouse click | Emergency intervention: request rescue dispatch to selected building |

---

## Architecture Overview (High-Level)

This project is intentionally organized as a layered architecture:

### 1) Simulation / Domain Layer (OOP)
Models the world using Object-Oriented Design:
- City / map entities
- Buildings (flammable states, fire levels)
- Rescue vehicles / emergency units
- Weather system that affects the simulation (spread rate, visibility, etc.)

### 2) Visualization Layer (Rendering Only)
A renderer dedicated to drawing:
- Uses `surface.blit()` and scaling for crisp visuals
- Uses float-based intermediate coordinate calculations to avoid jitter
- Supports selective redraw (dirty rectangles) to improve FPS

### 3) UI Layer (Modern GUI)
A UI manager dedicated to:
- Buttons, panels, status bars
- Clear feedback (hover highlight, button press animation)
- Dynamic layout on window resize

### 4) Animation Layer
An animation controller responsible for:
- Interpolated movement (linear or easing)
- Independent animation tick rate
- Pause / resume / speed scaling

---

## UTF-8 / Font Policy (No Garbled Text)

To ensure consistent text rendering across machines:
- All `.py` files should begin with:

```python
# -*- coding: utf-8 -*-
```

- Fonts are **preloaded** once at startup, e.g.:

```python
font_title = pygame.font.SysFont("Arial", 24, bold=True)
font_small = pygame.font.SysFont("Arial", 16)
```

If Arial is not available, the application should fall back to another sans-serif font.

---

## Project Structure (Final Target)

```text
task1_oop_application/
  src/
    __init__.py
    main.py
    models/
    simulation/
    visualization/
      gui_manager.py
      renderer.py
      animation_controller.py
  tests/
```

---

## Notes for Reviewers

- `Task 1/` in this repository is a **pre-submission snapshot**.
- The final codebase is `task1_oop_application/src`.
- The recommended execution command is:

```bash
python -m task1_oop_application.src.main
```
