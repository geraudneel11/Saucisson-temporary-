import pygame


def handle_attack_event(player, attacking, enemies, attack_done, attack_hitbox, attack_up, attack_down, attack_left, attack_right, player_system_module):
    if attacking or player.state == "hurt":
        return attacking, attack_done, attack_hitbox

    attacking = player_system_module.start_attack(player, attacking, enemies)

    if attacking:
        attack_done = False
        attack_hitbox = player_system_module.create_attack_hitbox(player)
        player_system_module.set_attack_animation(player, attack_up, attack_down, attack_left, attack_right)

    return attacking, attack_done, attack_hitbox


def resolve_player_attack(player, enemies, attacking, attack_done, attack_hitbox, max_targets):
    if not attacking or attack_done or not attack_hitbox:
        return attack_done, []

    targets = []

    for enemy in enemies:
        if enemy.dead:
            continue
        if attack_hitbox.colliderect(enemy.hitbox):
            targets.append(enemy)

    targets.sort(
        key=lambda enemy: (
            (enemy.rect.centerx - player.rect.centerx) ** 2
            + (enemy.rect.centery - player.rect.centery) ** 2
        )
    )

    killed_this_attack = []

    for enemy in targets[:max_targets]:
        if enemy.dead:
            continue
        enemy.take_damage(int(player.base_damage * player.damage_multiplier), player)
        enemy.hit_this_attack = True
        if enemy.dead:
            killed_this_attack.append(enemy)

    return True, killed_this_attack