# client/engine/arcade.py

import random
import pygame
from .combat import CombatState, DANO_BASE_HEROI, TIMER_ANIMACAO, TIMER_AGUARDAR
from network import gerar_questao

class ArcadeState(CombatState):
    """
    Subclasse de CombatState focada no modo Arcade.
    Tempo máximo de 2 minutos. 
    Acertos dão dano e pontos. Erros ou estouros do tempo de pergunta punem o relógio do jogador.
    """

    def __init__(self, nome_jogador, boss_data=None, nivel=1):
    
        super().__init__(nome_jogador, boss_data, nivel)
    
        self.fase = "batalha"              
        self.tempo_global = 120.0          
        self.timer_pergunta_limite = 15.0  

        self.itens_pernambucanos = [
            {"nome": "Bolo de Rolo", "tipo": "tempo_extra", "valor": 8, "msg": "Bolo de Rolo! Açúcar puro para te dar energia: +8s no relógio!"},
            {"nome": "Cartola", "tipo": "tempo_extra", "valor": 5, "msg": "Cartola quentinha! Rápido estímulo de foco: +5s no relógio!"},
            {"nome": "Tapioca da Sé", "tipo": "tempo_extra", "valor": 12, "msg": "Tapioca reforçada do Alto da Sé! Combustível hacker: +12s no relógio!"},
            {"nome": "Gin de 10", "tipo": "duplica_dano", "valor": True, "msg": "Gin de 10! Beba para DOBRAR seu próximo ataque e estraçalhar o Boss!"},
            {"nome": "Axé", "tipo": "tempo_extra", "valor": 15, "msg": "Um gole de Axé de Olinda! Ritmo frenético: +15s extras!"}
        ]

        self._carregar_questao()
    def update(self, dt):
        """Reescreve o update para tratar o tempo global e as regras do Arcade."""
        self.hero.update(dt)

        
        self.tempo_global = max(0.0, self.tempo_global - dt)
        if self.tempo_global == 0.0:
            self.proximo = "game_over"
            return

        
        self._atualizar_animacao(dt)
        self._atualizar_mensagem(dt)
        self._resolver_proxima_acao(dt)

       
        if not self.aguardando and self.mensagem_timer <= 0 and self.questao and self.fase == "batalha":
            self.timer_pergunta_limite = max(0.0, self.timer_pergunta_limite - dt)
            if self.timer_pergunta_limite == 0.0:
                self._processar_timeout_arcade()

    def _processar_acerto(self):
        """Acertou: Dano no boss, recupera mana e ganha bônus de tempo global!"""
        self.acertos += 1
        self.combo += 1
        self.maior_combo = max(self.combo, self.maior_combo)
        self.hero.ganhar_mana(10)
        
        
        bonus_tempo = 3.0 + min(self.combo, 5) 
        self.tempo_global += bonus_tempo

        dano = self._calcular_dano(DANO_BASE_HEROI, self.combo)
        self.boss.take_damage(dano)
        self.hero.set_state("attack")
        self.anim_timer = TIMER_ANIMACAO
        
        txt_feedback = f"✓ CORRETO! +{int(bonus_tempo)}s NO RELÓGIO   +{dano} DANO"
        self._set_mensagem(txt_feedback, cor=(40, 190, 80))
        
        
        if random.random() < 0.30:
            if len(self.inventario) < 5:
                item = random.choice(self.itens_pernambucanos)
                self.inventario.append(item)
                self.item_dropado = item
                self.fase = "popup_drop"  
            else:
                txt_feedback = f"✓ CORRETO! INVENTÁRIO CHEIO   +{dano} DANO"
                self._set_mensagem(txt_feedback, cor=(40, 190, 80))

        if self.boss.is_dead():
            self.bosses_derrotados += 1
            self.boss.hp = self.boss.max_hp
            self._set_mensagem(f"🏆 BOSS DESTRUIDO! PRÓXIMO ALVO ALINHADO!", cor=(255, 200, 40))

        
        if self.fase != "popup_drop":
            self.aguardando = True
            self.aguardando_timer = TIMER_AGUARDAR

    def _processar_erro(self):
        """Errou: Penaliza o tempo global bruscamente (-10 segundos) e quebra o combo."""
        self.erros += 1
        penalidade_tempo = 10.0

        if self.hero.escudo_ativo:
            self.hero.escudo_ativo = False
            self._set_mensagem("🛡 ESCUDO ABSORVEU A PENALIDADE DE TEMPO!", cor=(80, 160, 255))
        else:
            self.tempo_global = max(0.0, self.tempo_global - penalidade_tempo)
            self._set_mensagem(f"✗ ERRADO! QUEBROU COMBO! -{int(penalidade_tempo)}s NO RELÓGIO", cor=(220, 20, 60))
        
        self.hero.set_state("damage")
        self.anim_timer = TIMER_ANIMACAO
        self.combo = 0
        self.timer_pergunta_limite = 15.0
        self.aguardando = True
        self.aguardando_timer = TIMER_AGUARDAR

    def _processar_timeout_arcade(self):
        """Se o jogador demorar demais para responder, perde 7 segundos de relógio."""
        self.erros += 1
        penalidade = 7.0
        self.tempo_global = max(0.0, self.tempo_global - penalidade)
        
        self._set_mensagem(f"⏱ ENROLOU DEMAIS! -{int(penalidade)}s NO RELÓGIO", cor=(220, 140, 20))
        self.hero.set_state("damage")
        self.anim_timer = TIMER_ANIMACAO
        self.combo = 0
        self.aguardando = True
        self.aguardando_timer = TIMER_AGUARDAR

    def _carregar_questao(self):
        """Sobrescreve para resetar o micro-timer da pergunta quando uma nova carregar."""
        super()._carregar_questao()
        self.timer_pergunta_limite = 15.0

    def usar_item_selecionado(self):
        """Consome o item aplicando o efeito direto no tempo global do Arcade."""
        if self.inventario_selecionado >= len(self.inventario):
            return False 

        item = self.inventario.pop(self.inventario_selecionado)

        if item["tipo"] == "tempo_extra":
            
            self.tempo_global += item["valor"]
            self._set_mensagem(f"⏳ Usou {item['nome']}! +{item['valor']}s no Relógio Global", cor=(80, 160, 255))
            
        elif item["tipo"] == "duplica_dano":
            self.proximo_dano_duplicado = True
            self._set_mensagem(f"⚔️ Usou {item['nome']}! Próximo dano duplicado", cor=(220, 140, 20))

        return True