import pygame
from settings import *


def toggle_fullscreen(screen, fullscreen):

	fullscreen = not fullscreen

	if fullscreen:
		desktop_size = pygame.display.get_desktop_sizes()[0]
		screen = pygame.display.set_mode(
			desktop_size,
			pygame.NOFRAME | pygame.SCALED,
			vsync=1
		)
	else:
		screen = pygame.display.set_mode(
			(SCREEN_WIDTH, SCREEN_HEIGHT),
			pygame.SCALED,
			vsync=1
		)

	return screen, fullscreen