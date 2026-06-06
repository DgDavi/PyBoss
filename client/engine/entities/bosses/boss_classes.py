from .base import BossBase


class BossClasses(BossBase):
	def __init__(self, pos=(520, 300)):
		super().__init__("Boss Classes", "boss_classes.png", max_hp=90, pos=pos)
