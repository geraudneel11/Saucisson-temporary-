import pygame

import options
from settings import *


# One direction at a time: this MUST stay a strict if/elif chain,
# never four separate ifs (that would allow diagonal movement).
def move_player(player, speed, walk_up, walk_down, walk_left,
                walk_right):
    keys = pygame.key.get_pressed()
    moving = False

    k_left = options.KEYS["left"]
    k_right = options.KEYS["right"]
    k_up = options.KEYS["up"]
    k_down = options.KEYS["down"]

    if k_left is not None and keys[k_left]:
        player.rect.move_ip(-speed, 0)
        player.direction = "left"
        player.current_animation = walk_left
        moving = True
    elif k_right is not None and keys[k_right]:
        player.rect.move_ip(speed, 0)
        player.direction = "right"
        player.current_animation = walk_right
        moving = True
    elif k_up is not None and keys[k_up]:
        player.rect.move_ip(0, -speed)
        player.direction = "up"
        player.current_animation = walk_up
        moving = True
    elif k_down is not None and keys[k_down]:
        player.rect.move_ip(0, speed)
        player.direction = "down"
        player.current_animation = walk_down
        moving = True

    player.hitbox.center = player.rect.center
    return moving


def apply_idle(player, moving, attacking, idle_up, idle_down,
               idle_left, idle_right):
    # Snap back to the idle animation of the current direction
    # when nothing else (attack/hurt/move) is playing.
    if moving or attacking or player.state == "hurt":
        return
    player.current_frame = 0
    if player.direction == "up":
        player.current_animation = idle_up
    elif player.direction == "down":
        player.current_animation = idle_down
    elif player.direction == "left":
        player.current_animation = idle_left
    elif player.direction == "right":
        player.current_animation = idle_right


def advance_animation(player, moving, attacking, next_attack):
    # Frame counter for the current animation. Attacks alternate
    # between two swing variants (next_attack 1 <-> 2) and are
    # sped up by the equipped armor.
    if attacking:
        animation_speed = max(
            1, round(PLAYER_ATTACK_ANIM_SPEED
                     / player.armor_attack_factor()))
    elif moving:
        animation_speed = 6
    else:
        animation_speed = 10000

    player.frame_timer += 1

    if player.state == "hurt":
        if player.frame_timer >= 6:
            player.frame_timer = 0
            player.current_frame += 1
            if player.current_frame >= len(player.current_animation):
                player.current_frame = 0
                player.frame_timer = 0
                player.state = "idle"
        return attacking, next_attack

    if player.frame_timer >= animation_speed:
        player.frame_timer = 0
        player.current_frame += 1
        if player.current_frame >= len(player.current_animation):
            player.current_frame = 0
            if attacking:
                attacking = False
                next_attack = 2 if next_attack == 1 else 1
    return attacking, next_attack


def update_hurt(player, hurt_up, hurt_down, hurt_left, hurt_right):
    # Keep the hurt animation of the CURRENT direction playing
    # while the invincibility timer runs.
    if player.state != "hurt":
        return
    if player.invicible_timer >= 0:
        player.damage_timer -= 1
        if player.direction == "up":
            player.current_animation = hurt_up
        elif player.direction == "down":
            player.current_animation = hurt_down
        elif player.direction == "left":
            player.current_animation = hurt_left
        else:
            player.current_animation = hurt_right


def draw_player(surface, player, hurt_up, hurt_down, hurt_left,
                hurt_right):
    sprite_rect = player.current_animation[
        player.current_frame].get_rect(midbottom=(
            player.rect.centerx,
            player.rect.bottom + PLAYER_SPRITE_OFFSET_Y))
    if player.state == "hurt":
        if player.direction == "up":
            sprite = hurt_up[player.current_frame]
        elif player.direction == "down":
            sprite = hurt_down[player.current_frame]
        elif player.direction == "left":
            sprite = hurt_left[player.current_frame]
        else:
            sprite = hurt_right[player.current_frame]
    else:
        player.current_frame = min(
            player.current_frame,
            len(player.current_animation) - 1)
        sprite = player.current_animation[player.current_frame]
    surface.blit(sprite, sprite_rect)


def start_attack(player, attacking, enemies):
    # Flag the attack and reset the per-swing hit marker of every
    # enemy (one hit per enemy and per swing).
    if attacking or player.state == "hurt":
        return False
    attacking = True
    player.current_frame = 0
    for enemy in enemies:
        enemy.hit_this_attack = False
    return attacking


def create_attack_hitbox(player):
    # The swing zone starts at the player CENTER and extends in
    # the facing direction (reach x width rectangle).
    cx, cy = player.rect.center
    reach = PLAYER_ATTACK_REACH
    width = PLAYER_ATTACK_WIDTH
    if player.direction == "right":
        return pygame.Rect(cx, cy - width // 2, reach, width)
    elif player.direction == "left":
        return pygame.Rect(cx - reach, cy - width // 2, reach, width)
    elif player.direction == "up":
        return pygame.Rect(cx - width // 2, cy - reach, width, reach)
    else:
        return pygame.Rect(cx - width // 2, cy, width, reach)


def set_attack_animation(player, attack_up, attack_down,
                         attack_left, attack_right):
    if player.direction == "up":
        player.current_animation = attack_up
    elif player.direction == "down":
        player.current_animation = attack_down
    elif player.direction == "left":
        player.current_animation = attack_left
    else:
        player.current_animation = attack_right