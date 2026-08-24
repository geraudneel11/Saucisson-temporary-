import pygame
import math
import random
from classes import Player
from fonts import *
import dialogues

pygame.init()

def draw_health(screen, player):
    health_ratio = player.hp / player.max_hp

    pygame.draw.rect(screen, (255, 0, 0), (20, 20, 300, 30))
    pygame.draw.rect(screen, (0, 255, 50), (20, 20, 300 * health_ratio, 30))
    pygame.draw.rect(screen, (255, 255, 255), (20, 20, 300, 30), 3)

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
    screen.blit(coin_text,(20,60))

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
