import options


# Typewriter dialogue state. The text is TRANSLATED once when the
# dialogue starts, so the typewriter effect always shows the right
# language even while characters are still appearing.
text = ""
visible_chars = 0
timer = 0
finished = True
TEXT_SPEED = 2


def reset():
    global text, visible_chars, timer, finished
    text = ""
    visible_chars = 0
    timer = 0
    finished = True


def start(raw_text, speed=None):
    global text, visible_chars, timer, finished, TEXT_SPEED
    text = options.tr(raw_text)
    visible_chars = 0
    timer = 0
    finished = False
    TEXT_SPEED = 2 if speed is None else speed


def update():
    # Reveal one character every TEXT_SPEED frames until done.
    global visible_chars, timer, finished
    if finished:
        return
    timer += 1
    if timer >= TEXT_SPEED:
        timer = 0
        visible_chars += 1
        if visible_chars >= len(text):
            visible_chars = len(text)
            finished = True


def visible_text():
    return text[:visible_chars]


def full_text():
    return text


def is_finished():
    return finished


def skip():
    # Reveal everything at once (interaction key while talking).
    global visible_chars, finished
    visible_chars = len(text)
    finished = True