# GRP 36 Project — Disaster Response Simulator

This repository contains **Task 1** (Disaster Emergency Simulation System) and **Task 2** (Heap Sort self-study).

## Repository Structure

```
GRP_36_Project/
├── task1_oop_application/src/   # Task 1 — main application (entry point)
│   ├── main.py                  # App entry point & main loop
│   ├── core/                    # Domain layer (pure Python, no pygame)
│   │   ├── world.py             # City grid, CellType, World generation
│   │   ├── entities.py          # FireStation, FireTruck, TruckState FSM
│   │   ├── simulation.py        # Simulation orchestrator, fire physics, wind
│   │   ├── pathfinding.py       # A* algorithm + nearest_road BFS
│   │   └── events.py            # Typed event system (SimEvent, Severity)
│   ├── render/                  # Render layer (pygame drawing)
│   │   ├── renderer.py          # World tiles, fire glow, truck paths
│   │   ├── particles.py         # Particle system (snow, rain, wind, smoke, embers)
│   │   ├── camera.py            # Viewport pan & zoom
│   │   └── theme.py             # Color palette, fonts, legend items
│   ├── ui/                      # UI layer (pure pygame panels)
│   │   └── panels.py            # TopBar, LeftPanel, RightPanel, BottomPanel, overlays
│   └── models/                  # Base classes
│       └── model_base.py        # BaseEntity ABC
├── Task 2/                      # Heap Sort self-study
│   └── heap_sort.py
└── requirements.txt
```

---

## Task 1 — Disaster Response Simulator

A real-time city fire simulation with A\* dispatch, weather dynamics, a particle effects system, and a fully zoned city map — all rendered in a 1920×1080 Pygame window with a 4-layer OOP architecture.

### How to Run

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Launch (from repository root):**
```bash
python -m task1_oop_application.src.main
```

A **1920×1080** window will open. The simulation starts paused; press **START** or **F9** (Demo) to begin.

---

### Controls

| Key / Input | Action |
|---|---|
| **START** button / click | Start simulation |
| **PAUSE** button | Pause simulation |
| **RESET** button | Reset world and all units |
| **DEMO** / **F9** | Auto-start 3 fires for demonstration |
| **F1** | Toggle help overlay |
| **F2** | Toggle stats HUD |
| **F3** | Cycle simulation speed (1× → 2× → 4× → 8×) |
| **F4** | Cycle weather (Sun → Rain → Wind → Snow) |
| **ESC** | Quit |
| **Left click** on map | Select cell (click a building to ignite it) |
| **Right click + drag** | Pan camera |
| **Mouse wheel** | Zoom in / out |

---

### Layout (1920×1080)

```
┌───────────────────────────────────────────────────────────┐
│                     TOP BAR (56 px)                        │
├──────────────┬────────────────────────────┬────────────────┤
│              │                            │                │
│  LEFT PANEL  │      MAIN VIEWPORT         │  RIGHT PANEL   │
│   (300 px)   │    (1280 × 824 px)         │   (340 px)     │
│              │                            │                │
│  Controls    │  City map + particles      │  Inspector     │
│  Speed       │  Fire glow + flame tips    │  Unit list     │
│  Weather     │  Truck paths + units       │  Fire chart    │
│  Stats       │  Wind arrow indicator      │                │
│  Legend      │                            │                │
│  Hotkeys     │                            │                │
├──────────────┴────────────────────────────┴────────────────┤
│                   BOTTOM EVENT LOG (200 px)                 │
└───────────────────────────────────────────────────────────┘
```

No panel ever overlaps the main viewport.

---

### Legend — Color Semantics

| Color | Zone / Element |
|---|---|
| **Light gray** | Roads (continuous grid network) |
| **Dark gray** | Residential buildings |
| **Slate / Purple** | Office buildings |
| **Brown / Orange** | Industrial buildings |
| **Green** | Parks / Green space |
| **Blue** | Fire Station |
| **Red → Orange → Yellow-White** | Fire intensity gradient (low → max) |
| **Translucent gray/blue** | Smoke particles |
| **Orange/red sparks** | Ember particles |

The Legend is always visible in the left sidebar, with colored swatches.

---

### Particle Effects

| Weather | Effect |
|---|---|
| **Snow** | Small flakes (2–5 px), drift with wind, varying alpha |
| **Rain** | Short diagonal streaks, angle changes with wind direction |
| **Wind** | Translucent horizontal streaks, direction follows wind angle |
| **Fire** | Animated flame tips (per-cell), smoke + ember particles scaled by intensity |

Wind direction rotates slowly over time (8°/s) and influences:
- Rain/snow trajectory
- Fire spread bias (wind-downwind cells spread faster)

---

### Architecture — 4-Layer OOP

```
┌──────────────────────────────────────┐
│  App Layer  (main.py)                │  Event loop, wires all layers
├──────────────────────────────────────┤
│  UI Layer   (ui/panels.py)           │  Pure pygame panels, no domain logic
├──────────────────────────────────────┤
│  Render Layer (render/)              │  Drawing only — no domain mutations
│    renderer.py  particles.py         │
│    camera.py    theme.py             │
├──────────────────────────────────────┤
│  Core/Domain Layer (core/)           │  Pure Python — no pygame imports
│    simulation.py  world.py           │
│    entities.py    pathfinding.py     │
│    events.py                         │
└──────────────────────────────────────┘
```

**Key OOP concepts demonstrated:**
- **Encapsulation**: Each layer owns its data and exposes a minimal API
- **Inheritance / ABC**: `BaseEntity` → `FireStation`, `FireTruck`
- **Finite State Machine**: `TruckState` (IDLE → EN_ROUTE → EXTINGUISHING → RETURNING)
- **Strategy / polymorphism**: Particle emitter types (snow/rain/wind/smoke/ember)
- **Observer pattern**: `SimEvent` system with typed events and severity levels
- **Separation of concerns**: Domain layer has zero pygame imports

---

### Troubleshooting

**Windows — font rendering:**
The app uses `pygame.font.Font(None, size)` (built-in bitmap font) instead of `SysFont`, so no system font enumeration happens. This avoids the common Windows hang.

**Low FPS / performance:**
- Reduce particle count: edit `ParticleSystem(max_particles=...)` in `renderer.py`
- Lower simulation speed with **F3**
- The glow cache automatically limits glow surface allocations

**Display not 1920×1080:**
The window is created at exactly 1920×1080. On laptops with DPI scaling, ensure your OS display scaling is set to 100%, or the window may appear larger than the screen.

---

## Task 2 — Heap Sort (Self-study)

- Location: `Task 2/`
- Run: `python "Task 2/heap_sort.py"`

## Notes

- Language: Python 3.10+
- Dependencies: `pygame==2.6.1`, `numpy>=1.26`
- Tested on Ubuntu 22.04 and Windows 11
