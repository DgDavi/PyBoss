# client/viewer/tela_batalha.py

import math
import random
import unicodedata
import pygame

from viewer.base import TelaBase, AMARELO, CINZA, VERMELHO
from engine.entities import (
    Hero,
    BossClasses,
    BossDicts,
    BossExceptions,
    BossLists,
    BossLoops,
    BossRecursion,
)
from network import gerar_boss, gerar_questao

# ── Cores ────────────────────────────────
BRANCO      = (220, 220, 220)
VERDE       = (40,  190,  80)
LARANJA     = (220, 140,  20)
AZUL_CLARO  = (80,  160, 255)
VERM_ESCURO = (60,   10,  10)
PRETO_SEMI  = (0,     0,   0, 160)

# ── Constantes de combate ────────────────
TEMPO_RESPOSTA  = 15.0   # segundos por pergunta
DANO_BASE_HEROI = 12
DANO_BASE_BOSS  = 10
TIMER_AGUARDAR  = 0.9    # segundos de feedback antes da próxima pergunta
TIMER_MENSAGEM  = 1.4
TIMER_ANIMACAO  = 0.3
TIMER_NOVO_BOSS = 1.2

# ── Mapa tema → classe do boss ───────────
MAPA_BOSS = {
    "classes":    BossClasses,
    "dicionarios": BossDicts,
    "excecoes":   BossExceptions,
    "listas":     BossLists,
    "loops":      BossLoops,
    "recursao":   BossRecursion,
}


class TelaBatalha(TelaBase):

    def __init__(self, tela, nome_jogador):
        super().__init__(tela)
        self.nome_jogador = nome_jogador

        # Entidades
        self.hero      = Hero()
        self.boss      = None
        self.boss_data = None
        self.nivel     = 1

        # Questão atual
        self.questao   = None
        self.opcoes    = []
        self.selecionado = 0

        # Combate
        self.combo         = 0
        self.maior_combo   = 0
        self.temas_errados = []

        # Timer de resposta (regressivo)
        self.timer_resposta  = TEMPO_RESPOSTA
        self.timer_esgotado  = False

        # Controle de estados intermediários
        self.aguardando        = False
        self.aguardando_timer  = 0.0
        self.mensagem          = ""
        self.mensagem_cor      = AMARELO
        self.mensagem_timer    = 0.0
        self.anim_timer        = 0.0

        # Delta time
        self.ultima_atualizacao = pygame.time.get_ticks()

        # Fontes
        self.fonte_titulo   = pygame.font.SysFont("arialblack", 36)
        self.fonte_nome     = pygame.font.SysFont("arialblack", 20)
        self.fonte_menu     = pygame.font.SysFont("arialblack", 26)
        self.fonte_pergunta = pygame.font.SysFont("consolas",   20)
        self.fonte_codigo   = pygame.font.SysFont("consolas",   17)

        self._carregar_boss()
        self._carregar_questao()

    # ─────────────────────────────────────
    # EVENTOS
    # ─────────────────────────────────────

    def handle_event(self, evento):
        # Bloqueia input durante feedback ou carregamento
        if self.aguardando or self.mensagem_timer > 0 or not self.questao:
            return

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP:
                self.selecionado = (self.selecionado - 1) % len(self.opcoes)
            elif evento.key == pygame.K_DOWN:
                self.selecionado = (self.selecionado + 1) % len(self.opcoes)
            elif evento.key == pygame.K_RETURN:
                self._responder()

    # ─────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────

    def update(self):
        agora = pygame.time.get_ticks()
        dt    = (agora - self.ultima_atualizacao) / 1000
        self.ultima_atualizacao = agora

        self.hero.update(dt)
        self._atualizar_timer_resposta(dt)
        self._atualizar_animacao(dt)
        self._atualizar_mensagem(dt)
        self._resolver_proxima_acao(dt)

    def _atualizar_timer_resposta(self, dt):
        """Desconta o timer. Se zerar, trata como erro."""
        if self.aguardando or self.mensagem_timer > 0 or not self.questao:
            return

        self.timer_resposta = max(0.0, self.timer_resposta - dt)

        if self.timer_resposta == 0.0 and not self.timer_esgotado:
            self.timer_esgotado = True
            self._processar_timeout()

    def _atualizar_animacao(self, dt):
        if self.anim_timer <= 0:
            return
        self.anim_timer = max(0.0, self.anim_timer - dt)
        if self.anim_timer == 0.0:
            self.hero.set_state("idle")

    def _atualizar_mensagem(self, dt):
        if self.mensagem_timer <= 0:
            return
        self.mensagem_timer = max(0.0, self.mensagem_timer - dt)
        if self.mensagem_timer == 0.0:
            self.mensagem = ""

    def _resolver_proxima_acao(self, dt):
        """Após o delay de feedback, decide o que acontece a seguir."""
        if not self.aguardando:
            return

        self.aguardando_timer = max(0.0, self.aguardando_timer - dt)
        if self.aguardando_timer > 0:
            return

        self.aguardando = False

        if self.hero.is_dead():
            self.proximo = "game_over"
            return

        if self.boss and self.boss.is_dead():
            self._proximo_boss()
            return

        self._carregar_questao()

    # ─────────────────────────────────────
    # LÓGICA DE COMBATE
    # ─────────────────────────────────────

    def _responder(self):
        """Processa a resposta do jogador."""
        if not self.questao:
            return

        letra_escolhida = self.opcoes[self.selecionado].strip()[:1].upper()
        letra_correta   = str(self.questao.get("correta", "A")).strip()[:1].upper()

        if letra_escolhida == letra_correta:
            self._processar_acerto()
        else:
            self._processar_erro()

        self.aguardando       = True
        self.aguardando_timer = TIMER_AGUARDAR

    def _processar_acerto(self):
        self.combo       += 1
        self.maior_combo  = max(self.combo, self.maior_combo)
        dano              = self._calcular_dano(DANO_BASE_HEROI, self.combo)
        self.boss.take_damage(dano)
        self.hero.set_state("attack")
        self.anim_timer   = TIMER_ANIMACAO
        self._set_mensagem(
            f"✓ CORRETO!  COMBO x{self.combo}  +{dano} DANO",
            cor=VERDE
        )

    def _processar_erro(self):
        dano              = self._calcular_dano(DANO_BASE_BOSS, self.combo)
        self.hero.take_damage(dano)
        self.hero.set_state("damage")
        self.anim_timer   = TIMER_ANIMACAO
        self._set_mensagem(
            f"✗ ERRADO!  COMBO QUEBRADO  -{dano} HP",
            cor=VERMELHO
        )
        self.combo = 0
        self._registrar_erro_tema()

    def _processar_timeout(self):
        """Timer zerou — penalidade igual a um erro."""
        dano = self._calcular_dano(DANO_BASE_BOSS, self.combo)
        self.hero.take_damage(dano)
        self.hero.set_state("damage")
        self.anim_timer   = TIMER_ANIMACAO
        self._set_mensagem(
            f"⏱ TEMPO ESGOTADO!  -{dano} HP",
            cor=LARANJA
        )
        self.combo        = 0
        self.aguardando   = True
        self.aguardando_timer = TIMER_AGUARDAR
        self._registrar_erro_tema()

    def _calcular_dano(self, base, combo):
        bonus    = combo * 4
        nivel    = max(0, self.nivel - 1)
        variacao = random.randint(0, 2)
        return base + bonus + (nivel * 2) + variacao

    # ─────────────────────────────────────
    # CARREGAMENTO
    # ─────────────────────────────────────

    def _carregar_boss(self):
        self.boss_data  = gerar_boss(self.nivel)
        tema            = self._normalizar(self.boss_data.get("tema", ""))
        classe_boss     = MAPA_BOSS.get(tema, BossLoops)
        self.boss       = classe_boss()
        self.boss.name  = self.boss_data.get("nome", self.boss.name)
        self.boss.max_hp = int(self.boss_data.get("hp", self.boss.max_hp))
        self.boss.hp    = self.boss.max_hp

    def _carregar_questao(self):
        if not self.boss_data:
            return
        tema          = self.boss_data.get("tema", "loops")
        self.questao  = gerar_questao(tema, self.nivel, self.temas_errados)
        self.opcoes   = self.questao.get("opcoes", [])
        if not self.opcoes:
            self.opcoes = ["A) ???", "B) ???", "C) ???", "D) ???"]
        self.selecionado    = 0
        self.timer_resposta = TEMPO_RESPOSTA
        self.timer_esgotado = False

    def _proximo_boss(self):
        self.nivel += 1
        self._carregar_boss()
        self._set_mensagem(
            f"★ BOSS DERROTADO!  PRÓXIMO: {self.boss.name.upper()}",
            cor=AMARELO
        )
        self.aguardando       = True
        self.aguardando_timer = TIMER_NOVO_BOSS

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
        if not self.boss:
            return

        # Barra de vida — jogador (esquerda)
        self._draw_barra_vida(
            rect  = (self.largura // 2 - 330, 100, 260, 18),
            hp    = self.hero.hp,
            hp_max = self.hero.max_hp,
            nome  = self.nome_jogador.upper(),
            alinha_esquerda = True,
        )

        # Barra de vida — boss (direita)
        self._draw_barra_vida(
            rect  = (self.largura // 2 + 70, 100, 260, 18),
            hp    = self.boss.hp,
            hp_max = self.boss.max_hp,
            nome  = self.boss.name.upper(),
            alinha_esquerda = False,
        )

        # Combo centralizado
        cor_combo = AMARELO if self.combo > 0 else CINZA
        combo_txt = self.fonte_nome.render(f"COMBO  x{self.combo}", True, cor_combo)
        self.tela.blit(combo_txt,
                       (self.largura // 2 - combo_txt.get_width() // 2, 126))

        # Nível
        nivel_txt = self.fonte_hud.render(f"NV {self.nivel}", True, CINZA)
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
        if not self.questao or self.aguardando:
            return

        pct = self.timer_resposta / TEMPO_RESPOSTA
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
        seg = math.ceil(self.timer_resposta)
        txt = self.fonte_hud.render(f"{seg}s", True, cor)
        self.tela.blit(txt, (x + larg + 6, y - 2))

    def _draw_personagens(self):
        if self.hero:
            self.hero.draw(self.tela)
        if self.boss:
            self.boss.draw(self.tela)

    def _draw_pergunta(self, tempo):
        """Área de pergunta + opções na parte inferior."""
        if not self.questao:
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
        tema = self.boss_data.get("tema", "").upper() if self.boss_data else ""
        tag = self.fonte_hud.render(f"TEMA: {tema}", True, CINZA)
        self.tela.blit(tag, (fundo_rect.x + 12, fundo_rect.y + 6))

        # Enunciado
        y_atual = y_area + 18
        self._desenhar_texto(
            self.questao.get("pergunta", ""),
            x=fundo_rect.x + 12,
            y=y_atual,
            largura=fundo_rect.width - 24,
            fonte=self.fonte_pergunta,
            cor=BRANCO,
        )
        y_atual += self._altura_texto(
            self.questao.get("pergunta", ""),
            largura=fundo_rect.width - 24,
            fonte=self.fonte_pergunta,
        )

        # Código
        codigo = self.questao.get("codigo")
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
        for i, opcao in enumerate(self.opcoes):
            selecionado = i == self.selecionado
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
        if not self.mensagem or self.mensagem_timer <= 0:
            return

        # Fundo semi-transparente
        alpha  = int(min(255, self.mensagem_timer / TIMER_MENSAGEM * 255))
        overlay = pygame.Surface((self.largura, 44), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, max(0, alpha // 2)))
        self.tela.blit(overlay, (0, 154))

        # Pisca levemente
        pulso = 0.7 + 0.3 * math.sin(tempo * 8)
        cor   = tuple(min(255, int(c * pulso)) for c in self.mensagem_cor)

        txt = self.fonte_menu.render(self.mensagem, True, cor)
        self.tela.blit(txt, (self.largura // 2 - txt.get_width() // 2, 162))

    # ─────────────────────────────────────
    # UTILITÁRIOS
    # ─────────────────────────────────────

    def _set_mensagem(self, texto, cor=None):
        self.mensagem       = texto
        self.mensagem_cor   = cor if cor else AMARELO
        self.mensagem_timer = TIMER_MENSAGEM

    def _registrar_erro_tema(self):
        if not self.boss_data:
            return
        tema = self._normalizar(self.boss_data.get("tema", ""))
        if tema and tema not in self.temas_errados:
            self.temas_errados.append(tema)

    def _normalizar(self, texto):
        """Remove acentos e padroniza para lowercase."""
        if not texto:
            return ""
        texto = unicodedata.normalize("NFKD", str(texto))
        texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
        return texto.strip().lower()

    def _desenhar_texto(self, texto, x, y, largura, fonte, cor):
        for linha in self._quebrar_texto(str(texto), largura, fonte):
            surf = fonte.render(linha, True, cor)
            self.tela.blit(surf, (x, y))
            y += surf.get_height() + 4

    def _quebrar_texto(self, texto, largura, fonte):
        palavras, linhas, linha_atual = texto.split(), [], ""
        for palavra in palavras:
            teste = f"{linha_atual} {palavra}".strip()
            if fonte.size(teste)[0] <= largura:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    def _altura_texto(self, texto, largura, fonte):
        linhas = self._quebrar_texto(str(texto), largura, fonte)
        if not linhas:
            return 0
        altura_linha = fonte.get_height()
        return len(linhas) * (altura_linha + 4) - 4