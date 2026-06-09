from .base import BossBase


class BossDicts(BossBase):
	def __init__(self, pos=(520, 300)):
		super().__init__("Boss Dicts", "boss_dicts.png", max_hp=90, pos=pos)
