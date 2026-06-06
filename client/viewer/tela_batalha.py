# client/viewer/tela_batalha.py

import math
import pygame

from viewer.base import TelaBase, AMARELO, CINZA, VERMELHO
from engine.combat import CombatState, TEMPO_RESPOSTA, TIMER_MENSAGEM

# ── Cores ────────────────────────────────
BRANCO      = (220, 220, 220)
VERDE       = (40,  190,  80)
LARANJA     = (220, 140,  20)
AZUL_CLARO  = (80,  160, 255)
VERM_ESCURO = (60,   10,  10)
PRETO_SEMI  = (0,     0,   0, 160)


class TelaBatalha(TelaBase):

    def __init__(self, tela, nome_jogador):
        super().__init__(tela)
        self.nome_jogador = nome_jogador
        self.combat_state = CombatState(nome_jogador)

        # Delta time
        self.ultima_atualizacao = pygame.time.get_ticks()

        # Fontes
        self.fonte_titulo   = pygame.font.SysFont("arialblack", 36)
        self.fonte_nome     = pygame.font.SysFont("arialblack", 20)
        self.fonte_menu     = pygame.font.SysFont("arialblack", 26)
        self.fonte_pergunta = pygame.font.SysFont("consolas",   20)
        self.fonte_codigo   = pygame.font.SysFont("consolas",   17)

    @property
    def proximo(self):
        return self.combat_state.proximo

    @proximo.setter
    def proximo(self, valor):
        # O GameManager pode tentar setar, mas a lógica de fluxo
        # é controlada internamente pelo CombatState.
        pass

    # ─────────────────────────────────────
    # EVENTOS
    # ─────────────────────────────────────

    def handle_event(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP:
                self.combat_state.handle_input("up")
            elif evento.key == pygame.K_DOWN:
                self.combat_state.handle_input("down")
            elif evento.key == pygame.K_RETURN:
                self.combat_state.handle_input("confirm")

    # ─────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────

    def update(self):
        agora = pygame.time.get_ticks()
        dt    = (agora - self.ultima_atualizacao) / 1000
        self.ultima_atualizacao = agora

        self.combat_state.update(dt)

    # ─────────────────────────────────────
    # DRAW
    # ─────────────────────────────────────

    def draw(self):
        tempo = pygame.time.get_ticks() / 1000
        self.desenhar_degradê()
        self.desenhar_grade(tempo)
        self._draw_titulo(tempo)
        self._draw_hud()
        self._draw_timer_bar()
        self._draw_personagens()
        self._draw_pergunta(tempo)
        self._draw_mensagem(tempo)
        self.desenhar_rodape(tempo)
        self.desenhar_borda()
        self.desenhar_scanlines()

    def _draw_titulo(self, tempo):
        pulso = 0.85 + 0.15 * math.sin(tempo * 3)
        cor   = tuple(int(c * pulso) for c in AMARELO)
        titulo = self.fonte_titulo.render("BATALHA", True, cor)
        self.tela.blit(titulo, (self.largura // 2 - titulo.get_width() // 2, 14))
        pygame.draw.line(
            self.tela, VERMELHO,
            (self.largura // 2 - 140, 60),
            (self.largura // 2 + 140, 60), 2
        )

    def _draw_hud(self):
        cs = self.combat_state
        if not cs.boss:
            return

        # Barra de vida — jogador (esquerda)
        self._draw_barra_vida(
            rect  = (self.largura // 2 - 330, 100, 260, 18),
            hp    = cs.hero.hp,
            hp_max = cs.hero.max_hp,
            nome  = self.nome_jogador.upper(),
            alinha_esquerda = True,
        )

        # Barra de vida — boss (direita)
        self._draw_barra_vida(
            rect  = (self.largura // 2 + 70, 100, 260, 18),
            hp    = cs.boss.hp,
            hp_max = cs.boss.max_hp,
            nome  = cs.boss.name.upper(),
            alinha_esquerda = False,
        )

        # Combo centralizado
        cor_combo = AMARELO if cs.combo > 0 else CINZA
        combo_txt = self.fonte_nome.render(f"COMBO  x{cs.combo}", True, cor_combo)
        self.tela.blit(combo_txt,
                       (self.largura // 2 - combo_txt.get_width() // 2, 126))

        # Nível
        nivel_txt = self.fonte_hud.render(f"NV {cs.nivel}", True, CINZA)
        self.tela.blit(nivel_txt, (self.largura // 2 - nivel_txt.get_width() // 2, 148))

    def _draw_barra_vida(self, rect, hp, hp_max, nome, alinha_esquerda):
        x, y, w, h = rect

        # Fundo
        pygame.draw.rect(self.tela, VERM_ESCURO, rect)

        # Preenchimento com cor dinâmica
        pct = 0 if hp_max == 0 else hp / hp_max
        cor = VERDE if pct > 0.5 else LARANJA if pct > 0.25 else VERMELHO
        pygame.draw.rect(self.tela, cor, (x, y, int(w * pct), h))

        # Borda
        pygame.draw.rect(self.tela, AMARELO, rect, 2)

        # Nome e HP
        info = self.fonte_nome.render(f"{nome}  {hp}/{hp_max}", True, BRANCO)
        if alinha_esquerda:
            self.tela.blit(info, (x, y - 22))
        else:
            self.tela.blit(info, (x + w - info.get_width(), y - 22))

    def _draw_timer_bar(self):
        """Barra de tempo regressiva centralizada."""
        cs = self.combat_state
        if not cs.questao or cs.aguardando:
            return

        pct = cs.timer_resposta / TEMPO_RESPOSTA
        cor = VERDE if pct > 0.5 else LARANJA if pct > 0.25 else VERMELHO

        larg  = 320
        x     = self.largura // 2 - larg // 2
        y     = 170

        # Fundo
        pygame.draw.rect(self.tela, (30, 20, 50), (x, y, larg, 8))
        # Preenchimento
        pygame.draw.rect(self.tela, cor, (x, y, int(larg * pct), 8))
        # Borda
        pygame.draw.rect(self.tela, CINZA, (x, y, larg, 8), 1)

        # Segundos restantes
        seg = math.ceil(cs.timer_resposta)
        txt = self.fonte_hud.render(f"{seg}s", True, cor)
        self.tela.blit(txt, (x + larg + 6, y - 2))

    def _draw_personagens(self):
        cs = self.combat_state
        if cs.hero:
            cs.hero.draw(self.tela)
        if cs.boss:
            cs.boss.draw(self.tela)

    def _draw_pergunta(self, tempo):
        """Área de pergunta + opções na parte inferior."""
        cs = self.combat_state
        if not cs.questao:
            txt = self.fonte_menu.render("CARREGANDO QUESTÃO...", True, CINZA)
            self.tela.blit(txt, (self.largura // 2 - txt.get_width() // 2, 360))
            return

        y_area = 280
        pad = 14

        # Fundo da área de pergunta
        fundo_rect = pygame.Rect(
            30, y_area - pad, self.largura - 60, self.altura - y_area - 40
        )
        pygame.draw.rect(self.tela, (10, 6, 22, 200), fundo_rect)
        pygame.draw.rect(self.tela, VERMELHO, fundo_rect, 2)

        # Tema e dificuldade
        tema = cs.boss_data.get("tema", "").upper() if cs.boss_data else ""
        tag = self.fonte_hud.render(f"TEMA: {tema}", True, CINZA)
        self.tela.blit(tag, (fundo_rect.x + 12, fundo_rect.y + 6))

        # Enunciado
        y_atual = y_area + 18
        self._desenhar_texto(
            cs.questao.get("pergunta", ""),
            x=fundo_rect.x + 12,
            y=y_atual,
            largura=fundo_rect.width - 24,
            fonte=self.fonte_pergunta,
            cor=BRANCO,
        )
        y_atual += self._altura_texto(
            cs.questao.get("pergunta", ""),
            largura=fundo_rect.width - 24,
            fonte=self.fonte_pergunta,
        )

        # Código
        codigo = cs.questao.get("codigo")
        if codigo and str(codigo).strip().lower() not in ("null", "none", ""):
            linhas = str(codigo).split("\n")
            y_codigo = y_atual + 10
            alt_bloco = len(linhas) * 22 + 10
            codigo_rect = pygame.Rect(
                fundo_rect.x + 20, y_codigo - 4, fundo_rect.width - 40, alt_bloco
            )
            pygame.draw.rect(self.tela, (18, 12, 35), codigo_rect)
            pygame.draw.rect(self.tela, (50, 30, 80), codigo_rect, 1)
            for i, linha in enumerate(linhas):
                cod = self.fonte_codigo.render(linha, True, AMARELO)
                self.tela.blit(cod, (codigo_rect.x + 10, y_codigo + i * 22))
            y_atual = y_codigo + alt_bloco + 10
        else:
            y_atual += 10

        # Opções
        y_opcoes = y_atual
        for i, opcao in enumerate(cs.opcoes):
            selecionado = i == cs.selecionado
            y = y_opcoes + i * 34

            if selecionado:
                pulso = 0.4 + 0.6 * abs(math.sin(tempo * 4))
                cor_fundo = (int(60 * pulso), int(10 * pulso), int(10 * pulso))
                caixa = pygame.Rect(fundo_rect.x + 10, y - 5, fundo_rect.width - 20, 30)
                pygame.draw.rect(self.tela, cor_fundo, caixa)
                pygame.draw.rect(self.tela, AMARELO, caixa, 2)
                cor_texto = AMARELO
            else:
                cor_texto = CINZA

            txt = self.fonte_pergunta.render(opcao, True, cor_texto)
            self.tela.blit(txt, (fundo_rect.x + 26, y))

        # Instrução
        inst = self.fonte_hud.render("↑↓ NAVEGAR   ENTER CONFIRMAR", True, CINZA)
        self.tela.blit(
            inst, (self.largura // 2 - inst.get_width() // 2, self.altura - 70)
        )

    def _draw_mensagem(self, tempo):
        """Banner de feedback (acerto / erro / timeout) com fade."""
        cs = self.combat_state
        if not cs.mensagem or cs.mensagem_timer <= 0:
            return

        # Fundo semi-transparente
        alpha  = int(min(255, cs.mensagem_timer / TIMER_MENSAGEM * 255))
        overlay = pygame.Surface((self.largura, 44), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, max(0, alpha // 2)))
        self.tela.blit(overlay, (0, 154))

        # Pisca levemente
        pulso = 0.7 + 0.3 * math.sin(tempo * 8)
        cor   = tuple(min(255, int(c * pulso)) for c in cs.mensagem_cor)

        txt = self.fonte_menu.render(cs.mensagem, True, cor)
        self.tela.blit(txt, (self.largura // 2 - txt.get_width() // 2, 162))

    # ─────────────────────────────────────
    # UTILITÁRIOS DE RENDERIZAÇÃO
    # ─────────────────────────────────────

    def _desenhar_texto(self, texto, x, y, largura, fonte, cor):
        """Desenha texto com quebra de linha automática."""
        linhas = self._quebrar_texto(texto, largura, fonte)
        for i, linha in enumerate(linhas):
            render = fonte.render(linha, True, cor)
            self.tela.blit(render, (x, y + i * fonte.get_height()))

    def _quebrar_texto(self, texto, largura, fonte):
        """Quebra um texto longo em várias linhas."""
        linhas = []
        palavras = texto.split(' ')
        linha_atual = ''
        for palavra in palavras:
            # Verifica se a palavra com a linha atual excede a largura
            if fonte.size(linha_atual + ' ' + palavra)[0] < largura:
                linha_atual += ' ' + palavra
            else:
                linhas.append(linha_atual.strip())
                linha_atual = palavra
        linhas.append(linha_atual.strip())
        return linhas

    def _altura_texto(self, texto, largura, fonte):
        """Calcula a altura total que um texto ocupará."""
        linhas = self._quebrar_texto(texto, largura, fonte)
        return len(linhas) * fonte.get_height()