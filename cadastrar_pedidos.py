import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import banco

def abrir_tela_pedidos(frame_pai, usuario):
    # Título
    ctk.CTkLabel(frame_pai, text="📝 Criar Ordem de Saída", font=("Arial", 22, "bold")).pack(pady=(15, 20), anchor="w", padx=20)

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="#343638", foreground="white", rowheight=25, fieldbackground="#343638", borderwidth=0)
    style.map('Treeview', background=[('selected', '#1f538d')])
    style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")

    itens_carrinho = []

    # --- DADOS DA ORDEM (Capa) ---
    frame_capa = ctk.CTkFrame(frame_pai, fg_color="#2b2b2b", corner_radius=10)
    frame_capa.pack(fill="x", padx=20, pady=5)

    ctk.CTkLabel(frame_capa, text="Armazém:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    entry_armazem = ctk.CTkEntry(frame_capa, width=150)
    entry_armazem.grid(row=0, column=1, padx=10, pady=10)
    entry_armazem.insert(0, "MTLG-SC005") # Sugestão padrão

    ctk.CTkLabel(frame_capa, text="Depositante:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
    entry_depositante = ctk.CTkEntry(frame_capa, width=150)
    entry_depositante.grid(row=0, column=3, padx=10, pady=10)
    entry_depositante.insert(0, "426441") # Sugestão padrão

    # --- ADICIONAR ITENS ---
    frame_selecao = ctk.CTkFrame(frame_pai, fg_color="#2b2b2b", corner_radius=10)
    frame_selecao.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(frame_selecao, text="Item (SKU | Descrição):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    combo_produtos = ttk.Combobox(frame_selecao, width=60, state="readonly")
    combo_produtos.grid(row=0, column=1, padx=10, pady=10)

    ctk.CTkLabel(frame_selecao, text="Quantidade:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
    entry_qtd = ctk.CTkEntry(frame_selecao, width=100)
    entry_qtd.grid(row=0, column=3, padx=10, pady=10)

    def carregar_produtos_combobox():
        produtos = banco.listar_produtos()
        lista_formatada = []
        for p in produtos:
            sku = p[8] if len(p)>8 and p[8] else "S/C"
            # Formato: ID | SKU | Nome
            lista_formatada.append(f"{p[0]} | {sku} | {p[1]}")
        combo_produtos['values'] = lista_formatada
        if lista_formatada:
            combo_produtos.current(0)

    def adicionar_ao_carrinho():
        selecao = combo_produtos.get()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um produto!")
            return
        try:
            qtd = int(entry_qtd.get())
            if qtd <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Digite uma quantidade válida.")
            return

        id_produto = int(selecao.split(" | ")[0])
        nome_produto = selecao.split(" | ")[2]

        itens_carrinho.append((id_produto, nome_produto, qtd))
        atualizar_tabela_carrinho()
        entry_qtd.delete(0, tk.END)

    ctk.CTkButton(frame_selecao, text="ADICIONAR ITEM", fg_color="#1f538d", command=adicionar_ao_carrinho).grid(row=0, column=4, padx=20)

    # --- TABELA DO CARRINHO ---
    ctk.CTkLabel(frame_pai, text="Itens da Ordem Atual:", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
    
    colunas = ("ID Produto", "Descrição", "Qtd a Separar")
    tabela = ttk.Treeview(frame_pai, columns=colunas, show='headings', height=6)
    for col in colunas: tabela.heading(col, text=col)
    tabela.column("ID Produto", width=100, anchor="center")
    tabela.column("Descrição", width=400, anchor="center")
    tabela.column("Qtd a Separar", width=150, anchor="center")
    tabela.pack(fill="both", expand=True, padx=20, pady=5)

    def atualizar_tabela_carrinho():
        for item in tabela.get_children(): tabela.delete(item)
        for item in itens_carrinho:
            tabela.insert("", tk.END, values=(item[0], item[1], item[2]))

    def finalizar_pedido():
        if not itens_carrinho:
            messagebox.showwarning("Aviso", "A ordem está vazia! Adicione itens primeiro.")
            return
        
        armazem = entry_armazem.get().strip()
        depositante = entry_depositante.get().strip()
        
        # Envia os dados novos para o banco
        pedido_id = banco.criar_novo_pedido(armazem, depositante)
        
        for item in itens_carrinho:
            banco.adicionar_item_ao_pedido(pedido_id, item[0], item[2])
            
        messagebox.showinfo("Sucesso", f"Ordem #{pedido_id} gerada com sucesso e enviada para separação!")
        itens_carrinho.clear()
        atualizar_tabela_carrinho()

    ctk.CTkButton(frame_pai, text="SALVAR E GERAR ORDEM DE SAÍDA", fg_color="#2c7a3f", font=("Arial", 14, "bold"), height=40, command=finalizar_pedido).pack(fill="x", padx=20, pady=15)

    carregar_produtos_combobox()