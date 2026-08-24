import pygame
import random

from classes import Enemy
from settings import *

def monsters_for_wave(level, wave):
	monsters = 4 + (level - 1) * 6 + (wave - 1) * 3
	return min(monsters, 250)

def spawn_enemy(orc_data):

    side = random.randint(0, 3)

    if side == 0:
        x = random.randint(0, MAP_WIDTH)
        y = 0

    elif side == 1:
        x = random.randint(0, MAP_WIDTH)
        y = MAP_HEIGHT

    elif side == 2:
        x = 0
        y = random.randint(0, MAP_HEIGHT)

    else:
        x = MAP_WIDTH
        y = random.randint(0, MAP_HEIGHT)

    return Enemy.from_orc_data(x, y, orc_data)

def start_wave(enemies, level, wave, orc_data):

    enemies.clear()

    for i in range(monsters_for_wave(level, wave)):
        enemies.append(spawn_enemy(orc_data))