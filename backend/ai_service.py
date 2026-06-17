import random
import json
from groq import Groq
from .config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)
MODELO = "llama-3.3-70b-versatile"

def chamar_ia(prompt: str, temperature: float = 1.1) -> str | None:
    try:
        resposta = client.chat.completions.create(
            model=MODELO,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024,
        )
        texto = resposta.choices[0].message.content
        return texto.strip().replace("```json", "").replace("```", "").strip()
    except Exception as e:
        print(f"[AI] Erro na chamada: {e}")
        return None


def parsear_json(texto: str | None) -> dict | None:
    if not texto:
        return None
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return None


# ─────────────────────────────────────────
# GERAR BOSS
# ─────────────────────────────────────────

def gerar_boss(nivel: int) -> dict:
    tema_sugerido = random.choice(
        ["listas", "loops", "classes", "excecoes", "recursao", "dicionarios"]
    )

    prompt = f"""
    Você é o gerador de bosses do PyBoss, um jogo educativo de Python.

    Gere um boss para o nível {nivel}.

    Regras:
    - Nome criativo em MAIÚSCULAS que remeta ao tema Python
    - O tema deve ser UM desses valores exatos: listas, loops, classes, excecoes, recursao, dicionarios
    - Sugestão de tema para este nível: {tema_sugerido} (pode usar outro se preferir)
    - As 3 cores devem combinar e refletir a personalidade do boss (formato hex)
    - Descrição épica e curta (máximo 1 frase)
    - HP entre {80 + nivel * 15} e {100 + nivel * 20}

    Retorne APENAS o JSON abaixo, sem texto extra, sem ```json:
    {{
        "nome": "NOME EM MAIÚSCULAS",
        "tema": "escreva aqui o tema escolhido",
        "cores": ["#hexcor1", "#hexcor2", "#hexcor3"],
        "fraqueza": "tema que ele é fraco",
        "hp": 120,
        "descricao": "uma frase épica curta"
    }}
    """

    resposta = chamar_ia(prompt)
    boss     = parsear_json(resposta)

    if not boss:
        boss = {
            "nome":      "SYNTAXERROR",
            "tema":      tema_sugerido,
            "cores":     ["#1a1a2e", "#e94560", "#0f3460"],
            "fraqueza":  "funcoes",
            "hp":        80 + nivel * 15,
            "descricao": "O erro que nunca some."
        }

    return boss


def gerar_questao(tema: str, nivel: int, temas_errados: list = [], perguntas_anteriores: list = []) -> list:
    
    if nivel <= 2:
        dificuldade = "fácil: conceitos básicos, sintaxe simples, sem pegadinhas"
    elif nivel <= 4:
        dificuldade = "média: uso combinado de conceitos, trechos de código com saída esperada"
    elif nivel <= 6:
        dificuldade = "difícil: comportamentos sutis, erros comuns, output de código não-óbvio"
    else:
        dificuldade = "expert: edge cases, performance, comportamentos internos do Python"

    contexto_erros = (
        f"O jogador tem dificuldade com: {', '.join(temas_errados)}. Priorize esses temas."
        if temas_errados else
        "Sem histórico de erros ainda."
    )

    # Histórico para evitar repetição
    if perguntas_anteriores:
        historico = "PERGUNTAS JÁ FEITAS (não repita nem temas similares):\n" + \
                    "\n".join(f"- {p}" for p in perguntas_anteriores[-10:])
    else:
        historico = "Sem perguntas anteriores."

    prompt = f"""
    Você é o gerador de questões do PyBoss, jogo educativo de Python.

    Gere exatamente 5 questões de múltipla escolha sobre Python.

    Regras:
    - Tema principal: {tema}
    - Dificuldade: {dificuldade}
    - Nível atual do jogador: {nivel} (adapte a complexidade proporcionalmente)
    - {contexto_erros}
    - {historico}
    - Varie o TIPO de pergunta: conceito teórico, leitura de código, saída esperada, identificação de erro, completar código
    - Código curto se necessário (máximo 5 linhas)
    - O campo "codigo" deve conter APENAS código Python incompleto ou neutro que contextualize a pergunta
    - NUNCA revele a resposta correta dentro do campo "codigo"
    - Se não precisar de código, use null
    - 4 opções plausíveis por questão (distratores realistas, não óbvios)
    - Explicação didática e direta

    Retorne APENAS o JSON abaixo, sem texto extra, sem ```json:
    {{
        "questoes": [
            {{
                "pergunta": "texto da pergunta",
                "codigo": null,
                "opcoes": ["A) op1", "B) op2", "C) op3", "D) op4"],
                "correta": "A",
                "explicacao": "explicação"
            }}
        ]
    }}
    """

    resposta = chamar_ia(prompt)
    dados    = parsear_json(resposta)

    if dados and "questoes" in dados and dados["questoes"]:
        return dados["questoes"]

    return [_questao_fallback(tema)]  # retorna lista também para consistência

# ─────────────────────────────────────────
# GERAR RELATÓRIO FINAL
# ─────────────────────────────────────────

def gerar_relatorio(stats: dict) -> str:
    total = stats["certas"] + stats["erradas"]
    taxa  = round(stats["certas"] / total * 100) if total > 0 else 0
    temas = ", ".join(stats["temas_errados"]) if stats["temas_errados"] else "nenhum"

    prompt = f"""
    Você é o narrador do PyBoss, jogo educativo de Python.

    Estatísticas da run:
    - Bosses derrotados: {stats["bosses"]}
    - Questões certas: {stats["certas"]}
    - Questões erradas: {stats["erradas"]}
    - Taxa de acerto: {taxa}%
    - Maior combo: {stats["maior_combo"]}x
    - Temas que mais errou: {temas}

    Escreva um relatório com EXATAMENTE essa estrutura:
    1. Avaliação geral (1 frase épica)
    2. Ponto forte (1 frase)
    3. Ponto fraco (1 frase)
    4. Dica de estudo (1 dica prática)

    Máximo 6 linhas. Tom épico mas educativo. Sem JSON.
    """

    return chamar_ia(prompt) or "O Oráculo silencia. Sua jornada continua..."


# ─────────────────────────────────────────
# FALLBACK LOCAL
# ─────────────────────────────────────────

def _questao_fallback(tema: str) -> dict:
    import random
    fallbacks = {
        "loops": [
            {
                "pergunta": "O que range(3) retorna?",
                "codigo":   None,
                "opcoes":   ["A) [1,2,3]", "B) [0,1,2]", "C) [0,1,2,3]", "D) (0,1,2)"],
                "correta":  "B",
                "explicacao": "range(3) gera de 0 até 2, totalizando 3 elementos."
            },
            {
                "pergunta": "O que 'break' faz dentro de um loop?",
                "codigo":   None,
                "opcoes":   ["A) Pula iteração", "B) Encerra o loop", "C) Reinicia", "D) Nada"],
                "correta":  "B",
                "explicacao": "break encerra o loop imediatamente."
            },
        ],
        "listas": [
            {
                "pergunta": "Como acessar o último elemento de uma lista?",
                "codigo":   "lista = [10, 20, 30]",
                "opcoes":   ["A) lista[3]", "B) lista[-1]", "C) lista.last()", "D) lista[end]"],
                "correta":  "B",
                "explicacao": "Índice -1 acessa o último elemento."
            },
        ],
    }
    pool = fallbacks.get(tema, fallbacks["loops"])
    return random.choice(pool)
