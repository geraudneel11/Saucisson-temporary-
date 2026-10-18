import pygame

import options

pygame.init()

# System fonts for texts that are drawn with real TTF glyphs
# (none of the pixel-font sheets below have lowercase letters).
font = pygame.font.SysFont("Ebrima", 36, bold=True)
coin_font = pygame.font.SysFont("Ebrima", 32, bold=True)


# ------------------------------------------------------------
# PIXEL FONT SHEETS
# Every glyph lives on a sprite sheet (Text1..Text6.png):
#   - "title" fonts (lettersT1..T6): 7 x 9.2 px cells, one block
#     of A-Z + space + digits + punctuation;
#   - "body" fonts (lettersC1..C6): 5 x 6 px cells used by the
#     merchant-style UI text.
# load_font() MUST be called once after pygame.display.set_mode.
# ------------------------------------------------------------
def load_font():
    global title_font_sheet, corp_font_sheet
    global lettersT1, lettersC1, lettersC6, lettersC4, glyph_width
    global title3_font_sheet, lettersT3
    global title4_font_sheet, lettersT4
    global title5_font_sheet, lettersT5
    global title6_font_sheet, lettersT6

    title_font_sheet = pygame.image.load("Text1.png").convert_alpha()
    corp_font_sheet = pygame.image.load("Text2.png").convert_alpha()
    title3_font_sheet = pygame.image.load("Text3.png").convert_alpha()
    title4_font_sheet = pygame.image.load("Text4.png").convert_alpha()
    title5_font_sheet = pygame.image.load("Text5.png").convert_alpha()
    title6_font_sheet = pygame.image.load("Text6.png").convert_alpha()

    # Characters of the 10-column body font sheet (None = empty cell).
    corp_font_chars = [
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
        "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
        "U", "V", "W", "X", "Y", "Z", None, None, None, None,
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
        ".", ",", ":", "?", "!", "(", ")", "+", "-", "="
    ]

    # Narrow body glyphs: the sprite is 3 px wide but the glyph ink
    # only spans ~2 px, so advance by 2 to keep the text tight.
    glyph_width = {"'": 2, ".": 2, ",": 2, ":": 2, "!": 2}

    # Title font, sheet Text1: full hand-built grid (the reference
    # layout all the other title sheets reuse).
    lettersT1 = _construire_police_titre_text1(title_font_sheet)

    # Text3..Text6 share the Text1 grid (one block, no offset).
    lettersT3 = build_title_font(title3_font_sheet)
    lettersT4 = build_title_font(title4_font_sheet)
    lettersT5 = build_title_font(title5_font_sheet)
    lettersT6 = build_title_font(title6_font_sheet)

    # Body fonts: normal (C1), hover/bright (C6) and mid-tone (C4)
    # variants of the same character set on the same sheet.
    lettersC1 = build_body_font(
        corp_font_sheet, corp_font_chars,
        cols=10, cell_w=5, cell_h=6, offset_y=0)
    lettersC6 = build_body_font(
        corp_font_sheet, corp_font_chars,
        cols=10, cell_w=5, cell_h=6, offset_y=191)
    lettersC4 = build_body_font(
        corp_font_sheet, corp_font_chars,
        cols=10, cell_w=5, cell_h=6, offset_y=95)


def _construire_police_titre_text1(sheet):
    # Explicit subsurface grid for Text1 (7 x 9.2 px cells):
    # row 0-1 A-T, row 2 U-Z + space, row 3 digits, row 4 punctuation.
    font = {}
    rangees = ["ABCDEFGHIJ", "KLMNOPQRST", "UVWXYZ ",
               "1234567890", ".,:?!()+-="]
    for r, rangee in enumerate(rangees):
        for c, char in enumerate(rangee):
            font[char] = sheet.subsurface(
                (c * 7, r * 9.2, 7, 9.2))
    return font


def build_body_font(sheet, chars, cols, cell_w, cell_h, offset_y=0):
    # Body font from the 10-column sheet. The apostrophe is missing
    # from the sheet: build it by copying the comma glyph onto a
    # transparent cell.
    font = {}
    font[","] = sheet.subsurface((8, 27, 3, 3))
    apostrophe = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
    apostrophe.blit(font[","], (0, 0))
    font["'"] = apostrophe
    for i, char in enumerate(chars):
        if char is None:
            continue
        x = (i % cols) * cell_w
        y = (i // cols) * cell_h + offset_y
        font[char] = sheet.subsurface((x, y, cell_w, cell_h))
    return font


def build_title_font(sheet, offset_y=0.0):
    # Full title font dictionary (same 7 x 9.2 grid as Text1):
    # letters, space, digits and punctuation from one block.
    rangees = ["ABCDEFGHIJ", "KLMNOPQRST", "UVWXYZ ",
               "1234567890", ".,:?!()+-="]
    font = {}
    for r, rangee in enumerate(rangees):
        for c, char in enumerate(rangee):
            font[char] = sheet.subsurface(
                (c * 7, r * 9.2 + offset_y, 7, 9.2))
    return font


# Scaled sprites are expensive to build every frame: cache them
# per (font dict, character, scale) and blit the cached surface.
_scaled_cache = {}


def _sprite_scaled(sprite, cle, largeur, hauteur):
    en_cache = _scaled_cache.get(cle)
    if en_cache is None:
        en_cache = pygame.transform.scale(sprite, (largeur, hauteur))
        if len(_scaled_cache) > 512:
            _scaled_cache.clear()
        _scaled_cache[cle] = en_cache
    return en_cache


def draw_text(surface, text, x, y, scale=1, spacing=0, centered=False):
    # Title-font text (Text1). Text is translated at draw time so
    # every call site is automatically localized.
    text = options.tr(text).upper()
    total_width = 0
    for char in text:
        if char == " ":
            total_width += 7 * scale
            continue
        if char not in lettersT1:
            continue
        total_width += int(lettersT1[char].get_width() * scale) + spacing
    if centered:
        x -= total_width // 2

    current_x = x
    for char in text:
        if char == " ":
            current_x += 7 * scale
            continue
        if char not in lettersT1:
            continue
        sprite = lettersT1[char]
        if scale != 1:
            sprite = _sprite_scaled(
                sprite, ("t1", char, scale),
                int(sprite.get_width() * scale),
                int(sprite.get_height() * scale))
        surface.blit(sprite, (current_x, y))
        current_x += max(1, sprite.get_width() + spacing)


def draw_line(surface, text, x, y, scale=1, centered=False,
              font_dict=None):
    # One line of body-font text (no wrapping). Translated at
    # draw time; narrow glyphs advance by glyph_width.
    text = options.tr(text).upper()
    if font_dict is None:
        font_dict = lettersC1
    letter_spacing = 1
    word_spacing = 4

    total_width = 0
    for char in text:
        if char == " ":
            total_width += word_spacing * scale
            continue
        if char not in font_dict:
            continue
        total_width += font_dict[char].get_width() * scale + letter_spacing
    if centered:
        x -= total_width // 2

    current_x = x
    for char in text:
        if char == " ":
            current_x += word_spacing * scale
            continue
        if char not in font_dict:
            continue
        sprite = font_dict[char]
        if scale != 1:
            sprite = _sprite_scaled(
                sprite, (id(font_dict), char, scale),
                sprite.get_width() * scale,
                sprite.get_height() * scale)
        surface.blit(sprite, (current_x, y))
        advance = glyph_width.get(char, sprite.get_width())
        current_x += advance + letter_spacing


def get_text_width(text, scale, font_dict):
    # Measured width of one line (word spacing 4, letter spacing 1).
    # Translated as well so centering matches the drawn string.
    text = options.tr(text).upper()
    width = 0
    for char in text:
        if char == " ":
            width += 4 * scale
        elif char in font_dict:
            width += font_dict[char].get_width() * scale + 1
    return width


def draw_body_text(surface, text, x, y, max_width, font_dict, scale=1,
                   visible_chars=None):
    # Word-wrapped paragraph. visible_chars limits how much is
    # revealed (typewriter effect of the NPC dialogues).
    if visible_chars is not None:
        text = text[:visible_chars]
    words = text.split(" ")
    line = ""
    for word in words:
        test_line = line + word + " "
        width = get_text_width(test_line, scale, font_dict)
        if width > max_width and line != "":
            draw_line(surface, line, x, y, scale, font_dict=font_dict)
            y += 8 * scale
            line = word + " "
        else:
            line = test_line
    draw_line(surface, line, x, y, scale, font_dict=font_dict)


def draw_wrapped_text(surface, text, x, y, max_width, font_dict,
                      scale=1, max_y=None):
    # Like draw_body_text, but:
    #   - words longer than a full line are cut character by
    #     character (draw_body_text cannot do that);
    #   - stops writing as soon as a line would go past max_y
    #     (screen coordinate) so the text never overflows its area.
    line_step = 8 * scale
    lines = []
    line = ""

    for word in text.split(" "):
        # Word too long for one line: cut it into chunks.
        while get_text_width(word, scale, font_dict) > max_width:
            cut = len(word)
            while cut > 1 and get_text_width(
                    word[:cut], scale, font_dict) > max_width:
                cut -= 1
            if line != "":
                lines.append(line)
                line = ""
            lines.append(word[:cut])
            word = word[cut:]

        test_line = line + word + " "
        if get_text_width(test_line, scale, font_dict) > max_width \
                and line != "":
            lines.append(line)
            line = word + " "
        else:
            line = test_line

    if line != "":
        lines.append(line)

    for text_line in lines:
        if max_y is not None and y + line_step > max_y:
            break
        draw_line(surface, text_line, x, y, scale, font_dict=font_dict)
        y += line_step