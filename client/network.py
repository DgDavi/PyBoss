import os
import sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from backend.ai_service import gerar_boss as _gerar_boss
from backend.ai_service import gerar_questao as _gerar_questao

def gerar_boss(nivel):
    return _gerar_boss(nivel)

def gerar_questao(tema, nivel, temas_errados=None, perguntas_anteriores=None):
    if temas_errados is None:
        temas_errados = []
    if perguntas_anteriores is None:
        perguntas_anteriores = []
    return _gerar_questao(tema, nivel, temas_errados, perguntas_anteriores)