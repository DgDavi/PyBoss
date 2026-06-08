# client/viewer/tela_game_over.py

import math
import pygame
from viewer.base import TelaBase, AMARELO, CINZA, VERMELHO

BRANCO = (220, 220, 220)


class TelaGameOver(TelaBase):

    def __init__(self, tela, pontuacao=0):
        super().__init__(tela)
        self.pontuacao     = pontuacao
        self.fonte_titulo  = pygame.font.SysFont("arialblack", 60)
        self.fonte_grande  = pygame.font.SysFont("arialblack", 26)
        self.fonte_pequena = pygame.font.SysFont("consolas",   16)

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
        self._draw_instrucao(tempo)
        self.desenhar_borda()
        self.desenhar_scanlines()

    def _draw_titulo(self, tempo):
        pulso = 0.80 + 0.20 * math.sin(tempo * 4)
        cor   = tuple(int(c * pulso) for c in VERMELHO)
        txt   = self.fonte_titulo.render("GAME OVER", True, cor)
        self.tela.blit(txt, (self.largura // 2 - txt.get_width() // 2, 28))
        pygame.draw.line(
            self.tela, VERMELHO,
            (self.largura // 2 - 200, 100),
            (self.largura // 2 + 200, 100), 2
        )

    def _draw_pontuacao(self):
        txt = self.fonte_grande.render(
            f"PONTUAÇÃO FINAL:  {self.pontuacao} PTS", True, AMARELO)
        self.tela.blit(txt, (self.largura // 2 - txt.get_width() // 2, 114))

        subtitulo = self.fonte_pequena.render(
            "SUA JORNADA CHEGOU AO FIM...", True, CINZA)
        self.tela.blit(subtitulo,
                       (self.largura // 2 - subtitulo.get_width() // 2, 160))

    def _draw_instrucao(self, tempo):
        if int(tempo * 2) % 2 == 0:
            txt = self.fonte_pequena.render(
                "► [R] VOLTAR AO MENU ◄", True, AMARELO)
            self.tela.blit(
                txt, (self.largura // 2 - txt.get_width() // 2, self.altura - 60))