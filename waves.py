import pygame
import random

from classes import Enemy
from settings import *

def monsters_for_wave(level, wave):
	base = 4 + (level - 1) * 6 + (wave - 1) * 3
	monsters = int(base * MONSTER_COUNT_MULTIPLIER)
	return min(monsters, 300)

def spawn_enemy(orc_data, level=1, elite=False):

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

    enemy = Enemy.from_orc_data(x, y, orc_data, level)
    enemy.is_elite = elite
    return enemy

def start_wave(enemies, level, wave, orc_data):

    enemies.clear()

    # Composition de la vague (reglages dans settings.py) :
    # - MONSTER_ELITE_COUNT monstres d'ELITE par vague, d'un niveau
    #   aleatoire entre courant+MIN_OFFSET et courant+MAX_OFFSET
    #   (labels affiches dans MONSTER_ELITE_LABEL_COLOR) ;
    # - le reste : MONSTER_MAX_LEVEL_RATIO de la vague au niveau
    #   courant, le reste reparti sur les niveaux 1..courant-1.
    total = monsters_for_wave(level, wave)
    for i in range(total):
        if i < MONSTER_ELITE_COUNT:
            elite_level = random.randint(
                level + MONSTER_ELITE_MIN_OFFSET,
                level + MONSTER_ELITE_MAX_OFFSET
            )
            enemies.append(spawn_enemy(orc_data, elite_level, elite=True))
        elif level == 1 or random.random() < MONSTER_MAX_LEVEL_RATIO:
            enemies.append(spawn_enemy(orc_data, level))
        else:
            enemies.append(spawn_enemy(orc_data, random.randint(1, level - 1)))