import os
import math
import random

import pygame
from settings import *

_enabled = False
_muted = False
_sounds = {}        # name -> list of pygame.mixer.Sound variants
_last_play = {}     # name -> ms tick of the last playback
_listener = (0, 0)  # player position (ear point for spatial volume)
_step_timer = 0

_music_current = None   # path of the track being played (None = none)
_music_failed = set()   # unloadable paths (never retry them in a loop)
_fade = 0.0             # 0 = silent, 1 = full volume (crossfade state)
_duck = 1.0             # 1 = normal, MUSIC_DUCK_VOLUME = menu open
_music_on = True        # SETTINGS menu: music on/off
_sfx_on = True          # SETTINGS menu: sound effects on/off


# ============================================================
# INITIALIZATION
# ============================================================
def init():
    """Call ONCE, after pygame.init() and set_mode."""
    global _enabled
    if not AUDIO_ENABLED:
        return
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(44100, -16, 2, 512)
        pygame.mixer.set_num_channels(AUDIO_CHANNELS)
        _enabled = True
    except pygame.error as error:
        print(f"[AUDIO] mixer unavailable, running silent: {error}")
        _enabled = False
        return
    _load_all()


def _find_variants(name):
    # Look for name.ext, name_1.ext ... name_9.ext (wav, ogg, mp3).
    paths = []
    for candidate in [name] + [f"{name}_{i}" for i in range(1, 10)]:
        for ext in (".wav", ".ogg", ".mp3"):
            path = os.path.join(AUDIO_SFX_DIR, candidate + ext)
            if os.path.exists(path):
                paths.append(path)
                break
    return paths


def _load_all():
    missing = []
    for name in SFX_CONFIG:
        variants = []
        for path in _find_variants(name):
            try:
                variants.append(pygame.mixer.Sound(path))
            except pygame.error as error:
                print(f"[AUDIO] unreadable file {path}: {error}")
        if variants:
            _sounds[name] = variants
        else:
            missing.append(name)
    if missing:
        print(f"[AUDIO] sounds without file ({len(missing)}): "
              f"{', '.join(missing)}")


# ============================================================
# SOUND EFFECTS
# ============================================================
def set_listener(position):
    """Player position: the 'ear' point used for spatial volume."""
    global _listener
    _listener = position


def play(name, source=None, volume=1.0):
    """
    Play the sound effect 'name'.
      source: (x, y) world position -> volume falls off with the
              distance to the player; beyond AUDIO_HEARING_RADIUS
              nothing is played.
      volume: extra multiplier (0 to 1).
    """
    if not _enabled or _muted or not _sfx_on:
        return
    variants = _sounds.get(name)
    if not variants:
        return

    config = SFX_CONFIG.get(name, {})
    now = pygame.time.get_ticks()
    cooldown = config.get("cooldown", 0)
    if cooldown and now - _last_play.get(name, -999999) < cooldown:
        return

    level = SFX_MASTER_VOLUME * config.get("volume", 1.0) * volume
    if source is not None:
        distance = math.hypot(source[0] - _listener[0],
                              source[1] - _listener[1])
        if distance >= AUDIO_HEARING_RADIUS:
            return
        level *= 1 - distance / AUDIO_HEARING_RADIUS
    if level <= 0.01:
        return

    channel = random.choice(variants).play()
    if channel is not None:
        # None = no free channel: silently drop this sound.
        channel.set_volume(min(1.0, level))
    _last_play[name] = now


def footsteps(moving, game_state):
    """Call every frame: plays one step every FOOTSTEP_INTERVAL frames."""
    global _step_timer
    if not moving:
        _step_timer = FOOTSTEP_INTERVAL // 2
        # First step comes quickly after starting to walk.
        return
    _step_timer += 1
    if _step_timer >= FOOTSTEP_INTERVAL:
        _step_timer = 0
        surface = {"house": "step_wood", "chapel": "step_stone"}.get(
            game_state, "step_grass")
        play(surface)


def set_music(active):
    """Enable/disable MUSIC only (SETTINGS menu)."""
    global _music_on
    _music_on = bool(active)
    _apply_music_volume()


def set_sfx(active):
    """Enable/disable SOUND EFFECTS only (SETTINGS menu)."""
    global _sfx_on
    _sfx_on = bool(active)


def toggle_mute():
    """Mute / unmute everything (M key)."""
    global _muted
    _muted = not _muted
    if _enabled and _muted:
        pygame.mixer.stop()


# ============================================================
# MUSIC
# ============================================================
def _track_path(game_state):
    filename = MUSIC_TRACKS.get(game_state)
    if not filename:
        return None
    path = os.path.join(AUDIO_MUSIC_DIR, filename)
    if path in _music_failed or not os.path.exists(path):
        return None
    return path


def update_music(game_state, menu_open=False):
    """
    Call ONCE per frame. Fade state machine:
      - wanted track changed      -> fade out, then start the new one;
      - wanted track already playing -> fade in;
      - menu_open -> volume slides toward MUSIC_DUCK_VOLUME.
    """
    global _music_current, _fade, _duck
    if not _enabled:
        return

    wanted = _track_path(game_state)
    step = 1.0 / max(1, MUSIC_FADE_FRAMES)

    if wanted != _music_current:
        if _music_current is not None:
            _fade = max(0.0, _fade - step)   # fade out
            if _fade > 0:
                _apply_music_volume()
                return
            pygame.mixer.music.stop()
            _music_current = None
        if wanted:
            try:
                pygame.mixer.music.load(wanted)
                pygame.mixer.music.play(-1)  # -1 = loop forever
                _music_current = wanted
                _fade = 0.0
            except pygame.error as error:
                print(f"[AUDIO] unreadable music {wanted}: {error}")
                _music_failed.add(wanted)
    else:
        _fade = min(1.0, _fade + step)       # fade in

    target_duck = MUSIC_DUCK_VOLUME if menu_open else 1.0
    _duck += (target_duck - _duck) * 0.1     # smooth slide
    _apply_music_volume()


def _apply_music_volume():
    volume = MUSIC_VOLUME * _fade * _duck
    if _muted or not _music_on:
        volume = 0.0
    pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))