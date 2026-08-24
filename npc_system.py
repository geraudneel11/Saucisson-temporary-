import pygame

def get_interactable_npc(player, npcs):

    for npc in npcs:
        if player.hitbox.colliderect(npc.interaction_rect):
            return npc

    return None