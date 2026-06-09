from .base import AnimatedEntity, sprite_path


class Hero(AnimatedEntity):
	def __init__(self, pos=(80, 360)):
		animations = {
			"idle": [sprite_path("hero_idle.png")],
			"attack": [sprite_path("hero_attack.png")],
			"damage": [sprite_path("hero_damage.png")],
		}
		super().__init__("Hero", max_hp=100, pos=pos, animations=animations, speed=200)
