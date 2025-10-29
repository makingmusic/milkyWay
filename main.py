import pygame, sys

pygame.init()
clock = pygame.time.Clock()

# Window setup
screenWidth, screenHeight = 800, 600
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Echo Maze (Player Pulse)")

# Player setup
player = pygame.Rect(300, 300, 50, 50)
echoes = []

run = True
while run:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Create echo from PLAYER center, not mouse click
            echoes.append([player.centerx, player.centery, 0, 255])

    # Background color
    screen.fill((0, 20, 120))

    # Movement speed
    key = pygame.key.get_pressed()
    if key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]:
        x = 4
        y = -4
    else:
        x = 2
        y = -2

    # Diagonal movement (your method)
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

    # Keep player inside window
    player.clamp_ip(screen.get_rect())

    # Draw player
    pygame.draw.rect(screen, (255, 0, 0), player)

    # Draw echoes
    for echo in echoes[:]:
        ex, ey, r, a = echo
        r += 6       # expansion speed
        a -= 4       # fade speed
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
