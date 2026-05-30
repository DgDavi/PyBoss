from google import genai
from google.genai import types
import json
from config import GEMINI_KEY

client = genai.Client(api_key=GEMINI_KEY)

def chamar_ia(prompt):
    resposta = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt
    )

    texto = resposta.text.strip()
    texto = texto.replace("```json", "").replace("```", "").strip()
    return texto

def parsear_json(texto):
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return None
    

def gerar_boss(nivel: int):
    prompt = f"""
    Você é o gerador de bosses do PyBoss, um jogo educativo de Python.

    Gere um boss para o nível {nivel}.

    Regras:
    - O nome deve ser criativo e remeter ao tema Python
    - O tema deve ser UM desses valores exatos: listas, loops, classes, exceções, recursão, dicionários
    - As 3 cores devem combinar entre si e refletir a personalidade do boss
    - A descrição deve ser épica e curta (máximo 1 frase)
    - O HP deve ser entre {80 + nivel * 15} e {100 + nivel * 20}

    Retorne APENAS o JSON abaixo, sem texto extra, sem ```json, sem explicações:
    {{
        "nome": "NOME EM MAIÚSCULAS",
        "tema": "loops",
        "cores": ["#hexcor1", "#hexcor2", "#hexcor3"],
        "fraqueza": "tema que ele é fraco",
        "hp": 120,
        "descricao": "uma frase épica curta"
    }}
    """

    resposta = chamar_ia(prompt)
    boss = parsear_json(resposta)

    if not boss:
        boss = {
            "nome": "SYNTAXERROR",
            "tema": "loops",
            "cores": ["#1a1a2e", "#e94560", "#0f3460"],
            "fraqueza": "funções",
            "hp": 80 + nivel * 15,
            "descricao": "O erro que nunca some."
        }

    return boss


def gerar_questao(tema: str, nivel:int, temas_errados: list = []):
    dificuldade = (
        "fácil" if nivel <= 2 else
        "média" if nivel <=5 else
        "difícil"
    )

    contexto_erros = (
        f"O jogador tem dificuldade com: {', '.join(temas_errados)}. Priorize esses temas."
        if temas_errados else
        "Sem histórico de erros ainda."
    )

    prompt = f"""
    Você é o gerador de questões do PyBoss, um jogo educativo de Python.

    Gere UMA questão de múltipla escolha com as seguintes regras:
    - Tema principal: {tema}
    - Dificuldade: {dificuldade}
    - {contexto_erros}
    - Código curto se necessário (máximo 5 linhas)
    - As 4 opções devem ser plausíveis, não óbvias demais
    - A explicação deve ser didática e direta

    Retorne APENAS o JSON abaixo, sem texto extra, sem ```json, sem explicações:
    {{
        "pergunta": "texto da pergunta aqui",
        "codigo": "trecho de código Python ou null se não houver",
        "opcoes": ["A) opcao1", "B) opcao2", "C) opcao3", "D) opcao4"],
        "correta": "A",
        "explicacao": "por que essa resposta é a correta"
    }}
    """

    resposta = chamar_ia(prompt)
    questao = parsear_json(resposta)

    if not questao:
        questao = {
            "pergunta": "O que list(range(5)) retorna?",
            "codigo": "print(list(range(5)))",
            "opcoes": [
                "A) [1, 2, 3, 4, 5]",
                "B) [0, 1, 2, 3, 4]",
                "C) [0, 1, 2, 3, 4, 5]",
                "D) (0, 1, 2, 3, 4)"
            ],
            "correta": "B",
            "explicacao": "range(5) gera de 0 até 4, totalizando 5 elementos."
        }

    return questao


print(gerar_boss(5))
