from turtle import update

import pygame
import random
import math

from pygame import key

from animations import load_animation
from animations import load_animation_row
from animations import load_animation_column
from animations import load_animation_grid
from animations import split_frames_by_regions
from settings import *
from classes import Player, Enemy, Coin, NPC, Tree, Rock, Apple, GoldenApple, ItemDrop, Potion
import npc_system
import waves
import world
import player_system
import window
import fight
import collision 
import decor     

pygame.init()

fullscreen = True

if fullscreen:
	desktop_size = pygame.display.get_desktop_sizes()[0]
	screen = pygame.display.set_mode(desktop_size, pygame.NOFRAME | pygame.SCALED, vsync=1)
else:
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED, vsync=1)

from fonts import *
import fonts
import dialogues
import healer
import ui
import merchant_1

load_font()
healer.load_healer_ui()
merchant_1.load_merchant_ui()

speed = PLAYER_SPEED
transition = True
debug_hitboxes = DEBUG_HITBOXES
portal_timer = 0
smoke_timer = 0
smoke_frame = 0
dragon_timer = 0
dragon_frame = 0
current_npc = None
awaiting_npc_arrival = None
healer_state = "main"
merchant_state = "main"
HEAL_ANIMATION_DURATION = 30
BUY_COIN_ANIMATION_DURATION = 30
POTION_ANIMATION_DURATION = 30
potion_heal_timer = 0
potion_heal_animation_start_hp = 0
potion_heal_animation_target_hp = 0
heal_timer = 0
merchant_coin_timer = 0
heal_animation_start_hp = 0
heal_animation_target_hp = 0
heal_animation_start_coins = 0
heal_animation_target_coins = 0
heal_price = 0
buy_animation_target_coins = 0
buy_animation_start_coins = 0
buy_price = 0
partial_hp = 0
heal_final = 0
healer_text = ""
merchant_1_text = ""
heal_offer = None
wave_finished = False
shop_open = False
close_rect = None
heal_rect = None
quit_rect = None
shop_rect = None
confirm_rect = None
back_rect = None 
back_rect_2 = None # for NPC UI close button
left_arrow_rect = None
right_arrow_rect = None
merchant1_page = 1
merchant1_max_pages = 4
goodbye_timer = 0
heal_finished = False
PLAYER_SORT_MARGIN = 70  # ajuste cette valeur selon le ressenti en jeu

game_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT)).convert()

player_scale = 0.20 #(gardée en reserve )

walk_down_sheet = pygame.image.load("run_down.png").convert_alpha()

player1_run_sheet = pygame.image.load("Swordsman_lvl1_Run_with_shadow.png").convert_alpha()
player1_idle_sheet = pygame.image.load("Swordsman_lvl1_Idle_with_shadow.png").convert_alpha()
player1_attack_sheet = pygame.image.load("Swordsman_lvl1_attack_with_shadow.png").convert_alpha()
player1_hurt_sheet = pygame.image.load("Swordsman_lvl1_Hurt_with_shadow.png").convert_alpha()

orc1_walk_sheet = pygame.image.load("orc1_run_full.png").convert_alpha()
orc1_death_sheet = pygame.image.load("orc1_death_full.png").convert_alpha()
orc1_hurt_sheet = pygame.image.load("orc1_hurt_full.png").convert_alpha()
orc1_attack_sheet = pygame.image.load("orc1_attack_full.png").convert_alpha()
orc1_idle_sheet = pygame.image.load("orc1_idle_full.png").convert_alpha()

grass = pygame.image.load("Herbe.jpg").convert()

portal_sheet = pygame.image.load("Dimensional_Portal.png").convert_alpha()

coins_sheet = pygame.image.load("MonedaD.png").convert_alpha()

frame_width = walk_down_sheet.get_width() // 8
frame_height = walk_down_sheet.get_height()

shop_exterior_sheet = pygame.image.load("exterior.png").convert_alpha()

trees_sheet = pygame.image.load("Trees_animation.png").convert_alpha()

smoke_sheet = pygame.image.load("Smoke_animation.png").convert_alpha()
smoke_animation = load_animation(smoke_sheet, HOUSE_SCALE, 6)

walls_sheet = pygame.image.load("walls_floor.png").convert_alpha()

healer_idle_sheet = pygame.image.load("Citizen1_Idle.png").convert_alpha()
healer_walk_sheet = pygame.image.load("Citizen1_Walk.png").convert_alpha()

merchant1_idle_sheet = pygame.image.load("Citizen2_Idle.png").convert_alpha()
merchant1_walk_sheet = pygame.image.load("Citizen2_Walk.png").convert_alpha()

priest_idle_sheet = pygame.image.load("priest_idle.png").convert_alpha()
priest_walk_sheet = pygame.image.load("priest_walk.png").convert_alpha()

chapel_dragon_sheet = pygame.image.load("chapel_dragon.png").convert_alpha()
chapel_dragon_body_sheet = pygame.image.load("chapel_dragon_body.png").convert_alpha()

plaza = pygame.image.load("plaza.png").convert_alpha()
plaza = pygame.transform.scale(
	plaza,
	(
		int(plaza.get_width() * 0.5),
		int(plaza.get_height() * 0.5)
	)
)

walk_down = load_animation_row(player1_run_sheet, 0, PLAYER_SCALE, 8, 4)
walk_left = load_animation_row(player1_run_sheet, 1, PLAYER_SCALE, 8, 4)
walk_right = load_animation_row(player1_run_sheet, 2, PLAYER_SCALE, 8, 4)
walk_up = load_animation_row(player1_run_sheet, 3, PLAYER_SCALE, 8, 4)

idle_down = load_animation_row(player1_idle_sheet, 0, PLAYER_SCALE, 12, 4)
idle_left = load_animation_row(player1_idle_sheet, 1, PLAYER_SCALE, 12, 4)
idle_right = load_animation_row(player1_idle_sheet, 2, PLAYER_SCALE, 12, 4)
idle_up = load_animation_row(player1_idle_sheet, 3, PLAYER_SCALE, 12, 4)

attack_down = load_animation_row(player1_attack_sheet, 0, PLAYER_SCALE, 8, 4)
attack_left = load_animation_row(player1_attack_sheet, 1, PLAYER_SCALE, 8, 4)
attack_right = load_animation_row(player1_attack_sheet, 2, PLAYER_SCALE, 8, 4)
attack_up = load_animation_row(player1_attack_sheet, 3, PLAYER_SCALE, 8, 4)

hurt_down = load_animation_row(player1_hurt_sheet, 0, PLAYER_SCALE, 5, 4)
hurt_left = load_animation_row(player1_hurt_sheet, 1, PLAYER_SCALE, 5, 4)
hurt_right = load_animation_row(player1_hurt_sheet, 2, PLAYER_SCALE, 5, 4)
hurt_up = load_animation_row(player1_hurt_sheet, 3, PLAYER_SCALE, 5, 4)

orc1_walk_down = load_animation_row(orc1_walk_sheet, 0, ORC_SCALE, 8, 4)
orc1_walk_up = load_animation_row(orc1_walk_sheet, 1, ORC_SCALE, 8, 4)
orc1_walk_left = load_animation_row(orc1_walk_sheet, 2, ORC_SCALE, 8, 4)
orc1_walk_right = load_animation_row(orc1_walk_sheet, 3, ORC_SCALE, 8, 4)

orc1_hurt_down = load_animation_row(orc1_hurt_sheet, 0, ORC_SCALE, 6, 4)
orc1_hurt_up = load_animation_row(orc1_hurt_sheet, 1, ORC_SCALE, 6, 4)
orc1_hurt_left = load_animation_row(orc1_hurt_sheet, 2, ORC_SCALE, 6, 4)
orc1_hurt_right = load_animation_row(orc1_hurt_sheet, 3, ORC_SCALE, 6, 4)

orc1_die_down = load_animation_row(orc1_death_sheet, 0, ORC_SCALE, 8, 4)
orc1_die_up = load_animation_row(orc1_death_sheet, 1, ORC_SCALE, 8, 4)
orc1_die_left = load_animation_row(orc1_death_sheet, 2, ORC_SCALE, 8, 4)
orc1_die_right = load_animation_row(orc1_death_sheet, 3, ORC_SCALE, 8, 4)

orc1_attack_down = load_animation_row(orc1_attack_sheet, 0, ORC_SCALE, 8, 4)
orc1_attack_up = load_animation_row(orc1_attack_sheet, 1, ORC_SCALE, 8, 4)
orc1_attack_left = load_animation_row(orc1_attack_sheet, 2, ORC_SCALE, 8, 4)
orc1_attack_right = load_animation_row(orc1_attack_sheet, 3, ORC_SCALE, 8, 4)

orc1_idle_down = load_animation_row(orc1_idle_sheet, 0, ORC_SCALE, 4, 4)
orc1_idle_up = load_animation_row(orc1_idle_sheet, 1, ORC_SCALE, 4, 4)
orc1_idle_left = load_animation_row(orc1_idle_sheet, 2, ORC_SCALE, 4, 4)
orc1_idle_right = load_animation_row(orc1_idle_sheet, 3, ORC_SCALE, 4, 4)

portal_animation = load_animation_row(portal_sheet, 0, PORTAL_SCALE, 3, 2)

coins_animation = load_animation(coins_sheet, COINS_SCALE, 5)

house_sprite = shop_exterior_sheet.subsurface(pygame.Rect(0, 0, 145, 128))
tree1 = load_animation_column(trees_sheet, 0, 3.5, 9, 13)
tree2 = load_animation_column(trees_sheet, 1, 3.5, 9, 13)   # même arbre, taille moyenne
tree3 = load_animation_column(trees_sheet, 2, 3.5, 9, 13)   # même arbre, petit buisson
tree4 = load_animation_column(trees_sheet, 3, 3.5, 9, 13)   # pommier
tree5 = load_animation_column(trees_sheet, 6, 3.5, 9, 13)   # arbre feuillu foncé
apple_sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
pygame.draw.circle(apple_sprite, (200, 30, 30), (16, 16), 14)
pygame.draw.circle(apple_sprite, (120, 15, 15), (16, 16), 14, 2)

golden_apple_sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
pygame.draw.circle(golden_apple_sprite, (255, 215, 0), (16, 16), 14)
pygame.draw.circle(golden_apple_sprite, (180, 140, 0), (16, 16), 14, 2)
rock_big_sprite = shop_exterior_sheet.subsurface(ROCK_BIG_RECT)
rock_big_sprite = pygame.transform.scale(
	rock_big_sprite,
	(int(rock_big_sprite.get_width() * ROCK_BIG_SCALE), int(rock_big_sprite.get_height() * ROCK_BIG_SCALE))
)

rock_medium_sprite = shop_exterior_sheet.subsurface(ROCK_MEDIUM_RECT)
rock_medium_sprite = pygame.transform.scale(
	rock_medium_sprite,
	(int(rock_medium_sprite.get_width() * ROCK_MEDIUM_SCALE), int(rock_medium_sprite.get_height() * ROCK_MEDIUM_SCALE))
)

healer_idle = load_animation_row(healer_idle_sheet, 0, NPC_SCALE, 12, 4)
healer_walk_down = load_animation_row(healer_walk_sheet, 0, NPC_SCALE, 6, 4)
healer_walk_left = load_animation_row(healer_walk_sheet, 1, NPC_SCALE, 6, 4)
healer_walk_right = load_animation_row(healer_walk_sheet, 2, NPC_SCALE, 6, 4)
healer_walk_up = load_animation_row(healer_walk_sheet, 3, NPC_SCALE, 6, 4)

merchant1_idle = load_animation_row(merchant1_idle_sheet, 0, NPC_SCALE, 12, 4)
merchant1_walk_down = load_animation_row(merchant1_walk_sheet, 0, NPC_SCALE, 6, 4)
merchant1_walk_left = load_animation_row(merchant1_walk_sheet, 1, NPC_SCALE, 6, 4)
merchant1_walk_right = load_animation_row(merchant1_walk_sheet, 2, NPC_SCALE, 6, 4)
merchant1_walk_up = load_animation_row(merchant1_walk_sheet, 3, NPC_SCALE, 6, 4)

priest_idle = load_animation_row(priest_idle_sheet, 0, NPC_SCALE, 12, 4)
priest_walk_down = load_animation_row(priest_walk_sheet, 0, NPC_SCALE, 6, 4)
priest_walk_left = load_animation_row(priest_walk_sheet, 1, NPC_SCALE, 6, 4)
priest_walk_right = load_animation_row(priest_walk_sheet, 2, NPC_SCALE, 6, 4)
priest_walk_up = load_animation_row(priest_walk_sheet, 3, NPC_SCALE, 6, 4)

chapel = world.Chapel(CHAPEL_X, CHAPEL_Y)

chapel_dragon_animation = load_animation_grid(
	chapel_dragon_sheet, DRAGON_SCALE, 5, 5, frame_count=24
)
chapel_dragon_body_sprite = pygame.transform.scale(
	chapel_dragon_body_sheet,
	(
		int(chapel_dragon_body_sheet.get_width() * DRAGON_SCALE),
		int(chapel_dragon_body_sheet.get_height() * DRAGON_SCALE)
	)
)

orc_animations = {
	"down": orc1_walk_down,
	"up": orc1_walk_up,
	"left": orc1_walk_left,
	"right": orc1_walk_right
}
orc_hurt_animations = {
	"down": orc1_hurt_down,
	"up": orc1_hurt_up,
	"left": orc1_hurt_left,
	"right": orc1_hurt_right
}
orc_death_animations = {
	"down": orc1_die_down,
	"up": orc1_die_up,
	"left": orc1_die_left,
	"right": orc1_die_right
}
orc_attack_animations = {
	"down": orc1_attack_down,
	"up": orc1_attack_up,
	"left": orc1_attack_left,
	"right": orc1_attack_right
}
orc_idle_animations = {
	"down": orc1_idle_down,
	"up": orc1_idle_up,
	"left": orc1_idle_left,
	"right": orc1_idle_right
}
orc_data = {
	"walk": orc_animations,
	"hurt": orc_hurt_animations,
	"death": orc_death_animations,
	"attack": orc_attack_animations,
	"idle": orc_idle_animations,
}
healer_walk_animations = {
	"down": healer_walk_down,
	"left": healer_walk_left,
	"right": healer_walk_right,
	"up": healer_walk_up,
}
merchant1_walk_animations = {
	"down": merchant1_walk_down,
	"left": merchant1_walk_left,
	"right": merchant1_walk_right,
	"up": merchant1_walk_up,
}
priest_walk_animations = {
	"down": priest_walk_down,
	"left": priest_walk_left,
	"right": priest_walk_right,
	"up": priest_walk_up,
}

house_sprite = pygame.transform.scale(house_sprite, (int(house_sprite.get_width() * HOUSE_SCALE), int(house_sprite.get_height() * HOUSE_SCALE)))
house_width = house_sprite.get_width()
house_height = house_sprite.get_height()


roof_height = 270   # à ajuster

house_roof = house_sprite.subsurface(
	(0, 0, house_width, roof_height)
)

house_base = house_sprite.subsurface(
	(0, roof_height, house_width, house_height - roof_height)
)


house_x = HOUSE_X
house_y = HOUSE_Y

house_rect = pygame.Rect(
	house_x + 145,
	house_y + 230,
	80,
	55
)

Player.current_animation = idle_down
Player.direction = "down"

Player.current_frame = 0
Player.frame_timer = 0

player = Player(5000, 5000, frame_width * PLAYER_SCALE, frame_height * PLAYER_SCALE)
healer_npc = NPC(
	400,
	250,
	healer_idle,
	healer_walk_animations,
	"heal",
	hitbox_width=40,
	hitbox_height=40,
	hitbox_offset_x=0,
	hitbox_offset_y=-60,
	movement_points=[
		(400, 250),   # 0 - passage
		(250, 280),   # 1 - passage (relie vers le coin commode/plante)
		(113, 306),   # 2 - ARRÊT : devant la commode
		(53, 408),    # 3 - ARRÊT : devant la plante
		(250, 450),   # 4 - passage (retour vers le circuit principal)
		(400, 400),   # 5 - passage
		(300, 500),   # 6 - ARRÊT (existant)
		(500, 500),   # 7 - passage
		(600, 350),   # 8 - ARRÊT (existant)
	],
	stop_point_indices=[2, 3, 6, 8],
	stop_look_directions={
		2: "up",   # regarde la commode
		3: "up",   # regarde la plante
	},
	speed=2,
	stop_duration_min_seconds=2,
	stop_duration_max_seconds=10
)
merchant1_npc = NPC(
	700,
	250,
	merchant1_idle,
	merchant1_walk_animations,
	"merchant_1",
	hitbox_width=40,
	hitbox_height=40,
	hitbox_offset_x=0,
	hitbox_offset_y= -60,
	movement_points=[
		(700, 250),   # 0 - passage
		(850, 300),   # 1 - passage
		(900, 450),   # 2 - ARRÊT
		(800, 600),   # 3 - ARRÊT
		(400, 400),   # 4 - passage : POINT COMMUN avec la guérisseuse (son index 5)
		(600, 400),   # 5 - passage
		(750, 480),   # 6 - ARRÊT  
		(730, 550),   # 7 - passage
	],
	stop_point_indices=[2, 3, 6],
	speed=2,
	stop_duration_min_seconds=2,
	stop_duration_max_seconds=10
)


npcs = [healer_npc, merchant1_npc]
house = world.House()

priest_npc = NPC(
	CHAPEL_X + 180, CHAPEL_Y + 700,
	priest_idle,
	priest_walk_animations,
	"priest_ambient",
	hitbox_offset_y=-60,
	movement_points=[
		(CHAPEL_X + 180, CHAPEL_Y + 700),   # 0 - ARRÊT
		(CHAPEL_X + 330, CHAPEL_Y + 740),   # 1 - passage
		(CHAPEL_X + 330, CHAPEL_Y + 820),   # 2 - ARRÊT
		(CHAPEL_X + 180, CHAPEL_Y + 800),   # 3 - passage
	],
	stop_point_indices=[0, 2],
	speed=1.5,
	stop_duration_min_seconds=3,
	stop_duration_max_seconds=8
)
outdoor_npcs = [priest_npc]
# Pré-simulation : fait "vivre" les NPC avant même que le joueur ait
# ouvert la porte de la maison, pour qu'ils soient déjà en mouvement,
# désynchronisés, à des points différents de leur circuit dès la
# première entrée — plutôt que figés et alignés à leur position de
# départ.
_startup_colliders = [
	house.wall_top_hitbox,
	house.wall_bottom_hitbox,
	house.wall_left_hitbox,
	house.wall_right_hitbox,
]
_startup_colliders.extend(house.furniture_hitboxes.values())

for _ in range(3000):  # ~50 secondes de circuit simulées instantanément
	for npc in npcs:
		npc.update(_startup_colliders, None)

# Désactivé pour l'instant : le prêtre n'apparaît nulle part tant que
# l'intérieur de la chapelle n'existe pas. Décommenter avec la Partie 5.3
# et la Partie 5.4 quand ce sera le cas.
# _chapel_startup_colliders = [chapel.hitbox, house.hitbox]
# for _ in range(3000):
# 	for npc in outdoor_npcs:
# 		npc.update(_chapel_startup_colliders, None)

ground_details = decor.load_ground_details(splat_scale=SPLAT_SCALE, tuft_scale=TUFT_SCALE)

grass_color = pygame.transform.average_color(grass)
ground_color = decor.adjust_ground_color(grass_color, darken=GROUND_COLOR_DARKEN, desaturate=GROUND_COLOR_DESATURATE)
ground_layer = decor.build_ground_layer(
	MAP_WIDTH,
	MAP_HEIGHT,
	grass_color,
	ground_details["grass_tufts"],
	spacing=GROUND_TUFT_SPACING,
	jitter=GROUND_TUFT_JITTER,
	coverage=GROUND_TUFT_COVERAGE
)


plaza_center = (
	MAP_WIDTH // 2 + PORTAL_SIZE // 2 + PORTAL_OFFSET_X,
	MAP_HEIGHT // 2 + PORTAL_SIZE // 2 + PORTAL_OFFSET_Y
)
path_end = (house.door_hitbox.centerx, house.door_hitbox.bottom - 10)
path_splats = decor.generate_path(ground_details, plaza_center, path_end, half_width=PATH_HALF_WIDTH)
plaza_sprite = decor.load_plaza_sprite(scale=0.5)

shop_decor_layer, shop_decor_pos = decor.build_shop_decor_layer(
	ground_details,
	plaza_sprite,
	plaza_center,
	plaza_center,
	path_end,
	half_width=PATH_HALF_WIDTH,
	step=PLAZA_STEP,
	fill_chance=PLAZA_FILL_CHANCE,
	rock_chance=PATH_ROCK_CHANCE
)
chapel_path_layer, chapel_path_pos = decor.build_path_layer(
	ground_details, plaza_center, chapel.entrance_point,
	half_width=PATH_HALF_WIDTH, rock_chance=PATH_ROCK_CHANCE
)
# Ordre important : les cailloux (plaza_rocks) sont ajoutés en DERNIER,
# donc dessinés en dernier dans la boucle plus bas -> toujours au-dessus
# des taches de terre et du chemin.
shop_ground_decor = path_splats 

camera_x = 0
camera_y = 0

portal_rect = None
portal_frame = 0
portal_timer = 0
portal_animation_speed = 8

enemies = []
for i in range(MONSTRES):
	enemies.append(waves.spawn_enemy(orc_data))
coins = []
colliders = []


clock = pygame.time.Clock()

attacking = False
attack_done = False
next_attack = 1
attack_hitbox = None
game_state = "wave"

current_level = 1
current_wave = 1
portal = None
waves.start_wave(enemies, current_level, current_wave, orc_data)

monsters_to_spawn = MONSTRES
player.inventory = [
	{"item": None, "quantity": 0},
	{"item": None, "quantity": 0},
	{"item": None, "quantity": 0}
]
town_trees = []
tree_species = [
	(TREE_POSITIONS, tree1),
	(TREE_POSITIONS_TYPE2, tree2),
	(TREE_POSITIONS_TYPE3, tree3),
]

tree_index = 0
for positions, frames in tree_species:
	for x, y in positions:
		overrides = TREE_HITBOX_OVERRIDES.get(tree_index, {})
		town_trees.append(Tree(
			x, y, frames,
			index=tree_index,
			hitbox_width=overrides.get("width", 24),
			hitbox_height=overrides.get("height", 18),
			hitbox_offset_x=overrides.get("offset_x", 0),
			hitbox_offset_y=overrides.get("offset_y", TREE_HITBOX_OFFSET_Y),
			sway_min_seconds=TREE_SWAY_MIN_SECONDS,
			sway_max_seconds=TREE_SWAY_MAX_SECONDS,
			sway_frame_speed=TREE_SWAY_FRAME_SPEED
		))
		tree_index += 1

town_rocks = []
rock_species = [
	(ROCK_POSITIONS_BIG, rock_big_sprite, ROCK_BIG_HITBOX),
	(ROCK_POSITIONS_MEDIUM, rock_medium_sprite, ROCK_MEDIUM_HITBOX),
]

rock_index = 0
for positions, sprite, default_hitbox in rock_species:
	for x, y in positions:
		overrides = ROCK_HITBOX_OVERRIDES.get(rock_index, {})
		town_rocks.append(Rock(
			x, y, sprite,
			index=rock_index,
			hitbox_width=overrides.get("width", default_hitbox["width"]),
			hitbox_height=overrides.get("height", default_hitbox["height"]),
			hitbox_offset_x=overrides.get("offset_x", 0),
			hitbox_offset_y=overrides.get("offset_y", ROCK_HITBOX_OFFSET_Y)
		))
		rock_index += 1

house_bounds = (
	house_x - 150,
	house_y - 150,
	house_x + house_width + 150,
	house_y + house_height + 150
)

level_tree_placements = world.generate_level_trees(
	[tree1, tree2, tree3],
	(player.rect.centerx, player.rect.centery),
	MAP_WIDTH, MAP_HEIGHT,
	plaza_center, path_end, house_bounds,
	count=LEVEL_TREE_COUNT,
	min_spacing=LEVEL_TREE_MIN_SPACING,
	avoid_radius=LEVEL_TREE_AVOID_RADIUS
)

level_trees = [
	Tree(x, y, frames, index=i, hitbox_offset_y=TREE_HITBOX_OFFSET_Y)
	for i, (x, y, frames) in enumerate(level_tree_placements)
]
rock_variants = [
	(rock_big_sprite, ROCK_BIG_HITBOX),
	(rock_medium_sprite, ROCK_MEDIUM_HITBOX),
]

apple_tree_placements = world.generate_apple_trees(
	tree4,
	[(x, y) for x, y, _ in level_tree_placements],
	(player.rect.centerx, player.rect.centery),
	MAP_WIDTH, MAP_HEIGHT,
	plaza_center, path_end, house_bounds,
	max_count=APPLE_TREE_MAX_COUNT,
	spawn_chance=APPLE_TREE_SPAWN_CHANCE
)
apple_trees = [
	Tree(x, y, frames, hitbox_offset_y=TREE_HITBOX_OFFSET_Y)
	for x, y, frames in apple_tree_placements
]
for tree in apple_trees:
	tree.dropped_apple = False
	tree.dropped_golden_apple = False

level_rock_placements = world.generate_level_rocks(
	rock_variants,
	[(x, y) for x, y, _ in level_tree_placements] + [(x, y) for x, y, _ in apple_tree_placements],
	(player.rect.centerx, player.rect.centery),
	MAP_WIDTH, MAP_HEIGHT,
	plaza_center, path_end, house_bounds,
	count=LEVEL_ROCK_COUNT,
	min_spacing=LEVEL_ROCK_MIN_SPACING
)
level_rocks = [
	Rock(x, y, sprite, hitbox_width=hitbox["width"], hitbox_height=hitbox["height"], hitbox_offset_y=ROCK_HITBOX_OFFSET_Y)
	for x, y, sprite, hitbox in level_rock_placements
]

item_drops = []
player.selected_slot = 0
coins_to_collect = 0

run = True
while run == True :
	colliders.clear()
	if game_state == "house":
		screen.fill((0, 0, 0))
		house.interior_surface = house.draw_interior()
	
		
	player.apply_knockback()
	
	player_system.update_hurt(player, hurt_up, hurt_down, hurt_left, hurt_right)

	old_pos = player.rect.copy()
	if not attacking and player.state != "hurt" and current_npc is None and awaiting_npc_arrival is None:
		moving = player_system.movement(player, speed, walk_up, walk_down, walk_left, walk_right)

		near_npc = npc_system.get_interactable_npc(player, npcs)

	if game_state == "house":
		colliders.extend([
		house.wall_top_hitbox,
		house.wall_bottom_hitbox,
		house.wall_left_hitbox,
		house.wall_right_hitbox
	])
		colliders.extend(house.furniture_hitboxes.values())

		for npc in npcs:
			npc.update(colliders, player)

		colliders.extend(npc.hitbox_for_players for npc in npcs)

		# Le NPC est arrivé face au joueur : on ouvre le dialogue
		# maintenant, pas au moment où E a été pressé.
				# Le NPC est arrivé face au joueur : on ouvre le dialogue
		# seulement une fois le petit délai d'orientation écoulé.
		if (awaiting_npc_arrival is not None
				and awaiting_npc_arrival.state == "talking"
				and awaiting_npc_arrival.talk_delay_timer <= 0):
			current_npc = awaiting_npc_arrival
			awaiting_npc_arrival = None
			dialogues.reset()
			healer_state = "main"
			merchant_state = "main"

			if current_npc.type == "heal":
				if not player.met_healer:
					healer_text = random.choice(healer.healer_dialogues["first_meeting"])
					dialogues.start_dialogue(healer_text)
					player.met_healer = True
				else:
					hp_ratio = player.hp / player.max_hp
					if hp_ratio > 0.99:
						healer_text = random.choice(healer.healer_dialogues["healthy"])
						dialogues.start_dialogue(healer_text)
					elif hp_ratio < 0.25:
						healer_text = random.choice(healer.healer_dialogues["critical"])
						dialogues.start_dialogue(healer_text)
					else:
						healer_text = random.choice(healer.healer_dialogues["normal"])
						dialogues.start_dialogue(healer_text)

			elif current_npc.type == "merchant_1":
				if not player.met_merchant:
					merchant_1_text = random.choice(merchant_1.merchant_1_dialogues["first_meeting"])
					dialogues.start_dialogue(merchant_1_text)
					player.met_merchant = True
				else:
					merchant_1_text = random.choice(merchant_1.merchant_1_dialogues["normal"])
					dialogues.start_dialogue(merchant_1_text)
	else:
		player.clamp_to_map(MAP_WIDTH, MAP_HEIGHT)

	if game_state != "house":

		camera_x = player.rect.centerx - screen.get_width() // 2
		camera_y = player.rect.centery - screen.get_height() // 2
	else:
		camera_x = 0
		camera_y = 0

	if camera_x < 0:
		camera_x = 0 
	if camera_y < 0:
		camera_y = 0
	if camera_x > MAP_WIDTH - screen.get_width():
		camera_x = MAP_WIDTH - screen.get_width()
	if camera_y > MAP_HEIGHT - screen.get_height():
		camera_y = MAP_HEIGHT - screen.get_height()

	VIEWPORT_MARGIN = 300
	visible_rect = pygame.Rect(
		camera_x - VIEWPORT_MARGIN,
		camera_y - VIEWPORT_MARGIN,
		screen.get_width() + VIEWPORT_MARGIN * 2,
		screen.get_height() + VIEWPORT_MARGIN * 2
	)
	if game_state != "house":
		world.draw_ground(game_surface, ground_layer, camera_x, camera_y, screen.get_width(), screen.get_height())
	if game_state == "shop":
		visible_trees = [tree for tree in town_trees if visible_rect.colliderect(tree.rect)]
		visible_rocks = [rock for rock in town_rocks if visible_rect.colliderect(rock.rect)]
	else:
		visible_trees = []
		visible_rocks = []
	if game_state == "shop":
		colliders.append(house.hitbox)
		colliders.append(chapel.hitbox)
		colliders.extend(tree.hitbox for tree in visible_trees)
		colliders.extend(rock.hitbox for rock in visible_rocks)

		# for npc in outdoor_npcs:
		# 	npc.update(colliders, None)

	if game_state == "wave":
		colliders.extend(tree.hitbox for tree in level_trees)
		colliders.extend(tree.hitbox for tree in apple_trees)
		colliders.extend(rock.hitbox for rock in level_rocks)

	collision.resolve_player_collisions(player, colliders, old_pos)

	player.update_hitbox()

	player_system.idle(player, moving, attacking, idle_up, idle_down, idle_left, idle_right)


	attacking, next_attack = player_system.animate(player, moving, attacking, next_attack)
	
	if game_state == "shop":
		portal_timer, portal_frame = world.update_portal(
	game_state,
	portal_timer,
	portal_frame,
	portal_animation_speed,
	portal_animation
)
		smoke_timer, smoke_frame = world.update_smoke(
	game_state,
	smoke_timer,
	smoke_frame,
	SMOKE_ANIMATION_SPEED,
	smoke_animation
)
		dragon_timer, dragon_frame = world.update_dragon(
	game_state,
	dragon_timer,
	dragon_frame,
	DRAGON_ANIMATION_SPEED,
	chapel_dragon_animation
)
	was_attack_done = attack_done
	attack_done, killed_this_attack = fight.resolve_player_attack(
		player,
		enemies,
		attacking,
		attack_done,
		attack_hitbox,
		player.max_targets
	)

	if game_state == "wave" and not was_attack_done and attack_done:
		for tree in apple_trees:
			if not tree.dropped_apple and attack_hitbox and attack_hitbox.colliderect(tree.rect):
				if random.random() < APPLE_DROP_CHANCE:
					item_drops.append(ItemDrop(
						tree.rect.centerx, tree.rect.bottom - 10, Apple(apple_sprite),
						fall_height=ITEM_DROP_FALL_HEIGHT, fall_duration=ITEM_DROP_FALL_DURATION
					))
					tree.dropped_apple = True

		if len(killed_this_attack) >= GOLDEN_APPLE_KILL_COUNT:
			kill_x = sum(e.rect.centerx for e in killed_this_attack) / len(killed_this_attack)
			kill_y = sum(e.rect.centery for e in killed_this_attack) / len(killed_this_attack)
			for tree in apple_trees:
				if tree.dropped_golden_apple:
					continue
				dist = math.hypot(tree.rect.centerx - kill_x, tree.rect.centery - kill_y)
				if dist <= GOLDEN_APPLE_KILL_RADIUS:
					if random.random() < GOLDEN_APPLE_DROP_CHANCE:
						item_drops.append(ItemDrop(
							tree.rect.centerx, tree.rect.bottom - 10, GoldenApple(golden_apple_sprite),
							fall_height=ITEM_DROP_FALL_HEIGHT, fall_duration=ITEM_DROP_FALL_DURATION
						))
						tree.dropped_golden_apple = True
	

	for coin in coins[:]:
		if player.hitbox.colliderect(coin.rect):
			player.coins += coin.value
			coins.remove(coin)

	if game_state == "wave":
		for drop in item_drops[:]:
			drop.update(player)
			if player.hitbox.colliderect(drop.rect):
				if player.add_item_to_inventory(drop.item):
					item_drops.remove(drop)

	entities = []
	entities.append(("player", player, player.hitbox.bottom + PLAYER_SORT_MARGIN))
	if game_state == "house":
		for name, (sprite, rect, sort_y) in house.furniture_sprites.items():
			entities.append(("furniture", (sprite, rect), sort_y))
		for npc in npcs:
			entities.append(("npc", npc, npc.rect.bottom))

	if game_state == "shop":
		for tree in visible_trees:
			entities.append(("tree", tree, tree.rect.bottom))
		for rock in visible_rocks:
			entities.append(("rock", rock, rock.rect.bottom))
		# for npc in outdoor_npcs:
		# 	entities.append(("outdoor_npc", npc, npc.rect.bottom))
			
	if game_state == "wave":
		for tree in level_trees:
			entities.append(("tree", tree, tree.rect.bottom))
		for tree in apple_trees:
			entities.append(("tree", tree, tree.rect.bottom))
		for rock in level_rocks:
			entities.append(("rock", rock, rock.rect.bottom))
			
	if game_state == "shop":
		if player.hitbox.colliderect(portal_rect):
			game_state = "wave"
			current_level, current_wave, transition, TRANSITION_TIMER = world.start_new_level(enemies, current_level, orc_data)

			spawn_x, spawn_y = world.random_spawn_position(MAP_WIDTH, MAP_HEIGHT)
			player.rect.center = (spawn_x, spawn_y)
			player.update_hitbox()
			level_tree_placements = world.generate_level_trees(
				[tree1, tree2, tree3],
				(spawn_x, spawn_y),
				MAP_WIDTH, MAP_HEIGHT,
				plaza_center, path_end, house_bounds,
				count=LEVEL_TREE_COUNT,
				min_spacing=LEVEL_TREE_MIN_SPACING,
				avoid_radius=LEVEL_TREE_AVOID_RADIUS
			)
			level_trees = [
				Tree(x, y, frames, index=i, hitbox_offset_y=TREE_HITBOX_OFFSET_Y)
				for i, (x, y, frames) in enumerate(level_tree_placements)
			]

			apple_tree_placements = world.generate_apple_trees(
				tree4,
				[(x, y) for x, y, _ in level_tree_placements],
				(spawn_x, spawn_y),
				MAP_WIDTH, MAP_HEIGHT,
				plaza_center, path_end, house_bounds,
				max_count=APPLE_TREE_MAX_COUNT,
				spawn_chance=APPLE_TREE_SPAWN_CHANCE
			)
			apple_trees = [
				Tree(x, y, frames, hitbox_offset_y=TREE_HITBOX_OFFSET_Y)
				for x, y, frames in apple_tree_placements
			]
			for tree in apple_trees:
				tree.dropped_apple = False
				tree.dropped_golden_apple = False

			level_rock_placements = world.generate_level_rocks(
				rock_variants,
				[(x, y) for x, y, _ in level_tree_placements] + [(x, y) for x, y, _ in apple_tree_placements],
				(spawn_x, spawn_y),
				MAP_WIDTH, MAP_HEIGHT,
				plaza_center, path_end, house_bounds,
				count=LEVEL_ROCK_COUNT,
				min_spacing=LEVEL_ROCK_MIN_SPACING
			)
			level_rocks = [
				Rock(x, y, sprite, hitbox_width=hitbox["width"], hitbox_height=hitbox["height"], hitbox_offset_y=ROCK_HITBOX_OFFSET_Y)
				for x, y, sprite, hitbox in level_rock_placements
			]

			item_drops.clear()
	
	if game_state == "wave":
		level_obstacle_hitboxes = (
			[tree.rect for tree in level_trees]
			+ [tree.rect for tree in apple_trees]
			+ [rock.rect for rock in level_rocks]
		)
	else:
		level_obstacle_hitboxes = []

	for enemy in enemies:
		if transition == False:
			enemy.update(player, level_obstacle_hitboxes)

	collision.resolve_entity_collisions(enemies)

	for enemy in enemies[:]: 
		if enemy.dead_finished: 
			coins.append(Coin(enemy.rect.centerx, enemy.rect.centery, coins_animation))
			enemies.remove(enemy)

	if game_state == "wave" and len(enemies) == 0:
		coins_to_collect = min(5, len(coins))
		for coin in coins[:coins_to_collect]:
			coin.auto_collect = True

		if current_wave < 3:
			current_wave += 1
			waves.start_wave(enemies, current_level, current_wave, orc_data)
			transition = True
			TRANSITION_TIMER = 120

		else:
			merchant_1.refresh_shop()
			game_state = "shop"
			transition = True
			TRANSITION_TIMER = 120
			portal_x = MAP_WIDTH // 2 + PORTAL_OFFSET_X
			portal_y = MAP_HEIGHT // 2 + PORTAL_OFFSET_Y

			portal_rect = pygame.Rect(portal_x, portal_y, PORTAL_SIZE, PORTAL_SIZE)

			player.rect.center = (
				plaza_center[0] - PLAYER_SHOP_SPAWN_OFFSET_X,
				plaza_center[1] + PLAYER_SHOP_SPAWN_OFFSET_Y
			)
			player.update_hitbox()

		if transition and TRANSITION_TIMER <= 60:
			for coin in coins[:]:
				coin.auto_collect = False
			coins.clear()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		
		if event.type == pygame.KEYDOWN:
			
			# Cheat: press SPACE to kill all enemies on the map
			if event.key == pygame.K_SPACE:
				for e in enemies:
					# deal lethal damage using the player as source so death logic runs
					e.take_damage(e.hp, player)
			elif event.key == pygame.K_F1:
				debug_hitboxes = not debug_hitboxes
			elif event.key == pygame.K_F2:
				mx, my = pygame.mouse.get_pos()
				world_x = mx + camera_x
				world_y = my + camera_y
				print(f"OFFSET_X = {world_x - house_x}")
				print(f"OFFSET_Y = {world_y - house_y}")
			elif event.key == pygame.K_F3:
				mx, my = pygame.mouse.get_pos()
				world_x = mx + camera_x
				world_y = my + camera_y
				print(f"DRAGON_OFFSET_X = {world_x - chapel.rect.centerx}")
				print(f"DRAGON_OFFSET_Y = {world_y - chapel.rect.top}")
			elif event.key == pygame.K_F4:
				mx, my = pygame.mouse.get_pos()
				world_x = mx + camera_x
				world_y = my + camera_y
				print(f"DRAGON_BODY_OFFSET_X = {world_x - chapel.rect.centerx}")
				print(f"DRAGON_BODY_OFFSET_Y = {world_y - chapel.rect.top}")

		if event.type == pygame.MOUSEWHEEL:

			player.selected_slot = (
			player.selected_slot - event.y
			) % len(player.inventory)

		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				# Check if close button clicked on NPC UI
				if current_npc:

										# Fermer la fenêtre
					if close_rect and close_rect.collidepoint(event.pos):
						current_npc.end_conversation()
						current_npc = None
						close_rect = None
						dialogues.reset()
						healer_state = "main"

					if current_npc and current_npc.type == "heal":
					# Bouton Se soigner
						if healer_state == "main" and heal_rect.collidepoint(event.pos):
							heal_finished = False
							dialogues.reset()
							healer.previous_healer_state = healer_state
							missing_hp = player.max_hp - player.hp
							heal_price = math.ceil(missing_hp / 10 * 3)
							partial_hp = 0
							if missing_hp == 0:

								healer_text = (
			"Tu sembles deja en parfaite sante. "
			"Garde ton or, tu en auras certainement besoin..."
		)
								dialogues.start_dialogue(healer_text)
							elif player.coins >= heal_price:

								healer_text = (
			f"Il te manque {missing_hp} hp. "
			f"Je peux te soigner completement pour {heal_price} pieces d'or."
		)
								dialogues.start_dialogue(healer_text)
							else:

								partial_hp = min((player.coins * 10) // 3, missing_hp)

								healer_text = (
			f"Il te manque {missing_hp} hp. "
			f"Je peux te rendre {partial_hp} hp pour tout ton or."
		)
								dialogues.start_dialogue(healer_text)
							heal_offer = {
	"missing_hp": missing_hp,
	"price": heal_price,
	"heal_amount": missing_hp if player.coins >= heal_price else partial_hp,
	"partial": partial_hp if player.coins < heal_price else 0
}

							healer_state = "confirm"
					# Bouton Quitter
											# Bouton Quitter
						elif healer_state == "main" and quit_rect.collidepoint(event.pos):
							dialogues.reset()
							current_npc = None
							close_rect = None
							healer_state = "main"

					# Boutons de confirmation
						elif healer_state in ("confirm", "heal_confirm"):
							if missing_hp>0:
								if confirm_rect.collidepoint(event.pos):
									heal_price = heal_offer["price"]
									heal_final = heal_offer["heal_amount"]
									if player.hp < player.max_hp and heal_final > 0:
										heal_timer = HEAL_ANIMATION_DURATION
										heal_animation_start_hp = player.hp
										heal_animation_target_hp = min(player.max_hp, player.hp + heal_final)
										heal_animation_start_coins = player.coins
										heal_animation_target_coins = max(0, player.coins - heal_price)

								elif back_rect.collidepoint(event.pos):
									healer.previous_healer_state = healer_state
									dialogues.reset()
									healer_state = "main"
							if back_rect.collidepoint(event.pos):
								healer.previous_healer_state = healer_state
								dialogues.reset()
								healer_state = "main"
					elif current_npc and current_npc.type == "merchant_1":
						
						if merchant_state == "main":
							
							if quit_rect and quit_rect.collidepoint(event.pos):
								current_npc = None
								close_rect = None
								dialogues.reset()
								merchant_state = "main"

							elif shop_rect and shop_rect.collidepoint(event.pos):
								merchant_1.previous_merchant_state = merchant_state
								dialogues.reset()
								merchant_state = "shop"
								
						elif merchant_state == "shop":
							
							if merchant_1.back_rect_2 and merchant_1.back_rect_2.collidepoint(event.pos):
								
								merchant_1.previous_merchant_state = merchant_state
								dialogues.reset()
								merchant_state = "main"

								merchant_1_text = random.choice(merchant_1.merchant_1_dialogues["normal"])
								dialogues.start_dialogue(merchant_1_text)
							
							if right_arrow_rect and merchant_1.merchant1_page < merchant_1.merchant1_max_page and right_arrow_rect.collidepoint(event.pos):
								merchant_1.merchant1_page += 1
							if left_arrow_rect and merchant_1.merchant1_page > 1 and left_arrow_rect.collidepoint(event.pos):
								merchant_1.merchant1_page -= 1

							start = (merchant_1.merchant1_page - 1) * 6
							end = start + 6

							current_items = merchant_1.merchant_inventory[start:end]

							for item in current_items:
								if merchant_coin_timer == 0:
									if item.rect and item.rect.collidepoint(event.pos):
										if item.stock <= 0:
											merchant_1.set_click_text(
											"Rupture de stock."
										)
										elif player.coins < item.price:
											merchant_1.set_click_text(
											"Vous n'avez pas assez d'or."
										)
										else:
											if player.add_item_to_inventory(item):

												item.stock -= 1
												merchant_1.set_click_text(
												f"Vous achetez {item.name}."
											)
												merchant_coin_timer = BUY_COIN_ANIMATION_DURATION
												buy_animation_start_coins = player.coins
												buy_animation_target_coins = player.coins - item.price

											else:
												merchant_1.set_click_text(
												   "Votre inventaire est plein."
											)
				else:
					# Only allow attacking if not in NPC interaction
					attacking, attack_done, attack_hitbox = fight.handle_attack_event(
						player,
						attacking,
						enemies,
						attack_done,
						attack_hitbox,
						attack_up,
						attack_down,
						attack_left,
						attack_right,
						player_system
					)
			elif event.button == 3:
				if not attacking and player.state != "hurt" and current_npc is None:
					slot = player.inventory[player.selected_slot]
					item = slot["item"]

					if item is not None:
						if isinstance(item, Potion) and potion_heal_timer == 0:
							potion_heal_animation_start_hp = player.hp
							potion_heal_animation_target_hp = min(player.max_hp, player.hp + item.heal)
							potion_heal_timer = POTION_ANIMATION_DURATION

							slot["quantity"] -= 1
							if slot["quantity"] <= 0:
								slot["item"] = None
								slot["quantity"] = 0

						elif isinstance(item, (Apple, GoldenApple)):
							item.use(player)

							slot["quantity"] -= 1
							if slot["quantity"] <= 0:
								slot["item"] = None
								slot["quantity"] = 0
		if event.type == pygame.KEYDOWN:

			if event.key == pygame.K_e:
				if current_npc:
					
					if not dialogues.dialogue_finished:
						dialogues.skip_dialogue()
					else:
					# Close NPC interaction if already open
						current_npc = None
						close_rect = None
						healer_state = "main"
						merchant_state = "main"
						heal_offer = None
				elif near_npc and awaiting_npc_arrival is None:
					# On ne lance plus le dialogue tout de suite : le NPC
					# doit d'abord venir se placer face au joueur.
					near_npc.begin_conversation(player)
					awaiting_npc_arrival = near_npc
				else: 

					if game_state == "shop":

						if player.hitbox.colliderect(house.door_hitbox):

							game_state = "house"
							player.rect.center = (
							house.door_rect.centerx,
							HOUSE_INSIDE_HEIGHT - 220
							)			
							player.hitbox.center = player.rect.center
							player.direction = "up"

					elif game_state == "house":

						if player.hitbox.colliderect(house.door_rect):

							game_state = "shop"
							player.rect.center = (
							house.door_hitbox.centerx,
							house.door_hitbox.bottom + 40
					)
							player.hitbox.center = player.rect.center
							player.direction = "down"

	for enemy in enemies:
		entities.append(("enemy", enemy, enemy.rect.bottom + 105))

	if game_state == "shop":
		game_surface.blit(chapel_path_layer, chapel_path_pos)
		game_surface.blit(shop_decor_layer, shop_decor_pos)

		game_surface.blit(house_base, (house_x, house_y + roof_height))
		game_surface.blit(chapel.base, (chapel.rect.x, chapel.rect.y + chapel.roof_height))
		if player.hitbox.colliderect(house.door_hitbox):
			door_text = ui.font.render("E entrer", True, (255, 255, 255))
			game_surface.blit(door_text, (house.door_hitbox.centerx - door_text.get_width() // 2, house.door_hitbox.top - 30))

	for coin in coins[:]:

		if coin.auto_collect:
			coin.move_auto(player)
		else:
			coin.move_towards_player(player)

		coin.update()

		if player.hitbox.colliderect(coin.rect):
			if player.hitbox.colliderect(coin.rect):
				player.coins += coin.value
				coins.remove(coin)

		coin.draw(game_surface)


	entities.sort(key=lambda entity: entity[2])

	for entity_type, entity, sort_y in entities:
		if entity_type == "player":
			if game_state == "house":
				player_system.draw_player(house.interior_surface, player, hurt_up, hurt_down, hurt_left, hurt_right)
			else:
				player_system.draw_player(game_surface, player, hurt_up, hurt_down, hurt_left, hurt_right)

		elif entity_type == "enemy":
			sprite = entity.current_animation[entity.current_frame]
			sprite_rect = sprite.get_rect(midbottom=(entity.rect.centerx, entity.rect.bottom + ORC_SPRITE_OFFSET_Y))
			game_surface.blit(sprite, sprite_rect)
			entity.draw_health_bar(game_surface, sprite_rect)
		elif entity_type == "furniture":
			sprite, rect = entity
			house.interior_surface.blit(sprite, rect)
		elif entity_type == "npc":
			entity.draw(house.interior_surface)
		elif entity_type == "tree":
			game_surface.blit(entity.image, entity.rect)
		elif entity_type == "rock":
			game_surface.blit(entity.image, entity.rect)
		# elif entity_type == "outdoor_npc":
		# 	entity.draw(game_surface)
		if game_state == "wave":
			for drop in item_drops:
				drop.draw(game_surface)

	if game_state == "shop":
		sprite = portal_animation[portal_frame]
		rect = sprite.get_rect(center=portal_rect.center)
		game_surface.blit(sprite, rect)
		game_surface.blit(house_roof, (house_x, house_y))
		smoke_sprite = smoke_animation[smoke_frame]
		smoke_rect = smoke_sprite.get_rect(
			midbottom=(house_x + HOUSE_SMOKE_OFFSET_X, house_y + HOUSE_SMOKE_OFFSET_Y)
		)
		game_surface.blit(smoke_sprite, smoke_rect)

		dragon_sprite = chapel_dragon_animation[dragon_frame]
		dragon_rect = dragon_sprite.get_rect(
			midtop=(chapel.rect.centerx + DRAGON_OFFSET_X, chapel.rect.top + DRAGON_OFFSET_Y)
		)
		game_surface.blit(dragon_sprite, dragon_rect)
		game_surface.blit(chapel.roof, (chapel.rect.x, chapel.rect.y))

		dragon_body_rect = chapel_dragon_body_sprite.get_rect(
			midtop=(chapel.rect.centerx + DRAGON_BODY_OFFSET_X, chapel.rect.top + DRAGON_BODY_OFFSET_Y)
		)
		game_surface.blit(chapel_dragon_body_sprite, dragon_body_rect)

	if game_state == "shop":
		for tree in town_trees:
			tree.update()

	if transition:
		TRANSITION_TIMER -= 1
		overlay_presence = True

		if TRANSITION_TIMER <= 0:
			transition = False

	if player.invicible_timer > 0:
		player.invicible_timer -= 1

	player.update_buffs()

	if heal_timer > 0:
		heal_timer -= 1
		progress = (HEAL_ANIMATION_DURATION - heal_timer) / HEAL_ANIMATION_DURATION
		player.hp = int(round(heal_animation_start_hp + (heal_animation_target_hp - heal_animation_start_hp) * progress))
		player.coins = int(round(heal_animation_start_coins + (heal_animation_target_coins - heal_animation_start_coins) * progress))
		if heal_timer == 0 and not heal_finished:
			player.hp = heal_animation_target_hp
			player.coins = heal_animation_target_coins
			healer_state = "goodbye"
			goodbye_timer = pygame.time.get_ticks()
			healer_text = random.choice(healer.healer_dialogues["goodbye"])
			dialogues.start_dialogue(healer_text)
			heal_finished = True
	if healer_state == "goodbye":
		if pygame.time.get_ticks() - goodbye_timer > 1500:
			healer_state = "main"
			current_npc = None
			goodbye_timer = 0

	if merchant_coin_timer > 0:
		merchant_coin_timer -= 1
		progress = 1 - merchant_coin_timer / BUY_COIN_ANIMATION_DURATION
		player.coins = int(
		buy_animation_start_coins +
		(buy_animation_target_coins - buy_animation_start_coins)
		* progress
		)
		if merchant_coin_timer == 0:
			player.coins = buy_animation_target_coins

	if potion_heal_timer > 0:
		potion_heal_timer -= 1
		progress = (POTION_ANIMATION_DURATION - potion_heal_timer) / POTION_ANIMATION_DURATION
		player.hp = int(round(
		potion_heal_animation_start_hp +
		(potion_heal_animation_target_hp - potion_heal_animation_start_hp) * progress
	))
		if potion_heal_timer == 0:
			player.hp = potion_heal_animation_target_hp
 
	if game_state == "house":
			if player.hitbox.colliderect(house.door_rect):

				exit_text = ui.font.render("E sortir", True, (255, 255, 255))

				screen.blit(exit_text, (screen.get_width() // 2 - exit_text.get_width() // 2, screen.get_height() - 60))
	
	if near_npc:

		text = ui.font.render("E parler", True, (255,255,255))
		screen.blit(text, (screen.get_width()//2-text.get_width()//2, screen.get_height()-60))

	house.repeat_horizontal(house.top_wall_front, HOUSE_INSIDE_HEIGHT - house.top_wall_front.get_height() - 130)
	house.repeat_horizontal(house.wall_front, HOUSE_INSIDE_HEIGHT - house.wall_front.get_height())
	house.repeat_horizontal(house.wall_front, HOUSE_INSIDE_HEIGHT - house.wall_front.get_height())
	for window_rect in house.window_rects:
		house.interior_surface.blit(house.window, window_rect)
	house.interior_surface.blit(house.front_door, (HOUSE_INSIDE_WIDTH // 2 - house.front_door.get_width() // 2 + 93 + 195, HOUSE_INSIDE_HEIGHT - 126))
	if debug_hitboxes and game_state == "house":
		house.draw_debug_hitboxes(house.interior_surface)
		npc_debug_font = pygame.font.SysFont(None, 16)
		for npc in npcs:
			# Cyan : hitbox qui bloque le joueur (active dès maintenant)
			pygame.draw.rect(house.interior_surface, (0, 200, 255), npc.hitbox_for_players, 2)
			npc_label = npc_debug_font.render(npc.type + " (joueur)", True, (0, 200, 255))
			house.interior_surface.blit(npc_label, (npc.hitbox_for_players.x, npc.hitbox_for_players.y - 14))
		for npc in npcs:
			for i, point in enumerate(npc.movement_points):
				is_stop = i in npc.stop_point_indices
				color = (255, 80, 80) if is_stop else (255, 255, 0)
				pygame.draw.circle(house.interior_surface, color, point, 5)
				point_label = npc_debug_font.render(f"{npc.type} #{i}", True, color)
				house.interior_surface.blit(point_label, (point[0] + 6, point[1] - 6))
	if debug_hitboxes and game_state == "shop":
		tree_debug_font = pygame.font.SysFont(None, 16)
		for tree in town_trees:
			pygame.draw.rect(game_surface, (255, 80, 80), tree.hitbox, 2)
			label = tree_debug_font.render(f"arbre #{tree.index}", True, (255, 80, 80))
			game_surface.blit(label, (tree.hitbox.x, tree.hitbox.y - 14))
		for rock in town_rocks:
			pygame.draw.rect(game_surface, (80, 160, 255), rock.hitbox, 2)
			label = tree_debug_font.render(f"rocher #{rock.index}", True, (80, 160, 255))
			game_surface.blit(label, (rock.hitbox.x, rock.hitbox.y - 14))
		pygame.draw.rect(game_surface, (255, 80, 80), chapel.hitbox, 2)
		chapel_label = tree_debug_font.render("chapelle", True, (255, 80, 80))
		game_surface.blit(chapel_label, (chapel.hitbox.x, chapel.hitbox.y - 14))
		for npc in outdoor_npcs:
			pygame.draw.rect(game_surface, (0, 200, 255), npc.hitbox_for_players, 2)
			# Violet : hitbox réservée aux futures collisions NPC-meubles
		pygame.draw.rect(house.interior_surface, (170, 0, 255), npc.hitbox, 2)
		# Debug : rect complet du joueur (vert) + point utilisé pour le tri	
		pygame.draw.rect(house.interior_surface, (0, 255, 0), player.rect, 2)
		pygame.draw.line(
			house.interior_surface,
			(0, 255, 0),
			(player.rect.left, player.rect.bottom),
			(player.rect.right, player.rect.bottom),
			2
		)
		debug_font = pygame.font.SysFont(None, 16)
		player_label = f"player rect: h={player.rect.height} bottom={player.rect.bottom}"
		label_surface = debug_font.render(player_label, True, (0, 255, 0))
		house.interior_surface.blit(label_surface, (player.rect.x, player.rect.y - 14))
	if debug_hitboxes and game_state == "wave":
		for tree in level_trees:
			pygame.draw.rect(game_surface, (255, 80, 80), tree.hitbox, 2)
		for tree in apple_trees:
			pygame.draw.rect(game_surface, (255, 150, 0), tree.hitbox, 2)
		for rock in level_rocks:
			pygame.draw.rect(game_surface, (80, 160, 255), rock.hitbox, 2)

	if game_state == "house":
		overlay_presence = True
		inside_x = (screen.get_width() - HOUSE_INSIDE_WIDTH) // 2
		inside_y = (screen.get_height() - HOUSE_INSIDE_HEIGHT) // 2
		screen.blit(house.interior_surface, (inside_x, inside_y))
	else:
		overlay_presence = False
		screen.blit(game_surface, (-camera_x, -camera_y))

	inventory_slot_rects = [
	pygame.Rect(15, screen.get_height()-86, 64, 64),
	pygame.Rect(87, screen.get_height()-86, 64, 64),
	pygame.Rect(159, screen.get_height()-86, 64, 64)
]
	for i, rect in enumerate(inventory_slot_rects):

		slot = player.inventory[i]
		item = slot["item"]

		if item is not None:

			inventory_sprite = pygame.transform.scale(
			item.sprite,
			(rect.width - 16, rect.height - 16)   # marge pour laisser un peu d'espace dans le slot
		)
			sprite_rect = inventory_sprite.get_rect(center=rect.center)
			sprite_rect.y += 12   
			screen.blit(inventory_sprite, sprite_rect)

			quantity_font = fonts.lettersC6 if player.selected_slot == i else fonts.lettersC1
			if overlay_presence == True:
				quantity_font = fonts.lettersC4

			draw_body_text(
			screen,
			str(slot["quantity"]),
			rect.centerx - 9,
			rect.y - 10,
			30,
			quantity_font,
			max(1, UI_SCALE * 0.62)
		)
	if current_npc:
		dialogues.dialogue_timer += 1
		dialogues.update_dialogue()
		merchant_1.update_messages()

	ui.draw_health(screen, player)
	ui.draw_coins(screen, player)
	ui.draw_level(screen, current_level, current_wave, game_state)
	ui.draw_hotbar(screen, player)
	ui.draw_portal_indicator(screen,portal_rect, camera_x, camera_y, game_state)
	#for x, y, sprite in town_trees:
		#screen.blit(sprite[0], (x - camera_x, y - camera_y))
	ui.draw_transition(screen, transition, current_level, current_wave, game_state)

	# If interacting with an NPC, dim the rest of the screen and draw the NPC UI on top
	# Handle NPC interaction with dimmed overlay and close button
	if current_npc:
		overlay = pygame.Surface(screen.get_size())
		overlay.set_alpha(150)
		overlay.fill((0, 0, 0))
		overlay_presence = True
		screen.blit(overlay, (0, 0))
		if heal_timer > 0:
			ui.draw_health(screen, player)
			ui.draw_coins(screen, player)
		if merchant_coin_timer > 0:
			ui.draw_coins(screen, player)
		if current_npc and current_npc.type == "heal":
		
			missing_hp = player.max_hp - player.hp
			close_rect, heal_rect, quit_rect, confirm_rect, back_rect = healer.draw_healer_ui(screen, player, UI_SCALE, healer.shop_window_1, close_rect, healer.exit_button, healer.button_on, healer.button_on2, healer_state, heal_offer)
		elif current_npc and current_npc.type == "merchant_1":
			close_rect, shop_rect, quit_rect, left_arrow_rect, right_arrow_rect, slot_rects = merchant_1.draw_merchant_ui(
		screen,
		UI_SCALE,
		close_rect,
		merchant_state,
		merchant_1.button_on,
		merchant_1.button_on2
	)
	if transition == False and current_npc == None:
		overlay_presence = False
	pygame.display.update()
	clock.tick(FPS_MAX)

pygame.quit()