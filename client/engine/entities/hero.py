from .base import AnimatedEntity, sprite_path

class Hero(AnimatedEntity):
    def __init__(self, pos=(80, 360)):
        animations = {
            "idle":   [sprite_path("hero_idle.png")],
            "attack": [sprite_path("hero_attack.png")],
            "damage": [sprite_path("hero_damage.png")],
        }
        super().__init__("Hero", max_hp=100, pos=pos, animations=animations, speed=200)

        # ── Sistema de mana e skills ──
        self.mana     = 0
        self.max_mana = 100
        self.escudo_ativo = False  # próximo erro não causa dano

    def ganhar_mana(self, quantidade=10):
        self.mana = min(self.max_mana, self.mana + quantidade)

    def usar_dica(self):
        """Elimina 2 opções erradas. Retorna True se ativou."""
        if self.mana >= 30:
            self.mana -= 30
            return True
        return False

    def usar_tempo_extra(self):
        """Adiciona 10s no timer. Retorna True se ativou."""
        if self.mana >= 20:
            self.mana -= 20
            return True
        return False

    def usar_escudo(self):
        """Ativa escudo: próximo erro não causa dano. Retorna True se ativou."""
        if self.mana >= 40 and not self.escudo_ativo:
            self.mana -= 40
            self.escudo_ativo = True
            return True
        return False