# -*- coding: utf-8 -*-
"""
A* pathfinding on the road graph.

Pure domain logic — no pygame imports.
"""
from __future__ import annotations

import heapq
from collections import deque
from typing import Dict, List, Optional, Tuple


def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """Manhattan distance heuristic."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(
    world,
    start: Tuple[int, int],
    goal: Tuple[int, int],
) -> Optional[List[Tuple[int, int]]]:
    """
    A* shortest path on the road graph.

    Returns the path as a list of (gx, gy) tuples from *start* to *goal*
    (both inclusive), or None if no path exists.
    """
    if start == goal:
        return [start]

    open_heap: List[Tuple[float, Tuple[int, int]]] = [(0.0, start)]
    came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    g_score: Dict[Tuple[int, int], float] = {start: 0.0}

    while open_heap:
        _, current = heapq.heappop(open_heap)

        if current == goal:
            # Reconstruct path
            path: List[Tuple[int, int]] = []
            node: Optional[Tuple[int, int]] = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()
            return path

        for neighbor in world.road_neighbors(*current):
            tentative_g = g_score[current] + 1.0
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_heap, (f, neighbor))
                came_from[neighbor] = current

    return None  # No path found


def nearest_road(world, gx: int, gy: int) -> Optional[Tuple[int, int]]:
    """
    BFS to find the nearest road/station cell from any cell (including buildings).
    Used to find the road entry point next to a burning building.
    """
    from task1_oop_application.src.core.world import CellType

    start = (gx, gy)
    cell = world.get_cell(gx, gy)
    if cell and cell.type in (CellType.ROAD, CellType.STATION):
        return start

    queue: deque[Tuple[int, int]] = deque([start])
    visited = {start}

    while queue:
        cx, cy = queue.popleft()
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = cx + dx, cy + dy
            if (nx, ny) in visited:
                continue
            if not (0 <= nx < world.width and 0 <= ny < world.height):
                continue
            visited.add((nx, ny))
            neighbor_cell = world.get_cell(nx, ny)
            if neighbor_cell and neighbor_cell.type in (CellType.ROAD, CellType.STATION):
                return (nx, ny)
            queue.append((nx, ny))

    return None
