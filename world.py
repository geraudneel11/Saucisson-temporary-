import pygame
import waves
from classes import *
from settings import *
import random

_debug_font = None

def _get_debug_font():
	global _debug_font
	if _debug_font is None:
		_debug_font = pygame.font.SysFont(None, 16)
	return _debug_font

def draw_ground(surface, ground_layer, camera_x, camera_y, screen_width, screen_height):
	visible_rect = pygame.Rect(camera_x, camera_y, screen_width, screen_height)
	surface.blit(ground_layer, visible_rect.topleft, area=visible_rect)

def start_new_level(enemies, current_level, orc_data):
	current_level += 1
	current_wave = 1

	transition = True
	transition_timer = 120

	waves.start_wave(
		enemies,
		current_level,
		current_wave,
		orc_data
	)

	return (
		current_level,
		current_wave,
		transition,
		transition_timer
	)

def draw_portal(surface, rect, timer):
	perimeter = (rect.width + rect.height) * 2
	t = timer % perimeter

	if t < rect.width:
		x = rect.left + t
		y = rect.top
	elif t < rect.width + rect.height:
		x = rect.right
		y = rect.top + (t - rect.width)
	elif t < rect.width * 2 + rect.height:
		x = rect.right - (t - (rect.width + rect.height))
		y = rect.bottom
	else:
		x = rect.left
		y = rect.bottom - (t - (rect.width*2 + rect.height))

	pygame.draw.circle(surface, (0, 255, 255), (int(x), int(y)), 4)
	
def handle_player_collisions(player, colliders, old_pos):
	for collider in colliders:
		if player.hitbox.colliderect(collider):
			player.rect = old_pos
			player.hitbox.center = player.rect.center
			
def update_portal(game_state, portal_timer, portal_frame,
				  portal_animation_speed, portal_animation):

	if game_state == "shop":
		portal_timer += 1

		if portal_timer >= portal_animation_speed:
			portal_timer = 0
			portal_frame += 1

			if portal_frame >= len(portal_animation):
				portal_frame = 0

	return portal_timer, portal_frame

def update_smoke(game_state, smoke_timer, smoke_frame,
                  smoke_animation_speed, smoke_animation):

    if game_state == "shop":
        smoke_timer += 1

        if smoke_timer >= smoke_animation_speed:
            smoke_timer = 0
            smoke_frame += 1

            if smoke_frame >= len(smoke_animation):
                smoke_frame = 0

    return smoke_timer, smoke_frame

class House:

	def __init__(self):

		self.sheet = pygame.image.load("walls_floor.png").convert_alpha()
		self.deco_sheet = pygame.image.load("Interior.png").convert_alpha()
		self.deco_sheet2 = pygame.image.load("Interior_objects.png").convert_alpha()
		self.tapis_bleu = pygame.image.load("Tapis_bleu.png").convert_alpha()

		self.exterior_x = HOUSE_X
		self.exterior_y = HOUSE_Y
		# Ratio par défaut : on ne garde que le bas du sprite comme zone de collision
		self.DEFAULT_HITBOX_RATIO = 0.35

		# Config par objet. Clés possibles :
		#   ratio        -> hauteur de la hitbox en % de la hauteur du sprite (defaut 0.35)
		#   width_ratio  -> largeur de la hitbox en % de la largeur du sprite (defaut 1.0)
		#   height       -> hauteur fixe en pixels (prioritaire sur ratio)
		#   width        -> largeur fixe en pixels (prioritaire sur width_ratio)
		#   offset_x     -> décalage horizontal en pixels (defaut 0)
		#   offset_y     -> décalage vertical en pixels (defaut 0)
		#   anchor       -> point d'ancrage sur le rect du sprite (defaut "midbottom")
		self.furniture_hitbox_config = {
			"commode1":    {"ratio": 0.35, "width_ratio": 0.55, "offset_y": -110},
			"chest1":      {"ratio": 0.45, "width_ratio": 0.60, "offset_y": -110},
			"plant1":      {"height": 3, "width": 40, "offset_y": -70},
			"deck1":       {"height": 10, "width": 180, "offset_y": -100, "offset_x": 78},
			"bookshelf1":  {"height": 50, "width_ratio": 0.55, "offset_y": -100},
			"bookshelf2":  {"height": 50, "width_ratio": 0.55, "offset_y": -104},
			"sofa1":       {"height": 30, "width_ratio": 0.55, "offset_y": -80},
			"blackbord1":  {"ratio": 0.15, "width_ratio": 0.80, "offset_y": -95},
			"wooden_box1": {"height": 2, "width_ratio": 0.55, "offset_y": -90},
			"coal_sack1":  {"height": 2, "width_ratio": 0.55, "offset_y": -90, "offset_x": 10},
			"table1":      {"ratio": 0.15, "width_ratio": 0.50, "offset_y": -100, "offset_x": -7},
			"table2":      {"ratio": 0.15, "width_ratio": 0.45, "offset_y": -120},
			"stairs1":     {"height": 35, "width_ratio": 0.55, "offset_y": -80, "offset_x": -20},
			"chair_table2_top":    {"width": 18, "height": 18, "anchor": "midtop",    "offset_y": 40},
			"chair_table2_bottom": {"width": 18, "height": 18, "anchor": "midbottom", "offset_y": -100},
			"chair_table2_left":   {"width": 18, "height": 2, "anchor": "midleft",   "offset_x": 25, "offset_y": -50},
			"chair_table2_right":  {"width": 18, "height": 2, "anchor": "midright",  "offset_x": -14, "offset_y": -50},
		}
		# Décalage MANUEL et OPTIONNEL, en plus du point de tri automatique
		# (voir _build_furniture_render_list). Le point de départ du tri
		# vient maintenant directement du bas de la hitbox de chaque meuble
		# (déjà réglée visuellement) — indépendant de sa hauteur. Ce
		# dictionnaire ne sert que si un objet a encore besoin d'un tout
		# petit ajustement après vérification avec la ligne magenta (F1).
		# Ajustement individuel du point de tri, PAR-DESSUS le calcul
		# automatique (rect.bottom ou hitbox.bottom selon l'épaisseur de
		# la hitbox, voir _build_furniture_render_list). Sert à compenser
		# PLAYER_SORT_MARGIN pour les objets où la marge globale est trop
		# généreuse envers le joueur.
		self.furniture_sort_offset = {
			"coal_sack1":  80,
			"plant1":      80,
			"wooden_box1": 80,
			"chest1":	  -40,
			"deck1":	  -40,
			"bookshelf1":  -40,
			"sofa1":	  -40,
			"blackbord1":  -40,
			"table1":	  -40,
			"stairs1":	  -40,
			"commode1":	  -20,
			"bookshelf2":  -20,
			"table2":	  -20,
			"chair_table2_top":	-20,
			"chair_table2_bottom":	-20,
		}

		self.hitbox = pygame.Rect(
			self.exterior_x + 70,
			self.exterior_y + 160,
			int(145 * HOUSE_SCALE - 70),
			int(128 * HOUSE_SCALE - 240)
		)
		self.door_hitbox = pygame.Rect(
			HOUSE_X + 400,
			HOUSE_Y + 430,
			100,
			100
		)
		self.interior_surface = pygame.Surface((HOUSE_INSIDE_WIDTH, HOUSE_INSIDE_HEIGHT))
		self._draw_interior()
		self.wall_top_hitbox = pygame.Rect(0, 0, HOUSE_INSIDE_WIDTH, 106)
		self.wall_bottom_hitbox = pygame.Rect(0, HOUSE_INSIDE_HEIGHT - 85, HOUSE_INSIDE_WIDTH, 45)
		self.wall_left_hitbox = pygame.Rect(0, 0, 10, HOUSE_INSIDE_HEIGHT)
		self.wall_right_hitbox = pygame.Rect(HOUSE_INSIDE_WIDTH - 10, 0, 10, HOUSE_INSIDE_HEIGHT)

	def repeat_horizontal(self, sprite, y):
		for x in range(0, self.interior_surface.get_width(), sprite.get_width()):
			self.interior_surface.blit(sprite, (x, y))

	def repeat_vertical(self, sprite, x):
		for y in range(0, self.interior_surface.get_height(), sprite.get_height()):
			self.interior_surface.blit(sprite, (x, y))
	
	def repeat_area(self, sprite, x, y, width, height):
		for xx in range(x, x+width, sprite.get_width()):
			for yy in range(y, y+height, sprite.get_height()):
				self.interior_surface.blit(sprite, (xx, yy))

	def _make_hitbox(self, rect, cfg):
		ratio = cfg.get("ratio", self.DEFAULT_HITBOX_RATIO)
		width_ratio = cfg.get("width_ratio", 1.0)

		height = cfg.get("height", max(4, int(rect.height * ratio)))
		width = cfg.get("width", max(4, int(rect.width * width_ratio)))

		hitbox = pygame.Rect(0, 0, width, height)

		anchor = cfg.get("anchor", "midbottom")
		setattr(hitbox, anchor, getattr(rect, anchor))

		hitbox.x += cfg.get("offset_x", 0)
		hitbox.y += cfg.get("offset_y", 0)

		return hitbox

	def _build_furniture_hitboxes(self):
		rects_by_name = {
			"commode1": self.commode1_rect,
			"chest1": self.chest1_rect,
			"plant1": self.plant1_rect,
			"deck1": self.deck1_rect,
			"bookshelf1": self.bookshelf1_rect,
			"bookshelf2": self.bookshelf2_rect,
			"sofa1": self.sofa1_rect,
			"blackbord1": self.blackbord1_rect,
			"wooden_box1": self.wooden_box1_rect,
			"coal_sack1": self.coal_sack1_rect,
			"table1": self.table1_rect,
			"table2": self.table2_rect,
			"stairs1": self.stairs1_rect,
			"chair_table2_top":    self.table2_rect,
			"chair_table2_bottom": self.table2_rect,
			"chair_table2_left":   self.table2_rect,
			"chair_table2_right":  self.table2_rect,
			# red_rug / blue_rug volontairement absents : ce sont des decos
			# au sol, pas des obstacles. Ajoute-les ici si tu veux qu'elles
			# bloquent aussi le joueur.
		}

		self.furniture_hitboxes = {}
		for name, rect in rects_by_name.items():
			cfg = self.furniture_hitbox_config.get(name, {})
			self.furniture_hitboxes[name] = self._make_hitbox(rect, cfg)

	def _build_furniture_render_list(self):
		sprites_by_name = {
			"commode1": (self.commode1, self.commode1_rect),
			"chest1": (self.chest1, self.chest1_rect),
			"plant1": (self.plant1, self.plant1_rect),
			"deck1": (self.deck1, self.deck1_rect),
			"bookshelf1": (self.bookshelf1, self.bookshelf1_rect),
			"bookshelf2": (self.bookshelf2, self.bookshelf2_rect),
			"sofa1": (self.sofa1, self.sofa1_rect),
			"blackbord1": (self.blackbord1, self.blackbord1_rect),
			"wooden_box1": (self.wooden_box1, self.wooden_box1_rect),
			"coal_sack1": (self.coal_sack1, self.coal_sack1_rect),
			"table1": (self.table1, self.table1_rect),
			"table2": (self.table2, self.table2_rect),
			"stairs1": (self.stairs1, self.stairs1_rect),
		}

		THIN_HITBOX_THRESHOLD = 5
		# Une hitbox très fine (quelques pixels) sert de marqueur précis du
		# point où l'objet touche le sol : on l'utilise alors comme base de
		# tri. Une hitbox plus épaisse est un réglage de collision pensé
		# pour le gameplay (distance d'approche), pas pour la profondeur :
		# dans ce cas, on garde le bas du sprite complet (rect.bottom).
		self.furniture_sprites = {}
		for name, (sprite, rect) in sprites_by_name.items():
			hitbox = self.furniture_hitboxes.get(name)
			if hitbox is not None and hitbox.height <= THIN_HITBOX_THRESHOLD:
				sort_y = hitbox.bottom
			else:
				sort_y = rect.bottom
			sort_y += self.furniture_sort_offset.get(name, 0)
			self.furniture_sprites[name] = (sprite, rect, sort_y)

	def draw_debug_hitboxes(self, surface):
		font = _get_debug_font()

		wall_hitboxes = {
			"wall_top": self.wall_top_hitbox,
			"wall_bottom": self.wall_bottom_hitbox,
			"wall_left": self.wall_left_hitbox,
			"wall_right": self.wall_right_hitbox,
		}
		for name, rect in wall_hitboxes.items():
			pygame.draw.rect(surface, (255, 60, 60), rect, 2)

		pygame.draw.rect(surface, (60, 220, 255), self.door_rect, 2)
		label = font.render("door", True, (60, 220, 255))
		surface.blit(label, (self.door_rect.x, self.door_rect.y - 14))

		for name, rect in self.furniture_hitboxes.items():
			pygame.draw.rect(surface, (255, 170, 0), rect, 2)
			label = font.render(name, True, (255, 170, 0))
			surface.blit(label, (rect.x, rect.y - 14))
		# Ligne de tri en profondeur (Y-sort) : montre EXACTEMENT le point
		# utilisé pour décider si le meuble passe devant ou derrière le
		# joueur. Doit tomber au niveau du bas visible du sprite.
		for name, (sprite, rect, sort_y) in self.furniture_sprites.items():
			pygame.draw.line(
				surface,
				(255, 0, 255),
				(rect.left, sort_y),
				(rect.right, sort_y),
				2
			)
			sort_label = font.render(f"{name} sort_y={sort_y}", True, (255, 0, 255))
			surface.blit(sort_label, (rect.left, sort_y + 2))

	def _draw_interior(self):
		self.interior_surface.fill((95, 70, 45))
		self.wall_back = self.sheet.subsurface((51, 0, 25, 48))
		self.wall_left = self.sheet.subsurface((48, 4, 3, 4))
		self.wall_right = pygame.transform.flip(self.wall_left, True, False)
		self.top_wall_front = self.sheet.subsurface((58, 62, 4, 2))
		self.wall_front = self.sheet.subsurface((48, 64, 32, 29))
		self.front_door = self.sheet.subsurface((108, 97, 36, 28))
		self.window = self.sheet.subsurface((88, 67, 17, 19))
		self.commode1 = self.deco_sheet2.subsurface((133, 98, 51, 62))
		self.blue_rug = self.tapis_bleu.subsurface((10, 278, 94, 83))
		self.chest1 = self.deco_sheet2.subsurface((243, 355, 27, 24))
		self.plant1 = self.deco_sheet2.subsurface((265, 306, 21, 38))
		self.deck1 = self.deco_sheet2.subsurface((218, 225, 60, 37))
		self.bookshelf1 = self.deco_sheet.subsurface((161, 79, 30, 48))
		self.bookshelf2 = self.deco_sheet2.subsurface((330, 98, 50, 62))
		self.sofa1 = self.deco_sheet.subsurface((91, 148, 18, 35))
		self.blackbord1 = self.deco_sheet2.subsurface((49, 167, 45, 53))
		self.wooden_box1 = self.deco_sheet.subsurface((51, 47, 30, 28))
		self.coal_sack1 = self.deco_sheet.subsurface((105, 231, 25, 25))
		self.table1 = self.deco_sheet.subsurface((80, 36, 35, 40))
		self.table2 = self.deco_sheet.subsurface((7, 144, 67, 59))
		self.red_rug = self.deco_sheet.subsurface((124, 295, 56, 66))
		self.stairs1 = self.deco_sheet2.subsurface((10, 80, 51, 30))
		wall_back = pygame.transform.scale(self.wall_back, (self.wall_back.get_width() * WALL_SCALE, self.wall_back.get_height() * WALL_SCALE))
		wall_left = pygame.transform.scale(self.wall_left, (int(self.wall_left.get_width() * WALL_SCALE), int(self.wall_left.get_height() * WALL_SCALE)))
		wall_right = pygame.transform.scale(self.wall_right, (int(self.wall_right.get_width() * WALL_SCALE), int(self.wall_right.get_height() * WALL_SCALE)))
		self.top_wall_front = pygame.transform.scale(self.top_wall_front, (int(self.top_wall_front.get_width() * WALL_SCALE), int(self.top_wall_front.get_height() * WALL_SCALE)))
		self.wall_front = pygame.transform.scale(self.wall_front, (int(self.wall_front.get_width() * WALL_SCALE), int(self.wall_front.get_height() * WALL_SCALE)))
		self.front_door = pygame.transform.scale(self.front_door, (int(self.front_door.get_width() * 4.5), int(self.front_door.get_height() * 4.5)))
		self.window = pygame.transform.scale(self.window, (int(self.window.get_width() * WALL_SCALE), int(self.window.get_height() * WALL_SCALE)))
		self.commode1 = pygame.transform.scale(self.commode1, (int(self.commode1.get_width() * 4), int(self.commode1.get_height() * 4)))
		self.blue_rug = pygame.transform.scale(self.blue_rug, (int(self.blue_rug.get_width() * 4), int(self.blue_rug.get_height() * 4)))
		self.chest1 = pygame.transform.scale(self.chest1, (int(self.chest1.get_width() * 4), int(self.chest1.get_height() * 4)))
		self.plant1 = pygame.transform.scale(self.plant1, (int(self.plant1.get_width() * 4), int(self.plant1.get_height() * 4)))
		self.deck1 = pygame.transform.scale(self.deck1, (int(self.deck1.get_width() * 4), int(self.deck1.get_height() * 4)))
		self.bookshelf1 = pygame.transform.scale(self.bookshelf1, (int(self.bookshelf1.get_width() * 4), int(self.bookshelf1.get_height() * 4)))
		self.bookshelf2 = pygame.transform.scale(self.bookshelf2, (int(self.bookshelf2.get_width() * 4), int(self.bookshelf2.get_height() * 4)))
		self.sofa1 = pygame.transform.scale(self.sofa1, (int(self.sofa1.get_width() * 4), int(self.sofa1.get_height() * 4))) 
		self.blackbord1 = pygame.transform.scale(self.blackbord1, (int(self.blackbord1.get_width() * 4), int(self.blackbord1.get_height() * 4)))
		self.wooden_box1 = pygame.transform.scale(self.wooden_box1, (int(self.wooden_box1.get_width() * 4), int(self.wooden_box1.get_height() * 4)))
		self.coal_sack1 = pygame.transform.scale(self.coal_sack1, (int(self.coal_sack1.get_width() * 4), int(self.coal_sack1.get_height() * 4)))
		self.table1 = pygame.transform.scale(self.table1, (int(self.table1.get_width() * 4), int(self.table1.get_height() * 4)))
		self.table2 = pygame.transform.scale(self.table2, (int(self.table2.get_width() * 4), int(self.table2.get_height() * 4)))
		self.red_rug = pygame.transform.scale(self.red_rug, (int(self.red_rug.get_width() * 4), int(self.red_rug.get_height() * 4)))
		self.stairs1 = pygame.transform.scale(self.stairs1, (int(self.stairs1.get_width() * 4.5), int(self.stairs1.get_height() * 4.5)))
		self.door_rect = pygame.Rect(
			HOUSE_INSIDE_WIDTH // 2 - self.front_door.get_width() // 2 + 93 + 194,
			HOUSE_INSIDE_HEIGHT - 150,
			self.front_door.get_width(),
			self.front_door.get_height()
		)
		self.commode1_rect = pygame.Rect(HOUSE_INSIDE_WIDTH - HOUSE_INSIDE_WIDTH + wall_right.get_width()-2,
					HOUSE_INSIDE_HEIGHT - HOUSE_INSIDE_HEIGHT + self.top_wall_front.get_width(),
					self.commode1.get_width(),
					self.commode1.get_height()
				)
		self.chest1_rect = pygame.Rect(HOUSE_INSIDE_WIDTH - HOUSE_INSIDE_WIDTH + wall_right.get_width()-2 + self.commode1.get_width(),
					HOUSE_INSIDE_HEIGHT - HOUSE_INSIDE_HEIGHT + self.top_wall_front.get_width()+150,
					self.chest1.get_width(),
					self.chest1.get_height()
				)
		self.plant1_rect = pygame.Rect(HOUSE_INSIDE_WIDTH - HOUSE_INSIDE_WIDTH + wall_right.get_width()-2,
					HOUSE_INSIDE_HEIGHT - HOUSE_INSIDE_HEIGHT + self.top_wall_front.get_width()+self.commode1.get_height()-50,
					self.plant1.get_width(),
					self.plant1.get_height()
				)
		self.deck1_rect = pygame.Rect(HOUSE_INSIDE_WIDTH - HOUSE_INSIDE_WIDTH + wall_right.get_width()+50,
					HOUSE_INSIDE_HEIGHT - HOUSE_INSIDE_HEIGHT + self.top_wall_front.get_width()+self.blue_rug.get_height() - self.deck1.get_height()+200,
					self.plant1.get_width(),
					self.plant1.get_height()
				)
		self.bookshelf1_rect = pygame.Rect(HOUSE_INSIDE_WIDTH - self.bookshelf1.get_width()-10,
					HOUSE_INSIDE_HEIGHT - HOUSE_INSIDE_HEIGHT + self.top_wall_front.get_width()+(self.bookshelf1.get_height()//2)-30,
					self.bookshelf1.get_width(),
					self.bookshelf1.get_height()
				)
		self.bookshelf2_rect = pygame.Rect(HOUSE_INSIDE_WIDTH - self.bookshelf1.get_width()-10 - self.bookshelf2.get_width()+10,
					HOUSE_INSIDE_HEIGHT - HOUSE_INSIDE_HEIGHT + self.top_wall_front.get_width()+(self.bookshelf1.get_height()//2)-81,
					self.bookshelf2.get_width(),
					self.bookshelf2.get_height()
				)
		self.sofa1_rect = pygame.Rect(HOUSE_INSIDE_WIDTH - HOUSE_INSIDE_WIDTH+self.blue_rug.get_width()-self.sofa1.get_width(),
					HOUSE_INSIDE_HEIGHT - HOUSE_INSIDE_HEIGHT + self.top_wall_front.get_width()+self.blue_rug.get_height() - self.deck1.get_height()+200-self.sofa1.get_height(),
					self.sofa1.get_width(),
					self.sofa1.get_height()
				)
		self.blackbord1_rect = pygame.Rect(HOUSE_INSIDE_WIDTH - self.bookshelf1.get_width()-10 - self.bookshelf2.get_width()+10-self.blackbord1.get_width(),
					HOUSE_INSIDE_HEIGHT - HOUSE_INSIDE_HEIGHT + self.top_wall_front.get_width()+(self.bookshelf1.get_height()//2)-75,
					self.blackbord1.get_width(),
					self.blackbord1.get_height()
				)
		self.wooden_box1_rect = pygame.Rect(HOUSE_INSIDE_WIDTH - self.bookshelf1.get_width()-10 - self.bookshelf2.get_width()-250,
					HOUSE_INSIDE_HEIGHT - HOUSE_INSIDE_HEIGHT + self.top_wall_front.get_width()+(self.bookshelf1.get_height()//2)+200,
					self.wooden_box1.get_width(),
					self.wooden_box1.get_height()
				)
		self.coal_sack1_rect = pygame.Rect(HOUSE_INSIDE_WIDTH - self.bookshelf1.get_width()-10 - self.bookshelf2.get_width()-100,
					HOUSE_INSIDE_HEIGHT - HOUSE_INSIDE_HEIGHT + self.top_wall_front.get_width()+(self.bookshelf1.get_height()//2)+230,
					self.coal_sack1.get_width(),
					self.coal_sack1.get_height()
				)
		self.table1_rect = pygame.Rect(HOUSE_INSIDE_WIDTH - self.bookshelf1.get_width()-10 - self.bookshelf2.get_width()+100,
					HOUSE_INSIDE_HEIGHT - HOUSE_INSIDE_HEIGHT + self.top_wall_front.get_width()+(self.bookshelf1.get_height()//2)+220,
					self.table1.get_width(),
					self.table1.get_height()
				)
		self.table2_rect = pygame.Rect((HOUSE_INSIDE_WIDTH//2)-105,
					(HOUSE_INSIDE_HEIGHT//2)-25,
					self.table2.get_width(),
					self.table2.get_height()
				)
		self.red_rug_rect = pygame.Rect(HOUSE_INSIDE_WIDTH-self.red_rug.get_width()-115,
					HOUSE_INSIDE_HEIGHT-self.red_rug.get_height()-20,
					self.red_rug.get_width(),
					self.red_rug.get_height()
				)
		self.stairs1_rect = pygame.Rect(HOUSE_INSIDE_WIDTH - HOUSE_INSIDE_WIDTH + wall_right.get_width()+70,
					HOUSE_INSIDE_HEIGHT - HOUSE_INSIDE_HEIGHT + self.top_wall_front.get_width()+self.blue_rug.get_height() - self.deck1.get_height()+400,
					self.stairs1.get_width(),
					self.stairs1.get_height()
				)

		NUM_WINDOWS = 3
		usable_left = 10
		usable_right = self.door_rect.x   # début de door_rect
		window_w = self.window.get_width()
		gap = (usable_right - usable_left - NUM_WINDOWS * window_w) / (NUM_WINDOWS + 1)

		self.window_rects = []
		for i in range(NUM_WINDOWS):
			x = usable_left + gap * (i + 1) + window_w * i
			self.window_rects.append(pygame.Rect(
			int(x),
			HOUSE_INSIDE_HEIGHT - self.window.get_height() - 40,
			window_w,
			self.window.get_height()
		))
		self._build_furniture_hitboxes()
		self._build_furniture_render_list()
		self.repeat_horizontal(wall_back, 0)
		self.repeat_vertical(wall_left, 0)
		self.repeat_vertical(wall_right, HOUSE_INSIDE_WIDTH - wall_right.get_width())
		self.interior_surface.blit(self.blue_rug, (HOUSE_INSIDE_WIDTH-HOUSE_INSIDE_WIDTH + 10, 205))
		self.interior_surface.blit(self.red_rug, self.red_rug_rect)

	def draw_interior(self):
		self._draw_interior()
		return self.interior_surface


def random_spawn_position(map_width, map_height, margin=250):
	"""
	Renvoie une position (x, y) aléatoire dans les limites de la
	carte, avec une marge pour éviter de spawn collé aux bords.
	"""
	x = random.randint(margin, map_width - margin)
	y = random.randint(margin, map_height - margin)
	return x, y