# ⚔️ PyBoss

> **Aprenda Python derrotando chefes.**
> Um RPG de batalha onde cada boss representa um conceito da linguagem — e sua única arma são as respostas certas.
---

## Sobre o jogo

PyBoss é um jogo educativo construído com **Pygame** em que o jogador enfrenta uma sequência infinita de bosses gerados dinamicamente por IA. Cada boss representa um tema de Python — listas, loops, classes, exceções, recursão, dicionários — e combate funciona respondendo perguntas de múltipla escolha. Acertos causam dano ao boss; erros custam HP do herói.

As perguntas e os próprios bosses são gerados em tempo real pela API **Groq (LLaMA 3.3 70B)**, com dificuldade e tema adaptados ao nível atual do jogador. Um sistema de histórico evita repetição de perguntas ao longo da run.

---

## Funcionalidades

- **Bosses gerados por IA** — nome, tema, cores, HP e descrição únicos a cada run
- **Perguntas adaptativas** — dificuldade cresce com o nível; histórico impede repetição
- **Sistema de combo** — respostas consecutivas corretas multiplicam o dano
- **Relatório final** — ao fim de cada run, o Oráculo Groq avalia seu desempenho e aponta pontos fracos
- **Ranking local** — pontuações salvas em SQLite com placar dos melhores
- **Pixel art original** — sprites do herói e 6 bosses com animações de idle, ataque e dano
- **Visual retrô** — efeito scanline, grade animada, degradê e bordas neon

---

## Temas abordados

| Boss | Tema Python |
|------|-------------|
| 🔴 LISTUS MAXIMUS | Listas |
| 🔵 LOOPUS INFINITUS | Loops |
| 🟡 CLASSICUS REX | Classes e OOP |
| 🟣 EXCEPTIO FATALIS | Exceções |
| 🟢 RECURSIVUS | Recursão |
| ⚪ DICTATOR SUPREMUS | Dicionários |

---

## Estrutura do projeto

```
PyBoss/
├── client/
│   ├── main.py                  # Ponto de entrada
│   ├── engine/
│   │   ├── combat.py            # Lógica de estado do combate
│   │   ├── entities.py          # Herói e bosses (sprites + animações)
│   │   ├── utils.py             # Funções auxiliares
│   │   └── config.py
│   ├── viewer/
│   │   ├── base.py              # TelaBase (degradê, grade, scanlines)
│   │   ├── tela_nome.py         # Tela de entrada do nome
│   │   ├── tela_menu.py         # Menu principal
│   │   ├── tela_batalha.py      # Tela de combate e perguntas
│   │   ├── tela_transicao.py    # Entre bosses
│   │   ├── tela_game_over.py    # Derrota + relatório da IA
│   │   └── tela_rank.py         # Ranking local
│   ├── network/
│   │   └── ai_service.py        # Integração com Groq (bosses + questões + relatório)
│   └── backend/
│       └── database.py          # SQLite — salvar e consultar pontuações
└── assets/
    └── sprites/                 # Spritesheets PNG 128×128 RGBA
```

---

## Requisitos

- Python 3.11+
- Conta e chave de API na [Groq](https://console.groq.com) (gratuita)

---

## Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/pyboss.git
cd pyboss

# 2. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure a chave da API
#    Crie o arquivo client/engine/config.py com:
#    GROQ_API_KEY = "sua-chave-aqui"

# 5. Execute o jogo
python client/main.py
```

---

## Como jogar

| Tecla | Ação |
|-------|------|
| `↑` / `↓` | Navegar entre opções |
| `Enter` / `Espaço` | Confirmar resposta |
| `R` | Voltar ao menu (na tela de derrota) |

**Mecânicas principais:**

- Cada boss tem um tema Python associado — as perguntas giram em torno desse tema
- Responder corretamente aumenta seu **combo**, que amplifica o dano causado
- Errar ou deixar o tempo esgotar quebra o combo e causa dano ao herói
- Ao derrotar um boss você avança de nível — o próximo é mais difícil
- A run termina quando o HP do herói chega a zero

---

## Dependências

```
pygame
groq
```

> O banco de dados SQLite usa apenas a biblioteca padrão do Python — sem dependência extra.

---

## Variáveis de configuração

Em `client/engine/config.py`:

```python
GROQ_API_KEY = "sua-chave-aqui"
```

Em `client/engine/combat.py` você pode ajustar as constantes de combate:

```python
TEMPO_RESPOSTA  = 15.0   # segundos por pergunta
DANO_BASE_HEROI = 12     # dano base do acerto
DANO_BASE_BOSS  = 10     # dano base do erro
TIMER_APRESENTACAO = 3.0 # duração da tela de apresentação do boss
```

---
