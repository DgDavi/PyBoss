from .base import BossBase


class BossLists(BossBase):
	def __init__(self, pos=(520, 300)):
		super().__init__("Boss Lists", "boss_lists.png", max_hp=85, pos=pos)
