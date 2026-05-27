import pygame
import sys

# === Inicialização ===
pygame.init()
pygame.font.init()  # Garante que o módulo de texto foi carregado

# === Configurações da Janela ===
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("PyBoss — Alquimia Arcana")

# === Relógio ===
relogio = pygame.time.Clock()
FPS = 60

# === Definição de Cores (Vibe Retrô) ===
PRETO = (10, 10, 15)        # Fundo quase preto
ROXO_ESCURO = (40, 20, 60)  # Contorno de caixas
VERDE_PIXEL = (50, 255, 100) # Texto principal e brilho
BRANCO_FOSCO = (200, 200, 200) # Texto secundário

# === Configuração de Fontes ===
# Para o estilo pixelado, o ideal é usar uma fonte .ttf de pixel art.
# Como não temos uma ainda, usaremos a padrão do sistema em negrito.
# Você pode baixar uma (ex: 'Press Start 2P') e colocar na pasta assets.
fonte_titulo = pygame.font.SysFont("arialblack", 60)
fonte_input = pygame.font.SysFont("consolas", 32)
fonte_hud = pygame.font.SysFont("consolas", 20)

# === Variáveis do Estado do Input ===
nome_jogador = ""
input_ativo = True  # O campo de texto começa selecionado
cor_borda_input = VERDE_PIXEL  # Cor quando ativo

# === Função de Desenho ===
def desenhar_tela_inicial(superficie, nome):
    superficie.fill(PRETO)  # Limpa o fundo

    # 1. Título do Jogo (centralizado)
    texto_titulo = fonte_titulo.render("PYBOSS", True, VERDE_PIXEL)
    rect_titulo = texto_titulo.get_rect(center=(LARGURA // 2, ALTURA // 4))
    superficie.blit(texto_titulo, rect_titulo)

    # 2. Subtítulo
    texto_subtitulo = fonte_hud.render("Alquimia Arcana", True, BRANCO_FOSCO)
    rect_subtitulo = texto_subtitulo.get_rect(center=(LARGURA // 2, ALTURA // 4 + 50))
    superficie.blit(texto_subtitulo, rect_subtitulo)

    # 3. Prompt do Nome
    texto_prompt = fonte_input.render("COLOQUE SEU NOME, ALQUIMISTA:", True, BRANCO_FOSCO)
    rect_prompt = texto_prompt.get_rect(center=(LARGURA // 2, ALTURA // 2 - 40))
    superficie.blit(texto_prompt, rect_prompt)

    # 4. Caixa de Input e Texto Digitado
    # Define a caixa de texto
    largura_input = 400
    altura_input = 50
    retangulo_input = pygame.Rect((LARGURA // 2 - largura_input // 2, ALTURA // 2), (largura_input, altura_input))
    
    # Desenha o fundo da caixa
    pygame.draw.rect(superficie, ROXO_ESCURO, retangulo_input)
    # Desenha a borda da caixa
    pygame.draw.rect(superficie, cor_borda_input, retangulo_input, 3)

    # Renderiza o texto que o jogador já digitou
    superficie_nome = fonte_input.render(nome, True, VERDE_PIXEL)
    # Garante que o texto fique centralizado na caixa
    rect_nome = superficie_nome.get_rect(center=retangulo_input.center)
    superficie.blit(superficie_nome, rect_nome)

    # 5. Instrução para começar
    if len(nome) > 2:  # Só mostra se tiver pelo menos 3 letras
        texto_start = fonte_hud.render("APERTE [ENTER] PARA COMEÇAR O RITUAL", True, VERDE_PIXEL)
        rect_start = texto_start.get_rect(center=(LARGURA // 2, ALTURA // 2 + 100))
        
        # Efeito de piscar simples baseado no tempo
        if pygame.time.get_ticks() % 1000 < 500:
            superficie.blit(texto_start, rect_start)

# === Loop Principal ===
rodando = True
while rodando:
    # 1. Tratamento de Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        
        # Gerencia a digitação
        if evento.type == pygame.KEYDOWN:
            if input_ativo:
                if evento.key == pygame.K_RETURN:  # Apertou Enter
                    if len(nome_jogador) > 2:
                        print(f"Iniciando ritual para: {nome_jogador}")
                        # FUTURAMENTE: Mudar o estado do jogo para a Batalha
                    else:
                        print("Nome muito curto!")
                elif evento.key == pygame.K_BACKSPACE:  # Apagar
                    nome_jogador = nome_jogador[:-1]
                else:
                    # Adiciona o caractere digitado (se não for muito longo)
                    if len(nome_jogador) < 15 and evento.unicode.isprintable():
                        nome_jogador += evento.unicode

    # 2. Atualização da Lógica (neste caso, é visual)
    # Faz a borda do input piscar quando ativo
    if input_ativo:
        if pygame.time.get_ticks() % 1200 < 600:
            cor_borda_input = VERDE_PIXEL
        else:
            cor_borda_input = BRANCO_FOSCO
    else:
        cor_borda_input = ROXO_ESCURO

    # 3. Desenho
    desenhar_tela_inicial(tela, nome_jogador)

    # Atualiza a tela
    pygame.display.flip()
    relogio.tick(FPS)

# === Encerramento ===
pygame.quit()
sys.exit()