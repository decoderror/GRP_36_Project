# GRP_36 Disaster Response Simulator — Task 1

A real-time, interactive disaster fire-response simulator modelled on Hong Kong's
**Hung Hom (红磡)** district, built with Python and pygame.

---

## How to Run

From the **repository root**:

```bash
pip install -r requirements.txt
python -m task1_oop_application.src.main
```

The window opens at **1100 × 650** pixels — designed to fit a 14-inch laptop
(1366 × 768 resolution) comfortably.

---

## Features

- **Hung Hom district map** — irregular road network inspired by real Hung Hom
  streets (Hung Hom Road, Ma Tau Wai Road, Gillies Avenue South, etc.);
  Victoria Harbour waterfront to the south; Hong Kong PolyU campus area (commercial
  zone) in the north-west; pocket parks and Hung Hom Promenade.
- **Animated fire & smoke particle effects** — flickering orange/red fire particles
  rise from burning cells; gray smoke drifts upward. Particle count and size scale
  with fire intensity for a dramatic, clearly visible effect.
- **Real-time fire spread** — fires spread to adjacent residential and commercial
  buildings at a rate controlled by the active weather mode.
- **Automatic truck dispatch** — A\* pathfinding routes the nearest idle fire truck
  to each new fire; trucks extinguish the fire then return to their station.
- **Manual fire ignition** — left-click any building on the map to start a fire.
- **Speed control** — 1×, 2×, 4×, 8× simulation speed.
- **Weather system** — sun (normal spread), rain (slow), wind (fast), snow (slow).
- **Live statistics** — active fire count, deployed units, active-fires line chart.
- **Map legend** — colour-coded legend for Road, Residential, Commercial, Park,
  Fire Station, Water, and Fire.
- **Event log** — scrolling panel showing timestamped simulation events.

---

## Controls

| Key / Action | Function |
|---|---|
| **F1** | Toggle help overlay |
| **F2** | Toggle stats HUD (top-left of map) |
| **F3** | Cycle simulation speed (1×/2×/4×/8×) |
| **F4** | Cycle weather (sun/rain/wind/snow) |
| **F9** | Demo mode — auto-ignite 3 spread-out fires |
| **ESC** | Quit |
| **Left Click** (building) | Ignite building / select cell |
| **Right Drag** | Pan the map |
| **Mouse Wheel** | Zoom in / out |
| **START** button | Start / resume simulation |
| **PAUSE** button | Pause simulation |
| **RESET** button | Reset everything |
| **DEMO** button | Start demo scenario |

---

## Architecture (4-layer OOP)

```
task1_oop_application/src/
  core/                      Domain logic (no pygame)
    __init__.py
    world.py                 City grid — Hung Hom layout (CellType, Cell, World)
    entities.py              FireStation, FireTruck, TruckState FSM
    simulation.py            Simulation orchestrator (fire spread, dispatch, events)
    events.py                SimEvent, EventType, Severity
    pathfinding.py           A* + nearest-road BFS
  render/                    Rendering layer
    __init__.py
    camera.py                Viewport pan & zoom
    theme.py                 Colours, fonts, drawing helpers
    renderer.py              Main map renderer (cells, fires, trucks, particles)
    particles.py             Fire & smoke particle system
  ui/                        Pure-pygame UI panels
    __init__.py
    panels.py                TopBar, LeftPanel, RightPanel, BottomPanel, overlays
  models/                    Base OOP models
    __init__.py
    model_base.py
  visualization/             Legacy (kept for reference)
    gui_manager.py
  __init__.py
  main.py                    Entry point — wires all layers together
```

### Layer responsibilities

| Layer | Folder | Responsibility |
|---|---|---|
| **Domain** | `core/` | World state, fire simulation, pathfinding, event emission |
| **Rendering** | `render/` | Drawing world cells, fire/smoke particles, trucks onto pygame Surface |
| **UI** | `ui/` | Panels, buttons, overlays — pure pygame, no pygame_gui |
| **Entry point** | `main.py` | pygame init, event loop, wires all layers |

---

## Map — Hung Hom District Layout

The map is a **33 × 24** cell grid (at default zoom, each cell is 20 × 20 pixels).

| Area | Cell Type | Colour |
|---|---|---|
| Streets / roads | Road | Gray |
| Old Kowloon tenement blocks | Residential (Building) | Warm brown |
| PolyU campus + hotels | Commercial | Steel blue |
| Parks & promenade | Park | Vivid green |
| Fire stations (3 total) | Station | Bright blue |
| Victoria Harbour | Water | Deep blue |

Road network key features:
- **Major E-W**: Ma Tau Wai Road equivalent (y=0), Hung Hom Road (y=8), mid-level road (y=14), harbour road (y=20)
- **Major N-S**: Chatham Road South (x=0), Gillies Avenue South (x=7), Bailey Street (x=21), eastern boundary (x=32)
- Minor / short connectors add the irregular Kowloon block pattern

---

## Requirements

- Python 3.10+
- `pygame >= 2.5` (see `requirements.txt`)

