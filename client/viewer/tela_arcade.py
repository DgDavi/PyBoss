# client/viewer/tela_arcade.py

import pygame
from viewer.tela_batalha import TelaBatalha
from engine.arcade import ArcadeState

# Cores do HUD Cyberpunk
VERDE = (0, 255, 65)
AMARELO = (255, 204, 0)
VERMELHO = (255, 0, 51)
AZUL_HUD = (0, 240, 255)
BRANCO = (255, 255, 255)
CINZA = (128, 128, 128)

class TelaArcade(TelaBatalha):
    """
    Herdará toda a interface gráfica de TelaBatalha, mas adaptada
    para exibir o Cronômetro do Modo Arcade em vez da barra de HP do herói.
    """
    def __init__(self, tela, nome_jogador):
     
        super().__init__(tela, nome_jogador)
        
        
        self.combat_state = ArcadeState(nome_jogador)
        
        self.fonte_relogio = pygame.font.SysFont("Courier New", 28, bold=True)

    def update(self):
        """Sobrescreve o update para rodar a lógica do tempo mantendo a captação de delta time da mãe."""
        agora = pygame.time.get_ticks()
        dt = (agora - self.ultima_atualizacao) / 1000.0
        self.ultima_atualizacao = agora
        
        
        self.combat_state.update(dt)

    def _draw_batalha(self, tempo):
        """
        SOBRESCREVE O MÉTODO DA MÃE!
        Dita quais componentes aparecem na tela, substituindo o HUD clássico de HP.
        """
        
        self._draw_titulo(tempo)
        self._draw_personagens()
        self._draw_pergunta(tempo)
        self._draw_mensagem(tempo)
        
        
        self._desenhar_hud()
        
        
        pygame.draw.line(self.tela, CINZA, (30, 315), (self.largura - 30, 315), 1)

    def _desenhar_hud(self):
        """
        Sua lógica cyberpunk nativa: Renderiza o DOCKING TIME na esquerda
        e mantém o HP do Boss atualizado com a contagem de VÍTIMAS na direita.
        """
        cs = self.combat_state
       
        
        minutos = int(cs.tempo_global // 60)
        segundos = int(cs.tempo_global % 60)
        tempo_formatado = f"TEMPO RESTANTE: {minutos:02d}:{segundos:02d}"
        
        if cs.tempo_global > 60:
            cor_relogio = AZUL_HUD
        elif cs.tempo_global > 20:
            cor_relogio = AMARELO
        else:
            cor_relogio = VERMELHO 
            
        txt_tempo = self.fonte_relogio.render(tempo_formatado, True, cor_relogio)
        self.tela.blit(txt_tempo, (40, 30))
        
        
        largura_barra_pergunta = int((cs.timer_pergunta_limite / 15.0) * 250)
        pygame.draw.rect(self.tela, CINZA, (40, 65, 250, 4))
        pygame.draw.rect(self.tela, cor_relogio, (40, 65, largura_barra_pergunta, 4))

        
        txt_mp = self.fonte_hud.render(f"MP: {cs.hero.mana}/{cs.hero.max_mana}", True, (150, 150, 255))
        self.tela.blit(txt_mp, (40, 75))

        
        if cs.boss:
            nome_exibicao = f"{cs.boss.name} [VÍTIMAS: {cs.bosses_derrotados}]"
            txt_boss = self.fonte_hud.render(nome_exibicao, True, VERMELHO)
            self.tela.blit(txt_boss, (self.largura - txt_boss.get_width() - 40, 30))
            
            porcentagem_boss = cs.boss.hp / cs.boss.max_hp if cs.boss.max_hp > 0 else 0
            largura_barra_boss = int(porcentagem_boss * 300)
            
            pygame.draw.rect(self.tela, (60, 20, 20), (self.largura - 340, 55, 300, 15))
            pygame.draw.rect(self.tela, VERMELHO, (self.largura - 340, 55, largura_barra_boss, 15))