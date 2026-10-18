import random

from classes import Enemy
from settings import *


def monsters_for_wave(level, wave):
    # Total monsters for a wave, scaled by the difficulty settings.
    base = 4 + (level - 1) * 6 + (wave - 1) * 3
    monsters = int(base * MONSTER_COUNT_MULTIPLIER)
    return min(monsters, 300)


def spawn_enemy(orc_data, level=1, elite=False):
    # Spawn on a random map edge (top, bottom, left, right).
    side = random.randint(0, 3)
    if side == 0:
        x, y = random.randint(0, MAP_WIDTH), 0
    elif side == 1:
        x, y = random.randint(0, MAP_WIDTH), MAP_HEIGHT
    elif side == 2:
        x, y = 0, random.randint(0, MAP_HEIGHT)
    else:
        x, y = MAP_WIDTH, random.randint(0, MAP_HEIGHT)

    enemy = Enemy.from_orc_data(x, y, orc_data, level)
    enemy.is_elite = elite
    return enemy


def start_wave(enemies, level, wave, orc_data):
    # Wave composition (constants live in settings.py):
    # - MONSTER_ELITE_COUNT elites per wave, each at a random level
    #   between level+MIN_OFFSET and level+MAX_OFFSET;
    # - the rest: MONSTER_MAX_LEVEL_RATIO of them spawn at the
    #   current wave level, the others spread over levels 1..level-1.
    enemies.clear()
    total = monsters_for_wave(level, wave)
    for i in range(total):
        if i < MONSTER_ELITE_COUNT:
            elite_level = random.randint(
                level + MONSTER_ELITE_MIN_OFFSET,
                level + MONSTER_ELITE_MAX_OFFSET)
            enemies.append(
                spawn_enemy(orc_data, elite_level, elite=True))
        elif level == 1 or random.random() < MONSTER_MAX_LEVEL_RATIO:
            enemies.append(spawn_enemy(orc_data, level))
        else:
            enemies.append(
                spawn_enemy(orc_data, random.randint(1, level - 1)))