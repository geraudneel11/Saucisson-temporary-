import pygame

dialogue_visible_chars = 0
dialogue_timer = 0
dialogue_finished = False

dialogue_text = ""

TEXT_SPEED = 2

def start_dialogue(text, speed=None):
    global dialogue_text
    global dialogue_visible_chars
    global dialogue_timer
    global dialogue_finished
    global TEXT_SPEED

    dialogue_text = text
    dialogue_visible_chars = 0
    dialogue_timer = 0
    dialogue_finished = False

    if speed is None:
        TEXT_SPEED = 2
    else:
        TEXT_SPEED = speed

def update_dialogue():
    global dialogue_visible_chars
    global dialogue_timer
    global dialogue_finished

    if dialogue_finished:
        return
    dialogue_timer += 1

    if dialogue_timer >= TEXT_SPEED:
        dialogue_timer = 0
        dialogue_visible_chars += 1

        if dialogue_visible_chars >= len(dialogue_text):
            dialogue_visible_chars = len(dialogue_text)
            dialogue_finished = True

def get_visible_text():
    return dialogue_text[:dialogue_visible_chars]

def is_finished():
    return dialogue_finished

def skip_dialogue():
    global dialogue_visible_chars
    global dialogue_finished

    dialogue_visible_chars = len(dialogue_text)
    dialogue_finished = True

def get_full_text():
    return dialogue_text

def reset():

    global dialogue_text
    global dialogue_visible_chars
    global dialogue_timer
    global dialogue_finished

    dialogue_text = ""
    dialogue_visible_chars = 0
    dialogue_timer = 0
    dialogue_finished = True