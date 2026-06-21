# client/viewer/tela_batalha.py

import math
import pygame

from viewer.base import TelaBase, AMARELO, CINZA, VERMELHO
from engine.combat import CombatState, TEMPO_RESPOSTA, TIMER_MENSAGEM, TIMER_APRESENTACAO

# ── Cores ────────────────────────────────
BRANCO      = (220, 220, 220)
VERDE       = (40,  190,  80)
LARANJA     = (220, 140,  20)
AZUL_CLARO  = (80,  160, 255)
VERM_ESCURO = (60,   10,  10)
PRETO_SEMI  = (0,     0,   0, 160)
Y_DIVISOR   = 315
AZUL_MANA   = (60, 100, 220)

class TelaBatalha(TelaBase):
    """Gerencia a visualização e interação da interface de batalha."""

    def __init__(self, tela, nome_jogador, boss_data=None, nivel=1):
        """Inicializa a tela de batalha e o estado lógico do combate."""
        super().__init__(tela)
        self.nome_jogador = nome_jogador
        self.ultima_atualizacao = pygame.time.get_ticks()

        self.fonte_titulo   = pygame.font.SysFont("arialblack", 36)
        self.fonte_nome     = pygame.font.SysFont("arialblack", 20)
        self.fonte_menu     = pygame.font.SysFont("arialblack", 26)
        self.fonte_pergunta = pygame.font.SysFont("consolas",   20)
        self.fonte_codigo   = pygame.font.SysFont("consolas",   17)
        self.fonte_apres    = pygame.font.SysFont("arialblack", 44)
        self.fonte_apres_sub = pygame.font.SysFont("consolas",  18)
        
        self.combat_state = CombatState(nome_jogador, boss_data=boss_data, nivel=nivel)

    @property
    def proximo(self):
        """Retorna o próximo estado da aplicação."""
        return self.combat_state.proximo

    @proximo.setter
    def proximo(self, valor):
        pass

    def handle_event(self, evento):
        """Processa eventos de teclado para controle do combate."""
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP:
                self.combat_state.handle_input("up")
            elif evento.key == pygame.K_DOWN:
                self.combat_state.handle_input("down")
            elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.combat_state.handle_input("confirm")
            elif evento.key == pygame.K_q:
                self.combat_state.handle_input("skill_dica")
            elif evento.key == pygame.K_w:
                self.combat_state.handle_input("skill_tempo")
            elif evento.key == pygame.K_e:
                self.combat_state.handle_input("skill_escudo")

    def update(self):
        """Atualiza a lógica do estado de combate."""
        agora = pygame.time.get_ticks()
        dt = (agora - self.ultima_atualizacao) / 1000
        self.ultima_atualizacao = agora
        self.combat_state.update(dt)

    def draw(self):
        """Renderiza os elementos da tela de batalha."""
        tempo = pygame.time.get_ticks() / 1000
        self.desenhar_degradê()
        self.desenhar_grade(tempo)

        if self.combat_state.fase == "apresentando":
            self._draw_apresentacao(tempo)
        else:
            self._draw_batalha(tempo)

        self.desenhar_rodape(tempo)
        self.desenhar_borda()
        self.desenhar_scanlines()

    def _draw_apresentacao(self, tempo):
        """Desenha a cena de introdução do chefe."""
        cs = self.combat_state
        pulso = 0.80 + 0.20 * math.sin(tempo * 4)
        cor_titulo = tuple(int(c * pulso) for c in VERMELHO)
        titulo = self.fonte_apres.render("NOVO INIMIGO!", True, cor_titulo)
        self.tela.blit(titulo, (self.largura // 2 - titulo.get_width() // 2, 30))

        pygame.draw.line(self.tela, VERMELHO, (self.largura // 2 - 220, 88), (self.largura // 2 + 220, 88), 2)

        if cs.boss:
            cs.boss.rect.midbottom = (self.largura // 2, 280)
            cs.boss.draw(self.tela)

        if cs.boss_data:
            nome_boss = cs.boss_data.get("nome", "???").upper()
            nome_surf = self.fonte_apres.render(nome_boss, True, AMARELO)
            self.tela.blit(nome_surf, (self.largura // 2 - nome_surf.get_width() // 2, 290))

            tema = cs.boss_data.get("tema", "").upper()
            tema_surf = self.fonte_apres_sub.render(f"TEMA: {tema}", True, LARANJA)
            self.tela.blit(tema_surf, (self.largura // 2 - tema_surf.get_width() // 2, 344))

            if cs.boss_descricao:
                self._desenhar_texto(cs.boss_descricao, self.largura // 2 - 280, 376, 560, self.fonte_apres_sub, CINZA)

            hp_surf = self.fonte_apres_sub.render(f"HP: {cs.boss.max_hp}", True, VERMELHO)
            self.tela.blit(hp_surf, (self.largura // 2 - hp_surf.get_width() // 2, 420))

        pct = cs.apresentacao_timer / TIMER_APRESENTACAO
        larg = 320
        x = self.largura // 2 - larg // 2
        y = self.altura - 100
        pygame.draw.rect(self.tela, (30, 20, 50), (x, y, larg, 8))
        pygame.draw.rect(self.tela, AMARELO, (x, y, int(larg * pct), 8))
        pygame.draw.rect(self.tela, CINZA, (x, y, larg, 8), 1)

        inst = self.fonte_hud.render("ENTER PARA INICIAR BATALHA", True, CINZA)
        self.tela.blit(inst, (self.largura // 2 - inst.get_width() // 2, self.altura - 80))

    def _draw_batalha(self, tempo):
        """Gerencia a renderização de todos os componentes de combate."""
        self._draw_titulo(tempo)
        self._draw_hud()
        self._draw_timer_bar()  
        self._draw_mana_e_skills()
        self._draw_skills_canto(tempo)
        self._draw_personagens()
        self._draw_pergunta(tempo)
        self._draw_mensagem(tempo)

        pygame.draw.line(self.tela, CINZA, (30, Y_DIVISOR), (self.largura - 30, Y_DIVISOR), 1)

    def _draw_titulo(self, tempo):
        """Desenha o cabeçalho 'BATALHA' com efeito visual."""
        pulso = 0.85 + 0.15 * math.sin(tempo * 3)
        cor = tuple(int(c * pulso) for c in AMARELO)
        titulo = self.fonte_titulo.render("BATALHA", True, cor)
        self.tela.blit(titulo, (self.largura // 2 - titulo.get_width() // 2, 8))
        pygame.draw.line(self.tela, VERMELHO, (self.largura // 2 - 140, 50), (self.largura // 2 + 140, 50), 2)

    def _draw_hud(self):
        """Desenha as barras de vida e informações do combo."""
        cs = self.combat_state
        if not cs.boss:
            return

       
        self._draw_barra_vida((self.largura // 2 - 420, 48, 260, 18), cs.hero.hp, cs.hero.max_hp, self.nome_jogador.upper(), True)
        self._draw_barra_vida((self.largura // 2 + 160, 48, 260, 18), cs.boss.hp, cs.boss.max_hp, cs.boss.name.upper(), False)

        
        cor_combo = AMARELO if cs.combo > 0 else CINZA
        combo_txt = self.fonte_nome.render(f"COMBO x{cs.combo}", True, cor_combo)
        self.tela.blit(combo_txt, (self.largura // 2 - combo_txt.get_width() // 2, 54))

        
        nivel_txt = self.fonte_hud.render(f"NV {cs.nivel}", True, CINZA)
        self.tela.blit(nivel_txt, (self.largura // 2 - nivel_txt.get_width() // 2, 76))

    def _draw_barra_vida(self, rect, hp, hp_max, nome, alinha_esquerda):
        """Renderiza uma barra de vida genérica."""
        x, y, w, h = rect
        pygame.draw.rect(self.tela, VERM_ESCURO, rect)
        pct = 0 if hp_max == 0 else hp / hp_max
        cor = VERDE if pct > 0.5 else LARANJA if pct > 0.25 else VERMELHO
        pygame.draw.rect(self.tela, cor, (x, y, int(w * pct), h))
        pygame.draw.rect(self.tela, AMARELO, rect, 2)

        info = self.fonte_nome.render(f"{nome} {hp}/{hp_max}", True, BRANCO)
        if alinha_esquerda:
            self.tela.blit(info, (x, y - 22))
        else:
            self.tela.blit(info, (x + w - info.get_width(), y - 22))

    def _draw_timer_bar(self):
        """Desenha a barra de tempo restante para a pergunta."""
        cs = self.combat_state
        if not cs.questao or cs.aguardando:
            return

        pct = cs.timer_resposta / TEMPO_RESPOSTA
        cor = VERDE if pct > 0.5 else LARANJA if pct > 0.25 else VERMELHO
        larg = 320
        x = self.largura // 2 - larg // 2
        
        
        y = 104

        pygame.draw.rect(self.tela, (30, 20, 50), (x, y, larg, 8))
        pygame.draw.rect(self.tela, cor, (x, y, int(larg * pct), 8))
        pygame.draw.rect(self.tela, CINZA, (x, y, larg, 8), 1)

        # Contador da direita para a esquerda
        seg = math.ceil(cs.timer_resposta)
        txt = self.fonte_hud.render(f"{seg}s", True, cor)
        self.tela.blit(txt, (x - txt.get_width() - 10, y - 2))
    
    
    def _draw_personagens(self):
        """Posiciona e desenha os sprites do herói e do chefe."""
        cs = self.combat_state
        if cs.hero:
            cs.hero.rect.midbottom = (190, Y_DIVISOR - 8)
            cs.hero.draw(self.tela)
        if cs.boss:
            cs.boss.rect.midbottom = (950, Y_DIVISOR - 8)
            cs.boss.draw(self.tela)

    def _draw_pergunta(self, tempo):
        """Renderiza a caixa de pergunta e suas opções."""
        cs = self.combat_state
        if not cs.questao:
            txt = self.fonte_menu.render("CARREGANDO QUESTÃO...", True, CINZA)
            self.tela.blit(txt, (self.largura // 2 - txt.get_width() // 2, Y_DIVISOR + 20))
            return

        y_area = Y_DIVISOR + 8
        pad = 14
        fundo_rect = pygame.Rect(30, y_area - pad, self.largura - 60, self.altura - y_area - 30)
        pygame.draw.rect(self.tela, (10, 6, 22, 200), fundo_rect)
        pygame.draw.rect(self.tela, VERMELHO, fundo_rect, 2)

        tema = cs.boss_data.get("tema", "").upper() if cs.boss_data else ""
        tag = self.fonte_hud.render(f"TEMA: {tema}", True, CINZA)
        self.tela.blit(tag, (fundo_rect.x + 12, fundo_rect.y + 6))

        y_atual = y_area + 18
        self._desenhar_texto(cs.questao.get("pergunta", ""), fundo_rect.x + 12, y_atual, fundo_rect.width - 24, self.fonte_pergunta, BRANCO)
        y_atual += self._altura_texto(cs.questao.get("pergunta", ""), fundo_rect.width - 24, self.fonte_pergunta)

        codigo = cs.questao.get("codigo")
        if codigo and str(codigo).strip().lower() not in ("null", "none", ""):
            linhas = str(codigo).split("\n")
            y_codigo = y_atual + 10
            alt_bloco = len(linhas) * 22 + 10
            codigo_rect = pygame.Rect(fundo_rect.x + 20, y_codigo - 4, fundo_rect.width - 40, alt_bloco)
            pygame.draw.rect(self.tela, (18, 12, 35), codigo_rect)
            pygame.draw.rect(self.tela, (50, 30, 80), codigo_rect, 1)
            for i, linha in enumerate(linhas):
                cod = self.fonte_codigo.render(linha, True, AMARELO)
                self.tela.blit(cod, (codigo_rect.x + 10, y_codigo + i * 22))
            y_atual = y_codigo + alt_bloco + 10
        else:
            y_atual += 10

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

        inst = self.fonte_hud.render("↑↓ NAVEGAR  ENTER CONFIRMAR", True, CINZA)
        self.tela.blit(inst, (self.largura // 2 - inst.get_width() // 2, self.altura - 70))

    def _draw_mensagem(self, tempo):
        """Exibe mensagens temporárias de feedback na tela."""
        cs = self.combat_state
        if not cs.mensagem or cs.mensagem_timer <= 0:
            return

        alpha = int(min(255, cs.mensagem_timer / TIMER_MENSAGEM * 255))
        overlay = pygame.Surface((self.largura, 44), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, max(0, alpha // 2)))
        self.tela.blit(overlay, (0, 108))

        pulso = 0.7 + 0.3 * math.sin(tempo * 8)
        cor = tuple(min(255, int(c * pulso)) for c in cs.mensagem_cor)
        txt = self.fonte_menu.render(cs.mensagem, True, cor)
        self.tela.blit(txt, (self.largura // 2 - txt.get_width() // 2, 116))

    def _desenhar_texto(self, texto, x, y, largura, fonte, cor):
        """Desenha um bloco de texto com quebra de linha automática."""
        linhas = self._quebrar_texto(texto, largura, fonte)
        for i, linha in enumerate(linhas):
            render = fonte.render(linha, True, cor)
            self.tela.blit(render, (x, y + i * fonte.get_height()))

    def _quebrar_texto(self, texto, largura, fonte):
        """Divide uma string em linhas de acordo com a largura máxima."""
        linhas = []
        palavras = texto.split(' ')
        linha_atual = ''
        for palavra in palavras:
            if fonte.size(linha_atual + ' ' + palavra)[0] < largura:
                linha_atual += ' ' + palavra
            else:
                linhas.append(linha_atual.strip())
                linha_atual = palavra
        linhas.append(linha_atual.strip())
        return linhas

    def _altura_texto(self, texto, largura, fonte):
        """Calcula a altura total de um bloco de texto."""
        linhas = self._quebrar_texto(texto, largura, fonte)
        return len(linhas) * fonte.get_height()

    def _draw_orbe_mana(self, cx, cy, pct, tempo):
        """Renderiza o orbe decorativo da barra de mana."""
        raio = 7
        cor_base = (40, 60, 140)
        cor_cheia = (120, 200, 255)
        cor = tuple(int(cor_base[i] + (cor_cheia[i] - cor_base[i]) * pct) for i in range(3))

        if pct >= 0.999:
            glow_raio = raio + 3 + int(2 * math.sin(tempo * 5))
            glow_surf = pygame.Surface((glow_raio * 2 + 4, glow_raio * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*cor_cheia, 90), (glow_raio + 2, glow_raio + 2), glow_raio)
            self.tela.blit(glow_surf, (cx - glow_raio - 2, cy - glow_raio - 2))

        pygame.draw.circle(self.tela, (10, 10, 28), (cx, cy), raio + 2)
        pygame.draw.circle(self.tela, cor, (cx, cy), raio)
        pygame.draw.circle(self.tela, (200, 220, 255), (cx, cy), raio, 1)

    def _draw_mana_e_skills(self):
        """Desenha a interface da barra de mana e indicadores de custo."""
        hero = self.combat_state.hero
        tempo = pygame.time.get_ticks() / 1000
        larg_barra = 200
        alt_barra = 10
        x_barra = self.largura // 2 - larg_barra // 2
        y_barra = 136

        pct_mana = 0 if hero.max_mana == 0 else hero.mana / hero.max_mana
        cor_baixa = (40, 60, 140)
        cor_alta = (120, 200, 255)
        cor_mana = tuple(int(cor_baixa[i] + (cor_alta[i] - cor_baixa[i]) * pct_mana) for i in range(3))

        fundo_rect = pygame.Rect(x_barra, y_barra, larg_barra, alt_barra)
        pygame.draw.rect(self.tela, (8, 8, 28), fundo_rect, border_radius=alt_barra // 2)

        if pct_mana > 0:
            preench_rect = pygame.Rect(x_barra, y_barra, max(alt_barra, int(larg_barra * pct_mana)), alt_barra)
            pygame.draw.rect(self.tela, cor_mana, preench_rect, border_radius=alt_barra // 2)
            brilho_w = max(0, preench_rect.width - 4)
            if brilho_w > 0:
                brilho_surf = pygame.Surface((brilho_w, alt_barra // 3), pygame.SRCALPHA)
                brilho_surf.fill((255, 255, 255, 60))
                self.tela.blit(brilho_surf, (x_barra + 2, y_barra + 1))

        for custo in (20, 30, 40):
            if 0 < custo < hero.max_mana:
                x_marca = x_barra + int(larg_barra * (custo / hero.max_mana))
                pygame.draw.line(self.tela, (15, 15, 40), (x_marca, y_barra), (x_marca, y_barra + alt_barra), 1)

        if pct_mana >= 0.999:
            pulso = 0.6 + 0.4 * math.sin(tempo * 5)
            cor_borda = tuple(int(c * pulso) for c in cor_alta)
        else:
            cor_borda = (80, 100, 200)
        pygame.draw.rect(self.tela, cor_borda, fundo_rect, 2, border_radius=alt_barra // 2)
        self._draw_orbe_mana(x_barra - 16, y_barra + alt_barra // 2, pct_mana, tempo)

        mana_txt = self.fonte_hud.render(f"{hero.mana}/{hero.max_mana}", True, AZUL_CLARO)
        self.tela.blit(mana_txt, (x_barra + larg_barra + 8, y_barra - 2))

    def _draw_skills_canto(self, tempo):
        """Renderiza a lista de habilidades disponíveis e seus status."""
        hero = self.combat_state.hero
        skills = [
            ("Q", "DICA", 30, hero.mana >= 30, (255, 200, 40)),
            ("W", "+TEMPO", 20, hero.mana >= 20, (40, 200, 200)),
            ("E", "ESCUDO", 40, hero.mana >= 40 and not hero.escudo_ativo, (80, 160, 255)),
        ]
        largura_box = 118
        altura_box = 24
        espaco = 5
        x = self.largura - largura_box - 16
        y = 16

        for tecla, nome, custo, disponivel, cor in skills:
            rect = pygame.Rect(x, y, largura_box, altura_box)
            if disponivel:
                cor_fundo = tuple(int(c * 0.16) for c in cor)
                cor_borda = cor
                cor_texto = cor
            else:
                cor_fundo = (16, 14, 24)
                cor_borda = (55, 55, 60)
                cor_texto = (95, 95, 100)

            pygame.draw.rect(self.tela, cor_fundo, rect, border_radius=4)
            pygame.draw.rect(self.tela, cor_borda, rect, 1, border_radius=4)

            label = self.fonte_hud.render(f"[{tecla}] {nome}", True, cor_texto)
            self.tela.blit(label, (rect.x + 6, rect.y + (altura_box - label.get_height()) // 2))

            custo_txt = self.fonte_hud.render(str(custo), True, cor_texto)
            self.tela.blit(custo_txt, (rect.right - custo_txt.get_width() - 6, rect.y + (altura_box - custo_txt.get_height()) // 2))
            y += altura_box + espaco

        if hero.escudo_ativo:
            escudo_txt = self.fonte_hud.render("🛡 ATIVO", True, AZUL_CLARO)
            self.tela.blit(escudo_txt, (x + largura_box - escudo_txt.get_width(), y + 2))

    def _draw_keycap(self, rect, tecla, disponivel, cor, tempo, seed=0):
        """Desenha um botão estilizado de habilidade."""
        if disponivel:
            pulso = 0.75 + 0.25 * math.sin(tempo * 3 + seed)
            cor_topo = tuple(int(min(255, c * 1.4 * pulso)) for c in cor)
            cor_corpo = tuple(int(c * 0.5) for c in cor)
            cor_sombra = tuple(int(c * 0.22) for c in cor)
            cor_letra = (12, 12, 16)
            cor_borda = cor
            halo_raio = max(rect.width, rect.height) // 2 + 6
            halo_surf = pygame.Surface((halo_raio * 2, halo_raio * 2), pygame.SRCALPHA)
            pygame.draw.circle(halo_surf, (*cor, 45), (halo_raio, halo_raio), halo_raio)
            self.tela.blit(halo_surf, (rect.centerx - halo_raio, rect.centery - halo_raio))
        else:
            cor_topo = (60, 60, 68)
            cor_corpo = (35, 35, 42)
            cor_sombra = (18, 18, 22)
            cor_letra = (95, 95, 100)
            cor_borda = (55, 55, 60)

        pygame.draw.rect(self.tela, cor_sombra, rect.move(0, 3), border_radius=7)
        pygame.draw.rect(self.tela, cor_corpo, rect, border_radius=7)
        topo_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.width - 6, int(rect.height * 0.5))
        pygame.draw.rect(self.tela, cor_topo, topo_rect, border_radius=5)
        pygame.draw.rect(self.tela, cor_borda, rect, 2, border_radius=7)

        letra = self.fonte_menu.render(tecla, True, cor_letra)
        self.tela.blit(letra, (rect.centerx - letra.get_width() // 2, rect.centery - letra.get_height() // 2 - 1))