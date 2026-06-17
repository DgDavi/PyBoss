import pygame
import sys
import os
from viewer.base import TelaBase, AMARELO, CINZA, VERDE, BRANCO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.database import obter_top_ranking

ROXO_ESCURO = (25, 15, 35)

class TelaRanking(TelaBase):

    def __init__(self, tela):
        super().__init__(tela)
        self.fonte_titulo  = pygame.font.SysFont("arialblack", 50)
        self.fonte_sub     = pygame.font.SysFont("consolas", 24)
        self.fonte_pequena = pygame.font.SysFont("consolas", 18)

    def handle_event(self, evento):
        if evento.type == pygame.KEYDOWN:
            # Ao pressionar qualquer tecla (ou ESC/M), volta para o menu
            if evento.key in [pygame.K_ESCAPE, pygame.K_m, pygame.K_RETURN]:
                self.proximo = "menu"

    def update(self):
        pass

    def draw(self):
        tempo = pygame.time.get_ticks() / 1000
        self.desenhar_degradê()
        self.desenhar_grade(tempo)
        
        # Título da Tela
        txt_titulo = self.fonte_titulo.render("RANKING GERAL", True, VERDE)
        self.tela.blit(txt_titulo, (self.largura // 2 - txt_titulo.get_width() // 2, 40))
        
        # Painel centralizado do sqlite
        largura_box, altura_box = 500, 300
        x_box = self.largura // 2 - largura_box // 2
        y_box = 130
        
        pygame.draw.rect(self.tela, ROXO_ESCURO, (x_box, y_box, largura_box, altura_box))
        pygame.draw.rect(self.tela, VERDE, (x_box, y_box, largura_box, altura_box), 2)
        
        # Puxa os dados reais do banco sqlite
        try:
            top_5 = obter_top_ranking(5)
        except Exception:
            top_5 = []
            
        y_linha = y_box + 40
        if not top_5:
            txt_vazio = self.fonte_pequena.render("Nenhum alquimista registrado ainda...", True, CINZA)
            self.tela.blit(txt_vazio, (self.largura // 2 - txt_vazio.get_width() // 2, y_box + 130))
        else:
            for i, jogador in enumerate(top_5):
                nome, score = jogador
                linha_texto = f"{i+1}º  {nome.ljust(20)} {score} PTS"
                cor_texto = VERDE if i == 0 else BRANCO
                
                txt_linha = self.fonte_pequena.render(linha_texto, True, cor_texto)
                self.tela.blit(txt_linha, (x_box + 60, y_linha))
                y_linha += 45
                
        # mensagem para voltar
        if int(tempo * 2) % 2 == 0:
            txt_voltar = self.fonte_pequena.render("Pressione [ESC] ou [ENTER] para voltar ao Menu", True, AMARELO)
            self.tela.blit(txt_voltar, (self.largura // 2 - txt_voltar.get_width() // 2, self.altura - 60))
            
        self.desenhar_borda()
        self.desenhar_scanlines()