import pygame
import math
import random
import os
import json

from classes import Player
from fonts import *
import fonts
import dialogues
import options
from options import tr
from settings import *

pygame.init()

health_font = pygame.font.SysFont("Ebrima", 20, bold=True)

# ------------------------------------------------------------
# PIXEL-ART BAR FRAMES (Health_bar.png / Xp_bar.png)
# Each frame is loaded ONCE, cropped to its usable strip and then
# scaled WITHOUT smoothing (scale_by = crisp square pixels).
# The fill (red/green HP, blue XP) is drawn BEHIND the frame: we
# only paint the inner TRANSPARENT pixels (detected once and for
# all), so the frame itself stays untouched.
# ------------------------------------------------------------
BAR_SCALE = 5        # pixel density shared by both bars
HP_BAR_POS = (20, 20)   # health bar, top left
XP_BAR_POS = (20, 89)   # xp bar, right below the HP bar


def _transparent_runs(surface, y):
    # List of [x0, x1] runs of transparent pixels on row y.
    width = surface.get_width()
    runs, current = [], None
    for x in range(width):
        if surface.get_at((x, y))[3] == 0:
            current = [x, x] if current is None else [current[0], x]
        else:
            if current:
                runs.append(current)
                current = None
    if current:
        runs.append(current)
    return runs


def _prepare_bar(path, y0, y1):
    # Load the PNG, keep the strip (0, y0) -> (width, y1), detect
    # the inner windows (transparent runs surrounded by opaque
    # pixels on both sides) and return (zone, spans, scaled frame).
    img = pygame.image.load(path).convert_alpha()
    zone = img.subsurface((0, y0, img.get_width(), y1 - y0))
    spans = {}
    for y in range(zone.get_height()):
        # a run touching the strip edge is not a fillable window
        spans[y] = [tuple(r) for r in _transparent_runs(zone, y)
                    if r[0] > 0 and r[1] < zone.get_width() - 1]
    frame = pygame.transform.scale_by(zone, BAR_SCALE)
    return zone, spans, frame


HP_ZONE, HP_SPANS, HP_CADRE = _prepare_bar("Health_bar.png", 26, 38)
XP_ZONE, XP_SPANS, XP_CADRE = _prepare_bar("Xp_bar.png", 0, 6)


def _window_center(spans):
    # (x, y) center of the largest fill window (for the text).
    ys = [y for y, runs in spans.items()
          if any(r[1] - r[0] + 1 >= 30 for r in runs)]
    best = max((r for y in ys for r in spans[y]),
               key=lambda r: r[1] - r[0])
    return ((best[0] + best[1] + 1) / 2,
            (min(ys) + max(ys) + 1) / 2)


HP_CENTRE = _window_center(HP_SPANS)

_BARRES_CACHE = {}   # (zone, rounded ratio, colors) -> ready surface


def _bar_fill(zone, spans, ratio, back_color, fill_color):
    # The bar only changes when the ratio moves: cache the rendered
    # surface and rebuild it only then.
    key = (id(zone), round(ratio, 3), back_color, fill_color)
    cached = _BARRES_CACHE.get(key)
    if cached is not None:
        return cached
    # One long bevel-cut rectangle instead of filling every window:
    # background and gauge are drawn as single lines 1 px WIDER than
    # the window, and the opaque frame covers the surplus (the fill
    # therefore passes UNDER the frame's bevelled edge).
    surf = zone.copy()
    rows = [(y, runs[0]) for y, runs in sorted(spans.items()) if runs]
    if rows:
        left = min(r[0] for _, r in rows)
        y_ref, r_ref = max(rows, key=lambda t: t[1][1])
        right_max = r_ref[1]
        total = right_max - left + 1
        limit = left + int(total * ratio)   # vertical edge of the gauge
        for y, _ in rows:
            right = right_max - (y - y_ref) + 1   # bevel parallel to frame
            pygame.draw.line(surf, back_color, (left, y), (right, y))
            if limit > left:
                pygame.draw.line(surf, fill_color, (left, y),
                                 (min(right, limit - 1), y))
    surf = pygame.transform.scale_by(surf, BAR_SCALE)
    if len(_BARRES_CACHE) > 64:
        _BARRES_CACHE.clear()
    _BARRES_CACHE[key] = surf
    return surf


_GLYPHE_CACHE = {}   # (font dict, character, scale) -> ready sprite
HP_TEXT_SCALE = 2    # 7x9 Text3 digits scaled x2 (~18 px tall)


def _draw_hp_text(screen, text, cx, cy, scale=None, centered=True,
                  font_dict=None, slash_color=None):
    text = tr(text)
    # "X/Y" centered on (cx, cy): white digits from Text3 (title
    # sheet, same grid as Text1) plus a hand-drawn white slash (the
    # sheet has no "/" glyph).
    if scale is None:
        scale = HP_TEXT_SCALE
    if font_dict is None:
        font_dict = fonts.lettersT3
    if slash_color is None:
        slash_color = (255, 255, 255)
    height = 9 * scale
    slash_width = 4 * scale
    width = 0
    for char in text:
        if char == "/":
            width += slash_width
        elif char in font_dict:
            width += 7 * scale
        width += scale                       # small gap
    width -= scale
    x = cx - width // 2 if centered else cx
    y = cy - height // 2
    for char in text:
        if char == "/":
            pygame.draw.line(screen, slash_color,
                             (x, y + height - 1),
                             (x + slash_width - scale, y + 1), scale)
            x += slash_width + scale
        elif char in font_dict:
            # Scaled glyphs are CACHED: transform.scale per character
            # per frame was a real bottleneck in the HUD.
            key = (id(font_dict), char, scale)
            sprite = _GLYPHE_CACHE.get(key)
            if sprite is None:
                sprite = pygame.transform.scale(
                    font_dict[char], (7 * scale, height))
                _GLYPHE_CACHE[key] = sprite
            screen.blit(sprite, (x, y))
            x += 7 * scale + scale


def draw_health(screen, player):
    health_ratio = max(0, min(1, player.hp / player.max_hp))

    # Red background then green gauge BEHIND the iron pixel frame.
    fill = _bar_fill(HP_ZONE, HP_SPANS, health_ratio,
                     (255, 0, 0), (0, 255, 50))
    screen.blit(fill, HP_BAR_POS)
    screen.blit(HP_CADRE, HP_BAR_POS)
    # current/max HP shown in white ON the bar window (green or red)
    # without resizing it. Works for every heal (potion, golden
    # apple, healer) because everything goes through player.hp/max_hp.
    cx = HP_BAR_POS[0] + 3 + int(HP_CENTRE[0] * BAR_SCALE)
    cy = HP_BAR_POS[1] + int(HP_CENTRE[1] * BAR_SCALE)
    _draw_hp_text(screen, f"{int(player.hp)}/{int(player.max_hp)}",
                  cx, cy)


def draw_level(screen, current_level, current_wave, game_state):
    # LEVEL X in white T3, then SHOP in T6 or WAVE X / 3 in yellow T4.
    draw_title_text(screen, f"{tr('LEVEL')} {current_level}",
                    screen.get_width() // 2, 30, 3, fonts.lettersT3)
    if game_state == "shop" or game_state == "house":
        _draw_hp_text(screen, "SHOP",
                      screen.get_width() // 2, 64,
                      scale=3, centered=True, font_dict=fonts.lettersT6)
    else:
        _draw_hp_text(screen, f"{tr('WAVE')} {current_wave} / 3",
                      screen.get_width() // 2, 64,
                      scale=3, centered=True,
                      font_dict=fonts.lettersT4,
                      slash_color=(244, 219, 0))


_OVERLAY_TRANSITION = None


def draw_transition(screen, transition, current_level, current_wave,
                    game_state):
    if not transition:
        return

    # Full-screen Surface allocation EVERY frame is expensive:
    # build the overlay once and reuse it.
    global _OVERLAY_TRANSITION
    if _OVERLAY_TRANSITION is None:
        _OVERLAY_TRANSITION = pygame.Surface(
            screen.get_size()).convert()
        _OVERLAY_TRANSITION.fill((0, 0, 0))
    _OVERLAY_TRANSITION.set_alpha(150)
    screen.blit(_OVERLAY_TRANSITION, (0, 0))

    draw_title_text(screen, f"{tr('LEVEL')} {current_level}",
                    screen.get_width() // 2, 240, 4, fonts.lettersT3)
    if game_state == "shop":
        _draw_hp_text(screen, "SHOP",
                      screen.get_width() // 2, 290,
                      scale=4, centered=True, font_dict=fonts.lettersT6)
    else:
        _draw_hp_text(screen, f"{tr('WAVE')} {current_wave}",
                      screen.get_width() // 2, 290,
                      scale=4, centered=True, font_dict=fonts.lettersT4)


def draw_coins(screen, player):
    # "COINS: N" fully in yellow: letters and digits from Text4.
    _draw_hp_text(screen, f"{tr('COINS:')} {player.coins}", 20, 135,
                  scale=2, centered=False, font_dict=fonts.lettersT4)


def draw_xp_bar(screen, player):
    # XP bar: UNDER the HP bar, ABOVE the coins. Shorter and thinner
    # than the health bar, blue like the orbs. The level counter is
    # shown in the middle of the bar.
    ratio = max(0, min(1, player.xp / player.xp_required()))

    # Dark background then blue gauge BEHIND the iron pixel frame.
    fill = _bar_fill(XP_ZONE, XP_SPANS, ratio,
                     (30, 30, 45), XP_ORB_COLOR)
    screen.blit(fill, XP_BAR_POS)
    screen.blit(XP_CADRE, XP_BAR_POS)

    # XP level in white Text3 digits, centered on the bar.
    _draw_hp_text(screen, str(player.xp_level),
                  XP_BAR_POS[0] + XP_CADRE.get_width() // 2,
                  XP_BAR_POS[1] + XP_CADRE.get_height() // 2,
                  scale=2)


def draw_player_level(screen, player):
    # "SKILLS: LVL X" fully in pixel-art Text5 (no accented letters:
    # the title sheet has none).
    _draw_hp_text(screen, tr("SKILLS: LVL {}").format(player.level),
                  20, 169, scale=2, centered=False,
                  font_dict=fonts.lettersT5)


def draw_hotbar(screen, player):
    slot_size = 64
    spacing = 8

    start_x = 15
    y = screen.get_height() - 74

    for i in range(player.inventory_slots):
        color = (255, 255, 0) if i == player.selected_slot \
            else (255, 255, 255)
        pygame.draw.rect(
            screen, color,
            (start_x + i * (slot_size + spacing), y, slot_size,
             slot_size), 3)


def draw_portal_indicator(screen, portal_rect, camera_x, camera_y,
                          game_state):
    # In the shop, point at the exit portal with a pulsing dot when
    # the portal is off screen.
    if game_state == "shop" and portal_rect:
        portal_screen_x = portal_rect.centerx - camera_x
        portal_screen_y = portal_rect.centery - camera_y

        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2

        dx = portal_screen_x - center_x
        dy = portal_screen_y - center_y
        distance = math.hypot(dx, dy)

        if (portal_screen_x < 0
                or portal_screen_x > screen.get_width()
                or portal_screen_y < 0
                or portal_screen_y > screen.get_height()):
            dx /= distance
            dy /= distance
            margin = 25
            t = min(
                (center_x - margin) / abs(dx) if dx != 0 else 9999,
                (center_y - margin) / abs(dy) if dy != 0 else 9999)
            indicator_x = center_x + dx * t
            indicator_y = center_y + dy * t

            pulse = math.sin(pygame.time.get_ticks() / 120) * 3
            pygame.draw.circle(screen, (103, 166, 114),
                               (int(indicator_x), int(indicator_y)),
                               int(12 + pulse))
# ---------- MAIN MENU ----------
GAME_TITLE = "PIXSOULS"
_menu_button_sheet = pygame.image.load("Shop.png").convert_alpha()
MENU_CAP_PILL = _menu_button_sheet.subsurface((94, 186, 37, 17))
MENU_EXTEND_PILL = _menu_button_sheet.subsurface((102, 186, 29, 17))


def main_menu_buttons(screen):
    # Buttons identical to the NPC interfaces. All 3 buttons share
    # the SAME width (the widest label, in BOTH languages so the
    # layout never changes with the language) and stay centered.
    scale = UI_SCALE
    _base, height = npc_bar_size(scale)
    cx = screen.get_width() // 2
    y0 = int(screen.get_height() * 0.55)
    buttons = []
    for i, action in enumerate(("jouer", "reglages", "quitter")):
        width = button_width_for(
            ("JOUER", "REGLAGES", "QUIT TER".replace(" ", ""),
             "PLAY", "SETTINGS", "QUIT"), scale)
        buttons.append((pygame.Rect(cx - width // 2,
                                    y0 + i * (height
                                              + int(12 * UI_SCALE)),
                                    width, height), action))
    return buttons


def _draw_menu_button(screen, rect):
    # NPC bar stretched over the whole button width (see
    # draw_npc_bar): the text never overflows the bounds.
    draw_npc_bar(screen, rect.x, rect.y, UI_SCALE, rect.width)


def draw_menu(screen, buttons, background):
    # Pre-rendered game scene + dark veil, PIXSOULS title in T3,
    # then the NPC buttons: lettersC1 text switching to lettersC6
    # on hover (same behavior as the merchant buttons).
    screen.blit(background, (0, 0))
    veil = pygame.Surface(screen.get_size())
    veil.set_alpha(140)
    veil.fill((10, 10, 16))
    screen.blit(veil, (0, 0))
    _draw_hp_text(screen, GAME_TITLE,
                  screen.get_width() // 2, int(screen.get_height() * 0.28),
                  scale=8, centered=True, font_dict=fonts.lettersT3)
    mouse = pygame.mouse.get_pos()
    for rect, action in buttons:
        _draw_menu_button(screen, rect)
        label = (tr("PLAY") if action == "jouer" else
                 tr("SETTINGS") if action == "reglages"
                 else tr("QUIT"))
        _npc_label(screen, label, rect, UI_SCALE,
                   rect.collidepoint(mouse),
                   offset_y=LABEL_OFFSET_Y["main"],
                   offset_x=LABEL_OFFSET_X["main"])


STUDIO_NAME = "SAUCISSON STUDIOS"
INTRO_PHASES_MS = (1200, 900, 1200, 1000)   # fade in, hold,
                                            # fade out, menu reveal

# offsets of the DEATH screen BUTTONS: (dx, dy) per button, in
# screen px

# offsets of the SETTINGS page BUTTONS: (dx, dy) per button, in
# screen px (same principle as the death screen; clicks follow
# because the rects move)
SETTINGS_BUTTON_OFFSETS = {"musique": (-20, 0), "sons": (-20, 0),
                           "langues": (-20, 0), "touches": (-20, 0),
                           "retour": (-20, 0)}
DEATH_BUTTON_OFFSETS = {"reapparaitre": (0, -5), "quitter": (0, -5)}
LANGUAGES_BUTTON_OFFSETS = {"francais": (0, 0), "english": (0, 0),
                            "retour": (0, 0)}
KEYS_BUTTON_OFFSETS = {"reset": (0, 0), "retour": (0, 0)}
KEYS_ROWS_OFFSET = (0, 0)   # (dx, dy) shifts ALL the key rows


def draw_intro(screen, t_ms, buttons, background):
    # Black background, "SAUCISSON STUDIOS" fading in then out,
    # finally the menu revealing itself under a vanishing black
    # veil. Returns True when the intro is over.
    fade_in, hold, fade_out, reveal = INTRO_PHASES_MS
    total_text = fade_in + hold + fade_out
    if t_ms < total_text:
        if t_ms < fade_in:
            alpha = 255 * t_ms // fade_in
        elif t_ms < fade_in + hold:
            alpha = 255
        else:
            alpha = 255 - 255 * (t_ms - fade_in - hold) // fade_out
        screen.fill((0, 0, 0))
        temp = pygame.Surface(screen.get_size(),
                              pygame.SRCALPHA).convert_alpha()
        _draw_hp_text(temp, STUDIO_NAME,
                      screen.get_width() // 2, screen.get_height() // 2,
                      scale=5, centered=True, font_dict=fonts.lettersT3)
        temp.set_alpha(alpha)
        screen.blit(temp, (0, 0))
        return False
    # final phase: the menu appears under the vanishing black
    draw_menu(screen, buttons, background)
    remaining = t_ms - total_text
    if remaining < reveal:
        veil = pygame.Surface(screen.get_size())
        veil.fill((0, 0, 0))
        veil.set_alpha(255 - 255 * remaining // reveal)
        screen.blit(veil, (0, 0))
        return False
    return True


def draw_loading(screen, t_ms, duration):
    # Loading screen: LOADING in white T3 + the pixel-art xp gauge
    # (existing engine) filling up over the duration.
    ratio = min(1.0, t_ms / duration)
    screen.fill((0, 0, 0))
    draw_title_text(screen, "CHARGEMENT",
                    screen.get_width() // 2,
                    screen.get_height() // 2 - 32,
                    4, fonts.lettersT3)
    pos = (screen.get_width() // 2 - XP_CADRE.get_width() // 2,
           screen.get_height() // 2 + 10)
    screen.blit(_bar_fill(XP_ZONE, XP_SPANS, ratio,
                          (30, 30, 45), XP_ORB_COLOR), pos)
    screen.blit(XP_CADRE, pos)

# ---------- SUBMENUS: PLAY / SAVES / DEV / HITBOXES / DEV SETTINGS ----------
HITBOX_TYPES = ["JOUEUR", "ENNEMIS", "PIECES", "PNJ", "ORBES XP", "PORTAIL",
                "POINTS PNJ", "MEUBLES", "MURS", "DECORS", "PROJECTILES"]
HITBOX_COLORS = [(255, 60, 60), (60, 255, 90), (70, 140, 255),
                 (255, 220, 0), (0, 255, 255), (255, 0, 255),
                 (255, 255, 255), (255, 140, 0), (200, 160, 255),
                 (255, 105, 180), (180, 180, 180)]
SETTINGS_ROWS = [
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
SPAWN_PLACES = ["wave", "shop", "house", "chapel"]
PLACE_NAMES = {"wave": "VAGUES", "shop": "BOUTIQUE",
               "house": "MAISON", "chapel": "CHAPELLE"}

_PILL_STEP = 100.0 / 9.0     # 11.11: no repetition step of a link piece
_PILL_EXT1_X = 200.0 / 9.0   # 22.22: position of the 1st extension
_PILL_EXT2_X = 300.0 / 9.0   # 33.33: position of the 2nd extension
_PILL_LINK_VISIBLE = 23.0    # visible part of a link piece (source px)

# Manual positions of the setting names (white text at the left of
# the bars): key = SETTINGS_ROWS key, value = (dx, dy) in screen
# px. Example: "or_depart": (6, -2) moves that name 6 px right and
# 2 px up. Missing keys = (0, 0).
SETTING_LABEL_OFFSETS = {
    "pommes_pct": (110, 0),
    "pommes_dorees_pct": (110, 0),

}


def pill_pieces_count(width, scale):
    # Number of "link" pieces needed for the visible pill to reach
    # `width` px; 1 = short format (cap + a single piece, main menu
    # buttons), then one more per 11.11 source px step.
    one = int(_PILL_EXT1_X * scale) + int(_PILL_LINK_VISIBLE * scale)
    if width <= one:
        return 1
    step = max(1, int(_PILL_STEP * scale))
    return 1 + int(math.ceil((width - one) / step))


def pill_width(n, scale):
    # VISIBLE width of a pill made of n link pieces.
    step = max(1, int(_PILL_STEP * scale))
    return (int(_PILL_EXT1_X * scale) + (n - 1) * step
            + int(_PILL_LINK_VISIBLE * scale))


def draw_npc_bar(screen, x, y, scale, width=None):
    # Button bar of the NPC interfaces, composed EXACTLY like the
    # merchant bar: left cap + "link" pieces overlapped at a fixed
    # step, each piece hiding the rounded end of the previous one.
    # To lengthen: we ADD pieces, we never stretch the sprite (no
    # visible cut in the middle, ends intact).
    img_left = pygame.transform.scale(
        MENU_CAP_PILL, (int(37 * scale), int(17 * scale)))
    img_link = pygame.transform.scale(
        MENU_EXTEND_PILL, (int(29 * scale), int(17 * scale)))
    o1, o2 = int(_PILL_EXT1_X * scale), int(_PILL_EXT2_X * scale)
    screen.blit(img_left, (x, y))
    if width is None:
        screen.blit(img_link, (x + o1, y))
        screen.blit(img_link, (x + o2, y))
        return
    n = pill_pieces_count(width, scale)
    step = max(1, int(_PILL_STEP * scale))
    screen.blit(img_link, (x + o1, y))
    for k in range(n - 1):
        screen.blit(img_link, (x + o2 + k * step, y))


def npc_bar_size(scale):
    return int(33.33 * scale) + int(29 * scale), int(17 * scale)


def button_width_for(labels, scale):
    # Bar width shared by every button displayed at the same time:
    # the widest label + a margin, rounded to an EXACT pill width
    # (the bar ends exactly on the button edge, no overflow, no
    # shortcut).
    body = max(1, scale * 0.75)
    w = max(fonts.get_text_width(t, body, fonts.lettersC1)
            for t in labels)
    raw = int(w + 14 * scale)
    return pill_width(pill_pieces_count(raw, scale), scale)

# --- vertical text tuning, one entry per button size ---
# the text sits on the vertical center of the bar; put 2 to move
# the text 2 px down on screen, -3 to move it up, etc.
LABEL_OFFSET_Y = {
    "main": -10,          # main menu (UI_SCALE)
    "play": -10,          # PLAY / DEV MODE menu (UI_SCALE)
    "saves": -10,         # save slots (UI_SCALE * 0.85)
    "hitboxes": -10,      # ADD/REMOVE/BACK (UI_SCALE * 0.85)
    "entries": -7,        # hitbox rows (UI_SCALE * 0.70)
    "settings": -7,       # "- value +" bars (dynamic scale)
    "values": -7,
    "pause": -9,
    "death": 0,
    "death_title": 0,     # YOU ARE DEAD text
    "death_info": 0,      # LVL X WAVE X text
    "settings_buttons": -5,  # text ON the SETTINGS buttons
    "hardcore": -7,
    "hardsel": -7
}

LABEL_OFFSET_X = {
    # HORIZONTAL text offset (screen px); positive = right,
    # negative = left, per button size
    "main": 0,
    "play": 0,
    "dev": +10,
    "saves": 0,
    "hitboxes": +5,
    "entries": 0,
    "settings": 0,
    "values": +5,
    "pause": +9,
    "death": 0,
    "death_title": 0,     # YOU ARE DEAD text
    "death_info": 0,      # LVL X WAVE X text
    "settings_buttons": 20,  # text ON the SETTINGS buttons
    "settings_buttons2": 10,  # text ON the SETTINGS buttons
    "hardcore": +12,
    "hardsel": +15
}


def _npc_label(screen, text, rect, scale, hover, *, body=0.75,
               offset_y=0, offset_x=0):
    # Button text: lettersC1, lettersC6 on hover (like the merchant)
    # - centered on the VISIBLE pill: the left cap keeps ~5 px of
    #   transparency at its edge; without this fix the text looks
    #   shifted left
    # - offset_y / offset_x: fine text tuning, one value per button
    #   size (see LABEL_OFFSET_Y / LABEL_OFFSET_X)
    font_dict = fonts.lettersC6 if hover else fonts.lettersC1
    body_size = max(1, scale * body)
    margin = int(5 * scale)
    center_x = (rect.x + margin + (rect.width - margin) // 2
                + int(offset_x))
    fonts.draw_body_text(
        screen, text,
        center_x - fonts.get_text_width(text, body_size, font_dict) // 2,
        rect.centery - int(3 * body_size) + int(offset_y),
        rect.width, font_dict=font_dict, scale=body_size
    )


def _submenu_base(screen, background, title, alpha=185):
    screen.blit(background, (0, 0))
    veil = pygame.Surface(screen.get_size())
    veil.set_alpha(alpha)
    veil.fill((8, 8, 14))
    screen.blit(veil, (0, 0))
    _draw_hp_text(screen, title, screen.get_width() // 2,
                  int(screen.get_height() * 0.10),
                  scale=4, centered=True, font_dict=fonts.lettersT3)


def read_slots():
    # Short summary of the 10 slots: JSON dict or None when empty.
    slots = []
    for k in range(1, 11):
        path = os.path.join("saves", f"slot_{k}.json")
        try:
            with open(path, encoding="utf-8") as f:
                slots.append(json.load(f))
        except (OSError, ValueError):
            slots.append(None)
    return slots


def main_menu_buttons_x(screen):
    pass   # (the main menu buttons are higher up in the file)


def build_menu_play(screen):
    scale = UI_SCALE
    w, h = npc_bar_size(scale)
    w = max(w, button_width_for(
        ("AVEC SAUVEGARDE", "SANS SAUVEGARDE", "MODE DEV", "RETOUR"),
        scale))
    cx = screen.get_width() // 2
    y0 = int(screen.get_height() * 0.26)
    step = h + int(screen.get_height() * 0.05)
    return [(pygame.Rect(cx - w // 2, y0 + i * step, w, h), a)
            for i, a in enumerate(("sauvegarde", "sans", "dev", "retour"))]


def draw_menu_play(screen, buttons, background):
    _submenu_base(screen, background, "JOUER")
    mouse = pygame.mouse.get_pos()
    for rect, action in buttons:
        labels = {"sauvegarde": tr("WITH SAVE"),
                  "sans": tr("WITHOUT SAVE"),
                  "dev": tr("DEV MODE"), "retour": tr("BACK")}
        draw_npc_bar(screen, rect.x, rect.y, UI_SCALE, rect.width)
        _npc_label(screen, labels[action], rect, UI_SCALE,
                   rect.collidepoint(mouse),
                   offset_y=LABEL_OFFSET_Y["play"],
                   offset_x=LABEL_OFFSET_X["play"])


def build_menu_saves(screen):
    scale = UI_SCALE * 0.85
    w, h = npc_bar_size(scale)
    slots = read_slots()
    labels = [f"SLOT {k} - VIDE" if slots[k - 1] is None else
              f"SLOT {k} - NIV {slots[k - 1].get('niveau', '?')}"
              for k in range(1, 11)]
    labels.append("RETOUR")
    w = max(w, button_width_for(labels, scale))
    width, height = screen.get_width(), screen.get_height()
    cx = width // 2
    gap = int(24 * UI_SCALE)
    y0 = int(height * 0.14)
    # adaptive spacing: the 5 rows + BACK stay on screen
    step = min(h + int(5 * UI_SCALE),
               max(h + 4, (int(height * 0.90) - y0 - h) // 5))
    left_x = cx - (2 * w + gap) // 2
    buttons = []
    for k in range(10):
        col, row = k % 2, k // 2
        buttons.append((pygame.Rect(left_x + col * (w + gap),
                                    y0 + row * step, w, h),
                        ("slot", k + 1)))
    buttons.append((pygame.Rect(cx - w // 2, y0 + 5 * step, w, h),
                    ("retour", None)))
    return buttons


def draw_menu_saves(screen, buttons, background):
    _submenu_base(screen, background, tr("SAUVEGARDES"))
    mouse = pygame.mouse.get_pos()
    slots = read_slots()
    scale = UI_SCALE * 0.85
    for rect, action in buttons:
        draw_npc_bar(screen, rect.x, rect.y, scale, rect.width)
        hovered = rect.collidepoint(mouse)
        if action[0] == "retour":
            _npc_label(screen, tr("RETOUR"), rect, scale, hovered,
                       offset_y=LABEL_OFFSET_Y["saves"],
                       offset_x=LABEL_OFFSET_X["saves"])
            continue
        k = action[1]
        data = slots[k - 1]
        if data:
            label = tr("SLOT {} - NIV {}").format(
                k, data.get('niveau', '?'))
        else:
            label = tr("SLOT {} - VIDE").format(k)
        _npc_label(screen, label, rect, scale, hovered,
                   offset_y=LABEL_OFFSET_Y["saves"],
                   offset_x=LABEL_OFFSET_X["saves"])
    _draw_hp_text(screen,
                  tr("POUR SUPPRIMER UNE SAUVEGARDE, SUPPRIME SON FICHIER JSON"),
                  screen.get_width() // 2,
                  screen.get_height() - int(screen.get_height() * 0.03) - 22,
                  scale=2, centered=True, font_dict=fonts.lettersT3)


def build_menu_dev(screen):
    scale = UI_SCALE
    w, h = npc_bar_size(scale)
    w = max(w, button_width_for(
        ("HITBOXES", "REGLAGES", "JOUER", "RETOUR"), scale))
    cx = screen.get_width() // 2
    y0 = int(screen.get_height() * 0.26)
    step = h + int(screen.get_height() * 0.05)
    return [(pygame.Rect(cx - w // 2, y0 + i * step, w, h), a)
            for i, a in enumerate(("hitboxes", "settings", "jouer",
                                   "retour"))]


def draw_menu_dev(screen, buttons, background):
    _submenu_base(screen, background, "MODE DEV")
    mouse = pygame.mouse.get_pos()
    for rect, action in buttons:
        labels = {"hitboxes": tr("HITBOXES"), "settings": tr("REGLAGES"),
                  "jouer": tr("PLAY"), "retour": tr("BACK")}
        draw_npc_bar(screen, rect.x, rect.y, UI_SCALE, rect.width)
        _npc_label(screen, labels[action], rect, UI_SCALE,
                   rect.collidepoint(mouse),
                   offset_y=LABEL_OFFSET_Y["play"],
                   offset_x=LABEL_OFFSET_X["dev"])


def build_menu_hitboxes(screen, config):
    # On the left: ADD / REMOVE / BACK (large buttons); on the
    # right: the hitboxes in 2 columns (8 max per column) appearing
    # progressively. Common width per group, text inside.
    scale = UI_SCALE * 0.85
    w, h = npc_bar_size(scale)
    w = max(w, button_width_for(("AJOUTER", "ENLEVER", "RETOUR"),
                                scale))
    width, height = screen.get_width(), screen.get_height()
    left_x = int(width * 0.26) - w // 2
    y0 = int(height * 0.16)
    step = h + int(4 * UI_SCALE)
    rect_add = pygame.Rect(left_x, y0, w, h)
    rect_remove = pygame.Rect(left_x, y0 + step, w, h)
    rect_back = pygame.Rect(left_x, y0 + 2 * step, w, h)
    # rows: large bars, text fitted to the available space
    scale_row = UI_SCALE * 0.70
    row_w, row_h = npc_bar_size(scale_row)
    body_row = (0.85 if width >= 1200 else
                (0.6 if width >= 1000 else 0.5))
    raw = int(max(fonts.get_text_width(t, max(1, scale_row * body_row),
                                       fonts.lettersC1)
                  for t in HITBOX_TYPES) + 14 * scale_row)
    row_w = max(row_w, pill_width(pill_pieces_count(raw, scale_row),
                                  scale_row)) + int(12 * scale_row)
    row_step = row_h + max(3, int(height * 0.005))
    row_y0 = int(height * 0.15)
    col1_x = min(int(width * 0.48),
                 width - 14 - 2 * row_w - int(4 * UI_SCALE))
    rows = []
    for i in range(len(config)):
        col, row = i // 8, i % 8
        rows.append((pygame.Rect(
            col1_x + col * (row_w + int(4 * UI_SCALE)),
            row_y0 + row * row_step, row_w, row_h), i))
    return rows, rect_add, rect_remove, rect_back


def hitbox_dot_rect(rect):
    # Color dot at the right of a hitbox row.
    side = max(12, int(rect.h * 0.5))
    return pygame.Rect(rect.right - side - int(4 * UI_SCALE),
                       rect.centery - side // 2, side, side)


def draw_menu_hitboxes(screen, background, config):
    _submenu_base(screen, background, "HITBOXES")
    _draw_hp_text(screen, "F1 POUR AFFICHER EN JEU - MAX 15",
                  screen.get_width() // 2,
                  max(int(screen.get_height() * 0.135),
                      int(screen.get_height() * 0.10) + 40),
                  scale=2, centered=True, font_dict=fonts.lettersT4)
    rows, rect_add, rect_remove, rect_back = \
        build_menu_hitboxes(screen, config)
    mouse = pygame.mouse.get_pos()
    scale = UI_SCALE * 0.85
    scale_row = UI_SCALE * 0.70
    body_row = (0.85 if screen.get_width() >= 1200 else
                (0.6 if screen.get_width() >= 1000 else 0.5))
    # base buttons on the left
    for rect, label in ((rect_add, "AJOUTER"),
                        (rect_remove, "ENLEVER"),
                        (rect_back, "RETOUR")):
        draw_npc_bar(screen, rect.x, rect.y, scale, rect.width)
        _npc_label(screen, label, rect, scale,
                   rect.collidepoint(mouse),
                   offset_y=LABEL_OFFSET_Y["hitboxes"],
                   offset_x=LABEL_OFFSET_X["hitboxes"])
    # rows on the right (readable names, dot on the right)
    for rect, i in rows:
        entry = config[i]
        draw_npc_bar(screen, rect.x, rect.y, scale_row, rect.width)
        dot = hitbox_dot_rect(rect)
        pygame.draw.rect(screen, HITBOX_COLORS[entry["couleur"]], dot)
        pygame.draw.rect(screen, (18, 20, 28), dot, 2)
        zone = pygame.Rect(rect.x, rect.y,
                           rect.width - dot.width - int(6 * UI_SCALE),
                           rect.h)
        _npc_label(screen, tr(HITBOX_TYPES[entry["type"]]), zone,
                   scale_row, zone.collidepoint(mouse),
                   body=body_row,
                   offset_y=LABEL_OFFSET_Y["entries"],
                   offset_x=LABEL_OFFSET_X["entries"])


def _value_text(key, value):
    if isinstance(value, bool):
        return "ON" if value else "OFF"
    if key == "lieu":
        return PLACE_NAMES.get(value, value)
    if "pct" in key:
        return f"{value} %"
    return str(value)


def build_menu_dev_settings(screen):
    # "- value +" bars on the right side, labels at their left; the
    # bar width is computed on the widest possible values. ENLARGED
    # buttons: the bar height takes all the available screen space
    # for the 13 rows + BACK/PLAY.
    width = screen.get_width()
    height = screen.get_height()
    y0 = int(height * 0.15)
    h = min(int(17 * UI_SCALE * 0.73),
            max(24, (int(height * 0.84) - y0 - int(8 * UI_SCALE))
                // len(SETTINGS_ROWS) - 1))
    scale = h / 17.0
    body = max(1, scale * 0.75)
    samples = []
    for key, _label, _step, mini, maxi, kind in SETTINGS_ROWS:
        if kind == "cycle":
            samples.append(max(PLACE_NAMES.values(), key=len))
        elif kind == "onoff":
            samples.append("OFF")
        else:
            samples.append(str(maxi))
    raw = int(max(fonts.get_text_width("- " + e + " +", body,
                                       fonts.lettersC1)
                  for e in samples) + 12 * scale)
    w = max(npc_bar_size(scale)[0],
            pill_width(pill_pieces_count(raw, scale), scale))
    bar_x = int(width * 0.66) - w // 2
    step = h + max(4, int(height * 0.012))
    if y0 + len(SETTINGS_ROWS) * step + h > int(height * 0.90):
        step = max(h + 3, (int(height * 0.90) - y0 - h)
                   // len(SETTINGS_ROWS))
    rows = [(pygame.Rect(bar_x, y0 + i * step, w, h), key)
            for i, (key, *_rest) in enumerate(SETTINGS_ROWS)]
    buttons_y = y0 + len(SETTINGS_ROWS) * step + int(2 * UI_SCALE)
    rect_back = pygame.Rect(width // 2 - w // 2, buttons_y, w, h)
    return rows, rect_back


def _plus_minus_zone(rect, key, value, scale=None):
    # Clickable rectangles of the - and + symbols of a setting row
    # (the scale comes from the bar height: never shifted). The "-"
    # and the "+" are at EQUAL distance from the text on both sides.
    scale = scale or (rect.h / 17.0)
    body = max(1, scale * 0.75)
    font_dict = fonts.lettersC1
    value_text = _value_text(key, value)
    w_m = fonts.get_text_width("-", body, font_dict)
    w_v = fonts.get_text_width(value_text, body, font_dict)
    w_p = fonts.get_text_width("+", body, font_dict)
    g = int(6 * scale / 3)
    total = w_m + g + w_v + g + w_p
    xs = rect.centerx - total // 2
    y = rect.centery - int(3 * body)
    top = int(9 * body)
    # the "-" glyph occupies [xs, xs+w_m], the value starts g after;
    # the "+" glyph starts g after the end of the value: both
    # symbols are at EQUAL visual distance from the text
    rm = pygame.Rect(xs - g, y, w_m + 2 * g, top)
    rp = pygame.Rect(rm.right + w_v, y, w_p + 2 * g, top)
    return rm, rp


def draw_menu_dev_settings(screen, background, settings):
    _submenu_base(screen, background, tr("SETTINGS"))
    rows, rect_back = build_menu_dev_settings(screen)
    mouse = pygame.mouse.get_pos()
    scale = rows[0][0].h / 17.0
    body = max(1, scale * 0.75)
    for rect, key in rows:
        draw_npc_bar(screen, rect.x, rect.y, scale, rect.width)
        row = next(d for d in SETTINGS_ROWS if d[0] == key)
        label = tr(row[1])
        # setting name in WHITE (T3 sheet) and aligned: all names
        # end at the same x, just at the left of the bars;
        # SETTING_LABEL_OFFSETS[key] = (dx, dy) to adjust row by row
        dx_l, dy_l = SETTING_LABEL_OFFSETS.get(key, (0, 0))
        lx = (rect.x - 14 - fonts.get_text_width(label, 2,
                                                 fonts.lettersT3)
              + dx_l)
        fonts.draw_line(screen, label, lx, rect.centery - 9 + dy_l,
                        scale=2, font_dict=fonts.lettersT3)
        rm, rp = _plus_minus_zone(rect, key, settings[key])
        hover_v = rm.collidepoint(mouse) or rp.collidepoint(mouse)
        font_v = fonts.lettersC6 if hover_v else fonts.lettersC1
        value_text = _value_text(key, settings[key])
        ox_v = int(LABEL_OFFSET_X["values"])
        oy_v = int(LABEL_OFFSET_Y["values"])
        fonts.draw_body_text(
            screen, "-",
            rm.centerx - fonts.get_text_width("-", body, font_v) // 2
            + ox_v,
            rm.y + oy_v, rect.width, font_dict=font_v, scale=body)
        fonts.draw_body_text(
            screen, value_text, rm.right + ox_v, rp.y + oy_v,
            rect.width, font_dict=font_v, scale=body)
        fonts.draw_body_text(
            screen, "+",
            rp.centerx - fonts.get_text_width("+", body, font_v) // 2
            + ox_v,
            rp.y + oy_v, rect.width, font_dict=font_v, scale=body)
    draw_npc_bar(screen, rect_back.x, rect_back.y, scale,
                 rect_back.width)
    _npc_label(screen, "RETOUR", rect_back, scale,
               rect_back.collidepoint(mouse),
               offset_y=LABEL_OFFSET_Y["settings"],
               offset_x=LABEL_OFFSET_X["settings"])

# ---------- IN-GAME PAUSE MENU ----------
# Panel sliding in from the left; the game keeps running behind it
# (no freeze). 4 button slots: CONTINUE at the very top, QUIT at
# the very bottom, 2 RESERVED slots in the middle for future
# buttons (None actions = neither drawn nor clickable).
STATE_COLORS = {"wave": (255, 90, 90), "shop": (255, 210, 0),
                "house": (130, 200, 255), "chapel": (200, 160, 255)}
PAUSE_ANIM_MS = 250   # ms of enter / exit animation


def _tinted_text(surface, text, cx, cy, scale, color, font_dict,
                 alpha=255):
    text = tr(text)
    # Twin of _draw_hp_text (SAME metrics: 7*s glyph, s gap, special
    # slash, y = cy - height // 2) but tinted with the requested
    # color; optional alpha for the fades.
    height = 9 * scale
    slash_width = 4 * scale
    width = 0
    for char in text:
        if char == "/":
            width += slash_width
        elif char in font_dict:
            width += 7 * scale
        width += scale
    width -= scale
    pad = 2
    temp = pygame.Surface((int(width) + 2 * pad,
                           int(height) + 2 * pad),
                          pygame.SRCALPHA).convert_alpha()
    x, y = pad, pad
    for char in text:
        if char == "/":
            pygame.draw.line(temp, (255, 255, 255),
                             (x, y + height - 1),
                             (x + slash_width - scale, y + 1),
                             scale)
            x += slash_width + scale
        elif char in font_dict:
            sprite = pygame.transform.scale(font_dict[char],
                                            (7 * scale, height))
            temp.blit(sprite, (x, y))
            x += 7 * scale + scale
    temp.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
    if alpha < 255:
        temp.set_alpha(alpha)
    surface.blit(temp, (cx - width // 2 - pad,
                        cy - height // 2 - pad))

# --- HARDCORE mode: the white fonts of the game, of the mini-menu
# and of the loading screen turn blood red (black on red ground)
MODE_HARDCORE = False
BLOOD_RED = (186, 18, 18)
# death screen font: Text7.png (same grid as Text3), fallback to
# Text3 when the file is missing
DEATH_FONT_SHEET = None   # built at 1st call (after load_font)


def death_font():
    # Death screen font: Text7.png (same grid as Text3), fallback
    # to Text3 when the file is missing.
    global DEATH_FONT_SHEET
    if DEATH_FONT_SHEET is None:
        if os.path.exists("Text7.png"):
            sheet = pygame.image.load("Text7.png").convert_alpha()
            DEATH_FONT_SHEET = fonts.build_title_font(sheet, 0.0)
        else:
            DEATH_FONT_SHEET = fonts.lettersT3
    return DEATH_FONT_SHEET


def draw_title_text(screen, text, x, y, scale, font_dict,
                    red_background=False):
    # Big white text of the game; in hardcore it turns blood red
    # (black when laid on a red background).
    if not MODE_HARDCORE:
        _draw_hp_text(screen, text, x, y, scale=scale,
                      centered=True, font_dict=font_dict)
        return
    color = (0, 0, 0) if red_background else BLOOD_RED
    _tinted_text(screen, text, x, y, scale, color, font_dict)


def pause_panel_rect(screen):
    # Left side panel; its width depends on the longest button
    # (CONTINUE).
    scale = UI_SCALE * 0.8
    bar_w = button_width_for(("CONTINUER", "REGLAGES", "QUITTER"), scale)
    margin = int(26 * scale)
    return pygame.Rect(0, 0, bar_w + 2 * margin, screen.get_height())


def build_menu_echap(screen):
    # The 4 button slots of the panel (coordinates on the DEPLOYED
    # panel; the animation only moves the blit).
    scale = UI_SCALE * 0.8
    bar_w, bar_h = npc_bar_size(scale)
    bar_w = max(bar_w, button_width_for(
        ("CONTINUER", "REGLAGES", "QUITTER"), scale))
    panel = pause_panel_rect(screen)
    panel_cx = panel.w // 2
    zone_top = int(panel.h * 0.20)
    zone_bot = panel.h - int(panel.h * 0.06) - bar_h
    zone_step = (zone_bot - zone_top) / 3.0
    actions = ("continuer", "reglages", None, "quitter")
    return [(pygame.Rect(panel_cx - bar_w // 2,
                         int(zone_top + i * zone_step), bar_w, bar_h), a)
            for i, a in enumerate(actions)]


def draw_pause_menu(screen, state, t_open, t_close=None):
    # Draws the panel at its animation phase: t_open =
    # pygame.time.get_ticks() at opening; set t_close to see the
    # panel slide back to the left. Returns the CURRENT screen rect
    # of the panel (useful for clicks).
    now = pygame.time.get_ticks()
    if t_close is None:
        p = min(1.0, max(0.0, now - t_open) / PAUSE_ANIM_MS)
        phase = 1.0 - (1.0 - p) ** 3        # ease-out on entry
    else:
        p = min(1.0, max(0.0, now - t_close) / PAUSE_ANIM_MS)
        phase = (1.0 - p) ** 2              # ease-in on exit
    panel = pause_panel_rect(screen)
    panel_x = int(panel.w * (phase - 1.0))
    surf = pygame.Surface(panel.size, pygame.SRCALPHA).convert_alpha()
    surf.fill((8, 8, 14, 235))
    pygame.draw.rect(surf, (96, 122, 106), surf.get_rect(), 2)
    pygame.draw.line(surf, (150, 180, 160), (2, 2), (panel.w - 3, 2))
    # game title then game state harmonized, in its color
    draw_title_text(surf, GAME_TITLE, panel.w // 2,
                    int(panel.h * 0.05) + 18, 4, fonts.lettersT3)
    name = PLACE_NAMES.get(state, str(state).upper())
    name = tr(name)
    _tinted_text(surf, name, panel.w // 2, int(panel.h * 0.115) + 9,
                 2, STATE_COLORS.get(state, (255, 255, 255)),
                 fonts.lettersT3)
    # buttons
    mouse = pygame.mouse.get_pos()
    scale = UI_SCALE * 0.8
    labels = {"continuer": tr("CONTINUE"), "reglages": tr("SETTINGS"),
              "quitter": tr("QUIT")}
    for rect, action in build_menu_echap(screen):
        if action is None:
            continue
        draw_npc_bar(surf, rect.x, rect.y, scale, rect.width)
        _npc_label(surf, labels[action], rect, scale,
                   rect.collidepoint(mouse),
                   offset_y=LABEL_OFFSET_Y["pause"],
                   offset_x=LABEL_OFFSET_X["pause"])
    screen.blit(surf, (panel_x, 0))
    return pygame.Rect(panel_x, 0, panel.w, panel.h)


# ---------- HARDCORE MINI-MENU (no save) ----------
# Simple: MODE HARDCORE title, then 3 centered buttons
# (bar - ON/OFF +, PLAY, QUIT).
def build_menu_hardcore(screen):
    scale = UI_SCALE * 0.8
    bar_w, bar_h = npc_bar_size(scale)
    bar_w = max(bar_w, button_width_for(("JOUER", "QUITTER"), scale))
    bar2_w, bar2_h = npc_bar_size(scale)
    cx = screen.get_width() // 2
    height = screen.get_height()
    rect_bar = pygame.Rect(cx - bar2_w // 2,
                           int(height * 0.34), bar2_w, bar2_h)
    buttons_y = int(height * 0.48)
    rect_play = pygame.Rect(cx - bar_w // 2, buttons_y, bar_w, bar_h)
    rect_quit = pygame.Rect(cx - bar_w // 2,
                            buttons_y + bar_h + int(16 * UI_SCALE),
                            bar_w, bar_h)
    return rect_bar, rect_play, rect_quit


def draw_menu_hardcore(screen, background, settings):
    _submenu_base(screen, background, "MODE HARDCORE")
    rect_bar, rect_play, rect_quit = build_menu_hardcore(screen)
    mouse = pygame.mouse.get_pos()
    scale_b = rect_bar.h / 17.0
    draw_npc_bar(screen, rect_bar.x, rect_bar.y, scale_b,
                 rect_bar.width)
    value_text = _value_text("hardcore", settings["hardcore"])
    _npc_label(screen, value_text, rect_bar, scale_b,
               rect_bar.collidepoint(mouse),
               offset_y=LABEL_OFFSET_Y["play"],
               offset_x=LABEL_OFFSET_X["play"])
    for rect, label in ((rect_play, tr("PLAY")),
                        (rect_quit, tr("QUIT"))):
        draw_npc_bar(screen, rect.x, rect.y, UI_SCALE * 0.8,
                     rect.width)
        _npc_label(screen, label, rect, UI_SCALE * 0.8,
                   rect.collidepoint(mouse),
                   offset_y=LABEL_OFFSET_Y["hardcore"],
                   offset_x=LABEL_OFFSET_X["hardcore"])

# ---------- SETTINGS MENU (music/sound/languages/keys) ----------
def build_menu_settings(screen):
    # 5 stacked centered elements: MUSIC bar, SOUND bar,
    # LANGUAGES, KEYS, BACK.
    scale = UI_SCALE * 0.8
    bar_w, bar_h = npc_bar_size(scale)
    bar_w = max(bar_w, button_width_for(
        ("MUSIQUE : OFF", "SONS : OFF", "LANGUES", "TOUCHES",
         "RETOUR"), scale))
    cx = screen.get_width() // 2
    height = screen.get_height()
    actions = ("musique", "sons", "langues", "touches", "retour")
    positions = (0.32, 0.42, 0.53, 0.61, 0.72)
    buttons = []
    for action, p in zip(actions, positions):
        dx, dy = SETTINGS_BUTTON_OFFSETS[action]
        buttons.append(pygame.Rect(cx - bar_w // 2 + dx,
                                   int(height * p) + dy,
                                   bar_w, bar_h))
    return buttons


def draw_menu_settings(screen, background):
    _submenu_base(screen, background, tr("SETTINGS"))
    (rect_music, rect_sfx, rect_lng, rect_keys,
     rect_back) = build_menu_settings(screen)
    mouse = pygame.mouse.get_pos()
    scale_b = rect_music.h / 17.0
    txt_music = (f"{tr('MUSIC')} : "
                 f"{tr('ON') if options.MUSIC_ON else tr('OFF')}")
    txt_sfx = (f"{tr('SOUND')} : "
               f"{tr('ON') if options.SFX_ON else tr('OFF')}")
    for rect, text in ((rect_music, txt_music),
                       (rect_sfx, txt_sfx),
                       (rect_lng, tr("LANGUAGES")),
                       (rect_keys, tr("KEYS")),
                       (rect_back, tr("BACK"))):
        draw_npc_bar(screen, rect.x, rect.y, scale_b, rect.width)
        _npc_label(screen, text, rect, scale_b,
                   rect.collidepoint(mouse),
                   offset_y=LABEL_OFFSET_Y["settings_buttons"],
                   offset_x=LABEL_OFFSET_X["settings_buttons"])

# ---------- LANGUAGES MENU ----------
def build_menu_languages(screen):
    # FRANCAIS / ENGLISH buttons + BACK; the "current language"
    # text is drawn by draw_menu_languages.
    scale = UI_SCALE * 0.8
    bar_w, bar_h = npc_bar_size(scale)
    bar_w = max(bar_w, button_width_for(("FRANCAIS", "ENGLISH"),
                                        scale))
    cx = screen.get_width() // 2
    height = screen.get_height()
    dx_f, dy_f = LANGUAGES_BUTTON_OFFSETS["francais"]
    dx_e, dy_e = LANGUAGES_BUTTON_OFFSETS["english"]
    dx_r, dy_r = LANGUAGES_BUTTON_OFFSETS["retour"]
    return (pygame.Rect(cx - bar_w // 2 + dx_f,
                        int(height * 0.45) + dy_f, bar_w, bar_h),
            pygame.Rect(cx - bar_w // 2 + dx_e,
                        int(height * 0.55) + dy_e, bar_w, bar_h),
            pygame.Rect(cx - bar_w // 2 + dx_r,
                        int(height * 0.70) + dy_r, bar_w, bar_h))


def draw_menu_languages(screen, background):
    _submenu_base(screen, background, tr("LANGUAGES"))
    rect_fr, rect_en, rect_back = build_menu_languages(screen)
    mouse = pygame.mouse.get_pos()
    name = "FRANCAIS" if options.LANGUAGE == "fr" else "ENGLISH"
    _draw_hp_text(screen, tr("GAME LANGUAGE: {}").format(name),
                  screen.get_width() // 2,
                  int(screen.get_height() * 0.30), scale=3,
                  centered=True, font_dict=fonts.lettersT3)
    scale_b = rect_fr.h / 17.0
    for rect, text in ((rect_fr, "FRANCAIS"), (rect_en, "ENGLISH"),
                       (rect_back, tr("BACK"))):
        draw_npc_bar(screen, rect.x, rect.y, scale_b, rect.width)
        _npc_label(screen, text, rect, scale_b,
                   rect.collidepoint(mouse),
                   offset_y=LABEL_OFFSET_Y["settings_buttons"],
                   offset_x=LABEL_OFFSET_X["settings_buttons2"])

# ---------- KEYS MENU (keyboard re-mapping) ----------
LABELS_ACTIONS = {"left": "LEFT", "right": "RIGHT",
                  "up": "UP", "down": "DOWN",
                  "interact": "INTERACT", "attack": "ATTACK",
                  "mute": "MUTE"}


def build_menu_keys(screen):
    # rows (action, key_rect, change_rect) + RESET + BACK at the
    # bottom. KEYS_ROWS_OFFSET shifts the whole rows block;
    # KEYS_BUTTON_OFFSETS moves RESET / BACK individually.
    small_scale = UI_SCALE * 0.55
    _small_w, small_h = npc_bar_size(small_scale)
    cx = screen.get_width() // 2
    height = screen.get_height()
    rows_dx, rows_dy = KEYS_ROWS_OFFSET
    rows = []
    for i, action in enumerate(options.KEY_ORDER):
        y = int(height * 0.20) + i * int(height * 0.062) + rows_dy
        key_rect = pygame.Rect(cx - int(height * 0.09) + rows_dx, y,
                               int(height * 0.18), small_h)
        change_rect = pygame.Rect(cx + int(height * 0.12) + rows_dx, y,
                                  int(height * 0.14), small_h)
        rows.append((action, key_rect, change_rect))
    bottom_scale = UI_SCALE * 0.8
    bar_w, bar_h = npc_bar_size(bottom_scale)
    bar_w = max(bar_w, button_width_for(("REINITIALISER", "RETOUR"),
                                        bottom_scale))
    dx_r, dy_r = KEYS_BUTTON_OFFSETS["reset"]
    rect_reset = pygame.Rect(cx - bar_w // 2 + dx_r,
                             int(height * 0.72) + dy_r, bar_w, bar_h)
    dx_b, dy_b = KEYS_BUTTON_OFFSETS["retour"]
    rect_back = pygame.Rect(cx - bar_w // 2 + dx_b,
                            int(height * 0.81) + dy_b, bar_w, bar_h)
    return rows, rect_reset, rect_back


def draw_menu_keys(screen, background, capture_action=None):
    _submenu_base(screen, background, tr("KEYS"))
    rows, rect_reset, rect_back = build_menu_keys(screen)
    mouse = pygame.mouse.get_pos()
    conflicts = options.key_conflicts()
    height = screen.get_height()
    small_scale = UI_SCALE * 0.55
    for action, key_rect, change_rect in rows:
        # action name, at the left of the row
        _draw_hp_text(screen, tr(LABELS_ACTIONS[action]),
                      key_rect.x - int(height * 0.06),
                      key_rect.centery, scale=2, centered=True,
                      font_dict=fonts.lettersT3)
        # pill of the current key (or of the ongoing capture)
        draw_npc_bar(screen, key_rect.x, key_rect.y,
                     small_scale, key_rect.width)
        if capture_action == action:
            text = tr("PRESS ANY KEY...")
        elif (action == "attack"
              and options.KEYS[action] is None):
            text = tr("LEFT CLICK")
        else:
            text = options.key_name(options.KEYS[action])
        _npc_label(screen, text, key_rect, small_scale, False,
                   offset_y=LABEL_OFFSET_Y["settings_buttons"],
                   offset_x=LABEL_OFFSET_X["settings_buttons2"])
        # CHANGE button
        draw_npc_bar(screen, change_rect.x, change_rect.y,
                     small_scale, change_rect.width)
        _npc_label(screen, tr("CHANGE"), change_rect, small_scale,
                   change_rect.collidepoint(mouse),
                   offset_y=LABEL_OFFSET_Y["settings_buttons"],
                   offset_x=LABEL_OFFSET_X["settings_buttons2"])
        # conflict: 2 yellow "!" (T4) around the key and the
        # CHANGE button
        if (options.KEYS.get(action) is not None
                and options.KEYS[action] in conflicts):
            for rect in (key_rect, change_rect):
                _draw_hp_text(screen, "!",
                              rect.x - int(rect.h * 0.45),
                              rect.centery, scale=3, centered=True,
                              font_dict=fonts.lettersT4)
                _draw_hp_text(screen, "!",
                              rect.right + int(rect.h * 0.45),
                              rect.centery, scale=3,
                              centered=True,
                              font_dict=fonts.lettersT4)
    # bottom: RESET + BACK
    for rect, text in ((rect_reset, tr("RESET")),
                       (rect_back, tr("BACK"))):
        draw_npc_bar(screen, rect.x, rect.y, UI_SCALE * 0.8,
                     rect.width)
        _npc_label(screen, text, rect, UI_SCALE * 0.8,
                   rect.collidepoint(mouse),
                   offset_y=LABEL_OFFSET_Y["settings_buttons"],
                   offset_x=LABEL_OFFSET_X["settings_buttons2"])

# ---------- DEATH SCREEN ----------
DEATH_FADE_MS = 700   # ms of the black fade (game loop side)


def build_menu_death(screen):
    scale = UI_SCALE * 0.8
    bar_w, bar_h = npc_bar_size(scale)
    bar_w = max(bar_w, button_width_for(("REAPPARAITRE", "QUITTER"),
                                        scale))
    cx = screen.get_width() // 2
    buttons_y = int(screen.get_height() * 0.60)
    dx_r, dy_r = DEATH_BUTTON_OFFSETS["reapparaitre"]
    dx_q, dy_q = DEATH_BUTTON_OFFSETS["quitter"]
    return [(pygame.Rect(cx - bar_w // 2 + dx_r, buttons_y + dy_r,
                         bar_w, bar_h), "reapparaitre"),
            (pygame.Rect(cx - bar_w // 2 + dx_q,
                         buttons_y + bar_h
                         + int(16 * UI_SCALE) + dy_q,
                         bar_w, bar_h), "quitter")]


def _death_label(screen, text, cx, cy, scale, color):
    # Twin of _npc_label for the death menu: SAME font as the
    # buttons (lettersC1, body 0.75) but tinted, because the
    # merchant glyphs are dark (unreadable on the black
    # background).
    font_dict = fonts.lettersC1
    body = max(1, scale * 0.75)
    pad = 2
    width = int(fonts.get_text_width(text, body, font_dict))
    width += 2 * pad
    height = int(6 * body) + 2 * pad
    temp = pygame.Surface((width, height),
                          pygame.SRCALPHA).convert_alpha()
    fonts.draw_line(temp, text, pad, pad, body, font_dict=font_dict)
    # the merchant glyphs are DARK: we push them to white (rgb
    # addition) BEFORE tinting, otherwise the multiplicative tint
    # is invisible on (17, 11, 0)
    temp.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
    temp.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(temp, (cx - width // 2, cy - height // 2))


def draw_menu_death(screen, death_time, level, wave):
    # Black background, then YOU ARE DEAD + level/wave + buttons:
    # texts with _death_label (merchant font), like the buttons.
    t = pygame.time.get_ticks() - death_time
    screen.fill((0, 0, 0))
    if t <= DEATH_FADE_MS:
        return
    w, h = screen.get_width(), screen.get_height()
    # title at h*0.24 (BLOOD RED in hardcore), info at h*0.38,
    # both with the merchant font (_death_label)
    title_color = BLOOD_RED if MODE_HARDCORE else (255, 255, 255)
    _death_label(screen, tr("YOU ARE DEAD"),
                 w // 2 + int(LABEL_OFFSET_X["death_title"]),
                 int(h * 0.24) + int(LABEL_OFFSET_Y["death_title"]),
                 12, title_color)
    _death_label(screen,
                 f"{tr('LVL')} {level} {tr('WAVE')} {wave}",
                 w // 2 + int(LABEL_OFFSET_X["death_info"]),
                 int(h * 0.38) + int(LABEL_OFFSET_Y["death_info"]),
                 6, (255, 255, 255))
    mouse = pygame.mouse.get_pos()
    labels = {"reapparaitre": tr("RESPAWN"), "quitter": tr("QUIT")}
    for rect, action in build_menu_death(screen):
        draw_npc_bar(screen, rect.x, rect.y, UI_SCALE * 0.8,
                     rect.width)
        _npc_label(screen, labels[action], rect, UI_SCALE * 0.8,
                   rect.collidepoint(mouse),
                   offset_y=LABEL_OFFSET_Y["death"],
                   offset_x=LABEL_OFFSET_X["death"])