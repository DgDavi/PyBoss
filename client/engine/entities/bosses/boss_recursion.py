from .base import BossBase


class BossRecursion(BossBase):
	def __init__(self, pos=(520, 300)):
		super().__init__("Boss Recursion", "boss_recursion.png", max_hp=110, pos=pos)
