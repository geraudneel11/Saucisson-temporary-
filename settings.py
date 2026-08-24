import random

# --- Fumée de la cheminée ---
SMOKE_SCALE = 2.5
SMOKE_ANIMATION_SPEED = 12   # plus haut = fumée plus lente

# Position de la fumée par rapport au coin haut-gauche de la maison
# (house_x, house_y). À AJUSTER en testant en jeu, selon où se trouve
# la cheminée sur ton sprite exterior.png.
HOUSE_SMOKE_OFFSET_X = 160
HOUSE_SMOKE_OFFSET_Y = 126

SCREEN_WIDTH = 840
SCREEN_HEIGHT = 525

MAP_WIDTH = 10000
MAP_HEIGHT = 10000

PLAYER_SPEED = 14

PLAYER_SCALE = 3.5
ORC_SCALE = 3.5
PORTAL_SCALE = 6
COINS_SCALE = 3
HOUSE_SCALE = 4
NPC_SCALE = 3.5
WALL_SCALE = 4.5
UI_SCALE = 4.5

FPS_MAX = 60

MONSTRES = 15

ORC_SPRITE_OFFSET_Y = 105
PLAYER_SPRITE_OFFSET_Y = -7

HOUSE_X = MAP_WIDTH // 2 - 3000
HOUSE_Y = MAP_HEIGHT // 2 - 500
HOUSE_INSIDE_WIDTH = 1050
HOUSE_INSIDE_HEIGHT = 925

HEAL_POTION_QUANTITY = random.randint(3, 6)
HEAL_POTION_MAX_QUANTITY = 5

TRANSITION_TIMER = 120

DEBUG_HITBOXES = False

# --- Décor de sol (herbe + chemin + place) ---
SPLAT_SCALE = 3
TUFT_SCALE = 2.5
PLAZA_RADIUS = 290
PATH_HALF_WIDTH = 70

GROUND_TUFT_SPACING = 70    # distance moyenne entre deux touffes
GROUND_TUFT_JITTER = 25     # dispersion aléatoire autour de cette grille
GROUND_TUFT_COVERAGE = 0.5  # 0 = aucune touffe, 1 = une touffe partout

PORTAL_SIZE = 80
PLAZA_DENSITY = 6
PLAZA_ROCK_CHANCE = 0.01

GROUND_COLOR_DARKEN = 0.9
GROUND_COLOR_DESATURATE = 0.25

PLAZA_OVERFLOW = 0.18     # débordement irrégulier au-delà du rayon
ROCK_SCALE = 0.7          # cailloux plus petits (était 3, comme les taches de terre)

PLAZA_FILL_CHANCE = 0.95
PLAZA_STEP = 14

PORTAL_OFFSET_X = 0
PORTAL_OFFSET_Y = -100   # règle la position Y du portail ici (négatif = plus haut, positif = plus bas)

PATH_ROCK_CHANCE = 0.03   # quelques cailloux, pas une invasion
PLAYER_SHOP_SPAWN_OFFSET_X = 110   # distance au portail à l'arrivée en shop, pour ne pas le retoucher aussitôt
PLAYER_SHOP_SPAWN_OFFSET_Y = 0   # distance au portail à l'arrivée en shop, pour ne pas le retoucher aussitôt

# Positions absolues (x, y) sur la carte, calculées pour une carte de
# 10000x10000 avec la maison en (MAP_WIDTH//2+1800, MAP_HEIGHT//2+1400)
# et le portail sans offset. Si tu changes ces réglages, les arbres ne
# suivront pas automatiquement (contrairement à avant) — c'est le prix
# à payer pour un placement 100% manuel sur toute la carte. Modifie,
# déplace ou supprime les entrées comme tu veux.
TREE_POSITIONS = [
	(5305, 2471), (6468, 791), (1186, 8779), (1542, 5991), (9548, 950),
	(8313, 3517), (614, 1408), (1144, 3943), (6955, 968), (9264, 2028),
	(3657, 9551), (1013, 9455), (9593, 6499), (812, 3622), (2181, 4744),
	(6867, 2363), (9353, 5054), (9179, 2961), (1688, 9528), (6101, 1596),
	(8974, 1028), (3374, 8133), (8711, 7005), (5146, 7628), (9593, 7424),
	(5924, 4911), (4070, 2945), (3999, 1341), (8604, 8111), (5627, 7353),
	(1199, 1934), (2702, 5604), (2490, 8011), (5572, 5737), (4422, 7767),
	(1064, 994), (5072, 9469), (7301, 4662), (6320, 5685), (369, 7564),
	(5823, 2753), (1918, 8088), (4709, 2119), (4056, 6519), (6405, 8134),
	(1320, 2725), (9002, 4552), (2243, 7053), (6804, 5878), (6233, 3780),
	(2472, 1359), (2887, 2478), (3800, 3822), (9652, 2987), (4304, 4619),
	(6864, 8758), (884, 7481), (6521, 6536), (7889, 6560), (1019, 3122),
	(7219, 2659), (1801, 5571), (9286, 2478), (8791, 1662), (5957, 417),
	(1824, 409), (4506, 4012), (3657, 2286), (1679, 8935), (6912, 520),
	(434, 9195), (3257, 8928), (6873, 3611), (7359, 9654), (5574, 4552),
	(2547, 3527), (5514, 1674), (4333, 711), (7527, 8785), (2045, 6201),
	(4803, 5925), (3733, 4741), (3432, 4374), (2803, 8751), (7573, 6216),
	(4422, 9125), (3598, 5313), (525, 5168), (6572, 4386), (6482, 7517),
	(2340, 4339), (9197, 8830), (4304, 9577), (1489, 771), (1796, 2504),
	(8669, 4119), (4371, 5573), (4315, 8201), (2927, 8317), (1743, 4889),
	(319, 1832), (1290, 1403), (7962, 1133), (4342, 8645), (7397, 1982),
]
TREE_POSITIONS_TYPE2 = [
	(2929, 3772), (4070, 2183), (6276, 8696), (3550, 6127), (2494, 7560),
	(2932, 9288), (7684, 5183), (7580, 840), (5857, 2115), (2883, 607),
	(6970, 1409), (8575, 6640), (3289, 907), (3464, 7257), (5796, 7801),
	(2037, 1580), (4849, 2853), (2910, 6715), (5528, 3544), (5517, 6543),
	(615, 6111), (8243, 4801), (8736, 2085), (4207, 7060), (7209, 3186),
	(3238, 5658), (8712, 3317), (8374, 7276), (3281, 337), (523, 955),
]

TREE_POSITIONS_TYPE3 = [
	(6828, 4910), (6049, 9129), (9633, 9419), (1640, 6466), (5895, 4098),
	(6269, 3009), (7850, 9384), (7804, 2776), (2597, 7193), (942, 6843),
	(1860, 2059), (2243, 2460), (542, 8400), (2942, 1820), (2602, 2174),
	(8068, 7004), (5481, 5356), (3713, 8978), (2469, 303), (4731, 6546),
	(3961, 4256), (1539, 7122), (470, 3310), (2158, 2944), (4922, 1003),
	(9498, 7055), (8224, 2619), (8591, 9198), (9250, 5475), (8121, 3098),
]
# Ajustements individuels de hitbox par arbre, comme
# furniture_hitbox_config pour la maison. Clé = index de l'arbre
# (son rang dans TREE_POSITIONS, en commençant à 0), valeur = dict
# avec les clés optionnelles "width", "height", "offset_x", "offset_y".
# Un arbre absent de ce dict garde les valeurs par défaut (24, 18, 0, 0).
TREE_HITBOX_OVERRIDES = {
	# Exemple : "arbre #5" a un tronc décalé vers le bas et un peu
	# plus large que la moyenne.
	# 5: {"width": 30, "offset_y": -8},
}
TREE_HITBOX_OFFSET_Y = -80
TREE_SWAY_MIN_SECONDS = 5
TREE_SWAY_MAX_SECONDS = 20
TREE_SWAY_FRAME_SPEED = 6   # vitesse de l'animation elle-même (ticks entre deux frames)