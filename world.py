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

def _dist_point_segment(px, py, x1, y1, x2, y2):
	dx, dy = x2 - x1, y2 - y1
	length_sq = dx * dx + dy * dy
	if length_sq == 0:
		return math.hypot(px - x1, py - y1)
	t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / length_sq))
	proj_x, proj_y = x1 + t * dx, y1 + t * dy
	return math.hypot(px - proj_x, py - proj_y)


def _valid_scatter_position(x, y, placed_positions, map_width, map_height,
							 plaza_center, path_end, house_bounds, avoid_point,
							 min_spacing, edge_margin, plaza_radius, path_margin, avoid_radius):
	if x < edge_margin or x > map_width - edge_margin:
		return False
	if y < edge_margin or y > map_height - edge_margin:
		return False
	if avoid_point is not None and math.hypot(x - avoid_point[0], y - avoid_point[1]) < avoid_radius:
		return False
	if math.hypot(x - plaza_center[0], y - plaza_center[1]) < plaza_radius:
		return False
	if _dist_point_segment(x, y, plaza_center[0], plaza_center[1], path_end[0], path_end[1]) < path_margin:
		return False
	if house_bounds[0] <= x <= house_bounds[2] and house_bounds[1] <= y <= house_bounds[3]:
		return False
	for (px, py) in placed_positions:
		if math.hypot(x - px, y - py) < min_spacing:
			return False
	return True


def generate_level_trees(species_frames, avoid_point, map_width, map_height,
						  plaza_center, path_end, house_bounds,
						  count=80, min_spacing=280, edge_margin=300,
						  plaza_radius=380, path_margin=190, avoid_radius=400):
	placed_positions = []
	results = []
	attempts = 0
	max_attempts = count * 250

	while len(results) < count and attempts < max_attempts:
		attempts += 1
		x = random.randint(edge_margin, map_width - edge_margin)
		y = random.randint(edge_margin, map_height - edge_margin)

		if not _valid_scatter_position(x, y, placed_positions, map_width, map_height,
										plaza_center, path_end, house_bounds, avoid_point,
										min_spacing, edge_margin, plaza_radius, path_margin, avoid_radius):
			continue

		frames = random.choice(species_frames)
		placed_positions.append((x, y))
		results.append((x, y, frames))

	return results


def generate_apple_trees(apple_frames, existing_tree_positions, avoid_point,
						  map_width, map_height, plaza_center, path_end, house_bounds,
						  max_count=3, spawn_chance=1 / 3, min_spacing=280,
						  edge_margin=300, plaza_radius=380, path_margin=190, avoid_radius=400):
	"""
	Jusqu'à 'max_count' pommiers, chacun avec 'spawn_chance' de chance
	INDÉPENDANTE d'apparaître (donc parfois 0, parfois 3, en moyenne
	max_count * spawn_chance). Évite les autres arbres déjà placés.
	"""
	placed = list(existing_tree_positions)
	apple_positions = []

	for _ in range(max_count):
		if random.random() >= spawn_chance:
			continue

		attempts = 0
		while attempts < 300:
			attempts += 1
			x = random.randint(edge_margin, map_width - edge_margin)
			y = random.randint(edge_margin, map_height - edge_margin)

			if not _valid_scatter_position(x, y, placed, map_width, map_height,
											plaza_center, path_end, house_bounds, avoid_point,
											min_spacing, edge_margin, plaza_radius, path_margin, avoid_radius):
				continue

			placed.append((x, y))
			apple_positions.append((x, y, apple_frames))
			break

	return apple_positions


def generate_level_rocks(rock_variants, existing_positions, avoid_point,
						  map_width, map_height, plaza_center, path_end, house_bounds,
						  count=20, min_spacing=220, edge_margin=300,
						  plaza_radius=380, path_margin=190, avoid_radius=400):
	"""
	rock_variants : liste de tuples (sprite, hitbox_dict) parmi
	lesquels piocher aléatoirement pour chaque rocher.
	"""
	placed = list(existing_positions)
	rocks = []
	attempts = 0
	max_attempts = count * 250

	while len(rocks) < count and attempts < max_attempts:
		attempts += 1
		x = random.randint(edge_margin, map_width - edge_margin)
		y = random.randint(edge_margin, map_height - edge_margin)

		if not _valid_scatter_position(x, y, placed, map_width, map_height,
										plaza_center, path_end, house_bounds, avoid_point,
										min_spacing, edge_margin, plaza_radius, path_margin, avoid_radius):
			continue

		placed.append((x, y))
		sprite, hitbox = random.choice(rock_variants)
		rocks.append((x, y, sprite, hitbox))

	return rocks

class Chapel:
	"""
	Bâtiment extérieur de la chapelle. Pas d'intérieur pour l'instant
	(ce sera géré plus tard si besoin) : c'est un décor traversable
	uniquement au pourtour, avec le même découpage toit/base que House
	pour un rendu correct en profondeur -> la base est dessinée AVANT
	le tri des entités (le joueur passe toujours devant), le toit est
	dessiné APRÈS (toujours devant le joueur, comme le toit de la
	maison), voir main.py pour l'ordre exact des blits.
	"""

	def __init__(self, x, y, scale=None, roof_height=None, use_cross_variant=None):
		scale = scale if scale is not None else CHAPEL_SCALE
		roof_height = roof_height if roof_height is not None else CHAPEL_ROOF_HEIGHT
		use_cross_variant = (
			CHAPEL_USE_CROSS_VARIANT if use_cross_variant is None else use_cross_variant
		)

		self.sheet = pygame.image.load("chapel_exterior.png").convert_alpha()

		variant_x = 0 if use_cross_variant else 128
		building = self.sheet.subsurface((variant_x, 0, 128, 159))

		scaled_w = int(128 * scale)
		scaled_h = int(159 * scale)
		building = pygame.transform.scale(building, (scaled_w, scaled_h))

		roof_h_scaled = int(roof_height * scale)

		self.roof = building.subsurface((0, 0, scaled_w, roof_h_scaled))
		self.base = building.subsurface(
			(0, roof_h_scaled, scaled_w, scaled_h - roof_h_scaled)
		)

		self.rect = pygame.Rect(x, y, scaled_w, scaled_h)
		self.roof_height = roof_h_scaled

		# Point bas-centre du bâtiment : sert d'ancrage pour tracer le
		# chemin de la place vers la chapelle (voir main.py, decor.build_path_layer).
		self.entrance_point = (self.rect.centerx, self.rect.bottom - 20)

		hb = CHAPEL_HITBOX
		self.hitbox = pygame.Rect(
			self.rect.x + hb["offset_x"],
			self.rect.y + hb["offset_y"],
			hb["width"],
			hb["height"]
		)

		self.door_hitbox = pygame.Rect(0, 0, 100, 100)
		self.door_hitbox.center = (self.entrance_point[0], self.entrance_point[1] - 20)


def update_dragon(game_state, dragon_timer, dragon_frame,
				   dragon_animation_speed, dragon_animation, dragon_waiting, dragon_waiting_timer):
	"""
	Même principe que update_smoke/update_portal : l'animation
	n'avance que si on est en mode "shop" (là où la chapelle est
	visible).
	"""

	if game_state == "shop":
		if dragon_waiting:
			dragon_waiting_timer += 1
			if dragon_waiting_timer >= random.randint(60, 300):
				dragon_waiting = False
				dragon_timer = 0
				dragon_frame = 0
		else:
			dragon_timer += 1

			if dragon_timer >= dragon_animation_speed:
				dragon_timer = 0
				dragon_frame += 1

				if dragon_frame >= len(dragon_animation):
					dragon_frame = 0

	return dragon_timer, dragon_frame, dragon_waiting, dragon_waiting_timer

def compute_camera(player, area_width, area_height, screen_width, screen_height):
	"""
	Calcule un décalage de caméra centré sur le joueur, contraint pour
	ne jamais montrer au-delà des bords d'une zone de area_width x
	area_height. Générique : utilisable pour n'importe quel intérieur
	ou donjon plus grand que l'écran, exactement comme pour la carte
	extérieure.
	"""

	camera_x = player.rect.centerx - screen_width // 2
	camera_y = player.rect.centery - screen_height // 2

	if area_width < screen_width:
		camera_x = -(screen_width - area_width) // 2
	else:
		camera_x = max(0, min(camera_x, area_width - screen_width))

	if area_height < screen_height:
		camera_y = -(screen_height - area_height) // 2
	else:
		camera_y = max(0, min(camera_y, area_height - screen_height))

	return camera_x, camera_y

class ChapelInterior:
	"""
	Intérieur de la chapelle, construit étape par étape :
	  1. Murs (cette étape)
	  2. Décorations sur les murs
	  3. Sols et décorations au sol
	  4. Meubles
	  5. Meubles animés
	  6. Hitbox de tout ce qui précède

	Forme en 3 paliers de largeur sur l'axe Y (large / étroit / large)
	qui donne l'effet d'alcôves près de l'autel et d'une niche près de
	l'entrée, avec un couloir de bancs allongé au milieu. La
	bibliothèque est accolée à gauche, sur toute la longueur de ce
	couloir. Plus grand que l'écran -> utilise world.compute_camera,
	comme les zones extérieures.
	"""

	def __init__(self):
		self.sheet = pygame.image.load("chapel_interior_walls.png").convert_alpha()

		scale = CHAPEL_WALL_SCALE

		def cut(rect):
			x, y, w, h = rect
			piece = self.sheet.subsurface((x, y, w, h))
			return pygame.transform.scale(piece, (int(w * scale), int(h * scale)))
		
		self.wall_panel = cut((51, 0, 26, 64))
		self.wall_corner = cut((133, 128, 21, 63))
		self.wall_side = cut((77,0,3,64))
		self.big_wall_side = cut((125, 0, 6, 12))
		self.wall_panel2 = cut((51, 0, 26, 60))

		self.wall_back = cut((96, 0, 64, 64))          # mur plein, pour les segments horizontaux (haut/paliers)
		self.wall_left = cut((133, 128, 21, 63))        # pilier fin, pour les murs latéraux
		self.wall_right = pygame.transform.flip(self.wall_left, True, False)
		self.wall_gothic_arch = cut((0, 256, 144, 80))

		# --- Géométrie : 3 paliers de largeur ---
		narrow_w = CHAPEL_NAVE_NARROW_WIDTH
		wide_extra = CHAPEL_NAVE_WIDE_EXTRA
		wide_w = narrow_w + wide_extra * 2

		alcove_h = CHAPEL_ALCOVE_HEIGHT
		pew_hall_h = CHAPEL_PEW_HALL_HEIGHT
		vase_nook_h = CHAPEL_VASE_NOOK_HEIGHT
		entrance_h = CHAPEL_ENTRANCE_HEIGHT

		lib_w = CHAPEL_LIBRARY_WIDTH

		narrow_left = lib_w
		wide_left = narrow_left - wide_extra

		self.width = wide_left + wide_w
		self.height = alcove_h + pew_hall_h + vase_nook_h + entrance_h

		y = 0
		self.alcove_rect = pygame.Rect(wide_left, y, wide_w, alcove_h)
		y += alcove_h
		self.pew_hall_rect = pygame.Rect(narrow_left, y, narrow_w, pew_hall_h)
		y += pew_hall_h
		self.vase_nook_rect = pygame.Rect(wide_left, y, wide_w, vase_nook_h)
		y += vase_nook_h
		self.entrance_rect = pygame.Rect(narrow_left, y, narrow_w, entrance_h)

		self.library_rect = pygame.Rect(0, self.pew_hall_rect.top, lib_w, pew_hall_h)

		# Point d'entrée (venant de l'extérieur) et zone de sortie -
		# ce sont de simples repères, pas des hitbox de collision (qui
		# viendront à la toute dernière étape).
		self.entrance_point = (self.entrance_rect.centerx, self.entrance_rect.bottom - 30)
		self.exit_rect = pygame.Rect(0, 0, 160, 100)
		self.exit_rect.center = (self.entrance_rect.centerx, self.entrance_rect.bottom - 20)

		self._build_walls()

	def _tile_horizontal(self, surface, tile, x0, x1, y):
		tw = tile.get_width()
		for x in range(x0, x1, tw):
			surface.blit(tile, (x, y))

	def _tile_vertical(self, surface, tile, y0, y1, x):
		th = tile.get_height()
		for y in range(y0, y1, th):
			surface.blit(tile, (x, y))

	def _build_walls(self):
		self.static_surface = pygame.Surface((self.width, self.height))
		self.static_surface.fill((10, 10, 15))
		floor_color = (120, 118, 130)
		for rect in (self.alcove_rect, self.pew_hall_rect, self.vase_nook_rect,
					 self.entrance_rect, self.library_rect):
			pygame.draw.rect(self.static_surface, floor_color, rect)

		# --- Mur du bas (couloir d'entrée), avec un espace pour la porte de sortie --

		tw = self.wall_back.get_width()
		th = self.wall_back.get_height()
		sw = self.wall_left.get_width()

		# --- Alcôve (haut) ---

		# --- Couloir d'entrée (bas) : pas de mur en bas, la porte
		# extérieure viendra plus tard ---
		wall_h = self.wall_panel.get_height()
		y = self.entrance_rect.bottom - wall_h // 1.4
		col_y = self.entrance_rect.bottom - wall_h // 1.1
		y2 = 380
		door_w = CHAPEL_EXIT_DOOR_WIDTH
		door_left = self.entrance_rect.centerx - door_w // 2
		door_right = self.entrance_rect.centerx + door_w // 2
		self._tile_horizontal(self.static_surface, self.wall_panel2,
			self.vase_nook_rect.left, self.entrance_rect.left-25, 885)
		self._tile_horizontal(self.static_surface, self.wall_panel2,
			self.entrance_rect.right, self.vase_nook_rect.right, 885)
		self._tile_horizontal(self.static_surface, self.wall_panel,
			self.entrance_rect.left, door_left, y)
		self._tile_horizontal(self.static_surface, self.wall_panel,
			door_right, self.entrance_rect.right, y)
		sidewall_length = CHAPEL_ENTRANCE_SIDEWALL1_LENGTH
		self.tile_vertical_symmetric(
			self.static_surface, self.big_wall_side,
			self.entrance_rect.bottom - sidewall_length, self.entrance_rect.bottom,
			offset_x=self.entrance_rect.width // 2,
			centerx=self.entrance_rect.centerx
		)
		# Coins, aux deux extrémités du mur du bas
		corner_rect_left = self.wall_corner.get_rect(midtop=(self.entrance_rect.left, col_y))
		self.static_surface.blit(self.wall_corner, corner_rect_left)
		corner_rect_right = self.wall_corner.get_rect(midtop=(self.entrance_rect.right, col_y))
		self.static_surface.blit(self.wall_corner, corner_rect_right)


		self.interior_surface = self.static_surface.copy()

	def add_symmetric(self, surface, sprite, offset_x, y, centerx=None, anchor="midtop"):
		"""
		Pose 'sprite' à gauche ET à droite en une seule fois, symétrique
		par rapport à l'axe vertical centerx (par défaut le centre de la
		nef) :
		  - à gauche : tel quel, à 'offset_x' pixels du centre
		  - à droite : retourné horizontalement (flip), à la même distance
		'anchor' est n'importe quel attribut de pygame.Rect ('midtop',
		'midbottom', 'center', 'topleft'...) qui précise à quel point de
		'y' le sprite s'accroche.
		"""
		centerx = self.nave_rect.centerx if centerx is None else centerx
		flipped = pygame.transform.flip(sprite, True, False)

		left_rect = sprite.get_rect()
		setattr(left_rect, anchor, (centerx - offset_x, y))
		surface.blit(sprite, left_rect)

		right_rect = flipped.get_rect()
		setattr(right_rect, anchor, (centerx + offset_x, y))
		surface.blit(flipped, right_rect)

	def tile_vertical_symmetric(self, surface, sprite, y0, y1, offset_x, centerx=None):
		"""
		Carrelle 'sprite' verticalement (comme _tile_vertical) mais des
		deux côtés à la fois, symétriquement par rapport à centerx : la
		colonne de gauche reçoit le sprite tel quel, la colonne de droite
		reçoit sa version retournée horizontalement.
		"""
		centerx = self.nave_rect.centerx if centerx is None else centerx
		flipped = pygame.transform.flip(sprite, True, False)
		th = sprite.get_height()

		for y in range(y0, y1, th):
			left_rect = sprite.get_rect(midtop=(centerx - offset_x, y))
			surface.blit(sprite, left_rect)
			right_rect = flipped.get_rect(midtop=(centerx + offset_x, y))
			surface.blit(flipped, right_rect)

	def _tile_horizontal(self, surface, tile, x0, x1, y):
		tw = tile.get_width()
		for x in range(x0, x1, tw):
			surface.blit(tile, (x, y))

	def _tile_vertical(self, surface, tile, y0, y1, x):
		th = tile.get_height()
		for y in range(y0, y1, th):
			surface.blit(tile, (x, y))