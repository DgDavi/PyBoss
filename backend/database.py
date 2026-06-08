import sqlite3
import os

# Define o caminho onde o arquivo do banco de dados (ranking.db) será criado.
DB_PATH = os.path.join(os.path.dirname(__file__), 'ranking.db')

def conectar_banco():
    """Cria a conexão com o SQLite e gera a tabela de ranking caso ela não exista."""
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    
    # Cria a tabela com id auto-incremento, nome do alquimista e a pontuação
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            pontuacao INTEGER NOT NULL
        )
    ''')
    
    conexao.commit()
    return conexao

def salvar_pontuacao(nome, score):
    """Insere um novo recorde de jogador no banco de dados."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    # Insere o nome e os pontos da partida atual
    cursor.execute('INSERT INTO ranking (nome, pontuacao) VALUES (?, ?)', (nome, score))
    
    conexao.commit()
    conexao.close()
    print(f"[SQLITE] Pontuação de {nome} ({score} PTS) salva com sucesso!")

def obter_top_ranking(limite=5):
    """Busca os melhores jogadores ordenados da maior pontuação para a menor."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    # Ordena por pontuacao de forma Decrescente (DESC) e limita aos 5 melhores
    cursor.execute('SELECT nome, pontuacao FROM ranking ORDER BY pontuacao DESC LIMIT ?', (limite,))
    top_jogadores = cursor.fetchall()
    
    conexao.close()
    return top_jogadores