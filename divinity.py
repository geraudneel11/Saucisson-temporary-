import pygame
import math
import fonts
import dialogues
import random
from settings import *


def load_divinity_ui():
	global shop_window_1, exit_button, button_on, button_on2, arrow_right

	shop_window = pygame.image.load("Shop.png").convert_alpha()
	button_window = pygame.image.load("Buttons.png").convert_alpha()
	close_button_sheet = pygame.image.load("Shop_exit_button.png").convert_alpha()

	shop_window_1 = shop_window.subsurface((0, 0, 128, 160))

	button_on = shop_window.subsurface((94, 186, 37, 17))
	button_on2 = shop_window.subsurface((102, 186, 29, 17))
	exit_button = close_button_sheet.subsurface((109, 2, 9, 9))

	arrow_right = button_window.subsurface((336, 303, 16, 16))


# --- Phrases de la divinite : listes modifiables. Une phrase est
# tiree au hasard a chaque ouverture du menu (greetings) et a chaque
# clic sur Quitter (goodbye). Ajoute/enlève des phrases librement.
divinity_dialogues = {
	"greetings": [
		"Une presence ancienne s'eveille a ton approche...",
		"L'autel frissonne. La divinite te regarde, voyageur.",
		"Tu sens un regard bienveillant poser sur toi...",
	],
	"goodbye": [
		"Que ma lumiere veille sur ta route, enfant.",
		"Reviens quand ton ame cherchera a grandir.",
		"Les dieux t'attendent, toujours.",
	],
}


# ============================================================
# COMPETENCES DE LA DIVINITE
# Toute la mecanique du menu est pilotee par cette liste :
#   - une entree = une competence affichee (4 par page, les pages
#     suivantes se creent toutes seules grace a SKILLS_PER_PAGE).
#   - pour AJOUTER une competence future : copie un bloc, change
#     les valeurs, et le menu la placera automatiquement sur la
#     bonne page.
#   - pour BRANCHER ta mecanique plus tard : tout est deja la --
#     "key" sert d'identifiant stable (ne le change pas apres coup),
#     "xp_cost" est le cout en XP, "level" le niveau actuel acquis,
#     "value_per_level" le gain par niveau que ton systeme pourra
#     lire pour appliquer l'effet reel. Rien d'autre a toucher :
#     l'achat n'est PAS implemente (clic volontairement sans effet),
#     ces valeurs ne servent qu'a l'affichage pour l'instant.
# ============================================================
divinity_skills = [
	{
		"key": "max_hp",
		"name": "PV max",
		"description": "Points de vie maximum.",
		"xp_cost": 50,
		"level": 0,
		"value_per_level": 10,
	},
	{
		"key": "strength",
		"name": "Force",
		"description": "Degats d'attaque.",
		"xp_cost": 60,
		"level": 0,
		"value_per_level": 2,
	},
	{
		"key": "slot_capacity",
		"name": "Items par slot",
		"description": "Items max par slot.",
		"xp_cost": 40,
		"level": 0,
		"value_per_level": 1,
	},
	{
		"key": "slot_count",
		"name": "Slots",
		"description": "Emplacements d'inventaire.",
		"xp_cost": 80,
		"level": 0,
		"value_per_level": 1,
	},
]

# Nombre de competences affichees par page (modifie-le si tu veux
# des pages plus ou moins denses : la pagination s'adapte seule).
SKILLS_PER_PAGE = 4

# Nombre total de pages, recalcule automatiquement.
divinity_max_pages = max(1, math.ceil(len(divinity_skills) / SKILLS_PER_PAGE))


def draw_divinity_ui(screen, player, ui_scale, divinity_state, current_page):
	"""
	Dessine la fenetre de la divinite (interaction avec l'autel).
	divinity_state vaut "main" (greeting + liste des competences +
	fleches + Quitter) ou "goodbye" (phrase d'adieu avant fermeture).

	Retourne (close_rect, skill_rects, quit_rect, left_arrow_rect,
	right_arrow_rect) -- non pertinents pour l'etat courant valent
	None (ou [] pour skill_rects).
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

	close_rect = None
	skill_rects = []
	quit_rect = None
	left_arrow_rect = None
	right_arrow_rect = None

	fonts.draw_text(
		screen, "DIVINITE", window_x + scaled_window.get_width() // 2,
		window_y + 15, scale=ui_scale, spacing=-1, centered=True
	)

	if divinity_state == "main":
		# Phrase de greeting (affichage lettre par lettre, comme les
		# autres PNJ interactables), au-dessus de la liste.
		visible_text = dialogues.get_visible_text()
		fonts.draw_wrapped_text(
			screen, visible_text, window_x + 60, window_y + 70,
			scaled_window.get_width() - 120, classic_font,
			max(1, ui_scale * 0.6), max_y=window_y + 125
		)

		# --- Liste des competences de la page courante ---
		page_skills = divinity_skills[
			current_page * SKILLS_PER_PAGE:
			(current_page + 1) * SKILLS_PER_PAGE
		]
		name_scale = max(1, ui_scale * 0.667)   # nom sur UNE ligne
		desc_scale = max(1, ui_scale * 0.55)
		row_y = window_y + 130
		for skill in page_skills:
			rect = pygame.Rect(window_x + 60, row_y, scaled_window.get_width() - 120, 17 * 5)
			skill_rects.append(rect)

			name_font = fonts.lettersC6 if rect.collidepoint(mouse_pos) else fonts.lettersC1
			# Nom a gauche, niveau actuel a droite (sur la meme ligne).
			fonts.draw_body_text(
				screen, skill["name"], rect.x, rect.y,
				rect.width - 130, name_font, name_scale
			)
			level_font = fonts.lettersC6 if rect.collidepoint(mouse_pos) else fonts.lettersC1
			fonts.draw_body_text(
				screen, f"Niv. {skill['level']}", rect.right - 125, rect.y,
				125, level_font, max(1, ui_scale * 0.6)
			)
			# Description (une ligne) puis cout en XP.
			fonts.draw_body_text(
				screen, skill["description"], rect.x, rect.y + 38,
				rect.width, classic_font, desc_scale
			)
			cost_label = f"Cout : {skill['xp_cost']} XP"
			fonts.draw_body_text(
				screen, cost_label, rect.x, rect.bottom - 26,
				rect.width, fonts.lettersC1, desc_scale
			)
			row_y += 17 * 5 + 8

		# --- Fleches de pagination (comme le bibliothecaire) ---
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
		if current_page < divinity_max_pages - 1:
			screen.blit(scaled_arrow_right, right_arrow_rect.topleft)

		page_label = f"{current_page + 1} sur {divinity_max_pages}"
		fonts.draw_body_text(
			screen, page_label, window_x + scaled_window.get_width() // 2 - 60,
			window_y + 625, scaled_window.get_width(), fonts.lettersC1, max(1, ui_scale * 0.62)
		)

		# --- Bouton Quitter (meme ligne que les fleches) ---
		screen.blit(scaled_button_on, (window_x + 143, window_y + 550))
		screen.blit(scaled_button_on2, (window_x + 243, window_y + 550))
		screen.blit(scaled_button_on2, (window_x + 293, window_y + 550))
		quit_rect = pygame.Rect(window_x + 153, window_y + 550, 235, 17 * 4)
		quit_font = fonts.lettersC6 if quit_rect.collidepoint(mouse_pos) else fonts.lettersC1
		fonts.draw_body_text(
			screen, "Quitter", window_x + 217, window_y + 567,
			scaled_window.get_width() - 40, scale=body_scale, font_dict=quit_font
		)

	elif divinity_state == "goodbye":
		visible_text = dialogues.get_visible_text()
		fonts.draw_wrapped_text(
			screen, visible_text, window_x + 60, window_y + 80,
			scaled_window.get_width() - 120, classic_font, body_scale,
			max_y=window_y + 500
		)

	# Croix de fermeture rapide -- presente sur tous les ecrans
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

	return close_rect, skill_rects, quit_rect, left_arrow_rect, right_arrow_rect