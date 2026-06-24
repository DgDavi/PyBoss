# client/viewer/tela_menu.py

import pygame
import math
from viewer.base import TelaBase, AMARELO, CINZA, VERMELHO, ROXO

BRANCO = (220, 220, 220)


class TelaMenu(TelaBase):
    def __init__(self, tela, nome_jogador):
        super().__init__(tela)
        self.nome_jogador = nome_jogador
        
        
        self.opcoes       = ["MODO JORNADA", "MODO ARCADE", "COMO JOGAR", "RANKING"]
        self.selecionado  = 0

        self.fonte_titulo = pygame.font.SysFont("arialblack", 64)
        self.fonte_nome   = pygame.font.SysFont("arialblack", 22)
        
        self.fonte_menu   = pygame.font.SysFont("arialblack", 32)

    def handle_event(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP:
                self.selecionado = (self.selecionado - 1) % len(self.opcoes)
            elif evento.key == pygame.K_DOWN:
                self.selecionado = (self.selecionado + 1) % len(self.opcoes)
            elif evento.key == pygame.K_RETURN:
                
               
                if self.selecionado == 0:
                    self.proximo = "batalha"       
                elif self.selecionado == 1:
                    self.proximo = "arcade"        
                elif self.selecionado == 2:
                    self.proximo = "como_jogar"
                elif self.selecionado == 3:
                    self.proximo = "ranking"

    def draw(self):
        tempo = pygame.time.get_ticks() / 1000
        self.desenhar_degradê()
        self.desenhar_grade(tempo)
        self._titulo(tempo)
        self._saudacao()
        self._menu(tempo)
        self.desenhar_rodape(tempo)
        self.desenhar_borda()
        self.desenhar_scanlines()

    def _titulo(self, tempo):
        pulso  = 0.85 + 0.15 * math.sin(tempo * 3)
        cor    = tuple(int(c * pulso) for c in AMARELO)
        sombra = self.fonte_titulo.render("PyBoss", True, (60, 30, 0))
        
        self.tela.blit(sombra, (self.largura // 2 - sombra.get_width() // 2 + 3, 63))
        titulo = self.fonte_titulo.render("PyBoss", True, cor)
       
        self.tela.blit(titulo, (self.largura // 2 - titulo.get_width() // 2, 60))
        
        pygame.draw.line(self.tela, VERMELHO,
                         (self.largura // 2 - 180, 156),
                         (self.largura // 2 + 180, 156), 2)

    def _saudacao(self):
        saudacao = self.fonte_nome.render(
            f"BEM-VINDO, {self.nome_jogador.upper()}!", True, BRANCO)
        self.tela.blit(saudacao, (self.largura // 2 - saudacao.get_width() // 2, 176))

    def _menu(self, tempo):
        y_inicio = 225
        espacamento = 75
        alt_box = 52  

        for i, opcao in enumerate(self.opcoes):
            selecionado = (i == self.selecionado)
            y_centro_opcao = y_inicio + i * espacamento

            if selecionado:
                cor_texto = AMARELO
            else:
                cor_texto = CINZA
            texto = self.fonte_menu.render(opcao, True, cor_texto)

            
            larg_box = 380
            x_box = self.largura // 2 - larg_box // 2
            y_box = y_centro_opcao - (alt_box // 2)
            caixa = pygame.Rect(x_box, y_box, larg_box, alt_box)

            if selecionado:
                pulso     = 0.4 + 0.6 * abs(math.sin(tempo * 4))
                cor_fundo = (int(60 * pulso), int(10 * pulso), int(10 * pulso))
                pygame.draw.rect(self.tela, cor_fundo, caixa)
                pygame.draw.rect(self.tela, AMARELO, caixa, 2)

            x_texto = caixa.x + (caixa.width // 2) - (texto.get_width() // 2)
            y_texto = caixa.y + (caixa.height // 2) - (texto.get_height() // 2)
            self.tela.blit(texto, (x_texto, y_texto))

            if selecionado and int(tempo * 4) % 2 == 0:
                cursor = self.fonte_menu.render("►", True, AMARELO)
                y_cursor = caixa.y + (caixa.height // 2) - (cursor.get_height() // 2)
                self.tela.blit(cursor, (caixa.x - 40, y_cursor))

        y_inst = y_inicio + len(self.opcoes) * espacamento
        inst = self.fonte_nome.render("↑↓ NAVEGAR   ENTER CONFIRMAR", True, CINZA)
        self.tela.blit(inst, (self.largura // 2 - inst.get_width() // 2, y_inst))