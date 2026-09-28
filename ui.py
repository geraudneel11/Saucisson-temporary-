import pygame
import math
import random
from classes import Player
from fonts import *
import dialogues
from settings import *

pygame.init()

health_font = pygame.font.SysFont("Ebrima", 20, bold=True)

def draw_health(screen, player):
    health_ratio = player.hp / player.max_hp

    pygame.draw.rect(screen, (255, 0, 0), (20, 20, 300, 30))
    pygame.draw.rect(screen, (0, 255, 50), (20, 20, 300 * health_ratio, 30))
    pygame.draw.rect(screen, (255, 255, 255), (20, 20, 300, 30), 3)
        # pv / pv max affiches en blanc SUR la barre (vert ou rouge),
    # sans changer sa taille. Fonction pour tous les soins
    # (potion, pomme doree, healer) car tout passe par player.hp/max_hp.
    hp_text = health_font.render(f"{int(player.hp)}/{int(player.max_hp)}", True, (255, 255, 255))
    screen.blit(hp_text, (20 + (300 - hp_text.get_width()) // 2, 20 + (30 - hp_text.get_height()) // 2))

def draw_level(screen, current_level, current_wave, game_state):
    level_text = font.render(f"Niveau {current_level}", True, (255, 255, 255))
    screen.blit(level_text, (screen.get_width() // 2 - level_text.get_width() // 2, 15))

    if game_state == "shop" or game_state == "house":
        wave_text = font.render("SHOP", True, (0,255,255))
    else:
        wave_text = font.render(f"Vague {current_wave} / 3", True, (255,220,0))

    screen.blit(wave_text, (screen.get_width()//2-wave_text.get_width()//2, 55))

def draw_transition(screen, transition, current_level, current_wave, game_state):
    if not transition:
        return

    overlay = pygame.Surface(screen.get_size())
    overlay.set_alpha(150)
    overlay.fill((0,0,0))
    screen.blit(overlay,(0,0))

    txt1 = font.render(f"NIVEAU {current_level}", True, (255,255,255))

    if game_state == "shop":
        txt2 = font.render("SHOP",True,(0,255,255))
    else:
        txt2 = font.render(f"VAGUE {current_wave}", True, (255,220,0))

    screen.blit(txt1, (screen.get_width()/2-txt1.get_width()/2, 220))
    screen.blit(txt2,(screen.get_width()/2-txt2.get_width()/2,270))

def draw_coins(screen, player):
    coin_text = coin_font.render(f"Pieces : {player.coins}", True, (255,230,0))
    screen.blit(coin_text,(20,84))

def draw_xp_bar(screen, player):
    # Barre d'xp : SOUS les PV, AU-DESSUS de l'or. Plus courte et
    # plus fine que la barre de vie, bleue comme les orbes. Le
    # compteur de niveau est affiche juste a droite de la barre.
    ratio = max(0, min(1, player.xp / player.xp_required()))
    pygame.draw.rect(screen, (30, 30, 45), (20, 56, XP_BAR_WIDTH, XP_BAR_HEIGHT))
    pygame.draw.rect(screen, XP_ORB_COLOR, (20, 56, int(XP_BAR_WIDTH * ratio), XP_BAR_HEIGHT))
    pygame.draw.rect(screen, (255, 255, 255), (20, 56, XP_BAR_WIDTH, XP_BAR_HEIGHT), 2)

    level_text = coin_font.render(str(player.xp_level), True, (255, 255, 255))
    screen.blit(level_text, (20 + XP_BAR_WIDTH + 12,
        56 - (level_text.get_height() - XP_BAR_HEIGHT) // 2))

def draw_player_level(screen, player):
    # Compteur de niveau de personnage, sous le compteur de pieces
    level_text = coin_font.render(f"Compétences : niv {player.level}", True, (170, 190, 255))
    screen.blit(level_text, (20, 130))

def draw_hotbar(screen, player):
    slot_size = 64
    spacing = 8

    start_x = 15
    y = screen.get_height()-74

    for i in range(3):

        if i == player.selected_slot:
            color = (255,255,0)
        else:
            color = (255,255,255)

        pygame.draw.rect(screen, color, (start_x+i*(slot_size+spacing), y, slot_size, slot_size), 3)
    
def draw_portal_indicator(screen, portal_rect, camera_x, camera_y, game_state):
    if game_state == "shop" and portal_rect:

        portal_screen_x = portal_rect.centerx - camera_x
        portal_screen_y = portal_rect.centery - camera_y
    
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
    
        dx = portal_screen_x - center_x
        dy = portal_screen_y - center_y
        distance = math.hypot(dx, dy)
    
        if (portal_screen_x < 0 or portal_screen_x > screen.get_width() or portal_screen_y < 0 or portal_screen_y > screen.get_height()):
            dx /= distance
            dy /= distance
            margin = 25
            t = min((center_x - margin) / abs(dx) if dx != 0 else 9999, (center_y - margin) / abs(dy) if dy != 0 else 9999)
            indicator_x = center_x + dx * t
            indicator_y = center_y + dy * t
        
            pulse = math.sin(pygame.time.get_ticks() / 120) * 3
            pygame.draw.circle(screen, (103, 166, 114), (int(indicator_x), int(indicator_y)), int(12 + pulse))
