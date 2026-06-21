import pygame

from engine.game import GameManager
from pathlib import Path

AUDIO = Path(__file__).parent / 'assets' / 'audio' / 'trilha.mp3'

def main():
	pygame.init()
	pygame.font.init()
	pygame.mixer.init()

	pygame.mixer.music.load(str(AUDIO))
	pygame.mixer.music.set_volume(0.5)
	pygame.mixer.music.play(-1)

	largura, altura = 1280, 720
	tela = pygame.display.set_mode((largura, altura))
	pygame.display.set_caption("PyBoss")

	relogio = pygame.time.Clock()
	fps = 60

	game = GameManager(tela)
	rodando = True

	while rodando:
		for evento in pygame.event.get():
			if evento.type == pygame.QUIT:
				rodando = False
			else:
				game.handle_event(evento)

		game.update()
		game.draw()

		pygame.display.flip()
		relogio.tick(fps)

	pygame.quit()


if __name__ == "__main__":
	main()