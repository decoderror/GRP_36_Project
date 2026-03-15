# Disaster Response Simulator (Final Delivery)

A real-time, interactive disaster response simulator that models **urban fire incidents**, **emergency vehicle dispatch**, and **weather effects** with particle animations.

This folder (`task1_oop_application/src`) is the **final delivery codebase** for Task 1.

---

## Key Features

- **City map** with English-named roads, buildings, parks, and fire stations
- **Fire simulation** with spreading, intensity growth, and extinguishing
- **Emergency dispatch** using A* pathfinding on the road network
- **Weather system** with visual particle effects:
  - Rain: animated blue droplets falling diagonally
  - Snow: drifting white snowflakes with gentle sway
  - Wind: fast horizontal dust streaks
  - Sun: clear (no particles)
- **Interactive controls** via sidebar buttons and keyboard shortcuts
- **Live statistics**: active fires, deployed units, mini fire chart
- **Event log**: color-coded real-time event feed

---

## Requirements

- Python **3.12+**
- Dependencies (see `requirements.txt` at repository root):
  - `pygame` — rendering engine
  - `pygame_gui` — optional modern UI widgets

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

## Architecture (4 Layers)

### 1) Core Layer (`core/`)
Domain logic using Object-Oriented Design:
- `world.py` — City grid with cells, road names, and terrain types
- `entities.py` — FireStation and FireTruck with state-machine logic
- `simulation.py` — Main simulation orchestrator (fire, dispatch, weather)
- `events.py` — Typed event system with severity levels
- `pathfinding.py` — A* shortest path on the road graph

### 2) Render Layer (`render/`)
Visualization-only components:
- `renderer.py` — Draws world, fires, trucks, road names, and particles
- `camera.py` — Viewport pan and zoom management
- `theme.py` — Color palette and font helpers
- `particles.py` — Weather particle effects (rain, snow, wind)

### 3) UI Layer (`ui/`)
User interface panels:
- `panels.py` — TopBar, LeftPanel, RightPanel, BottomPanel, overlays

### 4) Entry Point (`main.py`)
Wires all layers together and runs the main game loop.

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

