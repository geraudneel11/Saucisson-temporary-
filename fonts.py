import pygame

pygame.init()

font = pygame.font.SysFont("Ebrima", 36, bold=True)
coin_font = pygame.font.SysFont("Ebrima", 32, bold=True)

def load_font():
	global title_font_sheet, corp_font_sheet, lettersT1, lettersC1, lettersC6, glyph_width, lettersC4
	global title3_font_sheet, lettersT3
	global title4_font_sheet, lettersT4
	title_font_sheet = pygame.image.load("Text1.png").convert_alpha()
	corp_font_sheet = pygame.image.load("Text2.png").convert_alpha()
	title3_font_sheet = pygame.image.load("Text3.png").convert_alpha()
	title4_font_sheet = pygame.image.load("Text4.png").convert_alpha()
	global title5_font_sheet, lettersT5
	title5_font_sheet = pygame.image.load("Text5.png").convert_alpha()
	global title6_font_sheet, lettersT6
	title6_font_sheet = pygame.image.load("Text6.png").convert_alpha()


	corp_font_chars = [
	"A","B","C","D","E","F","G","H","I","J",
	"K","L","M","N","O","P","Q","R","S","T",
	"U","V","W","X","Y","Z", None, None, None, None,
	"1","2","3","4","5","6","7","8","9","0",
	".", ",", ":", "?", "!", "(", ")", "+", "-", "="
]

	glyph_width = {
	"'": 2,
	".": 2,
	",": 2,
	":": 2,
	"!": 2,
}

	lettersT1 = {"A" : title_font_sheet.subsurface((0, 0, 7, 9.2)),
			 "B" : title_font_sheet.subsurface((7, 0, 7, 9.2)),
			 "C" : title_font_sheet.subsurface((14, 0, 7, 9.2)),
			 "D" : title_font_sheet.subsurface((21, 0, 7, 9.2)),
			 "E" : title_font_sheet.subsurface((28, 0, 7, 9.2)),
			 "F" : title_font_sheet.subsurface((35, 0, 7, 9.2)),
			 "G" : title_font_sheet.subsurface((42, 0, 7, 9.2)),
			 "H" : title_font_sheet.subsurface((49, 0, 7, 9.2)),
			 "I" : title_font_sheet.subsurface((56, 0, 7, 9.2)),
			 "J" : title_font_sheet.subsurface((63, 0, 7, 9.2)),
			 "K" : title_font_sheet.subsurface((0, 9.2, 7, 9.2)),
			 "L" : title_font_sheet.subsurface((7, 9.2, 7, 9.2)),
			 "M" : title_font_sheet.subsurface((14, 9.2, 7, 9.2)),
			 "N" : title_font_sheet.subsurface((21, 9.2, 7, 9.2)),
			 "O" : title_font_sheet.subsurface((28, 9.2, 7, 9.2)),
			 "P" : title_font_sheet.subsurface((35, 9.2, 7, 9.2)),
			 "Q" : title_font_sheet.subsurface((42, 9.2, 7, 9.2)),
			 "R" : title_font_sheet.subsurface((49, 9.2, 7, 9.2)),
			 "S" : title_font_sheet.subsurface((56, 9.2, 7, 9.2)),
			 "T" : title_font_sheet.subsurface((63, 9.2, 7, 9.2)),
			 "U" : title_font_sheet.subsurface((0, 18.4, 7, 9.2)),
			 "V" : title_font_sheet.subsurface((7, 18.4, 7, 9.2)),
			 "W" : title_font_sheet.subsurface((14, 18.4, 7, 9.2)),
			 "X" : title_font_sheet.subsurface((21, 18.4, 7, 9.2)),
			 "Y" : title_font_sheet.subsurface((28, 18.4, 7, 9.2)),
			 "Z" : title_font_sheet.subsurface((35, 18.4, 7, 9.2)),
			 " " : title_font_sheet.subsurface((42, 18.4, 7, 9.2)),
			 "1" : title_font_sheet.subsurface((0, 27.6, 7, 9.2)),
			 "2" : title_font_sheet.subsurface((7, 27.6, 7, 9.2)),
			 "3" : title_font_sheet.subsurface((14, 27.6, 7, 9.2)),
			 "4" : title_font_sheet.subsurface((21, 27.6, 7, 9.2)),
			 "5" : title_font_sheet.subsurface((28, 27.6, 7, 9.2)),
			 "6" : title_font_sheet.subsurface((35, 27.6, 7, 9.2)),
			 "7" : title_font_sheet.subsurface((42, 27.6, 7, 9.2)),
			 "8" : title_font_sheet.subsurface((49, 27.6, 7, 9.2)),
			 "9" : title_font_sheet.subsurface((56, 27.6, 7, 9.2)),
			 "0" : title_font_sheet.subsurface((63, 27.6, 7, 9.2)),
			 "." : title_font_sheet.subsurface((0, 36.8, 7, 9.2)),
			 "," : title_font_sheet.subsurface((7, 36.8, 7, 9.2)),
			 ":" : title_font_sheet.subsurface((14, 36.8, 7, 9.2)),
			 "?" : title_font_sheet.subsurface((21, 36.8, 7, 9.2)),
			 "!" : title_font_sheet.subsurface((28, 36.8, 7, 9.2)),
			 "(" : title_font_sheet.subsurface((35, 36.8, 7, 9.2)),
			 ")" : title_font_sheet.subsurface((42, 36.8, 7, 9.2)),
			 "+" : title_font_sheet.subsurface((49, 36.8, 7, 9.2)),
			 "-" : title_font_sheet.subsurface((56, 36.8, 7, 9.2)),
			 "=" : title_font_sheet.subsurface((63, 36.8, 7, 9.2)),
}

		# Chiffres blancs de Text3 : meme grille 7x9.2 que Text1, bloc C1
	# (offset 0). Si un jour les chiffres blancs passent dans un autre
	# bloc de la planche, il suffit de changer T3_OFFSET_Y de 46 en 46.
	T3_OFFSET_Y = 0.0
		# Text4 : TOUTES les lettres ET chiffres en jaune (bloc C1)
	lettersT3 = build_title_font(title3_font_sheet, T3_OFFSET_Y)

		# Chiffres jaunes de Text4 : meme grille que Text3 (bloc C1)
		# Text4 : TOUTES les lettres ET chiffres en jaune (bloc C1)
	lettersT4 = build_title_font(title4_font_sheet, T3_OFFSET_Y)
	lettersT5 = build_title_font(title5_font_sheet, T3_OFFSET_Y)
	lettersT6 = build_title_font(title6_font_sheet, T3_OFFSET_Y)
		
	lettersC1 = build_body_font(
	corp_font_sheet,
	corp_font_chars,
	cols=10,
	cell_w=5,
	cell_h=6,
	offset_y=0
)
	lettersC6 = build_body_font(
	corp_font_sheet,
	corp_font_chars,
	cols=10,
	cell_w=5,
	cell_h=6,
	offset_y=191
)
	lettersC4 = build_body_font(
		corp_font_sheet,
		corp_font_chars,
		cols=10,
		cell_w=5,
		cell_h=6,
		offset_y=95
	)

def build_body_font(sheet, chars, cols, cell_w, cell_h, offset_y=0):
	font = {}
	font[","] = sheet.subsurface((8, 27, 3, 3))
	apostrophe = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
	apostrophe.blit(font[","], (0, 0))
	font["'"] = apostrophe
	for i, char in enumerate(chars):
		if char is None:
			continue
		x = (i % cols) * cell_w
		y = (i // cols) * cell_h + offset_y
		font[char] = sheet.subsurface(
			(x, y, cell_w, cell_h))
	return font

def build_title_font(sheet, offset_y=0.0):
	# dictionnaire complet de la police titre (meme grille 7x9.2 que
	# Text1) : lettres, espace, chiffres et ponctuation d'un bloc
	lignes = ["ABCDEFGHIJ", "KLMNOPQRST", "UVWXYZ ",
			  "1234567890", ".,:?!()+-="]
	font = {}
	for r, ligne in enumerate(lignes):
		for c, char in enumerate(ligne):
			font[char] = sheet.subsurface((c * 7, r * 9.2 + offset_y, 7, 9.2))
	return font

def draw_text(surface, text, x, y, scale=1, spacing=0, centered=False):
	total_width = 0
	for char in text.upper():
		if char == " ":
			total_width += 7 * scale
			continue
		if char not in lettersT1:
			continue
		sprite = lettersT1[char]
		total_width += int(sprite.get_width() * scale) + spacing
	if centered:
		x -= total_width // 2
	current_x = x
	for char in text.upper():
		if char == " ":
			current_x += 7 * scale
			continue
		if char not in lettersT1:
			continue
		sprite = lettersT1[char]
		if scale != 1:
			sprite = pygame.transform.scale(
				sprite,
				(
					int(sprite.get_width() * scale),
					int(sprite.get_height() * scale)
				)
			)
		surface.blit(sprite, (current_x, y))
		current_x += max(1, sprite.get_width() + spacing)

def draw_line(surface, text, x, y, scale=1, centered=False, font_dict=None):
	if font_dict is None:
		font_dict = lettersC1
	letter_spacing = 1
	word_spacing = 4
	total_width = 0
	for char in text.upper():
		if char == " ":
			total_width += word_spacing * scale
			continue
		if char not in font_dict:
			continue
		sprite = font_dict[char]
		total_width += sprite.get_width() * scale + letter_spacing
	if centered:
		x -= total_width // 2
	current_x = x
	for char in text.upper():
		if char == " ":
			current_x += word_spacing * scale
			continue
		if char not in font_dict:
			continue
		sprite = font_dict[char]
		if scale != 1:
			sprite = pygame.transform.scale(
				sprite,
				(
					sprite.get_width() * scale,
					sprite.get_height() * scale
				)
			)
		surface.blit(sprite, (current_x, y))
		advance = glyph_width.get(char, sprite.get_width())
		current_x += advance + letter_spacing

def get_text_width(text, scale, font_dict):
	width = 0
	for char in text.upper():
		if char == " ":
			width += 4 * scale
		elif char in font_dict:
			width += font_dict[char].get_width() * scale + 1
	return width

def draw_body_text(surface, text, x, y, max_width, font_dict, scale=1, visible_chars=None):
	if visible_chars is not None:
		text = text[:visible_chars]
	words = text.split(" ")
	line = ""
	for word in words:
		test_line = line + word + " "
		width = get_text_width(test_line, scale, font_dict)
		if width > max_width and line != "":
			draw_line(surface, line, x, y, scale, font_dict=font_dict)
			y += 8 * scale          
			line = word + " "
		else:
			line = test_line
	draw_line(surface, line, x, y, scale, font_dict=font_dict)

def draw_wrapped_text(surface, text, x, y, max_width, font_dict, scale=1, max_y=None):
	"""
	Comme draw_body_text, mais :
	  - coupe aussi les mots plus longs qu'une ligne entière (caractère
	    par caractère), ce que draw_body_text ne sait pas faire ;
	  - s'arrête d'écrire dès qu'une ligne dépasserait 'max_y'
	    (coordonnée écran), pour ne jamais déborder de la zone de texte.
	"""
	line_step = 8 * scale
	lines = []
	line = ""

	for word in text.split(" "):
		# Mot trop long pour une ligne : on le découpe en morceaux.
		while get_text_width(word, scale, font_dict) > max_width:
			cut = len(word)
			while cut > 1 and get_text_width(word[:cut], scale, font_dict) > max_width:
				cut -= 1
			if line != "":
				lines.append(line)
				line = ""
			lines.append(word[:cut])
			word = word[cut:]

		test_line = line + word + " "
		if get_text_width(test_line, scale, font_dict) > max_width and line != "":
			lines.append(line)
			line = word + " "
		else:
			line = test_line

	if line != "":
		lines.append(line)

	for text_line in lines:
		if max_y is not None and y + line_step > max_y:
			break
		draw_line(surface, text_line, x, y, scale, font_dict=font_dict)
		y += line_step
