import pygame
import fonts
import dialogues
import random
from settings import *
from classes import Book


def load_librarian_ui():
	global shop_window_1, exit_button, button_on, button_on2
	global arrow_right

	shop_window = pygame.image.load("Shop.png").convert_alpha()
	button_window = pygame.image.load("Buttons.png").convert_alpha()
	close_button_sheet = pygame.image.load("Shop_exit_button.png").convert_alpha()

	shop_window_1 = shop_window.subsurface((0, 0, 128, 160))

	button_on = shop_window.subsurface((94, 186, 37, 17))
	button_on2 = shop_window.subsurface((102, 186, 29, 17))
	exit_button = close_button_sheet.subsurface((109, 2, 9, 9))

	arrow_right = button_window.subsurface((336, 303, 16, 16))


# --- Livres disponibles : liste modifiable. Un seul pour l'instant,
# avec un texte de TEST (titre + pages en caractères répétés) juste
# pour vérifier que la pagination fonctionne -- à remplacer par le
# vrai "Guide de certaines mécaniques" plus tard.
librarian_books = [
	Book(
		"Botanique : les pommes",
		[
			"Les pommiers sont des arbres communs dans ce monde. On en trouve dans les villages, les vergers et parfois meme à l’etat sauvage. Pourtant, ils entretiennent un lien etrange avec la magie. Lorsqu’une ame s’envole pres d’un pommier, l’arbre semble en garder une trace, melee a sa seve. Mais lorsque trois", 
			"ames s’envolent a proximite du meme arbre, il peut alors produire un fruit impregne de magie. Ces fruits sont rares et leur pouvoir varie selon les emes qui ont nourri l’arbre. Certains peuvent guerir, d’autres transmettre un pouvoir ou provoquer des phenomenes inexplicables. Ainsi, derriere leur apparence", 
			"ordinaire, les pommiers cachent une capacite que peu de personnes connaissent."
		]
	)
]

librarian_dialogues = {
	"first_meeting": [
		"Bonjour voyageur. Je veille sur ces ouvrages depuis de nombreuses annees.",
		"Contre une piece d'or, tu peux consulter notre bibliotheque.",
	],
	"normal": [
		"Tu souhaites de nouveau consulter les livres ?",
		"Nos ouvrages n'attendent que toi.",
	],
	"not_enough_gold": [
		"Il te faut au moins une piece d'or pour consulter les livres.",
	],
	"goodbye": [
		"Que la lecture t'ait ete profitable.",
		"Reviens quand tu voudras.",
		"Au revoir.",
	]
}


def draw_librarian_ui(screen, player, ui_scale, librarian_state, current_book_index, current_page):
	"""
	Dessine la fenetre du moine bibliothecaire. librarian_state vaut
	"main" (dialogue + Payer/Retour), "books" (liste des titres +
	Quitter) ou "reading" (page en cours + fleches + Retour).

	Retourne (close_rect, pay_rect, retour_rect, book_rects, quit_rect,
	back_rect, left_arrow_rect, right_arrow_rect) -- non pertinents
	pour l'etat courant valent None (ou [] pour book_rects).
	"""
	body_scale = max(1, ui_scale * 0.75)
	classic_font = fonts.lettersC1
	mouse_pos = pygame.mouse.get_pos()

	scaled_window = pygame.transform.scale(
		shop_window_1,
		(int(shop_window_1.get_width() * ui_scale), int(shop_window_1.get_height() * ui_scale))
	)
	window_x = screen.get_width() // 2 - scaled_window.get_width() // 2
	window_y = screen.get_height() // 2 - scaled_window.get_height() // 2
	screen.blit(scaled_window, (window_x, window_y))

	scaled_button_on = pygame.transform.scale(
		button_on, (int(button_on.get_width() * ui_scale), int(button_on.get_height() * ui_scale))
	)
	scaled_button_on2 = pygame.transform.scale(
		button_on2, (int(button_on2.get_width() * ui_scale), int(button_on2.get_height() * ui_scale))
	)

	pay_rect = None
	retour_rect = None
	book_rects = []
	quit_rect = None
	back_rect = None
	left_arrow_rect = None
	right_arrow_rect = None

	fonts.draw_text(
		screen, "MOINE", window_x + scaled_window.get_width() // 2,
		window_y + 15, scale=ui_scale, spacing=-1, centered=True
	)

	def draw_two_row_buttons(label_top, top_rect_y=250, bottom_rect_y=350):
		screen.blit(scaled_button_on, (window_x + 143, window_y + top_rect_y))
		screen.blit(scaled_button_on2, (window_x + 243, window_y + top_rect_y))
		screen.blit(scaled_button_on2, (window_x + 293, window_y + top_rect_y))

	if librarian_state == "main":
		visible_text = dialogues.get_visible_text()
		fonts.draw_body_text(
			screen, visible_text, window_x + 60, window_y + 80,
			scaled_window.get_width() - 80, classic_font, body_scale
		)

		screen.blit(scaled_button_on, (window_x + 143, window_y + 250))
		screen.blit(scaled_button_on2, (window_x + 243, window_y + 250))
		screen.blit(scaled_button_on2, (window_x + 293, window_y + 250))
		screen.blit(scaled_button_on, (window_x + 143, window_y + 350))
		screen.blit(scaled_button_on2, (window_x + 243, window_y + 350))
		screen.blit(scaled_button_on2, (window_x + 293, window_y + 350))

		pay_rect = pygame.Rect(window_x + 153, window_y + 250, 235, 17 * 4)
		retour_rect = pygame.Rect(window_x + 153, window_y + 350, 235, 17 * 4)

		pay_font = fonts.lettersC6 if pay_rect.collidepoint(mouse_pos) else fonts.lettersC1
		retour_font = fonts.lettersC6 if retour_rect.collidepoint(mouse_pos) else fonts.lettersC1

		fonts.draw_body_text(
			screen, "Payer (1 or)", window_x + 178, window_y + 267,
			scaled_window.get_width() - 40, font_dict=pay_font, scale=body_scale
		)
		fonts.draw_body_text(
			screen, "Retour", window_x + 217, window_y + 367,
			scaled_window.get_width() - 40, scale=body_scale, font_dict=retour_font
		)

	elif librarian_state == "books":
		row_y = window_y + 120
		for book in librarian_books:
			rect = pygame.Rect(window_x + 60, row_y, scaled_window.get_width() - 120, 17 * 4)
			book.rect = rect.copy()
			book_rects.append(rect)

			title_font = fonts.lettersC6 if rect.collidepoint(mouse_pos) else fonts.lettersC1
			fonts.draw_body_text(screen, book.title, rect.x, rect.y, rect.width, title_font, body_scale)
			row_y += 17 * 4 + 10

		screen.blit(scaled_button_on, (window_x + 143, window_y + 550))
		screen.blit(scaled_button_on2, (window_x + 243, window_y + 550))
		screen.blit(scaled_button_on2, (window_x + 293, window_y + 550))
		quit_rect = pygame.Rect(window_x + 153, window_y + 550, 235, 17 * 4)
		quit_font = fonts.lettersC6 if quit_rect.collidepoint(mouse_pos) else fonts.lettersC1
		fonts.draw_body_text(
			screen, "Quitter", window_x + 217, window_y + 567,
			scaled_window.get_width() - 40, scale=body_scale, font_dict=quit_font
		)

	elif librarian_state == "reading":
		book = librarian_books[current_book_index]

		fonts.draw_text(
			screen, book.title, window_x + scaled_window.get_width() // 2,
			window_y + 67, scale=ui_scale * 0.6, spacing=-1, centered=True
		)

		fonts.draw_wrapped_text(
			screen, book.pages[current_page], window_x + 60, window_y + 130,
			scaled_window.get_width() - 120, classic_font, body_scale,
			max_y=window_y + 500
		)

		page_label = f"{current_page + 1} sur {len(book.pages)}"
		fonts.draw_body_text(
			screen, page_label, window_x + scaled_window.get_width() // 2 - 60,
			window_y + 625, scaled_window.get_width(), fonts.lettersC1, max(1, ui_scale * 0.62)
		)

		scaled_arrow_right = pygame.transform.scale(
			arrow_right, (int(arrow_right.get_width() * ui_scale), int(arrow_right.get_height() * ui_scale))
		)
		scaled_arrow_left = pygame.transform.flip(scaled_arrow_right, True, False)

		left_arrow_rect = pygame.Rect(window_x + 60, window_y + 540, int(16 * ui_scale), int(16 * ui_scale))
		right_arrow_rect = pygame.Rect(
			window_x + scaled_window.get_width() - 60 - int(16 * ui_scale),
			window_y + 540, int(16 * ui_scale), int(16 * ui_scale)
		)
		if current_page > 0:
			screen.blit(scaled_arrow_left, left_arrow_rect.topleft)
		if current_page < len(book.pages) - 1:
			screen.blit(scaled_arrow_right, right_arrow_rect.topleft)

		screen.blit(scaled_button_on, (window_x + 143, window_y + 550))
		screen.blit(scaled_button_on2, (window_x + 243, window_y + 550))
		screen.blit(scaled_button_on2, (window_x + 293, window_y + 550))
		back_rect = pygame.Rect(window_x + 153, window_y + 550, 235, 17 * 4)
		back_font = fonts.lettersC6 if back_rect.collidepoint(mouse_pos) else fonts.lettersC1
		fonts.draw_body_text(
			screen, "Retour", window_x + 227, window_y + 567,
			scaled_window.get_width() - 40, scale=body_scale, font_dict=back_font
		)

	elif librarian_state == "goodbye":
		visible_text = dialogues.get_visible_text()
		fonts.draw_wrapped_text(
			screen, visible_text, window_x + 60, window_y + 80,
			scaled_window.get_width() - 120, classic_font, body_scale,
			max_y=window_y + 500
		)

	# Croix de fermeture rapide -- presente sur les 3 ecrans

	# Croix de fermeture rapide -- presente sur les 3 ecrans
	scaled_exit = pygame.transform.scale(
		exit_button, (int(exit_button.get_width() * ui_scale), int(exit_button.get_height() * ui_scale))
	)
	close_button_size = int(8 * ui_scale)
	close_rect = pygame.Rect(
		window_x + scaled_window.get_width() - close_button_size - 47,
		window_y + 10, close_button_size, close_button_size
	)
	if close_rect.collidepoint(mouse_pos):
		screen.blit(scaled_exit, scaled_exit.get_rect(center=close_rect.center))

	return close_rect, pay_rect, retour_rect, book_rects, quit_rect, back_rect, left_arrow_rect, right_arrow_rect

