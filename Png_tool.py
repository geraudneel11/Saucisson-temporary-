import pygame

pygame.init()

screen = pygame.display.set_mode((800, 1052))

sheet = pygame.image.load("Shop.png").convert_alpha()
clock = pygame.time.Clock()

zoom = 4.5

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            print(
                f"x = {mx//zoom} | y = {my//zoom}"
            )

    screen.fill((40,40,40))

    enlarged = pygame.transform.scale(
        sheet,
        (
            sheet.get_width()*zoom,
            sheet.get_height()*zoom
        )
    )

    screen.blit(enlarged,(20,20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()