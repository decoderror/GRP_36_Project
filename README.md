# GRP 36 Project

This repository is the **final submission** for Group 36.

It contains **Task 1** and **Task 2** in separate folders as required.

---

## Repository Structure

```
GRP_36_Project/
  task1_oop_application/   — Task 1: Disaster Response Simulator (Python, OOP)
    src/                   — Final application source code
  Task 2/                  — Task 2: Heap + Heap Sort (Python)
  README.md
  requirements.txt
```

---

## Task 1 — Disaster Response Simulator (Hong Kong Hung Hom District)

A real-time, interactive **disaster fire-response simulator** modelled on Hong Kong's
**Hung Hom (红磡)** district.  The map features realistic roads, a waterfront
(Victoria Harbour), the Hong Kong Polytechnic University campus area, parks, and
dense residential/commercial blocks.

### Features
- **Hung Hom district map** — irregular road network, Victoria Harbour waterfront,
  PolyU campus (commercial zone), pocket parks, and Hung Hom Promenade.
- **Animated fire & smoke particle effects** — fire particles flicker orange/red and
  rise from burning buildings; smoke drifts upward. Intensity scales with fire level.
- **Fire spread simulation** — fires spread to adjacent buildings at a rate affected
  by weather (sun / rain / wind / snow).
- **Fire truck dispatch** — A\* pathfinding dispatches the nearest idle truck to each
  fire automatically; trucks can also be triggered manually by clicking a building.
- **Speed control** — run at 1×, 2×, 4×, or 8× simulation speed.
- **Weather system** — four weather modes affect fire spread rate.
- **Live statistics** — active fire count, deployed units, event log, mini chart.
- **Map legend** — colour-coded legend for all cell types.

### Location
```
task1_oop_application/src/
```

### Architecture (4-layer OOP)
| Layer | Folder | Contents |
|---|---|---|
| Domain | `core/` | `world.py` (Hung Hom map), `entities.py`, `simulation.py`, `events.py`, `pathfinding.py` |
| Rendering | `render/` | `camera.py`, `theme.py`, `renderer.py`, `particles.py` |
| UI | `ui/` | `panels.py` (TopBar, LeftPanel, RightPanel, BottomPanel, overlays) |
| Entry point | — | `main.py` |

### How to Run
From the **repository root**:
```bash
pip install -r requirements.txt
python -m task1_oop_application.src.main
```

### Controls
| Key / Action | Function |
|---|---|
| F1 | Toggle help overlay |
| F2 | Toggle stats HUD |
| F3 | Cycle simulation speed (1×/2×/4×/8×) |
| F4 | Cycle weather (sun/rain/wind/snow) |
| F9 | Demo mode (auto-start 3 fires) |
| ESC | Quit |
| Left Click (building) | Ignite building / select cell |
| Right Drag | Pan map |
| Mouse Wheel | Zoom in / out |

---

## Task 2 — Heap + Heap Sort (Self-study)

- Location: `Task 2/`
- Code: `Task 2/heap_sort.py`
- Documentation: `Task 2/README.md`

### How to Run
```bash
python "Task 2/heap_sort.py"
```

---

## Requirements

- Python 3.10+
- See `requirements.txt` for dependencies (primarily `pygame`).

