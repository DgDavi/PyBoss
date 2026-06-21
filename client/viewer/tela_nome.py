import pygame
import math
from viewer.base import TelaBase, AMARELO, CINZA, VERMELHO

AMARELO_ESC = (120, 90, 10)
BRANCO = (220, 220, 220)


class TelaNome(TelaBase):
    def __init__(self, tela):
        super().__init__(tela)
        self.nome = ""

        self.fonte_titulo = pygame.font.SysFont("arialblack", 72)
        self.fonte_subtitulo = pygame.font.SysFont("arialblack", 22)
        self.fonte_input = pygame.font.SysFont("consolas", 28)

    def handle_event(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN and len(self.nome) >= 3:
                self.proximo = "menu"
            elif evento.key == pygame.K_BACKSPACE:
                self.nome = self.nome[:-1]
            else:
                if len(self.nome) < 15 and evento.unicode.isprintable():
                    self.nome += evento.unicode

    def draw(self):
        tempo = pygame.time.get_ticks() / 1000
        self.desenhar_degradê()
        self.desenhar_grade(tempo)
        self._titulo(tempo)
        self._input(tempo)
        self.desenhar_rodape(tempo)
        self.desenhar_borda()
        self.desenhar_scanlines()

    def _titulo(self, tempo):
        pulso  = 0.85 + 0.15 * math.sin(tempo * 3)
        cor    = tuple(int(c * pulso) for c in AMARELO)
        sombra = self.fonte_titulo.render("PyBoss", True, (60, 30, 0))
        self.tela.blit(sombra, (self.largura // 2 - sombra.get_width() // 2 + 4, 84))
        titulo = self.fonte_titulo.render("PyBoss", True, cor)
        self.tela.blit(titulo, (self.largura // 2 - titulo.get_width() // 2, 80))
        
        
        sub = self.fonte_subtitulo.render("— ALQUIMIA ARCANA —", True, CINZA)
        self.tela.blit(sub, (self.largura // 2 - sub.get_width() // 2, 175))
        
        
        pygame.draw.line(self.tela, VERMELHO,
                         (self.largura // 2 - 180, 215),
                         (self.largura // 2 + 180, 215), 2)
        

    def _input(self, tempo):
        prompt = self.fonte_hud.render("INSIRA SEU NOME, ALQUIMISTA:", True, BRANCO)
        self.tela.blit(prompt, (self.largura // 2 - prompt.get_width() // 2, 240))

        larg, alt = 380, 48
        caixa = pygame.Rect(self.largura // 2 - larg // 2, 272, larg, alt)
        pygame.draw.rect(self.tela, (15, 10, 30), caixa)
        pisca = int(tempo * 3) % 2 == 0
        cor_borda = AMARELO if pisca else AMARELO_ESC
        pygame.draw.rect(self.tela, cor_borda, caixa, 2)

        texto = self.fonte_input.render(self.nome, True, AMARELO)
        self.tela.blit(texto, (caixa.x + 14, caixa.y + 10))

        if pisca:
            cx = caixa.x + 14 + texto.get_width() + 2
            pygame.draw.rect(self.tela, AMARELO, (cx, caixa.y + 10, 3, 28))

        if len(self.nome) >= 3:
            if int(tempo * 2) % 2 == 0:
                enter = self.fonte_hud.render("► APERTE ENTER PARA CONTINUAR ◄", True, AMARELO)
                self.tela.blit(enter, (self.largura // 2 - enter.get_width() // 2, 342))
        else:
            aviso = self.fonte_hud.render("(mínimo 3 caracteres)", True, CINZA)
            self.tela.blit(aviso, (self.largura // 2 - aviso.get_width() // 2, 342))
