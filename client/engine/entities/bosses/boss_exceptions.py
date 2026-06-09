from .base import BossBase


class BossExceptions(BossBase):
	def __init__(self, pos=(520, 300)):
		super().__init__("Boss Exceptions", "boss_exceptions.png", max_hp=100, pos=pos)
