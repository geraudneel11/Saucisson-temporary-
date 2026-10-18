import pygame
import math
import random
import os
import json
from classes import Player
from fonts import *
import fonts
import dialogues
from settings import *
import options
from options import tr

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
_BARRES_CACHE = {}   # (zone, ratio arrondi, couleurs) -> surface prete
def _remplissage_barre(zone, spans, ratio, couleur_fond, couleur_jauge):
    # the bar only changes when the ratio moves: cache the rendered
    # surface and rebuild it only then
    cle = (id(zone), round(ratio, 3), couleur_fond, couleur_jauge)
    en_cache = _BARRES_CACHE.get(cle)
    if en_cache is not None:
        return en_cache
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
    surf = pygame.transform.scale_by(surf, BAR_SCALE)
    if len(_BARRES_CACHE) > 64:
        _BARRES_CACHE.clear()
    _BARRES_CACHE[cle] = surf
    return surf
HP_TEXT_SCALE = 2     # chiffres 7x9 de Text3 agrandis x2 (~18 px de haut)
_GLYPHE_CACHE = {}   # (police, caractere, echelle) -> sprite pret

def _draw_hp_text(screen, texte, cx, cy, echelle=None, centered=True,
                  police=None, slash_couleur=None):
    # "X/Y" centre sur (cx, cy) : chiffres blancs de Text3 (planche
    # titre, meme grille que Text1) et slash blanc normal dessine a
    # la main (la planche n'a pas de glyphe "/").
    texte = tr(texte)
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
            # scaled glyphs are CACHED: transform.scale per
            # character per frame was a real bottleneck in the HUD
            cle = (id(police), char, echelle)
            sprite = _GLYPHE_CACHE.get(cle)
            if sprite is None:
                sprite = pygame.transform.scale(police[char],
                                                (7 * echelle, haut))
                _GLYPHE_CACHE[cle] = sprite
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
    texte_titre_hc(screen, f"{tr('LEVEL')} {current_level}",
            screen.get_width() // 2, 30, 3, fonts.lettersT3)
    if game_state == "shop" or game_state == "house":
        _draw_hp_text(screen, tr("SHOP"),
                      screen.get_width() // 2, 64,
                      echelle=3, centered=True, police=fonts.lettersT6)
    else:
        _draw_hp_text(screen, f"{tr('WAVE')} {current_wave} / 3",
                      screen.get_width() // 2, 64,
                      echelle=3, centered=True, police=fonts.lettersT4,
                      slash_couleur=(244, 219, 0))
_OVERLAY_TRANSITION = None
def draw_transition(screen, transition, current_level, current_wave, game_state):
    if not transition:
        return

    global _OVERLAY_TRANSITION
    if _OVERLAY_TRANSITION is None:
        _OVERLAY_TRANSITION = pygame.Surface(
            screen.get_size()).convert()
        _OVERLAY_TRANSITION.fill((0, 0, 0))
    _OVERLAY_TRANSITION.set_alpha(150)
    screen.blit(_OVERLAY_TRANSITION, (0, 0))

    texte_titre_hc(screen, f"{tr('LEVEL')} {current_level}",
                   screen.get_width() // 2, 240, 4, fonts.lettersT3)
    if game_state == "shop":
        _draw_hp_text(screen, "SHOP",
                      screen.get_width() // 2, 290,
                      echelle=4, centered=True, police=fonts.lettersT6)
    else:
        _draw_hp_text(screen, f"{tr('WAVE')} {current_wave}",
                      screen.get_width() // 2, 290,
                      echelle=4, centered=True, police=fonts.lettersT4)

def draw_coins(screen, player):
    # "PIECES : N" entierement en jaune : lettres et chiffres de Text4
    _draw_hp_text(screen, f"{tr('COINS:')} {player.coins}", 20, 135,
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
    _draw_hp_text(screen, tr("SKILLS: LVL {}").format(player.level), 20, 169,
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
    # boutons identiques a ceux des interfaces PNJ ; chaque bouton est
    # ajuste a SA propre etiquette (boutons courts, pas de longueur
    # morte) et l'ensemble reste centre au milieu de l'ecran
    scale = UI_SCALE
    _base, hauteur = dims_barre_pnj(scale)
    cx = screen.get_width() // 2
    y0 = int(screen.get_height() * 0.55)
    boutons = []
    for i, action in enumerate(("jouer", "reglages", "quitter")):
        # les 3 boutons ont la MEME largeur (celle du plus long
        # libelle, dans les 2 langues) et un espacement reduit
        largeur = largeur_bouton_pour(
            ("JOUER", "REGLAGES", "QUITTER",
             "PLAY", "SETTINGS", "QUIT"), scale)
        boutons.append((pygame.Rect(cx - largeur // 2,
                                    y0 + i * (hauteur
                                              + int(12 * UI_SCALE)),
                                    largeur, hauteur), action))
    return boutons

def _dessiner_bouton_menu(screen, rect):
    # barre PNJ etalee sur toute la largeur du bouton (voir
    # dessiner_barre_pnj) : le texte ne depasse jamais des cotes
    dessiner_barre_pnj(screen, rect.x, rect.y, UI_SCALE, rect.width)

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
    for rect, action in boutons:
        _dessiner_bouton_menu(screen, rect)
        label = (tr("PLAY") if action == "jouer" else
                 tr("SETTINGS") if action == "reglages"
                 else tr("QUIT"))
        _label_pnj(screen, label, rect, UI_SCALE,
                   rect.collidepoint(survol),
                   offset_y=OFFSET_Y_TEXTE["principal"],
                   offset_x=OFFSET_X_TEXTE["principal"])
INTRO_STUDIO = "SAUCISSON STUDIOS"
INTRO_DUREES = (1200, 900, 1200, 1000)   # fondu entrant, pause,
                                         # fondu sortant, reveal du menu


# decalages des BOUTONS de l'ecran de mort : (dx, dy) par
# bouton, en px ecran
OFFSET_BOUTONS_MORT = {"reapparaitre": (0, -15), "quitter": (0, -15)}
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
    texte_titre_hc(screen, "CHARGEMENT",
                   screen.get_width() // 2, screen.get_height() // 2 - 32,
                   4, fonts.lettersT3)
    pos = (screen.get_width() // 2 - XP_CADRE.get_width() // 2,
           screen.get_height() // 2 + 10)
    screen.blit(_remplissage_barre(XP_ZONE, XP_SPANS, ratio,
                                   (30, 30, 45), XP_ORB_COLOR), pos)
    screen.blit(XP_CADRE, pos)

# ---------- SOUS-MENUS : JOUER / SAUVEGARDES / DEV / HITBOXES / REGLAGES ----------
HITBOX_TYPES = ["JOUEUR", "ENNEMIS", "PIECES", "PNJ", "ORBES XP", "PORTAIL",
                "POINTS PNJ", "MEUBLES", "MURS", "DECORS", "PROJECTILES"]
HITBOX_COULEURS = [(255, 60, 60), (60, 255, 90), (70, 140, 255),
                   (255, 220, 0), (0, 255, 255), (255, 0, 255),
                   (255, 255, 255), (255, 140, 0), (200, 160, 255),
                   (255, 105, 180), (180, 180, 180)]
SETTINGS_LIGNES = [
    ("vitesse_joueur", "VITESSE JOUEUR", 1, 1, 60, "int"),
    ("force_joueur", "FORCE JOUEUR", 1, 1, 200, "int"),
    ("pv_ennemis", "PV ENNEMIS (BASE)", 5, 5, 500, "int"),
    ("degats_ennemis", "DEGATS ENNEMIS (BASE)", 1, 0, 100, "int"),
    ("vitesse_ennemis", "VITESSE ENNEMIS (BASE)", 1, 1, 20, "int"),
    ("or_depart", "OR DE DEPART", 50, 0, 100000, "int"),
    ("niveau_competences", "NIV. COMPETENCES", 1, 0, 50, "int"),
    ("potions_depart", "POTIONS DE DEPART", 1, 0, 99, "int"),
    ("lieu", "LIEU D'APPARITION", None, None, None, "cycle"),
    ("pommes_pct", "TAUX POMMES (%)", 5, 0, 100, "int"),
    ("pommes_dorees_pct", "TAUX POMMES DOREES (%)", 5, 0, 100, "int"),
    ("immortalite", "IMMORTALITE", None, None, None, "onoff"),
    ("space_kill", "SPACE KILL", None, None, None, "onoff"),
]
LIEUX = ["wave", "shop", "house", "chapel"]
NOMS_LIEUX = {"wave": "VAGUES", "shop": "BOUTIQUE",
              "house": "MAISON", "chapel": "CHAPELLE"}

_PAS_PILULE = 100.0 / 9.0      # 11.11 : pas de repetition d'un morceau suite
_O1_PILULE = 200.0 / 9.0       # 22.22 : position du 1er prolongement
_O2_PILULE = 300.0 / 9.0       # 33.33 : position du 2e prolongement
_SUITE_VISIBLE = 23.0          # partie visible d'un morceau suite (px source)

OFFSET_REGLAGES = {
    "pommes_pct": (110, 0),
    "pommes_dorees_pct": (110, 0),
    
}

def n_morceaux_pilule(largeur, scale):
    # nombre de morceaux "suite" necessaires pour que la pilule
    # visible atteigne `largeur` px ; 1 = format court (capot + un
    # seul morceau, boutons du menu principal), puis un de plus par
    # pas de 11,11 px source
    une = int(_O1_PILULE * scale) + int(_SUITE_VISIBLE * scale)
    if largeur <= une:
        return 1
    pas = max(1, int(_PAS_PILULE * scale))
    return 1 + int(math.ceil((largeur - une) / pas))

def largeur_pilule(n, scale):
    # largeur VISIBLE d'une pilule composee de n morceaux suite
    pas = max(1, int(_PAS_PILULE * scale))
    return (int(_O1_PILULE * scale) + (n - 1) * pas
            + int(_SUITE_VISIBLE * scale))

def dessiner_barre_pnj(screen, x, y, scale, largeur=None):
    # barre de bouton des interfaces PNJ, composee EXACTEMENT comme la
    # barre du marchand : capot gauche + morceaux "suite" superposes a
    # pas fixe, chaque morceau cachant le cap arrondi du precedent.
    # Pour allonger : on RAJOUTE des morceaux, on n'etire jamais le
    # sprite (aucune coupure visible au milieu, extremites intactes).
    img_g = pygame.transform.scale(
        MENU_BOUTON_GAUCHE, (int(37 * scale), int(17 * scale)))
    img_d = pygame.transform.scale(
        MENU_BOUTON_SUITE, (int(29 * scale), int(17 * scale)))
    o1, o2 = int(_O1_PILULE * scale), int(_O2_PILULE * scale)
    screen.blit(img_g, (x, y))
    if largeur is None:
        screen.blit(img_d, (x + o1, y))
        screen.blit(img_d, (x + o2, y))
        return
    n = n_morceaux_pilule(largeur, scale)
    pas = max(1, int(_PAS_PILULE * scale))
    screen.blit(img_d, (x + o1, y))
    for k in range(n - 1):
        screen.blit(img_d, (x + o2 + k * pas, y))

def dims_barre_pnj(scale):
    return int(33.33 * scale) + int(29 * scale), int(17 * scale)

def largeur_bouton_pour(labels, scale):
    # largeur de barre commune a tous les boutons affiches en meme
    # temps : la plus large des etiquettes + une marge, arrondie a une
    # largeur de pilule EXACTE (la barre finit pile sur le bord du
    # bouton, sans debordement ni raccourci)
    body = max(1, scale * 0.75)
    w = max(fonts.get_text_width(t, body, fonts.lettersC1)
            for t in labels)
    brute = int(w + 14 * scale)
    return largeur_pilule(n_morceaux_pilule(brute, scale), scale)

# --- reglage vertical du texte, une entree par taille de bouton ---
# le texte est pose au centre vertical de la barre ; mets 2 pour
# descendre le texte de 2 px a l'ecran, -3 pour le monter, etc.
# --- reglage vertical du texte, une entree par taille de bouton ---
# le texte est pose au centre vertical de la barre ; mets 2 pour
# descendre le texte de 2 px a l'ecran, -3 pour le monter, etc.
class _OffsetLangue(dict):
    # dict d'offsets : en ANGLAIS, ajoute le delta de self.en a la
    # valeur francaise. Les appels OFFSET_X_TEXTE["jouer"] restent
    # inchanges.
    def __init__(self, base, en):
        super().__init__(base)
        self.en = en

    def __getitem__(self, cle):
        valeur = super().__getitem__(cle)
        if options.LANGUAGE == "en":
            valeur += self.en.get(cle, 0)
        return valeur

OFFSET_Y_TEXTE = _OffsetLangue({
    "principal": -10,
    "jouer": -10,
    "sauvegardes": -10,
    "hitboxes": -10,
    "entrees": -7,
    "reglages": -7,
    "valeurs": -7,
    "echap": -9,
    "mort": -6,
    "hardcore": -7,
    "hardsel": -7,
    "reglages_boutons": -5,
    "keys_menu": -5
}, en={
    # delta ANGLAIS ajoute a la valeur ci-dessus (0 = identique au francais)
    "principal": 0, "jouer": 0, "sauvegardes": 0, "hitboxes": 0,
    "entrees": 0, "reglages": 0, "valeurs": 0, "echap": 0, "mort": 0,
    "hardcore": 0, "hardsel": 0, "reglages_boutons": 0, "keys_menu": 0
})

OFFSET_X_TEXTE = _OffsetLangue({
    "principal": 0,
    "jouer": 0,
    "dev": +10,
    "sauvegardes": 0,
    "hitboxes": +5,
    "entrees": 0,
    "reglages": 0,
    "valeurs": +5,
    "echap": +9,
    "mort": 0,
    "hardcore": +12,
    "hardsel": +15,
    "reglages_boutons": 20,
    "language": 5,
    "keys_menu": +10,
}, en={
    "principal": 0, "jouer": 0, "dev": 0, "sauvegardes": 0, "hitboxes": 0,
    "entrees": 0, "reglages": 0, "valeurs": 0, "echap": 0, "mort": 5,
    "hardcore": 0, "hardsel": 0, "reglages_boutons": 0, "language": 0, "keys_menu": 0
})
# positions MANUELLES des noms de reglages (texte blanc a gauche des
# barres) : cle = cle de SETTINGS_LIGNES, valeur = (dx, dy) en px
# ecran. Exemple : "or_depart": (6, -2) deplace ce nom de 6 px a
# droite et 2 px vers le haut. Les cles absentes = (0, 0).
OFFSET_REGLAGES = {}

def _label_pnj(screen, texte, rect, scale, survol, corps=0.75, offset_y=0,
               offset_x=0):
    # texte du bouton : lettersC1, lettersC6 au survol (comme le marchand)
    # - centre sur la pilule VISIBLE : le cap gauche garde ~5 px de
    #   transparence a son bord, sans cette correction le texte parait
    #   decale vers la gauche
    # - offset_y / offset_x : reglages fins du texte, une valeur par
    #   taille de bouton (voir OFFSET_Y_TEXTE / OFFSET_X_TEXTE)
    police = fonts.lettersC6 if survol else fonts.lettersC1
    body = max(1, scale * corps)
    marge = int(5 * scale)
    centre_x = (rect.x + marge + (rect.width - marge) // 2
                + int(offset_x))
    fonts.draw_body_text(
        screen, texte,
        centre_x - fonts.get_text_width(texte, body, police) // 2,
        rect.centery - int(3 * body) + int(offset_y),
        rect.width, font_dict=police, scale=body
    )

def _sous_menu_base(screen, fond, titre, alpha=185):
    screen.blit(fond, (0, 0))
    voile = pygame.Surface(screen.get_size())
    voile.set_alpha(alpha)
    voile.fill((8, 8, 14))
    screen.blit(voile, (0, 0))
    _draw_hp_text(screen, titre, screen.get_width() // 2,
                  int(screen.get_height() * 0.10),
                  echelle=4, centered=True, police=fonts.lettersT3)

def lire_slots():
    # contenu resume des 10 slots : dict JSON ou None si vide
    slots = []
    for k in range(1, 11):
        chemin = os.path.join("saves", f"slot_{k}.json")
        try:
            with open(chemin, encoding="utf-8") as f:
                slots.append(json.load(f))
        except (OSError, ValueError):
            slots.append(None)
    return slots

def calculer_boutons_menu_x(screen):
    pass   # (les boutons du menu principal sont plus haut dans le fichier)

def calculer_menu_jouer(screen):
    scale = UI_SCALE
    l, h = dims_barre_pnj(scale)
    l = max(l, largeur_bouton_pour(
        ("AVEC SAUVEGARDE", "SANS SAUVEGARDE", "MODE DEV", "RETOUR"),
        scale))
    cx = screen.get_width() // 2
    y0 = int(screen.get_height() * 0.26)
    pas = h + int(screen.get_height() * 0.05)
    return [(pygame.Rect(cx - l // 2, y0 + i * pas, l, h), a)
            for i, a in enumerate(("sauvegarde", "sans", "dev", "retour"))]

def draw_menu_jouer(screen, boutons, fond):
    _sous_menu_base(screen, fond, "JOUER")
    survol = pygame.mouse.get_pos()
    for rect, action in boutons:
        labels = {"sauvegarde": tr("WITH SAVE"), "sans": tr("WITHOUT SAVE"),
                  "dev": tr("DEV MODE"), "retour": tr("BACK")}
        dessiner_barre_pnj(screen, rect.x, rect.y, UI_SCALE, rect.width)
        _label_pnj(screen, labels[action], rect, UI_SCALE,
                   rect.collidepoint(survol),
                   offset_y=OFFSET_Y_TEXTE["jouer"],
                   offset_x=OFFSET_X_TEXTE["jouer"])

def calculer_menu_sauvegardes(screen):
    scale = UI_SCALE * 0.85
    l, h = dims_barre_pnj(scale)
    slots = lire_slots()
    labels = [f"SLOT {k} - VIDE" if slots[k - 1] is None else
              f"SLOT {k} - NIV {slots[k - 1].get('niveau', '?')}"
              for k in range(1, 11)]
    labels.append("RETOUR")
    l = max(l, largeur_bouton_pour(labels, scale))
    largeur, hauteur = screen.get_width(), screen.get_height()
    cx = largeur // 2
    ecart = int(24 * UI_SCALE)
    y0 = int(hauteur * 0.14)
    # espacement adapte : les 5 rangees + RETOUR restent dans l'ecran
    dy = min(h + int(5 * UI_SCALE),
             max(h + 4, (int(hauteur * 0.90) - y0 - h) // 5))
    x_gauche = cx - (2 * l + ecart) // 2
    boutons = []
    for k in range(10):
        col, row = k % 2, k // 2
        boutons.append((pygame.Rect(x_gauche + col * (l + ecart),
                                    y0 + row * dy, l, h), ("slot", k + 1)))
    boutons.append((pygame.Rect(cx - l // 2, y0 + 5 * dy, l, h),
                    ("retour", None)))
    return boutons

def draw_menu_sauvegardes(screen, boutons, fond):
    _sous_menu_base(screen, fond, tr("SAUVEGARDES"))
    survol = pygame.mouse.get_pos()
    slots = lire_slots()
    scale = UI_SCALE * 0.85
    for rect, action in boutons:
        dessiner_barre_pnj(screen, rect.x, rect.y, scale, rect.width)
        survole = rect.collidepoint(survol)
        if action[0] == "retour":
            _label_pnj(screen, tr("RETOUR"), rect, scale, survole,
                       offset_y=OFFSET_Y_TEXTE["sauvegardes"],
                       offset_x=OFFSET_X_TEXTE["sauvegardes"])
            continue
        k = action[1]
        d = slots[k - 1]
        if d:
            label = tr("SLOT {} - NIV {}").format(
                k, d.get('niveau', '?'))
        else:
            label = tr("SLOT {} - VIDE").format(k)
        _label_pnj(screen, label, rect, scale, survole,
                   offset_y=OFFSET_Y_TEXTE["sauvegardes"],
                   offset_x=OFFSET_X_TEXTE["sauvegardes"])

        _draw_hp_text(screen,
                  tr("POUR SUPPRIMER UNE SAUVEGARDE, SUPPRIME SON FICHIER JSON"),
                  screen.get_width() // 2,
                  screen.get_height() - int(screen.get_height() * 0.03) - 22,
                  echelle=2, centered=True, police=fonts.lettersT3)

def calculer_menu_dev(screen):
    scale = UI_SCALE
    l, h = dims_barre_pnj(scale)
    l = max(l, largeur_bouton_pour(
        ("HITBOXES", "REGLAGES", "JOUER", "RETOUR"), scale))
    cx = screen.get_width() // 2
    y0 = int(screen.get_height() * 0.26)
    pas = h + int(screen.get_height() * 0.05)
    return [(pygame.Rect(cx - l // 2, y0 + i * pas, l, h), a)
            for i, a in enumerate(("hitboxes", "settings", "jouer",
                                   "retour"))]

def draw_menu_dev(screen, boutons, fond):
    _sous_menu_base(screen, fond, tr("MODE DEV"))
    survol = pygame.mouse.get_pos()
    for rect, action in boutons:
        labels = {"hitboxes": tr("HITBOXES"), "settings": tr("REGLAGES"),
                  "jouer": tr("PLAY"), "retour": tr("BACK")}
        dessiner_barre_pnj(screen, rect.x, rect.y, UI_SCALE, rect.width)
        _label_pnj(screen, labels[action], rect, UI_SCALE,
                   rect.collidepoint(survol),
                   offset_y=OFFSET_Y_TEXTE["jouer"],
                   offset_x=OFFSET_X_TEXTE["dev"])

def calculer_menu_hitboxes(screen, config):
    # a gauche : AJOUTER / ENLEVER / RETOUR (grands boutons) ; a droite
    # : les hitboxes en 2 colonnes (8 max par colonne) qui apparaissent
    # au fur et a mesure. Largeur commune par groupe, texte dedans.
    scale = UI_SCALE * 0.85
    l, h = dims_barre_pnj(scale)
    l = max(l, largeur_bouton_pour(("AJOUTER", "ENLEVER", "RETOUR"),
                                   scale))
    largeur, hauteur = screen.get_width(), screen.get_height()
    x_gauche = int(largeur * 0.26) - l // 2
    y0 = int(hauteur * 0.16)
    pas = h + int(4 * UI_SCALE)
    rect_ajouter = pygame.Rect(x_gauche, y0, l, h)
    rect_enlever = pygame.Rect(x_gauche, y0 + pas, l, h)
    rect_retour = pygame.Rect(x_gauche, y0 + 2 * pas, l, h)
    # entrees : grandes barres, texte adapte a la place disponible
    scale_e = UI_SCALE * 0.70
    l_e, h_e = dims_barre_pnj(scale_e)
    corps_e = (0.85 if largeur >= 1200 else
               (0.6 if largeur >= 1000 else 0.5))
    brute = int(max(fonts.get_text_width(t, max(1, scale_e * corps_e),
                                         fonts.lettersC1)
                    for t in HITBOX_TYPES) + 14 * scale_e)
    l_e = max(l_e, largeur_pilule(n_morceaux_pilule(brute, scale_e),
                                  scale_e)) + int(12 * scale_e)
    pas_e = h_e + max(3, int(hauteur * 0.005))
    y0_e = int(hauteur * 0.15)
    x_col1 = min(int(largeur * 0.48),
                 largeur - 14 - 2 * l_e - int(4 * UI_SCALE))
    lignes = []
    for i in range(len(config)):
        col, row = i // 8, i % 8
        lignes.append((pygame.Rect(
            x_col1 + col * (l_e + int(4 * UI_SCALE)),
            y0_e + row * pas_e, l_e, h_e), i))
    return lignes, rect_ajouter, rect_enlever, rect_retour

def rect_pastille_hitbox(rect):
    # pastille de couleur a droite d'une ligne de hitbox
    cote = max(12, int(rect.h * 0.5))
    return pygame.Rect(rect.right - cote - int(4 * UI_SCALE),
                       rect.centery - cote // 2, cote, cote)

def draw_menu_hitboxes(screen, fond, config):
    _sous_menu_base(screen, fond, tr("HITBOXES"))
    _draw_hp_text(screen, "F1 POUR AFFICHER EN JEU - MAX 15",
                  screen.get_width() // 2,
                  max(int(screen.get_height() * 0.135),
                      int(screen.get_height() * 0.10) + 40),
                  echelle=2, centered=True, police=fonts.lettersT4)
    lignes, rect_ajouter, rect_enlever, rect_retour = \
        calculer_menu_hitboxes(screen, config)
    survol = pygame.mouse.get_pos()
    scale = UI_SCALE * 0.85
    scale_e = UI_SCALE * 0.70
    corps_e = (0.85 if screen.get_width() >= 1200 else
               (0.6 if screen.get_width() >= 1000 else 0.5))
    # boutons de base a gauche
    for rect, label in ((rect_ajouter, "AJOUTER"),
                        (rect_enlever, "ENLEVER"),
                        (rect_retour, "RETOUR")):
        dessiner_barre_pnj(screen, rect.x, rect.y, scale, rect.width)
        _label_pnj(screen, label, rect, scale,
                   rect.collidepoint(survol),
                   offset_y=OFFSET_Y_TEXTE["hitboxes"],
                   offset_x=OFFSET_X_TEXTE["hitboxes"])
    # entrees a droite (noms lisibles, pastille a droite)
    for rect, i in lignes:
        entree = config[i]
        dessiner_barre_pnj(screen, rect.x, rect.y, scale_e, rect.width)
        pastille = rect_pastille_hitbox(rect)
        pygame.draw.rect(screen, HITBOX_COULEURS[entree["couleur"]], pastille)
        pygame.draw.rect(screen, (18, 20, 28), pastille, 2)
        zone = pygame.Rect(rect.x, rect.y,
                           rect.width - pastille.width - int(6 * UI_SCALE),
                           rect.h)
        _label_pnj(screen, HITBOX_TYPES[entree["type"]], zone, scale_e,
                   zone.collidepoint(survol), corps_e,
                   offset_y=OFFSET_Y_TEXTE["entrees"],
                   offset_x=OFFSET_X_TEXTE["entrees"])

def _valeur_texte(cle, val):
    if isinstance(val, bool):
        return "ON" if val else "OFF"
    if cle == "lieu":
        return tr(NOMS_LIEUX.get(val, val))
    if "pct" in cle:
        return f"{val} %"
    return str(val)

def calculer_menu_settings(screen):
    # barres "- valeur +" cote droit, labels a leur gauche ; largeur de
    # barre commune calculee sur les valeurs les plus larges possibles.
    # Boutons AGRANDIS : la hauteur des barres prend tout l'ecran
    # disponible pour les 11 lignes + RETOUR/JOUER.
    largeur = screen.get_width()
    hauteur = screen.get_height()
    y0 = int(hauteur * 0.15)
    h = min(int(17 * UI_SCALE * 0.73),
            max(24, (int(hauteur * 0.84) - y0 - int(8 * UI_SCALE))
                // len(SETTINGS_LIGNES) - 1))
    scale = h / 17.0
    body = max(1, scale * 0.75)
    echantillons = []
    for cle, _lab, _pas, mini, maxi, genre in SETTINGS_LIGNES:
        if genre == "cycle":
            echantillons.append(max(NOMS_LIEUX.values(), key=len))
        elif genre == "onoff":
            echantillons.append("OFF")
        else:
            echantillons.append(str(maxi))
    brute = int(max(fonts.get_text_width("- " + e + " +", body,
                                         fonts.lettersC1)
                    for e in echantillons) + 12 * scale)
    l = max(dims_barre_pnj(scale)[0],
            largeur_pilule(n_morceaux_pilule(brute, scale), scale))
    x_barre = int(largeur * 0.66) - l // 2
    dy = h + max(4, int(hauteur * 0.012))
    if y0 + len(SETTINGS_LIGNES) * dy + h > int(hauteur * 0.90):
        dy = max(h + 3, (int(hauteur * 0.90) - y0 - h)
                 // len(SETTINGS_LIGNES))
    lignes = [(pygame.Rect(x_barre, y0 + i * dy, l, h), cle)
              for i, (cle, *_rest) in enumerate(SETTINGS_LIGNES)]
    y_boutons = y0 + len(SETTINGS_LIGNES) * dy + int(2 * UI_SCALE)
    rect_retour = pygame.Rect(largeur // 2 - l // 2, y_boutons, l, h)
    return lignes, rect_retour

def _zone_plus_moins(rect, cle, valeur, scale=None):
    # rectangles cliquables des symboles - et + d'une ligne de reglage
    # (l'echelle se deduit de la hauteur de la barre : jamais decalée).
    # Le "-" et le "+" sont a EGALE distance du texte des deux cotes.
    scale = scale or (rect.h / 17.0)
    body = max(1, scale * 0.75)
    police = fonts.lettersC1
    vt = _valeur_texte(cle, valeur)
    l_m = fonts.get_text_width("-", body, police)
    l_v = fonts.get_text_width(vt, body, police)
    l_p = fonts.get_text_width("+", body, police)
    g = int(6 * scale / 3)
    total = l_m + g + l_v + g + l_p
    xs = rect.centerx - total // 2
    y = rect.centery - int(3 * body)
    haut = int(9 * body)
    # le glyphe "-" occupe [xs, xs+l_m], la valeur commence a g apres ;
    # le glyphe "+" commence a g apres la fin de la valeur : les deux
    # symboles sont a EGALE distance visuelle du texte
    rm = pygame.Rect(xs - g, y, l_m + 2 * g, haut)
    rp = pygame.Rect(rm.right + l_v, y, l_p + 2 * g, haut)
    return rm, rp

def draw_menu_settings(screen, fond, reglages):
    _sous_menu_base(screen, fond, tr("SETTINGS"))
    lignes, rect_retour = calculer_menu_settings(screen)
    survol = pygame.mouse.get_pos()
    scale = lignes[0][0].h / 17.0
    body = max(1, scale * 0.75)
    for rect, cle in lignes:
        dessiner_barre_pnj(screen, rect.x, rect.y, scale, rect.width)
        definition = next(d for d in SETTINGS_LIGNES if d[0] == cle)
        label = tr(definition[1])
        
                # nom du reglage en BLANC (planche T3) et aligne : tous les
        # noms se terminent a la meme x, juste a gauche des barres ;
        # OFFSET_REGLAGES[cle] = (dx, dy) pour ajuster ligne par ligne
        dx_l, dy_l = OFFSET_REGLAGES.get(cle, (0, 0))
        lx = (rect.x - 14 - fonts.get_text_width(label, 2, fonts.lettersT3)
              + dx_l)
        fonts.draw_line(screen, label, lx, rect.centery - 9 + dy_l,
                        scale=2, font_dict=fonts.lettersT3)
        rm, rp = _zone_plus_moins(rect, cle, reglages[cle])
        survole_v = rm.collidepoint(survol) or rp.collidepoint(survol)
        police_v = fonts.lettersC6 if survole_v else fonts.lettersC1
        vt = _valeur_texte(cle, reglages[cle])
        ox_v = int(OFFSET_X_TEXTE["valeurs"])
        oy_v = int(OFFSET_Y_TEXTE["valeurs"])
        fonts.draw_body_text(
            screen, "-", rm.centerx - fonts.get_text_width("-", body, police_v) // 2 + ox_v,
            rm.y + oy_v, rect.width, font_dict=police_v, scale=body)
        fonts.draw_body_text(
            screen, vt, rm.right + ox_v, rp.y + oy_v, rect.width,
            font_dict=police_v, scale=body)
        fonts.draw_body_text(
            screen, "+", rp.centerx - fonts.get_text_width("+", body, police_v) // 2 + ox_v,
            rp.y + oy_v, rect.width, font_dict=police_v, scale=body)
    dessiner_barre_pnj(screen, rect_retour.x, rect_retour.y, scale,
                       rect_retour.width)
    _label_pnj(screen, "RETOUR", rect_retour, scale,
               rect_retour.collidepoint(survol),
               offset_y=OFFSET_Y_TEXTE["reglages"],
               offset_x=OFFSET_X_TEXTE["reglages"])

# ---------- MENU ECHAP IN-GAME ----------
# panneau qui glisse depuis la gauche ; le jeu continue
# derriere (aucun freeze). 4 positions de boutons : CONTINUER
# tout en haut, QUITTER tout en bas, 2 slots RESERVES au milieu
# pour de futurs boutons (actions None = ni dessines ni cliquables).
ETATS_COULEURS = {"wave": (255, 90, 90), "shop": (255, 210, 0),
                  "house": (130, 200, 255), "chapel": (200, 160, 255)}
ECHAP_DUREE = 250   # ms d'animation d'entree / sortie

def _texte_teinte(surface, texte, cx, cy, echelle, couleur, police,
                  alpha=255):
    # jumeau de _draw_hp_text (MEME metrique : glyphe 7*e,
    # ecart e, slash special, y = cy - haut // 2) mais teinte a
    # la couleur demandee ; alpha optionnel pour les fondus
    texte = tr(texte)
    haut = 9 * echelle
    slash_largeur = 4 * echelle
    largeur = 0
    for char in texte:
        if char == "/":
            largeur += slash_largeur
        elif char in police:
            largeur += 7 * echelle
        largeur += echelle
    largeur -= echelle
    pad = 2
    temp = pygame.Surface((int(largeur) + 2 * pad,
                           int(haut) + 2 * pad),
                          pygame.SRCALPHA).convert_alpha()
    x, y = pad, pad
    for char in texte:
        if char == "/":
            pygame.draw.line(temp, (255, 255, 255),
                             (x, y + haut - 1),
                             (x + slash_largeur - echelle, y + 1),
                             echelle)
            x += slash_largeur + echelle
        elif char in police:
            sprite = pygame.transform.scale(police[char],
                                            (7 * echelle, haut))
            temp.blit(sprite, (x, y))
            x += 7 * echelle + echelle
    temp.fill(couleur, special_flags=pygame.BLEND_RGBA_MULT)
    if alpha < 255:
        temp.set_alpha(alpha)
    surface.blit(temp, (cx - largeur // 2 - pad,
                        cy - haut // 2 - pad))

# --- mode HARDCORE : les polices blanches du jeu, du mini-menu
# et du chargement deviennent rouge sang (noires sur fond rouge)
MODE_HARDCORE = False
ROUGE_SANG = (186, 18, 18)
# police de l'ecran de mort : Text7.png (meme grille que Text3),
# repli sur Text3 si le fichier est absent
POLICE_MORT = None   # construite au 1er appel (apres load_font)

def police_mort():
    # police de l'ecran de mort : Text7.png (meme grille que
    # Text3), repli sur Text3 si le fichier est absent
    global POLICE_MORT
    if POLICE_MORT is None:
        if os.path.exists("Text7.png"):
            feuille = pygame.image.load("Text7.png").convert_alpha()
            POLICE_MORT = fonts.build_title_font(feuille, 0.0)
        else:
            POLICE_MORT = fonts.lettersT3
    return POLICE_MORT

def texte_titre_hc(screen, texte, x, y, echelle, police,
                   fond_rouge=False):
    # gros texte blanc du jeu ; en hardcore il devient rouge sang
    # (noir s'il est pose sur un fond rouge)
    if not MODE_HARDCORE:
        _draw_hp_text(screen, texte, x, y, echelle=echelle,
                      centered=True, police=police)
        return
    coul = (0, 0, 0) if fond_rouge else ROUGE_SANG
    _texte_teinte(screen, texte, x, y, echelle, coul, police) 

def rect_panneau_echap(screen):
    # panneau lateral gauche ; sa largeur depend du plus long
    # bouton (CONTINUER)
    scale = UI_SCALE * 0.8
    l_b = largeur_bouton_pour(("CONTINUER", "REGLAGES", "QUITTER"), scale)
    marge = int(26 * scale)
    return pygame.Rect(0, 0, l_b + 2 * marge, screen.get_height())

def calculer_menu_echap(screen):
    # les 4 positions de boutons du panneau (coordonnees ecran
    # du panneau DEPLOYE ; l'animation ne deplace que le blit).
    # CONTINUER et REGLAGES sont COLLES en haut ; le slot 3 reste
    # reserve pour un futur bouton ; QUITTER reste tout en bas.
    scale = UI_SCALE * 0.8
    l_b, h_b = dims_barre_pnj(scale)
    l_b = max(l_b, largeur_bouton_pour(
        ("CONTINUER", "REGLAGES", "QUITTER"), scale))
    panneau = rect_panneau_echap(screen)
    cx_p = panneau.w // 2
    zone_top = int(panneau.h * 0.20)
    zone_bot = panneau.h - int(panneau.h * 0.06) - h_b

    ecart = int(10 * UI_SCALE * 0.8)      # espace entre deux boutons voisins
    pas_haut = h_b + ecart                # distance d'un bouton au suivant
    ys = (zone_top,                       # 0 - CONTINUER
          zone_top + pas_haut,            # 1 - REGLAGES (juste dessous)
          zone_top + 2 * pas_haut,        # 2 - slot reserve
          zone_bot)                       # 3 - QUITTER (tout en bas)

    actions = ("continuer", "reglages", None, "quitter")
    return [(pygame.Rect(cx_p - l_b // 2, ys[i], l_b, h_b), a)
            for i, a in enumerate(actions)]

def dessiner_menu_echap(screen, etat, t_ouverture, t_fermeture=None):
    # dessine le panneau a sa phase d'animation : t_ouverture =
    # pygame.time.get_ticks() a l'ouverture ; pose t_fermeture
    # pour voir le panneau reglisser vers la gauche. Renvoie le
    # rect ecran ACTUEL du panneau (utile pour les clics).
    maintenant = pygame.time.get_ticks()
    if t_fermeture is None:
        p = min(1.0, max(0.0, maintenant - t_ouverture) / ECHAP_DUREE)
        phase = 1.0 - (1.0 - p) ** 3        # ease-out a l'entree
    else:
        p = min(1.0, max(0.0, maintenant - t_fermeture) / ECHAP_DUREE)
        phase = (1.0 - p) ** 2              # ease-in a la sortie
    panneau = rect_panneau_echap(screen)
    x_panneau = int(panneau.w * (phase - 1.0))
    surf = pygame.Surface(panneau.size, pygame.SRCALPHA).convert_alpha()
    surf.fill((8, 8, 14, 235))
    pygame.draw.rect(surf, (96, 122, 106), surf.get_rect(), 2)
    pygame.draw.line(surf, (150, 180, 160), (2, 2), (panneau.w - 3, 2))
    # titre du jeu puis game state harmonise, de sa couleur
    texte_titre_hc(surf, MENU_TITRE, panneau.w // 2,
                   int(panneau.h * 0.05)+18, 4, fonts.lettersT3)
    nom = NOMS_LIEUX.get(etat, str(etat).upper())
    nom = tr(nom)
    _texte_teinte(surf, nom, panneau.w // 2, int(panneau.h * 0.115)+9,
                  2, ETATS_COULEURS.get(etat, (255, 255, 255)),
                  fonts.lettersT3)
    # boutons
    survol = pygame.mouse.get_pos()
    scale = UI_SCALE * 0.8
    labels = {"continuer": tr("CONTINUE"), "reglages": tr("SETTINGS"),
              "quitter": tr("QUIT")}
    for rect, action in calculer_menu_echap(screen):
        if action is None:
            continue
        dessiner_barre_pnj(surf, rect.x, rect.y, scale, rect.width)
        _label_pnj(surf, labels[action], rect, scale,
                   rect.collidepoint(survol),
                   offset_y=OFFSET_Y_TEXTE["echap"],
                   offset_x=OFFSET_X_TEXTE["echap"])
    screen.blit(surf, (x_panneau, 0))
    return pygame.Rect(x_panneau, 0, panneau.w, panneau.h) 

# ---------- MINI-MENU HARDCORE (sans sauvegarde) ----------
# ---------- MINI-MENU HARDCORE (sans sauvegarde) ----------
# simple : titre MODE HARDCORE, puis 3 boutons centres
# (barre - ON/OFF +, JOUER, QUITTER)
def calculer_menu_hardcore(screen):
    scale = UI_SCALE * 0.8
    l_b, h_b = dims_barre_pnj(scale)
    l_b = max(l_b, largeur_bouton_pour(("JOUER", "RETOUR"), scale))
    l_barre, h_barre = dims_barre_pnj(scale)
    cx = screen.get_width() // 2
    hauteur = screen.get_height()
    rect_barre = pygame.Rect(cx - l_barre // 2,
                             int(hauteur * 0.34), l_barre, h_barre)
    y_b = int(hauteur * 0.48)
    rect_jouer = pygame.Rect(cx - l_b // 2, y_b, l_b, h_b)
    rect_quitter = pygame.Rect(cx - l_b // 2,
                               y_b + h_b + int(16 * UI_SCALE),
                               l_b, h_b)
    return rect_barre, rect_jouer, rect_quitter

def draw_menu_hardcore(screen, fond, reglages):
    _sous_menu_base(screen, fond, "MODE HARDCORE")
    rect_barre, rect_jouer, rect_quitter = \
        calculer_menu_hardcore(screen)
    survol = pygame.mouse.get_pos()
    scale_b = rect_barre.h / 17.0
    dessiner_barre_pnj(screen, rect_barre.x, rect_barre.y, scale_b,
                       rect_barre.width)
    vt = _valeur_texte("hardcore", reglages["hardcore"])
    _label_pnj(screen, vt, rect_barre, scale_b,
               rect_barre.collidepoint(survol),
               offset_y=OFFSET_Y_TEXTE["jouer"],
               offset_x=OFFSET_X_TEXTE["jouer"])
    for rect, lab in ((rect_jouer, "JOUER"), (rect_quitter, "RETOUR")):
        dessiner_barre_pnj(screen, rect.x, rect.y, UI_SCALE * 0.8,
                           rect.width)
        _label_pnj(screen, lab, rect, UI_SCALE * 0.8,
                   rect.collidepoint(survol),
                   offset_y=OFFSET_Y_TEXTE["hardcore"],
                   offset_x=OFFSET_X_TEXTE["hardcore"])

# ---------- MENU REGLAGES (musique/sons/langues/touches) ----------
OFFSET_BOUTONS_REGLAGES = {"musique": (-20, 0), "sons": (-20, 0),
                           "langues": (-20, 0), "touches": (-20, 0),
                           "retour": (-20, 0)}

def calculer_menu_reglages(screen):
    # 5 elements empiles et centres : barre MUSIQUE, barre SONS,
    # LANGUES, TOUCHES, RETOUR
    scale = UI_SCALE * 0.8
    l_b, h_b = dims_barre_pnj(scale)
    l_b = max(l_b, largeur_bouton_pour(
        ("MUSIQUE : OFF", "SONS : OFF", "LANGUES", "TOUCHES",
         "RETOUR"), scale))
    cx = screen.get_width() // 2
    h = screen.get_height()
    cles = ("musique", "sons", "langues", "touches", "retour")
    positions = (0.32, 0.42, 0.53, 0.61, 0.72)
    boutons = []
    for cle, p in zip(cles, positions):
        dx, dy = OFFSET_BOUTONS_REGLAGES[cle]
        boutons.append(pygame.Rect(cx - l_b // 2 + dx,
                                   int(h * p) + dy, l_b, h_b))
    return boutons

def draw_menu_reglages(screen, fond):
    _sous_menu_base(screen, fond, tr("SETTINGS"))
    rect_mus, rect_sons, rect_lng, rect_tch, rect_ret = \
        calculer_menu_reglages(screen)
    survol = pygame.mouse.get_pos()
    scale_b = rect_mus.h / 17.0
    txt_mus = f"{tr('MUSIC')} : {tr('ON') if options.MUSIC_ON else tr('OFF')}"
    txt_sons = f"{tr('SOUND')} : {tr('ON') if options.SFX_ON else tr('OFF')}"
    for rect, texte in ((rect_mus, txt_mus), (rect_sons, txt_sons),
                        (rect_lng, tr("LANGUAGES")),
                        (rect_tch, tr("KEYS")),
                        (rect_ret, tr("BACK"))):
        dessiner_barre_pnj(screen, rect.x, rect.y, scale_b,
                           rect.width)
        _label_pnj(screen, texte, rect, scale_b,
                   rect.collidepoint(survol),
                   offset_y=OFFSET_Y_TEXTE["reglages_boutons"],
                   offset_x=OFFSET_X_TEXTE["reglages_boutons"])

# ---------- MENU LANGUES ----------
def calculer_menu_langues(screen):
    # boutons FRANCAIS / ENGLISH + RETOUR ; le texte "langue
    # actuelle" est dessine par draw_menu_langues
    scale = UI_SCALE * 0.8
    l_b, h_b = dims_barre_pnj(scale)
    l_b = max(l_b, largeur_bouton_pour(("FRANCAIS", "ENGLISH"),
                                       scale))
    cx = screen.get_width() // 2
    h = screen.get_height()
    return (pygame.Rect(cx - l_b // 2, int(h * 0.45), l_b, h_b),
            pygame.Rect(cx - l_b // 2, int(h * 0.55), l_b, h_b),
            pygame.Rect(cx - l_b // 2, int(h * 0.70), l_b, h_b))

def draw_menu_langues(screen, fond):
    _sous_menu_base(screen, fond, tr("LANGUAGES"))
    rect_fr, rect_en, rect_ret = calculer_menu_langues(screen)
    survol = pygame.mouse.get_pos()
    nom = "FRANCAIS" if options.LANGUAGE == "fr" else "ENGLISH"
    _draw_hp_text(screen, tr("GAME LANGUAGE: {}").format(nom),
                  screen.get_width() // 2,
                  int(screen.get_height() * 0.30), echelle=3,
                  centered=True, police=fonts.lettersT3)
    scale_b = rect_fr.h / 17.0
    for rect, texte in ((rect_fr, "FRANCAIS"), (rect_en, "ENGLISH"),
                        (rect_ret, tr("BACK"))):
        dessiner_barre_pnj(screen, rect.x, rect.y, scale_b,
                           rect.width)
        _label_pnj(screen, texte, rect, scale_b,
                   rect.collidepoint(survol),
                   offset_y=OFFSET_Y_TEXTE["jouer"],
                   offset_x=OFFSET_X_TEXTE["language"])

# ---------- MENU TOUCHES (re-mappage clavier) ----------
LABELS_ACTIONS = {"gauche": "LEFT", "droite": "RIGHT",
                  "haut": "UP", "bas": "DOWN",
                  "interaction": "INTERACT", "attaque": "ATTACK",
                  "mute": "MUTE"}

def calculer_menu_touches(screen):
    # lignes (action, rect_touche, rect_changer) + REINITIALISER +
    # RETOUR en bas
    scale_pet = UI_SCALE * 0.55
    _l_pet, h_pet = dims_barre_pnj(scale_pet)
    cx = screen.get_width() // 2
    h = screen.get_height()
    lignes = []
    for i, action in enumerate(options.KEY_ORDER):
        y = int(h * 0.20) + i * int(h * 0.062)
        rect_touche = pygame.Rect(cx - int(h * 0.09), y,
                                  int(h * 0.18), h_pet)
        rect_changer = pygame.Rect(cx + int(h * 0.12), y,
                                   int(h * 0.14), h_pet)
        lignes.append((action, rect_touche, rect_changer))
    scale_bas = UI_SCALE * 0.8
    l_b, h_b = dims_barre_pnj(scale_bas)
    l_b = max(l_b, largeur_bouton_pour(("REINITIALISER", "RETOUR"),
                                       scale_bas))
    rect_reset = pygame.Rect(cx - l_b // 2, int(h * 0.72), l_b, h_b)
    rect_ret = pygame.Rect(cx - l_b // 2, int(h * 0.81), l_b, h_b)
    return lignes, rect_reset, rect_ret

def draw_menu_touches(screen, fond, capture_action=None):
    _sous_menu_base(screen, fond, tr("KEYS"))
    lignes, rect_reset, rect_ret = calculer_menu_touches(screen)
    survol = pygame.mouse.get_pos()
    conflits = options.key_conflicts()
    h = screen.get_height()
    scale_pet = UI_SCALE * 0.55
    for action, rect_touche, rect_changer in lignes:
        # nom de l'action, a gauche de la ligne
        _draw_hp_text(screen, tr(LABELS_ACTIONS[action]),
                      rect_touche.x - int(h * 0.06),
                      rect_touche.centery, echelle=2, centered=True,
                      police=fonts.lettersT3)
        # pilule de la touche actuelle (ou de la capture en cours)
        dessiner_barre_pnj(screen, rect_touche.x, rect_touche.y,
                           scale_pet, rect_touche.width)
        if capture_action == action:
            txt = tr("PRESS ANY KEY...")
        elif (action == "attaque"
              and options.KEYS[action] is None):
            txt = tr("LEFT CLICK")
        else:
            txt = options.key_name(options.KEYS[action])
        _label_pnj(screen, txt, rect_touche, scale_pet, False,
                   offset_y=OFFSET_Y_TEXTE["keys_menu"],
                   offset_x=OFFSET_X_TEXTE["keys_menu"])
        # bouton CHANGER
        dessiner_barre_pnj(screen, rect_changer.x, rect_changer.y,
                           scale_pet, rect_changer.width)
        _label_pnj(screen, tr("CHANGE"), rect_changer, scale_pet,
                   rect_changer.collidepoint(survol),
                   offset_y=OFFSET_Y_TEXTE["keys_menu"],
                   offset_x=OFFSET_X_TEXTE["keys_menu"])
        # conflit : 2 "!" jaunes (T4) autour de la touche et du
        # bouton CHANGER
        if (options.KEYS.get(action) is not None
                and options.KEYS[action] in conflits):
            for rect in (rect_touche, rect_changer):
                _draw_hp_text(screen, "!",
                              rect.x - int(rect.h * 0.45),
                              rect.centery, echelle=3, centered=True,
                              police=fonts.lettersT4)
                _draw_hp_text(screen, "!",
                              rect.right + int(rect.h * 0.45),
                              rect.centery, echelle=3, centered=True,
                              police=fonts.lettersT4)
    # bas : REINITIALISER + RETOUR
    for rect, texte in ((rect_reset, tr("RESET")),
                        (rect_ret, tr("BACK"))):
        dessiner_barre_pnj(screen, rect.x, rect.y, UI_SCALE * 0.8,
                           rect.width)
        _label_pnj(screen, texte, rect, UI_SCALE * 0.8,
                   rect.collidepoint(survol),
                   offset_y=OFFSET_Y_TEXTE["keys_menu"],
                   offset_x=OFFSET_X_TEXTE["keys_menu"])
# ---------- ECRAN DE MORT ----------
MORT_DUREE_FONDU = 700   # ms du fondu noir (cote boucle de jeu)

def calculer_menu_mort(screen):
    scale = UI_SCALE * 0.8
    l_b, h_b = dims_barre_pnj(scale)
    l_b = max(l_b, largeur_bouton_pour(("REAPPARAITRE", "QUITTER"),
                                       scale))
    cx = screen.get_width() // 2
    y_b = int(screen.get_height() * 0.60)
    dx_r, dy_r = OFFSET_BOUTONS_MORT["reapparaitre"]
    dx_q, dy_q = OFFSET_BOUTONS_MORT["quitter"]
    return [(pygame.Rect(cx - l_b // 2 + dx_r, y_b + dy_r,
                         l_b, h_b), "reapparaitre"),
            (pygame.Rect(cx - l_b // 2 + dx_q,
                         y_b + h_b + int(16 * UI_SCALE) + dy_q,
                         l_b, h_b), "quitter")]

def _label_mort(screen, texte, cx, cy, scale, couleur):
    # jumeau de _label_pnj pour le menu mort : MEME police que les
    # boutons (lettersC1, corps 0.75) mais teintee, car les glyphes
    # du marchand sont fonces (illisibles sur le fond noir)
    police = fonts.lettersC1
    corps = max(1, scale * 0.75)
    pad = 2
    largeur = int(fonts.get_text_width(texte, corps, police))
    largeur += 2 * pad
    hauteur = int(6 * corps) + 2 * pad
    temp = pygame.Surface((largeur, hauteur),
                          pygame.SRCALPHA).convert_alpha()
    fonts.draw_line(temp, texte, pad, pad, corps, font_dict=police)
    # les glyphes du marchand sont FONCES : on les passe a blanc
    # (addition rgb) AVANT de teinter, sinon la teinte multiplicative
    # ne se voit pas sur du (17, 11, 0)
    temp.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
    temp.fill(couleur, special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(temp, (cx - largeur // 2, cy - hauteur // 2))

def draw_menu_mort(screen, t_mort, niveau, vague):
    # fond noir, puis VOUS ETES MORT + niveau/vague + boutons :
    # textes avec _label_mort (police du marchand), comme les boutons
    t = pygame.time.get_ticks() - t_mort
    screen.fill((0, 0, 0))
    if t <= MORT_DUREE_FONDU:
        return
    w, h = screen.get_width(), screen.get_height()
    # titre a h*0.24 (ROUGE SANG en hardcore), info a h*0.38,
    # tous les deux avec la police du marchand (_label_mort)
    coul_titre = ROUGE_SANG if MODE_HARDCORE else (255, 255, 255)
    _label_mort(screen, tr("YOU ARE DEAD"), w // 2, int(h * 0.24),
                12, coul_titre)
    _label_mort(screen, f"{tr('LVL')} {niveau} {tr('WAVE')} {vague}", w // 2,
                int(h * 0.38), 6, (255, 255, 255))
    survol = pygame.mouse.get_pos()
    labels = {"reapparaitre": tr("RESPAWN"), "quitter": tr("QUIT")}
    for rect, action in calculer_menu_mort(screen):
        dessiner_barre_pnj(screen, rect.x, rect.y, UI_SCALE * 0.8,
                           rect.width)
        _label_pnj(screen, labels[action], rect, UI_SCALE * 0.8,
                   rect.collidepoint(survol),
                   offset_y=OFFSET_Y_TEXTE["mort"],
                   offset_x=OFFSET_X_TEXTE["mort"])