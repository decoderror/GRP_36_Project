# GRP 36 Project — Disaster Response Simulator

This repository contains **Task 1** and **Task 2** for Group 36.

---

## Task 1 — Disaster Response Simulator

A **showcase-ready strategy-simulation** built with Python + pygame.  
Features a polished dark-theme GUI, real fire-spread simulation, A\* pathfinding for fire trucks,
live charts, and a scripted demo mode.

### Screenshot

![Disaster Response Simulator](https://github.com/user-attachments/assets/6229409e-c686-46c4-bb3a-bea4b1d9ced2)

### How to run

```bash
# 1. Install dependencies (Python 3.11+)
python -m pip install -r requirements.txt

# 2. Launch
python -m task1_oop_application.src.main
```

### Controls

| Input | Action |
|---|---|
| **Left Click** on map | Select cell / ignite building |
| **Right Drag** | Pan the map |
| **Mouse Wheel** | Zoom in / out |
| **F1** | Toggle help overlay |
| **F2** | Toggle stats HUD |
| **F3** | Cycle simulation speed (1x / 2x / 4x / 8x) |
| **F4** | Cycle weather (Sun / Rain / Wind / Snow) |
| **F9** | Demo mode — auto-starts 3 fires & dispatches trucks |
| **ESC** | Quit |
| **START / PAUSE** | Control simulation |
| **RESET** | Reset world to initial state |
| **DEMO** | Same as F9 |

---

### Architecture overview (4 layers)

```
task1_oop_application/src/
├── core/               # Layer 1 — Domain / Simulation (no pygame)
│   ├── events.py       #   Typed event objects (SimEvent, EventType, Severity)
│   ├── world.py        #   City grid generator (Cell, CellType, World)
│   ├── entities.py     #   FireStation + FireTruck with 4-state FSM
│   ├── pathfinding.py  #   A* on road graph + nearest-road BFS
│   └── simulation.py   #   Orchestrator: fire spread, dispatch, history
│
├── render/             # Layer 2 — Rendering
│   ├── theme.py        #   Color palette, font helpers, draw utilities
│   ├── camera.py       #   Pan / zoom camera (world ↔ screen transforms)
│   └── renderer.py     #   Draws world tiles, fire, paths, trucks
│
├── ui/                 # Layer 3 — UI Panels (pure pygame, no pygame_gui)
│   └── panels.py       #   TopBar, LeftPanel, RightPanel, BottomPanel,
│                       #   HelpOverlay, StatsOverlay, Button
│
└── main.py             # Layer 4 — App entry point (wires all layers)
```

**Layer 1 (core)** has zero pygame imports — fully unit-testable in isolation.  
**Layer 2 (render)** reads from the domain and paints to a pygame Surface.  
**Layer 3 (ui)** draws all HUD panels and handles mouse/keyboard input.  
**Layer 4 (main)** initialises pygame, creates all objects, and runs the game loop.

---

### Simulation features

- **City grid** — procedural road layout + building blocks (seeded RNG for determinism).
- **Fire spread** — intensity model; weather multiplies spread rate (Wind 2.8×, Rain 0.25×).
- **Fire trucks** — FSM: `IDLE → EN_ROUTE → EXTINGUISHING → RETURNING`.
- **A\* pathfinding** — trucks navigate on the road graph; path shown as overlay.
- **Auto-dispatch** — idle trucks are assigned to unattended fires every tick.
- **Weather system** — 4 modes (Sun / Rain / Wind / Snow) affect spread rate.
- **Event log** — typed events (FIRE_STARTED, UNIT_DISPATCHED, …) with severity colours.
- **Live chart** — mini line chart of active fires over the last 60 seconds (right panel).
- **Demo mode** — F9 starts 3 spread-out fires and auto-dispatches all trucks.

---

### Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: pygame` | Run `pip install -r requirements.txt` |
| Black / blank window | Update GPU drivers; try `set SDL_VIDEODRIVER=windib` (Windows) |
| Very low FPS | Lower the zoom level (scroll out) to reduce tile-draw count |
| `log.txt` appears | A crash occurred — open it for the full traceback |
| Font looks blocky | Expected — uses pygame's built-in bitmap font (no SysFont) |

---

## Task 2 — Heap + Heap Sort (Self-study)

- Location: `Task 2/`
- Code: `Task 2/heap_sort.py`

### How to run

```bash
python "Task 2/heap_sort.py"
```

---

## Repository structure

```
GRP_36_Project/
├── requirements.txt
├── README.md
├── task1_oop_application/
│   └── src/
│       ├── main.py          ← entry point
│       ├── core/            ← domain layer
│       ├── render/          ← rendering layer
│       └── ui/              ← UI layer
└── Task 2/
    └── heap_sort.py
```

