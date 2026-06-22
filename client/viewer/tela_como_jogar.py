# client/viewer/como_jogar.py

import pygame
from viewer.base import TelaBase, AMARELO, CINZA, VERMELHO

# ── Cores Locais ─────────────────────────
BRANCO      = (220, 220, 220)
VERDE       = (40,  190,  80)
LARANJA     = (220, 140,  20)
AZUL_CLARO  = (80,  160, 255)

class TelaComoJogar(TelaBase):
    """Tela que explica os comandos, mecânicas e itens do jogo."""

    def __init__(self, tela):
        super().__init__(tela)
        self._proximo = self  
        
        
        self.fonte_titulo   = pygame.font.SysFont("arialblack", 32)
        self.fonte_secao    = pygame.font.SysFont("arialblack", 18)
        self.fonte_texto    = pygame.font.SysFont("consolas", 15)
        self.fonte_sub      = pygame.font.SysFont("consolas", 16)

    @property
    def proximo(self):
        return self._proximo

    @proximo.setter
    def proximo(self, valor):
        self._proximo = valor

    def handle_event(self, evento):
        """Volta para o menu principal se o jogador apertar ESC ou ENTER."""
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self.proximo = "menu" 

    def update(self):
        """apenas espera o input de saída."""
        pass

    def draw(self):
        """Renderiza o guia completo de jogo."""
        self.desenhar_degradê()
        
       
        titulo = self.fonte_titulo.render(" MANUAL DE OPERAÇÕES ", True, AMARELO)
        self.tela.blit(titulo, (self.largura // 2 - titulo.get_width() // 2, 20))
        pygame.draw.line(self.tela, VERMELHO, (self.largura // 2 - 200, 65), (self.largura // 2 + 200, 65), 2)

       
        largura_bloco = 340
        y_blocos = 90
        
        x_col1 = 40
        x_col2 = 400
        x_col3 = 760

        
        self._desenhar_painel(x_col1, y_blocos, largura_bloco, 420, ":: CONTROLES DA ARENA ::")
        
        controles = [
            ("↑↓ SETAS", "Navegar pelas opções de resposta."),
            ("ENTER", "Confirmar a alternativa selecionada."),
            ("TAB", "Abrir / Fechar o Inventário de Itens."),
            ("← → SETAS", "Navegar pelos slots do Inventário."),
            ("ESC", "Voltar para o Menu Anterior."),
        ]
        y_txt = y_blocos + 45
        for comando, desc in controles:
            txt_cmd = self.fonte_sub.render(comando, True, AMARELO)
            self.tela.blit(txt_cmd, (x_col1 + 15, y_txt))
            self._desenhar_texto_quebrado(desc, x_col1 + 15, y_txt + 18, largura_bloco - 40, CINZA)
            y_txt += 65

        
        self._desenhar_painel(x_col2, y_blocos, largura_bloco, 420, ":: SKILLS DE PROGRAMADOR ::")
        
        skills = [
            ("[Q] DICA (30 MP)", "Remove uma das alternativas incorretas da questão atual."),
            ("[W] +TEMPO (20 MP)", "Adiciona +5 segundos extras ao timer de resposta."),
            ("[E] ESCUDO (40 MP)", "Protege contra o próximo ataque do Boss caso você erre."),
        ]
        y_txt = y_blocos + 45
        cores_skills = [AMARELO, AZUL_CLARO, VERDE]
        for i, (skill, desc) in enumerate(skills):
            txt_sk = self.fonte_sub.render(skill, True, cores_skills[i])
            self.tela.blit(txt_sk, (x_col2 + 15, y_txt))
            self._desenhar_texto_quebrado(desc, x_col2 + 15, y_txt + 18, largura_bloco - 40, CINZA)
            y_txt += 80
            
       
        self._desenhar_texto_quebrado("INFO: Acertar perguntas recupera +10 MP. Erros reduzem sua barra de integridade (HP).", x_col2 + 15, y_blocos + 340, largura_bloco - 40, LARANJA)

        
        self._desenhar_painel(x_col3, y_blocos, largura_bloco, 420, ":: RECOMPENSAS REGIONAIS ::")
        
        recompensas_texto = (
            "Ao acertar uma resposta, você tem 30%\n"
            "de chance de obter um item típico\n"
            "da cultura pernambucana. Você pode\n"
            "carregar até 5 itens simultâneos.\n\n"
            "Consuma-os estrategicamente de dentro\n"
            "do seu inventário (TAB) para aplicar\n"
            "buffs imediatos:\n\n"
            "  * Tapioca / Bolo de Rolo / Cartola:\n"
            "    Recupera pontos de vida (HP).\n"
            "  * Gin de 10: Concede multiplicador\n"
            "    de dano.\n"
            "  * Axé: Garante tempo extra."
        )
        self._desenhar_texto_quebrado(recompensas_texto, x_col3 + 15, y_blocos + 45, largura_bloco - 40, BRANCO)

       
        instrucao = self.fonte_sub.render("[ Pressione ESC ou ENTER para retornar ao menu ]", True, CINZA)
        self.tela.blit(instrucao, (self.largura // 2 - instrucao.get_width() // 2, self.altura - 45))
        
        self.desenhar_borda()
        self.desenhar_scanlines()

    def _desenhar_painel(self, x, y, w, h, titulo):
        """Desenha uma caixinha de seção estilizada."""
       
        fundo = pygame.Surface((w, h), pygame.SRCALPHA)
        fundo.fill((14, 10, 28, 210))
        self.tela.blit(fundo, (x, y))
        
        pygame.draw.rect(self.tela, VERMELHO, (x, y, w, h), 1, border_radius=4)
        
        txt_titulo = self.fonte_secao.render(titulo, True, BRANCO)
        self.tela.blit(txt_titulo, (x + w // 2 - txt_titulo.get_width() // 2, y + 12))
        pygame.draw.line(self.tela, VERMELHO, (x + 10, y + 36), (x + w - 10, y + 36), 1)

    def _desenhar_texto_quebrado(self, texto, x, y, largura, cor):
        """Renderiza texto respeitando quebras manuais (\n) e automáticas."""
        largura_util = largura - 20
        linhas = []
        
        
        paragrafos = texto.split('\n')
        
        for paragrafo in paragrafos:
            if paragrafo.strip() == '':
                linhas.append('') 
                continue
                
            palavras = paragrafo.split(' ')
            linha_atual = ''
            
            for palavra in palavras:
                if self.fonte_texto.size(linha_atual + ' ' + palavra)[0] < largura_util:
                    linha_atual += ' ' + palavra
                else:
                    linhas.append(linha_atual.strip())
                    linha_atual = palavra
            linhas.append(linha_atual.strip())

        for i, linha in enumerate(linhas):
            if linha != '':
                render = self.fonte_texto.render(linha, True, cor)
                self.tela.blit(render, (x, y + i * (self.fonte_texto.get_height() + 3)))