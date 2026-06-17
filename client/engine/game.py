from viewer import TelaNome, TelaMenu, TelaBatalha, TelaTransicao, TelaGameOver
from viewer.tela_rank import TelaRanking


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

    # ─────────────────────────────────────
    # TRANSIÇÕES
    # ─────────────────────────────────────

    def _verificar_transicao(self):
        proximo = self.tela_atual.proximo
        if not proximo:
            return

        # Captura nome antes de trocar de tela
        if isinstance(self.tela_atual, TelaNome):
            self.nome_jogador = self.tela_atual.nome

        if proximo == "menu":
            self.tela_atual = TelaMenu(self.tela, self.nome_jogador)

        elif proximo == "batalha":
            if isinstance(self.tela_atual, TelaTransicao):
                # Vindo da TelaTransicao — aproveita o boss já gerado
                nova_tela = TelaBatalha(self.tela, self.nome_jogador)
                cs = nova_tela.combat_state
                cs.boss_data = self.tela_atual.proximo_boss
                cs.nivel = self.tela_atual.nivel_atual
                cs.carregar_boss_dos_dados()
                # Reinicia a fase de apresentação para o novo boss
                from engine.combat import TIMER_APRESENTACAO
                cs.fase = "apresentando"
                cs.apresentacao_timer = TIMER_APRESENTACAO
                self.tela_atual = nova_tela
            else:
                # Vindo do menu — começa do zero
                self.tela_atual = TelaBatalha(self.tela, self.nome_jogador)

        elif proximo == "transicao":
            cs = self.tela_atual.combat_state
            self.tela_atual = TelaTransicao(
                tela = self.tela,
                boss_atual = cs.boss_anterior,
                proximo_boss = cs.proximo_boss_data,
                nivel_atual = cs.nivel,
                stats = cs.get_stats_finais(),
            )

        elif proximo == "ranking":
            self.tela_atual = TelaRanking(self.tela)

        elif proximo == "game_over":
            cs = self.tela_atual.combat_state
            pontuacao = cs.maior_combo * 10 + cs.nivel * 50

            # salvar no banco
            from backend.database import salvar_pontuacao
            try:
                salvar_pontuacao(self.nome_jogador if self.nome_jogador else "Alquimista", pontuacao)
            except Exception as e:
                print(f"[SQLITE] Erro ao salvar pontuação: {e}")

            # stats sempre definido antes do try
            stats_reais = cs.get_stats_finais()

            # gerar relatório via IA
            from backend.ai_service import gerar_relatorio
            try:
                relatorio_ia = gerar_relatorio(stats_reais)
            except Exception as e:
                print(f"[GROQ] Erro ao gerar relatório: {e}")
                relatorio_ia = "Seus erros foram guardados. Continue praticando para superar o próximo Boss!"

            self.tela_atual = TelaGameOver(self.tela, pontuacao, relatorio_ia, stats_reais)