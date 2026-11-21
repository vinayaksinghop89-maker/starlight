"""AURA's first interactive 2D robot simulator."""

import math
import sys

import pygame

from commands import parse_mission
from navigation import choose_escape_step, nearest_open_cell, plan_path

CELL_SIZE = 25
GRID_WIDTH = 32
GRID_HEIGHT = 22
WORLD_WIDTH = GRID_WIDTH * CELL_SIZE
WORLD_HEIGHT = GRID_HEIGHT * CELL_SIZE
HUD_HEIGHT = 100
WINDOW_SIZE = (WORLD_WIDTH, WORLD_HEIGHT + HUD_HEIGHT)
ROBOT_RADIUS = 11
ROBOT_SPEED = 190
TARGET_MOVE_INTERVAL = CELL_SIZE / ROBOT_SPEED
TAG_DISTANCE = ROBOT_RADIUS + 10
CHASE_TIME_LIMIT = 60.0
TARGET_CELL = (28, 14)
START_CELL = (3, 3)

OBSTACLES = (
    pygame.Rect(8 * CELL_SIZE, 2 * CELL_SIZE, 2 * CELL_SIZE, 9 * CELL_SIZE),
    pygame.Rect(8 * CELL_SIZE, 15 * CELL_SIZE, 2 * CELL_SIZE, 6 * CELL_SIZE),
    pygame.Rect(15 * CELL_SIZE, 0, 2 * CELL_SIZE, 7 * CELL_SIZE),
    pygame.Rect(15 * CELL_SIZE, 11 * CELL_SIZE, 2 * CELL_SIZE, 8 * CELL_SIZE),
    pygame.Rect(22 * CELL_SIZE, 4 * CELL_SIZE, 2 * CELL_SIZE, 10 * CELL_SIZE),
    pygame.Rect(25 * CELL_SIZE, 17 * CELL_SIZE, 5 * CELL_SIZE, 2 * CELL_SIZE),
)

BACKGROUND = (21, 27, 38)
GRID_COLOR = (37, 46, 60)
OBSTACLE_COLOR = (103, 119, 140)
ROBOT_COLOR = (59, 174, 255)
TARGET_COLOR = (245, 72, 72)
PATH_COLOR = (78, 221, 165)
TEXT_COLOR = (233, 239, 247)
MUTED_COLOR = (158, 173, 194)


def cell_center(cell: tuple[int, int]) -> pygame.Vector2:
    return pygame.Vector2(
        cell[0] * CELL_SIZE + CELL_SIZE / 2,
        cell[1] * CELL_SIZE + CELL_SIZE / 2,
    )


def circle_hits_obstacle(position: pygame.Vector2) -> bool:
    for obstacle in OBSTACLES:
        nearest_x = max(obstacle.left, min(position.x, obstacle.right))
        nearest_y = max(obstacle.top, min(position.y, obstacle.bottom))
        dx = position.x - nearest_x
        dy = position.y - nearest_y
        if dx * dx + dy * dy < ROBOT_RADIUS * ROBOT_RADIUS:
            return True
    return False


def get_blocked_cells() -> set[tuple[int, int]]:
    blocked = set()
    clearance = ROBOT_RADIUS + 2
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            center = cell_center((x, y))
            if (
                center.x < clearance
                or center.x > WORLD_WIDTH - clearance
                or center.y < clearance
                or center.y > WORLD_HEIGHT - clearance
            ):
                blocked.add((x, y))
                continue
            if circle_hits_obstacle(center):
                blocked.add((x, y))
    return blocked


def plan_target_route(
    robot: pygame.Vector2,
    target_cell: tuple[int, int],
    blocked: set[tuple[int, int]],
) -> list[pygame.Vector2] | None:
    start = (int(robot.x // CELL_SIZE), int(robot.y // CELL_SIZE))
    path = plan_path(start, target_cell, GRID_WIDTH, GRID_HEIGHT, blocked)
    if path is None:
        return None
    return [cell_center(cell) for cell in path[1:]]


def draw_grid(screen: pygame.Surface) -> None:
    for x in range(0, WORLD_WIDTH + 1, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, WORLD_HEIGHT))
    for y in range(0, WORLD_HEIGHT + 1, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WORLD_WIDTH, y))


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("AURA | Robot Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)

    robot = cell_center(START_CELL)
    target_cell = TARGET_CELL
    target = cell_center(target_cell)
    blocked = get_blocked_cells()
    route: list[pygame.Vector2] = []
    status = "Ready. Press T, type 'tag the red object', then Enter."
    command = ""
    typing_command = False
    found_target = False
    tagged = False
    active_mission: str | None = None
    target_move_timer = 0.0
    game_time_remaining = CHASE_TIME_LIMIT
    game_over = False
    running = True

    def finish_game(winner: str) -> None:
        nonlocal active_mission, tagged, game_over, status
        route.clear()
        active_mission = None
        game_over = True
        tagged = winner == "aura"
        status = (
            "AURA tagged the red object! AURA wins!"
            if winner == "aura"
            else "Red caught AURA! Red wins!"
        )

    while running:
        dt = min(clock.tick(60) / 1000, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if typing_command:
                    if event.key == pygame.K_ESCAPE:
                        typing_command = False
                        command = ""
                    elif event.key == pygame.K_RETURN:
                        mission = parse_mission(command)
                        command = ""
                        typing_command = False
                        if mission in {"find_red", "tag_red"}:
                            if mission == "tag_red" and tagged:
                                status = "Red object already tagged!"
                                continue
                            try:
                                route = plan_target_route(robot, target_cell, blocked)
                            except ValueError as error:
                                route.clear()
                                active_mission = None
                                status = f"Cannot plan route: {error}."
                            else:
                                if route is None:
                                    route.clear()
                                    active_mission = None
                                    status = "No safe route to the red object."
                                else:
                                    active_mission = mission
                                    target_move_timer = 0.0
                                    found_target = False
                                    if mission == "tag_red":
                                        game_time_remaining = CHASE_TIME_LIMIT
                                        game_over = False
                                    if route:
                                        status = (
                                            "Chasing the red object..."
                                            if mission == "tag_red"
                                            else "Navigating to the red object..."
                                        )
                                    else:
                                        found_target = True
                                        if mission == "tag_red":
                                            finish_game("aura")
                                        else:
                                            status = "Red object found!"
                                            active_mission = None
                        else:
                            status = "Unknown command. Try: tag the red object"
                    elif event.key == pygame.K_BACKSPACE:
                        command = command[:-1]
                    elif event.unicode.isprintable():
                        command += event.unicode
                elif game_over:
                    if event.key == pygame.K_r:
                        robot = cell_center(START_CELL)
                        target_cell = TARGET_CELL
                        target = cell_center(target_cell)
                        route.clear()
                        tagged = False
                        found_target = False
                        active_mission = None
                        target_move_timer = 0.0
                        game_time_remaining = CHASE_TIME_LIMIT
                        game_over = False
                        status = "Ready. Press T, type 'tag the red object', then Enter."
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif event.key == pygame.K_t and active_mission != "red_chasing":
                    typing_command = True
                    command = ""
                    route.clear()
                    active_mission = None
                elif event.key == pygame.K_SPACE:
                    if active_mission != "red_chasing":
                        route.clear()
                        active_mission = None
                        status = "Stopped."
                elif event.key == pygame.K_ESCAPE:
                    running = False

        if active_mission in {"tag_red", "red_chasing"} and not game_over:
            if robot.distance_to(target) <= TAG_DISTANCE:
                finish_game("aura" if active_mission == "tag_red" else "red")

        if active_mission == "tag_red" and not game_over:
            game_time_remaining = max(0.0, game_time_remaining - dt)
            if game_time_remaining <= 0:
                active_mission = "red_chasing"
                route.clear()
                target_move_timer = 0.0
                status = "Time's up! Red is chasing AURA—run with WASD!"

        if not game_over and not typing_command and not route:
            keys = pygame.key.get_pressed()
            movement = pygame.Vector2(
                float(keys[pygame.K_RIGHT] or keys[pygame.K_d])
                - float(keys[pygame.K_LEFT] or keys[pygame.K_a]),
                float(keys[pygame.K_DOWN] or keys[pygame.K_s])
                - float(keys[pygame.K_UP] or keys[pygame.K_w]),
            )
            if movement.length_squared() > 0:
                movement = movement.normalize() * ROBOT_SPEED * dt
                candidate_x = pygame.Vector2(robot.x + movement.x, robot.y)
                if (
                    ROBOT_RADIUS <= candidate_x.x <= WORLD_WIDTH - ROBOT_RADIUS
                    and not circle_hits_obstacle(candidate_x)
                ):
                    robot.x = candidate_x.x
                candidate_y = pygame.Vector2(robot.x, robot.y + movement.y)
                if (
                    ROBOT_RADIUS <= candidate_y.y <= WORLD_HEIGHT - ROBOT_RADIUS
                    and not circle_hits_obstacle(candidate_y)
                ):
                    robot.y = candidate_y.y
                found_target = robot.distance_to(target) <= ROBOT_RADIUS + 12
                if active_mission == "red_chasing":
                    status = "Run! The red object is chasing AURA!"
                else:
                    status = "Red object found!" if found_target else "Manual control."

        if active_mission in {"tag_red", "red_chasing"} and not game_over:
            target_move_timer += dt
            if target_move_timer >= TARGET_MOVE_INTERVAL:
                target_move_timer -= TARGET_MOVE_INTERVAL
                if active_mission == "tag_red":
                    pursuer = (
                        robot.x / CELL_SIZE - 0.5,
                        robot.y / CELL_SIZE - 0.5,
                    )
                    next_cell = choose_escape_step(
                        target_cell,
                        pursuer,
                        GRID_WIDTH,
                        GRID_HEIGHT,
                        blocked,
                    )
                else:
                    robot_cell = (
                        int(robot.x // CELL_SIZE),
                        int(robot.y // CELL_SIZE),
                    )
                    chase_goal = nearest_open_cell(
                        robot_cell, GRID_WIDTH, GRID_HEIGHT, blocked
                    )
                    chase_path = (
                        plan_path(
                            target_cell,
                            chase_goal,
                            GRID_WIDTH,
                            GRID_HEIGHT,
                            blocked,
                        )
                        if chase_goal is not None
                        else None
                    )
                    next_cell = (
                        chase_path[1]
                        if chase_path is not None and len(chase_path) > 1
                        else target_cell
                    )

                if next_cell != target_cell:
                    target_cell = next_cell
                    target = cell_center(target_cell)
                    if active_mission == "tag_red":
                        try:
                            route = plan_target_route(robot, target_cell, blocked)
                        except ValueError as error:
                            route.clear()
                            active_mission = None
                            status = f"Cannot replan route: {error}."
                        else:
                            if route is None:
                                active_mission = None
                                status = "No safe route to the moving red object."
                            else:
                                status = "Chasing the red object..."

        if route:
            distance_left = ROBOT_SPEED * dt
            route_failed = False
            while route and distance_left > 0:
                delta = route[0] - robot
                distance = delta.length()
                step = min(distance, distance_left)
                candidate = robot + delta.normalize() * step
                if (
                    not ROBOT_RADIUS <= candidate.x <= WORLD_WIDTH - ROBOT_RADIUS
                    or not ROBOT_RADIUS <= candidate.y <= WORLD_HEIGHT - ROBOT_RADIUS
                    or circle_hits_obstacle(candidate)
                ):
                    route.clear()
                    found_target = False
                    active_mission = None
                    status = "Route blocked; stopped safely."
                    route_failed = True
                    break
                robot = candidate
                distance_left -= step
                if distance <= step:
                    route.pop(0)
                else:
                    distance_left = 0
            if not route and not route_failed:
                found_target = True
                if active_mission == "tag_red":
                    finish_game("aura")
                else:
                    status = "Red object found!"
                    active_mission = None

        if (
            active_mission in {"tag_red", "red_chasing"}
            and not game_over
            and robot.distance_to(target) <= TAG_DISTANCE
        ):
            finish_game("aura" if active_mission == "tag_red" else "red")

        screen.fill(BACKGROUND)
        draw_grid(screen)

        for obstacle in OBSTACLES:
            pygame.draw.rect(screen, OBSTACLE_COLOR, obstacle, border_radius=4)

        if route:
            points = [(round(robot.x), round(robot.y))]
            points.extend((round(point.x), round(point.y)) for point in route)
            if len(points) > 1:
                pygame.draw.lines(screen, PATH_COLOR, False, points, 3)

        target_color = (87, 220, 139) if tagged else TARGET_COLOR
        outline_color = (192, 255, 211) if tagged else (255, 190, 190)
        pygame.draw.circle(screen, target_color, target, 10)
        pygame.draw.circle(screen, outline_color, target, 15, 2)
        if tagged:
            tag_label = small_font.render("TAGGED", True, target_color)
            screen.blit(tag_label, (target.x - tag_label.get_width() / 2, target.y - 32))
        pygame.draw.circle(screen, ROBOT_COLOR, (round(robot.x), round(robot.y)), ROBOT_RADIUS)
        pygame.draw.circle(screen, (225, 245, 255), (round(robot.x), round(robot.y)), ROBOT_RADIUS, 2)

        pygame.draw.rect(
            screen, (15, 20, 29), (0, WORLD_HEIGHT, WORLD_WIDTH, HUD_HEIGHT)
        )
        pygame.draw.line(
            screen, (57, 70, 88), (0, WORLD_HEIGHT), (WORLD_WIDTH, WORLD_HEIGHT), 2
        )
        status_text = font.render(status, True, TEXT_COLOR)
        screen.blit(status_text, (16, WORLD_HEIGHT + 12))

        if active_mission == "tag_red":
            game_label = f"AURA has {math.ceil(game_time_remaining)}s"
        elif active_mission == "red_chasing":
            game_label = "RUN! Red is chasing"
        elif game_over:
            game_label = "R: play again"
        else:
            game_label = ""
        if game_label:
            timer_text = small_font.render(game_label, True, PATH_COLOR)
            screen.blit(
                timer_text,
                (WORLD_WIDTH - timer_text.get_width() - 16, WORLD_HEIGHT + 12),
            )

        if typing_command:
            input_text = f"> {command}_"
            hint = "Enter: run command | Esc: cancel"
        elif game_over:
            input_text = "Game over"
            hint = "R: play again | Esc: quit"
        elif active_mission == "red_chasing":
            input_text = "Red is chasing AURA!"
            hint = "WASD / arrows: run | Esc: quit"
        else:
            input_text = "Press T to enter a mission"
            hint = "WASD / arrows: drive | Space: stop chase | Esc: quit"
        screen.blit(
            small_font.render(input_text, True, PATH_COLOR if typing_command else MUTED_COLOR),
            (16, WORLD_HEIGHT + 42),
        )
        screen.blit(
            small_font.render(hint, True, MUTED_COLOR),
            (16, WORLD_HEIGHT + 68),
        )

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
