from viewer import TelaNome, TelaMenu

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
            pass  # self.tela_atual = TelaBatalha(...)
        elif proximo == "ranking":
            pass  # self.tela_atual = TelaRanking(...)
        elif proximo == "game_over":
            pass  # self.tela_atual = TelaGameOver(...)