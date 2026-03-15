# GRP 36 Project

This repository contains the coursework for Group 36.
It includes **Task 1** (Disaster Response Simulator) and **Task 2** (Heap Sort) in separate folders.

## Repository Structure

- `task1_oop_application/` — Disaster Response Simulator (Python, OOP-based, Pygame GUI)
- `Task 2/` — Max Heap (Data Structure) + Heap Sort (Algorithm) (Python implementation)

## Task 1 — Disaster Response Simulator

- Location: `task1_oop_application/src/`
- Entry point: `task1_oop_application/src/main.py`

### Features

- Real-time urban fire simulation with spreading mechanics
- Emergency vehicle dispatch with A* pathfinding
- Weather system (sun, rain, wind, snow) with **particle effects**
- English road name labels on the city map
- Interactive controls: start/pause/reset, speed adjustment, weather toggle
- Live statistics, event log, and mini fire chart
- Help overlay (F1) and stats HUD (F2)

### How to Run

From the repository root:

```bash
pip install -r requirements.txt
python -m task1_oop_application.src.main
```

### Controls

| Key / Action   | Function                              |
|----------------|---------------------------------------|
| ESC            | Quit                                  |
| F1             | Toggle help overlay                   |
| F2             | Toggle stats HUD                      |
| F3             | Cycle simulation speed (1x/2x/4x/8x) |
| F4             | Cycle weather (sun/rain/wind/snow)    |
| F9             | Demo mode (auto-start fires)          |
| Left Click     | Select cell / ignite building         |
| Right Drag     | Pan the map                           |
| Mouse Wheel    | Zoom in / out                         |

## Task 2 — Heap + Heap Sort

- Location: `Task 2/`
- Code: `Task 2/heap_sort.py`

### How to Run

```bash
python "Task 2/heap_sort.py"
```

## Dependencies

See `requirements.txt` for the full list. Key dependencies:

- `pygame` — game engine for rendering and input
- `pygame_gui` — modern UI widget toolkit (optional)

## Notes

- All source code and UI text is in **English**.
- The OOP architecture follows a 4-layer design: core, render, ui, and main entry point.
- Weather particle effects are visible when weather is set to rain, snow, or wind.
