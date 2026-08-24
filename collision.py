import pygame


def resolve_player_collisions(player, colliders, old_pos):
    for collider in colliders:
        if player.hitbox.colliderect(collider):
            player.rect = old_pos
            player.hitbox.center = player.rect.center


def resolve_entity_collisions(enemies):
    for i, enemy1 in enumerate(enemies):
        for enemy2 in enemies[i + 1:]:
            if enemy1.hitbox.colliderect(enemy2.hitbox):
                dx = enemy1.rect.centerx - enemy2.rect.centerx
                dy = enemy1.rect.centery - enemy2.rect.centery

                if dx == 0 and dy == 0:
                    dx = 1

                distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)
                push_strength = 3

                push_x = dx / distance * push_strength
                push_y = dy / distance * push_strength

                enemy1.rect.x += int(push_x)
                enemy1.rect.y += int(push_y)
                enemy2.rect.x -= int(push_x)
                enemy2.rect.y -= int(push_y)

                enemy1.hitbox.center = enemy1.rect.center
                enemy2.hitbox.center = enemy2.rect.center
