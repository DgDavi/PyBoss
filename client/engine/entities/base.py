import os
import pygame


SPRITES_DIR = os.path.abspath(
	os.path.join(os.path.dirname(__file__), "..", "..", "assets", "pyboss_sprites")
)


def sprite_path(filename):
	return os.path.join(SPRITES_DIR, filename)


class Entity:
	def __init__(self, name, max_hp, pos, sprite_path_value, speed=0):
		self.name = name
		self.max_hp = max_hp
		self.hp = max_hp
		self.speed = speed

		self.sprite = pygame.image.load(sprite_path_value).convert_alpha()
		self.rect = self.sprite.get_rect(topleft=pos)

	def take_damage(self, amount):
		self.hp = max(0, self.hp - amount)

	def is_dead(self):
		return self.hp <= 0

	def draw(self, surface):
		surface.blit(self.sprite, self.rect)


class AnimatedEntity(Entity):
	def __init__(self, name, max_hp, pos, animations, speed=0):
		first_sprite = next(iter(animations.values()))[0]
		super().__init__(name, max_hp, pos, first_sprite, speed=speed)
		self.animations = {
			key: [pygame.image.load(path).convert_alpha() for path in paths]
			for key, paths in animations.items()
		}
		self.state = "idle"
		self.frame = 0
		self.frame_timer = 0.0
		self.frame_delay = 0.12

	def set_state(self, state):
		if state != self.state and state in self.animations:
			self.state = state
			self.frame = 0
			self.frame_timer = 0.0
			self.sprite = self.animations[self.state][self.frame]

	def update(self, dt):
		frames = self.animations.get(self.state)
		if not frames:
			return
		self.frame_timer += dt
		if self.frame_timer >= self.frame_delay:
			self.frame_timer = 0.0
			self.frame = (self.frame + 1) % len(frames)
			self.sprite = frames[self.frame]

	def sprite_path(filename):
		caminho = os.path.join(SPRITES_DIR, filename)
		print(f"[sprite_path] buscando: {caminho}")
		print(f"[sprite_path] existe: {os.path.exists(caminho)}")
		return caminho
