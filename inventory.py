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
INVENTORY_TITLE_OFFSET_Y = 0

_EMPTY_SLOT = {"item": None, "quantity": 0}

_EMPTY_SLOT = {"item": None, "quantity": 0}


class InventoryUI:
    def __init__(self, atlas_path=None):
        if atlas_path is None:
            atlas_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "Equipment.png"
            )
        atlas = pygame.image.load(atlas_path).convert_alpha()
        self.panel = atlas.subsurface((7, 193, 147, 83)).copy()
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

    # Use the same arrow sprite as the librarian; mirror it for the left arrow.
        button_sheet = pygame.image.load("Buttons.png").convert_alpha()
        self.arrow_right = button_sheet.subsurface((336, 303, 16, 16)).copy()
        self.arrow_left = pygame.transform.flip(self.arrow_right, True, False)

        self.is_open = False
        self.page = 0
        self.background = None
        self.drag_source = None
        self.drag_position = None
        self.panel_rect = pygame.Rect(0, 0, 0, 0)
        self.slot_rects = []
        self.weapon_rect = pygame.Rect(0, 0, 0, 0)
        self.armor_rect = pygame.Rect(0, 0, 0, 0)
        self.previous_rect = pygame.Rect(0, 0, 0, 0)
        self.next_rect = pygame.Rect(0, 0, 0, 0)
        self.close_rect = pygame.Rect(0, 0, 0, 0)

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

    def _layout(self, screen):
        scale = min(
        UI_SCALE * INVENTORY_SCALE_FACTOR,
        screen.get_width() / 147.0,
        screen.get_height() / 83.0
        )
        scale = max(1.0, scale)
        width = int(round(147 * scale))
        height = int(round(83 * scale))
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
        rect(73 + column * 16, 17 + row * 16, 16, 16)
        for row in range(INVENTORY_ROWS)
        for column in range(INVENTORY_COLUMNS)
    ]

    # The armor and sword slots align horizontally with the character's torso
    # and sword in the reference illustration.
        self.armor_rect = rect(17, 43, 14, 14)
        self.weapon_rect = rect(44, 43, 14, 14)

        self.previous_rect = rect(63, 38, 10, 10)
        self.next_rect = rect(137, 38, 8, 10)
        self.close_rect = rect(136, 1, 9, 11)
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

    @staticmethod
    def _draw_icon(screen, icon, rect, inset=3):
        if not isinstance(icon, pygame.Surface):
            return
        available = max(1, rect.width - inset * 2)
        ratio = min(available / icon.get_width(),
                    available / icon.get_height())
        size = (max(1, int(icon.get_width() * ratio)),
                max(1, int(icon.get_height() * ratio)))
        scaled = pygame.transform.scale(icon, size)
        screen.blit(scaled, scaled.get_rect(center=rect.center))

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
        if not enabled:
            return
        scaled_arrow = pygame.transform.scale(sprite, rect.size)
        screen.blit(scaled_arrow, rect)

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

    def draw(self, screen, player):
        self.ensure_player(player)
        scale, rect = self._layout(screen)

        if self.background is not None:
            screen.blit(self.background, (0, 0))
            shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 125))
            screen.blit(shade, (0, 0))

        panel = pygame.transform.scale(
            self.panel, self.panel_rect.size
        )
        screen.blit(panel, self.panel_rect)

        fonts.draw_text(
            screen,
        options.tr("INVENTORY"),
        rect(103, 5, 0, 0).x,
        rect(0, 5 + INVENTORY_TITLE_OFFSET_Y, 0, 0).y,
        scale=scale,
        spacing=0,
        centered=True
    )

        avatar_box = rect(5, 13, 59, 54)
        character = self.character_icon
        character_scale = min(
        avatar_box.width / character.get_width(),
        avatar_box.height / character.get_height()
    )
        character_size = (
        max(1, int(round(character.get_width() * character_scale))),
        max(1, int(round(character.get_height() * character_scale)))
    )
        character = pygame.transform.scale(character, character_size)
        screen.blit(
        character,
        character.get_rect(center=avatar_box.center)
    )

        for gear_rect in (self.weapon_rect, self.armor_rect):
            pygame.draw.rect(screen, (99, 66, 38), gear_rect)
            pygame.draw.rect(
            screen, (171, 126, 69), gear_rect,
            max(1, int(round(scale * 0.7)))
        )

        gear_inset = max(4, int(round(scale * 1.25)))
        self._draw_icon(screen, self.weapon_icon, self.weapon_rect, gear_inset)

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

            screen.blit(
            pygame.transform.scale(self.cell, slot_rect.size),
            slot_rect
        )

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
                item_inset
            )
                self._draw_number(
                screen,
                int(slot.get("quantity", 0)),
                slot_rect,
                scale
            )

        # Draw the hotbar frame last so the yellow border stays visible
        # and aligned with the square, even when the cell contains an item.
            if index < player.inventory_slots:
                accent = max(2, int(round(scale * 0.7)))
                frame_rect = slot_rect.inflate(-2, -2)
                pygame.draw.rect(
                screen, (241, 205, 77), frame_rect, accent
            )

        if hovered_index is not None:
            hovered_item = self._bag_slot(player, hovered_index).get("item")
            label = self._item_name(hovered_item)
        elif self.weapon_rect.collidepoint(mouse_position):
            label = options.tr("SWORD")
        elif self.armor_rect.collidepoint(mouse_position):
            label = (
                self._item_name(equipped_armor)
                if equipped_armor is not None else ""
        )
        else:
            label = ""

        if label:
            label_rect = rect(74, 66, 65, 14)
            label_scale = max(1.0, scale * 0.40)
            label = self._fit_label(
            label,
            label_rect.width - int(4 * scale),
            label_scale
        )
            fonts.draw_line(
            screen,
            label,
            label_rect.x + int(2 * scale),
            label_rect.y + int(3 * scale),
            scale=label_scale,
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

        return self.panel_rect.copy()