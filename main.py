import pygame, sys, random, time
from collections import deque

########################################################
# Config: All config lives here. Self explanatory names.
########################################################
GAME_FRAME_RATE = 60

MAZE_TITLE = "One Maze to Rule Them All"
MAZE_COMPLEXITY = 0.01  # 0.0 -> very simple (straighter, longer corridors), 1.0 -> very complex (more turns/branching feel)

CELL_SIZE = 20
MAZE_W, MAZE_H = 31, 21
MAZE_WALL_COLOR = (173, 216, 230)  # Light blue
MAZE_PATH_COLOR = (0, 0, 0)  # Black
MAZE_ENTRANCE_COLOR = (0, 0, 0)  # Black
MAZE_EXIT_COLOR = (0, 255, 0)  # Green

ECHO_RADIUS_MAX = 25
ECHO_RADIUS_MIN = 0
ECHO_RADIUS_START = 0
ECHO_RADIUS_INCREMENT = 6  # how much the radius increases by each frame.
ECHO_THICKNESS = 2  # width of the echo circle
ECHO_COLOR = (255, 255, 255)  # White

ECHO_ALPHA_MAX = 255
ECHO_ALPHA_MIN = 0
ECHO_ALPHA_START = 255
ECHO_ALPHA_DECREMENT = 4  # how much the alpha decreases by each frame.

PLAYER_SIZE = 15  # 15x15 pixels
PLAYER_START_X = 5
PLAYER_START_Y = 5
PLAYER_COLOR = (255, 0, 0)  # Red
PLAYER_BLINK_COLOR = (255, 255, 255)  # White
PLAYER_EXIT_COLOR = (0, 255, 0)  # Green
PLAYER_XAXIS_MOVEMENT_SPEED = 2
PLAYER_YAXIS_MOVEMENT_SPEED = 2
PLAYER_SHIFT_KEY_MULTIPLIER = 2
PLAYER_DIAGONAL_MOVEMENT_FACTOR = 0.7071  # factor for diagonal movement.

# PLAYER_RIGHT_KEY = pygame.K_d
# PLAYER_LEFT_KEY = pygame.K_a
# PLAYER_UP_KEY = pygame.K_w
# PLAYER_DOWN_KEY = pygame.K_s
PLAYER_RIGHT_KEY = pygame.K_RIGHT
PLAYER_LEFT_KEY = pygame.K_LEFT
PLAYER_UP_KEY = pygame.K_UP
PLAYER_DOWN_KEY = pygame.K_DOWN

PLAYER_ECHO_KEY = pygame.K_SPACE  # Press space to trigger an echo.
PLAYER_SHIFT_KEY = pygame.K_LSHIFT

########################################################
# Maze Util Functions
########################################################


def genMaze(width, height, complexity=MAZE_COMPLEXITY):
    """
    Generate a maze using a depth-first search algorithm.
    Starts with all filled up areas and then carves out the maze.

    Args:
        width: int - width of the maze
        height: int - height of the maze
        complexity: float in [0.0, 1.0] - corridor-turning bias
            0.0 -> very simple (straighter, longer corridors)
            1.0 -> very complex (more turns/branching feel)

    Returns:
        list: 2D list of integers where 0 = path, 1 = wall
    """
    maze = [[1 for _ in range(width)] for _ in range(height)]
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    # Clamp complexity to [0, 1]
    if complexity < 0.0 or complexity > 1.0:
        complexity = MAZE_COMPLEXITY

    def carve(x, y, last_dir=None):
        maze[y][x] = 0
        # Build a working ordering of directions with a bias:
        # lower complexity -> prefer to continue in the same direction
        dirs = directions[:]
        random.shuffle(dirs)
        if last_dir in dirs and random.random() < (1.0 - complexity):
            # Move last_dir to the front to keep corridors straight more often
            dirs.remove(last_dir)
            dirs.insert(0, last_dir)

        for dx, dy in dirs:
            nx, ny = (x + dx * 2), (y + dy * 2)
            if (
                0 <= ny < height and 0 <= nx < width and maze[ny][nx] == 1
            ):  # if the new position is within the bounds and is a wall
                maze[y + dy][x + dx] = 0
                carve(nx, ny, (dx, dy))

    carve(0, 0, None)  # start at the top-left corner
    maze[0][0] = 0  # set the start position to a path
    maze[height - 1][width - 1] = 0  # set the end position to a path

    # Verify the exit is reachable from the start
    # risky. it might become an infinite loop. come back to this later to fix it.
    # i can count the number of times the function is called and if it exceeds a certain number, return an error.
    # TODO: for later.
    if not is_reachable(maze, (0, 0), (width - 1, height - 1)):
        return genMaze(
            width, height, complexity
        )  # If exit is not reachable, regenerate the maze

    return maze


def is_reachable(maze, start, end):
    """
    Check if there's a path from start to end in the maze using BFS.

    Args:
        maze: 2D list where 0 = path, 1 = wall
        start: tuple (x, y) of starting position
        end: tuple (x, y) of ending position

    Returns:
        bool: True if end is reachable from start, False otherwise
    """
    if not maze or not maze[0]:
        return False

    height, width = len(maze), len(maze[0])
    start_x, start_y = start
    end_x, end_y = end

    # Check if start and end are valid positions
    if (
        start_x < 0
        or start_x >= width
        or start_y < 0
        or start_y >= height
        or end_x < 0
        or end_x >= width
        or end_y < 0
        or end_y >= height
    ):
        return False

    # Check if start and end are paths (not walls)
    if maze[start_y][start_x] == 1 or maze[end_y][end_x] == 1:
        return False

    # If start and end are the same position
    if start == end:
        return True

    visited = set()
    queue = deque([start])
    visited.add(start)

    # Directions: up, right, down, left
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    while queue:
        current_x, current_y = queue.popleft()

        # Check if we've reached the end
        if (current_x, current_y) == end:
            return True

        # Explore all 4 directions
        for dx, dy in directions:
            next_x, next_y = current_x + dx, current_y + dy

            # Check bounds
            if (
                0 <= next_x < width
                and 0 <= next_y < height
                and (next_x, next_y) not in visited
                and maze[next_y][next_x] == 0
            ):  # 0 means path
                visited.add((next_x, next_y))
                queue.append((next_x, next_y))

    return False


def detectCollision(player, maze):
    """
    Detect if the player has collided with a wall in the maze.
    """
    # normalize the player to maze grid.
    player_left = player.x // CELL_SIZE
    player_right = (player.x + player.width - 1) // CELL_SIZE
    player_top = player.y // CELL_SIZE
    player_bottom = (player.y + player.height - 1) // CELL_SIZE

    # Check if any part of the player is in a wall
    for y in range(player_top, player_bottom + 1):
        for x in range(player_left, player_right + 1):
            if 0 <= y < len(maze) and 0 <= x < len(maze[0]):  # Check bounds
                if maze[y][x] == 1:  # 1 represents a wall
                    return True
    return False


def resolveCollision(player, maze):
    """
    Return minimal (dx, dy) displacement vector to resolve overlaps with wall tiles.
    If no overlap, returns (0, 0).
    """
    player_left_cell = player.left // CELL_SIZE
    player_right_cell = (player.right - 1) // CELL_SIZE
    player_top_cell = player.top // CELL_SIZE
    player_bottom_cell = (player.bottom - 1) // CELL_SIZE

    height = len(maze)
    width = len(maze[0]) if height > 0 else 0

    min_left_clear = float("inf")
    max_right_clear = float("-inf")
    min_top_clear = float("inf")
    max_bottom_clear = float("-inf")

    def intervals_overlap(a_start, a_end, b_start, b_end):
        return not (a_end <= b_start or b_end <= a_start)

    any_collision = False

    for ty in range(player_top_cell, player_bottom_cell + 1):
        for tx in range(player_left_cell, player_right_cell + 1):
            if not (0 <= ty < height and 0 <= tx < width):
                continue
            if maze[ty][tx] != 1:
                continue

            wall_left = tx * CELL_SIZE
            wall_top = ty * CELL_SIZE
            wall_right = wall_left + CELL_SIZE
            wall_bottom = wall_top + CELL_SIZE

            if not intervals_overlap(player.left, player.right, wall_left, wall_right):
                continue
            if not intervals_overlap(player.top, player.bottom, wall_top, wall_bottom):
                continue

            any_collision = True

            left_clear = wall_left - player.right
            right_clear = wall_right - player.left
            if left_clear < min_left_clear:
                min_left_clear = left_clear
            if right_clear > max_right_clear:
                max_right_clear = right_clear

            top_clear = wall_top - player.bottom
            bottom_clear = wall_bottom - player.top
            if top_clear < min_top_clear:
                min_top_clear = top_clear
            if bottom_clear > max_bottom_clear:
                max_bottom_clear = bottom_clear

    if not any_collision:
        return (0, 0)

    # Compute minimal axis-aligned resolution on each axis independently
    if min_left_clear < 0 < max_right_clear:
        dx_candidate = (
            min_left_clear
            if abs(min_left_clear) <= abs(max_right_clear)
            else max_right_clear
        )
    else:
        dx_candidate = 0

    if min_top_clear < 0 < max_bottom_clear:
        dy_candidate = (
            min_top_clear
            if abs(min_top_clear) <= abs(max_bottom_clear)
            else max_bottom_clear
        )
    else:
        dy_candidate = 0

    # Prefer the smallest movement overall and avoid diagonal hops:
    # move only along the axis with the smaller absolute correction.
    if dx_candidate == 0 and dy_candidate == 0:
        # Fallback: pick the smallest absolute among available finite endpoints
        candidates = []
        if min_left_clear != float("inf"):
            candidates.append(min_left_clear)
        if max_right_clear != float("-inf"):
            candidates.append(max_right_clear)
        if min_top_clear != float("inf"):
            candidates.append(min_top_clear)
        if max_bottom_clear != float("-inf"):
            candidates.append(max_bottom_clear)
        if not candidates:
            return (0, 0)
        best = min(candidates, key=lambda v: abs(v))
        if best in (min_left_clear, max_right_clear):
            return (int(best), 0)
        else:
            return (0, int(best))

    if dx_candidate == 0:
        return (0, int(dy_candidate))
    if dy_candidate == 0:
        return (int(dx_candidate), 0)

    if abs(dx_candidate) <= abs(dy_candidate):
        return (int(dx_candidate), 0)
    else:
        return (0, int(dy_candidate))


def hasPlayerReachedExit(player, maze):
    """
    Check if the player has reached the exit in the maze.
    """
    # find the rect for the player
    player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
    # find the rect for the exit
    exit_rect = pygame.Rect(
        (mazeX - 1) * CELL_SIZE, (mazeY - 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE
    )
    # check if the player's rect overlaps with the exit's rect
    has_reached = player_rect.colliderect(exit_rect)
    return has_reached


########################################################
# Init
########################################################
player = pygame.Rect(PLAYER_START_X, PLAYER_START_Y, PLAYER_SIZE, PLAYER_SIZE)
echoes = []
pygame.init()
clock = pygame.time.Clock()

cellSize = CELL_SIZE
mazeX, mazeY = MAZE_W, MAZE_H
start_time = time.time()
maze = genMaze(mazeX, mazeY)
end_time = time.time()
time_taken_to_generate_maze = round((end_time - start_time) * 1000000, 2)
print("successfully generated maze in ", time_taken_to_generate_maze, "microseconds")

# Window setup
screenWidth, screenHeight = mazeX * cellSize, mazeY * cellSize
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption(MAZE_TITLE)

# color setup
wallColor = MAZE_WALL_COLOR
pathColor = MAZE_PATH_COLOR
entranceColor = MAZE_ENTRANCE_COLOR
exitColor = MAZE_EXIT_COLOR

########################################################
# Main Loop
########################################################
run = True
maze_solve_start_time = time.time()

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if (event.type == pygame.MOUSEBUTTONDOWN) or (
            event.type == pygame.KEYDOWN and event.key == PLAYER_ECHO_KEY
        ):
            echoes.append(
                [player.centerx, player.centery, ECHO_RADIUS_START, ECHO_ALPHA_START]
            )  # schedule the echo to be drawn.

    screen.fill((0, 0, 0))  # clear the screen

    # draw the maze.
    for y in range(mazeY):
        for x in range(mazeX):
            rect = pygame.Rect(x * cellSize, y * cellSize, cellSize, cellSize)
            if y == mazeY - 1 and x == mazeX - 1:
                pygame.draw.rect(screen, exitColor, rect)
            elif maze[y][x] == 1:
                pygame.draw.rect(screen, wallColor, rect)
            else:
                pygame.draw.rect(screen, pathColor, rect)

    # find out if any key is pressed by the player.
    key = pygame.key.get_pressed()  # returns immediately.

    # movement speed setup
    if key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]:
        x_axis_movement_speed = (
            PLAYER_XAXIS_MOVEMENT_SPEED * PLAYER_SHIFT_KEY_MULTIPLIER
        )
        y_axis_movement_speed = (
            PLAYER_YAXIS_MOVEMENT_SPEED * PLAYER_SHIFT_KEY_MULTIPLIER
        )
    else:
        x = 2
        y = -2

    # movement logic
    diag_factor = PLAYER_DIAGONAL_MOVEMENT_FACTOR
    if key[PLAYER_UP_KEY] and key[PLAYER_RIGHT_KEY]:  # top right
        player.move_ip(
            x_axis_movement_speed * diag_factor, -y_axis_movement_speed * diag_factor
        )
    elif key[PLAYER_RIGHT_KEY] and key[PLAYER_DOWN_KEY]:  # bottom right
        player.move_ip(
            x_axis_movement_speed * diag_factor, y_axis_movement_speed * diag_factor
        )
    elif key[PLAYER_DOWN_KEY] and key[PLAYER_LEFT_KEY]:  # bottom left
        player.move_ip(
            -x_axis_movement_speed * diag_factor, y_axis_movement_speed * diag_factor
        )
    elif key[PLAYER_LEFT_KEY] and key[PLAYER_UP_KEY]:  # top left
        player.move_ip(
            -x_axis_movement_speed * diag_factor, -y_axis_movement_speed * diag_factor
        )
    elif key[PLAYER_LEFT_KEY]:  # left
        player.move_ip(-x_axis_movement_speed, 0)
    elif key[PLAYER_RIGHT_KEY]:  # right
        player.move_ip(x_axis_movement_speed, 0)
    elif key[PLAYER_UP_KEY]:  # up
        player.move_ip(0, -y_axis_movement_speed)
    elif key[PLAYER_DOWN_KEY]:  # down
        player.move_ip(0, y_axis_movement_speed)

    # the player may have gone off the screen. bring it back in.
    player.clamp_ip(screen.get_rect())
    pygame.draw.rect(screen, (0, 30, 255), player)

    # draw the echoes. concentric cirles in increasing and descreasing brightness.
    for echo in echoes[::-1]:
        ex, ey, r, a = echo
        r += ECHO_RADIUS_INCREMENT
        a -= ECHO_ALPHA_DECREMENT
        echo[2], echo[3] = r, a  # update the echo to a higher radius and lower alpha.
        if a <= 0:
            echoes.remove(echo)
            continue
        s = pygame.Surface(
            (screenWidth, screenHeight), pygame.SRCALPHA
        )  # make a new clean surface on which to draw the echo.
        pygame.draw.circle(s, ECHO_COLOR, (ex, ey), r, ECHO_THICKNESS)
        screen.blit(s, (0, 0))

    # check if the player has reached the exit.
    if hasPlayerReachedExit(player, maze):
        print("You have reached the exit!")
        # change the color of the player to green with a white outline.
        pygame.draw.rect(screen, PLAYER_EXIT_COLOR, player, 2)
        pygame.display.flip()
        time.sleep(1)
        pygame.draw.rect(screen, PLAYER_COLOR, player)
        pygame.display.flip()
        run = False

    pygame.display.flip()
    clock.tick(GAME_FRAME_RATE)  # GAME_FRAME_RATE frames per second.
    # end of main loop.

# measure the time taken from the start of the main loop to the end of the main loop.
maze_solve_end_time = time.time()
print(
    "time taken to solve: ",
    round((maze_solve_end_time - maze_solve_start_time), 2),
    "seconds",
)

# TODO: do an animation of the player reaching the exit.


# sleep for 1 second.
time.sleep(1)
pygame.quit()
sys.exit()
