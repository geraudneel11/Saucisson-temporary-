import pygame

def load_animation(sheet, scale, columns):

    frame_width = sheet.get_width() // columns
    frame_height = sheet.get_height()

    animation = []

    for i in range(columns):
        frame = sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
        frame = pygame.transform.scale(
            frame,
            (
                frame_width * scale,
                frame_height * scale
            )
        )
        animation.append(frame)
    return animation

def load_animation_row(sheet, row, scale, columns, rows):

    frames = []

    frame_width = sheet.get_width() // columns
    frame_height = sheet.get_height() // rows

    for col in range(columns):

        frame = sheet.subsurface(
            (
                col * frame_width,
                row * frame_height,
                frame_width,
                frame_height
            )
        )

        frame = pygame.transform.scale(
            frame,
            (
                int(frame_width * scale),
                int(frame_height * scale)
            )
        )

        frames.append(frame)

    return frames

def load_animation_column(sheet, column, scale, columns, rows):

    frames = []

    frame_width = sheet.get_width() // columns
    frame_height = sheet.get_height() // rows

    for row in range(rows):

        frame = sheet.subsurface(
            (
                column * frame_width,
                row * frame_height,
                frame_width,
                frame_height
            )
        )

        frame = pygame.transform.scale(
            frame,
            (
                int(frame_width * scale),
                int(frame_height * scale)
            )
        )

        frames.append(frame)

    return frames

def load_animation_grid(sheet, scale, columns, rows, frame_count=None):
    """
    Découpe une feuille en grille (colonnes x rangées), lue ligne par
    ligne (comme un texte : rangée 0 de gauche à droite, puis rangée 1,
    etc.). 'frame_count' permet de s'arrêter avant la fin si les
    dernières cases de la grille sont vides (comme pour le dragon, où
    la case 25/25 est vide).
    """

    frame_width = sheet.get_width() // columns
    frame_height = sheet.get_height() // rows

    total_frames = columns * rows if frame_count is None else frame_count

    frames = []

    for i in range(total_frames):
        col = i % columns
        row = i // columns

        frame = sheet.subsurface(
            (col * frame_width, row * frame_height, frame_width, frame_height)
        )

        frame = pygame.transform.scale(
            frame,
            (
                int(frame_width * scale),
                int(frame_height * scale)
            )
        )

        frames.append(frame)

    return frames

def split_frames_by_regions(frames, region_rects):
    """
    Sépare chaque frame d'une liste d'animation en deux surfaces de la
    MÊME TAILLE que l'originale (donc utilisables avec le même rect de
    position à l'affichage) :
      - 'inside'  : ne garde que le contenu des rectangles de
                    'region_rects' (union de plusieurs zones possible),
                    le reste est transparent.
      - 'outside' : garde tout SAUF ces rectangles.

    Accepter plusieurs rectangles permet de découper une forme non
    rectangulaire (ex : une aile sans la patte qui dépasse dessous) en
    excluant simplement certaines zones du découpage.
    """

    inside_frames = []
    outside_frames = []

    for frame in frames:
        inside = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
        outside = frame.copy()

        for region_rect in region_rects:
            crop = frame.subsurface(region_rect)
            inside.blit(crop, region_rect.topleft)

            hole = pygame.Surface((region_rect.width, region_rect.height), pygame.SRCALPHA)
            hole.fill((0, 0, 0, 0))
            outside.blit(hole, region_rect.topleft, special_flags=pygame.BLEND_RGBA_MULT)

        inside_frames.append(inside)
        outside_frames.append(outside)

    return inside_frames, outside_frames

def load_item_sprite(path, scale=1):
    """
    Charge un PNG d'objet (pomme, potion...) et le prépare :
      1. rogne toute la zone transparente autour du dessin
         (get_bounding_rect donne la boîte du contenu visible) ;
      2. recentre le dessin dans un carré transparent, pour que
         le redimensionnement en carré (hotbar : 48x48) ne le
         déforme pas ;
      3. agrandit par 'scale' (pygame.transform.scale = plus proche
         voisin, donc le pixel art reste net).
    Doit être appelée APRÈS pygame.display.set_mode (convert_alpha).
    """
    image = pygame.image.load(path).convert_alpha()

    bounds = image.get_bounding_rect()
    cropped = image.subsurface(bounds)

    side = max(bounds.width, bounds.height)
    square = pygame.Surface((side, side), pygame.SRCALPHA)
    square.blit(cropped, cropped.get_rect(center=square.get_rect().center))

    if scale != 1:
        square = pygame.transform.scale(
            square, (int(side * scale), int(side * scale))
        )
    return square