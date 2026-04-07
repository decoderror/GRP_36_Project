# Disaster Response Simulator

A real-time, interactive disaster response simulator that models **urban fire incidents**, **emergency vehicle dispatch**, and **weather effects** with particle animations.

This folder (`task1_oop_application/src`) is the **final delivery codebase** for Task 1.
## 🎥 Task 1 Video

[![Task 1 Video](https://img.shields.io/badge/Video-Task%201-brightgreen?style=for-the-badge)](https://github.com/decoderror/GRP_36_Project/blob/1586fa701d4f55747269bbabead950abf0ed3273/TASK_1/task1_video.mp4)

> Click the button above！！！If GitHub cannot play the video directly, click **“View raw”** on GitHub to download or play it.

## Key Features

- **City map** with roads, buildings, parks, and fire stations
- **Fire simulation** with spreading, intensity growth, and extinguishing
- **Emergency dispatch** using A* pathfinding on the road network
- **Weather system** with visual particle effects:
  - Rain: animated blue droplets
  - Snow: drifting snowflakes
  - Wind: fast horizontal streaks
  - Sun: clear (no particles)
- **Interactive controls** via sidebar buttons and keyboard shortcuts
- **Modern UI** with stylish panels, legend overlay, adaptive pop-up feedback
- **Live statistics**: active fires, deployed units, mini fire chart
- **Event log**: color-coded real-time event feed

---

## Requirements

- Python **3.12+**
- Dependencies (see `requirements.txt`):
  - `pygame` — rendering engine
  - `pygame.freetype` — modern font rendering (included with recent pygame)
  - *(If your project uses it:)* `pygame_gui` — optional modern UI widgets

---

## How to Run

From the **repository root**:

```bash
pip install -r requirements.txt
python -m task1_oop_application.src.main
```

---

## Controls

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

---

## Architecture

### 1) Core Layer (`core/`)
- `world.py`, `entities.py`, `simulation.py`, `events.py`, `pathfinding.py`

### 2) Render Layer (`render/`)
- `renderer.py`, `camera.py`, `theme.py`, `particles.py`

### 3) UI Layer (`ui/`)
- `panels.py` (includes all modern overlays, popups, legend, etc.)

### 4) Entry Point (`main.py`)
- Runs the main loop and wires all layers

### 5) Models & Visualization
- `models/model_base.py`, `visualization/gui_manager.py`: For extensions or modular architecture

---

## Project Structure

```text
task1_oop_application/
  src/
    __init__.py
    main.py
    core/
      __init__.py
      world.py
      entities.py
      simulation.py
      events.py
      pathfinding.py
    render/
      __init__.py
      renderer.py
      camera.py
      theme.py
      particles.py
    ui/
      __init__.py
      panels.py
    models/
      __init__.py
      model_base.py
    visualization/
      gui_manager.py
```

---

## Notes
- UI uses modern styles (rounded panels, gradients, overlays, live popups).
- See source code for integration details and extensibility.
```

