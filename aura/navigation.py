"""Grid-based A* path planning for the AURA simulator."""

from heapq import heappop, heappush

GridPoint = tuple[int, int]


def plan_path(
    start: GridPoint,
    goal: GridPoint,
    width: int,
    height: int,
    blocked: set[GridPoint],
) -> list[GridPoint] | None:
    """Return a shortest four-direction grid path, or None if no path exists."""
    for point, label in ((start, "start"), (goal, "goal")):
        x, y = point
        if not (0 <= x < width and 0 <= y < height):
            raise ValueError(f"{label} is outside the grid")
        if point in blocked:
            raise ValueError(f"{label} is blocked")

    frontier: list[tuple[int, int, GridPoint]] = []
    heappush(frontier, (0, 0, start))
    came_from: dict[GridPoint, GridPoint] = {}
    cost_so_far = {start: 0}
    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))

    while frontier:
        _, current_cost, current = heappop(frontier)
        if current_cost != cost_so_far[current]:
            continue
        if current == goal:
            path = [goal]
            while path[-1] != start:
                path.append(came_from[path[-1]])
            path.reverse()
            return path

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            x, y = neighbor
            if not (0 <= x < width and 0 <= y < height) or neighbor in blocked:
                continue
            new_cost = current_cost + 1
            if new_cost >= cost_so_far.get(neighbor, float("inf")):
                continue
            cost_so_far[neighbor] = new_cost
            came_from[neighbor] = current
            heuristic = abs(goal[0] - x) + abs(goal[1] - y)
            heappush(frontier, (new_cost + heuristic, new_cost, neighbor))

    return None


def choose_escape_step(
    current: GridPoint,
    pursuer: tuple[float, float],
    width: int,
    height: int,
    blocked: set[GridPoint],
) -> GridPoint:
    """Move one cell away from the pursuer when a safer cell is available."""
    x, y = current
    candidates = [current]
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        neighbor = (x + dx, y + dy)
        nx, ny = neighbor
        if (
            0 <= nx < width
            and 0 <= ny < height
            and neighbor not in blocked
        ):
            candidates.append(neighbor)

    def distance_squared(cell: GridPoint) -> float:
        return (cell[0] - pursuer[0]) ** 2 + (cell[1] - pursuer[1]) ** 2

    safest = max(candidates, key=distance_squared)
    if distance_squared(safest) > distance_squared(current):
        return safest
    return current


def nearest_open_cell(
    point: GridPoint,
    width: int,
    height: int,
    blocked: set[GridPoint],
) -> GridPoint | None:
    """Return the open cell nearest to point, or None if the grid is blocked."""
    open_cells = (
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in blocked
    )
    return min(
        open_cells,
        key=lambda cell: ((cell[0] - point[0]) ** 2 + (cell[1] - point[1]) ** 2, cell),
        default=None,
    )
