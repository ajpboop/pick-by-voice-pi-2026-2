import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import banco

def abrir_tela_historico(frame_pai):
    ctk.CTkLabel(frame_pai, text="🕰️ Histórico de Pedidos Concluídos", font=("Arial", 22, "bold")).pack(pady=(15, 20), anchor="w", padx=20)

    # --- Tabela Superior (Lista de Pedidos Fechados) ---
    frame_tabela = ctk.CTkFrame(frame_pai, fg_color="transparent")
    frame_tabela.pack(fill="x", padx=20, pady=(0, 20))

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25, fieldbackground="#2b2b2b", borderwidth=0)
    style.map("Treeview", background=[("selected", "#1f538d")])
    style.configure("Treeview.Heading", background="#1e1e1e", foreground="white", font=("Arial", 10, "bold"))

    colunas_pedidos = ("ID", "Data Abertura", "Data Fechamento", "Colaborador Responsável")
    tabela_pedidos = ttk.Treeview(frame_tabela, columns=colunas_pedidos, show="headings", height=8)

    for col in colunas_pedidos:
        tabela_pedidos.heading(col, text=col)

    tabela_pedidos.column("ID", width=80, anchor="center")
    tabela_pedidos.column("Data Abertura", width=180, anchor="center")
    tabela_pedidos.column("Data Fechamento", width=180, anchor="center")
    tabela_pedidos.column("Colaborador Responsável", width=250, anchor="center")
    tabela_pedidos.pack(fill="x")

    # --- Tabela Inferior (Itens do Pedido) ---
    ctk.CTkLabel(frame_pai, text="Componentes Separados no Pedido:", font=("Arial", 16, "bold")).pack(anchor="w", padx=20, pady=(10, 5))

    frame_itens = ctk.CTkFrame(frame_pai, fg_color="transparent")
    frame_itens.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    colunas_itens = ("ID Produto", "Nome do Componente", "Qtd Separada")
    tabela_itens = ttk.Treeview(frame_itens, columns=colunas_itens, show="headings", height=6)

    for col in colunas_itens:
        tabela_itens.heading(col, text=col)

    tabela_itens.column("ID Produto", width=100, anchor="center")
    tabela_itens.column("Nome do Componente", width=300, anchor="center")
    tabela_itens.column("Qtd Separada", width=150, anchor="center")
    tabela_itens.pack(fill="both", expand=True)

    # --- Lógica de Carregamento ---
    def carregar_historico():
        for item in tabela_pedidos.get_children():
            tabela_pedidos.delete(item)
            
        conn = banco.conectar()
        cursor = conn.cursor()
        # Busca apenas os concluídos, do mais recente para o mais antigo
        cursor.execute("SELECT id, data_criacao, data_conclusao, colaborador FROM pedidos WHERE status = 'Concluído' ORDER BY id DESC")
        for linha in cursor.fetchall():
            # Trata o caso de pedidos antigos que não tinham colaborador/data
            linha_formatada = (linha[0], linha[1], linha[2] if linha[2] else "N/A", linha[3] if linha[3] else "N/A")
            tabela_pedidos.insert("", tk.END, values=linha_formatada)
        conn.close()

    def ver_detalhes(event):
        selecionado = tabela_pedidos.selection()
        if not selecionado:
            return
        
        pedido_id = tabela_pedidos.item(selecionado[0], 'values')[0]
        
        for item in tabela_itens.get_children():
            tabela_itens.delete(item)

        conn = banco.conectar()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT i.produto_id, p.nome, i.quantidade 
            FROM itens_pedido i
            JOIN produtos p ON i.produto_id = p.id
            WHERE i.pedido_id = ?
        ''', (pedido_id,))
        for linha in cursor.fetchall():
            tabela_itens.insert("", tk.END, values=linha)
        conn.close()

    tabela_pedidos.bind("<ButtonRelease-1>", ver_detalhes)
    carregar_historico()