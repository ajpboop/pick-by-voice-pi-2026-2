import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import banco
import threading
from movimentacoes import executar_picking_dinamico

# =======================================================================
# VISÃO DO ADMINISTRADOR: Consultar Ordens de Saída
# =======================================================================
def abrir_tela_pedidos_admin(frame_pai):
    ctk.CTkLabel(frame_pai, text="📦 Consultar Ordens de Saída", font=("Arial", 22, "bold")).pack(pady=(15, 10), anchor="w", padx=20)

    # --- Tabela Superior (Lista de Ordens) ---
    frame_tabela = ctk.CTkFrame(frame_pai, fg_color="transparent")
    frame_tabela.pack(fill="x", padx=20, pady=(0, 5))

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25, fieldbackground="#2b2b2b", borderwidth=0)
    style.map("Treeview", background=[("selected", "#1f538d")])
    style.configure("Treeview.Heading", background="#1e1e1e", foreground="white", font=("Arial", 10, "bold"))

    colunas_pedidos = ("Ordem", "Status", "Data de Criação")
    tabela_pedidos = ttk.Treeview(frame_tabela, columns=colunas_pedidos, show="headings", height=6)

    for col in colunas_pedidos:
        tabela_pedidos.heading(col, text=col)

    tabela_pedidos.column("Ordem", width=100, anchor="center")
    tabela_pedidos.column("Status", width=150, anchor="center")
    tabela_pedidos.column("Data de Criação", width=200, anchor="center")
    tabela_pedidos.pack(fill="x")

    # --- Controles da Tabela Superior (Botão Excluir) ---
    frame_controles = ctk.CTkFrame(frame_pai, fg_color="transparent")
    frame_controles.pack(fill="x", padx=20, pady=(0, 15))

    def excluir_ordem():
        selecionado = tabela_pedidos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma Ordem na tabela superior primeiro!")
            return
        
        pedido_id = tabela_pedidos.item(selecionado[0], 'values')[0]
        
        if messagebox.askyesno("Excluir Ordem", f"Tem a certeza que deseja apagar a Ordem {pedido_id} e todos os seus itens permanentemente?"):
            banco.deletar_pedido(pedido_id)
            messagebox.showinfo("Sucesso", f"Ordem {pedido_id} apagada com sucesso!")
            carregar_pedidos()
            # Limpa a tabela inferior para não mostrar dados de uma ordem apagada
            for item in tabela_itens.get_children():
                tabela_itens.delete(item)

    ctk.CTkButton(frame_controles, text="EXCLUIR ORDEM SELECIONADA", fg_color="#a33535", hover_color="#7a2828", command=excluir_ordem).pack(side="right")

    # --- Tabela Inferior (Detalhes da Ordem de Saída) ---
    ctk.CTkLabel(frame_pai, text="Detalhes da Ordem de Saída:", font=("Arial", 16, "bold")).pack(anchor="w", padx=20, pady=(10, 5))

    frame_itens = ctk.CTkFrame(frame_pai, fg_color="transparent")
    frame_itens.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    colunas_itens = ("Armazém", "Depositante", "Ordem", "Nro Linha", "Item (SKU)", "Descrição", "Quantidade", "Qtd. Conferida")
    tabela_itens = ttk.Treeview(frame_itens, columns=colunas_itens, show="headings", height=8)

    for col in colunas_itens:
        tabela_itens.heading(col, text=col)

    tabela_itens.column("Armazém", width=120, anchor="center")
    tabela_itens.column("Depositante", width=100, anchor="center")
    tabela_itens.column("Ordem", width=80, anchor="center")
    tabela_itens.column("Nro Linha", width=80, anchor="center")
    tabela_itens.column("Item (SKU)", width=120, anchor="center")
    tabela_itens.column("Descrição", width=250, anchor="center")
    tabela_itens.column("Quantidade", width=80, anchor="center")
    tabela_itens.column("Qtd. Conferida", width=100, anchor="center")
    
    tabela_itens.pack(fill="both", expand=True)

    # --- Funções de Lógica ---
    def carregar_pedidos():
        for item in tabela_pedidos.get_children():
            tabela_pedidos.delete(item)
            
        conn = banco.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, status, data_criacao FROM pedidos ORDER BY id DESC")
        for linha in cursor.fetchall():
            tabela_pedidos.insert("", tk.END, values=linha)
        conn.close()

    def ver_detalhes(event):
        selecionado = tabela_pedidos.selection()
        if not selecionado: return
        
        pedido_id = tabela_pedidos.item(selecionado[0], 'values')[0]
        
        for item in tabela_itens.get_children():
            tabela_itens.delete(item)

        conn = banco.conectar()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COALESCE(ped.armazem, 'N/A'), 
                COALESCE(ped.depositante, 'N/A'), 
                ped.id, 
                i.id, 
                COALESCE(prod.sku, 'N/A'), 
                prod.nome, 
                i.quantidade, 
                i.qtd_conferida 
            FROM itens_pedido i
            JOIN produtos prod ON i.produto_id = prod.id
            JOIN pedidos ped ON i.pedido_id = ped.id
            WHERE i.pedido_id = ?
        ''', (pedido_id,))
        
        for linha in cursor.fetchall():
            tabela_itens.insert("", tk.END, values=linha)
        conn.close()

    tabela_pedidos.bind("<ButtonRelease-1>", ver_detalhes) 
    carregar_pedidos()

# =======================================================================
# VISÃO DO COLABORADOR: Ordens em Aberto
# =======================================================================
def abrir_tela_pedidos_colab(janela_pai, usuario):
    janela_pedidos = ctk.CTkToplevel(janela_pai)
    janela_pedidos.title("Ordens em Aberto")
    janela_pedidos.geometry("600x400")
    janela_pedidos.attributes('-topmost', True) 

    ctk.CTkLabel(janela_pedidos, text="📋 Selecione uma Ordem para Separar", font=("Arial", 20, "bold")).pack(pady=15)

    frame_tabela = ctk.CTkFrame(janela_pedidos, fg_color="transparent")
    frame_tabela.pack(fill="both", expand=True, padx=20, pady=10)

    colunas = ("Ordem", "Data de Criação")
    tabela_abertos = ttk.Treeview(frame_tabela, columns=colunas, show="headings")

    for col in colunas:
        tabela_abertos.heading(col, text=col)

    tabela_abertos.column("Ordem", width=150, anchor="center")
    tabela_abertos.column("Data de Criação", width=350, anchor="center")
    tabela_abertos.pack(fill="both", expand=True)

    conn = banco.conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, data_criacao FROM pedidos WHERE status = 'Aberto' ORDER BY id ASC")
    for linha in cursor.fetchall():
        tabela_abertos.insert("", tk.END, values=linha)
    conn.close()

    def iniciar_separacao():
        selecionado = tabela_abertos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma ordem da lista primeiro.")
            return
        
        pedido_id = tabela_abertos.item(selecionado[0], 'values')[0]
        janela_pedidos.destroy() 
        
        thread_voz = threading.Thread(target=executar_picking_dinamico, args=(pedido_id, usuario))
        thread_voz.start()

    ctk.CTkButton(janela_pedidos, text="INICIAR VOICE PICKING DA ORDEM", font=("Arial", 14, "bold"), 
                  height=40, fg_color="#2c7a3f", hover_color="#1f5a2d", command=iniciar_separacao).pack(pady=20, padx=20, fill="x")