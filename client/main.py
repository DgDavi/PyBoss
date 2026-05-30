import pygame
import sys
import math

# === Inicialização ===
pygame.init()
pygame.font.init()

# === Configurações da Janela ===
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("PyBoss")

# === Relógio ===
relogio = pygame.time.Clock()
FPS = 60

# === Cores ===
PRETO        = (5, 5, 15)
AZUL_ESCURO  = (10, 10, 40)
VERM_ESCURO  = (40, 5, 5)
AMARELO      = (240, 192, 40)
AMARELO_ESC  = (120, 90, 10)
BRANCO       = (220, 220, 220)
CINZA        = (80, 75, 100)
VERMELHO     = (200, 30, 30)
ROXO         = (60, 20, 100)

# === Fontes ===
fonte_titulo   = pygame.font.SysFont("arialblack", 72)
fonte_input    = pygame.font.SysFont("consolas", 28)
fonte_hud      = pygame.font.SysFont("consolas", 16)

# === Estado ===
nome_jogador = ""


def desenhar_degradê():
    """Fundo degradê azul escuro → vermelho escuro."""
    for y in range(ALTURA):
        t = y / ALTURA
        r = int(AZUL_ESCURO[0] + (VERM_ESCURO[0] - AZUL_ESCURO[0]) * t)
        g = int(AZUL_ESCURO[1] + (VERM_ESCURO[1] - AZUL_ESCURO[1]) * t)
        b = int(AZUL_ESCURO[2] + (VERM_ESCURO[2] - AZUL_ESCURO[2]) * t)
        pygame.draw.line(tela, (r, g, b), (0, y), (LARGURA, y))


def desenhar_grade(tempo):
    """Grade de perspectiva estilo fliperama com scroll."""
    cor = (30, 15, 60)
    ponto_x = LARGURA // 2
    ponto_y = ALTURA // 2

    # Linhas verticais convergindo ao centro
    for x in range(0, LARGURA + 1, 60):
        pygame.draw.line(tela, cor, (ponto_x, ponto_y), (x, ALTURA), 1)

    # Linhas horizontais com scroll
    espacamento = 40
    offset = int(tempo * 50) % espacamento
    for y in range(ALTURA // 2, ALTURA + espacamento, espacamento):
        pygame.draw.line(tela, cor, (0, y - offset), (LARGURA, y - offset), 1)


def desenhar_borda():
    """Borda dupla estilo arcade."""
    pygame.draw.rect(tela, ROXO,    (0, 0, LARGURA, ALTURA), 6)
    pygame.draw.rect(tela, AMARELO, (6, 6, LARGURA - 12, ALTURA - 12), 2)


def desenhar_titulo(tempo):
    """Título com sombra e pulso."""
    pulso = 0.85 + 0.15 * math.sin(tempo * 3)
    r = int(AMARELO[0] * pulso)
    g = int(AMARELO[1] * pulso)
    b = int(AMARELO[2] * pulso)

    # Sombra
    sombra = fonte_titulo.render("PyBoss", True, (60, 30, 0))
    tela.blit(sombra, (LARGURA // 2 - sombra.get_width() // 2 + 4, 84))

    # Título
    titulo = fonte_titulo.render("PyBoss", True, (r, g, b))
    tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 80))

    # Linha decorativa
    pygame.draw.line(tela, VERMELHO,
                     (LARGURA // 2 - 180, 192),
                     (LARGURA // 2 + 180, 192), 2)


def desenhar_input(nome, tempo):
    """Campo de nome do jogador."""
    # Prompt
    prompt = fonte_hud.render("INSIRA SEU NOME, ALQUIMISTA:", True, BRANCO)
    tela.blit(prompt, (LARGURA // 2 - prompt.get_width() // 2, 240))

    # Caixa
    larg, alt = 380, 48
    caixa = pygame.Rect(LARGURA // 2 - larg // 2, 272, larg, alt)
    pygame.draw.rect(tela, (15, 10, 30), caixa)

    # Borda piscante
    pisca = int(tempo * 3) % 2 == 0
    cor_borda = AMARELO if pisca else AMARELO_ESC
    pygame.draw.rect(tela, cor_borda, caixa, 2)

    # Texto digitado
    texto = fonte_input.render(nome, True, AMARELO)
    tela.blit(texto, (caixa.x + 14, caixa.y + 10))

    # Cursor piscante após o texto
    if pisca:
        cursor_x = caixa.x + 14 + texto.get_width() + 2
        pygame.draw.rect(tela, AMARELO, (cursor_x, caixa.y + 10, 3, 28))

    # Instrução de confirmação
    if len(nome) >= 3:
        if int(tempo * 2) % 2 == 0:
            enter = fonte_hud.render("► APERTE ENTER PARA COMEÇAR ◄", True, AMARELO)
            tela.blit(enter, (LARGURA // 2 - enter.get_width() // 2, 342))
    else:
        aviso = fonte_hud.render("(mínimo 3 caracteres)", True, CINZA)
        tela.blit(aviso, (LARGURA // 2 - aviso.get_width() // 2, 342))


def desenhar_scanlines():
    """Scanlines para efeito CRT."""
    scanline = pygame.Surface((LARGURA, 1), pygame.SRCALPHA)
    scanline.fill((0, 0, 0, 50))
    for y in range(0, ALTURA, 3):
        tela.blit(scanline, (0, y))


# === Loop Principal ===
rodando = True
while rodando:
    tempo = pygame.time.get_ticks() / 1000

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                if len(nome_jogador) >= 3:
                    print(f"Iniciando jogo: {nome_jogador}")
                    # FUTURAMENTE: mudar estado para Batalha
            elif evento.key == pygame.K_BACKSPACE:
                nome_jogador = nome_jogador[:-1]
            else:
                if len(nome_jogador) < 15 and evento.unicode.isprintable():
                    nome_jogador += evento.unicode

    # Desenho
    desenhar_degradê()
    desenhar_grade(tempo)
    desenhar_titulo(tempo)
    desenhar_input(nome_jogador, tempo)
    desenhar_borda()
    desenhar_scanlines()  # sempre por último

    pygame.display.flip()
    relogio.tick(FPS)

pygame.quit()
sys.exit()