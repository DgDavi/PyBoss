from ..base import Entity, sprite_path

class BossBase(Entity):
	def __init__(self, name, sprite_filename, max_hp, pos=(520, 300)):
		super().__init__(name, max_hp, pos, sprite_path(sprite_filename))
