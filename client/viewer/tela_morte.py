import pygame
import sys
import os

# Garante que o Python consiga herdar as funções do banco de dados do backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.database import obter_top_ranking

class TelaMorte:
    def __init__(self, tela):
        self.tela = tela
        # Configurações de fontes
        self.fonte_gameover = pygame.font.SysFont("arialblack", 65)
        self.fonte_subtitulo = pygame.font.SysFont("consolas", 24)
        self.fonte_ranking = pygame.font.SysFont("consolas", 20)
        
        # Cores
        self.PRETO = (10, 10, 15)
        self.VERMELHO = (255, 50, 50)
        self.VERDE_PIXEL = (50, 255, 100)
        self.BRANCO = (220, 220, 220)
        self.ROXO_ESCURO = (30, 15, 45)

    def renderizar(self, pontuacao_atual=0):
        # 1. Limpa a tela com fundo preto
        self.tela.fill(self.PRETO)
        
        # 2. Texto "GAME OVER" - Alto e Centralizado (Y = 100)
        txt_gameover = self.fonte_gameover.render("GAME OVER", True, self.VERMELHO)
        rect_gameover = txt_gameover.get_rect(center=(400, 100))
        self.tela.blit(txt_gameover, rect_gameover)
        
        # 3. Mostra a pontuação que o jogador fez nessa partida específica
        txt_sua_pont = self.fonte_subtitulo.render(f"Sua Pontuação: {pontuacao_atual} PTS", True, self.BRANCO)
        rect_sua_pont = txt_sua_pont.get_rect(center=(400, 170))
        self.tela.blit(txt_sua_pont, rect_sua_pont)
        
        # 4. Painel do Ranking dos Top 5 (Posicionado logo abaixo)
        retangulo_rank = pygame.Rect(180, 220, 440, 260)
        pygame.draw.rect(self.tela, self.ROXO_ESCURO, retangulo_rank)
        pygame.draw.rect(self.tela, self.VERMELHO, retangulo_rank, 2) # Borda vermelha indicando a derrota
        
        txt_rank_tit = self.fonte_subtitulo.render("TOP 5 ALQUIMISTAS (SQLite)", True, self.VERDE_PIXEL)
        rect_rank_tit = txt_rank_tit.get_rect(center=(400, 250))
        self.tela.blit(txt_rank_tit, rect_rank_tit)
        
        # Puxa o Top 5 do arquivo SQLite usando o nome correto da função
        try:
            top_5 = obter_top_ranking(5)
        except Exception:
            top_5 = []
            
        y_pos = 290
        if not top_5:
            txt_vazio = self.fonte_ranking.render("Nenhum registro no banco de dados.", True, self.BRANCO)
            self.tela.blit(txt_vazio, txt_vazio.get_rect(center=(400, 360)))
        else:
            for i, jogador in enumerate(top_5):
                nome, score = jogador
                # Alinha o texto usando ljust para os nomes e pontos ficarem retos
                texto_linha = f"{i+1}º  {nome.ljust(15)} {score} PTS"
                
                # O primeiro lugar ganha destaque em verde pixel, o resto fica branco
                cor_linha = self.VERDE_PIXEL if i == 0 else self.BRANCO
                
                txt_linha = self.fonte_ranking.render(texto_linha, True, cor_linha)
                self.tela.blit(txt_linha, (220, y_pos))
                y_pos += 32
                
        # 5. Instrução de rodapé para sair ou reiniciar
        txt_instrucao = self.fonte_subtitulo.render("Pressione [R] para voltar ao Menu", True, self.VERMELHO)
        rect_instrucao = txt_instrucao.get_rect(center=(400, 540))
        # Faz o texto piscar de leve baseado no tempo do Pygame
        if pygame.time.get_ticks() % 1200 < 600:
            self.tela.blit(txt_instrucao, rect_instrucao)