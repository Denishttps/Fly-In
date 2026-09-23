*This project has been created as part of the 42 curriculum by dbobrov.*

---

# Fly-In 🚁

A multi-drone routing simulator that computes conflict-free paths for a fleet of drones navigating from a shared start zone to a shared goal zone across a directed graph of interconnected hubs. The program supports both a terminal output mode and an interactive web visualizer.

---

## Description

**Goal:** Given a map describing a graph of hubs (zones), their connections, capacity constraints, and zone types, route *N* drones from `start_hub` to `end_hub` in as few simulation turns as possible — without collisions or capacity violations.

### Overview

Each map defines:
- A set of **hubs** (nodes) with 2D coordinates, optional colors, capacity limits, and zone types.
- **Connections** (undirected edges) between hubs with optional per-link drone capacity.
- A **drone count** specifying how many drones depart simultaneously from `start_hub`.

The simulator plans every drone's full path before the simulation begins (offline planning) using a **space-time A\*** search with a shared **Reservation Table** to guarantee conflict-free routes. After planning, the program replays all movements tick by tick, printing or animating the state at each step.

### Zone Types

| Type | Base Cost | Behavior |
|---|---|---|
| `normal` | 1 turn | Standard movement |
| `priority` | 0.8 turns | Preferred routing (faster heuristic) |
| `restricted` | 2 turns | Traversal takes two ticks |
| `blocked` | ∞ | Impassable — never routed through |

---

## Algorithm Choices and Implementation Strategy

### Space-Time A\*

The core routing engine is **Space-Time A\***, a generalisation of A\* that operates in the *space × time* domain. Each search state is `(hub_name, tick)` rather than just `(hub_name)`. This allows the planner to reason about *when* a drone is at a location, not just *where*, which is essential for collision-free multi-agent routing.

**Heuristic:** Before planning begins, Dijkstra's algorithm is run *backwards* from the goal hub to pre-compute the shortest-path distance from every hub to the goal. This distance serves as the admissible heuristic `h(n)`, guaranteeing that A\* finds optimal paths.

**Waiting:** At each tick a drone may either move to a neighbour or **wait** in place (cost: 1 turn). Waiting is represented as a self-loop in space-time, enabling drones to yield to one another at bottlenecks.

**Horizon expansion:** The planner starts with an initial time horizon `h0 + padding` (where `h0` is the heuristic from start to goal and `padding` defaults to 40 ticks). If no conflict-free path is found within the horizon, it doubles the horizon and retries — up to a configurable maximum of 4 000 ticks.

### Reservation Table

A global `ReservationTable` tracks which hubs and edges are already reserved at each future tick. When planning drone *k*, the paths of drones *1 … k-1* are already locked in the table, so drone *k*'s search is automatically steered around them. Reservations are made at:
- **Nodes:** one entry per `(hub_name, tick)` slot, enforcing `max_drones` capacity.
- **Edges:** one entry per `(frozenset{src, dst}, tick)` slot over the full traversal duration, enforcing `max_link_capacity`.

This **Prioritised Planning** approach (sequential, offline, ordered by drone ID) is computationally light and produces collision-free plans with no need for re-planning — at the cost of not guaranteeing a globally optimal solution.

### Step-Cost Function

The step cost from hub *u* to hub *v* combines:
1. The **base cost** of the target zone (`restricted` = 2, `priority` = 0.8, `normal` = 1).
2. A **capacity delay** `k / throughput`, where `k` is how many times the hub has been targeted by already-planned drones and `throughput = min(max_drones_u, max_link_capacity, max_drones_v)`.

This biases later drones away from congested hubs without requiring re-planning.

---

## Visual Representation

### Terminal Mode (Rich)

When run without `--web`, the simulator prints each tick's movements to the terminal using the [Rich](https://github.com/Textualize/rich) library. Each drone token `D{id}-{location}` is **coloured** according to the hub's defined `color` field in the map. When a drone is *in transit* between two hubs, the displayed colour is the average of the source and destination hub colours, smoothly blending between them. Only ticks where at least one drone changes position are printed, keeping the output concise.

This gives an immediate at-a-glance view of:
- Which drone is where at each step.
- The colour-coded zone the drone is currently in or transitioning through.
- The total number of ticks required.

### Web Interface

Launched with `--web`, the project serves a **FastAPI** web server (default: `http://127.0.0.1:8000`) with an interactive browser visualiser:
- A **dropdown** lists all available maps grouped by difficulty.
- Clicking **Generate** calls the backend API, runs the simulation for the chosen map, and returns the full tick-by-tick history as JSON.
- The graph is rendered as a **scalable SVG**, with hubs drawn as coloured circles and connections as lines.
- Drones are animated step by step: each drone appears as a moving circle that travels along the planned route, pausing on restricted zones and visually colliding with capacity limits — though the planning guarantees they never actually conflict.
- Labels are automatically repositioned to avoid overlapping when hubs are tightly packed.

This visual mode is especially useful for understanding how the planner resolves conflicts: you can watch drones yield to one another and take alternative paths in real time.

---

## Instructions

### Requirements

- Python 3.13+
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`

### Installation

```bash
git clone <repository-url>
cd fly-in
uv sync          # installs all dependencies from uv.lock
```

Or with pip:

```bash
pip install fastapi[all] rich argparse pydantic webcolors
```

### Running — Terminal Mode

```bash
python -m src --path maps/easy/01_linear_path.txt
python -m src --path maps/medium/02_circular_loop.txt
python -m src --path maps/hard/03_ultimate_challenge.txt
```

### Running — Web Interface

```bash
python -m src --web
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser, choose a map from the dropdown and click **Generate**.

---

## Map Format

Maps are plain-text files. Lines beginning with `#` are comments and are ignored.

```
nb_drones: <N>

start_hub: <name> <x> <y> [<metadata>]
hub:       <name> <x> <y> [<metadata>]
end_hub:   <name> <x> <y> [<metadata>]

connection: <hub_a>-<hub_b> [<metadata>]
```

**Hub metadata** (inside `[...]`, space-separated key=value pairs):

| Key | Default | Description |
|---|---|---|
| `color` | none | Display colour (CSS name, e.g. `green`) |
| `max_drones` | 1 | Max simultaneous drones in this zone (`-1` = unlimited) |
| `zone` | `normal` | Zone type: `normal`, `priority`, `restricted`, `blocked` |

**Connection metadata:**

| Key | Default | Description |
|---|---|---|
| `max_link_capacity` | 1 | Max simultaneous drones on this link |

---

## Example Input and Expected Output

### Input — `maps/easy/01_linear_path.txt`

```
# Easy Level 1: Simple linear path
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

Two drones travel a linear chain. Because `max_drones` defaults to 1 per hub, the second drone must wait one tick before entering each zone already occupied by the first.

### Expected Output (terminal)

```
D1-start-waypoint1 D2-start
D1-waypoint1 D2-start-waypoint1
D1-waypoint1-waypoint2 D2-waypoint1
D1-waypoint2 D2-waypoint1-waypoint2
D1-waypoint2-goal D2-waypoint2
D1-goal D2-waypoint2-goal
D2-goal
```

Each token is printed in the colour of the hub or the blended colour of the transition. Ticks where nothing moves are omitted.

### Input — `maps/easy/02_simple_fork.txt`

```
nb_drones: 4

start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: path_a 2 1 [color=blue]
hub: path_b 2 -1 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-junction [max_link_capacity=2]
connection: junction-path_a
connection: junction-path_b
connection: path_a-goal
connection: path_b-goal
```

Four drones split at `junction` (capacity 2): two take `path_a`, two take `path_b`. The `max_link_capacity=2` on `start-junction` allows two drones to move simultaneously on that link.

---

## Project Structure

```
fly-in/
├── src/
│   ├── __main__.py          # CLI entry point (--path / --web)
│   ├── dispatcher.py        # Orchestrates planning and output
│   ├── app/                 # FastAPI web server
│   │   ├── app.py
│   │   ├── endpoints/       # REST endpoints (/api/v1/simulation, /api/v1/getMaps)
│   │   ├── schemas/         # Pydantic request/response models
│   │   └── services/        # SimulationService
│   └── core/
│       ├── parser.py        # Map text parser
│       ├── graph_factory.py # Builds Graph from parsed data
│       ├── drone_planner.py # Plans a single drone's route
│       ├── plan_builder.py  # Reconstructs DronePlan from came_from map
│       ├── models/          # Node, Edge, Graph, Drone, Reservation, Plan
│       ├── search/          # SpaceTimeSearch base, A*, Dijkstra
│       └── utils/           # Distance pre-computation, colour blending, map loader
├── maps/                    # Bundled test maps (easy / medium / hard / challenger)
├── static/                  # Web frontend (script.js, style.css)
├── templates/               # Jinja2 HTML template
└── pyproject.toml
```

---

## Resources

### Pathfinding and Multi-Agent Planning

- **A\* Search Algorithm** — Hart, P.E., Nilsson, N.J., Raphael, B. (1968). *A Formal Basis for the Heuristic Determination of Minimum Cost Paths.* IEEE Transactions on Systems Science and Cybernetics.
- **Space-Time A\*** — Silver, D. (2005). *Cooperative Pathfinding.* AIIDE 2005. [PDF](https://www.davidsilver.uk/wp-content/uploads/2020/03/coop-path-AIIDE.pdf)
- **Prioritised Planning** — Erdmann, M., Lozano-Perez, T. (1987). *On Multiple Moving Objects.* Algorithmica.
- **Multi-Agent Pathfinding survey** — Sharon, G. et al. (2015). *Conflict-Based Search for Optimal Multi-Agent Pathfinding.* Artificial Intelligence. [arXiv](https://arxiv.org/abs/1409.3512)
- **Wikipedia — A\* search algorithm** — [https://en.wikipedia.org/wiki/A*\_search\_algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm)

### Libraries and Frameworks

- **FastAPI** — [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Rich** — [https://github.com/Textualize/rich](https://github.com/Textualize/rich)
- **Pydantic** — [https://docs.pydantic.dev](https://docs.pydantic.dev)
- **Uvicorn** — [https://www.uvicorn.org](https://www.uvicorn.org)

### AI Usage
- **README writing:** this document was drafted with the assistance of Claude based on the full project source code.