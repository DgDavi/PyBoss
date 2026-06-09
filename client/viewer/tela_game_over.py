# client/viewer/tela_game_over.py

import math
import pygame
from viewer.base import TelaBase, AMARELO, CINZA, VERMELHO

BRANCO = (220, 220, 220)

class TelaGameOver(TelaBase):

    def __init__(self, tela, pontuacao=0, relatorio_ia=""):
        super().__init__(tela)
        self.pontuacao = pontuacao
        self.relatorio_ia = relatorio_ia #string longa gerada pelo Groq
        
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
        
        #desenha relatório gerado
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

    def _draw_relatorio_ia(self):
        """Exibe o texto do relatório da IA quebrando as linhas perfeitamente na tela"""
        #título do Relatório
        txt_tit = self.fonte_sub.render("AVALIAÇÃO DO ORÁCULO GROQ:", True, AMARELO)
        self.tela.blit(txt_tit, (self.largura // 2 - txt_tit.get_width() // 2, 160))
        
        #divide o texto que veio da IA por linhas (\n) para desenhar uma embaixo da outra
        linhas_do_relatorio = self.relatorio_ia.split('\n')
        
        y_pos = 200
        for linha in linhas_do_relatorio:
            linha_limpa = linha.strip()
            if not linha_limpa:
                continue 
                
            txt_linha = self.fonte_pequena.render(linha_limpa, True, BRANCO)
            #centraliza linha por linha horizontalmente
            self.tela.blit(txt_linha, (self.largura // 2 - txt_linha.get_width() // 2, y_pos))
            y_pos += 26 #espaçamento entre cada frase

    def _draw_instrucao(self, tempo):
        if int(tempo * 2) % 2 == 0:
            txt = self.fonte_pequena.render(
                "► [R] VOLTAR AO MENU ◄", True, AMARELO)
            self.tela.blit(
                txt, (self.largura // 2 - txt.get_width() // 2, self.altura - 50))