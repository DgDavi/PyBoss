from viewer import TelaNome, TelaMenu, TelaBatalha, TelaTransicao


class GameManager:

    def __init__(self, tela):
        self.tela         = tela
        self.nome_jogador = ""
        self.tela_atual   = TelaNome(tela)

    def handle_event(self, evento):
        self.tela_atual.handle_event(evento)

    def update(self):
        self.tela_atual.update()
        self._verificar_transicao()

    def draw(self):
        self.tela_atual.draw()

    def _verificar_transicao(self):
        proximo = self.tela_atual.proximo
        if not proximo:
            return

        if isinstance(self.tela_atual, TelaNome):
            self.nome_jogador = self.tela_atual.nome

        if proximo == "menu":
            self.tela_atual = TelaMenu(self.tela, self.nome_jogador)

        elif proximo == "batalha":
            # Vindo da TelaTransicao — aproveita o boss já gerado
            if isinstance(self.tela_atual, TelaTransicao):
                nova_tela = TelaBatalha(self.tela, self.nome_jogador)
                nova_tela.combat.boss_data = self.tela_atual.proximo_boss
                nova_tela.combat.carregar_boss_dos_dados()
                self.tela_atual = nova_tela
            else:
                # Vindo do menu — começa do zero
                self.tela_atual = TelaBatalha(self.tela, self.nome_jogador)

        elif proximo == "transicao":
            c = self.tela_atual.combat
            self.tela_atual = TelaTransicao(
                tela         = self.tela,
                boss_atual   = c.boss_anterior,
                proximo_boss = c.proximo_boss_data,
                nivel_atual  = c.nivel,
                stats        = c.get_stats_finais(),
            )

        elif proximo == "ranking":
            pass  # self.tela_atual = TelaRanking(self.tela)

        elif proximo == "game_over":
            pass  # self.tela_atual = TelaGameOver(self.tela)