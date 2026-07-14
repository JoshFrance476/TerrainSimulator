from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
import heapq

_finder = AStarFinder()
_cached_grid = None
_cached_matrix = None

def find_path_astar(start, end, traversal_map):
    global _cached_grid, _cached_matrix

    # Only rebuild the grid if the map has changed
    if traversal_map is not _cached_matrix:
        _cached_matrix = traversal_map
        _cached_grid = Grid(matrix=traversal_map)
    else:
        _cached_grid.cleanup()  # resets node state without rebuilding

    start_node = _cached_grid.node(start[1], start[0])
    end_node = _cached_grid.node(end[1], end[0])

    path, _ = _finder.find_path(start_node, end_node, _cached_grid)
    return path

def find_path_dijkstra(start, end, traversal_map, max_distance=1000):
    rows = len(traversal_map)
    cols = len(traversal_map[0])

    heap = [(0, 0, start)]
    visited = {}
    parent = {start: None}

    while heap:
        cost, steps, (row, col) = heapq.heappop(heap)

        if (row, col) in visited:
            continue
        visited[(row, col)] = cost

        if (row, col) == end or steps >= max_distance:
            # Reconstruct path
            path = []
            node = (row, col)
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            return [(col, row) for row, col in path]

        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = row + dr, col + dc
            if (0 <= nr < rows and
                0 <= nc < cols and
                (nr, nc) not in visited):
                new_cost = cost + traversal_map[nr][nc]
                if (nr, nc) not in parent:
                    parent[(nr, nc)] = (row, col)
                    heapq.heappush(heap, (new_cost, steps + 1, (nr, nc)))

    return []