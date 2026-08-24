import pygame
import math
import fonts
import dialogues
import random
from settings import * 
from classes import Potion

def load_merchant_ui():
    global shop_window
    global shop_window_1
    global shop_window_2
    global close_button_sheet
    global exit_button
    global button_on
    global button_on2
    global arrow_right
    global pressed_arrow_right
    global merchant1_page
    global merchant1_max_page
    global little_potion_sprite
    global scaled_little_potion
    global merchant_inventory 

    shop_window = pygame.image.load("Shop.png").convert_alpha()
    button_window = pygame.image.load("Buttons.png").convert_alpha()

    little_potion_sheet = pygame.image.load("Fiole_de_soin.png").convert_alpha()

    close_button_sheet = pygame.image.load("shop_exit_button.png").convert_alpha()

    shop_window_1 = shop_window.subsurface((0, 0, 128, 160))
    shop_window_2 = shop_window.subsurface((128, 0, 128, 160))

    button_on = shop_window.subsurface((94, 186, 37, 17))
    button_on2 = shop_window.subsurface((102, 186, 29, 17))
    exit_button = close_button_sheet.subsurface((109, 2, 9, 9))
    arrow_right  = button_window.subsurface((336, 303, 16, 16))
    pressed_arrow_right = button_window.subsurface((352, 303, 16, 16))
    little_potion_sprite = little_potion_sheet.subsurface(24, 23, 16, 17)
    scaled_little_potion = pygame.transform.scale(
        little_potion_sprite,
        (
            int(little_potion_sprite.get_width() * UI_SCALE),
            int(little_potion_sprite.get_height() * UI_SCALE)
        )
    )
    merchant_inventory = [Potion(scaled_little_potion)]
    merchant1_page = 1
    merchant1_max_page = max(1, math.ceil(len(merchant_inventory) / 6))
merchant_hover_text = ""
merchant_click_text = ""

last_hover_slot = None

merchant_message_timer = 0
MERCHANT_MESSAGE_DURATION = 120  
previous_merchant_state = None
merchant_items = [
    "little heal potion"
]
possible_items = [
    Potion,
]
merchant_hover_text = ""
merchant_message = ""
merchant_hover_slot = None
merchant_pages = [
    [None] * 6,   # page 1
    [None] * 6,   # page 2
    [None] * 6,   # page 3
    [None] * 6    # page 4
]
def refresh_shop():

    global merchant_inventory

    merchant_inventory.clear()

    for item_class in possible_items:

        if random.random() < 0.7:

            potion = Potion(scaled_little_potion)

            potion.stock = random.randint(
                potion.max_stock // 2,
                potion.max_stock
            )

            merchant_inventory.append(potion)
merchant_1_dialogues = {
    "first_meeting": [
        "Salut, moi c'est Languillan. Je suis marchand et apprenti alchimiste.",
        "Bienvenue. Je peux te vendre ce que tu veux.",
        "Cela faisait longtemps que je n'avait pas vu de guerriers."
    ],
    "normal": [
        "Te revoila, j'ai fais le plein de produits.",
        "Salut guerrier, comment vas-tu ?",
        "Que puis-je faire pour toi ?"
    ],
    "goodbye": [
        "Au revoir.",
        "Prends soin de toi.",
        "Bonne chance.",
        "Reviens quand tu voudras."
    ]
}
def set_hover_text(text):

    global merchant_hover_text
    global last_hover_slot

    if merchant_hover_text != text:
        merchant_hover_text = text
        dialogues.start_dialogue(text, speed=1)


def set_click_text(text):

    global merchant_click_text
    global merchant_message_timer

    merchant_click_text = text
    merchant_message_timer = MERCHANT_MESSAGE_DURATION

    dialogues.start_dialogue(text, speed=1)
def update_messages():

    global merchant_click_text
    global merchant_message_timer

    if merchant_message_timer > 0:

        merchant_message_timer -= 1

        if merchant_message_timer == 0:

            merchant_click_text = ""

            if merchant_hover_text != "":
                dialogues.start_dialogue(
                    merchant_hover_text,
                    speed=1
                )
def draw_merchant_ui(
    screen,
    ui_scale,
    close_rect,
    merchant_state,
    button_on, button_on2
                    ):	
    global back_rect_2
    body_scale = max(1, ui_scale * 0.75)
    body_scale_2 = max(1, ui_scale * 0.62)
    classic_font = fonts.lettersC1
    sclaled_button_on = pygame.transform.scale(
        button_on,
        (
            int(button_on.get_width() * ui_scale),
            int(button_on.get_height() * ui_scale)
        )
    )
    scaled_button_on2 = pygame.transform.scale(
        button_on2,
        (
            int(button_on2.get_width() * ui_scale),
            int(button_on2.get_height() * ui_scale)
        )
    )
    scaled_arrow_right = pygame.transform.scale(
        arrow_right,
        (
            int(arrow_right.get_width() * ui_scale),
            int(arrow_right.get_height() * ui_scale)
        )
    )
    scaled_arrow_left = pygame.transform.scale(
        arrow_right,
        (
            int(arrow_right.get_width() * ui_scale),
            int(arrow_right.get_height() * ui_scale)
        )
    )
    scaled_pressed_arrow_right = pygame.transform.scale(
        pressed_arrow_right,
        (
            int(arrow_right.get_width() * ui_scale),
            int(arrow_right.get_height() * ui_scale)
        )
    )
    scaled_pressed_arrow_left = pygame.transform.scale(
        pressed_arrow_right,
        (
            int(arrow_right.get_width() * ui_scale),
            int(arrow_right.get_height() * ui_scale)
        )
    )
    scaled_pressed_arrow_left2 = pygame.transform.flip(scaled_pressed_arrow_left, True, False)
    scaled_arrow_left2 = pygame.transform.flip(scaled_arrow_left, True, False)
    close_rect = None
    shop_rect = None
    quit_rect = None
    back_rect_2 = None
    left_arrow_rect = None
    right_arrow_rect = None
    slot_rects = []

    if merchant_state == "main":
        scaled_window = pygame.transform.scale(
        shop_window_1,
    (
        int(shop_window_1.get_width()*ui_scale),
        int(shop_window_1.get_height()*ui_scale)
    )
    )

        window_x = screen.get_width()//2-scaled_window.get_width()//2
        window_y = screen.get_height()//2-scaled_window.get_height()//2

        screen.blit(scaled_window,(window_x,window_y))
        fonts.draw_text(
            screen,
            "LANGUILLAN",
            window_x + scaled_window.get_width() // 2,
            window_y + 15,
            scale=ui_scale,
            spacing=-1,
            centered=True
        )
        visible_text = dialogues.get_visible_text()

        fonts.draw_body_text(
            screen,
            visible_text,
            window_x + 60,
            window_y + 80,
            scaled_window.get_width() - 80,
            classic_font,
            body_scale
        )
        screen.blit(sclaled_button_on, (window_x + 143, window_y + 250))
        screen.blit(scaled_button_on2, (window_x + 243, window_y + 250))
        screen.blit(scaled_button_on2, (window_x + 293, window_y + 250))
        screen.blit(sclaled_button_on, (window_x + 143, window_y + 350))
        screen.blit(scaled_button_on2, (window_x + 243, window_y + 350))
        screen.blit(scaled_button_on2, (window_x + 293, window_y + 350))

        shop_rect = pygame.Rect(window_x + 153, window_y + 250, 235, 17 * 4)
        quit_rect = pygame.Rect(window_x + 153, window_y + 350, 235, 17 * 4)
        mouse_pos = pygame.mouse.get_pos()
        shop_hovered = shop_rect.collidepoint(mouse_pos)
        quit_hovered = quit_rect.collidepoint(mouse_pos)
        shop_font = fonts.lettersC6 if shop_hovered else fonts.lettersC1
        quit_font = fonts.lettersC6 if quit_hovered else fonts.lettersC1

        fonts.draw_body_text(
            screen,
            "Acheter",
            window_x + 217,
            window_y + 267,
            scaled_window.get_width() - 40,
            font_dict=shop_font,
            scale=body_scale
        )
        fonts.draw_body_text(
            screen,
            "Quitter",
            window_x + 217,
            window_y + 367,
            scaled_window.get_width() - 40,
            scale=body_scale,
            font_dict=quit_font
        )
        scaled_exit = pygame.transform.scale(
        exit_button,
    (
        int(exit_button.get_width()*ui_scale),
        int(exit_button.get_height()*ui_scale)
    )
)
        close_button_size = int(8*ui_scale)

        close_rect = pygame.Rect(
        window_x+scaled_window.get_width()-close_button_size-47,
        window_y+10,
        close_button_size,
        close_button_size)
        mouse = pygame.mouse.get_pos()

        if close_rect and close_rect.collidepoint(mouse):

            rect = scaled_exit.get_rect(center=close_rect.center)
            screen.blit(scaled_exit,rect)

    elif merchant_state == "shop":
        scaled_window = pygame.transform.scale(
        shop_window_2,
    (
        int(shop_window_2.get_width() * ui_scale),
        int(shop_window_2.get_height() * ui_scale)
    )
    )
        
        window_x = screen.get_width() // 2 - scaled_window.get_width() // 2
        window_y = screen.get_height() // 2 - scaled_window.get_height() // 2
        screen.blit(scaled_window, (window_x, window_y))

        fonts.draw_text(
        screen,
        "LANGUILLAN",
        window_x + scaled_window.get_width() // 2,
        window_y + 15,
        scale=ui_scale,
        spacing=-1,
        centered=True
    )
        mouse = pygame.mouse.get_pos()
        screen.blit(sclaled_button_on, (window_x + 50, window_y + 575))
        screen.blit(scaled_button_on2, (window_x + 150, window_y + 575))
        screen.blit(scaled_button_on2, (window_x + 200, window_y + 575))

        back_rect_2 = pygame.Rect(
        window_x + 60,
        window_y + 575,
        235,
        17 * 4
    )
        left_arrow_rect = pygame.Rect(
        window_x + 325,
        window_y + 567,
        16*ui_scale,
        16*ui_scale
    )
        right_arrow_rect = pygame.Rect(
        window_x + 430,
        window_y + 567,
        16*ui_scale,
        16*ui_scale
    )
        if right_arrow_rect and right_arrow_rect.collidepoint(mouse):
            screen.blit(scaled_pressed_arrow_right, (window_x + 430, window_y + 567))
        else:
            screen.blit(scaled_arrow_right, (window_x + 430, window_y + 567))
        if left_arrow_rect and left_arrow_rect.collidepoint(mouse):
            screen.blit(scaled_pressed_arrow_left2, (window_x + 325, window_y + 567))
        else:	
            screen.blit(scaled_arrow_left2, (window_x + 325, window_y + 567))	
        mouse = pygame.mouse.get_pos()

        back_font = (
        fonts.lettersC6
        if back_rect_2.collidepoint(mouse)
        else fonts.lettersC1
    )
        fonts.draw_body_text(
        screen,
        "Retour",
        window_x + 130,
        window_y + 592,
        scaled_window.get_width(),
        back_font,
        body_scale
    )
        page_text = f"{merchant1_page} sur {merchant1_max_page}"
        fonts.draw_body_text(
        screen,
        page_text,
        window_x + 367,      # à ajuster selon ton interface
        window_y + 596,
        scaled_window.get_width(),
        fonts.lettersC1,
        body_scale_2
    )
        scaled_exit = pygame.transform.scale(
        exit_button,
    (
        int(exit_button.get_width()*ui_scale),
        int(exit_button.get_height()*ui_scale)
    )
    )
        close_button_size = int(8*ui_scale)

        close_rect = pygame.Rect(
        window_x+scaled_window.get_width()-close_button_size-47,
        window_y+10,
        close_button_size,
        close_button_size)
        mouse = pygame.mouse.get_pos()
        merchant_hover_text = ""
        slot_rects = [

        pygame.Rect(window_x + 95,  window_y + 77, 21*ui_scale, 21*ui_scale),
        pygame.Rect(window_x + 239, window_y + 77, 21*ui_scale, 21*ui_scale),
        pygame.Rect(window_x + 382, window_y + 77, 21*ui_scale, 21*ui_scale),
        pygame.Rect(window_x + 95, window_y + 329, 21*ui_scale, 21*ui_scale),

        pygame.Rect(window_x + 239,  window_y + 329, 21*ui_scale, 21*ui_scale),
        pygame.Rect(window_x + 382, window_y + 329, 21*ui_scale, 21*ui_scale),
        ]
        start = (merchant1_page - 1) * 6
        end = start + 6
        current_items = merchant_inventory[start:end]
        mouse = pygame.mouse.get_pos()
        global merchant_message
        global last_hover_slot
        hover_slot = None
        for i, rect in enumerate(slot_rects):
            has_item = i < len(current_items)
            if rect.collidepoint(mouse):

                marge = 5
                if has_item:
                    color = (255,255,255)      # blanc
                else:
                    color = (255,0,0)  
                hover_rect = pygame.Rect(
                    rect.x + marge,
                    rect.y + marge,
                    rect.width - marge * 2,
                    rect.height - marge * 2
                    
        )
                pygame.draw.rect(screen, (color), hover_rect, 3)
        hover_slot = None
        for i, rect in enumerate(slot_rects):
            has_item = i < len(current_items)
            if rect.collidepoint(mouse):

                hover_slot = (merchant1_page, i)
                if hover_slot != last_hover_slot:
                    last_hover_slot = hover_slot
                    if has_item:
                        item = current_items[i]
                        if item.stock > 0:
                            set_hover_text(f"{item.name}: {item.price} or")
                        else:
                            set_hover_text(
                            item.name + " (Rupture de stock)"
                        )
                    else:
                        set_hover_text(
                        "La case est vide"
                    )
                visible_text = dialogues.get_visible_text()

                fonts.draw_body_text(
                screen,
                visible_text,
                window_x + 80,
                window_y + 520,
                scaled_window.get_width() - 160,
                fonts.lettersC1,
                body_scale
            )
        if hover_slot is None:
            last_hover_slot = None

                # Temporairement on considère toutes les cases comme pleines
        for i, item in enumerate(current_items):

            rect = slot_rects[i]
            item.rect = rect.copy()
            sprite_rect = item.sprite.get_rect(center=rect.center)
            screen.blit(item.sprite, sprite_rect)
            fonts.draw_body_text(
            screen,
            str(item.stock),
            rect.centerx - 7,
            rect.bottom + 2,
            scaled_window.get_width(),
            fonts.lettersC1,
            body_scale,
        )
        if close_rect and close_rect.collidepoint(mouse):

            rect = scaled_exit.get_rect(center=close_rect.center)
            screen.blit(scaled_exit,rect)

    return close_rect, shop_rect, quit_rect, left_arrow_rect, right_arrow_rect, slot_rects