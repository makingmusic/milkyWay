import pygame, sys, random

pygame.init()
clock = pygame.time.Clock()

# Player setup
player = pygame.Rect(5, 5, 15, 15)
echoes = []

# Maze Genreation
def genMaze(width, height):
    maze = [[1 for _  in range(width)] for _ in range(height)]
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    def carve(x, y):
        maze[y][x] = 0
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = (x + dx * 2), (y + dy * 2)
            if 0 <= ny < height and 0 <= nx < width and maze[ny][nx] == 1:
                maze[y + dy][x + dx] = 0
                carve(nx,ny)

    carve(0, 0)
    maze[0][0] = 0
    maze[height - 1][width - 1] = 0
    return maze

cellSize = 20
mazeX, mazeY = 31, 21
maze = genMaze(mazeX, mazeY)

# Window setup
screenWidth, screenHeight = mazeX * cellSize, mazeY * cellSize
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Echo Maze (Player Pulse)")

wallColor = (0, 0, 80)
pathColor = (0, 0, 0)
entranceColor = (0, 0, 0)
exitColor = (0, 255, 0)

run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            echoes.append([player.centerx, player.centery, 0, 255])

    screen.fill((0, 0, 0))

    for y in range(mazeY):
        for x in range(mazeX):
            rect = pygame.Rect(x * cellSize, y * cellSize, cellSize, cellSize)
            if y == mazeY - 1 and x == mazeX - 1:
                pygame.draw.rect(screen, exitColor, rect)
            elif maze[y][x] == 1:
                pygame.draw.rect(screen, wallColor, rect)
            else:
                pygame.draw.rect(screen, pathColor, rect)

    key = pygame.key.get_pressed()
    if key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]:
        x = 4
        y = -4
    else:
        x = 2
        y = -2

    if key[pygame.K_w] and key[pygame.K_d]:
        player.move_ip(x * 0.7071, y * 0.7071)
    elif key[pygame.K_d] and key[pygame.K_s]:
        player.move_ip(x * 0.7071, -y * 0.7071)
    elif key[pygame.K_s] and key[pygame.K_a]:
        player.move_ip(-x * 0.7071, -y * 0.7071)
    elif key[pygame.K_a] and key[pygame.K_w]:
        player.move_ip(-x * 0.7071, y * 0.7071)
    elif key[pygame.K_a]:
        player.move_ip(-x, 0)
    elif key[pygame.K_d]:
        player.move_ip(x, 0)
    elif key[pygame.K_w]:
        player.move_ip(0, y)
    elif key[pygame.K_s]:
        player.move_ip(0, -y)

    player.clamp_ip(screen.get_rect())
    pygame.draw.rect(screen, (255, 0, 0), player)

    for echo in echoes[:]:
        ex, ey, r, a = echo
        r += 6
        a -= 4
        echo[2], echo[3] = r, a
        if a <= 0:
            echoes.remove(echo)
            continue
        s = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
        pygame.draw.circle(s, (0, 150, 255, a), (ex, ey), r, 2)
        screen.blit(s, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
