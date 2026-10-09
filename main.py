import os
import pygame 
import random  
import math
import json
import time

from pygame import key

from animations import load_animation
from animations import load_animation_row
from animations import load_animation_column
from animations import load_animation_grid
from animations import split_frames_by_regions 
from animations import load_item_sprite
from settings import *
from classes import Player, Enemy, Coin, NPC, Tree, Rock, Apple, GoldenApple, ItemDrop, Potion, Dynamite, DynamiteProjectile, XpOrb, Explosion, ArmorOffer
import npc_system
import waves
import world
import player_system
import window
import fight
import collision 
import decor  
import audio   

pygame.mixer.pre_init(44100, -16, 2, 512)
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
import librarian
import divinity

load_font()
healer.load_healer_ui()
merchant_1.load_merchant_ui()
librarian.load_librarian_ui()
divinity.load_divinity_ui()
audio.init()

speed = PLAYER_SPEED
transition = True

debug_monk_points = DEBUG_MONK_POINTS
portal_timer = 0
smoke_timer = 0
smoke_frame = 0
dragon_timer = 0
dragon_frame = 0
dragon_waiting = False
dragon_waiting_timer = 0
current_npc = None
awaiting_npc_arrival = None
healer_state = "main"
merchant_state = "main"
librarian_state = "main"
librarian_pay_rect = None
librarian_retour_rect = None
librarian_book_rects = []
librarian_quit_rect = None
librarian_back_rect = None
librarian_left_arrow_rect = None
librarian_right_arrow_rect = None
current_librarian_book = None
current_librarian_page = 0
librarian_coin_timer = 0
librarian_buy_animation_start_coins = 0
librarian_buy_animation_target_coins = 0
divinity_state = "main"
divinity_page = 0
divinity_skill_rects = []
divinity_quit_rect = None
divinity_left_arrow_rect = None
divinity_right_arrow_rect = None
divinity_purchase = None   # achat en cours : {skill, old_level, phase, timer}
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
DEV_START_GAME_STATE = "wave"
game_state = "intro"

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

priest_idle_sheet = pygame.image.load("Priest_Idle.png").convert_alpha()
priest_walk_sheet = pygame.image.load("Priest_Walk.png").convert_alpha()

chapel_dragon_sheet = pygame.image.load("chapel_dragon.png").convert_alpha()
chapel_dragon_body_sheet = pygame.image.load("chapel_dragon_body.png").convert_alpha()

dynamite_sheet = pygame.image.load("Dynamite.png").convert_alpha()

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
apple_sprite = load_item_sprite("apple.png", APPLE_SPRITE_SCALE)
golden_apple_sprite = load_item_sprite("golden_apple.png", APPLE_SPRITE_SCALE)
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

house = world.House()
chapel = world.Chapel(CHAPEL_X, CHAPEL_Y)
chapel_interior = world.ChapelInterior()

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

dynamite_sprite = dynamite_sheet.subsurface(0, 0, 16, 16)
scaled_dynamite = pygame.transform.scale(
	dynamite_sprite,
	(
		int(dynamite_sprite.get_width() * DYNAMITE_SCALE),
		int(dynamite_sprite.get_height() * DYNAMITE_SCALE)
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
if DEV_START_GAME_STATE == "chapel":
	player.rect.center = chapel_interior.entrance_point
	player.hitbox.center = player.rect.center
	player.direction = "up"

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
		(900, 500),   # 2 - ARRÊT
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
# --- Marchand : absences et armures -----------------------------
# Le calendrier : en mode DEV, absences aux niveaux de jeu 2 et 5 ;
# en mode normal, seuils tires au hasard dans les fourchettes.
if ARMOR_DEV_MODE:
	ARMOR_ABSENCE_LEVELS = [2, 5]
else:
	ARMOR_ABSENCE_LEVELS = [random.randint(*ARMOR1_ABSENCE_RANGE),
		random.randint(*ARMOR2_ABSENCE_RANGE)]
merchant_absent = False

def charger_animations_joueur(tier):
	# Reconstruit walk/idle/attack/hurt depuis les planches
	# Swordsman_lvl{tier}_*.png (meme decoupage que le lvl1).
	# Ne touche a rien (renvoie False) si une planche manque.
	niveau_sprite = tier + 1
	prefixe = f"Swordsman_lvl{niveau_sprite}_"
	fichiers = {
		"run": prefixe + "Run_with_shadow.png",
		"idle": prefixe + "Idle_with_shadow.png",
		"attack": prefixe + "attack_with_shadow.png",
		"hurt": prefixe + "Hurt_with_shadow.png",
	}
	if not all(os.path.exists(f) for f in fichiers.values()):
		return False
	run_sheet = pygame.image.load(fichiers["run"]).convert_alpha()
	idle_sheet = pygame.image.load(fichiers["idle"]).convert_alpha()
	attack_sheet = pygame.image.load(fichiers["attack"]).convert_alpha()
	hurt_sheet = pygame.image.load(fichiers["hurt"]).convert_alpha()
	for row, liste in ((0, walk_down), (1, walk_left), (2, walk_right), (3, walk_up)):
		liste[:] = load_animation_row(run_sheet, row, PLAYER_SCALE, 8, 4)
	for row, liste in ((0, idle_down), (1, idle_left), (2, idle_right), (3, idle_up)):
		liste[:] = load_animation_row(idle_sheet, row, PLAYER_SCALE, 12, 4)
	for row, liste in ((0, attack_down), (1, attack_left), (2, attack_right), (3, attack_up)):
		liste[:] = load_animation_row(attack_sheet, row, PLAYER_SCALE, 8, 4)
	for row, liste in ((0, hurt_down), (1, hurt_left), (2, hurt_right), (3, hurt_up)):
		liste[:] = load_animation_row(hurt_sheet, row, PLAYER_SCALE, 5, 4)
	return True

def icone_armure(tier):
	# Icone de l'offre dans la boutique : le PNG defini dans
	# settings (ARMOR_ICON_FILE_1/2) s'il existe, sinon un simple
	# cercle gris en attendant le visuel definitif.
	chemin = ARMOR_ICON_FILE_1 if tier == 1 else ARMOR_ICON_FILE_2
	if chemin and os.path.exists(chemin):
		return pygame.transform.scale(
			pygame.image.load(chemin).convert_alpha(), (40, 40))
	icone = pygame.Surface((40, 40), pygame.SRCALPHA)
	pygame.draw.circle(icone, (130, 130, 135), (20, 20), 17)
	pygame.draw.circle(icone, (90, 90, 95), (20, 20), 17, 2)
	return icone

def update_merchant_presence():
	# Appele a chaque arrivee en phase de shop : applique l'absence,
	# l'annonce d'absence et l'offre d'armure selon le niveau de jeu
	# qui vient de se terminer (current_level).
	global merchant_absent
	merchant_absent = current_level in ARMOR_ABSENCE_LEVELS
	if merchant_absent and merchant1_npc in npcs:
		npcs.remove(merchant1_npc)      # plus dessine, plus interactif
	elif not merchant_absent and merchant1_npc not in npcs:
		npcs.append(merchant1_npc)
	# Le marchand annonce l'absence a la visite D'AVANT
	merchant_1.annonce_absence = ((current_level + 1) in ARMOR_ABSENCE_LEVELS)
	# Offre : le premier tier debloque et pas encore equipe
		# Offre STRICTEMENT sequentielle : uniquement le tier suivant
	# (impossible de voir ou d'acheter le tier 2 avant le tier 1).
	offre = None
	suivant = player.equipment_level + 1
	if (suivant <= 2
			and current_level >= ARMOR_ABSENCE_LEVELS[suivant - 1] + 1):
		offre = suivant
	if offre and not merchant_absent:
		merchant_1.set_armor_offer(offre, icone_armure(offre))
	else:
		merchant_1.set_armor_offer(None, None)

def equiper_armure(tier):
	# Achete -> equipe automatiquement : apparence + stats.
	charger_animations_joueur(tier)   # no-op si les planches manquent
	player.equipment_level = tier
	ancien_max = player.max_hp
	player.recompute_max_hp()
	# Le bonus de pv est aussi ajoute aux pv actuels (comme PV max)
	player.hp = min(player.max_hp, player.hp + (player.max_hp - ancien_max))
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

# Fausse cible d'interaction pour l'autel : un "NPC" qui n'est
# ni dessine ni mis a jour ; il sert seulement de handle pour
# current_npc afin de reutiliser tout le pipeline des menus
# (overlay, croix de fermeture, greetings).
divinity_npc = NPC(
	0, 0, None, None,
	"divinity",
	movement_points=[],
)

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

# Pré-simulation de la chapelle : mêmes colliders que dans la boucle de
# jeu (murs + meubles + bancs + hitboxes croisées des PNJ), pour que les
# moines et le prêtre soient déjà en plein circuit, désynchronisés, dès
# la première entrée dans la chapelle. L'intérieur existe désormais
# (créé plus haut), l'ancien bloc commenté est remplacé par cette
# version active.
_chapel_startup_colliders = list(chapel_interior.wall_hitboxes)
_chapel_startup_colliders.extend(chapel_interior.chapel_furniture_hitboxes.values())
_chapel_startup_colliders.extend(chapel_interior.pew_hitboxes)
_chapel_startup_colliders.extend(npc.hitbox_for_players for npc in chapel_interior.chapel_npcs)

for _ in range(3000):  # ~50 secondes de circuit simulées instantanément
	for npc in chapel_interior.chapel_npcs:
		npc.update(_chapel_startup_colliders, None)

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
xp_orbs = []   # orbes d'xp lachees par les monstres
colliders = []


clock = pygame.time.Clock()

attacking = False
attack_done = False
next_attack = 1
attack_hitbox = None

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

# Especes d'arbres considerees comme "petites" : elles recoivent la hitbox
# dynamite DYNAMITE_SMALL_TREE_HITBOX. Ajoute tree2 ici si tu veux aussi les
# arbres de taille moyenne : small_tree_frames = [tree3, tree2]
small_tree_frames = [tree3]

def make_level_tree(x, y, frames, index):
	# `is` : on compare l'objet liste de frames lui-meme (identite de l'espece)
	is_small = any(frames is small for small in small_tree_frames)
	return Tree(
		x, y, frames, index=index,
		hitbox_offset_y=TREE_HITBOX_OFFSET_Y,
		dynamite_hitbox_config=DYNAMITE_SMALL_TREE_HITBOX if is_small else None
	)

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
	make_level_tree(x, y, frames, i)
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
projectiles = []
explosions = []
player.selected_slot = 0

level_obstacle_hitboxes = (
	[tree.rect for tree in level_trees]
	+ [tree.rect for tree in apple_trees]
	+ [rock.rect for rock in level_rocks]
)

# TEST : dynamites de depart, pour ne pas attendre le shop (voir settings.py)
if DEV_GIVE_DYNAMITE:
	for _ in range(5):
		player.add_item_to_inventory(Dynamite(scaled_dynamite))
coins_to_collect = 0
def enemy_obstacle(obj):
	# Arbre ou rocher : tant que le joueur est SOUS le sprite (sa hitbox
	# touche le rect complet), le monstre n'est bloqué que par le tronc /
	# la base (obj.hitbox), comme le joueur. Sinon, il doit contourner
	# tout le sprite (obj.rect).
	if player.hitbox.colliderect(obj.rect):
		return obj.hitbox
	return obj.rect 

# ---------- MENU PRINCIPAL ----------
# fond : la scene shop pre-rendue une seule fois
menu_fond = pygame.Surface(screen.get_size())
menu_fond.blit(chapel_path_layer, chapel_path_pos)
menu_fond.blit(shop_decor_layer, shop_decor_pos)
menu_fond.blit(house_base, (house_x, house_y + roof_height))
menu_fond.blit(chapel.base, (chapel.rect.x, chapel.rect.y + chapel.roof_height))
boutons_menu = ui.calculer_boutons_menu(screen)
intro_debut = pygame.time.get_ticks()

# ---------- SAUVEGARDES + MODE DEV + HITBOXES (F1) ----------
slot_sauvegarde_actif = None      # 1..10 quand on joue AVEC sauvegarde
chargement_action = ("nouveau", None)   # ou ("sauvegarde", slot)
hitboxes_config = []              # [{"type": i, "couleur": j}] max 15
hitboxes_visibles = False
# --- menu echap in-game (le jeu continue derriere, pas de freeze) ---
menu_echap_actif = False
echap_t_ouverture = 0
echap_t_fermeture = None
# --- sauvegarde memoire "sans sauvegarde" : posee a chaque nouveau
# niveau, sert au bouton REAPPARAITRE ; disparait en quittant

# --- ecran de mort ---
mort_en_cours = False
mort_debut = 0
# animation de mort du joueur : planches 4 rangees (bas, gauche,
# droite, haut) x 7 frames de 64x64, MEME pixelisation que le
# joueur (PLAYER_SCALE), une planche par niveau d'armure
# (3 en comptant celle de base) ; repli si une planche manque
DEATH_FRAME_MS = 90
mort_anims = []
for _tier in (1, 2, 3):
	_chemin = f"Swordsman_lvl{_tier}_Death_with_shadow.png"
	if os.path.exists(_chemin):
		_feuille = pygame.image.load(_chemin).convert_alpha()
		mort_anims.append({
			"down": load_animation_row(_feuille, 0, PLAYER_SCALE,
									   7, 4),
			"left": load_animation_row(_feuille, 1, PLAYER_SCALE,
									   7, 4),
			"right": load_animation_row(_feuille, 2, PLAYER_SCALE,
										7, 4),
			"up": load_animation_row(_feuille, 3, PLAYER_SCALE,
									 7, 4),
		})
	else:
		mort_anims.append(None)
_f1_precedent = False
_etat_precedent = game_state
DEFAUTS_REGLAGES = {
	"vitesse_joueur": 14, "force_joueur": 10,
	"pv_ennemis": 20, "degats_ennemis": 5, "vitesse_ennemis": 4,
	"or_depart": 150, "niveau_competences": 0, "potions_depart": 0,
	"lieu": "wave", "pommes_pct": 33, "pommes_dorees_pct": 20,
	"immortalite": False, "space_kill": True,
	"hardcore": False,
}
dev_reglages = dict(DEFAUTS_REGLAGES)
mode_dev_actif = False

def restaurer_defauts_dev():
	dev_reglages.clear()
	dev_reglages.update(DEFAUTS_REGLAGES)

def lancer_chargement(action):
	global chargement_action, game_state
	global chargement_debut, chargement_duree  
	if action[0] == "nouveau":
		# toute nouvelle partie repart d'un etat vierge
		reinitialiser_partie()
		capturer_checkpoint()
	chargement_action = action
	game_state = "chargement"
	chargement_debut = pygame.time.get_ticks()
	chargement_duree = random.randint(500, 2000)

def appliquer_reglages_dev():
	# applique les reglages du menu dev : player (vitesse, force, or,
	# competences, items), constantes monstres (module classes, qui
	# capture ses valeurs a l'import), taux de pommes (module main)
	# et lieu d'apparition
	import classes as _classes
	r = dev_reglages
	_classes.IMMORTALITE = bool(r["immortalite"])
	_classes.IMMORTALITE = bool(r["immortalite"])
	ui.MODE_HARDCORE = bool(r["hardcore"])
	global speed
	# le mouvement du joueur lit la GLOBALE speed (voir plus bas),
	# pas player.speed : les deux doivent etre mises a jour
	speed = r["vitesse_joueur"]
	player.speed = r["vitesse_joueur"]
	player.base_damage = r["force_joueur"]
	for module in (globals().get("settings"), _classes):
		if module is None:
			continue
		setattr(module, "MONSTER_BASE_HP", r["pv_ennemis"])
		setattr(module, "MONSTER_BASE_DAMAGE", r["degats_ennemis"])
		setattr(module, "MONSTER_BASE_SPEED", r["vitesse_ennemis"])
	player.coins = r["or_depart"]
	player.level = r["niveau_competences"]
	if r["potions_depart"] > 0:
		player.inventory[0] = {"item": fabriquer_item("Potion"),
							   "quantity": r["potions_depart"]}
	else:
		player.inventory[0] = {"item": None, "quantity": 0}
	globals()["DEV_START_GAME_STATE"] = r["lieu"]
	globals()["APPLE_DROP_CHANCE"] = r["pommes_pct"] / 100.0
	globals()["GOLDEN_APPLE_DROP_CHANCE"] = r["pommes_dorees_pct"] / 100.0
	points = {"chapel": chapel_interior.entrance_point,
			  "house": getattr(house, "entrance_point", None),
			  "shop": plaza_center}
	point = points.get(r["lieu"])
	if point:
		player.rect.center = (int(point[0]), int(point[1]))
		player.update_hitbox()
checkpoint_donnees = {}   # copie de l'etat du joueur a chaque nouveau niveau
def reinitialiser_partie():
	# remet l'etat du jeu a zero avant une NOUVELLE partie (dev,
	# sans sauvegarde, slot vide) : sans ca, quitter puis relancer
	# reprenait la partie precedente (ennemis, position, decor...)
	global current_level, current_wave, transition, TRANSITION_TIMER
	global portal_rect, attack_hitbox
	global level_trees, apple_trees, level_rocks
	current_level = 1
	current_wave = 1
	enemies.clear()
	coins.clear()
	xp_orbs.clear()
	item_drops.clear()
	projectiles.clear()
	explosions.clear()
	attack_hitbox = None
	player.hp = player.max_hp
	player.coins = int(dev_reglages.get("or_depart", 150)) 
	player.xp = 0
	player.xp_level = 0
	player.selected_slot = 0
	player.inventory = [{"item": None, "quantity": 0}
						for _ in range(3)]
	if mode_dev_actif and DEV_GIVE_DYNAMITE:
		for _ in range(5):
			player.add_item_to_inventory(Dynamite(scaled_dynamite))
	player.knockback_x = 0
	player.knockback_y = 0
	player.invicible_timer = 0
	player.damage_timer = 0
	lieu = DEV_START_GAME_STATE
	if lieu == "shop":
		player.rect.center = (
			plaza_center[0] - PLAYER_SHOP_SPAWN_OFFSET_X,
			plaza_center[1] + PLAYER_SHOP_SPAWN_OFFSET_Y)
		player.update_hitbox()
		portal_rect = pygame.Rect(MAP_WIDTH // 2 + PORTAL_OFFSET_X,
								  MAP_HEIGHT // 2 + PORTAL_OFFSET_Y,
								  PORTAL_SIZE, PORTAL_SIZE)
	elif lieu == "house":
		player.rect.center = (house.door_rect.centerx,
							  HOUSE_INSIDE_HEIGHT - 220)
		player.update_hitbox()
	elif lieu == "chapel":
		player.rect.center = chapel_interior.entrance_point
		player.hitbox.center = player.rect.center
		player.direction = "up"
	else:
		# vague : spawn aleatoire + decors regeneres + vague neuve
		spawn_x, spawn_y = world.random_spawn_position(
			MAP_WIDTH, MAP_HEIGHT)
		player.rect.center = (spawn_x, spawn_y)
		player.update_hitbox()
		level_tree_placements = world.generate_level_trees(
			[tree1, tree2, tree3],
			(spawn_x, spawn_y),
			MAP_WIDTH, MAP_HEIGHT,
			plaza_center, path_end, house_bounds,
			count=LEVEL_TREE_COUNT,
			min_spacing=LEVEL_TREE_MIN_SPACING,
			avoid_radius=LEVEL_TREE_AVOID_RADIUS)
		level_trees = [make_level_tree(x, y, frames, i)
					   for i, (x, y, frames)
					   in enumerate(level_tree_placements)]
		apple_tree_placements = world.generate_apple_trees(
			tree4,
			[(x, y) for x, y, _ in level_tree_placements],
			(spawn_x, spawn_y),
			MAP_WIDTH, MAP_HEIGHT,
			plaza_center, path_end, house_bounds,
			max_count=APPLE_TREE_MAX_COUNT,
			spawn_chance=APPLE_TREE_SPAWN_CHANCE)
		apple_trees = [Tree(x, y, frames,
							hitbox_offset_y=TREE_HITBOX_OFFSET_Y)
					   for x, y, frames in apple_tree_placements]
		for tree in apple_trees:
			tree.dropped_apple = False
			tree.dropped_golden_apple = False
		level_rock_placements = world.generate_level_rocks(
			rock_variants,
			[(x, y) for x, y, _ in level_tree_placements]
			+ [(x, y) for x, y, _ in apple_tree_placements],
			(spawn_x, spawn_y),
			MAP_WIDTH, MAP_HEIGHT,
			plaza_center, path_end, house_bounds,
			count=LEVEL_ROCK_COUNT,
			min_spacing=LEVEL_ROCK_MIN_SPACING)
		level_rocks = [Rock(x, y, sprite,
							hitbox_width=hitbox["width"],
							hitbox_height=hitbox["height"],
							hitbox_offset_y=ROCK_HITBOX_OFFSET_Y)
					   for x, y, sprite, hitbox
					   in level_rock_placements]
		waves.start_wave(enemies, current_level, current_wave,
						 orc_data)
	transition = True
	TRANSITION_TIMER = 120

def capturer_checkpoint():
	# copie COMPLETE de l'etat du joueur dans la sauvegarde
	# memoire, avec les memes champs que le JSON des slots (or,
	# xp, competences, armure, inventaire...) ; ne vit que le
	# temps de la partie
	checkpoint_donnees.clear()
	checkpoint_donnees.update({
		"niveau": current_level,
		"vague": current_wave,
		"or": player.coins,
		"hp": player.hp,
		"xp": player.xp,
		"xp_level": player.xp_level,
		"niveau_competences": player.level,
		"skills": dict(player.skill_levels),
		"equipement": player.equipment_level,
		"inventaire": [
			{"item": (it["item"].__class__.__name__
					  if it["item"] else None),
			 "quantite": it["quantity"]}
			for it in player.inventory
		],
		"lieu": "wave",
	})

def restaurer_checkpoint():
	# restaure l'etat complet du checkpoint (a appeler APRES la
	# purge de reinitialiser_partie) ; remet aussi l'armure en
	# apparence via les planches du niveau d'equipement
	global current_level, current_wave
	d = checkpoint_donnees
	current_level = int(d.get("niveau", 1))
	current_wave = int(d.get("vague", 1))
	player.coins = int(d.get("or", 150))
	player.xp = int(d.get("xp", 0))
	player.xp_level = int(d.get("xp_level", 0))
	player.level = int(d.get("niveau_competences", 0))
	for cle, val in d.get("skills", {}).items():
		if cle in player.skill_levels:
			player.skill_levels[cle] = int(val)
	player.equipment_level = int(d.get("equipement", 0))
	charger_animations_joueur(max(0, player.equipment_level))
	for i, sac in enumerate(d.get("inventaire", [])):
		if i >= len(player.inventory):
			break
		player.inventory[i] = {
			"item": fabriquer_item(sac.get("item")),
			"quantity": int(sac.get("quantite", 0)),
		}
	player.recompute_max_hp()
	player.hp = max(1, min(int(d.get("hp", player.max_hp)),
						   player.max_hp))

def reapparaitre():
	# bouton REAPPARAITRE de l'ecran de mort
	global game_state, transition, TRANSITION_TIMER
	if dev_reglages.get("hardcore"):
		# hardcore : on recommence TOUT (nouvelle partie complete)
		lancer_chargement(("nouveau", None))
		return
	reinitialiser_partie()      # purge du monde (ennemis, decors...)
	restaurer_checkpoint()      # l'etat COMPLET du checkpoint
	waves.start_wave(enemies, current_level, current_wave,
					 orc_data)
	game_state = "wave"
	transition = True
	TRANSITION_TIMER = 120

def fabriquer_item(nom):
	# reconstruit un item d'inventaire d'apres son nom de classe
	# (les classes d'items exigent leur sprite en argument)
	import classes as _classes
	if nom == "Potion":
		img = pygame.image.load("Fiole_de_soin.png").convert_alpha()
		return _classes.Potion(pygame.transform.scale(img, (48, 51)))
	if nom == "Dynamite":
		img = pygame.image.load("Dynamite.png").convert_alpha()
		return _classes.Dynamite(pygame.transform.scale(img, (48, 48)))
	return None

def sauvegarder_partie(slot):
	# ecrit l'etat de progression dans saves/slot_<n>.json (appele a
	# chaque entree et sortie du niveau shop)
	donnees = {
		"niveau": current_level,
		"vague": current_wave,
		"or": player.coins,
		"hp": player.hp,
		"xp": player.xp,
		"xp_level": player.xp_level,
		"niveau_competences": player.level,
		"skills": dict(player.skill_levels),
		"equipement": player.equipment_level,
		"inventaire": [
			{"item": (it["item"].__class__.__name__ if it["item"] else None),
			 "quantite": it["quantity"]}
			for it in player.inventory
		],
		"position": [player.rect.centerx, player.rect.centery],
		"lieu": game_state if game_state in ("wave", "shop", "house",
											 "chapel") else "shop",
		"date": time.strftime("%d/%m %H:%M"),
	}
	os.makedirs("saves", exist_ok=True)
	with open(os.path.join("saves", f"slot_{slot}.json"), "w",
			  encoding="utf-8") as f:
		json.dump(donnees, f, indent=2, ensure_ascii=False)

def charger_partie(slot):
	# ressssssstaure la progression d'un slot ; reprise dans le lieu sauvegarde
	global current_level, current_wave, game_state
	reinitialiser_partie()
	with open(os.path.join("saves", f"slot_{slot}.json"),
			  encoding="utf-8") as f:
		d = json.load(f)
	current_level = int(d.get("niveau", 1))
	current_wave = int(d.get("vague", 1))
	player.coins = int(d.get("or", 150))
	player.xp = int(d.get("xp", 0))
	player.xp_level = int(d.get("xp_level", 0))
	player.level = int(d.get("niveau_competences", 0))
	for cle, val in d.get("skills", {}).items():
		if cle in player.skill_levels:
			player.skill_levels[cle] = int(val)
	player.equipment_level = int(d.get("equipement", 0))
	for i, sac in enumerate(d.get("inventaire", [])):
		if i >= len(player.inventory):
			break
		nom = sac.get("item")
		player.inventory[i] = {
			"item": fabriquer_item(nom),
			"quantity": int(sac.get("quantite", 0)),
		}
	player.recompute_max_hp()
	player.hp = max(1, min(int(d.get("hp", player.max_hp)), player.max_hp))
	if d.get("position"):
		player.rect.center = (int(d["position"][0]), int(d["position"][1]))
		player.update_hitbox()
	game_state = d.get("lieu", "shop")
	if game_state == "shop":
		# reprise directe dans le shop : le portail n'existe pas encore
		# (il nait de la vague precedante), on en pose un au plaza
		global portal_rect
		portal_rect = pygame.Rect(int(plaza_center[0]) - 32,
								  int(plaza_center[1]) - 32, 64, 64)
		if game_state == "wave":
		# la purge a retire les ennemis : on remet la vague
		# du niveau sauvegarde avec les constantes actuelles
			waves.start_wave(enemies, current_level, current_wave,
						orc_data)

def cibles_hitbox(indice):
	# liste (rect monde, nom) pour le type de hitbox demande
	if indice == 0:
		return [(player.hitbox, "JOUEUR")]
	if indice == 1:
		return [(e.hitbox, f"ENNEMI {e.level}") for e in enemies]
	if indice == 2:
		return [(c.rect, "PIECE") for c in coins]
	if indice == 3:
		if game_state == "chapel":
			pnjs = chapel_interior.chapel_npcs
		elif game_state == "shop":
			pnjs = outdoor_npcs
		else:
			pnjs = npcs
		return [(n.hitbox_for_players, str(getattr(n, "type", "PNJ")).upper())
				for n in pnjs]
	if indice == 4:
		return [(o.rect, "XP") for o in xp_orbs]
	if indice == 5:
		return [(portal_rect, "PORTAIL")] if portal_rect else []
	if indice == 6:
		return [(pos, nom) for pos, nom in points_pnj_hitbox()]
	if indice == 7:
		# meubles : mobilier de la maison, mobilier + bancs de la chapelle
		if game_state == "chapel":
			out = [(r, "MEUBLE") for r in
				   chapel_interior.chapel_furniture_hitboxes.values()]
			out += [(r, "BANC") for r in chapel_interior.pew_hitboxes]
			return out
		if game_state == "house":
			return [(r, "MEUBLE")
					for r in house.furniture_hitboxes.values()]
		return []
	if indice == 8:
		# murs : maison ou chapelle selon le lieu
		if game_state == "chapel":
			return [(r, "MUR") for r in chapel_interior.wall_hitboxes]
		if game_state == "house":
			return [(house.wall_top_hitbox, "MUR"),
					(house.wall_bottom_hitbox, "MUR"),
					(house.wall_left_hitbox, "MUR"),
					(house.wall_right_hitbox, "MUR")]
		return []
	if indice == 9:
		# decors : arbres, rochers, chapelle, hitboxes dynamite
		if game_state == "shop":
			out = [(t.hitbox, f"ARBRE {t.index}") for t in town_trees]
			out += [(r.hitbox, f"ROCHER {r.index}") for r in town_rocks]
			out += [(chapel.hitbox, "CHAPELLE")]
			return out
		if game_state == "wave":
			out = [(t.hitbox, "ARBRE") for t in level_trees]
			out += [(t.hitbox, "POMMIER") for t in apple_trees]
			out += [(r.hitbox, "ROCHER") for r in level_rocks]
			out += [(t.dynamite_hitbox, "DYNAMITE")
					for t in level_trees + apple_trees
					if t.dynamite_hitbox]
			out += [(r.dynamite_hitbox, "DYNAMITE")
					for r in level_rocks if r.dynamite_hitbox]
			return out
		return []
	if indice == 10:
		# projectiles du joueur et des ennemis + coup d'attaque
		out = [(p.hitbox, "PROJ") for p in projectiles]
		if attack_hitbox and attacking:
			out.append((attack_hitbox, "ATTAQUE"))
		return out
	return []

def points_pnj_hitbox():
	# points de deplacement des pnj : (position monde, nom)
	if game_state == "chapel":
		pnjs = chapel_interior.chapel_npcs
	elif game_state == "shop":
		pnjs = outdoor_npcs
	else:
		pnjs = npcs
	out = []
	for n in pnjs:
		for i, point in enumerate(n.movement_points):
			arret = i in n.stop_point_indices
			out.append((point, f"{getattr(n, 'type', 'PNJ')} #{i}"
						+ (" ARRET" if arret else "")))
	return out

def dessiner_hitboxes(offset_x, offset_y):
	# dessine les hitboxes configurees dans le menu dev, avec
	# l'offset monde -> ecran (camera negative, ou position de
	# l'interieur centre pour la maison)
	for entree in hitboxes_config:
		couleur = ui.HITBOX_COULEURS[entree["couleur"]]
		if entree["type"] == 6:
			# points de deplacement des pnj : ronds
			for pos, nom in points_pnj_hitbox():
				cx = int(pos[0] + offset_x)
				cy = int(pos[1] + offset_y)
				pygame.draw.circle(screen, couleur, (cx, cy), 5)
				ui._draw_hp_text(screen, nom, cx, cy - 16,
								 echelle=1, centered=True)
			continue
		for rect_monde, nom in cibles_hitbox(entree["type"]):
			ecran_r = rect_monde.move(int(offset_x), int(offset_y))
			pygame.draw.rect(screen, couleur, ecran_r, 2)
			ui._draw_hp_text(screen, nom, ecran_r.centerx,
							 ecran_r.top - 9, echelle=1,
							 centered=True)



run = True
while run == True :
	if game_state == "intro":
		# intro studio : fondu SAUCISSON STUDIOS puis reveal du menu
		# (un clic passe directement au menu)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				intro_debut = pygame.time.get_ticks() - 10 ** 9
		if ui.draw_intro(screen, pygame.time.get_ticks() - intro_debut,
						 boutons_menu, menu_fond):
			game_state = "menu"
			intro_debut = pygame.time.get_ticks()
		pygame.display.update()
		clock.tick(FPS_MAX)
		continue

	if game_state == "menu":
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
				for rect, action in boutons_menu:
					if rect.collidepoint(event.pos):
						if action == "jouer":
							game_state = "menu_jouer"
						elif action == "quitter":
							run = False
		ui.draw_menu(screen, boutons_menu, menu_fond)
		pygame.display.update()
		clock.tick(FPS_MAX) 
		continue
	if game_state == "chargement":
		# ecran de chargement : duree aleatoire 0.5 a 2 s posee par le 
		# clic sur JOUER, puis la partie demarre
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
		ui.draw_chargement(screen,
						   pygame.time.get_ticks() - chargement_debut,
						   chargement_duree)
		if pygame.time.get_ticks() - chargement_debut >= chargement_duree:
			if chargement_action[0] == "sauvegarde":
				charger_partie(chargement_action[1])
			elif chargement_action[0] == "menu":
				game_state = "menu"
				ui.MODE_HARDCORE = False
			else:
				game_state = DEV_START_GAME_STATE
		pygame.display.update()
		clock.tick(FPS_MAX)
		continue
	if game_state == "mort":
		# ecran de mort : fondu noir, VOUS ETES MORT, 2 boutons
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				for rect, action in ui.calculer_menu_mort(screen):
					if action and rect.collidepoint(event.pos):
						if action == "reapparaitre":
							mort_en_cours = False
							reapparaitre()
						elif action == "quitter":
							mort_en_cours = False
							lancer_chargement(("menu", None))
						break
		ui.draw_menu_mort(screen, mort_debut, current_level,
						  current_wave)
		pygame.display.update()
		clock.tick(FPS_MAX)
		continue
	if game_state in ("menu_jouer", "menu_sauvegardes", "menu_dev",
					  "menu_hitboxes", "menu_settings","menu_hardcore"):
		# sous-menus : ni monde ni entites, juste les clics
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if game_state == "menu_hardcore":
					rect_barre, rect_jouer, rect_quitter = \
						ui.calculer_menu_hardcore(screen)
					if rect_barre.collidepoint(event.pos):
						rm, rp = ui._zone_plus_moins(
							rect_barre, "hardcore",
							dev_reglages["hardcore"])
						if rm.collidepoint(event.pos) or \
								rp.collidepoint(event.pos):
							dev_reglages["hardcore"] = \
								not dev_reglages["hardcore"]
					elif rect_jouer.collidepoint(event.pos):
						appliquer_reglages_dev()
						lancer_chargement(("nouveau", None))
					elif rect_quitter.collidepoint(event.pos):
						game_state = "menu_jouer"
				if game_state == "menu_jouer":
					for rect, action in ui.calculer_menu_jouer(screen):
						if rect.collidepoint(event.pos):
							if action == "sauvegarde":
								game_state = "menu_sauvegardes"
								mode_dev_actif = False
							elif action == "sans":
								restaurer_defauts_dev()
								slot_sauvegarde_actif = None
								# mini-menu : choix hardcore off/on
								game_state = "menu_hardcore"
								mode_dev_actif = False
							elif action == "dev":
								mode_dev_actif = True
								game_state = "menu_dev"
							elif action == "retour":
								game_state = "menu"
							break
				elif game_state == "menu_sauvegardes":
					for rect, action in ui.calculer_menu_sauvegardes(screen):
						if rect.collidepoint(event.pos):
							if action[0] == "retour":
								game_state = "menu_jouer"
							else:
								slot_sauvegarde_actif = action[1]
								restaurer_defauts_dev()
								appliquer_reglages_dev()
								existant = os.path.exists(os.path.join(
									"saves", f"slot_{action[1]}.json"))
								if existant:
									lancer_chargement(
										("sauvegarde", action[1]))
								else:
									lancer_chargement(("nouveau", None))
							break
				elif game_state == "menu_dev":
					for rect, action in ui.calculer_menu_dev(screen):
						if rect.collidepoint(event.pos):
							if action == "hitboxes":
								game_state = "menu_hitboxes"
							elif action == "settings":
								game_state = "menu_settings"
							elif action == "jouer":
								appliquer_reglages_dev()
								slot_sauvegarde_actif = None
								lancer_chargement(("nouveau", None))
							elif action == "retour":
								game_state = "menu_jouer"
							break
				elif game_state == "menu_hitboxes":
					lignes, rect_ajouter, rect_enlever, rect_retour = \
						ui.calculer_menu_hitboxes(screen, hitboxes_config)
					for rect, i in lignes:
						if rect.collidepoint(event.pos):
							pastille = ui.rect_pastille_hitbox(rect)
							if pastille.collidepoint(event.pos):
								e = hitboxes_config[i]
								e["couleur"] = ((e["couleur"] + 1)
									% len(ui.HITBOX_COULEURS))
							else:
								e = hitboxes_config[i]
								e["type"] = ((e["type"] + 1)
									% len(ui.HITBOX_TYPES))
							break
					else:
						if rect_ajouter.collidepoint(event.pos):
							if len(hitboxes_config) < 15:
								hitboxes_config.append({"type": 0,
														"couleur": 0})
						elif rect_enlever.collidepoint(event.pos):
							if hitboxes_config:
								hitboxes_config.pop()
						elif rect_retour.collidepoint(event.pos):
							game_state = "menu_dev"
				elif game_state == "menu_settings":
					lignes, rect_retour = \
						ui.calculer_menu_settings(screen)
					for rect, cle in lignes:
						if not rect.collidepoint(event.pos):
							continue
						definition = next(
							d for d in ui.SETTINGS_LIGNES if d[0] == cle)
						_cle, _label, pas, mini, maxi, genre = definition
						rm, rp = ui._zone_plus_moins(
							rect, cle, dev_reglages[cle])
						if genre == "cycle":
							i = ui.LIEUX.index(dev_reglages[cle])
							if rm.collidepoint(event.pos):
								i = (i - 1) % len(ui.LIEUX)
							elif rp.collidepoint(event.pos):
								i = (i + 1) % len(ui.LIEUX)
							dev_reglages[cle] = ui.LIEUX[i]
						elif genre == "onoff":
							dev_reglages[cle] = not dev_reglages[cle]
						elif rm.collidepoint(event.pos):
							dev_reglages[cle] = max(mini,
								dev_reglages[cle] - pas)
						elif rp.collidepoint(event.pos):
							dev_reglages[cle] = min(maxi,
								dev_reglages[cle] + pas)
						break
					else:
						if rect_retour.collidepoint(event.pos):
							game_state = "menu_dev"
		if game_state == "menu_jouer":
			ui.draw_menu_jouer(screen, ui.calculer_menu_jouer(screen),
							   menu_fond)
		elif game_state == "menu_sauvegardes":
			ui.draw_menu_sauvegardes(screen,
									 ui.calculer_menu_sauvegardes(screen),
									 menu_fond)
		elif game_state == "menu_hardcore":
			ui.draw_menu_hardcore(screen, menu_fond, dev_reglages)
		elif game_state == "menu_dev":
			ui.draw_menu_dev(screen, ui.calculer_menu_dev(screen),
							 menu_fond)
		elif game_state == "menu_hitboxes":
			ui.draw_menu_hitboxes(screen, menu_fond, hitboxes_config)
		elif game_state == "menu_settings":
			ui.draw_menu_settings(screen, menu_fond, dev_reglages) 
		pygame.display.update()
		clock.tick(FPS_MAX)
		continue
		# --- sauvegarde automatique a l'entree et a la sortie du shop ---
	if game_state != _etat_precedent:
		if slot_sauvegarde_actif is not None and \
				"shop" in (game_state, _etat_precedent):
			sauvegarder_partie(slot_sauvegarde_actif)
	_etat_precedent = game_state

	# --- F1 : afficher/masquer les hitboxes de debug configurees ---
	_f1 = pygame.key.get_pressed()[pygame.K_F1]
	if _f1 and not _f1_precedent:
		hitboxes_visibles = not hitboxes_visibles
	_f1_precedent = _f1

	colliders.clear()
	colliders.clear()
	if game_state == "house":
		screen.fill((0, 0, 0))
		house.interior_surface = house.draw_interior()
	elif game_state == "chapel":
		screen.fill((0, 0, 0))
		chapel_interior.interior_surface.blit(chapel_interior.static_surface, (0, 0))
		
		chapel_interior.interior_surface.blit(
			chapel_interior.candelabra_frames[chapel_interior.candelabra_frame],
			chapel_interior.candelabra_rect1
		)
		chapel_interior.interior_surface.blit(
			chapel_interior.candelabra_frames[chapel_interior.candelabra_frame],
			chapel_interior.candelabra_rect2	
		)
		
	player.apply_knockback()
	
	player_system.update_hurt(player, hurt_up, hurt_down, hurt_left, hurt_right)

	old_pos = player.rect.copy()
	if not attacking and player.state != "hurt" and current_npc is None and awaiting_npc_arrival is None:
		moving = player_system.movement(player, speed, walk_up, walk_down, walk_left, walk_right)

		if game_state == "chapel":
			interactable_npcs = [chapel_interior.monk_desk_npc]
		else:
			interactable_npcs = npcs

		near_npc = npc_system.get_interactable_npc(player, interactable_npcs)

		# Le NPC est arrivé face au joueur : on ouvre le dialogue seulement
	# une fois le petit délai d'orientation écoulé. Générique, s'applique
	# quel que soit le game_state (house, chapel...).
	if (awaiting_npc_arrival is not None
			and awaiting_npc_arrival.state == "talking"
			and awaiting_npc_arrival.talk_delay_timer <= 0):
		current_npc = awaiting_npc_arrival
		awaiting_npc_arrival = None
		dialogues.reset()
		healer_state = "main"
		merchant_state = "main"
		librarian_state = "main"

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
				merchant_1_text = random.choice(merchant_1.merchant_1_dialogues["annonce" if merchant_1.annonce_absence else "normal"])
				dialogues.start_dialogue(merchant_1_text)

		elif current_npc.type == "monk_desk":
			if player.coins < 1:
				librarian_text = random.choice(librarian.librarian_dialogues["not_enough_gold"])
				dialogues.start_dialogue(librarian_text)
			elif not player.met_librarian:
				librarian_text = random.choice(librarian.librarian_dialogues["first_meeting"])
				dialogues.start_dialogue(librarian_text)
				player.met_librarian = True
			else:
				librarian_text = random.choice(librarian.librarian_dialogues["normal"])
				dialogues.start_dialogue(librarian_text)

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
	elif game_state == "chapel":
		player.clamp_to_map(chapel_interior.width, chapel_interior.height)
		chapel_interior.update_altar()
		chapel_interior.update_statues()
		chapel_interior.update_parishioners()
		chapel_interior.update_candelabra()
		
		
	else:
		player.clamp_to_map(MAP_WIDTH, MAP_HEIGHT)

	if game_state == "house":
		camera_x = 0
		camera_y = 0
	elif game_state == "chapel":
		camera_x, camera_y = world.compute_camera(
			player, chapel_interior.width, chapel_interior.height,
			screen.get_width(), screen.get_height()
		)
	else:
		camera_x, camera_y = world.compute_camera(
			player, MAP_WIDTH, MAP_HEIGHT, screen.get_width(), screen.get_height()
		)

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

	if game_state == "chapel":
		colliders.extend(chapel_interior.wall_hitboxes)
		colliders.extend(chapel_interior.chapel_furniture_hitboxes.values())
		colliders.extend(chapel_interior.pew_hitboxes)
		colliders.extend(npc.hitbox_for_players for npc in chapel_interior.chapel_npcs)

		for npc in chapel_interior.chapel_npcs:
			npc.update(colliders, None)

	collision.resolve_player_collisions(player, colliders, old_pos)

	player.update_hitbox()

	player_system.idle(player, moving, attacking, idle_up, idle_down, idle_left, idle_right)


	attacking, next_attack = player_system.animate(player, moving, attacking, next_attack)

	audio.set_listener(player.rect.center)
	audio.footsteps(
		moving and not attacking and player.state != "hurt"
		and current_npc is None and awaiting_npc_arrival is None,
		game_state
	)
	
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
		dragon_timer, dragon_frame, dragon_waiting, dragon_waiting_timer = world.update_dragon(
	game_state,
	dragon_timer,
	dragon_frame,
	DRAGON_ANIMATION_SPEED,
	chapel_dragon_animation,
	dragon_waiting,
	dragon_waiting_timer
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
	
		# Mise a jour des projectiles (dynamites) et des explosions
		# Mise a jour des projectiles (dynamites) et des explosions
	# Obstacles DE LA DYNAMITE : hitbox au niveau du sol (souche/tronc),
	# differentes de `colliders` (celles-ci sont decalees pour le joueur).
	if projectiles and game_state == "wave":
		dynamite_colliders = (
			[tree.dynamite_hitbox for tree in level_trees]
			+ [tree.dynamite_hitbox for tree in apple_trees]
			+ [rock.dynamite_hitbox for rock in level_rocks]
		)
	else:
		dynamite_colliders = []

	for projectile in projectiles[:]:
		if projectile.update(dynamite_colliders, enemies):
			continue

		# La meche est finie : BOUM
		projectiles.remove(projectile)
		explosion = Explosion(projectile.x, projectile.y, DYNAMITE_EXPLOSION_RADIUS, DYNAMITE_DAMAGE)
		explosions.append(explosion)
		audio.play("explosion", source=(projectile.x, projectile.y))

		# 1) Degats aux monstres dans le rayon (l'explosion sert de source
		#    pour le recul : ils sont repousses depuis son centre)
		for enemy in enemies:
			if enemy.dead:
				continue
			distance = math.hypot(enemy.rect.centerx - explosion.x, enemy.rect.centery - explosion.y)
			if distance <= explosion.radius:
				enemy.take_damage(explosion.damage, explosion)

		# 2) Degats au joueur (souffle), reduits par DYNAMITE_PLAYER_DAMAGE_RATIO
		if game_state == "wave" and DYNAMITE_PLAYER_DAMAGE_RATIO > 0:
			distance = math.hypot(player.rect.centerx - explosion.x, player.rect.centery - explosion.y)
			if distance <= explosion.radius:
				player.take_damage(int(explosion.damage * DYNAMITE_PLAYER_DAMAGE_RATIO), explosion)

		# 3) Pommiers secoues par le souffle : chance de faire tomber une pomme
		if game_state == "wave":
			for tree in apple_trees:
				distance = math.hypot(tree.rect.centerx - explosion.x, tree.rect.centery - explosion.y)
				if distance > explosion.radius:
					continue
				if random.random() < APPLE_DROP_CHANCE + DYNAMITE_TREE_HIT_APPLE_BOOST:
					if not tree.dropped_golden_apple and random.random() < GOLDEN_APPLE_DROP_CHANCE:
						item_drops.append(ItemDrop(
							tree.rect.centerx, tree.rect.bottom - 10, GoldenApple(golden_apple_sprite),
							fall_height=ITEM_DROP_FALL_HEIGHT, fall_duration=ITEM_DROP_FALL_DURATION
						))
						tree.dropped_golden_apple = True
					elif not tree.dropped_apple:
						item_drops.append(ItemDrop(
							tree.rect.centerx, tree.rect.bottom - 10, Apple(apple_sprite),
							fall_height=ITEM_DROP_FALL_HEIGHT, fall_duration=ITEM_DROP_FALL_DURATION
						))
						tree.dropped_apple = True

	for explosion in explosions[:]:
		if not explosion.update():
			explosions.remove(explosion) 

	for coin in coins[:]:
		if player.hitbox.colliderect(coin.rect):
			player.coins += coin.value
			audio.play("coin")
			coins.remove(coin)

	if game_state == "wave":
		for drop in item_drops[:]:
			drop.update(player)
			if player.hitbox.colliderect(drop.rect):
				if player.add_item_to_inventory(drop.item):
					audio.play("item_pickup")
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
	if game_state == "chapel":
		entities.append((
			"chapel_npc",
			chapel_interior.monk_desk_npc,
			chapel_interior.monk_desk_npc.rect.bottom
		))
	if game_state == "chapel":
		for name, (sprite, rect) in chapel_interior.chapel_furniture.items():
			offset = chapel_interior.chapel_furniture_sort_offset.get(name, 0)
			entities.append(("chapel_furniture", (sprite, rect), rect.bottom + offset))
		altar_sprite = chapel_interior.altar_frames[chapel_interior.altar_frame]
		entities.append((
			"chapel_altar",
			(altar_sprite, chapel_interior.altar_rect),
			chapel_interior.altar_rect.bottom
		))
		entities.append((
			"chapel_npc",
			chapel_interior.priest_npc,
			chapel_interior.priest_npc.rect.bottom
		))

		angel_sprite = chapel_interior.angel_frames[chapel_interior.statue_frame]
		for x, y in chapel_interior.statue_positions:
			rect = angel_sprite.get_rect(midbottom=(x, y))
			entities.append(("chapel_statue", (angel_sprite, rect), rect.bottom))

		dragon_sprite = chapel_interior.dragon_frames[chapel_interior.statue_frame]
		for x, y in chapel_interior.dragon_positions:
			rect = dragon_sprite.get_rect(midbottom=(x, y))
			entities.append(("chapel_statue", (dragon_sprite, rect), rect.bottom))

		for pew_sprite, pew_rect, occupants in chapel_interior.pew_units:
			entities.append(("chapel_pew", (pew_sprite, pew_rect, occupants), pew_rect.bottom))

		for npc in chapel_interior.chapel_npcs:
			entities.append(("chapel_npc", npc, npc.rect.bottom))

	
			
	if game_state == "shop":
		if player.hitbox.colliderect(portal_rect):
			game_state = "wave"
			audio.play("portal")
			current_level, current_wave, transition, TRANSITION_TIMER = world.start_new_level(enemies, current_level, orc_data)
						# sauvegarde memoire du nouveau niveau (checkpoint
			# du bouton REAPPARAITRE, mode sans sauvegarde)
			capturer_checkpoint()

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
				make_level_tree(x, y, frames, i)
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
			[enemy_obstacle(tree) for tree in level_trees]
			+ [enemy_obstacle(tree) for tree in apple_trees]
			+ [enemy_obstacle(rock) for rock in level_rocks]
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
			# L'xp lachee depend du niveau du monstre (10 + 2 x niveau)
			xp_orbs.append(XpOrb(enemy.rect.centerx, enemy.rect.centery,
				MONSTER_BASE_XP + MONSTER_XP_PER_LEVEL * enemy.level))
			enemies.remove(enemy)
	if game_state == "wave" and len(enemies) == 0:
		coins_to_collect = min(5, len(coins))
		for coin in coins[:coins_to_collect]:
			coin.auto_collect = True

		# --- Nettoyage des pièces immobiles ---
		# À faire AVANT la téléportation du joueur vers le shop :
		# les distances sont calculées depuis sa position actuelle.
		for coin in coins[:]:
			if coin.auto_collect:
				continue  # déjà en route vers le joueur
			dx = player.rect.centerx - coin.rect.centerx
			dy = player.rect.centery - coin.rect.centery
			if math.hypot(dx, dy) < COIN_MAGNET_RADIUS:
				coin.auto_collect = True  # elle bougerait de toute façon : on la garde
			else:
				coins.remove(coin)  # immobile : elle disparaît

		if current_wave < 3:
			current_wave += 1
			waves.start_wave(enemies, current_level, current_wave, orc_data)
			audio.play("wave_start")
			transition = True
			TRANSITION_TIMER = 120
		else:
			merchant_1.refresh_shop()
			audio.play("wave_clear")
			update_merchant_presence()
			projectiles.clear()
			explosions.clear()
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

	

		# L'xp restante en vol est creditee directement (jamais perdue)
		for orb in xp_orbs[:]:
			
			player.gain_xp(orb.value)
			
			xp_orbs.remove(orb)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		
		if event.type == pygame.KEYDOWN:
			
			# Cheat: press SPACE to kill all enemies on the map
			if event.key == pygame.K_SPACE:
				# cheat SPACE KILL : activable/coupable dans REGLAGES
				if mode_dev_actif and dev_reglages.get("space_kill"):

					for e in enemies:
						# deal lethal damage using the player as source so death logic runs
						e.take_damage(e.hp, player)
			if event.key == pygame.K_ESCAPE and current_npc is None:
				# menu echap in-game : le jeu continue derriere
				if menu_echap_actif:
					menu_echap_actif = False
					echap_t_fermeture = pygame.time.get_ticks()
				else:
					menu_echap_actif = True
					echap_t_ouverture = pygame.time.get_ticks()
					echap_t_fermeture = None
			elif event.key == pygame.K_m:
				audio.toggle_mute()

		if event.type == pygame.MOUSEWHEEL:

			player.selected_slot = (
			player.selected_slot - event.y
			) % len(player.inventory)

		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				if menu_echap_actif:
					# clics sur le panneau echap : geres ici,
					# jamais transformes en attaque
					if ui.rect_panneau_echap(screen).collidepoint(event.pos):
						for rect, action in ui.calculer_menu_echap(screen):
							if action and rect.collidepoint(event.pos):
								if action == "continuer":
									menu_echap_actif = False
									echap_t_fermeture = pygame.time.get_ticks()
								elif action == "quitter":
									menu_echap_actif = False
									echap_t_fermeture = None
									current_npc = None
									lancer_chargement(("menu", None))
								break
						continue
				# Check if close button clicked on NPC UI

			
				if current_npc:
					audio.play("ui_click")

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
							librarian_state = "main"

					# Boutons de confirmation
						elif healer_state in ("confirm", "heal_confirm"):
							if missing_hp>0:
								if confirm_rect.collidepoint(event.pos):
									heal_price = heal_offer["price"]
									heal_final = heal_offer["heal_amount"]
									if player.hp < player.max_hp and heal_final > 0:
										heal_timer = HEAL_ANIMATION_DURATION
										audio.play("heal")
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

					elif current_npc and current_npc.type == "monk_desk":

						if librarian_state == "main":
							if librarian_pay_rect and librarian_pay_rect.collidepoint(event.pos):
								if player.coins >= 1:
									librarian_buy_animation_start_coins = player.coins
									librarian_buy_animation_target_coins = player.coins - 1
									librarian_coin_timer = BUY_COIN_ANIMATION_DURATION
									audio.play("buy")
									librarian_state = "books"
									dialogues.reset()
							elif librarian_retour_rect and librarian_retour_rect.collidepoint(event.pos):
								current_npc.end_conversation()
								current_npc = None
								close_rect = None
								librarian_state = "main"

						elif librarian_state == "books":
							clicked_book = False
							for i, rect in enumerate(librarian_book_rects):
								if rect.collidepoint(event.pos):
									current_librarian_book = i
									current_librarian_page = 0
									librarian_state = "reading"
									clicked_book = True
									break
							if not clicked_book and librarian_quit_rect and librarian_quit_rect.collidepoint(event.pos):
								librarian_state = "goodbye"
								goodbye_timer = pygame.time.get_ticks()
								librarian_text = random.choice(librarian.librarian_dialogues["goodbye"])
								dialogues.start_dialogue(librarian_text)

						elif librarian_state == "reading":
							if librarian_back_rect and librarian_back_rect.collidepoint(event.pos):
								librarian_state = "books"
							elif librarian_left_arrow_rect and librarian_left_arrow_rect.collidepoint(event.pos):
								if current_librarian_page > 0:
									current_librarian_page -= 1
									audio.play("page_turn")
							elif librarian_right_arrow_rect and librarian_right_arrow_rect.collidepoint(event.pos):
								book = librarian.librarian_books[current_librarian_book]
								if current_librarian_page < len(book.pages) - 1:
									current_librarian_page += 1
									audio.play("page_turn")

					elif current_npc and current_npc.type == "divinity":

						if divinity_state == "main":
							if divinity_quit_rect and divinity_quit_rect.collidepoint(event.pos):
								divinity_state = "goodbye"
								goodbye_timer = pygame.time.get_ticks()
								divinity_text = random.choice(divinity.divinity_dialogues["goodbye"])
								dialogues.start_dialogue(divinity_text)
							elif divinity_left_arrow_rect and divinity_left_arrow_rect.collidepoint(event.pos):
								if divinity_page > 0:
									divinity_page -= 1
							elif divinity_right_arrow_rect and divinity_right_arrow_rect.collidepoint(event.pos):
								if divinity_page < divinity.divinity_max_pages - 1:
									divinity_page += 1
							else:
								for i, rect in enumerate(divinity_skill_rects):
									if rect.collidepoint(event.pos):
										# Achat de la competence cliquee (si les
										# moyens sont la) : stats appliquees
										# immediatement, puis effet spell
										# au-dessus de l'autel et banniere.
										skill = divinity.divinity_skills[
											divinity_page
											* divinity.SKILLS_PER_PAGE + i]
										# --- DEBUG (a retirer quand ça marche) ---
										print(f"[DIVINITE] clic {skill['key']} | "
											f"cout {skill['cost_kind']}:{skill['cost_value']} | "
											f"xp_level={player.xp_level} xp_barre={player.xp} | "
											f"moyens={divinity.can_afford(player, skill)} | "
											f"etat={divinity_state}")
										# -----------------------------------------
										if (divinity_purchase is None
												and divinity.can_afford(player, skill)):
											result = divinity.purchase(player, skill)
											if result:
												old_level, _new_level = result
												divinity_state = "purchase"
												audio.play("skill_buy")
												priest = chapel_interior.priest_npc
												if (priest.messe_active
														and priest.messe_phase == "effect"):
													divinity_purchase = {"skill": skill, "old_level": old_level, "phase": "wait_spell", "timer": 0}
												else:
													divinity_purchase = {"skill": skill, "old_level": old_level, "phase": "spell", "timer": len(chapel_interior.priest_spell_effect_anim) * SKILL_SPELL_FRAME_TIME}
										elif divinity_purchase is None:
											# Refus (pas assez de niveaux d'xp) : on ne
											# laisse jamais un clic etre mort, le menu
											# affiche la raison comme un dialogue.
											dialogues.reset()
											divinity_text = "Pas assez de niveaux d'XP pour cette competence..."
											audio.play("ui_error")
											dialogues.start_dialogue(divinity_text)
											break 
					
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

								merchant_1_text = random.choice(merchant_1.merchant_1_dialogues["annonce" if merchant_1.annonce_absence else "normal"])
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
										if isinstance(item, ArmorOffer):
											# Achat d'armure : equipement automatique,
											# dans l'ordre (tier 2 refuse sans le tier 1)
											if item.tier != player.equipment_level + 1:
												merchant_1.set_click_text("Achetez d'abord l'armure precedente.")
											elif player.coins >= item.price:
												buy_animation_start_coins = player.coins
												buy_animation_target_coins = player.coins - item.price
												merchant_coin_timer = BUY_COIN_ANIMATION_DURATION
												equiper_armure(item.tier)
												audio.play("buy")
												merchant_1.merchant_inventory.remove(item)
												merchant_1.set_click_text(f"Tu équipes {item.name} !")
											else:
												merchant_1.set_click_text("Vous n'avez pas assez d'or.")
										elif item.stock <= 0:
											merchant_1.set_click_text(
											"Rupture de stock."
										)
											audio.play("ui_error")
										elif player.coins < item.price:
											merchant_1.set_click_text(
											"Vous n'avez pas assez d'or."
										)
											audio.play("ui_error")
										else:
											if player.add_item_to_inventory(item):

												item.stock -= 1
												merchant_1.set_click_text(
												f"Vous achetez {item.name}.")
												audio.play("buy")
											
												merchant_coin_timer = BUY_COIN_ANIMATION_DURATION
												buy_animation_start_coins = player.coins
												buy_animation_target_coins = player.coins - item.price

											else:
												merchant_1.set_click_text(
												   "Votre inventaire est plein."
											)
												audio.play("ui_error")
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
				print(f"Clic droit détecté ! game_state={game_state}, attacking={attacking}, player.state={player.state}, current_npc={current_npc}")
				if not attacking and player.state != "hurt" and current_npc is None:
					slot = player.inventory[player.selected_slot]
					item = slot["item"]
					print(f"Slot sélectionné: {player.selected_slot}, item: {item}, quantity: {slot['quantity']}")

					if item is not None:
						print(f"Item type: {type(item).__name__}, isinstance(Dynamite): {isinstance(item, Dynamite)}")
						if isinstance(item, Potion) and potion_heal_timer == 0:
							potion_heal_animation_start_hp = player.hp
							potion_heal_animation_target_hp = min(player.max_hp, player.hp + item.heal)
							potion_heal_timer = POTION_ANIMATION_DURATION
							audio.play("potion")

							slot["quantity"] -= 1
							if slot["quantity"] <= 0:
								slot["item"] = None
								slot["quantity"] = 0

						elif isinstance(item, (Apple, GoldenApple)):
							item.use(player)
							audio.play("eat")
							slot["quantity"] -= 1
							if slot["quantity"] <= 0:
								slot["item"] = None
								slot["quantity"] = 0
						
						elif isinstance(item, Dynamite):
							# Lancer la dynamite vers la souris
							if game_state in ["wave", "world"]:
								mx, my = pygame.mouse.get_pos()
								# Convertir les coordonnées écran en coordonnées monde
								world_mx = mx + camera_x
								world_my = my + camera_y
								
								item.use(player, world_mx, world_my, projectiles, scaled_dynamite)
								audio.play("dynamite_throw")
								
								slot["quantity"] -= 1
								if slot["quantity"] <= 0:
									slot["item"] = None
									slot["quantity"] = 0
							else:
								merchant_1.set_click_text("Vous ne pouvez lancer la dynamite que dans le monde.")

		if event.type == pygame.KEYDOWN: 

			if event.key == pygame.K_e:
				if current_npc and divinity_purchase is None:
					
					if not dialogues.dialogue_finished:
						dialogues.skip_dialogue()
					else:
					# Close NPC interaction if already open
						current_npc = None
						close_rect = None
						healer_state = "main"
						merchant_state = "main"
						divinity_state = "main"
						heal_offer = None
				elif near_npc and awaiting_npc_arrival is None:
					# On ne lance plus le dialogue tout de suite : le NPC
					# doit d'abord venir se placer face au joueur.
					near_npc.begin_conversation(player)
					awaiting_npc_arrival = near_npc
				else: 
					if (game_state == "chapel"
							and divinity_purchase is None
							and player.hitbox.colliderect(chapel_interior.altar_interaction_rect)):
						# Interaction avec l'autel : ouverture directe
						# du menu de la divinite (pas d'approche, l'autel
						# ne se deplace pas). Le titre affiche
						# "DIVINITE" et non un nom de PNJ.
						current_npc = divinity_npc
						divinity_state = "main"
						divinity_page = 0
						dialogues.reset()
						divinity_text = random.choice(divinity.divinity_dialogues["greetings"])
						dialogues.start_dialogue(divinity_text)
					if game_state == "shop":

						if player.hitbox.colliderect(house.door_hitbox):

							game_state = "house"
							audio.play("door")
							player.rect.center = (
							house.door_rect.centerx,
							HOUSE_INSIDE_HEIGHT - 220
							)			
							player.hitbox.center = player.rect.center
							player.direction = "up"

						elif player.hitbox.colliderect(chapel.door_hitbox):

							game_state = "chapel"
							audio.play("door")
							player.rect.center = chapel_interior.entrance_point
							player.hitbox.center = player.rect.center
							player.direction = "up"
							chapel_interior.reset_seating()

					elif game_state == "house":

						if player.hitbox.colliderect(house.door_rect):

							game_state = "shop"
							audio.play("door")
							player.rect.center = (
							house.door_hitbox.centerx,
							house.door_hitbox.bottom + 40
					)
							player.hitbox.center = player.rect.center
							player.direction = "down"

					elif game_state == "chapel":

						if player.hitbox.colliderect(chapel_interior.exit_rect):

							game_state = "shop"
							audio.play("door")
							player.rect.center = (
							chapel.door_hitbox.centerx,
							chapel.door_hitbox.bottom + 40
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
		

	for coin in coins[:]:

		if coin.auto_collect:
			coin.move_auto(player)
		else:
			coin.move_towards_player(player)

		coin.update()

		if player.hitbox.colliderect(coin.rect):
			if player.hitbox.colliderect(coin.rect):
				player.coins += coin.value
				audio.play("coin")
				coins.remove(coin)

		coin.draw(game_surface)

	for orb in xp_orbs[:]:
		orb.update(player)
		if player.hitbox.colliderect(orb.rect):
			player.gain_xp(orb.value)
			audio.play("xp_orb")
			xp_orbs.remove(orb)
		orb.draw(game_surface)
	
	
	# Dessiner les dynamites (coordonnees MONDE, sur game_surface)
	for projectile in projectiles:
		projectile.draw(game_surface)


	entities.sort(key=lambda entity: entity[2])

	for entity_type, entity, sort_y in entities:
		if entity_type == "player":
			if mort_en_cours:
				# l'animation de mort est dessinee a part :
				# le sprite debout ne s'affiche plus
				pass
			if game_state == "house":
				player_system.draw_player(house.interior_surface, player, hurt_up, hurt_down, hurt_left, hurt_right)
			elif game_state == "chapel":
				player_system.draw_player(chapel_interior.interior_surface, player, hurt_up, hurt_down, hurt_left, hurt_right)
				if divinity_purchase and divinity_purchase["phase"] == "spell":
					# Effet de sortilege de l'achat, au-dessus de l'autel
					# (meme rendu que l'effet de messe, sans lien avec elle)
					fx_anim = chapel_interior.priest_spell_effect_anim
					if fx_anim:
						elapsed = len(fx_anim) * SKILL_SPELL_FRAME_TIME - divinity_purchase["timer"]
						fx_index = max(0, min(len(fx_anim) - 1, elapsed // SKILL_SPELL_FRAME_TIME))
						fx = fx_anim[fx_index]
						fx_rect = fx.get_rect(midbottom=(
							chapel_interior.altar_rect.centerx,
							chapel_interior.altar_rect.top - SKILL_SPELL_ALTAR_OFFSET_Y
						))
						chapel_interior.interior_surface.blit(fx, fx_rect)
			else:
				player_system.draw_player(game_surface, player, hurt_up, hurt_down, hurt_left, hurt_right)

		elif entity_type == "enemy":
			sprite = entity.current_animation[entity.current_frame]
			sprite_rect = sprite.get_rect(midbottom=(entity.rect.centerx, entity.rect.bottom + ORC_SPRITE_OFFSET_Y))
			game_surface.blit(sprite, sprite_rect)
			entity.draw_health_bar(game_surface, sprite_rect)
			entity.draw_level_label(game_surface, sprite_rect)
		elif entity_type == "furniture":
			sprite, rect = entity
			house.interior_surface.blit(sprite, rect)
		elif entity_type == "chapel_furniture":
			sprite, rect = entity
			chapel_interior.interior_surface.blit(sprite, rect)
		elif entity_type in ("chapel_altar", "chapel_statue"):
			sprite, rect = entity
			chapel_interior.interior_surface.blit(sprite, rect)
		elif entity_type == "chapel_pew":
			pew_sprite, pew_rect, occupants = entity
			chapel_interior.interior_surface.blit(pew_sprite, pew_rect)
			for x, y, occupant in occupants:
				if occupant is None:
					continue
				sprite = chapel_interior.parishioner_frames[occupant][chapel_interior.parishioner_frame]
				hair_offset = chapel_interior.parishioner_hair_offset.get(occupant, 0) * CHAPEL_DECOR_SCALE
				rect = sprite.get_rect(midbottom=(x, y - hair_offset))
				chapel_interior.interior_surface.blit(sprite, rect)
		elif entity_type == "chapel_npc":
			entity.draw(chapel_interior.interior_surface)
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

		# Explosions : par-dessus les entites
	for explosion in explosions:
		explosion.draw(game_surface)

	if game_state == "chapel":
		for sprite, rect in chapel_interior.vase_nook_wall_tiles:
			chapel_interior.interior_surface.blit(sprite, rect)

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
		

	if librarian_coin_timer > 0:
		librarian_coin_timer -= 1
		progress = 1 - librarian_coin_timer / BUY_COIN_ANIMATION_DURATION
		player.coins = int(
			librarian_buy_animation_start_coins +
			(librarian_buy_animation_target_coins - librarian_buy_animation_start_coins) * progress
		)
		if librarian_coin_timer == 0:
			player.coins = librarian_buy_animation_target_coins

	if librarian_state == "goodbye":
		if pygame.time.get_ticks() - goodbye_timer > 1500:
			librarian_state = "main"
			current_npc = None
			goodbye_timer = 0
	if divinity_purchase:
		if divinity_purchase["phase"] == "wait_spell":
			# La messe joue son effet : on attend qu'elle ait fini
			priest = chapel_interior.priest_npc
			if not (priest.messe_active and priest.messe_phase == "effect"):
				divinity_purchase["phase"] = "spell"
				divinity_purchase["timer"] = len(chapel_interior.priest_spell_effect_anim) * SKILL_SPELL_FRAME_TIME
		elif divinity_purchase["phase"] == "spell":
			divinity_purchase["timer"] -= 1
			if divinity_purchase["timer"] <= 0:
				divinity_purchase["phase"] = "banner_x"
				divinity_purchase["timer"] = SKILL_BANNER_FRAMES
		elif divinity_purchase["phase"] == "banner_x":
			# L'ancien niveau s'affiche puis disparaît
			divinity_purchase["timer"] -= 1
			if divinity_purchase["timer"] <= 0:
				divinity_purchase["phase"] = "banner_y"
				divinity_purchase["timer"] = SKILL_BANNER_FRAMES
		elif divinity_purchase["phase"] == "banner_y":
			# Le nouveau niveau apparaît, puis le menu se reaffiche
			divinity_purchase["timer"] -= 1
			if divinity_purchase["timer"] <= 0:
				divinity_purchase = None
				divinity_state = "main"

	if potion_heal_timer > 0:
		potion_heal_timer -= 1
		progress = (POTION_ANIMATION_DURATION - potion_heal_timer) / POTION_ANIMATION_DURATION
		player.hp = int(round(
		potion_heal_animation_start_hp +
		(potion_heal_animation_target_hp - potion_heal_animation_start_hp) * progress
	))
		if potion_heal_timer == 0:
			player.hp = potion_heal_animation_target_hp
 
	
	
	
	

	house.repeat_horizontal(house.top_wall_front, HOUSE_INSIDE_HEIGHT - house.top_wall_front.get_height() - 130)
	house.repeat_horizontal(house.wall_front, HOUSE_INSIDE_HEIGHT - house.wall_front.get_height())
	house.repeat_horizontal(house.wall_front, HOUSE_INSIDE_HEIGHT - house.wall_front.get_height())
	for window_rect in house.window_rects:
		house.interior_surface.blit(house.window, window_rect)
	house.interior_surface.blit(house.front_door, (HOUSE_INSIDE_WIDTH // 2 - house.front_door.get_width() // 2 + 93 + 195, HOUSE_INSIDE_HEIGHT - 126))

	if game_state == "house":
		overlay_presence = True
		inside_x = (screen.get_width() - HOUSE_INSIDE_WIDTH) // 2
		inside_y = (screen.get_height() - HOUSE_INSIDE_HEIGHT) // 2
		screen.blit(house.interior_surface, (inside_x, inside_y))
		if hitboxes_visibles:
			dessiner_hitboxes(inside_x, inside_y)
	elif game_state == "chapel":
		overlay_presence = True
		screen.blit(chapel_interior.interior_surface, (-camera_x, -camera_y))
		chapel_interior.draw_debug_monk_points(chapel_interior.interior_surface)
		if hitboxes_visibles:
			dessiner_hitboxes(-camera_x, -camera_y)
	#if debug_monk_points and game_state == "chapel":
		#chapel_interior.draw_debug_monk_points(chapel_interior.interior_surface)

	else:
		overlay_presence = False
		screen.blit(game_surface, (-camera_x, -camera_y))
		if hitboxes_visibles:
			dessiner_hitboxes(-camera_x, -camera_y)

		# Slots dynamiques : un rect de plus a chaque competence "Slots" achetee
	inventory_slot_rects = [
	pygame.Rect(15 + i * 72, screen.get_height()-86, 64, 64)
	for i in range(len(player.inventory))
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
	ui.draw_xp_bar(screen, player)
	ui.draw_player_level(screen, player)
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
		if librarian_coin_timer > 0:
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
		elif current_npc and current_npc.type == "monk_desk":
			(close_rect, librarian_pay_rect, librarian_retour_rect, librarian_book_rects,
			 librarian_quit_rect, librarian_back_rect, librarian_left_arrow_rect,
			 librarian_right_arrow_rect) = librarian.draw_librarian_ui(
				screen, player, UI_SCALE, librarian_state, current_librarian_book, current_librarian_page
			)
		elif current_npc and current_npc.type == "divinity" and divinity_state != "purchase":
			(close_rect, divinity_skill_rects, divinity_quit_rect,
			 divinity_left_arrow_rect, divinity_right_arrow_rect) = divinity.draw_divinity_ui(
				screen, player, UI_SCALE, divinity_state, divinity_page
			)
	if divinity_purchase and divinity_purchase["phase"] in ("banner_x", "banner_y"):
		# Grande annonce, comme les changements de niveau :
		# "{competence} : niveau x" (disparition) puis "niveau y".
		overlay = pygame.Surface((screen.get_width(), screen.get_height()))
		overlay.set_alpha(150)
		overlay.fill((0, 0, 0))
		screen.blit(overlay, (0, 0))
		skill = divinity_purchase["skill"]
		if divinity_purchase["phase"] == "banner_x":
			shown_level = divinity_purchase["old_level"]
		else:
			shown_level = player.skill_levels[skill["key"]]
		ui._draw_hp_text(screen,
						 f"{skill['name']} : niveau {shown_level}".upper(),
						 screen.get_width() // 2, 270,
						 echelle=4, centered=True)
		
	if transition == False and current_npc == None:
		overlay_presence = False
	if menu_echap_actif or (echap_t_fermeture is not None
							and pygame.time.get_ticks() - echap_t_fermeture
							< ui.ECHAP_DUREE + 40):
		ui.dessiner_menu_echap(screen, game_state, echap_t_ouverture,
							   None if menu_echap_actif
							   else echap_t_fermeture)
		# --- mort du joueur : fondu noir puis ecran de mort ---
	if (game_state == "wave" and player.hp <= 0
			and not mort_en_cours):
		mort_en_cours = True
		mort_debut = pygame.time.get_ticks()
		menu_echap_actif = False
	if mort_en_cours and game_state == "wave":
		p = min(1.0, (pygame.time.get_ticks() - mort_debut)
			   / 700.0)
		# animation de mort : la planche de l'armure portee
		# (repli sur la premiere disponible si elle manque),
		# 7 frames joue une fois pendant le fondu
		anim_mort = None
		if mort_anims:
			anim_mort = mort_anims[min(player.equipment_level, 2)]
			if anim_mort is None:
				anim_mort = next((a for a in mort_anims
								  if a is not None), None)
		if anim_mort:
			frames_mort = anim_mort.get(player.direction) \
						  or anim_mort["down"]
			img_mort = frames_mort[min(
				len(frames_mort) - 1,
				(pygame.time.get_ticks() - mort_debut)
				// DEATH_FRAME_MS)]
			pos_mort = img_mort.get_rect(midbottom=(
				player.rect.centerx - camera_x,
				player.rect.bottom - camera_y + 10))
			screen.blit(img_mort, pos_mort)
		voile = pygame.Surface(screen.get_size())
		voile.fill((0, 0, 0))
		voile.set_alpha(int(255 * p))
		screen.blit(voile, (0, 0))
		if p >= 1.0:
			game_state = "mort"
	audio.update_music(game_state, menu_open=current_npc is not None)
	pygame.display.update()
	clock.tick(FPS_MAX)

pygame.quit() 