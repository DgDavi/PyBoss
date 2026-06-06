# client/engine/utils.py

import unicodedata

def normalizar_texto(texto: str) -> str:
    """Remove acentos e converte para minúsculas."""
    if not isinstance(texto, str):
        return ""
    # NFD: Normalization Form Decomposed
    forma_nfd = unicodedata.normalize('NFD', texto.lower())
    # Remove caracteres de combinação (acentos)
    return "".join(c for c in forma_nfd if not unicodedata.combining(c))
