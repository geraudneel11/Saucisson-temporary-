import pygame
import math
import random
from classes import Player
from fonts import *
import fonts
import dialogues
from settings import *

pygame.init()

health_font = pygame.font.SysFont("Ebrima", 20, bold=True)

# --- Cadres de barres pixel art (Health_bar.png / Xp_bar.png) ---
# Chaque cadre est charge UNE seule fois, decoupe sur sa zone utile
# puis agrandi sans lisser (scale_by = pixels carres nets).
# Le remplissage (rouge/vert PV, bleu XP) est dessine DERRIERE le
# cadre : on ne peint que les pixels TRANSPARENTS interieurs
# (detectes une fois pour toutes), le cadre reste donc intact.
BAR_SCALE = 5                    # densite de pixels commune aux 2 barres
HP_BAR_POS = (20, 20)            # barre de vie en haut a gauche
XP_BAR_POS = (20, 89)            # barre d'xp, juste sous les PV          # barre d'xp, juste sous les PV



def _runs_transparents(surface, y):
    # liste des runs [x0, x1] de pixels transparents sur la ligne y
    largeur = surface.get_width()
    runs, cur = [], None
    for x in range(largeur):
        if surface.get_at((x, y))[3] == 0:
            cur = [x, x] if cur is None else [cur[0], x]
        else:
            if cur:
                runs.append(cur)
                cur = None
    if cur:
        runs.append(cur)
    return runs

def _preparer_barre(chemin, y0, y1):
    # charge le PNG, garde la bande (0, y0) -> (largeur, y1), detecte
    # les fenetres interieures (runs transparents bordes d'opaque des
    # deux cotes) et renvoie (zone, spans, cadre agrandi)
    img = pygame.image.load(chemin).convert_alpha()
    zone = img.subsurface((0, y0, img.get_width(), y1 - y0))
    spans = {}
    for y in range(zone.get_height()):
        # un run qui touche un bord de la zone n'est pas remplissable
        spans[y] = [tuple(r) for r in _runs_transparents(zone, y)
                    if r[0] > 0 and r[1] < zone.get_width() - 1]
    cadre = pygame.transform.scale_by(zone, BAR_SCALE)
    return zone, spans, cadre

HP_ZONE, HP_SPANS, HP_CADRE = _preparer_barre("Health_bar.png", 26, 38)
XP_ZONE, XP_SPANS, XP_CADRE = _preparer_barre("Xp_bar.png", 0, 6)

def _centre_fenetre(spans):
    # centre (x, y) de la grande fenetre de remplissage (pour le texte)
    ys = [y for y, runs in spans.items()
          if any(r[1] - r[0] + 1 >= 30 for r in runs)]
    meilleure = max((r for y in ys for r in spans[y]),
                    key=lambda r: r[1] - r[0])
    return ((meilleure[0] + meilleure[1] + 1) / 2,
            (min(ys) + max(ys) + 1) / 2)

HP_CENTRE = _centre_fenetre(HP_SPANS)

def _remplissage_barre(zone, spans, ratio, couleur_fond, couleur_jauge):
    # long rectangle coupe en biseau au lieu de remplir chaque fenetre :
    # fond et jauge sont dessines d'un trait, 1 px plus LARGE que la
    # fenetre, et le cadre opaque recouvre le surplus (le vert passe
    # donc SOUS le bord en diagonale du cadre)
    surf = zone.copy()
    lignes = [(y, runs[0]) for y, runs in sorted(spans.items()) if runs]
    if lignes:
        gauche = min(r[0] for _, r in lignes)
        y_ref, r_ref = max(lignes, key=lambda t: t[1][1])
        droit_max = r_ref[1]
        total = droit_max - gauche + 1
        limite = gauche + int(total * ratio)      # bord vertical de la jauge
        for y, _ in lignes:
            droit = droit_max - (y - y_ref) + 1   # biseau parallele au cadre
            pygame.draw.line(surf, couleur_fond, (gauche, y), (droit, y))
            if limite > gauche:
                pygame.draw.line(surf, couleur_jauge, (gauche, y),
                                 (min(droit, limite - 1), y))
    return pygame.transform.scale_by(surf, BAR_SCALE)
HP_TEXT_SCALE = 2     # chiffres 7x9 de Text3 agrandis x2 (~18 px de haut)

def _draw_hp_text(screen, texte, cx, cy, echelle=None, centered=True,
                  police=None):
    # "X/Y" centre sur (cx, cy) : chiffres blancs de Text3 (planche
    # titre, meme grille que Text1) et slash blanc normal dessine a
    # la main (la planche n'a pas de glyphe "/").
    if echelle is None:
        echelle = HP_TEXT_SCALE
    if police is None:
        police = fonts.lettersT3
    haut = 9 * echelle
    slash_largeur = 4 * echelle
    largeur = 0
    for char in texte:
        if char == "/":
            largeur += slash_largeur
        elif char in police:
            largeur += 7 * echelle
        largeur += echelle                      # petit ecart
    largeur -= echelle
    x = cx - largeur // 2
    y = cy - haut // 2
    for char in texte:
        if char == "/":
            pygame.draw.line(screen, (255, 255, 255),
                             (x, y + haut - 1),
                             (x + slash_largeur - echelle, y + 1), echelle)
            x += slash_largeur + echelle
        elif char in police:
            sprite = pygame.transform.scale(fonts.lettersT3[char],
                                            (7 * echelle, haut))
            screen.blit(sprite, (x, y))
            x += 7 * echelle + echelle
def draw_health(screen, player):
    health_ratio = max(0, min(1, player.hp / player.max_hp))

    # fond rouge puis jauge verte DERRIERE le cadre de fer pixel art
    remplissage = _remplissage_barre(HP_ZONE, HP_SPANS, health_ratio,
                                     (255, 0, 0), (0, 255, 50))
    screen.blit(remplissage, HP_BAR_POS)
    screen.blit(HP_CADRE, HP_BAR_POS)
    # pv / pv max affiches en blanc SUR la fenetre de la barre (vert ou
    # rouge), sans changer sa taille. Fonction pour tous les soins
    # (potion, pomme doree, healer) car tout passe par player.hp/max_hp.
    cx = HP_BAR_POS[0] + 3+int(HP_CENTRE[0] * BAR_SCALE)
    cy = HP_BAR_POS[1] + int(HP_CENTRE[1] * BAR_SCALE)
    _draw_hp_text(screen, f"{int(player.hp)}/{int(player.max_hp)}", cx, cy)

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
    # "PIECES : N" entierement en jaune : lettres et chiffres de Text4
    _draw_hp_text(screen, f"PIECES : {player.coins}", 20, 135,
                  echelle=2, centered=False, police=fonts.lettersT4)
    
def draw_xp_bar(screen, player):
    # Barre d'xp : SOUS les PV, AU-DESSUS de l'or. Plus courte et
    # plus fine que la barre de vie, bleue comme les orbes. Le
    # compteur de niveau est affiche juste a droite de la barre.
    ratio = max(0, min(1, player.xp / player.xp_required()))

    # fond sombre puis jauge bleue DERRIERE le cadre de fer pixel art
    remplissage = _remplissage_barre(XP_ZONE, XP_SPANS, ratio,
                                     (30, 30, 45), XP_ORB_COLOR)
    screen.blit(remplissage, XP_BAR_POS)
    screen.blit(XP_CADRE, XP_BAR_POS)

        # niveau d'xp en chiffres blancs Text3, au centre de la barre
    _draw_hp_text(screen, str(player.xp_level),
                  XP_BAR_POS[0] + XP_CADRE.get_width() // 2,
                  XP_BAR_POS[1] + XP_CADRE.get_height() // 2, echelle=2)
def draw_player_level(screen, player):
    # Compteur de niveau de personnage, sous le compteur de pieces
    level_text = coin_font.render(f"Compétences : niv {player.level}", True, (170, 190, 255))
    screen.blit(level_text, (20, 163))

def draw_hotbar(screen, player):
    slot_size = 64
    spacing = 8

    start_x = 15
    y = screen.get_height()-74

    for i in range(player.inventory_slots):

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
