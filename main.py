import pygame, sys, random, time
from collections import deque


########################################################
# Config: All config lives here.
########################################################
CELL_SIZE = 20
MAZE_W, MAZE_H = 31, 21
PLAYER_SIZE = 15 # 15x15 pixels
PLAYER_START_X = 5
PLAYER_START_Y = 5
PLAYER_COLOR = (255, 0, 0) # Red

WALL_COLOR = (0, 0, 80) # Dark gray
PATH_COLOR = (0, 0, 0) # Black
ENTRANCE_COLOR = (0, 0, 0) # Black
EXIT_COLOR = (0, 255, 0) # Green

GAME_FRAME_RATE = 60

PLAYER_XAXIS_MOVEMENT_SPEED = 2
PLAYER_YAXIS_MOVEMENT_SPEED = 2
PLAYER_SHIFT_KEY_MULTIPLIER = 2 # when shift key is pressed, the movement speed is multiplied by this value.

#PLAYER_RIGHT_KEY = pygame.K_d
#PLAYER_LEFT_KEY = pygame.K_a
#PLAYER_UP_KEY = pygame.K_w
#PLAYER_DOWN_KEY = pygame.K_s 

PLAYER_RIGHT_KEY = pygame.K_RIGHT
PLAYER_LEFT_KEY = pygame.K_LEFT
PLAYER_UP_KEY = pygame.K_UP
PLAYER_DOWN_KEY = pygame.K_DOWN
PLAYER_ECHO_KEY = pygame.K_SPACE # Press space to trigger an echo.
PLAYER_SHIFT_KEY = pygame.K_LSHIFT

ECHO_RADIUS_MAX = 25
ECHO_RADIUS_MIN = 0
ECHO_RADIUS_START = 0
ECHO_RADIUS_INCREMENT = 6 # how much the radius increases by each frame.
ECHO_THICKNESS = 2
ECHO_COLOR = (255, 255, 255) # White

ECHO_ALPHA_MAX = 255
ECHO_ALPHA_MIN = 0
ECHO_ALPHA_START = 255 
ECHO_ALPHA_DECREMENT = 4 # how much the alpha decreases by each frame. 

MAZE_TITLE = "One Maze to Rule Them All"

########################################################
# Maze Util Functions 
########################################################

def genMaze(width, height):
    """
    Generate a maze using a depth-first search algorithm. 
    Starts with all filled up areas and then carves out the maze.
    
    Args:
        width: int - width of the maze
        height: int - height of the maze
    
    Returns:
        list: 2D list of integers where 0 = path, 1 = wall
    """
    maze = [[1 for _  in range(width)] for _ in range(height)]
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    def carve(x, y):
        maze[y][x] = 0
        random.shuffle(directions) # pick any direction at random
        for dx, dy in directions:
            nx, ny = (x + dx * 2), (y + dy * 2)
            if 0 <= ny < height and 0 <= nx < width and maze[ny][nx] == 1: # if the new position is within the bounds and is a wall
                maze[y + dy][x + dx] = 0
                carve(nx,ny)

    carve(0, 0) # start at the top-left corner
    maze[0][0] = 0 # set the start position to a path
    maze[height - 1][width - 1] = 0 # set the end position to a path 
    
    # Verify the exit is reachable from the start
    # risky. it might become an infinite loop. come back to this later to fix it. 
    # i can count the number of times the function is called and if it exceeds a certain number, return an error.  
    # TODO: for later. 
    if not is_reachable(maze, (0, 0), (width-1, height-1)):
        return genMaze(width, height) # If exit is not reachable, regenerate the maze
    
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
    if (start_x < 0 or start_x >= width or start_y < 0 or start_y >= height or
        end_x < 0 or end_x >= width or end_y < 0 or end_y >= height):
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
            if (0 <= next_x < width and 0 <= next_y < height and
                (next_x, next_y) not in visited and
                maze[next_y][next_x] == 0):  # 0 means path
                
                visited.add((next_x, next_y))
                queue.append((next_x, next_y))
    
    return False


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
print("successfully generated maze in ", round((end_time - start_time) * 1000000, 2), "micro seconds")

# Window setup
screenWidth, screenHeight = mazeX * cellSize, mazeY * cellSize
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption(MAZE_TITLE)

# color setup
wallColor = WALL_COLOR
pathColor = PATH_COLOR
entranceColor = ENTRANCE_COLOR
exitColor = EXIT_COLOR

########################################################
# Main Loop
########################################################
run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if ((event.type == pygame.MOUSEBUTTONDOWN) or (event.type == pygame.KEYDOWN and event.key == PLAYER_ECHO_KEY)):
            echoes.append([player.centerx, player.centery, ECHO_RADIUS_START, ECHO_ALPHA_START]) # schedule the echo to be drawn.

    screen.fill((0, 0, 0)) # clear the screen

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
    key = pygame.key.get_pressed() # returns immediately.

    # movement speed setup
    if key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]: 
        x_axis_movement_speed = PLAYER_XAXIS_MOVEMENT_SPEED * PLAYER_SHIFT_KEY_MULTIPLIER
        y_axis_movement_speed = PLAYER_YAXIS_MOVEMENT_SPEED * PLAYER_SHIFT_KEY_MULTIPLIER
    else:
        x_axis_movement_speed = PLAYER_XAXIS_MOVEMENT_SPEED
        y_axis_movement_speed = PLAYER_YAXIS_MOVEMENT_SPEED

    # movement logic 
    diag_factor = 0.7071
    if key[PLAYER_UP_KEY] and key[PLAYER_RIGHT_KEY]: # top right
        player.move_ip(x_axis_movement_speed * diag_factor, -y_axis_movement_speed * diag_factor)
    elif key[PLAYER_RIGHT_KEY] and key[PLAYER_DOWN_KEY]: # bottom right
        player.move_ip(x_axis_movement_speed * diag_factor, y_axis_movement_speed * diag_factor)
    elif key[PLAYER_DOWN_KEY] and key[PLAYER_LEFT_KEY]: # bottom left
        player.move_ip(-x_axis_movement_speed * diag_factor, y_axis_movement_speed * diag_factor)
    elif key[PLAYER_LEFT_KEY] and key[PLAYER_UP_KEY]: # top left
        player.move_ip(-x_axis_movement_speed * diag_factor, -y_axis_movement_speed * diag_factor)
    elif key[PLAYER_LEFT_KEY]: # left
        player.move_ip(-x_axis_movement_speed, 0)
    elif key[PLAYER_RIGHT_KEY]: # right
        player.move_ip(x_axis_movement_speed, 0)
    elif key[PLAYER_UP_KEY]: # up
        player.move_ip(0, -y_axis_movement_speed)
    elif key[PLAYER_DOWN_KEY]: # down
        player.move_ip(0, y_axis_movement_speed)
        
    # the player may have gone off the screen. bring it back in. 
    player.clamp_ip(screen.get_rect()) 
    pygame.draw.rect(screen, PLAYER_COLOR, player) 

    # draw the echoes. concentric cirles in increasing and descreasing brightness. 
    for echo in echoes[::-1]:
        ex, ey, r, a = echo
        r += ECHO_RADIUS_INCREMENT
        a -= ECHO_ALPHA_DECREMENT
        echo[2], echo[3] = r, a # update the echo to a higher radius and lower alpha. 
        if a <= 0:
            echoes.remove(echo)
            continue
        s = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA) #make a new clean surface on which to draw the echo.
        pygame.draw.circle(s, ECHO_COLOR, (ex, ey), r, ECHO_THICKNESS)
        screen.blit(s, (0, 0)) 

    pygame.display.flip()
    clock.tick(GAME_FRAME_RATE) # GAME_FRAME_RATE frames per second. 
    # end of main loop. 

pygame.quit()
sys.exit()
