import pygame
import random
import math
from settings import * 

from pygame import surface

class Player:

	def __init__(self, x, y, width, height):

		self.rect = pygame.Rect(x, y, width, height)
		self.hp = 100
		self.max_hp = 100
		self.speed = 14
		self.hitbox = pygame.Rect(0, 0, 70, 70)
		self.hitbox.center = self.rect.center
		self.max_targets = 5
		self.state = "idle"
		self.damage_timer = 0
		self.current_frame = 0
		self.frame_timer = 0
		self.current_animation = None
		self.direction = "down"
		self.invicible_timer = 0
		self.coins = 0
		self.selected_slot = 0
		self.met_healer = False
		self.met_merchant = False

		self.knockback_x = 0
		self.knockback_y = 0

		self.inventory = [
    	{"item": None, "quantity": 0},
    	{"item": None, "quantity": 0},
    	{"item": None, "quantity": 0},
		]

	def update_hitbox(self):
		self.hitbox.center = self.rect.center

	def apply_knockback(self):
		self.rect.x += self.knockback_x
		self.rect.y += self.knockback_y
		self.update_hitbox()
		self.knockback_x *= 0.7
		self.knockback_y *= 0.7

	def clamp_to_map(self, map_width, map_height):
		if self.rect.left < 0:
			self.rect.left = 0
		if self.rect.right > map_width:
			self.rect.right = map_width
		if self.rect.top < 0:
			self.rect.top = 0
		if self.rect.bottom > map_height:
			self.rect.bottom = map_height
		self.update_hitbox()

	def take_damage(self, damage, enemy):
		if self.invicible_timer <= 0:
			self.hp -= damage

			self.state = "hurt"
			self.current_frame = 0
			self.frame_timer = 0

			self.damage_timer = 36

			dx = self.rect.centerx - enemy.rect.centerx
			dy = self.rect.centery - enemy.rect.centery

			distance = max(1, (dx**2 + dy**2) ** 0.5)

			self.knockback_x = dx / distance * 20
			self.knockback_y = dy / distance * 20

			if self.hp < 0:
				self.hp = 0

			self.invicible_timer = 40
	def add_item_to_inventory(self, item):

	# Chercher une pile existante
		for slot in self.inventory:

			if slot["item"] is not None:

				if slot["item"].name == item.name:

					slot["quantity"] += 1
					return True

	# Sinon créer une nouvelle pile
		for slot in self.inventory:

			if slot["item"] is None:

				slot["item"] = item.copy()
				slot["quantity"] = 1
				return True

		return False

class Enemy:

	@classmethod
	def from_orc_data(cls, x, y, orc_data):
		return cls(
			x,
			y,
			orc_data["walk"],
			orc_data["hurt"],
			orc_data["death"],
			orc_data["attack"],
			orc_data["idle"]
		)

	def __init__(self, x, y, orc_animations, orc_hurt_animations, orc_death_animations, orc_attack_animations, orc_idle_animations):

		self.rect = pygame.Rect(x, y, 64, 64)
		self.hitbox = pygame.Rect(0, 0, 40, 40)
		self.hitbox.center = self.rect.center

		self.hp = 20
		self.max_hp = 20
		self.damage = 5

		self.speedx = 4
		self.speedy = 4
		self.attack_range = 75
		self.attack_cooldown = 0
		self.attack_hit_done = False
		self.attack_hitbox = None
		self.hit_this_attack = False

		self.animations = orc_animations
		self.hurt_animations = orc_hurt_animations
		self.death_animations = orc_death_animations
		self.attack_animations = orc_attack_animations
		self.idle_animations = orc_idle_animations

		self.direction = "down"
		self.state = "walk"
		self.current_animation = orc_animations["down"]
		self.current_frame = 0
		self.frame_timer = 0
		self.damage_timer = 0
		self.health_bar_timer = 0

		self.knockback_x = 0
		self.knockback_y = 0

		self.dead = False
		self.dead_finished = False
		self.dead_timer = 0

	def take_damage(self, damage, player):
		if self.dead:
			return

		self.hp = max(self.hp - damage, 0)
		self.health_bar_timer = 120
		self.attack_cooldown = 120
		self.state = "hurt"
		self.current_frame = 0
		self.frame_timer = 0
		self.damage_timer = len(self.hurt_animations[self.direction]) * 6

		if self.hp == 0:
			self.dead = True
			self.state = "dead"
			self.current_frame = 0
			self.frame_timer = 0
			self.coin_dropped = True

		self._apply_knockback_from(player)

	def draw_health_bar(self, surface, sprite_rect):
		if self.health_bar_timer <= 0:
			return

		health_ratio = self.hp / self.max_hp
		bar_width = 48
		bar_height = 6
		bar_x = sprite_rect.centerx - bar_width // 2
		bar_y = sprite_rect.top - 10
		pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
		pygame.draw.rect(surface, (0, 220, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))

	def update(self, player):
		self._apply_knockback()

		if self.dead:
			self._update_dead()
			return

		self._update_direction(player)

		if self.state == "hurt":
			self._update_hurt()
		elif self.state == "attack":
			self._update_attack(player)
		else:
			self._update_movement(player)

		self._advance_frame()
		self._update_cooldowns()

	def _apply_knockback_from(self, player):
		dx = self.rect.centerx - player.rect.centerx
		dy = self.rect.centery - player.rect.centery
		distance = max(1, math.hypot(dx, dy))
		self.knockback_x = dx / distance * 20
		self.knockback_y = dy / distance * 20

	def _apply_knockback(self):
		self.rect.x += self.knockback_x
		self.rect.y += self.knockback_y
		self.knockback_x *= 0.7
		self.knockback_y *= 0.7
		self.hitbox.center = self.rect.center

	def _update_direction(self, player):
		dx = player.rect.centerx - self.rect.centerx
		dy = player.rect.centery - self.rect.centery
		if abs(dx) > abs(dy):
			self.direction = "right" if dx > 0 else "left"
		else:
			self.direction = "down" if dy > 0 else "up"

	def _set_animation(self, animation):
		self.current_animation = animation
		self.current_frame = min(self.current_frame, len(animation) - 1)

	def _update_dead(self):
		self._set_animation(self.death_animations[self.direction])
		self.frame_timer += 1
		if self.frame_timer >= 6:
			self.frame_timer = 0
			if self.current_frame < len(self.current_animation) - 1:
				self.current_frame += 1
		if self.current_frame == len(self.current_animation) - 1:
			self.dead_timer += 1
		if self.dead_timer >= 30:
			self.dead_finished = True

	def _update_hurt(self):
		self._set_animation(self.hurt_animations[self.direction])
		self.damage_timer -= 1
		if self.damage_timer <= 0:
			self.state = "walk"

	def _update_attack(self, player):
		self._set_animation(self.attack_animations[self.direction])
		if 3 <= self.current_frame <= 5 and not self.attack_hit_done:
			self._create_attack_hitbox()
			if self.attack_hitbox.colliderect(player.hitbox):
				player.take_damage(self.damage, self)
				self.attack_hit_done = True

	def _update_movement(self, player):
		dx = player.rect.centerx - self.rect.centerx
		dy = player.rect.centery - self.rect.centery
		distance = math.hypot(dx, dy)

		if distance <= self.attack_range and self.attack_cooldown <= 0:
			self.state = "attack"
			self.current_frame = 0
			self.frame_timer = 0
			self.attack_hit_done = False
		elif distance <= 45:
			self.state = "idle"
		else:
			self.state = "walk"

		if self.state == "walk":
			self._set_animation(self.animations[self.direction])
			self._move_towards(player, speed=math.hypot(self.speedx, self.speedy))
		elif self.state == "idle":
			self._set_animation(self.idle_animations[self.direction])

		self.hitbox.center = self.rect.center

	def _move_towards(self, player, speed):
		if self.rect.centerx < player.rect.centerx:
			self.rect.x += self.speedx
		elif self.rect.centerx > player.rect.centerx:
			self.rect.x -= self.speedx
		if self.rect.centery < player.rect.centery:
			self.rect.y += self.speedy
		elif self.rect.centery > player.rect.centery:
			self.rect.y -= self.speedy

		self.hitbox.center = self.rect.center

	def _create_attack_hitbox(self):
		if self.direction == "right":
			self.attack_hitbox = pygame.Rect(self.rect.right - 10, self.rect.centery - 40, 90, 80)
		elif self.direction == "left":
			self.attack_hitbox = pygame.Rect(self.rect.left - 80, self.rect.centery - 40, 90, 80)
		elif self.direction == "up":
			self.attack_hitbox = pygame.Rect(self.rect.centerx - 40, self.rect.top - 80, 80, 90)
		else:
			self.attack_hitbox = pygame.Rect(self.rect.centerx - 40, self.rect.bottom - 10, 80, 90)

	def _advance_frame(self):
		self.frame_timer += 1
		if self.frame_timer >= 6:
			self.frame_timer = 0
			self.current_frame += 1
			if self.current_frame >= len(self.current_animation):
				self.current_frame = 0
				if self.state == "attack":
					self.state = "walk"
					self.attack_cooldown = 120
					self.attack_hit_done = False

	def _update_cooldowns(self):
		if self.attack_cooldown > 0:
			self.attack_cooldown -= 1
		if self.health_bar_timer > 0:
			self.health_bar_timer -= 1

class Coin:

	def __init__(self, x, y, animation):
		self.animation = animation
		self.current_frame = 0
		self.frame_timer = 0
		self.rect = pygame.Rect(x, y, 24, 24)
		self.rect.center = (x, y)
		self.auto_collect = False
		self.value = 1

	def update(self):
		self.frame_timer += 1
		if self.frame_timer >= 6:
			self.frame_timer = 0
			self.current_frame += 1
			if self.current_frame >= len(self.animation):
				self.current_frame = 0

	def draw(self, surface):
		sprite = self.animation[self.current_frame]
		rect = sprite.get_rect(centerx=self.rect.centerx, centery=self.rect.centery + 25)
		surface.blit(sprite, rect)

	def move_towards_player(self, player):
		dx = player.rect.centerx - self.rect.centerx
		dy = player.rect.centery - self.rect.centery
		distance = math.hypot(dx, dy)
		if distance < 200 and distance > 1:
			speed = 8
			self.rect.x += dx / distance * speed
			self.rect.y += dy / distance * speed

	def move_auto(self, player):
		dx = player.rect.centerx - self.rect.centerx
		dy = player.rect.centery - self.rect.centery
		distance = math.hypot(dx, dy)
		if distance > 1:
			speed = 12
			self.rect.x += dx / distance * speed
			self.rect.y += dy / distance * speed

class NPC:

	def __init__(
		self,
		x, y,
		idle_animation,
		walk_animations,
		npc_type,
		hitbox_width=40,
		hitbox_height=40,
		hitbox_for_players_width=30,
		hitbox_for_players_height=5,
		hitbox_offset_x=0,
		hitbox_offset_y=0,
		hitbox_for_furniture_width=30,
		hitbox_for_furniture_height=5,
		movement_points=None,
		stop_point_indices=None,
		stop_look_directions=None,
		speed=1.5,
		stop_duration_min_seconds=2,
		stop_duration_max_seconds=10,
		turn_pause_min_seconds=2,
		turn_pause_max_seconds=4
	):

		self.rect = pygame.Rect(x, y, 64, 64)

		self.idle_animation = idle_animation
		self.walk_animations = walk_animations
		self.current_animation = idle_animation

		self.current_frame = 0
		self.frame_timer = 0

		self.direction = "down"

		self.type = npc_type

		self.interaction_rect = pygame.Rect(
			self.rect.x - 30,
			self.rect.y - 30,
			self.rect.width + 60,
			self.rect.height + 60
		)

		self.hitbox_offset_x = hitbox_offset_x
		self.hitbox_offset_y = hitbox_offset_y

		self.hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
		self.hitbox_for_players = pygame.Rect(0, 0, hitbox_for_players_width, hitbox_for_players_height)

		# Hitbox dédiée aux collisions NPC-vs-meubles/murs pendant le
		# déplacement, à la même taille que celle du joueur (70x70).
		# self.hitbox reste inchangée et disponible pour un usage futur.
		self.hitbox_for_furniture = pygame.Rect(0, 0, hitbox_for_furniture_width, hitbox_for_furniture_height)

		self._update_hitbox_position()

		# --- Circuit : movement_points est la liste ORDONNÉE de tous les
		# points (passage + arrêt). stop_point_indices = index des points
		# d'ARRÊT (éligibles au tirage au sort) ; les autres index ne sont
		# que des points de passage, traversés sans pause.
		self.movement_points = movement_points or []
		if stop_point_indices is None:
			self.stop_point_indices = list(range(len(self.movement_points)))
		else:
			self.stop_point_indices = stop_point_indices

		# Direction à regarder pour un point d'arrêt donné, ex :
		# {2: "up"} -> en s'arrêtant au point d'index 2, le NPC regarde
		# vers le haut. Un index absent = pas de consigne (idle générique).
		self.stop_look_directions = stop_look_directions or {}

		self.speed = speed
		self.stop_duration_min = int(stop_duration_min_seconds * FPS_MAX)
		self.stop_duration_max = int(stop_duration_max_seconds * FPS_MAX)
		self.turn_pause_min = int(turn_pause_min_seconds * FPS_MAX)
		self.turn_pause_max = int(turn_pause_max_seconds * FPS_MAX)

		self.path_index = 0
		self.path_direction = 1
		self.target_stop_index = None
		self.resting_at_index = None
		self.current_target = self.movement_points[0] if self.movement_points else None

		self.state = "idle"              # "idle" (à l'arrêt) ou "moving"
		self.idle_timer = random.randint(60, 180)  # attente avant le tout premier départ
		self.stuck_timer = 0
		self.conversation_target = None
		self.face_target_point = None
		self.approach_stuck_timer = 0
		self.talk_delay_timer = 0

	def _update_hitbox_position(self):
		self.hitbox.center = self.rect.center
		self.hitbox_for_players.center = self.rect.center
		self.hitbox_for_players.x += self.hitbox_offset_x
		self.hitbox_for_players.y += self.hitbox_offset_y
		self.hitbox_for_furniture.center = self.rect.center

	def _pick_new_stop_target(self):
		if not self.stop_point_indices:
			return
		candidates = [i for i in self.stop_point_indices if i != self.path_index]
		if not candidates:
			candidates = self.stop_point_indices
		self.target_stop_index = random.choice(candidates)

		new_direction = 1 if self.target_stop_index > self.path_index else -1
		reversing = new_direction != self.path_direction
		self.path_direction = new_direction
		self.resting_at_index = None

		if reversing:
			# Elle change de sens : petite pause supplémentaire avant de
			# repartir, quel que soit le type de point (arrêt ou passage)
			# où elle se trouve actuellement. target_stop_index reste
			# fixé : au prochain réveil, elle partira directement,
			# sans retirer une nouvelle destination.
			self.idle_timer = random.randint(self.turn_pause_min, self.turn_pause_max)
		else:
			self.state = "moving"

	def _advance_to_next_point(self):
		if len(self.movement_points) <= 1:
			return
		self.path_index += self.path_direction
		self.path_index = max(0, min(self.path_index, len(self.movement_points) - 1))
		self.current_target = self.movement_points[self.path_index]

		if self.path_index == self.target_stop_index:
			# Point d'arrêt atteint : pause aléatoire (2-10s par défaut)
			self.state = "idle"
			self.idle_timer = random.randint(self.stop_duration_min, self.stop_duration_max)
			self.resting_at_index = self.target_stop_index
			look_direction = self.stop_look_directions.get(self.target_stop_index)
			if look_direction:
				self.direction = look_direction
			self.target_stop_index = None

	def _direction_towards(self, target_x, target_y):
		dx = target_x - self.rect.centerx
		dy = target_y - self.rect.centery
		if abs(dx) > abs(dy):
			return "right" if dx > 0 else "left"
		else:
			return "down" if dy > 0 else "up"

	def _update_direction_towards_target(self):
		target_x, target_y = self.current_target
		self.direction = self._direction_towards(target_x, target_y)
		
	def begin_conversation(self, player):
		self.conversation_target = self._compute_approach_target(player)
		self.face_target_point = (player.hitbox.centerx, player.hitbox.centery)
		self.state = "approaching"
		self.approach_stuck_timer = 0

	def begin_conversation(self, player):
		self.direction = self._direction_towards(player.hitbox.centerx, player.hitbox.centery)
		self.state = "talking"
		self.talk_delay_timer = 20  # ~1/3 de seconde à 60 FPS, pour laisser voir l'orientation
		
	def end_conversation(self):
		self.state = "idle"
		self.idle_timer = random.randint(30, 90)  # petite pause avant de reprendre le circuit

	def _set_animation(self, animation):
		self.current_animation = animation
		self.current_frame = min(self.current_frame, len(animation) - 1)

	def _resolve_movement_collisions(self, colliders, old_pos):
		self._update_hitbox_position()
		for collider in colliders:
			if self.hitbox_for_furniture.colliderect(collider):
				self.rect = old_pos
				self._update_hitbox_position()
				return True
		return False

	def _move_towards_target(self, colliders):
		self._update_direction_towards_target()

		target_x, target_y = self.current_target
		dx = target_x - self.rect.centerx
		dy = target_y - self.rect.centery
		distance = math.hypot(dx, dy)

		if distance <= 1:
			self.stuck_timer = 0
			self._advance_to_next_point()
			return

		old_pos = self.rect.copy()

		step = min(self.speed, distance)
		self.rect.x += dx / distance * step
		self.rect.y += dy / distance * step

		blocked = self._resolve_movement_collisions(colliders, old_pos)

		if blocked:
			self.stuck_timer += 1
			if self.stuck_timer >= 30:
				self.stuck_timer = 0
				self._advance_to_next_point()
		else:
			self.stuck_timer = 0

	def update(self, colliders=None, player=None):

		if colliders is not None:
			if self.state == "idle":
				if self.movement_points:
					self.idle_timer -= 1
					if self.idle_timer <= 0:
						if self.target_stop_index is None:
							self._pick_new_stop_target()
						else:
							# Destination déjà choisie : la pause de
							# demi-tour vient de se terminer, on part.
							self.state = "moving"
							self.is_turn_pause = False
			elif self.state == "moving":
				self._move_towards_target(colliders)
			elif self.state == "talking":
				# NPC totalement figé, seul le délai avant ouverture du
				# dialogue continue de décompter.
				if self.talk_delay_timer > 0:
					self.talk_delay_timer -= 1
			# "talking" : aucune mise à jour de position, NPC totalement figé.

		frozen_pose = False

		if self.state == "moving":
			self._set_animation(self.walk_animations[self.direction])
		elif self.state == "talking":
			# Idle normal, animé, pendant que le NPC est orienté vers le
			# joueur (l'orientation elle-même est gérée séparément via
			# self.direction, fixée dans begin_conversation).
			self._set_animation(self.idle_animation)
		elif self.resting_at_index is not None and self.resting_at_index in self.stop_look_directions:
			self.current_animation = self.walk_animations[self.direction]
			self.current_frame = 0
			frozen_pose = True
		else:
			self._set_animation(self.idle_animation)

		if not frozen_pose:
			self.frame_timer += 1

			if self.frame_timer >= 8:

				self.frame_timer = 0

				self.current_frame += 1

				if self.current_frame >= len(self.current_animation):
					self.current_frame = 0

		self.interaction_rect.center = self.rect.center
		self._update_hitbox_position()

	def draw(self, surface):

		sprite = self.current_animation[self.current_frame]

		sprite_rect = sprite.get_rect(
			midbottom=self.rect.midbottom
		)

		surface.blit(sprite, sprite_rect)
		
class Potion:

	def __init__(self, sprite):
		self.name = "Potion de soin"
		self.price = 15
		self.heal = 30

		self.stock = HEAL_POTION_QUANTITY          # quantité chez le marchand
		self.max_stock = HEAL_POTION_MAX_QUANTITY

		self.sprite = sprite     # chargé plus tard
		self.rect = None         # utilisé pour le clic
	def copy(self):
		return Potion(self.sprite)

	def use(self, player):
		player.hp = min(player.max_hp, player.hp + self.heal)

class Tree:

    def __init__(self, x, y, frames, index=None,
                 hitbox_width=24, hitbox_height=18,
                 hitbox_offset_x=0, hitbox_offset_y=0,
                 sway_min_seconds=5, sway_max_seconds=20, sway_frame_speed=6):

        self.frames = frames
        self.frame = 0
        self.frame_timer = 0
        self.playing = False

        self.image = self.frames[0]

        self.rect = self.image.get_rect(midbottom=(x, y))

        self.index = index

        self.hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.hitbox_offset_x = hitbox_offset_x
        self.hitbox_offset_y = hitbox_offset_y

        self.hitbox.midbottom = self.rect.midbottom
        self.hitbox.x += self.hitbox_offset_x
        self.hitbox.y += self.hitbox_offset_y

        self.sway_min_frames = int(sway_min_seconds * FPS_MAX)
        self.sway_max_frames = int(sway_max_seconds * FPS_MAX)
        self.sway_frame_speed = sway_frame_speed

        # Décalé aléatoirement dès la création : les arbres ne se
        # balancent jamais tous en même temps.
        self.animation_timer = random.randint(self.sway_min_frames, self.sway_max_frames)

    def update(self):
        if self.playing:
            self.frame_timer += 1
            if self.frame_timer >= self.sway_frame_speed:
                self.frame_timer = 0
                self.frame += 1

                if self.frame >= len(self.frames):
                    self.frame = 0
                    self.playing = False
                    self.animation_timer = random.randint(self.sway_min_frames, self.sway_max_frames)

            self.image = self.frames[self.frame]
        else:
            self.animation_timer -= 1
            if self.animation_timer <= 0:
                self.playing = True
                self.frame = 0
                self.frame_timer = 0