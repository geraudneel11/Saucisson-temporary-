import pygame

import audio


def handle_attack(player, attacking, enemies, attack_done,
                  attack_hitbox, attack_up, attack_down,
                  attack_left, attack_right, player_system_module):
    # Start a new swing if none is running. The hitbox and the
    # attack animation are created ONCE, on the starting frame.
    if attacking or player.state == "hurt":
        return attacking, attack_done, attack_hitbox

    attacking = player_system_module.start_attack(
        player, attacking, enemies)

    if attacking:
        audio.play("attack")
        attack_done = False
        attack_hitbox = player_system_module.create_attack_hitbox(
            player)
        player_system_module.set_attack_animation(
            player, attack_up, attack_down, attack_left,
            attack_right)

    return attacking, attack_done, attack_hitbox


def resolve_attack(player, enemies, attacking, attack_done,
                   attack_hitbox, max_targets):
    # Damage the closest enemies inside the swing hitbox, up to
    # max_targets per attack. Returns (attack_done, killed_this_attack).
    if not attacking or attack_done or not attack_hitbox:
        return attack_done, []

    px, py = player.rect.centerx, player.rect.centery
    targets = [enemy for enemy in enemies
               if not enemy.dead
               and attack_hitbox.colliderect(enemy.hitbox)]
    targets.sort(
        key=lambda enemy: (enemy.rect.centerx - px) ** 2
                           + (enemy.rect.centery - py) ** 2)

    killed_this_attack = []
    for enemy in targets[:max_targets]:
        enemy.take_damage(
            int(player.base_damage * player.strength_factor()
                * player.armor_damage_factor()
                * player.damage_multiplier),
            player)
        audio.play("hit_enemy")
        enemy.hit_this_attack = True
        if enemy.dead:
            killed_this_attack.append(enemy)

    return True, killed_this_attack