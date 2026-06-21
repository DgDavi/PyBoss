# client/engine/combat.py

import random
import pygame

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
from engine.utils import normalizar_texto

# ── Constantes de combate ────────────────
TEMPO_RESPOSTA  = 15.0   # segundos por pergunta
TEMPO_EXTRA_SKILL = 10.0
DANO_BASE_HEROI = 12
DANO_BASE_BOSS  = 10
TIMER_AGUARDAR  = 0.9    # segundos de feedback antes da próxima pergunta
TIMER_MENSAGEM  = 1.4
TIMER_ANIMACAO  = 0.3
TIMER_NOVO_BOSS = 1.2

# Duração da tela de apresentação do boss
TIMER_APRESENTACAO = 3.0

# ── Mapa tema → classe do boss ───────────
MAPA_BOSS = {
    "classes":     BossClasses,
    "dicionarios": BossDicts,
    "excecoes":    BossExceptions,
    "listas":      BossLists,
    "loops":       BossLoops,
    "recursao":    BossRecursion,
}


class CombatState:
    """Gerencia toda a lógica de estado e regras da batalha."""

    def __init__(self, nome_jogador, boss_data=None, nivel=1):
        # Entidades
        self.hero = Hero()
        self.boss = None
        self.boss_data = None
        self.boss_descricao = ""
        self.nivel = nivel
        self.nome_jogador = nome_jogador

        # Questão atual
        self.questao = None
        self.opcoes = []
        self.selecionado = 0

        # Combate
        self.combo = 0
        self.maior_combo = 0
        self.temas_errados = []
        self._fila_questoes = {}
        self.perguntas_feitas = []
        self.bosses_derrotados = 0
        self.acertos = 0
        self.erros = 0

        # Timer de resposta (regressivo)
        self.timer_resposta = TEMPO_RESPOSTA
        self.timer_esgotado = False

        # Controle de estados intermediários
        self.aguardando = False
        self.aguardando_timer = 0.0
        self.mensagem = ""
        self.mensagem_cor = (220, 220, 220)
        self.mensagem_timer = 0.0
        self.anim_timer = 0.0

        # ── Estado de apresentação do boss ──
        # "apresentando" → mostra tema/sprite antes das perguntas
        # "batalha"      → perguntas ativas
        self.fase = "apresentando"
        self.apresentacao_timer = TIMER_APRESENTACAO

        # Controle de fluxo
        self.proximo = None

        # Dados guardados para transição
        self.boss_anterior = None
        self.proximo_boss_data = None

        #Release 2: itens da cultura pernambucana, que dão algum bônus para o jogador
        self.itens_pernambucanos = [
            {"nome": "Bolo de Rolo", "tipo": "cura", "valor": 15, "msg": "Você comeu um bolo de rolo legítimo e ganhou +15 HP!"},
            {"nome": "Cartola", "tipo": "cura", "valor": 10, "msg": "Banana com queijo assado e canela! Ganhou +10 HP!"},
            {"nome": "Tapioca da Sé", "tipo": "cura", "valor": 25, "msg": "Subiu o Alto da Sé e comeu uma tapioca! Recuperou +25 HP!"},
            {"nome": "Gin de 10", "tipo": "duplica_dano", "valor": True, "msg": "Gin de 10! Seu próximo ataque dará o DOBRO de dano!"},
            {"nome": "Axé", "tipo": "tempo_extra", "valor": 5, "msg": "Um gole de Axé de Olinda! +5 segundos na próxima rodada!"}
        ]
        self.proximo_dano_duplicado = False
        self.tempo_bonus_proxima_rodada = 0.0

        # A questão só é carregada quando a apresentação terminar

        if boss_data:
            self.boss_data = boss_data
            self.carregar_boss_dos_dados()
        else:
            self.carregar_boss()

    # ─────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────

    def update(self, dt):
        self.hero.update(dt)

        if self.fase == "apresentando":
            self._atualizar_apresentacao(dt)
        else:
            self._atualizar_timer_resposta(dt)
            self._atualizar_animacao(dt)
            self._atualizar_mensagem(dt)
            self._resolver_proxima_acao(dt)

    def _atualizar_apresentacao(self, dt):
        """Conta o tempo de apresentação; ao zerar entra na fase de batalha."""
        self.apresentacao_timer = max(0.0, self.apresentacao_timer - dt)
        if self.apresentacao_timer == 0.0:
            self.fase = "batalha"
            self._carregar_questao()

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
    # INPUT
    # ─────────────────────────────────────

    def handle_input(self, acao):
        if self.fase == "apresentando":
            if acao == "confirm":
                self.apresentacao_timer = 0.0
            return

        if self.aguardando or self.mensagem_timer > 0 or not self.questao:
            return

        if acao == "up":
            self.selecionado = (self.selecionado - 1) % len(self.opcoes)
        elif acao == "down":
            self.selecionado = (self.selecionado + 1) % len(self.opcoes)
        elif acao == "confirm":
            self._responder()
        elif acao == "skill_dica":      # ← novo
            self._usar_dica()
        elif acao == "skill_tempo":     # ← novo
            self._usar_tempo_extra()
        elif acao == "skill_escudo":    # ← novo
            self._usar_escudo()

    # ─────────────────────────────────────
    # LÓGICA DE COMBATE
    # ─────────────────────────────────────

    def _responder(self):
        """Processa a resposta do jogador."""
        if not self.questao:
            return

        letra_escolhida = self.opcoes[self.selecionado].strip()[:1].upper()
        letra_correta = str(self.questao.get("correta", "A")).strip()[:1].upper()

        if letra_escolhida == letra_correta:
            self._processar_acerto()
        else:
            self._processar_erro()

        self.aguardando = True
        self.aguardando_timer = TIMER_AGUARDAR

    def _processar_acerto(self):
        self.acertos += 1
        self.combo += 1
        self.maior_combo = max(self.combo, self.maior_combo)
        self.hero.ganhar_mana(10)   
        
        dano = self._calcular_dano(DANO_BASE_HEROI, self.combo)
        self.boss.take_damage(dano)
        self.hero.set_state("attack")
        self.anim_timer = TIMER_ANIMACAO
        
        txt_feedback = f"✓ CORRETO!  COMBO x{self.combo}  +{dano} DANO"
        cor_feedback = (40, 190, 80)
        
        if random.random() < 0.30:
            item = random.choice(self.itens_pernambucanos)
            txt_feedback = f"🎁 {item['msg']}" 
            cor_feedback = (255, 105, 180) 
            
            if item["tipo"] == "cura":
                self.hero.hp = min(self.hero.max_hp, self.hero.hp + item["valor"])
            elif item["tipo"] == "duplica_dano":
                self.proximo_dano_duplicado = True
            elif item["tipo"] == "tempo_extra":
                self.tempo_bonus_proxima_rodada = item["valor"]
                
        self._set_mensagem(txt_feedback, cor=cor_feedback)
        

    def _processar_erro(self):
        self.erros += 1
        if self.hero.escudo_ativo:
            self.hero.escudo_ativo = False
            self._set_mensagem("🛡 ESCUDO ABSORVEU O DANO!", cor=(80, 160, 255))
        else:
            dano = self._calcular_dano(DANO_BASE_BOSS, self.combo)
            self.hero.take_damage(dano)
            self._set_mensagem(f"✗ ERRADO!  COMBO QUEBRADO  -{dano} HP", cor=(220, 20, 60))
        self.hero.set_state("damage")
        self.anim_timer = TIMER_ANIMACAO
        self.combo = 0
        self._registrar_erro_tema()

    def _processar_timeout(self):
        """Timer zerou — penalidade igual a um erro."""
        self.erros += 1
        dano = self._calcular_dano(DANO_BASE_BOSS, self.combo)
        self.hero.take_damage(dano)
        self.hero.set_state("damage")
        self.anim_timer = TIMER_ANIMACAO
        self._set_mensagem(
            f"⏱ TEMPO ESGOTADO!  -{dano} HP",
            cor=(220, 140, 20)
        )
        self.combo = 0
        self.aguardando = True
        self.aguardando_timer = TIMER_AGUARDAR
        self._registrar_erro_tema()

    def _calcular_dano(self, base, combo):
        bonus = combo * 4
        nivel = max(0, self.nivel - 1)
        variacao = random.randint(0, 2)
        dano_final = base + bonus + (nivel * 2) + variacao
        
        if self.proximo_dano_duplicado:
            dano_final *= 2
            self.proximo_dano_duplicado = False 
            
        return dano_final

    # ─────────────────────────────────────
    # CARREGAMENTO
    # ─────────────────────────────────────

    def carregar_boss(self):
        """Gera e instancia o boss para o nível atual."""
        self.boss_data   = gerar_boss(self.nivel)
        tema             = normalizar_texto(self.boss_data.get("tema", ""))
        classe_boss      = MAPA_BOSS.get(tema, BossLoops)
        self.boss        = classe_boss()
        self.boss.name   = self.boss_data.get("nome",   self.boss.name)
        self.boss.max_hp = int(self.boss_data.get("hp", self.boss.max_hp))
        self.boss.hp     = self.boss.max_hp
        self.boss_descricao = self.boss_data.get("descricao", "")

    def carregar_boss_dos_dados(self):
        """
        Instancia o boss a partir de boss_data já preenchido externamente
        (usado pelo GameManager ao retornar da TelaTransicao).
        """
        if not self.boss_data:
            self.carregar_boss()
            return
        tema = normalizar_texto(self.boss_data.get("tema", ""))
        classe_boss      = MAPA_BOSS.get(tema, BossLoops)
        self.boss        = classe_boss()
        self.boss.name   = self.boss_data.get("nome",   self.boss.name)
        self.boss.max_hp = int(self.boss_data.get("hp", self.boss.max_hp))
        self.boss.hp     = self.boss.max_hp
        self.boss_descricao = self.boss_data.get("descricao", "")

    def _proximo_boss(self):
        """Chamado quando boss atual morre — sinaliza transição."""
        self.boss_anterior = self.boss_data.copy()
        self.nivel += 1
        self.proximo_boss_data = gerar_boss(self.nivel)
        self._fila_questoes = {}
        self.proximo = "transicao"

    # ─────────────────────────────────────
    # UTILITÁRIOS
    # ─────────────────────────────────────

    def get_stats_finais(self):
        return {
            "bosses": self.nivel - 1,
            "certas": self.acertos,
            "erradas": self.erros,
            "maior_combo": self.maior_combo,
            "temas_errados": list(self.temas_errados),
        }

    def _set_mensagem(self, texto, cor=None):
        self.mensagem = texto
        self.mensagem_cor = cor if cor else (220, 220, 20)
        self.mensagem_timer = TIMER_MENSAGEM

    def _registrar_erro_tema(self):
        if not self.boss_data:
            return
        tema = normalizar_texto(self.boss_data.get("tema", ""))
        if tema and tema not in self.temas_errados:
            self.temas_errados.append(tema)

    def _carregar_questao(self):
        if not self.boss_data:
            return
        tema = self.boss_data.get("tema", "")
        dificuldade = self.nivel

        if self._fila_questoes.get(tema):
            dados = self._fila_questoes[tema].pop(0)
        else:
            resposta = gerar_questao(
                tema,
                dificuldade,
                temas_errados=self.temas_errados,
                perguntas_anteriores=self.perguntas_feitas
            )
            if not resposta:
                self.questao = None
                self.opcoes  = []
                return
            if isinstance(resposta, list):
                self._fila_questoes[tema] = resposta[1:]
                dados = resposta[0]
            else:
                dados = resposta

        # Registra a pergunta no histórico global
        if dados and "pergunta" in dados:
            self.perguntas_feitas.append(dados["pergunta"])

        self.questao        = dados
        self.opcoes         = dados.get("opcoes", [])
        self.selecionado    = 0
        self.timer_resposta = TEMPO_RESPOSTA + self.tempo_bonus_proxima_rodada
        self.tempo_bonus_proxima_rodada = 0.0
        self.timer_esgotado = False

    def _usar_dica(self):
        if not self.questao or not self.opcoes:
            return
        if self.hero.usar_dica():
            correta = str(self.questao.get("correta", "A")).strip()[:1].upper()
            erradas = [i for i, op in enumerate(self.opcoes)
                    if op.strip()[:1].upper() != correta]
            remover = erradas[:2]
            # Substitui as opções eliminadas por texto vazio
            for i in remover:
                self.opcoes[i] = f"{self.opcoes[i][:2]}~~eliminada~~"
            if self.selecionado in remover:
                self.selecionado = next(
                    i for i in range(len(self.opcoes)) if i not in remover
                )
            self._set_mensagem("💡 DICA USADA — 2 opções eliminadas!", cor=(255, 200, 40))

    def _usar_tempo_extra(self):
        if self.hero.usar_tempo_extra():
            self.timer_resposta = min(TEMPO_RESPOSTA, self.timer_resposta + TEMPO_EXTRA_SKILL)
            self._set_mensagem(f"⏱ +{int(TEMPO_EXTRA_SKILL)}s ADICIONADOS!", cor=(40, 190, 190))

    def _usar_escudo(self):
        if self.hero.usar_escudo():
            self._set_mensagem("🛡 ESCUDO ATIVADO — próximo erro sem dano!", cor=(80, 160, 255))
        # Se já ativo, silencia (não gasta mana)