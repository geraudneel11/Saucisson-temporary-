import random
import pygame

# --- Taches de terre battue (haut du fichier, y = 0 à 128) ---
# Classées par taille pour un chemin qui se densifie vers le centre.
SPLAT_RECTS = {
	"small": [
		(237, 4, 6, 6), (307, 7, 6, 6), (168, 9, 5, 6), (81, 12, 6, 7),
		(112, 16, 6, 6), (76, 17, 6, 6), (240, 24, 6, 6), (137, 40, 6, 6),
		(145, 44, 7, 7), (17, 50, 6, 6),
	],
	"medium": [
		(300, 0, 8, 6), (295, 8, 10, 9), (107, 9, 9, 9), (43, 11, 9, 9),
		(235, 17, 9, 9), (201, 42, 9, 9), (235, 50, 9, 9), (97, 66, 9, 9),
	],
	"large": [
		(10, 11, 10, 11), (43, 41, 12, 12), (1, 64, 11, 13),
		(67, 89, 14, 11), (199, 97, 14, 11), (102, 90, 12, 10),
	],
	"xl": [
		(165, 106, 21, 18), (192, 109, 21, 17),
		(34, 89, 18, 12), (135, 105, 16, 15),
	],
}

# --- Touffes d'herbe (bas du fichier, y = 138 à 288) ---
# Utilisées pour décorer le sol uni, en remplacement de la texture
# d'herbe tuilée. Pas de tri par taille : juste de la variété.
GRASS_TUFT_RECTS = [
	(13, 141, 23, 29), (58, 138, 32, 24), (218, 179, 21, 19),
	(10, 236, 30, 19), (145, 186, 25, 25), (303, 142, 25, 25),
	(101, 141, 17, 26), (37, 189, 17, 26), (39, 264, 17, 20),
	(212, 264, 21, 16), (171, 264, 22, 13), (281, 190, 21, 22),
	(252, 210, 17, 20), (214, 242, 20, 12), (213, 221, 18, 16),
	(10, 268, 13, 10), (250, 188, 10, 10), (313, 187, 13, 9),
	(275, 154, 10, 9), (314, 235, 10, 9), (293, 141, 7, 5),
	(245, 153, 7, 5), (63, 227, 7, 5), (260, 244, 6, 5),
	(140, 206, 3, 4), (204, 201, 4, 2),
]
ROCK_RECTS = [
	(146, 113, 14, 14),
	(162, 115, 15, 12),
	(176, 112, 16, 15),
	(194, 116, 14, 12),
	(208, 113, 16, 15),
]


def load_ground_details(splat_scale=3, tuft_scale=2.5, rock_scale=3):
	sheet = pygame.image.load("ground_grass_details.png").convert_alpha()
	rock_sheet = pygame.image.load("exterior.png").convert_alpha()

	tiles = {}
	for tier_name, rects in SPLAT_RECTS.items():
		tiles[tier_name] = []
		for (x, y, w, h) in rects:
			piece = sheet.subsurface((x, y, w, h))
			if splat_scale != 1:
				piece = pygame.transform.scale(
					piece, (int(w * splat_scale), int(h * splat_scale))
				)
			tiles[tier_name].append(piece)

	tiles["grass_tufts"] = []
	for (x, y, w, h) in GRASS_TUFT_RECTS:
		piece = sheet.subsurface((x, y, w, h))
		if tuft_scale != 1:
			piece = pygame.transform.scale(
				piece, (int(w * tuft_scale), int(h * tuft_scale))
			)
		tiles["grass_tufts"].append(piece)

	tiles["rocks"] = []
	for (x, y, w, h) in ROCK_RECTS:
		piece = rock_sheet.subsurface((x, y, w, h))
		if rock_scale != 1:
			piece = pygame.transform.scale(
				piece, (int(w * rock_scale), int(h * rock_scale))
			)
		tiles["rocks"].append(piece)

	return tiles


def _pick_tile(tiles, closeness):
	"""
	closeness va de 0 (bord, loin du centre du chemin/de la place) à 1
	(plein centre). Plus on est proche du centre, plus on pioche dans
	les taches grandes/denses ; plus on est loin, plus c'est petit et
	discret, pour se fondre dans l'herbe.
	"""
	if closeness > 0.75:
		pool = tiles["xl"] + tiles["large"]
	elif closeness > 0.45:
		pool = tiles["large"] + tiles["medium"]
	elif closeness > 0.2:
		pool = tiles["medium"] + tiles["small"]
	else:
		pool = tiles["small"]
	return random.choice(pool)


def generate_path(tiles, start, end, half_width=45, step=18,
				   edge_chance=0.30, center_chance=0.85):
	"""
	Génère une liste de (x, y, surface) à disperser entre 'start' et
	'end' (deux tuples (x, y) en coordonnées monde), pour simuler un
	chemin de terre battue discret et naturel.
	"""
	placements = []
	x0, y0 = start
	x1, y1 = end
	dx, dy = x1 - x0, y1 - y0
	length = max(1, (dx ** 2 + dy ** 2) ** 0.5)
	steps = int(length // step)

	perp_x, perp_y = -dy / length, dx / length

	for i in range(steps + 1):
		t = i / max(1, steps)
		cx = x0 + dx * t
		cy = y0 + dy * t

		for offset in range(-half_width, half_width + 1, step):
			closeness = 1 - abs(offset) / half_width
			chance = edge_chance + (center_chance - edge_chance) * closeness

			if random.random() > chance:
				continue

			jitter_x = random.randint(-6, 6)
			jitter_y = random.randint(-6, 6)

			px = cx + perp_x * offset + jitter_x
			py = cy + perp_y * offset + jitter_y

			tile = _pick_tile(tiles, closeness)
			placements.append((px, py, tile))

	return placements



def generate_plaza(tiles, center, radius=320, density=0.7, step=18,
					rock_chance=0.12, overflow=0.18):
	"""
	Génère la place autour de 'center'. Retourne un tuple
	(placements, rock_placements) séparé exprès : les cailloux sont
	renvoyés à part pour être dessinés en dernier (par-dessus le
	reste), et donc toujours visibles au premier plan.

	Au-delà de 'radius', une zone de débordement (contrôlée par
	'overflow') continue de placer quelques taches, de plus en plus
	rares en s'éloignant, pour un bord irrégulier qui déborde
	naturellement dans l'herbe au lieu de s'arrêter net en cercle.
	"""
	placements = []
	rock_placements = []
	cx, cy = center
	max_radius = radius * (1 + overflow)

	for x in range(int(cx - max_radius), int(cx + max_radius), step):
		for y in range(int(cy - max_radius), int(cy + max_radius), step):
			dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
			if dist > max_radius:
				continue

			if dist <= radius:
				closeness = 1 - dist / radius
				chance = density * (0.55 + 0.45 * closeness)
			else:
				# zone de débordement : de plus en plus clairsemée
				overflow_t = (dist - radius) / (max_radius - radius)
				chance = density * 0.25 * (1 - overflow_t)
				closeness = 0

			if random.random() > chance:
				continue

			jitter_x = random.randint(-6, 6)
			jitter_y = random.randint(-6, 6)
			px, py = x + jitter_x, y + jitter_y

			if random.random() < rock_chance:
				rock_placements.append((px, py, random.choice(tiles["rocks"])))
			else:
				placements.append((px, py, _pick_tile(tiles, closeness)))

	return placements, rock_placements

def build_ground_layer(map_width, map_height, grass_color, tuft_tiles,
						spacing=70, jitter=25, coverage=0.5):
	"""
	Construit UNE SEULE FOIS une surface de la taille de la carte :
	un fond plat de la couleur 'grass_color', parsemé de touffes
	d'herbe (tuft_tiles) à intervalles irréguliers. Remplace l'ancien
	tuilage de Herbe.jpg — à appeler au démarrage, pas dans la boucle.
	"""
	layer = pygame.Surface((map_width, map_height)).convert()
	layer.fill(grass_color)

	for x in range(0, map_width, spacing):
		for y in range(0, map_height, spacing):
			if random.random() > coverage:
				continue

			jitter_x = random.randint(-jitter, jitter)
			jitter_y = random.randint(-jitter, jitter)

			tuft = random.choice(tuft_tiles)
			layer.blit(tuft, (x + jitter_x, y + jitter_y))

	return layer

def adjust_ground_color(color, darken=0.9, desaturate=0.25):
	"""
	Éloigne légèrement la couleur du sol de celle des touffes d'herbe
	(évite l'effet "ton sur ton"), sans changement extravagant.
	"""
	r, g, b = color[0], color[1], color[2]
	gray = (r + g + b) / 3

	r = r * (1 - desaturate) + gray * desaturate
	g = g * (1 - desaturate) + gray * desaturate
	b = b * (1 - desaturate) + gray * desaturate

	return (int(r * darken), int(g * darken), int(b * darken))

def bake_path_sprites(ground_layer, tiles, start, end, half_width=45,
                       step=14, fill_chance=0.95, rock_chance=0.0):
    """
    Peint directement sur ground_layer un chemin de terre battue dense
    entre 'start' et 'end', avec les sprites de
    ground_grass_details.png, puis quelques cailloux par-dessus si
    rock_chance > 0.
    """
    x0, y0 = start
    x1, y1 = end
    dx, dy = x1 - x0, y1 - y0
    length = max(1, (dx ** 2 + dy ** 2) ** 0.5)
    steps = int(length // step)
    perp_x, perp_y = -dy / length, dx / length

    # --- Taches de terre ---
    for i in range(steps + 1):
        t = i / max(1, steps)
        px0 = x0 + dx * t
        py0 = y0 + dy * t

        for offset in range(-half_width, half_width + 1, step):
            closeness = 1 - abs(offset) / half_width
            if random.random() > fill_chance * (0.6 + 0.4 * closeness):
                continue

            jitter_x = random.randint(-5, 5)
            jitter_y = random.randint(-5, 5)
            px = px0 + perp_x * offset + jitter_x
            py = py0 + perp_y * offset + jitter_y

            tile = _pick_tile(tiles, closeness)
            ground_layer.blit(
                tile,
                (int(px - tile.get_width() // 2), int(py - tile.get_height() // 2))
            )

    # --- Quelques cailloux, en dernier -> toujours visibles au-dessus ---
    if rock_chance > 0:
        for i in range(steps + 1):
            t = i / max(1, steps)
            px0 = x0 + dx * t
            py0 = y0 + dy * t

            for offset in range(-half_width, half_width + 1, step * 2):
                if random.random() > rock_chance:
                    continue

                jitter_x = random.randint(-8, 8)
                jitter_y = random.randint(-8, 8)
                px = px0 + perp_x * offset + jitter_x
                py = py0 + perp_y * offset + jitter_y

                rock = random.choice(tiles["rocks"])
                ground_layer.blit(
                    rock,
                    (int(px - rock.get_width() // 2), int(py - rock.get_height() // 2))
                )

def build_path_layer(tiles, start, end, half_width=45, step=14,
                      fill_chance=0.95, rock_chance=0.0, margin=40):
    """
    Construit UNE SEULE FOIS une petite surface (pas toute la carte)
    contenant le chemin de terre battue entre 'start' et 'end'.
    Retourne (surface, top_left) : top_left est la position en
    coordonnées monde du coin haut-gauche de cette surface, à
    utiliser pour la coller au bon endroit chaque frame.
    """
    x0, y0 = start
    x1, y1 = end

    min_x = min(x0, x1) - half_width - margin
    max_x = max(x0, x1) + half_width + margin
    min_y = min(y0, y1) - half_width - margin
    max_y = max(y0, y1) + half_width + margin

    width = int(max_x - min_x)
    height = int(max_y - min_y)

    layer = pygame.Surface((width, height), pygame.SRCALPHA)

    def to_local(px, py):
        return px - min_x, py - min_y

    dx, dy = x1 - x0, y1 - y0
    length = max(1, (dx ** 2 + dy ** 2) ** 0.5)
    steps = int(length // step)
    perp_x, perp_y = -dy / length, dx / length

    # --- Taches de terre ---
    for i in range(steps + 1):
        t = i / max(1, steps)
        px0 = x0 + dx * t
        py0 = y0 + dy * t

        for offset in range(-half_width, half_width + 1, step):
            closeness = 1 - abs(offset) / half_width
            if random.random() > fill_chance * (0.6 + 0.4 * closeness):
                continue

            jitter_x = random.randint(-5, 5)
            jitter_y = random.randint(-5, 5)
            px = px0 + perp_x * offset + jitter_x
            py = py0 + perp_y * offset + jitter_y
            lx, ly = to_local(px, py)

            tile = _pick_tile(tiles, closeness)
            layer.blit(tile, (int(lx - tile.get_width() // 2), int(ly - tile.get_height() // 2)))

    # --- Cailloux, en dernier -> toujours visibles au-dessus ---
    if rock_chance > 0:
        for i in range(steps + 1):
            t = i / max(1, steps)
            px0 = x0 + dx * t
            py0 = y0 + dy * t

            for offset in range(-half_width, half_width + 1, step * 2):
                if random.random() > rock_chance:
                    continue

                jitter_x = random.randint(-8, 8)
                jitter_y = random.randint(-8, 8)
                px = px0 + perp_x * offset + jitter_x
                py = py0 + perp_y * offset + jitter_y
                lx, ly = to_local(px, py)

                rock = random.choice(tiles["rocks"])
                layer.blit(rock, (int(lx - rock.get_width() // 2), int(ly - rock.get_height() // 2)))

    return layer, (int(min_x), int(min_y))

def build_shop_decor_layer(tiles, plaza_sprite, plaza_center, path_start, path_end,
                            half_width=45, step=14, fill_chance=0.95,
                            rock_chance=0.0, margin=60):
    """
    Construit UNE SEULE FOIS une surface combinant le chemin (dessiné
    en premier, donc EN DESSOUS) et la place plaza_sprite (dessinée
    par-dessus, donc au-dessus du bout de chemin qui passe sous son
    bord). Retourne (surface, top_left).
    """
    x0, y0 = path_start
    x1, y1 = path_end

    plaza_half_w = plaza_sprite.get_width() // 2
    plaza_half_h = plaza_sprite.get_height() // 2

    min_x = min(x0, x1, plaza_center[0] - plaza_half_w) - margin
    max_x = max(x0, x1, plaza_center[0] + plaza_half_w) + margin
    min_y = min(y0, y1, plaza_center[1] - plaza_half_h) - margin
    max_y = max(y0, y1, plaza_center[1] + plaza_half_h) + margin

    width = int(max_x - min_x)
    height = int(max_y - min_y)

    layer = pygame.Surface((width, height), pygame.SRCALPHA)

    def to_local(px, py):
        return px - min_x, py - min_y

    dx, dy = x1 - x0, y1 - y0
    length = max(1, (dx ** 2 + dy ** 2) ** 0.5)
    steps = int(length // step)
    perp_x, perp_y = -dy / length, dx / length

    # --- Chemin (dessous) ---
    for i in range(steps + 1):
        t = i / max(1, steps)
        px0 = x0 + dx * t
        py0 = y0 + dy * t

        for offset in range(-half_width, half_width + 1, step):
            closeness = 1 - abs(offset) / half_width
            if random.random() > fill_chance * (0.6 + 0.4 * closeness):
                continue
            jitter_x = random.randint(-5, 5)
            jitter_y = random.randint(-5, 5)
            px = px0 + perp_x * offset + jitter_x
            py = py0 + perp_y * offset + jitter_y
            lx, ly = to_local(px, py)
            tile = _pick_tile(tiles, closeness)
            layer.blit(tile, (int(lx - tile.get_width() // 2), int(ly - tile.get_height() // 2)))

    if rock_chance > 0:
        for i in range(steps + 1):
            t = i / max(1, steps)
            px0 = x0 + dx * t
            py0 = y0 + dy * t
            for offset in range(-half_width, half_width + 1, step * 2):
                if random.random() > rock_chance:
                    continue
                jitter_x = random.randint(-8, 8)
                jitter_y = random.randint(-8, 8)
                px = px0 + perp_x * offset + jitter_x
                py = py0 + perp_y * offset + jitter_y
                lx, ly = to_local(px, py)
                rock = random.choice(tiles["rocks"])
                layer.blit(rock, (int(lx - rock.get_width() // 2), int(ly - rock.get_height() // 2)))

    # --- Place (dessus, recouvre le bout de chemin qui passe dessous) ---
    plaza_local = to_local(*plaza_center)
    plaza_rect = plaza_sprite.get_rect(center=plaza_local)
    layer.blit(plaza_sprite, plaza_rect)

    return layer, (int(min_x), int(min_y))

def load_plaza_sprite(scale=0.5):
    """Charge plaza.png (image toute faite) à l'échelle voulue."""
    sprite = pygame.image.load("plaza.png").convert_alpha()
    if scale != 1:
        sprite = pygame.transform.scale(
            sprite,
            (int(sprite.get_width() * scale), int(sprite.get_height() * scale))
        )
    return sprite


def bake_plaza_image(ground_layer, plaza_sprite, center):
    """Colle plaza.png centrée sur 'center', une seule fois."""
    rect = plaza_sprite.get_rect(center=center)
    ground_layer.blit(plaza_sprite, rect)