import pygame
from settings import PLAYER_SPRITE_OFFSET_Y


def movement(player, speed, walk_up, walk_down, walk_left, walk_right):

    keys = pygame.key.get_pressed()

    moving = False

    if keys[pygame.K_q]:
        player.rect.move_ip(-speed, 0)
        player.direction = "left"
        player.current_animation = walk_left
        moving = True

    elif keys[pygame.K_d]:
        player.rect.move_ip(speed, 0)
        player.direction = "right"
        player.current_animation = walk_right
        moving = True

    elif keys[pygame.K_z]:
        player.rect.move_ip(0, -speed)
        player.direction = "up"
        player.current_animation = walk_up
        moving = True

    elif keys[pygame.K_s]:
        player.rect.move_ip(0, speed)
        player.direction = "down"
        player.current_animation = walk_down
        moving = True

    player.hitbox.center = player.rect.center

    return moving

def idle(player, moving, attacking, idle_up, idle_down, idle_left, idle_right):

    
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

def animate(player, moving, attacking, next_attack):

    if attacking:
        animation_speed = 4
    elif moving:
        animation_speed = 6
    else:
        animation_speed = 10000
    if player.state == "hurt":
        player.frame_timer += 1
        if player.frame_timer >= 6:
            player.frame_timer = 0
            player.current_frame += 1
            if player.current_frame >= len(player.current_animation):
                player.current_frame = 0
                player.frame_timer = 0
                player.state = "idle"
        return attacking, next_attack
    player.frame_timer += 1

    if player.frame_timer >= animation_speed:
        player.frame_timer = 0
        player.current_frame += 1
        if player.current_frame >= len(player.current_animation):
            if attacking:
                attacking = False
                player.current_frame = 0
                if next_attack == 1:
                    next_attack = 2
                else:
                    next_attack = 1
            else:
                player.current_frame = 0
    return attacking, next_attack

def update_hurt(player, hurt_up, hurt_down, hurt_left, hurt_right):

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

def draw_player(surface, player, hurt_up, hurt_down, hurt_left, hurt_right):

    player_sprite_rect = player.current_animation[player.current_frame].get_rect(
        midbottom=(
            player.rect.centerx,
            player.rect.bottom + PLAYER_SPRITE_OFFSET_Y
        )
    )
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
            len(player.current_animation) - 1
        )
        sprite = player.current_animation[player.current_frame]
    
    surface.blit(sprite, player_sprite_rect)
def start_attack(player, attacking, enemies):

    if attacking or player.state == "hurt":
        return False

    attacking = True

    player.current_frame = 0

    for enemy in enemies:
        enemy.hit_this_attack = False

    return attacking

def create_attack_hitbox(player):

    if player.direction == "right":

        return pygame.Rect(
            player.rect.right - 155,
            player.rect.centery - 50,
            110,
            125
        )

    elif player.direction == "left":

        return pygame.Rect(
            player.rect.left + 45,
            player.rect.centery - 50,
            110,
            125
        )

    elif player.direction == "up":

        return pygame.Rect(
            player.rect.centerx - 62,
            player.rect.top + 35,
            120,
            110
        )

    else:

        return pygame.Rect(
            player.rect.centerx - 62,
            player.rect.bottom - 75,
            120,
            100
        )
    
def set_attack_animation(
    player,
    attack_up,
    attack_down,
    attack_left,
    attack_right
):

    if player.direction == "up":
        player.current_animation = attack_up

    elif player.direction == "down":
        player.current_animation = attack_down

    elif player.direction == "left":
        player.current_animation = attack_left

    else:
        player.current_animation = attack_right

def change_slot(player, wheel_direction):

    if wheel_direction > 0:
        player.selected_slot = (player.selected_slot - 1) % 3

    elif wheel_direction < 0:
        player.selected_slot = (player.selected_slot + 1) % 3