import sqlite3

def conectar_banco():
    conexao = sqlite3.connect('banco.db')
    conexao.execute('PRAGMA foreign_keys = ON')
    return conexao

def criar_tabela_pessoas():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade INTEGER NOT NULL,
            cpf TEXT NOT NULL UNIQUE,
            foto_cadastro TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS capturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pessoa_id INTEGER NOT NULL,
            caminho_foto TEXT NOT NULL,
            criada_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pessoa_id) REFERENCES pessoas(id)
        )
    """)

    colunas_capturas = [
        coluna[1]
        for coluna in cursor.execute("PRAGMA table_info(capturas)")
    ]

    if "origem" not in colunas_capturas:
        cursor.execute("""
            ALTER TABLE capturas
            ADD COLUMN origem TEXT NOT NULL DEFAULT 'camera'
        """)

    if "arquivo_origem" not in colunas_capturas:
        cursor.execute("""
            ALTER TABLE capturas
            ADD COLUMN arquivo_origem TEXT
        """)

    conexao.commit()
    conexao.close()

def cadastrar_pessoa(nome, idade, cpf, foto_cadastro, embedding):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO pessoas (nome, idade, cpf, foto_cadastro, embedding)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, idade, cpf, foto_cadastro, embedding))

    conexao.commit()
    conexao.close()

def buscar_pessoas():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, idade, cpf, foto_cadastro, embedding
        FROM pessoas
    """)

    pessoas = cursor.fetchall()
    conexao.close()

    return pessoas

def registrar_captura(
    pessoa_id,
    caminho_foto,
    origem,
    arquivo_origem=None
):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO capturas (
            pessoa_id,
            caminho_foto,
            origem,
            arquivo_origem
        )
        VALUES (?, ?, ?, ?)
    """, (
        pessoa_id,
        caminho_foto,
        origem,
        arquivo_origem
    ))

    conexao.commit()
    conexao.close()