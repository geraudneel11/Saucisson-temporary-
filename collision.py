import pygame


def resolve_tree_bounce(player, tree_collider, old_pos):
    dx = player.rect.centerx - tree_collider.centerx
    dy = player.rect.centery - tree_collider.centery

    if dx == 0 and dy == 0:
        dx = 1

    distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)
    bounce_strength = 5

    player.rect.x += int(dx / distance * bounce_strength)
    player.rect.y += int(dy / distance * bounce_strength)
    player.hitbox.center = player.rect.center


def resolve_player_collisions(player, colliders, old_pos):
    # collidelist fait la boucle en C : meme resultat que tester chaque
    # collider un par un (un seul contact suffit a annuler le deplacement)
    if player.hitbox.collidelist(colliders) != -1:
        player.rect = old_pos
        player.hitbox.center = player.rect.center


def resolve_entity_collisions(enemies):
    # Balayage trie par x : pour chaque monstre on ne teste que ses
    # voisins de droite, et on s'arrete des que le suivant commence
    # apres son bord droit. Evite de tester les n*(n-1)/2 paires.
    ordered = sorted(enemies, key=lambda enemy: enemy.hitbox.left)
    count = len(ordered)

    for i in range(count):
        enemy1 = ordered[i]
        right = enemy1.hitbox.right

        for j in range(i + 1, count):
            enemy2 = ordered[j]
            if enemy2.hitbox.left >= right:
                break
            if not enemy1.hitbox.colliderect(enemy2.hitbox):
                continue

            dx = enemy1.rect.centerx - enemy2.rect.centerx
            dy = enemy1.rect.centery - enemy2.rect.centery

            if dx == 0 and dy == 0:
                dx = 1

            distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)
            push_strength = 3

            push_x = int(dx / distance * push_strength)
            push_y = int(dy / distance * push_strength)

            enemy1.rect.x += push_x
            enemy1.rect.y += push_y
            enemy2.rect.x -= push_x
            enemy2.rect.y -= push_y

            enemy1.hitbox.center = enemy1.rect.center
            enemy2.hitbox.center = enemy2.rect.center