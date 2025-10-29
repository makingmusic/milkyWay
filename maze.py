import pygame
import random
import sys

# --- Maze generation using DFS ---
def generate_maze(width, height):
    # Grid of walls
    maze = [[1 for _ in range(width)] for _ in range(height)]
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # up, right, down, left

    def carve(x, y):
        maze[y][x] = 0  # mark as path
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            # Check inside bounds
            if 0 <= ny < height and 0 <= nx < width and maze[ny][nx] == 1:
                maze[y + dy][x + dx] = 0  # carve wall between
                carve(nx, ny)

    carve(0, 0)  # Start from top-left
    maze[0][0] = 0
    maze[height - 1][width - 1] = 0
    return maze


# --- Pygame setup ---
pygame.init()

CELL_SIZE = 20
MAZE_W, MAZE_H = 31, 21  # must be odd numbers for clean carving
maze = generate_maze(MAZE_W, MAZE_H)

SCREEN_W, SCREEN_H = MAZE_W * CELL_SIZE, MAZE_H * CELL_SIZE
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("DFS Maze Generator")

# Colors
WALL_COLOR = (30, 30, 60)
PATH_COLOR = (220, 220, 255)
ENTRANCE_COLOR = (0, 255, 0)
EXIT_COLOR = (255, 0, 0)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw maze
    for y in range(MAZE_H):
        for x in range(MAZE_W):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if maze[y][x] == 1:
                pygame.draw.rect(screen, WALL_COLOR, rect)
            else:
                pygame.draw.rect(screen, PATH_COLOR, rect)

    # Mark entrance and exit
    pygame.draw.rect(screen, ENTRANCE_COLOR, (0, 0, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(
        screen, EXIT_COLOR,
        ((MAZE_W - 1) * CELL_SIZE, (MAZE_H - 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    )

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
