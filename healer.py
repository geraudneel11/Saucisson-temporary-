import pygame
import math
import dialogues
import fonts

def load_healer_ui():
    global shop_window, close_button_sheet, button_on, button_on2, shop_window, shop_window_1, shop_window_2, exit_button
    shop_window = pygame.image.load("Shop.png").convert_alpha()
    close_button_sheet = pygame.image.load("shop_exit_button.png").convert_alpha()
    button_on = shop_window.subsurface((94, 186, 37, 17))
    button_on2 = shop_window.subsurface((102, 186, 29, 17))
    shop_window_2 = shop_window.subsurface((128, 0, 128, 160))
    shop_window_1 = shop_window.subsurface((0, 0, 128, 160))
    exit_button = close_button_sheet.subsurface((109, 2, 9, 9))
previous_healer_state = None

healer_dialogues = {
    "first_meeting": [
        "Bonjour voyageur. Je me nomme Geovah.",
        "Bienvenue. J'espere pouvoir t'etre utile.",
        "Je soigne les aventuriers qui passent par ici."
    ],

    "healthy": [
        "Tu sembles en pleine forme.",
        "Tu n'as pas besoin de mes soins.",
        "Garde ton or, tu en auras besoin."
    ],

    "critical": [
        "Par les anciens... tu tiens encore debout ?",
        "Tes blessures sont graves.",
        "Tu arrives juste a temps."
    ],

    "normal": [
        "Bonjour, que puis-je faire pour toi ?",
        "Je peux soigner tes blessures.",
        "Tu sembles fatigue."
    ],
    "goodbye": [
        "Au revoir.",
        "Prends soin de toi.",
        "Que les dieux te protegent.",
        "Bonne chance.",
        "Reviens quand tu voudras."
    ]
}

def draw_healer_ui(screen, player, ui_scale, shop_window_sprite, close_rect, exit_button, button_on, button_on2, healer_state, heal_offer):
    # Scale the window sprite
    heal_final = None
    scaled_window = pygame.transform.scale(
        shop_window_sprite,
        (
            int(shop_window_sprite.get_width() * ui_scale),
            int(shop_window_sprite.get_height() * ui_scale)
        )
    )
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
    
    # Position the window centered on screen
    window_x = screen.get_width() // 2 - scaled_window.get_width() // 2
    window_y = screen.get_height() // 2 - scaled_window.get_height() // 2
    shop_rect = None
    quit_rect = None
    close_rect = None
    confirm_rect = None
    back_rect = None

    # Draw the window background
    screen.blit(scaled_window, (window_x, window_y))
    classic_font = fonts.lettersC1  # Default font for body text
    # Body text: use a smaller scale than the UI window so body remains compact
    body_scale = max(1, ui_scale * 0.75)

    if healer_state == "main":
        # Interface principale du healer
        fonts.draw_text(
            screen,
            "GEOVAH",
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
        close_button_size = int(8 * ui_scale)
        close_rect = pygame.Rect(
            window_x + scaled_window.get_width() - close_button_size - 47,
            window_y + 10,
            close_button_size,
            close_button_size
        )

        mouse_pos = pygame.mouse.get_pos()
        close_hovered = close_rect.collidepoint(mouse_pos)
        shop_hovered = shop_rect.collidepoint(mouse_pos)
        quit_hovered = quit_rect.collidepoint(mouse_pos)

        shop_font = fonts.lettersC6 if shop_hovered else fonts.lettersC1
        quit_font = fonts.lettersC6 if quit_hovered else fonts.lettersC1
        scaled_exit_button = pygame.transform.scale(
            exit_button,
            (int(exit_button.get_width() * ui_scale), int(exit_button.get_height() * ui_scale))
        )
        exit_button_rect = scaled_exit_button.get_rect(center=close_rect.center)
        if close_hovered:
            screen.blit(scaled_exit_button, exit_button_rect)

        fonts.draw_body_text(
            screen,
            "Se soigner.",
            window_x + 188,
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

    elif healer_state in ("confirm", "heal_confirm"):
        missing_hp = heal_offer["missing_hp"]
        heal_price = heal_offer["price"]
        heal_amount = heal_offer["heal_amount"]
        partial_hp = heal_offer["partial"]
        if heal_price > player.coins:
            heal_final = partial_hp
        else:
            heal_final = missing_hp
        
        # Interface de confirmation du healer
        fonts.draw_text(
            screen,
            "GEOVAH",
            window_x + scaled_window.get_width() // 2,
            window_y + 15,
            scale=ui_scale,
            spacing=-1,
            centered=True
        )
        
        visible_text = dialogues.get_visible_text()

# On enlève le dernier mot s'il est incomplet
        

        fonts.draw_body_text(
            screen,
            visible_text,
            window_x + 60,
            window_y + 80,
            scaled_window.get_width() - 80,
            fonts.lettersC1,
            body_scale,
            visible_chars=dialogues.dialogue_visible_chars
        )
        if missing_hp > 0:
            screen.blit(sclaled_button_on, (window_x + 143, window_y + 250))
            screen.blit(scaled_button_on2, (window_x + 243, window_y + 250))
            screen.blit(scaled_button_on2, (window_x + 293, window_y + 250))
            screen.blit(sclaled_button_on, (window_x + 143, window_y + 350))
            screen.blit(scaled_button_on2, (window_x + 243, window_y + 350))
            screen.blit(scaled_button_on2, (window_x + 293, window_y + 350))
        else:
            screen.blit(sclaled_button_on, (window_x + 143, window_y + 250))
            screen.blit(scaled_button_on2, (window_x + 243, window_y + 250))
            screen.blit(scaled_button_on2, (window_x + 293, window_y + 250))
        
        if missing_hp > 0:
            confirm_rect = pygame.Rect(window_x + 153, window_y + 250, 235, 17 * 4)
            back_rect = pygame.Rect(window_x + 153, window_y + 350, 235, 17 * 4)
        else:
            back_rect = pygame.Rect(window_x + 153, window_y + 250, 235, 17 * 4)
        close_button_size = int(8 * ui_scale)
        close_rect = pygame.Rect(
            window_x + scaled_window.get_width() - close_button_size - 47,
            window_y + 10,
            close_button_size,
            close_button_size
        )

        mouse_pos = pygame.mouse.get_pos()
        close_hovered = close_rect.collidepoint(mouse_pos)
        if missing_hp>0:
            confirm_hovered = confirm_rect.collidepoint(mouse_pos)
        back_hovered = back_rect.collidepoint(mouse_pos)
        if missing_hp>0:
            confirm_font = fonts.lettersC6 if confirm_hovered else fonts.lettersC1
        back_font = fonts.lettersC6 if back_hovered else fonts.lettersC1
        scaled_exit_button = pygame.transform.scale(
            exit_button,
            (int(exit_button.get_width() * ui_scale), int(exit_button.get_height() * ui_scale))
        )
        exit_button_rect = scaled_exit_button.get_rect(center=close_rect.center)
        if close_hovered:
            screen.blit(scaled_exit_button, exit_button_rect)
        if missing_hp>0:
            fonts.draw_body_text(
            screen,
            "Confirmer",
            window_x + 185,
            window_y + 267,
            scaled_window.get_width() - 40,
            font_dict=confirm_font,
            scale=body_scale
)

            fonts.draw_body_text(
            screen,
            "Retour",
            window_x + 205,
            window_y + 367,
            scaled_window.get_width() - 40,
            font_dict=back_font,
            scale=body_scale
)
        else:
            fonts.draw_body_text(
            screen,
            "Retour",
            window_x + 205,
            window_y + 267,
            scaled_window.get_width() - 40,
            font_dict=back_font,
            scale=body_scale)
    elif healer_state == "goodbye":

        fonts.draw_text(
        screen,
        "GEOVAH",
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
        scaled_window.get_width() - 0,
        fonts.lettersC1,
        body_scale
    )
        heal_offer = None
        healer_state = "main"
    return close_rect, shop_rect, quit_rect, confirm_rect, back_rect
    