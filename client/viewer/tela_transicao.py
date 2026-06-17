# client/viewer/tela_transicao.py

import math
import pygame
from viewer.base import TelaBase, AMARELO, CINZA, VERMELHO

BRANCO = (220, 220, 220)
VERDE = (40, 190, 80)
LARANJA = (220, 140, 20)

class TelaTransicao(TelaBase):
    """Exibe a tela de transição entre chefes, mostrando resultados e o próximo desafio."""

    def __init__(self, tela, boss_atual: dict, proximo_boss: dict,
                 nivel_atual: int, stats: dict):
        """Inicializa os dados da transição e os elementos visuais."""
        super().__init__(tela)

        self.boss_atual = boss_atual
        self.proximo_boss = proximo_boss
        self.nivel_atual = nivel_atual
        self.stats = stats

        self.fonte_titulo = pygame.font.SysFont("arialblack", 36)
        self.fonte_grande = pygame.font.SysFont("arialblack", 26)
        self.fonte_media = pygame.font.SysFont("consolas", 20)
        self.fonte_pequena = pygame.font.SysFont("consolas", 16)

        self.sprite_atual = self._carregar_sprite(boss_atual)
        self.sprite_proximo = self._carregar_sprite(proximo_boss)

        self.alpha_overlay = 255
        self.pronto = False
        self._tempo_inicio = pygame.time.get_ticks() / 1000

    def _carregar_sprite(self, boss_data: dict):
        """Instancia o boss correspondente ao tema para exibição de sprite."""
        from engine.utils import normalizar_texto
        from engine.entities import (
            BossClasses, BossDicts, BossExceptions,
            BossLists, BossLoops, BossRecursion,
        )
        MAPA = {
            "classes": BossClasses,
            "dicionarios": BossDicts,
            "excecoes": BossExceptions,
            "listas": BossLists,
            "loops": BossLoops,
            "recursao": BossRecursion,
        }
        tema = normalizar_texto(boss_data.get("tema", ""))
        classe_boss = MAPA.get(tema, BossLoops)
        boss = classe_boss()
        boss.name = boss_data.get("nome", boss.name)
        return boss

    def handle_event(self, evento):
        """Processa a entrada do jogador para avançar a tela."""
        if not self.pronto:
            return
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.proximo = "batalha"

    def update(self, dt=None):
        """Atualiza a animação de transição e o estado de prontidão."""
        if dt is None:
            dt = 1 / 60

        if self.alpha_overlay > 0:
            self.alpha_overlay = max(0, self.alpha_overlay - int(300 * dt))

        tempo = pygame.time.get_ticks() / 1000
        if tempo - self._tempo_inicio > 1.5 and not self.pronto:
            self.pronto = True

    def draw(self):
        """Renderiza todos os elementos da tela de transição."""
        tempo = pygame.time.get_ticks() / 1000
        self.desenhar_degradê()
        self.desenhar_grade(tempo)
        self._draw_titulo(tempo)
        self._draw_boss_derrotado(tempo)
        self._draw_proximo_boss(tempo)
        self._draw_stats()
        self._draw_instrucao(tempo)
        self.desenhar_borda()
        self.desenhar_scanlines()

        if self.alpha_overlay > 0:
            overlay = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, self.alpha_overlay))
            self.tela.blit(overlay, (0, 0))

    def _draw_titulo(self, tempo):
        """Desenha o título da tela com efeito de pulso."""
        pulso = 0.85 + 0.15 * math.sin(tempo * 3)
        cor = tuple(int(c * pulso) for c in VERDE)
        titulo = self.fonte_titulo.render("BOSS DERROTADO!", True, cor)
        self.tela.blit(titulo, (self.largura // 2 - titulo.get_width() // 2, 20))
        pygame.draw.line(self.tela, VERDE, (self.largura // 2 - 200, 66), (self.largura // 2 + 200, 66), 2)

    def _draw_boss_derrotado(self, tempo):
        """Renderiza as informações do boss que acabou de ser vencido."""
        x_centro = self.largura // 4
        label = self.fonte_pequena.render("DERROTADO", True, VERMELHO)
        self.tela.blit(label, (x_centro - label.get_width() // 2, 80))

        if self.sprite_atual:
            sprite_surf = pygame.Surface(self.sprite_atual.sprite.get_size(), pygame.SRCALPHA)
            sprite_surf.blit(self.sprite_atual.sprite, (0, 0))
            sprite_surf.set_alpha(120)
            x = x_centro - self.sprite_atual.rect.width // 2
            self.tela.blit(sprite_surf, (x, 100))

        nome = self.fonte_grande.render(self.boss_atual.get("nome", "???"), True, VERMELHO)
        self.tela.blit(nome, (x_centro - nome.get_width() // 2, 270))

        tema = self.fonte_pequena.render(f"TEMA: {self.boss_atual.get('tema','').upper()}", True, CINZA)
        self.tela.blit(tema, (x_centro - tema.get_width() // 2, 300))

        descricao = self.boss_atual.get("descricao", "")
        if descricao:
            self._desenhar_texto_centralizado(descricao, x_centro, 325, 300, self.fonte_pequena, CINZA)

    def _draw_proximo_boss(self, tempo):
        """Renderiza a prévia do próximo desafiante."""
        x_centro = (self.largura * 3) // 4
        if int(tempo * 2) % 2 == 0:
            label = self.fonte_pequena.render("PRÓXIMO DESAFIANTE", True, AMARELO)
            self.tela.blit(label, (x_centro - label.get_width() // 2, 80))

        if self.sprite_proximo:
            sprite_surf = pygame.Surface(self.sprite_proximo.sprite.get_size(), pygame.SRCALPHA)
            sprite_surf.blit(self.sprite_proximo.sprite, (0, 0))
            escuro = pygame.Surface(self.sprite_proximo.sprite.get_size(), pygame.SRCALPHA)
            escuro.fill((0, 0, 0, 160))
            sprite_surf.blit(escuro, (0, 0))
            x = x_centro - self.sprite_proximo.rect.width // 2
            self.tela.blit(sprite_surf, (x, 100))

        nome = self.fonte_grande.render(self.proximo_boss.get("nome", "???"), True, AMARELO)
        self.tela.blit(nome, (x_centro - nome.get_width() // 2, 270))

        tema = self.fonte_pequena.render(f"TEMA: {self.proximo_boss.get('tema','').upper()}", True, CINZA)
        self.tela.blit(tema, (x_centro - tema.get_width() // 2, 300))

        hp = self.fonte_pequena.render(f"HP: {self.proximo_boss.get('hp', '???')}", True, LARANJA)
        self.tela.blit(hp, (x_centro - hp.get_width() // 2, 322))

        fraqueza = self.fonte_pequena.render(f"FRAQUEZA: {self.proximo_boss.get('fraqueza','???').upper()}", True, VERDE)
        self.tela.blit(fraqueza, (x_centro - fraqueza.get_width() // 2, 344))

    def _draw_stats(self):
        """Exibe o resumo da performance na batalha anterior."""
        y = 390
        cx = self.largura // 2
        label = self.fonte_pequena.render("─── RESULTADO DA BATALHA ───", True, CINZA)
        self.tela.blit(label, (cx - label.get_width() // 2, y))

        itens = [
            ("NÍVEL ALCANÇADO", str(self.nivel_atual), AMARELO),
            ("MAIOR COMBO", f"x{self.stats.get('maior_combo', 0)}", VERDE),
            ("TEMAS COM ERRO", ", ".join(self.stats.get("temas_errados", [])) or "nenhum", LARANJA),
        ]

        for i, (chave, valor, cor) in enumerate(itens):
            chave_txt = self.fonte_pequena.render(f"{chave}:", True, CINZA)
            valor_txt = self.fonte_pequena.render(valor, True, cor)
            x_chave = cx - 180
            x_valor = cx + 10
            y_linha = y + 24 + i * 24
            self.tela.blit(chave_txt, (x_chave, y_linha))
            self.tela.blit(valor_txt, (x_valor, y_linha))

    def _draw_instrucao(self, tempo):
        """Exibe a instrução para o jogador prosseguir."""
        if not self.pronto:
            return
        if int(tempo * 2) % 2 == 0:
            txt = self.fonte_pequena.render("► ENTER PARA ENFRENTAR O PRÓXIMO BOSS ◄", True, AMARELO)
            self.tela.blit(txt, (self.largura // 2 - txt.get_width() // 2, self.altura - 60))

    def _desenhar_texto_centralizado(self, texto, cx, y, largura, fonte, cor):
        """Desenha um bloco de texto centralizado com quebra automática."""
        palavras = texto.split()
        linha_atual = ""
        linhas = []
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
        for linha in linhas:
            surf = fonte.render(linha, True, cor)
            self.tela.blit(surf, (cx - surf.get_width() // 2, y))
            y += surf.get_height() + 4