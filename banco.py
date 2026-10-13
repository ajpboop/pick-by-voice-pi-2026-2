import sqlite3

def conectar():
    return sqlite3.connect('estoque.db')

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()
    
    # Criação base das tabelas
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, senha TEXT NOT NULL, perfil TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, quantidade INTEGER NOT NULL, qtd_minima INTEGER NOT NULL, preco REAL NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY AUTOINCREMENT, status TEXT NOT NULL DEFAULT 'Aberto', data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS itens_pedido (id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_id INTEGER NOT NULL, produto_id INTEGER NOT NULL, quantidade INTEGER NOT NULL, FOREIGN KEY (pedido_id) REFERENCES pedidos (id), FOREIGN KEY (produto_id) REFERENCES produtos (id))''')
    
    # ---------------------------------------------------------
    # 1. ATUALIZAÇÕES DA TABELA DE PEDIDOS (Ordens de Saída)
    # ---------------------------------------------------------
    novas_colunas_pedidos = [
        "data_conclusao TIMESTAMP", "colaborador TEXT", "armazem TEXT", 
        "depositante TEXT", "onda TEXT", "transportadora TEXT", "cliente TEXT"
    ]
    for coluna in novas_colunas_pedidos:
        try: cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {coluna}")
        except sqlite3.OperationalError: pass

    # ---------------------------------------------------------
    # 2. ATUALIZAÇÕES DA TABELA DE PRODUTOS
    # ---------------------------------------------------------
    novas_colunas_produtos = [
        "corredor TEXT", "prateleira TEXT", "lugar TEXT", 
        "sku TEXT", "udm TEXT", "lote TEXT", "validade TEXT"
    ]
    for coluna in novas_colunas_produtos:
        try: cursor.execute(f"ALTER TABLE produtos ADD COLUMN {coluna}")
        except sqlite3.OperationalError: pass
        
    # ---------------------------------------------------------
    # 3. ATUALIZAÇÕES DA TABELA DE ITENS DO PEDIDO (Separação)
    # ---------------------------------------------------------
    novas_colunas_itens = [
        "qtd_conferida INTEGER DEFAULT 0", "qtd_cortada INTEGER DEFAULT 0"
    ]
    for coluna in novas_colunas_itens:
        try: cursor.execute(f"ALTER TABLE itens_pedido ADD COLUMN {coluna}")
        except sqlite3.OperationalError: pass

    # ---------------------------------------------------------
    # Usuário Admin padrão
    # ---------------------------------------------------------
    cursor.execute('SELECT COUNT(*) FROM usuarios')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (nome, senha, perfil) VALUES ('admin', 'admin', 'Administrador')")
        
    conn.commit()
    conn.close()

# ATUALIZADA com SKU, UDM, LOTE e VALIDADE
def adicionar_produto(nome, quantidade, qtd_minima, preco, corredor, prateleira, lugar, sku="", udm="UN", lote="", validade=""):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO produtos (nome, quantidade, qtd_minima, preco, corredor, prateleira, lugar, sku, udm, lote, validade) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, quantidade, qtd_minima, preco, corredor, prateleira, lugar, sku, udm, lote, validade))
    conn.commit()
    conn.close()

def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    linhas = cursor.fetchall()
    conn.close()
    return linhas

def deletar_produto(id_produto):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
    conn.commit()
    conn.close()

def criar_novo_pedido(armazem="N/A", depositante="N/A"):
    conn = conectar()
    cursor = conn.cursor()
    # Agora insere o armazém e o depositante na tabela de pedidos
    cursor.execute("INSERT INTO pedidos (status, armazem, depositante) VALUES ('Aberto', ?, ?)", (armazem, depositante))
    pedido_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return pedido_id

def adicionar_item_ao_pedido(pedido_id, produto_id, quantidade):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO itens_pedido (pedido_id, produto_id, quantidade) VALUES (?, ?, ?)", (pedido_id, produto_id, quantidade))
    conn.commit()
    conn.close()

def atualizar_quantidade_estoque(produto_id, quantidade_adicionada):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE produtos SET quantidade = quantidade + ? WHERE id = ?", (quantidade_adicionada, produto_id))
    conn.commit()
    conn.close()

def concluir_pedido_e_atualizar_estoque(pedido_id, nome_colaborador="Não Informado"):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE pedidos SET status = 'Concluído', data_conclusao = datetime('now', 'localtime'), colaborador = ? WHERE id = ?", (nome_colaborador, pedido_id))
        
        cursor.execute("SELECT produto_id, quantidade FROM itens_pedido WHERE pedido_id = ?", (pedido_id,))
        itens = cursor.fetchall()
        
        for produto_id, quantidade_separada in itens:
            cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (quantidade_separada, produto_id))
            
        conn.commit()
    except Exception as e:
        print(f"Erro ao atualizar estoque: {e}")
    finally:
        conn.close()

# FUNÇÕES DE GERENCIAMENTO DE USUÁRIOS
def listar_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, perfil FROM usuarios")
    linhas = cursor.fetchall()
    conn.close()
    return linhas

def adicionar_usuario(nome, senha, perfil):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nome, senha, perfil) VALUES (?, ?, ?)", (nome, senha, perfil))
    conn.commit()
    conn.close()

def deletar_usuario(id_usuario):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
    conn.commit()
    conn.close()

def listar_pedidos_abertos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, data_criacao, colaborador FROM pedidos WHERE status = 'Aberto'")
    linhas = cursor.fetchall()
    conn.close()
    return linhas

def atribuir_colaboradores_pedido(pedido_id, nomes_colaboradores):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE pedidos SET colaborador = ? WHERE id = ?", (nomes_colaboradores, pedido_id))
    conn.commit()
    conn.close()

def atualizar_produto_completo(id_produto, nome, quantidade, qtd_minima, preco, corredor, prateleira, lugar, sku):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE produtos 
        SET nome=?, quantidade=?, qtd_minima=?, preco=?, corredor=?, prateleira=?, lugar=?, sku=? 
        WHERE id=?
    """, (nome, quantidade, qtd_minima, preco, corredor, prateleira, lugar, sku, id_produto))
    conn.commit()
    conn.close()

def deletar_pedido(pedido_id):
    conn = conectar()
    cursor = conn.cursor()
    # Primeiro apaga os itens associados à ordem
    cursor.execute("DELETE FROM itens_pedido WHERE pedido_id = ?", (pedido_id,))
    # Depois apaga a capa da ordem
    cursor.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
    
    # FORÇA O RESET DO CONTADOR: 
    # Diz ao SQLite para olhar para o maior ID que sobrou e ajustar o contador para ele
    cursor.execute("UPDATE sqlite_sequence SET seq = (SELECT COALESCE(MAX(id), 0) FROM pedidos) WHERE name = 'pedidos'")
    
    conn.commit()
    conn.close()