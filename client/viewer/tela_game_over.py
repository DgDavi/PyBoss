import math
import pygame
from viewer.base import TelaBase, AMARELO, CINZA, VERMELHO

BRANCO  = (220, 220, 220)
LARANJA = (255, 140, 0)
VERDE   = (60, 200, 80)

class TelaGameOver(TelaBase):
    def __init__(self, tela, pontuacao=0, relatorio_ia="", stats=None):
        super().__init__(tela)
        self.pontuacao   = pontuacao
        self.relatorio_ia = relatorio_ia
        self.stats       = stats or {}

        self.fonte_titulo  = pygame.font.SysFont("arialblack", 60)
        self.fonte_grande  = pygame.font.SysFont("arialblack", 26)
        self.fonte_sub     = pygame.font.SysFont("consolas", 20)
        self.fonte_pequena = pygame.font.SysFont("consolas", 16)

    def handle_event(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                self.proximo = "menu"

    def update(self):
        pass

    def draw(self):
        tempo = pygame.time.get_ticks() / 1000
        self.desenhar_degradê()
        self.desenhar_grade(tempo)
        self._draw_titulo(tempo)
        self._draw_pontuacao()
        self._draw_painel_stats()
        self._draw_relatorio_ia()
        self._draw_instrucao(tempo)
        self.desenhar_borda()
        self.desenhar_scanlines()

    def _draw_titulo(self, tempo):
        pulso = 0.80 + 0.20 * math.sin(tempo * 4)
        cor   = tuple(int(c * pulso) for c in VERMELHO)
        txt   = self.fonte_titulo.render("GAME OVER", True, cor)
        self.tela.blit(txt, (self.largura // 2 - txt.get_width() // 2, 25))
        pygame.draw.line(
            self.tela, VERMELHO,
            (self.largura // 2 - 200, 95),
            (self.largura // 2 + 200, 95), 2
        )

    def _draw_pontuacao(self):
        txt = self.fonte_grande.render(
            f"PONTUAÇÃO FINAL:  {self.pontuacao} PTS", True, AMARELO)
        self.tela.blit(txt, (self.largura // 2 - txt.get_width() // 2, 110))

    def _draw_painel_stats(self):
        """Exibe bosses derrotados e temas em que o jogador errou."""
        bosses = self.stats.get("bosses", 0)
        temas_errados = self.stats.get("temas_errados", [])

        cx = self.largura // 2
        y  = 160

        # — Bosses derrotados —
        txt = self.fonte_sub.render(
            f"⚔  BOSSES DERROTADOS:  {bosses}", True, LARANJA)
        self.tela.blit(txt, (cx - txt.get_width() // 2, y))
        y += 34

        # — Temas com erro —
        if temas_errados:
            txt_label = self.fonte_sub.render("✗  TEMAS COM DIFICULDADE:", True, VERMELHO)
            self.tela.blit(txt_label, (cx - txt_label.get_width() // 2, y))
            y += 26

            for tema in temas_errados:
                txt_tema = self.fonte_pequena.render(
                    f"  • {tema.upper()}", True, BRANCO)
                self.tela.blit(txt_tema, (cx - txt_tema.get_width() // 2, y))
                y += 22
        else:
            txt_ok = self.fonte_sub.render("✓  SEM TEMAS PROBLEMÁTICOS!", True, VERDE)
            self.tela.blit(txt_ok, (cx - txt_ok.get_width() // 2, y))
            y += 30

        # Linha separadora antes do relatório
        pygame.draw.line(
            self.tela, CINZA,
            (cx - 200, y + 6),
            (cx + 200, y + 6), 1
        )
        self._y_relatorio = y + 18

    def _draw_relatorio_ia(self):
        txt_tit = self.fonte_sub.render("AVALIAÇÃO DO ORÁCULO GROQ:", True, AMARELO)
        self.tela.blit(txt_tit, (self.largura // 2 - txt_tit.get_width() // 2,
                                  self._y_relatorio))

        linhas = self.relatorio_ia.split('\n')
        y_pos  = self._y_relatorio + 30

        for linha in linhas:
            linha_limpa = linha.strip()
            if not linha_limpa:
                continue
            txt_linha = self.fonte_pequena.render(linha_limpa, True, BRANCO)
            self.tela.blit(txt_linha,
                           (self.largura // 2 - txt_linha.get_width() // 2, y_pos))
            y_pos += 26

    def _draw_instrucao(self, tempo):
        if int(tempo * 2) % 2 == 0:
            txt = self.fonte_pequena.render("► [R] VOLTAR AO MENU ◄", True, AMARELO)
            self.tela.blit(
                txt, (self.largura // 2 - txt.get_width() // 2, self.altura - 50))