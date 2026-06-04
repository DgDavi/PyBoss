from .base import BossBase


class BossLoops(BossBase):
	def __init__(self, pos=(520, 300)):
		super().__init__("Boss Loops", "boss_loops.png", max_hp=95, pos=pos)
