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
