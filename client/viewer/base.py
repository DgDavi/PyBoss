import pygame
import math

AZUL_ESCURO = (10, 10, 40)
VERM_ESCURO = (40, 5, 5)
AMARELO = (240, 192, 40)
CINZA = (80, 75, 100)
VERMELHO = (200, 30, 30)
ROXO = (60, 20, 100)


class TelaBase:
    def __init__(self, tela):
        self.tela    = tela
        self.largura = tela.get_width()
        self.altura  = tela.get_height()
        self.proximo = None  # sinaliza transição para o GameManager

        self.fonte_hud = pygame.font.SysFont("consolas", 16)

    def handle_event(self, evento):
        raise NotImplementedError

    def update(self):
        pass

    def draw(self):
        raise NotImplementedError

    # ── Elementos visuais compartilhados ─

    def desenhar_degradê(self):
        for y in range(self.altura):
            t = y / self.altura
            r = int(AZUL_ESCURO[0] + (VERM_ESCURO[0] - AZUL_ESCURO[0]) * t)
            g = int(AZUL_ESCURO[1] + (VERM_ESCURO[1] - AZUL_ESCURO[1]) * t)
            b = int(AZUL_ESCURO[2] + (VERM_ESCURO[2] - AZUL_ESCURO[2]) * t)
            pygame.draw.line(self.tela, (r, g, b), (0, y), (self.largura, y))

    def desenhar_grade(self, tempo):
        cor = (30, 15, 60)
        cx  = self.largura // 2
        cy  = self.altura  // 2
        for x in range(0, self.largura + 1, 60):
            pygame.draw.line(self.tela, cor, (cx, cy), (x, self.altura), 1)
        esp    = 40
        offset = int(tempo * 50) % esp
        for y in range(self.altura // 2, self.altura + esp, esp):
            pygame.draw.line(self.tela, cor, (0, y - offset), (self.largura, y - offset), 1)

    def desenhar_borda(self):
        pygame.draw.rect(self.tela, ROXO,    (0, 0, self.largura, self.altura), 6)
        pygame.draw.rect(self.tela, AMARELO, (6, 6, self.largura - 12, self.altura - 12), 2)

    def desenhar_rodape(self, tempo):
        pass

    def desenhar_scanlines(self):
        scanline = pygame.Surface((self.largura, 1), pygame.SRCALPHA)
        scanline.fill((0, 0, 0, 50))
        for y in range(0, self.altura, 3):
            self.tela.blit(scanline, (0, y))