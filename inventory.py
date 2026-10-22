import os

import pygame

import fonts
import options
from classes import ArmorOffer
from settings import UI_SCALE


INVENTORY_CAPACITY = 24
INVENTORY_PAGE_SIZE = 12
INVENTORY_COLUMNS = 4
INVENTORY_ROWS = 3

# Increase this factor to enlarge the inventory panel and its contents.
INVENTORY_SCALE_FACTOR = 1.25

# Vertical title adjustment in panel source pixels; edit this value as needed.
INVENTORY_TITLE_OFFSET_Y = -4
INVENTORY_TITLE_OFFSET_X = -1

# ---------------------------------------------------------------
# PANEL GEOMETRY
# Every value below is in Equipment.png pixels. The panel is the
# (7, 193, 147, 83) crop of the atlas; the two plain beige columns of
# the item area are duplicated on both sides so the page arrows get
# their own room inside the frame, without touching the slots nor the
# wooden border.
# ---------------------------------------------------------------
PANEL_CROP = (7, 193, 147, 83)
PANEL_SIDE_PAD = 10                 # extra beige columns per side
PANEL_CREAM_LEFT = 67               # first beige column of the item area
PANEL_CREAM_WIDTH = 76 + 2 * PANEL_SIDE_PAD
# Plain columns (beige body + green title) duplicated to widen the panel.
PANEL_WIDEN_COLUMNS = (100, 110)

SLOT_SIZE = 16                      # bag slot sprite size
GRID_TOP = 17
GRID_WIDTH = INVENTORY_COLUMNS * SLOT_SIZE
GRID_LEFT = PANEL_CREAM_LEFT + (PANEL_CREAM_WIDTH - GRID_WIDTH) // 2

GEAR_SLOT_SIZE = 14                 # armor / weapon squares

# Character avatar: drawn in the left brown area, nudged a bit left.
AVATAR_BOX = (5, 13, 59, 54)
CHARACTER_OFFSET_X = -6             # negative : vers la gauche
CHARACTER_OFFSET_Y = 0
# Sword grip, in character-icon pixels: the weapon slot is centered on
# it so it lines up with the blade, like on the reference panel.
SWORD_ANCHOR = (38.5, 26.5)

# Page arrows: kept inside the beige area, with a gap before the grid.
ARROW_WIDTH = 8
ARROW_HEIGHT = 12
ARROW_GAP = 4
ARROW_TOP = 35

# Item name label, under the slot grid.
LABEL_TOP = 66
LABEL_HEIGHT = 14
LABEL_MARGIN = 3                    # marge avec les bords beiges
LABEL_SCALE = 0.60  
# ---------------------------------------------------------------
# FINE TUNING
# All values are in slot source pixels (the slot sprite is 16 x 16):
# a value of 1 moves the element by one pixel of Equipment.png, so it
# is automatically multiplied by the screen scale.
# ---------------------------------------------------------------
# Item icons inside the bag slots.
ITEM_OFFSET_X = 0.1
ITEM_OFFSET_Y = -1
# Armor icon inside its equipment slot.
GEAR_OFFSET_X = 0
GEAR_OFFSET_Y = 0
# Yellow hotbar frames (offset + thickness grows INWARD, never outside
# the slot).
HOTBAR_FRAME_OFFSET_X = 0
HOTBAR_FRAME_OFFSET_Y = -1
HOTBAR_FRAME_SIZE_OFFSET = -1           

_EMPTY_SLOT = {"item": None, "quantity": 0}

CLOSE_OFFSET_X = 1
CLOSE_OFFSET_Y = 0.25


class InventoryUI:
    def __init__(self, atlas_path=None):
        if atlas_path is None:
            atlas_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
              
                "Equipment.png"
            )
        
        asset_dir = os.path.dirname(os.path.abspath(atlas_path))
        atlas = pygame.image.load(atlas_path).convert_alpha()
        self.panel = self._widen_panel(
            atlas.subsurface(PANEL_CROP).copy(), PANEL_SIDE_PAD
        )
        self.panel_size = self.panel.get_size()
        self.cell = atlas.subsurface((80, 17, 16, 16)).copy()
        self.weapon_icon = atlas.subsurface((112, 352, 13, 12)).copy()
        self.armor_icon = atlas.subsurface((128, 352, 13, 13)).copy()

        # Crop the armored character from the reference atlas.
        self.character_icon = atlas.subsurface((50, 336, 43, 46)).copy()
        character_bounds = self.character_icon.get_bounding_rect(min_alpha=1)
        if character_bounds.width and character_bounds.height:
            self.character_icon = self.character_icon.subsurface(
                character_bounds
            ).copy()

        # Same arrow sprite as the librarian, mirrored for the left arrow.
        # The sprite is cropped to its ink so it fills its rect exactly.
        button_sheet = pygame.image.load(
            os.path.join(asset_dir, "Buttons.png")
        ).convert_alpha()
        arrow = button_sheet.subsurface((336, 303, 16, 16)).copy()
        arrow_bounds = arrow.get_bounding_rect()
        if arrow_bounds.width and arrow_bounds.height:
            arrow = arrow.subsurface(arrow_bounds).copy()
        self.arrow_right = arrow
        self.arrow_left = pygame.transform.flip(arrow, True, False)
        self.close_button_sheet = pygame.image.load("Shop_exit_button.png").convert_alpha()
        
        self.exit_button = self.close_button_sheet.subsurface(
    (109, 2, 9, 9)
        ).copy()
        self.is_open = False
        self.page = 0
        self.background = None
        self.drag_source = None
        self.drag_position = None
        self.panel_rect = pygame.Rect(0, 0, 0, 0)
        self.slot_rects = []
        self.character_rect = pygame.Rect(0, 0, 0, 0)
        self.armor_rect = pygame.Rect(0, 0, 0, 0)
        self.weapon_rect = pygame.Rect(0, 0, 0, 0)
        self.previous_rect = pygame.Rect(0, 0, 0, 0)
        self.next_rect = pygame.Rect(0, 0, 0, 0)
        self.close_rect = pygame.Rect(0, 0, 0, 0)
        self.label_rect = pygame.Rect(0, 0, 0, 0)
        self.title_center_x = 0
        self._panel_cache = (None, None)
        self._character_cache = (None, None)
        self._cell_cache = (None, None)
        self._shade_cache = (None, None)
        self._icon_cache = {}
        self.exit_button = self.close_button_sheet.subsurface((109, 2, 9, 9))

    @staticmethod
    def _widen_panel(panel, pad):
        # Duplicate two plain columns (beige body, green title, brown
        # bottom) so the item area grows without distorting the frame,
        # the title bar or the close button.
        if pad <= 0:
            return panel
        width, height = panel.get_size()
        left_column, right_column = PANEL_WIDEN_COLUMNS
        wide = pygame.Surface((width + 2 * pad, height), pygame.SRCALPHA)
        wide.blit(panel, (0, 0), (0, 0, left_column, height))
        for offset in range(pad):
            wide.blit(
                panel, (left_column + offset, 0), (left_column, 0, 1, height)
            )
        wide.blit(
            panel, (left_column + pad, 0),
            (left_column, 0, right_column - left_column, height)
        )
        for offset in range(pad):
            wide.blit(
                panel, (right_column + pad + offset, 0),
                (right_column, 0, 1, height)
            )
        wide.blit(
            panel, (right_column + 2 * pad, 0),
            (right_column, 0, width - right_column, height)
        )
        return wide

    @staticmethod
    def ensure_player(player):
        if not isinstance(getattr(player, "inventory", None), list):
            player.inventory = []
        if len(player.inventory) < INVENTORY_CAPACITY:
            player.inventory.extend(
                {"item": None, "quantity": 0}
                for _ in range(INVENTORY_CAPACITY - len(player.inventory))
            )
        player.inventory_slots = max(
            3, min(INVENTORY_CAPACITY,
                   int(getattr(player, "inventory_slots", 3)))
        )
        player.selected_slot %= player.inventory_slots
        if not hasattr(player, "equipped_armor_item"):
            tier = int(getattr(player, "equipment_level", 0))
            player.equipped_armor_item = (
                ArmorOffer(tier) if tier > 0 else None
            )

    def open(self, background, player):
        self.ensure_player(player)
        self.background = background.copy()
        self.page = 0
        self.drag_source = None
        self.drag_position = None
        self.is_open = True
        self._layout(background)

    def close(self):
        self.is_open = False
        self.drag_source = None
        self.drag_position = None
        self.background = None

    def _character_rect(self, rect, scale):
        # Character fitted in the avatar box, then nudged by
        # CHARACTER_OFFSET_X / _Y (panel source pixels).
        box = rect(*AVATAR_BOX)
        icon = self.character_icon
        if icon.get_width() <= 0 or icon.get_height() <= 0:
            return box
        fit = min(
            box.width / float(icon.get_width()),
            box.height / float(icon.get_height())
        )
        character_rect = pygame.Rect(
            0, 0,
            max(1, int(round(icon.get_width() * fit))),
            max(1, int(round(icon.get_height() * fit)))
        )
        character_rect.center = box.center
        character_rect.x += int(round(CHARACTER_OFFSET_X * scale))
        character_rect.y += int(round(CHARACTER_OFFSET_Y * scale))
        return character_rect

    def _layout(self, screen):
        panel_width, panel_height = self.panel_size
        scale = min(
            UI_SCALE * INVENTORY_SCALE_FACTOR,
            screen.get_width() / float(panel_width),
            screen.get_height() / float(panel_height)
        )
        scale = max(1.0, scale)
        width = int(round(panel_width * scale))
        height = int(round(panel_height * scale))
        x = (screen.get_width() - width) // 2
        y = (screen.get_height() - height) // 2
        self.panel_rect = pygame.Rect(x, y, width, height)

        def rect(local_x, local_y, local_w, local_h):
            return pygame.Rect(
                x + int(round(local_x * scale)),
                y + int(round(local_y * scale)),
                max(1, int(round(local_w * scale))),
                max(1, int(round(local_h * scale)))
            )

        self.slot_rects = [
            rect(GRID_LEFT + column * SLOT_SIZE,
                 GRID_TOP + row * SLOT_SIZE, SLOT_SIZE, SLOT_SIZE)
            for row in range(INVENTORY_ROWS)
            for column in range(INVENTORY_COLUMNS)
        ]

        # The armor slot sits exactly on the character's centre, the
        # weapon slot on the sword grip of the same character.
        self.character_rect = self._character_rect(rect, scale)
        gear_size = max(1, int(round(GEAR_SLOT_SIZE * scale)))
        icon = self.character_icon
        sword_x = self.character_rect.left + int(round(
            SWORD_ANCHOR[0] * self.character_rect.width
            / float(max(1, icon.get_width()))
        ))
        sword_y = self.character_rect.top + int(round(
            SWORD_ANCHOR[1] * self.character_rect.height
            / float(max(1, icon.get_height()))
        ))

        self.armor_rect = pygame.Rect(0, 0, gear_size, gear_size)
        self.armor_rect.center = self.character_rect.center
        self.weapon_rect = pygame.Rect(0, 0, gear_size, gear_size)
        self.weapon_rect.center = (sword_x, sword_y)

        # Arrows stay fully inside the beige area, clear of the slots.
        self.previous_rect = rect(
            GRID_LEFT - ARROW_GAP - ARROW_WIDTH, ARROW_TOP,
            ARROW_WIDTH, ARROW_HEIGHT
        )
        self.next_rect = rect(
            GRID_LEFT + GRID_WIDTH + ARROW_GAP, ARROW_TOP,
            ARROW_WIDTH, ARROW_HEIGHT
        )
        # Close button: the beige plate of the atlas spans 157..163 x
        # and 2..8 y, the click zone is a bit larger around it.
        self.close_rect = rect(
    panel_width - 12 + CLOSE_OFFSET_X,
    1 + CLOSE_OFFSET_Y,
    9,
    9
)
        self.label_rect = rect(
            PANEL_CREAM_LEFT + LABEL_MARGIN, LABEL_TOP,
            PANEL_CREAM_WIDTH - 2 * LABEL_MARGIN, LABEL_HEIGHT
        )
        self.title_center_x = (
            x + int(round((66 + panel_width - 1) / 2.0 * scale))
            + int(round(INVENTORY_TITLE_OFFSET_X * scale))
        )
        return scale, rect

    @staticmethod
    def _item_icon(item, fallback):
        sprite = getattr(item, "sprite", None) if item is not None else None
        if isinstance(sprite, pygame.Surface):
            return sprite
        return fallback

    @staticmethod
    def _item_name(item):
        if item is None:
            return ""
        if isinstance(item, ArmorOffer):
            return f"{options.tr('Armor tier')} {item.tier}"
        return options.tr(str(getattr(item, "name", "ITEM")))

    def _draw_icon(self, screen, icon, rect, inset=3, offset=(0, 0)):
        if not isinstance(icon, pygame.Surface):
            return

        scaled = self._scaled_icon(icon, rect, inset)
        center = (
            rect.centerx + int(offset[0]),
            rect.centery + int(offset[1])
        )
        screen.blit(scaled, scaled.get_rect(center=center))

    @staticmethod
    def _draw_number(screen, value, rect, scale):
        if value <= 0:
            return
        text = str(value)
        text_scale = max(1.0, scale * 0.72)
        width = fonts.get_text_width(
            text, text_scale, fonts.lettersC1
        )
        x = rect.right - int(round(2 * scale)) - int(width)
        glyph_height = max(
            (fonts.lettersC1[char].get_height()
             for char in text if char in fonts.lettersC1),
            default=6
        )
        y = (rect.bottom - int(round(2 * scale))
             - int(round(glyph_height * text_scale)))
        for char in text:
            glyph = fonts.lettersC1.get(char)
            if glyph is None:
                continue
            white_glyph = pygame.mask.from_surface(glyph).to_surface(
                setcolor=(255, 255, 255, 255),
                unsetcolor=(0, 0, 0, 0)
            )
            glyph_size = (
                max(1, int(round(glyph.get_width() * text_scale))),
                max(1, int(round(glyph.get_height() * text_scale)))
            )
            white_glyph = pygame.transform.scale(white_glyph, glyph_size)
            screen.blit(white_glyph, (x, y))
            x += int(round(glyph.get_width() * text_scale)) + 1

    @staticmethod
    def _draw_arrow(screen, sprite, rect, enabled):
        if not enabled or not isinstance(sprite, pygame.Surface):
            return
        # Keep the arrow's proportions and centre it in its rect so it
        # can never stick out of the frame.
        ratio = min(
            rect.width / float(max(1, sprite.get_width())),
            rect.height / float(max(1, sprite.get_height()))
        )
        size = (max(1, int(round(sprite.get_width() * ratio))),
                max(1, int(round(sprite.get_height() * ratio))))
        scaled = pygame.transform.scale(sprite, size)
        screen.blit(scaled, scaled.get_rect(center=rect.center))

    @staticmethod
    def _fit_label(text, max_width, scale):
        text = options.tr(str(text)).upper()
        if fonts.get_text_width(text, scale, fonts.lettersC1) <= max_width:
            return text
        while text and fonts.get_text_width(
                text + "...", scale, fonts.lettersC1) > max_width:
            text = text[:-1]
        return text + "..." if text else ""

    @staticmethod
    def _bag_slot(player, index):
        if 0 <= index < len(player.inventory):
            return player.inventory[index]
        return _EMPTY_SLOT

    def _hovered_index(self, position):
        for index, rect in enumerate(self.slot_rects):
            if rect.collidepoint(position):
                return self.page * INVENTORY_PAGE_SIZE + index
        return None

    @staticmethod
    def _is_armor(item):
        return isinstance(item, ArmorOffer)

    @staticmethod
    def _equip(player, item, callback):
        tier = int(item.tier) if item is not None else 0
        player.equipped_armor_item = item
        if callback is not None:
            callback(tier)
        else:
            player.equipment_level = tier

    def _finish_drag(self, position, player, equip_armor):
        source = self.drag_source
        self.drag_source = None
        self.drag_position = None
        if source is None:
            return

        target_index = self._hovered_index(position)
        source_kind, source_value = source

        if source_kind == "bag":
            source_index = source_value
            source_slot = self._bag_slot(player, source_index)
            source_item = source_slot.get("item")
            if source_item is None:
                return

            if target_index is not None:
                if target_index == source_index:
                    return
                target_slot = self._bag_slot(player, target_index)
                target_item = target_slot.get("item")
                if (target_item is not None
                        and target_item.__class__ is source_item.__class__
                        and target_item.name == source_item.name
                        and not self._is_armor(source_item)):
                    maximum = player.item_max_per_slot()
                    moved = min(
                        source_slot["quantity"],
                        max(0, maximum - target_slot["quantity"])
                    )
                    target_slot["quantity"] += moved
                    source_slot["quantity"] -= moved
                    if source_slot["quantity"] <= 0:
                        source_slot["item"] = None
                        source_slot["quantity"] = 0
                else:
                    source_slot["item"], target_slot["item"] = (
                        target_slot["item"], source_slot["item"]
                    )
                    source_slot["quantity"], target_slot["quantity"] = (
                        target_slot["quantity"], source_slot["quantity"]
                    )
                return

            if self.armor_rect.collidepoint(position) and self._is_armor(source_item):
                old_armor = player.equipped_armor_item
                if old_armor is None and player.equipment_level > 0:
                    old_armor = ArmorOffer(
                        player.equipment_level, self.armor_icon
                    )
                self._equip(player, source_item, equip_armor)
                source_slot["item"] = old_armor
                source_slot["quantity"] = 1 if old_armor else 0

        elif source_kind == "armor":
            if target_index is None:
                return
            target_slot = self._bag_slot(player, target_index)
            target_item = target_slot.get("item")
            if target_item is not None and not self._is_armor(target_item):
                return
            old_armor = player.equipped_armor_item
            if old_armor is None and player.equipment_level > 0:
                old_armor = ArmorOffer(
                    player.equipment_level, self.armor_icon
                )
            if target_item is None:
                target_slot["item"] = old_armor
                target_slot["quantity"] = 1 if old_armor else 0
                self._equip(player, None, equip_armor)
            else:
                self._equip(player, target_item, equip_armor)
                target_slot["item"] = old_armor
                target_slot["quantity"] = 1 if old_armor else 0

    def handle_event(self, event, player, equip_armor=None,
                 interact_key=pygame.K_e):
        if not self.is_open:
            return
        self.ensure_player(player)

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, interact_key):
                self.close()
                return

        if event.type == pygame.MOUSEMOTION:
            if self.drag_source is not None:
                self.drag_position = event.pos

            # Dragging over an enabled arrow changes page immediately.
                if (self.page > 0
                        and self.previous_rect.collidepoint(event.pos)):
                    self.page -= 1
                elif (self.page < 1
                    and self.next_rect.collidepoint(event.pos)):
                    self.page += 1

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                self.close()
                return
            if self.previous_rect.collidepoint(event.pos):
                self.page = max(0, self.page - 1)
                return
            if self.next_rect.collidepoint(event.pos):
                self.page = min(1, self.page + 1)
                return

            index = self._hovered_index(event.pos)
            if index is not None:
                if self._bag_slot(player, index).get("item") is not None:
                    self.drag_source = ("bag", index)
                    self.drag_position = event.pos
                return

            if (self.armor_rect.collidepoint(event.pos)
                    and player.equipment_level > 0):
                self.drag_source = ("armor", None)
                self.drag_position = event.pos

        if (event.type == pygame.MOUSEBUTTONUP and event.button == 1
                and self.drag_source is not None):
            self._finish_drag(event.pos, player, equip_armor)

    def _scaled_panel(self):
        size = self.panel_rect.size
        if self._panel_cache[0] != size:
            self._panel_cache = (
                size, pygame.transform.scale(self.panel, size)
            )
        return self._panel_cache[1]

    def _scaled_cell(self, slot_rect):
        if self._cell_cache[0] != slot_rect.size:
            self._cell_cache = (
                slot_rect.size,
                pygame.transform.scale(self.cell, slot_rect.size)
            )
        return self._cell_cache[1]

    def _scaled_icon(self, icon, rect, inset):
        # Resized item sprites are cached: the bag redraws them every
        # frame while the window is open.
        key = (id(icon), rect.width, rect.height, inset)
        cached = self._icon_cache.get(key)
        if cached is not None and cached[0] is icon:
            return cached[1]
        available = max(1, rect.width - inset * 2)
        ratio = min(available / icon.get_width(),
                    available / icon.get_height())
        size = (max(1, int(icon.get_width() * ratio)),
                max(1, int(icon.get_height() * ratio)))
        scaled = pygame.transform.scale(icon, size)
        if len(self._icon_cache) > 128:
            self._icon_cache.clear()
        # The source surface is kept in the cache so its id can never be
        # reused by another sprite while the entry is alive.
        self._icon_cache[key] = (icon, scaled)
        return scaled

    def _shade(self, screen):
        if self._shade_cache[0] != screen.get_size():
            shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 125))
            self._shade_cache = (screen.get_size(), shade)
        return self._shade_cache[1]

    def _scaled_character(self):
        size = self.character_rect.size
        if self._character_cache[0] != size:
            self._character_cache = (
                size, pygame.transform.scale(self.character_icon, size)
            )
        return self._character_cache[1]

    def draw(self, screen, player):
        self.ensure_player(player)
        scale, rect = self._layout(screen)

        if self.background is not None:
            screen.blit(self.background, (0, 0))
            screen.blit(self._shade(screen), (0, 0))

        mouse_position = pygame.mouse.get_pos()
                # Red close cross on hover, exactly like the NPC windows.
        if self.close_rect.collidepoint(mouse_position):
            cross = pygame.transform.scale(
                self.exit_button, self.close_rect.size
            )
            screen.blit(cross, cross.get_rect(center=self.close_rect.center))

        screen.blit(self._scaled_panel(), self.panel_rect)

        fonts.draw_text(
            screen,
            options.tr("INVENTORY"),
            self.title_center_x,
            rect(0, 5 + INVENTORY_TITLE_OFFSET_Y, 0, 0).y,
            scale=scale,
            spacing=0,
            centered=True
        )

        # Character, fitted in its box then nudged left/right by the
        # CHARACTER_OFFSET_X / _Y settings.
        if self.character_rect.width > 0:
            screen.blit(self._scaled_character(), self.character_rect)

        for gear_rect in (self.weapon_rect, self.armor_rect):
            pygame.draw.rect(screen, (99, 66, 38), gear_rect)
            pygame.draw.rect(
                screen, (171, 126, 69), gear_rect,
                max(1, int(round(scale * 0.7)))
            )

        gear_inset = max(4, int(round(scale * 1.25)))
        

        equipped_armor = player.equipped_armor_item
        if equipped_armor is None and player.equipment_level > 0:
            equipped_armor = ArmorOffer(
                player.equipment_level, self.armor_icon
            )
            player.equipped_armor_item = equipped_armor

        if equipped_armor is not None:
            self._draw_icon(
                screen,
                self._item_icon(equipped_armor, self.armor_icon),
                self.armor_rect,
                gear_inset
            )

        start = self.page * INVENTORY_PAGE_SIZE
        mouse_position = pygame.mouse.get_pos()
        hovered_index = self._hovered_index(mouse_position)

        for local_index, slot_rect in enumerate(self.slot_rects):
            index = start + local_index
            slot = self._bag_slot(player, index)

            screen.blit(self._scaled_cell(slot_rect), slot_rect)

            is_dragged_source = self.drag_source == ("bag", index)
            item = slot.get("item")

            if item is not None and not is_dragged_source:
                # Leave a scaled margin so large icons, such as dynamite,
                # do not touch the cell edges.
                item_inset = max(6, int(round(scale * 1.8)))
                self._draw_icon(
                    screen,
                    self._item_icon(item, self.armor_icon),
                    slot_rect,
                    item_inset,
                    (
                        int(round(ITEM_OFFSET_X * scale)),
                        int(round(ITEM_OFFSET_Y * scale))
                    )
                )
                self._draw_number(
                    screen,
                    int(slot.get("quantity", 0)),
                    slot_rect,
                    scale
                )

            # Draw the hotbar frame last so the yellow border stays
            # visible over the item. The cell sprite has a 1 source pixel
            # cream border, so the frame is inset by that border: it
            # covers the inner square (exactly the slot size) and never
            # spills over the neighbouring cell.
            if index < player.inventory_slots:
                size_offset = int(round(HOTBAR_FRAME_SIZE_OFFSET * scale))
                frame_rect = slot_rect.inflate(
                    size_offset, size_offset
                ).move(
                int(round(HOTBAR_FRAME_OFFSET_X * scale)),
                int(round(HOTBAR_FRAME_OFFSET_Y * scale))
                )
                accent = max(2, int(round(scale * 0.55)))
                pygame.draw.rect(
                screen, (241, 205, 77), frame_rect, accent
                )
        if hovered_index is not None:
            hovered_item = self._bag_slot(player, hovered_index).get("item")
            label = self._item_name(hovered_item)
        elif self.weapon_rect.collidepoint(mouse_position):
            label = ""
        elif self.armor_rect.collidepoint(mouse_position):
            label = (
                self._item_name(equipped_armor)
                if equipped_armor is not None else ""
            )
        else:
            label = ""

        if label:
            label_scale = max(1.0, scale * LABEL_SCALE)
            label = self._fit_label(
                label,
                self.label_rect.width - int(round(4 * scale)),
                label_scale
            )
            glyph_height = max(
                (fonts.lettersC1[char].get_height()
                 for char in label if char in fonts.lettersC1),
                default=6
            )
            fonts.draw_line(
                screen,
                label,
                self.label_rect.centerx,
                self.label_rect.centery
                - int(round(glyph_height * label_scale / 2.0)),
                scale=label_scale,
                centered=True,
                font_dict=fonts.lettersC1
            )

        self._draw_arrow(
            screen, self.arrow_left, self.previous_rect, self.page > 0
        )
        self._draw_arrow(
            screen, self.arrow_right, self.next_rect, self.page < 1
        )

        if self.drag_source is not None and self.drag_position is not None:
            item = None
            if self.drag_source[0] == "bag":
                item = self._bag_slot(
                    player, self.drag_source[1]
                ).get("item")
            elif self.drag_source[0] == "armor":
                item = player.equipped_armor_item

            if item is not None:
                icon = self._item_icon(
                    item,
                    self.armor_icon if self._is_armor(item)
                    else self.weapon_icon
                )
                drag_rect = pygame.Rect(
                    self.drag_position[0] - int(8 * scale),
                    self.drag_position[1] - int(8 * scale),
                    int(16 * scale),
                    int(16 * scale)
                )
                drag_inset = max(3, int(round(scale * 0.7)))
                self._draw_icon(screen, icon, drag_rect, drag_inset)

        scaled_exit = pygame.transform.scale(
    self.exit_button,
    (
        int(self.exit_button.get_width() * scale),
        int(self.exit_button.get_height() * scale)
    )
)
        if self.close_rect.collidepoint(mouse_position):
            screen.blit(
        scaled_exit,
        scaled_exit.get_rect(center=self.close_rect.center)
    )

        return self.panel_rect.copy()