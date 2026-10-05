import os
import math
import random
import pygame
from settings import *

_enabled = False
_muted = False
_sounds = {}          # nom -> liste de pygame.mixer.Sound (variantes)
_last_play = {}       # nom -> instant (ms) de la dernière lecture
_listener = (0, 0)    # position du joueur (pour le volume selon la distance)
_step_timer = 0

_music_current = None   # chemin de la musique en cours (None = aucune)
_music_failed = set()   # chemins qui n'ont pas pu être chargés (évite de réessayer en boucle)
_fade = 0.0             # 0 = muet, 1 = plein volume (fondu)
_duck = 1.0             # 1 = normal, MUSIC_DUCK_VOLUME = menu ouvert


# ============================================================
# INITIALISATION
# ============================================================
def init():
	"""À appeler UNE fois, après pygame.init() et set_mode."""
	global _enabled
	if not AUDIO_ENABLED:
		return
	try:
		if not pygame.mixer.get_init():
			pygame.mixer.init(44100, -16, 2, 512)
		pygame.mixer.set_num_channels(AUDIO_CHANNELS)
		_enabled = True
	except pygame.error as error:
		print(f"[AUDIO] mixer indisponible, jeu sans son : {error}")
		_enabled = False
		return
	_load_all()


def _find_variants(name):
	# Cherche name.ext, name_1.ext ... name_9.ext (wav, ogg, mp3)
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
				print(f"[AUDIO] fichier illisible {path} : {error}")
		if variants:
			_sounds[name] = variants
		else:
			missing.append(name)
	if missing:
		print(f"[AUDIO] sons sans fichier ({len(missing)}) : {', '.join(missing)}")


# ============================================================
# BRUITAGES
# ============================================================
def set_listener(position):
	"""Position du joueur : centre de la 'oreille' pour les sons spatialisés."""
	global _listener
	_listener = position


def play(name, source=None, volume=1.0):
	"""
	Joue le bruitage 'name'.
	  source : (x, y) monde -> le volume baisse avec la distance au
	           joueur ; au-delà de AUDIO_HEARING_RADIUS, rien n'est joué.
	  volume : coefficient supplémentaire (0 à 1).
	"""
	if not _enabled or _muted:
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
		distance = math.hypot(source[0] - _listener[0], source[1] - _listener[1])
		if distance >= AUDIO_HEARING_RADIUS:
			return
		level *= 1 - distance / AUDIO_HEARING_RADIUS
	if level <= 0.01:
		return

	channel = random.choice(variants).play()
	if channel is not None:        # None = plus de canal libre : on abandonne ce son
		channel.set_volume(min(1.0, level))
	_last_play[name] = now


def footsteps(moving, game_state):
	"""À appeler à chaque frame : joue un pas toutes les FOOTSTEP_INTERVAL frames."""
	global _step_timer
	if not moving:
		_step_timer = FOOTSTEP_INTERVAL // 2   # le 1er pas arrive vite après le départ
		return
	_step_timer += 1
	if _step_timer >= FOOTSTEP_INTERVAL:
		_step_timer = 0
		surface = {"house": "step_wood", "chapel": "step_stone"}.get(game_state, "step_grass")
		play(surface)


def toggle_mute():
	"""Coupe / rétablit tout le son (touche M)."""
	global _muted
	_muted = not _muted
	if _enabled and _muted:
		pygame.mixer.stop()


# ============================================================
# MUSIQUE
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
	À appeler UNE fois par frame. Machine à états du fondu :
	  - la musique voulue change  -> fondu sortant, puis on lance la nouvelle ;
	  - la musique voulue est déjà celle en cours -> fondu entrant ;
	  - menu_open -> le volume glisse vers MUSIC_DUCK_VOLUME.
	"""
	global _music_current, _fade, _duck
	if not _enabled:
		return

	wanted = _track_path(game_state)
	step = 1.0 / max(1, MUSIC_FADE_FRAMES)

	if wanted != _music_current:
		if _music_current is not None:
			_fade = max(0.0, _fade - step)       # fondu sortant
			if _fade > 0:
				_apply_music_volume()
				return
			pygame.mixer.music.stop()
			_music_current = None
		if wanted:
			try:
				pygame.mixer.music.load(wanted)
				pygame.mixer.music.play(-1)      # -1 = boucle infinie
				_music_current = wanted
				_fade = 0.0
			except pygame.error as error:
				print(f"[AUDIO] musique illisible {wanted} : {error}")
				_music_failed.add(wanted)
	else:
		_fade = min(1.0, _fade + step)           # fondu entrant

	target_duck = MUSIC_DUCK_VOLUME if menu_open else 1.0
	_duck += (target_duck - _duck) * 0.1         # glissement doux
	_apply_music_volume()


def _apply_music_volume():
	volume = 0.0 if _muted else MUSIC_VOLUME * _fade * _duck
	pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))