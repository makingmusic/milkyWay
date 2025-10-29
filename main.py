import pygame
import time

pygame.init()
clock = pygame.time.Clock()

screenWidth = 800
screenHeight = 600

screen = pygame.display.set_mode((screenWidth, screenHeight))

echoes


# Player sprite shape stuff(Widt, Height, x pos, y pos)
player = pygame.Rect(300, 300, 50, 50)

run = 1
while run:
    # Color for BG
    screen.fill((0,20,120))

    pygame.draw.rect(screen, (255, 0, 0), player)

    key = pygame.key.get_pressed()
    if key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]:
        x = 4
        y = -4
    else:
        x = 2
        y = -2

    # diagonal movement 
    if key[pygame.K_w] and key[pygame.K_d]:
        player.move_ip(x * 0.7071, y * 0.7071)
    elif key[pygame.K_d] and key[pygame.K_s]:
        player.move_ip(x * 0.7071, -y * 0.7071)
    elif key[pygame.K_s] and key[pygame.K_a]:
        player.move_ip(-x * 0.7071, -y * 0.7071)
    elif key[pygame.K_a] and key[pygame.K_w]:
        player.move_ip(-x * 0.7071, y * 0.7071)

    # single direction movement
    elif key[pygame.K_a]:
        player.move_ip(-x, 0)
    elif key[pygame.K_d]:
        player.move_ip(x, 0)
    elif key[pygame.K_w]:
        player.move_ip(0, y)
    elif key[pygame.K_s]:
        player.move_ip(0, -y)

    # stop program thingy
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    time.sleep(0.01)

    pygame.display.update()

pygame.quit()



### Next Steps: ###
## Sprite PNG loading(Figure out how to make player a png/jpg/pdf/etc.)
## Maze Gen
## Pulse Creation