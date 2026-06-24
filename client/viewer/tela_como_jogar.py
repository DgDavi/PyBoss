# client/viewer/como_jogar.py

import pygame


AMARELO = (255, 204, 0)
VERMELHO = (255, 0, 51)
CINZA = (160, 160, 160)
BRANCO = (255, 255, 255)
LARANJA = (255, 128, 0)
AZUL_CLARO = (0, 200, 255)
VERDE = (0, 255, 100)

class TelaComoJogar:
    def __init__(self, tela):
        self.tela = tela
        self.largura = tela.get_width()
        self.altura = tela.get_height()
        self.proximo = None

       
        self.fonte_titulo = pygame.font.SysFont("Courier New", 32, bold=True)
        self.fonte_sub = pygame.font.SysFont("Courier New", 18, bold=True)
        self.fonte_texto = pygame.font.SysFont("Courier New", 14)

       
        self.aba_atual = 0 
        self.abas = [" JORNADA ", " ARCADE "]

    def update(self):
        """Método update vazio, já que a tela de instruções é estática."""
        pass

    def handle_event(self, evento):
        """Gerencia a troca de abas e o retorno ao menu."""
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self.proximo = "menu"
            
            
            elif evento.key == pygame.K_LEFT:
                self.aba_atual = (self.aba_atual - 1) % len(self.abas)
            elif evento.key == pygame.K_RIGHT:
                self.aba_atual = (self.aba_atual + 1) % len(self.abas)

    def draw(self):
        """Renderiza o manual baseado na aba selecionada."""
        
       
        self.tela.fill((15, 10, 30)) 

        
        titulo = self.fonte_titulo.render(" MANUAL DE OPERAÇÕES ", True, AMARELO)
        self.tela.blit(titulo, (self.largura // 2 - titulo.get_width() // 2, 20))
        
        
        y_abas = 70
        x_start = self.largura // 2 - 160
        
        for i, nome_aba in enumerate(self.abas):
            if i == self.aba_atual:
                
                txt_aba = self.fonte_sub.render(f"[{nome_aba}]", True, AMARELO)
                pygame.draw.rect(self.tela, VERMELHO, (x_start + i*160 - 5, y_abas - 2, txt_aba.get_width() + 10, 25), 1)
            else:
                
                txt_aba = self.fonte_sub.render(f" {nome_aba} ", True, CINZA)
                
            self.tela.blit(txt_aba, (x_start + i*160, y_abas))

        
        largura_bloco = 340
        y_blocos = 120
        x_col1, x_col2, x_col3 = 40, 400, 760

        
        if self.aba_atual == 0:
            self._renderizar_conteudo_jornada(x_col1, x_col2, x_col3, y_blocos, largura_bloco)
        else:
            self._renderizar_conteudo_arcade(x_col1, x_col2, x_col3, y_blocos, largura_bloco)

        
        instrucao_txt = "[ ← / → Setas: Mudar Aba ]  [ ESC ou ENTER: Retornar ao Menu ]"
        instrucao = self.fonte_sub.render(instrucao_txt, True, CINZA)
        self.tela.blit(instrucao, (self.largura // 2 - instrucao.get_width() // 2, self.altura - 45))
        
     

    def _renderizar_conteudo_jornada(self, x1, x2, x3, y, larg):
        """Renderiza o manual clássico do Modo Jornada."""
        # Coluna 1
        self._desenhar_painel(x1, y, larg, 410, ":: CONTROLES DA ARENA ::")
        controles = [
            ("↑↓ SETAS", "Navegar pelas opções de resposta."),
            ("ENTER", "Confirmar a alternativa selecionada."),
            ("TAB", "Abrir / Fechar o Inventário de Itens."),
            ("← → SETAS", "Navegar pelos slots do Inventário."),
            ("ESC", "Voltar para o Menu Anterior."),
        ]
        y_txt = y + 45
        for comando, desc in controles:
            txt_cmd = self.fonte_sub.render(comando, True, AMARELO)
            self.tela.blit(txt_cmd, (x1 + 15, y_txt))
            self._desenhar_texto_quebrado(desc, x1 + 15, y_txt + 18, larg - 40, CINZA)
            y_txt += 65

      
        self._desenhar_painel(x2, y, larg, 410, ":: SKILLS DE PROGRAMADOR ::")
        skills = [
            ("[Q] DICA (30 MP)", "Remove uma das alternativas incorretas da questão atual."),
            ("[W] +TEMPO (20 MP)", "Adiciona +5 segundos extras ao timer de resposta."),
            ("[E] ESCUDO (40 MP)", "Protege contra o próximo ataque do Boss caso você erre."),
        ]
        y_txt = y + 45
        cores_skills = [AMARELO, AZUL_CLARO, VERDE]
        for i, (skill, desc) in enumerate(skills):
            txt_sk = self.fonte_sub.render(skill, True, cores_skills[i])
            self.tela.blit(txt_sk, (x2 + 15, y_txt))
            self._desenhar_texto_quebrado(desc, x2 + 15, y_txt + 18, larg - 40, CINZA)
            y_txt += 80
        self._desenhar_texto_quebrado("INFO: Acertar perguntas recupera +10 MP. Erros reduzem sua barra de integridade (HP).", x2 + 15, y + 335, larg - 40, LARANJA)

      
        self._desenhar_painel(x3, y, larg, 410, ":: RECOMPENSAS JORNADA ::")
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
            "  * Axé: Garante tempo extra de round."
        )
        self._desenhar_texto_quebrado(recompensas_texto, x3 + 15, y + 45, larg - 40, BRANCO)

    def _renderizar_conteudo_arcade(self, x1, x2, x3, y, larg):
        """Renderiza o manual exclusivo do Modo Arcade (Hackathon)."""
        
        self._desenhar_painel(x1, y, larg, 410, ":: DIRETRIZES DO ARCADE ::")
        diretrizes = (
            "Esqueça o HP do herói! No modo Arcade\n"
            "você entra em ambiente de HACKATHON.\n\n"
            "Você inicia com um cronômetro global de\n"
            "2 MINUTOS (120 segundos) decrescentes.\n\n"
            "O objetivo é triturar o maior número de\n"
            "linhas de código e derrubar quantos\n"
            "Bosses puder antes do deploy falhar\n"
            "(o relógio zerar)."
        )
        self._desenhar_texto_quebrado(diretrizes, x1 + 15, y + 45, larg - 40, BRANCO)

      
        self._desenhar_painel(x2, y, larg, 410, ":: SISTEMA DE PENALIDADES ::")
        penalidades = (
            "Cada ação altera diretamente seu tempo:\n\n"
            "  * ACERTO CORRETO:\n"
            "    Ganha bônus de +3s a +8s no relógio\n"
            "    (quanto maior o combo, maior o bônus).\n\n"
            "  * RESPOSTA INCORRETA:\n"
            "    Quebra o combo e gera uma penalidade\n"
            "    pesada de -10s imediatos no relógio.\n\n"
            "  * ENROLAR NA PERGUNTA (15s):\n"
            "    Estourar o micro-timer da questão te\n"
            "    faz perder -7s e passa a pergunta."
        )
        self._desenhar_texto_quebrado(penalidades, x2 + 15, y + 45, larg - 40, LARANJA)

        
        self._desenhar_painel(x3, y, larg, 410, ":: RECOMPENSAS TIME-ATTACK ::")
        recompensas_arcade = (
            "Para fazer sentido, os drops locais foram\n"
            "recalibrados para focar em tempo:\n\n"
            "  * Cartola: Injeção rápida (+5s).\n"
            "  * Bolo de Rolo: Energia pura (+8s).\n"
            "  * Tapioca da Sé: Carga hacker (+12s).\n"
            "  * Axé de Olinda: Ritmo total (+15s).\n\n"
            "  * Gin de 10: Mantém o efeito clássico\n"
            "    de DOBRAR seu próximo ataque.\n\n"
            "Dica: Ativar o ESCUDO (E) com mana protege\n"
            "seu tempo global de perder 10s no erro!"
        )
        self._desenhar_texto_quebrado(recompensas_arcade, x3 + 15, y + 45, larg - 40, AZUL_CLARO)

    def _desenhar_painel(self, x, y, largura, altura, titulo):
        """Desenha a caixa vermelha padrão com o título do painel."""
        pygame.draw.rect(self.tela, VERMELHO, (x, y, largura, altura), 1)
        pygame.draw.rect(self.tela, (10, 5, 20), (x + 1, y + 1, largura - 2, 30))
        
        txt_titulo = self.fonte_sub.render(titulo, True, BRANCO)
        self.tela.blit(txt_titulo, (x + (largura // 2 - txt_titulo.get_width() // 2), y + 6))
        pygame.draw.line(self.tela, VERMELHO, (x, y + 30), (x + largura, y + 30), 1)

    def _desenhar_texto_quebrado(self, texto, x, y, largura, cor):
        """Renderiza texto respeitando quebras manuais e automáticas com margem segura."""
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