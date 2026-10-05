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
                  police=None, slash_couleur=None):
    # "X/Y" centre sur (cx, cy) : chiffres blancs de Text3 (planche
    # titre, meme grille que Text1) et slash blanc normal dessine a
    # la main (la planche n'a pas de glyphe "/").
    if echelle is None:
        echelle = HP_TEXT_SCALE
    if police is None:
        police = fonts.lettersT3
    if slash_couleur is None:
        slash_couleur = (255, 255, 255)
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
    x = cx - largeur // 2 if centered else cx
    y = cy - haut // 2
    for char in texte:
        if char == "/":
            pygame.draw.line(screen, slash_couleur,
                             (x, y + haut - 1),
                             (x + slash_largeur - echelle, y + 1), echelle)
            x += slash_largeur + echelle
        elif char in police:
            sprite = pygame.transform.scale(police[char],
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
    # NIVEAU X en T3 blanc, puis SHOP en T6 ou VAGUE X / 3 en T4 jaune
    _draw_hp_text(screen, f"NIVEAU {current_level}",
                  screen.get_width() // 2, 24,
                  echelle=3, centered=True, police=fonts.lettersT3)
    if game_state == "shop" or game_state == "house":
        _draw_hp_text(screen, "SHOP",
                      screen.get_width() // 2, 64,
                      echelle=3, centered=True, police=fonts.lettersT6)
    else:
        _draw_hp_text(screen, f"VAGUE {current_wave} / 3",
                      screen.get_width() // 2, 64,
                      echelle=3, centered=True, police=fonts.lettersT4,
                      slash_couleur=(244, 219, 0))

def draw_transition(screen, transition, current_level, current_wave, game_state):
    if not transition:
        return

    overlay = pygame.Surface(screen.get_size())
    overlay.set_alpha(150)
    overlay.fill((0,0,0))
    screen.blit(overlay,(0,0))

    _draw_hp_text(screen, f"NIVEAU {current_level}",
                  screen.get_width() // 2, 240,
                  echelle=4, centered=True, police=fonts.lettersT3)
    if game_state == "shop":
        _draw_hp_text(screen, "SHOP",
                      screen.get_width() // 2, 290,
                      echelle=4, centered=True, police=fonts.lettersT6)
    else:
        _draw_hp_text(screen, f"VAGUE {current_wave}",
                      screen.get_width() // 2, 290,
                      echelle=4, centered=True, police=fonts.lettersT4)

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
    # "COMPETENCES : NIV X" entierement en pixel art Text5
    # (sans accent : la planche titre n'a pas de "e" accentue)
    _draw_hp_text(screen, f"COMPETENCES : NIV {player.level}", 20, 169,
                  echelle=2, centered=False, police=fonts.lettersT5)

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

# ---------- MENU PRINCIPAL ----------
MENU_TITRE = "PIXSOULS"
_menu_shop_sheet = pygame.image.load("Shop.png").convert_alpha()
MENU_BOUTON_GAUCHE = _menu_shop_sheet.subsurface((94, 186, 37, 17))
MENU_BOUTON_SUITE = _menu_shop_sheet.subsurface((102, 186, 29, 17))

def calculer_boutons_menu(screen):
    # boutons identiques a ceux des interfaces PNJ : barre de 280 px
    # scalés (meme largeur que "Acheter"/"Quitter" du marchand),
    # hauteur 17 px a l'echelle UI_SCALE
    largeur = int(150 + 29 * UI_SCALE)
    hauteur = int(17 * UI_SCALE)
    cx = screen.get_width() // 2
    y0 = int(screen.get_height() * 0.55)
    return [
        (pygame.Rect(cx - largeur // 2, y0, largeur, hauteur), "jouer"),
        (pygame.Rect(cx - largeur // 2, y0 + hauteur + int(24 * UI_SCALE),
                     largeur, hauteur), "quitter"),
    ]

def _dessiner_bouton_menu(screen, rect):
    # meme recette que "Acheter" / "Quitter" du marchand : le capot
    # gauche (37 px) puis les 2 prolongements (29 px) POSES CHEVAUCHES
    # aux offsets 0 / +100 / +150 (px scalés, comme en fenetre shop)
    for sprite, delta in ((MENU_BOUTON_GAUCHE, 0),
                          (MENU_BOUTON_SUITE, 100),
                          (MENU_BOUTON_SUITE, 150)):
        img = pygame.transform.scale(
            sprite,
            (int(sprite.get_width() * UI_SCALE),
             int(sprite.get_height() * UI_SCALE)))
        screen.blit(img, (rect.x + delta, rect.y))

def draw_menu(screen, boutons, fond):
    # scene du jeu pre-rendue + voile sombre, titre PIXSOULS en T3
    # puis les boutons PNJ : texte lettersC1 qui devient lettersC6 au
    # survol (comportement identique aux boutons du marchand)
    screen.blit(fond, (0, 0))
    voile = pygame.Surface(screen.get_size())
    voile.set_alpha(140)
    voile.fill((10, 10, 16))
    screen.blit(voile, (0, 0))
    _draw_hp_text(screen, MENU_TITRE,
                  screen.get_width() // 2, int(screen.get_height() * 0.28),
                  echelle=8, centered=True, police=fonts.lettersT3)
    survol = pygame.mouse.get_pos()
    body_scale = max(1, UI_SCALE * 0.75)
    for rect, action in boutons:
        _dessiner_bouton_menu(screen, rect)
        label = "JOUER" if action == "jouer" else "QUITTER"
        police = fonts.lettersC6 if rect.collidepoint(survol) else fonts.lettersC1
        fonts.draw_body_text(
            screen, label,
            rect.centerx - fonts.get_text_width(label, body_scale, police) // 2,
            rect.centery - int(3 * body_scale)-10,
            rect.width, font_dict=police, scale=body_scale
        )

INTRO_STUDIO = "SAUCISSON STUDIOS"
INTRO_DUREES = (1200, 900, 1200, 1000)   # fondu entrant, pause,
                                         # fondu sortant, reveal du menu

def draw_intro(screen, t_ms, boutons, fond):
    # fond noir, "SAUCISSON STUDIOS" en fondu puis fondu sortant, et
    # enfin le menu qui se revele sous un voile noir qui s'efface.
    # Renvoie True quand l'intro est terminee.
    entree, pause, sortie, reveal = INTRO_DUREES
    total_texte = entree + pause + sortie
    if t_ms < total_texte:
        if t_ms < entree:
            alpha = 255 * t_ms // entree
        elif t_ms < entree + pause:
            alpha = 255
        else:
            alpha = 255 - 255 * (t_ms - entree - pause) // sortie
        screen.fill((0, 0, 0))
        temp = pygame.Surface(screen.get_size(),
                              pygame.SRCALPHA).convert_alpha()
        _draw_hp_text(temp, INTRO_STUDIO,
                      screen.get_width() // 2, screen.get_height() // 2,
                      echelle=5, centered=True, police=fonts.lettersT3)
        temp.set_alpha(alpha)
        screen.blit(temp, (0, 0))
        return False
    # phase finale : le menu apparait sous le noir qui s'efface
    draw_menu(screen, boutons, fond)
    reste = t_ms - total_texte
    if reste < reveal:
        voile = pygame.Surface(screen.get_size())
        voile.fill((0, 0, 0))
        voile.set_alpha(255 - 255 * reste // reveal)
        screen.blit(voile, (0, 0))
        return False
    return True

def draw_chargement(screen, t_ms, duree):
    # ecran de chargement : CHARGEMENT en T3 blanc + la jauge d'xp
    # pixel art (moteur existant) qui se remplit sur la duree
    ratio = min(1.0, t_ms / duree)
    screen.fill((0, 0, 0))
    _draw_hp_text(screen, "CHARGEMENT",
                  screen.get_width() // 2, screen.get_height() // 2 - 50,
                  echelle=4, centered=True, police=fonts.lettersT3)
    pos = (screen.get_width() // 2 - XP_CADRE.get_width() // 2,
           screen.get_height() // 2 + 10)
    screen.blit(_remplissage_barre(XP_ZONE, XP_SPANS, ratio,
                                   (30, 30, 45), XP_ORB_COLOR), pos)
    screen.blit(XP_CADRE, pos)
