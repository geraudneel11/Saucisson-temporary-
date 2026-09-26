import pygame
import waves
from classes import *
from settings import *
import random
from animations import load_animation, load_animation_row

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
		self.deck1 = pygame.transform.scale(self.deck1, (int(self.deck1.get_width() * 3.5), int(self.deck1.get_height() * 3.5)))
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
	def reset_seating(self):
		"""
		Tire au sort l'occupation de chaque place (1/3 de chance d'être
		vide, sinon un des 11 fidèles au hasard). Appelée une fois à la
		création, puis à chaque entrée dans la chapelle.

		Chaque banc et ses occupants sont regroupés en UNE seule unité
		(self.pew_units) plutôt que deux listes séparées : ainsi ils
		partagent le même point de tri en Y et ne peuvent jamais se
		désynchroniser (le fidèle devant, le banc derrière, ou l'inverse).
		"""
		self.pew_units = []
		for row_index, y in enumerate(self.pew_row_ys):
			for side, pew_x in (("left", self.pew_left_x), ("right", self.pew_right_x)):
				if side == "left" and row_index == self.library_gap_row_index:
					continue

				pew_rect = self.pew_double.get_rect(midbottom=(pew_x, y))
				occupants = []
				for offset in self.seat_offsets:
					if random.random() < 1 / 3:
						occupant = None
					else:
						occupant = random.randint(0, 10)
					seat_y = y - self.pew_double.get_height() // 3 + 4
					occupants.append((pew_x + offset, seat_y, occupant))

				self.pew_units.append((self.pew_double, pew_rect, occupants))
	def __init__(self):
		self.sheet = pygame.image.load("chapel_interior_walls.png").convert_alpha()
		self.sheet2 = pygame.image.load("chapel_interior_objects.png").convert_alpha()
		self.sheet3 = pygame.image.load("interior_objects.png").convert_alpha()

		scale = CHAPEL_WALL_SCALE

		def cut(rect):
			x, y, w, h = rect
			piece = self.sheet.subsurface((x, y, w, h))
			return pygame.transform.scale(piece, (int(w * scale), int(h * scale)))

		def cut2(rect):
			x, y, w, h = rect
			piece = self.sheet2.subsurface((x, y, w, h))
			return pygame.transform.scale(piece, (int(w * scale), int(h * scale)))

		def cut3(rect):
			x, y, w, h = rect
			piece = self.sheet3.subsurface((x, y, w, h))
			return pygame.transform.scale(piece, (int(w * scale), int(h * scale)))	
		
		self.wall_panel = cut((51, 0, 26, 64))
		self.wall_corner = cut((133, 128, 21, 63))
		self.wall_side = cut((77,0,3,64))
		self.big_wall_side = cut((125, 0, 6, 12))
		self.big_wall_side_flipped = pygame.transform.flip(self.big_wall_side, True, False)
		self.wall_panel2 = cut((51, 0, 5, 60))
		self.arch_round = cut((0, 176, 112, 71))
		self.vitrail = cut((69, 400, 11, 45))
		self.vitrail_L = cut((10, 345, 12, 55))
		self.vitrail_R = cut((72, 345, 12, 55))
		self.tableau1 = cut2((10, 130, 20, 30))
		self.floor_tile = cut((32, 496, 32, 32))

		self.wall_back = cut((96, 0, 64, 64))          # mur plein, pour les segments horizontaux (haut/paliers)
		self.wall_left = cut((133, 128, 21, 63))        # pilier fin, pour les murs latéraux
		self.wall_right = pygame.transform.flip(self.wall_left, True, False)
		self.wall_gothic_arch = cut((0, 168, 112, 80))
		self.angel_statue = cut2((34, 4, 29, 72))
		self.dragon_statue = cut2((79, 5, 42, 72))
		self.deck2 = cut3((218, 225, 60, 37))
		self.bookshelf1 = cut3((330, 98, 50, 62))
		self.chest1 = cut3((243, 355, 27, 24))
		self.rug1 = cut3((0, 225, 80, 80))
		self.sofa1 = cut3((115, 300, 60, 50))

		# --- Géométrie : 3 paliers de largeur ---
		narrow_w = CHAPEL_NAVE_NARROW_WIDTH
		wide_extra = CHAPEL_NAVE_WIDE_EXTRA
		wide_w = narrow_w + wide_extra * 2

		alcove_h = CHAPEL_ALCOVE_HEIGHT
		pew_hall_h = CHAPEL_PEW_HALL_HEIGHT
		vase_nook_h = CHAPEL_VASE_NOOK_HEIGHT
		entrance_h = CHAPEL_ENTRANCE_HEIGHT

		lib_w = CHAPEL_LIBRARY_WIDTH

				# Chaque feuille Parishioner fait 4 colonnes x 12 rangées, mais la
		# TAILLE DE CELLULE varie d'un fichier à l'autre (36x48, 40x32,
		# 36x32, 40x48) -> on la calcule à partir des dimensions de la
		# feuille au lieu de la coder en dur.
		#
		# L'animation se lit EN COLONNE (les 12 rangées) et non en ligne :
		# les 4 colonnes d'une même rangée sont des copies identiques
		# simplement décalées horizontalement (c'est ce qui faisait
		# "glisser" le fidèle en x). En descendant une colonne, le x reste
		# constant et seul le contenu bouge -> vraie animation sur place.
		#
		# Enfin, chaque frame est recadrée sur la boîte réelle du contenu
		# (commune aux 12 frames, pour ne pas écraser le petit mouvement
		# vertical), sinon l'ancrage midbottom tombe dans le vide de la
		# cellule et le fidèle flotte au-dessus du banc.
		self.parishioner_frames = []
		for i in range(1, 12):
			sheet = pygame.image.load(f"Parishioner{i}.png").convert_alpha()
			cell_w = sheet.get_width() // 4
			cell_h = sheet.get_height() // 12

			cells = [
				sheet.subsurface((0, row * cell_h, cell_w, cell_h))
				for row in range(12)
			]

			bounds = [cell.get_bounding_rect() for cell in cells]
			left = min(b.left for b in bounds)
			top = min(b.top for b in bounds)
			right = max(b.right for b in bounds)
			bottom = max(b.bottom for b in bounds)
			crop = pygame.Rect(left, top, right - left, bottom - top)

			frames = []
			for cell in cells:
				piece = cell.subsurface(crop)
				frames.append(pygame.transform.scale(
					piece,
					(int(crop.width * CHAPEL_DECOR_SCALE),
					 int(crop.height * CHAPEL_DECOR_SCALE))
				))
			self.parishioner_frames.append(frames)

				# Certains fidèles ont des cheveux/une capuche qui dépassent sous
		# le corps -> leur boîte de recadrage est plus haute qu'elle ne
		# devrait "visuellement" l'être pour l'ancrage au banc. On les
		# remonte d'autant lors du dessin (voir main.py). Valeurs de
		# départ à ajuster : indices 0-based, donc 0 = Parishioner1.
		self.parishioner_hair_offset = {
			0: 9,    # Parishioner1 - cheveux longs
			5: -4,    # Parishioner6 - capuche
			10: -12,  # Parishioner11 - capuche + longue mèche
		}
		self.parishioner_frame = 0
		self.parishioner_timer = 0

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
		self.entrance2_rect = pygame.Rect(narrow_left, y-500, narrow_w, entrance_h+500)

		self.library_rect = pygame.Rect(0, self.pew_hall_rect.top, lib_w, pew_hall_h-200)

		# Point d'entrée (venant de l'extérieur) et zone de sortie -
		# ce sont de simples repères, pas des hitbox de collision (qui
		# viendront à la toute dernière étape).
		self.entrance_point = (self.entrance_rect.centerx, self.entrance_rect.bottom - 30)
		self.exit_rect = pygame.Rect(0, 0, 160, 100)
		self.exit_rect.center = (self.entrance_rect.centerx, self.entrance_rect.bottom - 20)
		self.objects_sheet = pygame.image.load("chapel_interior_objects.png").convert_alpha()
		self.house_deco_sheet = pygame.image.load("Interior.png").convert_alpha()

		decor_scale = CHAPEL_DECOR_SCALE
		altar_sheet = pygame.image.load("chapel_altar.png").convert_alpha()
		self.altar_frames = load_animation(altar_sheet, ALTAR_SCALE, 3)
		self.altar_frame = 0
		self.altar_timer = 0

		altar_w, altar_h = self.altar_frames[0].get_size()
		self.altar_rect = pygame.Rect(0, 0, altar_w, altar_h)
		self.altar_rect.midbottom = (self.entrance_rect.centerx, 550)

		Candelabra_sheet = pygame.image.load("Candelabra.png").convert_alpha()
		self.candelabra_frames = load_animation(Candelabra_sheet, decor_scale, 3)
		self.candelabra_frame = 0
		self.candelabra_timer = 0

		candelabra_w, candelabra_h = self.candelabra_frames[0].get_size()
		self.candelabra_rect1 = pygame.Rect(0, 0, candelabra_w, candelabra_h)
		self.candelabra_rect1.midbottom = (self.entrance_rect.centerx-730, 735)
		self.candelabra_rect2 = pygame.Rect(0, 0, candelabra_w, candelabra_h)
		self.candelabra_rect2.midbottom = (self.entrance_rect.centerx - 800, 735)

		def cut_obj(rect, s=None):
			x, y, w, h = rect
			piece = self.objects_sheet.subsurface((x, y, w, h))
			s = decor_scale if s is None else s
			return pygame.transform.scale(piece, (int(w * s), int(h * s)))

		# Tapis de l'allée : le sprite source (0,0,32,128) a une bande
		# "escalier" plus sombre vers y=27-35 -- on prend un morceau
		# propre du motif plus bas (y=40-72) pour un carrelage sans
		# cette marque répétée.
		self.carpet_main = cut_obj((0, 40, 32, 32))

		# Moitié du tapis rouge ovale de la maison (Interior.png), pour
		# la porte de la bibliothèque : coupé en deux sur son axe
		# vertical, on garde la moitié DROITE (bord plat à gauche,
		# arrondi qui dépasse à droite -- vers la nef).
		red_rug_full = self.house_deco_sheet.subsurface((124, 295, 56, 66))
		red_rug_full = pygame.transform.scale(
			red_rug_full,
			(int(56 * decor_scale), int(66 * decor_scale))
		)
		half_w = red_rug_full.get_width() // 2
		self.library_rug_half = red_rug_full.subsurface(
			(half_w, 0, red_rug_full.get_width() - half_w, red_rug_full.get_height())
		)
		statues_sheet = pygame.image.load("Statues.png").convert_alpha()

		self.angel_frames = []
		self.dragon_frames = []
		for f in range(3):
			angel_piece = statues_sheet.subsurface((f * 112, 0, 56, 80))
			dragon_piece = statues_sheet.subsurface((f * 112 + 56, 0, 56, 80))
			self.angel_frames.append(pygame.transform.scale(
				angel_piece,
				(int(56 * CHAPEL_DECOR_SCALE), int(80 * CHAPEL_DECOR_SCALE))
			))
			self.dragon_frames.append(pygame.transform.scale(
				dragon_piece,
				(int(56 * CHAPEL_DECOR_SCALE), int(80 * CHAPEL_DECOR_SCALE))
			))

		self.statue_frame = 0
		self.statue_timer = 0

		statue_pairs = [
			350,    # coins tout en haut
			725,    # coins concaves (270°) vers y=565
			1440,   # coins tout en bas
		]
		self.statue_positions = [(730, y) for y in statue_pairs]
		self.dragon_positions = [(1520, y) for y in statue_pairs]

		self.pew_double = cut_obj((139, 37, 49, 32))

				# Bancs placés symétriquement de part et d'autre du tapis bleu,
		# à distance égale de son bord.
		carpet_half_w = self.carpet_main.get_width() // 2
		carpet_center_x = self.entrance_rect.centerx
		pew_gap = 40   # écart entre le bord du tapis et le bord du banc

		pew_w = self.pew_double.get_width()
		self.pew_left_x = carpet_center_x - carpet_half_w - pew_gap - pew_w // 2
		self.pew_right_x = carpet_center_x + carpet_half_w + pew_gap + pew_w // 2

		pew_h = self.pew_double.get_height()
		pew_spacing = pew_h + 20
		self.pew_row_ys = list(range(700, 1250, pew_spacing))

		# Rangée la plus proche du tapis rouge -> banc de gauche retiré
		self.library_gap_row_index = min(
			range(len(self.pew_row_ys)),
			key=lambda i: abs(self.pew_row_ys[i] - self.library_rect.centery)
		)

		self.seat_offsets = [-(pew_w // 4), pew_w // 4]

		self.reset_seating()

		self._build_walls()

	def _tile_horizontal(self, surface, tile, x0, x1, y):
		tw = tile.get_width()
		for x in range(x0, x1, tw):
			surface.blit(tile, (x, y))

	def _tile_vertical(self, surface, tile, y0, y1, x):
		th = tile.get_height()
		for y in range(y0, y1, th):
			surface.blit(tile, (x, y))

	def _wall_column_tiles(self, sprite, y0, y1, x):
		th = sprite.get_height()
		tiles = []
		for y in range(y0, y1, th):
			rect = sprite.get_rect(midtop=(x, y))
			tiles.append((sprite, rect))
		return tiles

	def _wall_row_tiles(self, sprite, x0, x1, y):
		tw = sprite.get_width()
		tiles = []
		for x in range(x0, x1, tw):
			rect = sprite.get_rect(topleft=(x, y))
			tiles.append((sprite, rect))
		return tiles

	def _slice_vertical(self, sprite, rect, slice_height=18):
		"""
		Découpe un sprite vertical (pilier, colonne) en fines tranches
		horizontales pour un tri en Y progressif : sans ça, un pilier de
		190px de haut bascule d'un coup, entièrement, devant/derrière sur
		UNE seule ligne, au lieu de se révéler progressivement comme le
		fait déjà le mur carrelé (tuiles de 36px).
		"""
		slices = []
		y = 0
		height = sprite.get_height()
		width = sprite.get_width()
		while y < height:
			h = min(slice_height, height - y)
			piece = sprite.subsurface((0, y, width, h))
			piece_rect = pygame.Rect(rect.x, rect.y + y, width, h)
			slices.append((piece, piece_rect))
			y += h
		return slices

	def _build_walls(self):
		self.static_surface = pygame.Surface((self.width, self.height))
		self.static_surface.fill((10, 10, 15))
		self.wall_hitboxes = []
		floor_color = (120, 118, 130)
		arch_x = self.alcove_rect.centerx - self.wall_gothic_arch.get_width() // 2

		# Couloir de bancs (étroit) : x=470 -> entrance_rect.right, y=122 -> 565
		pew_hall_floor = pygame.Rect(
			470+188, 122, self.entrance_rect.right - 470-188, 565 - 122)

		# Niche à vases (large) : x=0 -> entrance_rect.right+162, y=565 -> 1265
		vase_nook_floor = pygame.Rect(
			0, 565, (self.entrance_rect.right + 162), 1265 - 565)

		# Alcôve (haut) : provisoire, calée sur l'arche + les segments de
		# mur autour d'elle -- à ajuster si ça dépasse encore visuellement

		# Gardés en mémoire pour le debug F1 (points aux coins)
		
		self.floor_rects = [
			pew_hall_floor, vase_nook_floor,
			self.entrance2_rect, self.library_rect
		]

		for rect in self.floor_rects:
			self._tile_floor(self.static_surface, rect)

		# --- Alcôve (haut) ---

		# --- Couloir d'entrée (bas) : pas de mur en bas, la porte
		# extérieure viendra plus tard ---
		# rug1 était placé hors écran : x négatif + y très bas, donc il
		# n'apparaissait jamais. On le remet dans le champ visible.
		self.rug1_rect = self.rug1.get_rect(midtop=(self.entrance_rect.centerx-870, 920))
		self.static_surface.blit(self.rug1, self.rug1_rect)
		self.sofa1_rect = self.sofa1.get_rect(midtop=(self.entrance_rect.centerx-739, 1120))
		
		
		wall_h = self.wall_panel.get_height()
		y = self.entrance_rect.bottom - wall_h // 1.4
		col_y = self.entrance_rect.bottom - wall_h // 1.1
		y2 = 380
		door_w = CHAPEL_EXIT_DOOR_WIDTH
		door_left = self.entrance_rect.centerx - door_w // 2
		door_right = self.entrance_rect.centerx + door_w // 2
				# Tapis central : de la porte du bas jusqu'à 200px sous le sommet
		carpet_x = self.entrance_rect.centerx - self.carpet_main.get_width() // 2
		self._tile_vertical(self.static_surface, self.carpet_main,
			500, self.height, carpet_x)
		# Tapis en demi-cercle devant la porte de la bibliothèque
		rug_x = 470   # bord du couloir de bancs réel, côté bibliothèque
		rug_y = self.library_rect.centery - self.library_rug_half.get_height() // 2
		self.static_surface.blit(self.library_rug_half, (rug_x, rug_y))
		self._tile_horizontal(self.static_surface, self.wall_panel2,
			645, 1000, 122)
		self.wall_hitboxes.append(pygame.Rect(645, 122, 1000 - 645, self.wall_panel2.get_height()))

		self._tile_horizontal(self.static_surface, self.wall_panel2,
			arch_x+self.wall_gothic_arch.get_width(), arch_x+self.wall_gothic_arch.get_width()+305, 122)
		self.wall_hitboxes.append(pygame.Rect(
			arch_x + self.wall_gothic_arch.get_width(), 122, 305, self.wall_panel2.get_height()
		))
		corner_rect_7 = self.wall_corner.get_rect(midtop=(645, 84))
		self.static_surface.blit(self.wall_corner, corner_rect_7)
		
		self.tile_vertical_symmetric(
			self.static_surface, self.big_wall_side,
			122, 565,
			offset_x=self.entrance_rect.width // 2,
			centerx=self.entrance_rect.centerx
		)
		self.wall_hitboxes.append(pygame.Rect(
			self.entrance_rect.centerx - self.entrance_rect.width // 2, 122,
			self.big_wall_side.get_width(), 565 - 122
		))
		self.wall_hitboxes.append(pygame.Rect(
			self.entrance_rect.centerx + self.entrance_rect.width // 2, 122,
			self.big_wall_side.get_width(), 565 - 122
		))

		self._tile_horizontal(self.static_surface, self.wall_panel2,
			470, 645, 565)
		self.wall_hitboxes.append(pygame.Rect(645, 122, 1000 - 645, self.wall_panel2.get_height()))

		self._tile_horizontal(self.static_surface, self.wall_panel2,
			arch_x+self.wall_gothic_arch.get_width(), arch_x+self.wall_gothic_arch.get_width()+305, 122)
		self.wall_hitboxes.append(pygame.Rect(
			arch_x + self.wall_gothic_arch.get_width(), 122, 305, self.wall_panel2.get_height()
		))

		corner_rect_7b = self.wall_corner.get_rect(
			midtop=(2 * self.entrance_rect.centerx - 645, 84))
		self.static_surface.blit(self.wall_corner, corner_rect_7b)
		self.tile_vertical_symmetric(
					self.static_surface, self.big_wall_side,
					122, 565,
					offset_x=self.entrance_rect.width // 2,
					centerx=self.entrance_rect.centerx
				)
		self._tile_horizontal(self.static_surface, self.wall_panel2,
			470, 645, 565)
		self.wall_hitboxes.append(pygame.Rect(470, 565, 645 - 470, self.wall_panel2.get_height()))

		self._tile_horizontal(self.static_surface, self.wall_panel2,
			0, 470, 565)
		self.wall_hitboxes.append(pygame.Rect(0, 565, 470, self.wall_panel2.get_height()))

		self._tile_horizontal(self.static_surface, self.wall_panel2,
			self.entrance_rect.right, 1775, 565)
		self.wall_hitboxes.append(pygame.Rect(
			self.entrance_rect.right, 565,
			1775 - self.entrance_rect.right, self.wall_panel2.get_height()
		))

		corner_rect_5 = self.wall_corner.get_rect(midtop=(475, 527))
		self.static_surface.blit(self.wall_corner, corner_rect_5)
		self.wall_hitboxes.append(corner_rect_5.copy())

		self.vase_nook_wall_tiles = self._wall_column_tiles(self.big_wall_side, 565, 1265, 470)

		# --- Porte de la bibliothèque : trou dans la hitbox du mur x=470 ---
		# Le passage est percé au niveau du centre Y du tapis rouge
		# (library_rug_half est posé pile sur library_rect.centery, même
		# formule que son blit plus haut) : si tu déplaces le tapis, le
		# trou suit automatiquement. Largeur du passage en Y =
		# CHAPEL_LIBRARY_DOOR_WIDTH (settings.py).
		door_cy = self.library_rect.centery
		door_top = door_cy - CHAPEL_LIBRARY_DOOR_WIDTH // 2
		door_bottom = door_cy + CHAPEL_LIBRARY_DOOR_WIDTH // 2

		wall_x = 470
		wall_top = 565
		wall_bottom = 1265

		# Segment de mur AU-DESSUS du passage
		self.wall_hitboxes.append(pygame.Rect(
			wall_x, wall_top,
			self.big_wall_side.get_width(),
			door_top - wall_top
		))
		# Segment de mur EN-DESSOUS du passage
		self.wall_hitboxes.append(pygame.Rect(
			wall_x, door_bottom,
			self.big_wall_side.get_width(),
			wall_bottom - door_bottom
		))
		corner_rect_4 = self.wall_corner.get_rect(midtop=(0, 527))
		self.static_surface.blit(self.wall_corner, corner_rect_4)
		self.wall_hitboxes.append(corner_rect_4.copy())

		self._tile_vertical(self.static_surface, self.big_wall_side,565, 1265, 0)
		self.wall_hitboxes.append(pygame.Rect(0, 565, self.big_wall_side.get_width(), 1265 - 565))

		self._tile_vertical(self.static_surface, self.big_wall_side_flipped,565, 1265, self.entrance_rect.right+162)
		self.wall_hitboxes.append(pygame.Rect(
			self.entrance_rect.right + 162, 565, self.big_wall_side_flipped.get_width(), 1265 - 565
		))

		self._tile_horizontal(self.static_surface, self.wall_panel2,
			470, 645, 1265)
		self.wall_hitboxes.append(pygame.Rect(470, 1265, 645 - 470, self.wall_panel2.get_height()))

		self._tile_horizontal(self.static_surface, self.wall_panel2,
			self.entrance_rect.right, 1775, 1265)
		self.wall_hitboxes.append(pygame.Rect(
			self.entrance_rect.right, 1265,
			1775 - self.entrance_rect.right, self.wall_panel2.get_height()
		))
		self._tile_horizontal(self.static_surface, self.wall_panel,
			self.entrance_rect.left, door_left, y)
		self.wall_hitboxes.append(pygame.Rect(
			self.entrance_rect.left, int(y), door_left - self.entrance_rect.left, self.wall_panel.get_height()
		))

		self._tile_horizontal(self.static_surface, self.wall_panel,
			door_right, self.entrance_rect.right, y)
		self.wall_hitboxes.append(pygame.Rect(
			door_right, int(y), self.entrance_rect.right - door_right, self.wall_panel.get_height()
		))
		sidewall_length = CHAPEL_ENTRANCE_SIDEWALL1_LENGTH
		corner_rect_3 = self.wall_corner.get_rect(midtop=(645, 1227))
		self.static_surface.blit(self.wall_corner, corner_rect_3)
		corner_rect_3b = self.wall_corner.get_rect(
			midtop=(2 * self.entrance_rect.centerx - 645, 1227))
		self.static_surface.blit(self.wall_corner, corner_rect_3b)
		self.tile_vertical_symmetric(
			self.static_surface, self.big_wall_side,
			self.entrance_rect.bottom - sidewall_length, self.entrance_rect.bottom,
			offset_x=self.entrance_rect.width // 2,
			centerx=self.entrance_rect.centerx
		)
		self.wall_hitboxes.append(pygame.Rect(
			self.entrance_rect.centerx - self.entrance_rect.width // 2,
			self.entrance_rect.bottom - sidewall_length,
			self.big_wall_side.get_width(), sidewall_length
		))
		self.wall_hitboxes.append(pygame.Rect(
			self.entrance_rect.centerx + self.entrance_rect.width // 2,
			self.entrance_rect.bottom - sidewall_length,
			self.big_wall_side.get_width(), sidewall_length
		))
		# Coins, aux deux extrémités du mur du bas
		corner_rect_left = self.wall_corner.get_rect(midtop=(self.entrance_rect.left, col_y))
		self.static_surface.blit(self.wall_corner, corner_rect_left)
		corner_rect_right = self.wall_corner.get_rect(midtop=(self.entrance_rect.right, col_y))
		self.static_surface.blit(self.wall_corner, corner_rect_right)
		#self.static_surface.blit(self.wall_gothic_arch, (arch_x, 50))
		arch_y = 50
		wall_line_y = 122   # hauteur à partir de laquelle l'arche entre "dans" la pièce
		arch_w, arch_h = self.wall_gothic_arch.get_size()
		cutoff = max(0, min(arch_h, wall_line_y - arch_y))

		if cutoff > 0:
			top_part = self.wall_gothic_arch.subsurface((0, 0, arch_w, cutoff))
			top_silhouette = pygame.mask.from_surface(top_part).to_surface(
				setcolor=(10, 10, 15, 255), unsetcolor=(0, 0, 0, 0)
			)
			self.static_surface.blit(top_silhouette, (arch_x, arch_y))

		bottom_part = self.wall_gothic_arch.subsurface((0, cutoff, arch_w, arch_h - cutoff))
		self.static_surface.blit(bottom_part, (arch_x, arch_y + cutoff))

				# Coins, un blit séparé par colonne pour contrôler l'ordre
		# individuellement (devant/derrière tel ou tel mur)

		corner_rect_6 = self.wall_corner.get_rect(midtop=(645, 527))
		tableau1_rect = self.tableau1.get_rect(midtop=(644, 550))
		tableau1_rect2 = self.tableau1.get_rect(midtop=(2 * self.entrance_rect.centerx - 646, 550))
		tableau1_rect3 = self.tableau1.get_rect(midtop=(self.entrance_rect.centerx-108, 150))
		tableau1_rect4 = self.tableau1.get_rect(midtop=(self.entrance_rect.centerx+105, 150))
		self.static_surface.blit(self.wall_corner, corner_rect_6)
		corner_rect_6b = self.wall_corner.get_rect(
			midtop=(2 * self.entrance_rect.centerx - 645, 527))
		self.static_surface.blit(self.wall_corner, corner_rect_6b)
		self.static_surface.blit(self.tableau1, tableau1_rect)
		self.static_surface.blit(self.tableau1, tableau1_rect2)
		self.static_surface.blit(self.tableau1, tableau1_rect3)
		self.static_surface.blit(self.tableau1, tableau1_rect4)

		for sprite, rect in self._wall_row_tiles(self.wall_panel2, 0, 470, 1265):
			self.vase_nook_wall_tiles.append((sprite, rect))
		self.wall_hitboxes.append(pygame.Rect(0, 1265, 470, self.wall_panel2.get_height()))

		corner_rect_8 = self.wall_corner.get_rect(
			midtop=(door_left, col_y))
		self.static_surface.blit(self.wall_corner, corner_rect_8)

		corner_rect_9 = self.wall_corner.get_rect(
			midtop=(door_right, col_y))
		self.static_surface.blit(self.wall_corner, corner_rect_9)
		corner_rect_1 = self.wall_corner.get_rect(midtop=(0, 1227))
		self.vase_nook_wall_tiles.append((self.wall_corner, corner_rect_1))
		self.wall_hitboxes.append(corner_rect_1.copy())
				
		corner_rect_2 = self.wall_corner.get_rect(midtop=(475, 1227))
		self.vase_nook_wall_tiles.append((self.wall_corner, corner_rect_2))
		self.wall_hitboxes.append(corner_rect_2.copy())
		self.vitrail_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-2, 96))
		self.vitrail_L_rect = self.vitrail_L.get_rect(midtop=(self.entrance_rect.centerx - 73, 97))
		self.vitrail_R_rect = self.vitrail_R.get_rect(midtop=(self.entrance_rect.centerx + 67, 97))
		self.static_surface.blit(self.vitrail, self.vitrail_rect)
		self.static_surface.blit(self.vitrail_L, self.vitrail_L_rect)
		self.static_surface.blit(self.vitrail_R, self.vitrail_R_rect)
		self.vitrail2_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-161, 120))
		self.vitrail3_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx+160, 120))
		self.vitrail4_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-221, 120))
		self.vitrail5_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx+220, 120))
		self.vitrail6_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-281, 120))
		self.vitrail7_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx+280, 120))
		self.vitrail8_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-341, 120))
		self.vitrail9_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx+340, 120))
		self.vitrail10_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-401, 120))
		self.vitrail11_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx+400, 120))
		self.vitrail12_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-531, 563))
		self.vitrail13_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx+530, 563))
		self.vitrail14_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-591, 563))
		self.vitrail15_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx+605, 563))
		self.vitrail16_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-531, 1264))
		self.vitrail17_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx+530, 1264))
		self.vitrail18_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-591, 1264))
		self.vitrail19_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx+605, 1264))
		self.vitrail20_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-401, 1501))
		self.vitrail21_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx+400, 1501))
		self.vitrail22_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-341, 1501))
		self.vitrail23_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx+340, 1501))
		self.vitrail24_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-281, 1501))
		self.vitrail25_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx+280, 1501))
		self.vitrail26_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-221, 1501))
		self.vitrail27_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx+220, 1501))
		self.vitrail28_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-161, 1501))
		self.vitrail29_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx+160, 1501))
		self.vitrail30_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-700, 1264))
		self.vitrail31_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-760, 1264))
		self.vitrail32_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-820, 1264))
		self.vitrail33_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-880, 1264))
		self.vitrail34_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-940, 1264))
		self.vitrail35_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-1000, 1264))
		self.vitrail36_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-1060, 1264))
		self.vitrail37_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-700, 563))
		self.vitrail38_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-760, 563))
		self.vitrail39_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-820, 563))		
		self.vitrail40_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-880, 563))
		self.vitrail41_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-940, 563))
		self.vitrail42_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-1000, 563))
		self.vitrail43_rect = self.vitrail.get_rect(midtop=(self.entrance_rect.centerx-1060, 563))


		self.static_surface.blit(self.vitrail, self.vitrail2_rect)
		self.static_surface.blit(self.vitrail, self.vitrail3_rect)		
		self.static_surface.blit(self.vitrail, self.vitrail4_rect)
		self.static_surface.blit(self.vitrail, self.vitrail5_rect)
		self.static_surface.blit(self.vitrail, self.vitrail6_rect)
		self.static_surface.blit(self.vitrail, self.vitrail7_rect)
		self.static_surface.blit(self.vitrail, self.vitrail8_rect)
		self.static_surface.blit(self.vitrail, self.vitrail9_rect)	
		self.static_surface.blit(self.vitrail, self.vitrail10_rect)
		self.static_surface.blit(self.vitrail, self.vitrail11_rect)
		self.static_surface.blit(self.vitrail, self.vitrail12_rect)
		self.static_surface.blit(self.vitrail, self.vitrail13_rect)	
		self.static_surface.blit(self.vitrail, self.vitrail14_rect)
		self.static_surface.blit(self.vitrail, self.vitrail15_rect)
		self.static_surface.blit(self.vitrail, self.vitrail16_rect)
		self.static_surface.blit(self.vitrail, self.vitrail17_rect)	
		self.static_surface.blit(self.vitrail, self.vitrail18_rect)
		self.static_surface.blit(self.vitrail, self.vitrail19_rect)	
		self.static_surface.blit(self.vitrail, self.vitrail20_rect)
		self.static_surface.blit(self.vitrail, self.vitrail21_rect)	
		self.static_surface.blit(self.vitrail, self.vitrail22_rect)
		self.static_surface.blit(self.vitrail, self.vitrail23_rect)
		self.static_surface.blit(self.vitrail, self.vitrail24_rect)
		self.static_surface.blit(self.vitrail, self.vitrail25_rect)
		self.static_surface.blit(self.vitrail, self.vitrail26_rect)
		self.static_surface.blit(self.vitrail, self.vitrail27_rect)
		self.static_surface.blit(self.vitrail, self.vitrail28_rect)
		self.static_surface.blit(self.vitrail, self.vitrail29_rect)
		for vitrail_rect in (
			self.vitrail30_rect, self.vitrail31_rect, self.vitrail32_rect,
			self.vitrail33_rect, self.vitrail34_rect, self.vitrail35_rect,
			self.vitrail36_rect,
		):
			self.vase_nook_wall_tiles.append((self.vitrail, vitrail_rect))
		self.static_surface.blit(self.vitrail, self.vitrail37_rect)
		self.static_surface.blit(self.vitrail, self.vitrail38_rect)
		self.static_surface.blit(self.vitrail, self.vitrail39_rect)
		self.static_surface.blit(self.vitrail, self.vitrail40_rect)
		self.static_surface.blit(self.vitrail, self.vitrail41_rect)
		self.static_surface.blit(self.vitrail, self.vitrail42_rect)
		self.static_surface.blit(self.vitrail, self.vitrail43_rect)
				# Les 6 statues : deux colonnes (x=470 à gauche, x=645 à droite),
		# ange à gauche / dragon à droite à chaque hauteur.

		
		self.bookshelf1_rect = self.bookshelf1.get_rect(midtop=(self.entrance_rect.centerx-1010, 570))
		self.deck2_rect = self.deck2.get_rect(midtop=(self.entrance_rect.centerx-1010, 750))
		self.chest1_rect = self.chest1.get_rect(midtop=(self.entrance_rect.centerx-900, 675))
		self.static_surface.blit(self.bookshelf1, self.bookshelf1_rect)
		self.static_surface.blit(self.chest1, self.chest1_rect)
		# self.deck2 sorti de static_surface : rejoint le tri en Y (main.py)

		self.chapel_furniture_sort_offset = {
			"sofa1": 0,
			"deck2": 0,
		}
				# ------------------------------------------------------------------
		# Hitboxes des meubles de la chapelle (même principe que dans House) :
		# chaque meuble reçoit un rect SÉPARÉ, indépendant du rect du sprite,
		# que tu peux redimensionner et déplacer librement. Clés possibles :
		#   ratio        -> hauteur de la hitbox en % de la hauteur du sprite (defaut 0.35)
		#   width_ratio  -> largeur de la hitbox en % de la largeur du sprite (defaut 1.0)
		#   height       -> hauteur fixe en pixels (prioritaire sur ratio)
		#   width        -> largeur fixe en pixels (prioritaire sur width_ratio)
		#   offset_x     -> décalage horizontal en pixels (defaut 0)
		#   offset_y     -> décalage vertical en pixels (defaut 0, négatif = vers le haut)
		#   anchor       -> point d'ancrage sur le rect du sprite (defaut "midbottom")
		# ------------------------------------------------------------------
		self.DEFAULT_CHAPEL_HITBOX_RATIO = 0.35

		# Tailles des sprites à l'échelle 3, pour repère :
		#   bookshelf1 150x186 | chest1 81x72 | sofa1 180x150
		#   deck2 180x111      | candelabra 96x96
		self.chapel_furniture_hitbox_config = {
			"bookshelf1":   {"height": 50, "width_ratio": 0.85, "offset_y": -90},
			"chest1":       {"ratio": 0.45, "width_ratio": 0.60, "offset_y": -90},
			"sofa1":        {"height": 85, "width_ratio": 0.80, "offset_y": 0},
			"deck2":        {"height": 10, "width_ratio": 0.85, "offset_y": -90},
			"candelabra1":  {"width": 30, "height": 30, "offset_x": 0, "offset_y": -90},
			"candelabra2":  {"width": 30, "height": 30, "offset_x": 0, "offset_y": -90},
			"altar":        {"height": 2, "width_ratio": 0.50, "offset_y": -100},
			"angel_0":      {"height": 30, "width_ratio": 0.60, "offset_y": -100},
			"angel_1":      {"height": 30, "width_ratio": 0.60, "offset_y": -100},
			"angel_2":      {"height": 30, "width_ratio": 0.60, "offset_y": -100},
			"dragon_0":     {"height": 30, "width_ratio": 0.60, "offset_y": -100},
			"dragon_1":     {"height": 30, "width_ratio": 0.60, "offset_y": -100},
			"dragon_2":     {"height": 30, "width_ratio": 0.60, "offset_y": -100},
		}

		self._build_chapel_furniture_hitboxes()
		# Un seul réglage, appliqué à chaque banc (même sprite, même
		# taille pour tous) -- pas besoin d'un nom par banc.
		self.pew_hitbox_config = {"height": 20, "width_ratio": 0.85, "offset_y": -90}
		self.pew_hitboxes = [
			self._make_chapel_hitbox(pew_rect, self.pew_hitbox_config)
			for pew_sprite, pew_rect, occupants in self.pew_units
		]
		self.chapel_furniture = {
			"sofa1": (self.sofa1, self.sofa1_rect),
			"deck2": (self.deck2, self.deck2_rect),
		}
		for index, offset in CHAPEL_WALL_HITBOX_OVERRIDES.items():
			if index < len(self.wall_hitboxes):
				self.wall_hitboxes[index].x += offset.get("offset_x", 0)
				self.wall_hitboxes[index].y += offset.get("offset_y", 0)

		self.interior_surface = self.static_surface.copy()

	def _make_chapel_hitbox(self, rect, cfg):
		"""Crée un rect de collision SÉPARÉ à partir du rect du sprite :
		taille par ratio du sprite ou en pixels fixes (prioritaires),
		ancré sur 'anchor' (defaut midbottom), puis décalé par les offsets."""
		ratio = cfg.get("ratio", self.DEFAULT_CHAPEL_HITBOX_RATIO)
		width_ratio = cfg.get("width_ratio", 1.0)

		height = cfg.get("height", max(4, int(rect.height * ratio)))
		width = cfg.get("width", max(4, int(rect.width * width_ratio)))

		hitbox = pygame.Rect(0, 0, width, height)

		anchor = cfg.get("anchor", "midbottom")
		setattr(hitbox, anchor, getattr(rect, anchor))

		hitbox.x += cfg.get("offset_x", 0)
		hitbox.y += cfg.get("offset_y", 0)

		return hitbox

	def _build_chapel_furniture_hitboxes(self):
		rects_by_name = {
			"sofa1":       self.sofa1_rect,
			"deck2":       self.deck2_rect,
			"bookshelf1":  self.bookshelf1_rect,
			"chest1":      self.chest1_rect,
			"candelabra1": self.candelabra_rect1,
			"candelabra2": self.candelabra_rect2,
			"altar":       self.altar_rect,
		}
		for i, pos in enumerate(self.statue_positions):
			rects_by_name[f"angel_{i}"] = self.angel_frames[0].get_rect(midbottom=pos)
		for i, pos in enumerate(self.dragon_positions):
			rects_by_name[f"dragon_{i}"] = self.dragon_frames[0].get_rect(midbottom=pos)

		self.chapel_furniture_hitboxes = {}
		for name, rect in rects_by_name.items():
			cfg = self.chapel_furniture_hitbox_config.get(name, {})
			self.chapel_furniture_hitboxes[name] = self._make_chapel_hitbox(rect, cfg)

	def update_altar(self, animation_speed=8):
		self.altar_timer += 1
		if self.altar_timer >= animation_speed:
			self.altar_timer = 0
			self.altar_frame += 1
			if self.altar_frame >= len(self.altar_frames):
				self.altar_frame = 0

	def update_candelabra(self, animation_speed=10):
		self.candelabra_timer += 1
		if self.candelabra_timer >= animation_speed:
			self.candelabra_timer = 0
			self.candelabra_frame += 1
			if self.candelabra_frame >= len(self.candelabra_frames):
				self.candelabra_frame = 0


	def update_statues(self, animation_speed=12):
		self.statue_timer += 1
		if self.statue_timer >= animation_speed:
			self.statue_timer = 0
			self.statue_frame += 1
			if self.statue_frame >= len(self.angel_frames):
				self.statue_frame = 0

	def update_parishioners(self, animation_speed=14):
		self.parishioner_timer += 1
		if self.parishioner_timer >= animation_speed:
			self.parishioner_timer = 0
			self.parishioner_frame += 1
			if self.parishioner_frame >= 12:
				self.parishioner_frame = 0

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

	def _tile_floor(self, surface, rect):
		"""
		Carrelle 'floor_tile' en alignant toujours sur la même grille
		globale (à partir de (0,0), le coin haut-gauche de la chapelle),
		même si 'rect' ne commence pas pile sur un multiple de la taille
		du carreau -- évite les coutures visibles entre deux rectangles
		de sol voisins, comme pour l'herbe en extérieur.
		"""
		tw, th = self.floor_tile.get_width(), self.floor_tile.get_height()

		previous_clip = surface.get_clip()
		surface.set_clip(rect)

		start_x = (rect.left // tw) * tw
		start_y = (rect.top // th) * th

		for x in range(start_x, rect.right, tw):
			for y in range(start_y, rect.bottom, th):
				surface.blit(self.floor_tile, (x, y))

		surface.set_clip(previous_clip)

	def draw_debug_hitboxes(self, surface):
		font = _get_debug_font()
		for index, rect in enumerate(self.wall_hitboxes):
			pygame.draw.rect(surface, (255, 80, 80), rect, 2)
			label = font.render(str(index), True, (255, 255, 0))
			surface.blit(label, (rect.x, rect.y - 12))
				# Hitboxes des meubles (orange, comme dans House)
		for name, rect in self.chapel_furniture_hitboxes.items():
			pygame.draw.rect(surface, (255, 170, 0), rect, 2)
			label = font.render(name, True, (255, 170, 0))
			surface.blit(label, (rect.x, rect.y - 14))

		# Hitboxes des bancs (cyan, numérotées comme les murs)
		for index, rect in enumerate(self.pew_hitboxes):
			pygame.draw.rect(surface, (0, 220, 220), rect, 2)
			label = font.render(str(index), True, (0, 220, 220))
			surface.blit(label, (rect.x, rect.y - 12))
					# Zone de sortie (vert, pour vérifier qu'elle tombe bien dans
		# l'ouverture de la porte du bas, entre les deux murs)
		pygame.draw.rect(surface, (0, 255, 0), self.exit_rect, 2)
		label = font.render("exit_rect", True, (0, 255, 0))
		surface.blit(label, (self.exit_rect.x, self.exit_rect.y - 14))

	def draw_debug_floor_corners(self, surface, radius=6):
		"""
		Dessine un point sur le coin haut-gauche (vert) et bas-droite
		(rouge) de chaque rectangle de sol -- pratique pour lire
		précisément où sont posées les bornes actuelles et ajuster les
		chiffres dans _build_walls en conséquence.
		"""
		font = _get_debug_font()
		for i, rect in enumerate(self.floor_rects):
			pygame.draw.circle(surface, (0, 255, 0), rect.topleft, radius)
			pygame.draw.circle(surface, (255, 0, 0), rect.bottomright, radius)

			label_tl = font.render(f"#{i} {rect.topleft}", True, (0, 255, 0))
			surface.blit(label_tl, (rect.left + 8, rect.top - 4))

			label_br = font.render(f"#{i} {rect.bottomright}", True, (255, 0, 0))
			surface.blit(label_br, (rect.right - label_br.get_width() - 8, rect.bottom - 14))