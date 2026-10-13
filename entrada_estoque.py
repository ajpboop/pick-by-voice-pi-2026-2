import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import banco

def abrir_tela_entrada(frame_pai):
    ctk.CTkLabel(frame_pai, text="📦 Entrada de Estoque", font=("Arial", 22, "bold")).pack(pady=(15, 20), anchor="w", padx=20)

    # Memória para armazenar a última operação e permitir o "Desfazer"
    ultima_entrada = None

    # --- Frame Superior (Controlos de Adição) ---
    frame_controles = ctk.CTkFrame(frame_pai, fg_color="#2b2b2b")
    frame_controles.pack(fill="x", padx=20, pady=(0, 20))

    ctk.CTkLabel(frame_controles, text="Quantidade recebida:", font=("Arial", 14)).grid(row=0, column=0, padx=15, pady=15)
    entry_qtd = ctk.CTkEntry(frame_controles, width=120, font=("Arial", 14))
    entry_qtd.grid(row=0, column=1, padx=15, pady=15)

    def confirmar_entrada():
        nonlocal ultima_entrada
        selecionado = tabela.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um componente na lista primeiro.")
            return
        
        try:
            qtd = int(entry_qtd.get())
            if qtd <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Digite um número inteiro maior que zero.")
            return
        
        # Obtém os dados da linha selecionada
        valores = tabela.item(selecionado[0], 'values')
        produto_id = valores[0]
        nome_produto = valores[1]
        
        # Regista a soma na base de dados
        banco.atualizar_quantidade_estoque(produto_id, qtd)
        
        # Guarda os dados na memória e ativa o botão de desfazer
        ultima_entrada = {"id": produto_id, "nome": nome_produto, "qtd": qtd}
        btn_desfazer.configure(state="normal")
        
        messagebox.showinfo("Sucesso", f"Foram adicionadas {qtd} unidades ao componente '{nome_produto}'.")
        
        entry_qtd.delete(0, tk.END)
        carregar_produtos() # Atualiza a tabela

    def desfazer_entrada():
        nonlocal ultima_entrada
        if not ultima_entrada:
            return
            
        produto_id = ultima_entrada["id"]
        nome_produto = ultima_entrada["nome"]
        qtd_adicionada = ultima_entrada["qtd"]
        
        # Reverte a adição (passando a quantidade como valor negativo para subtrair)
        banco.atualizar_quantidade_estoque(produto_id, -qtd_adicionada)
        
        messagebox.showinfo("Desfeito", f"A entrada de {qtd_adicionada} unidades de '{nome_produto}' foi cancelada.")
        
        # Limpa o histórico e desativa o botão novamente para evitar cliques múltiplos
        ultima_entrada = None
        btn_desfazer.configure(state="disabled")
        
        carregar_produtos()

    ctk.CTkButton(frame_controles, text="CONFIRMAR ENTRADA", font=("Arial", 12, "bold"), fg_color="#2c7a3f", 
                  hover_color="#1f5a2d", command=confirmar_entrada).grid(row=0, column=2, padx=20, pady=15)
                  
    # Cria o botão Desfazer (começa desativado/disabled até que uma entrada seja feita)
    btn_desfazer = ctk.CTkButton(frame_controles, text="DESFAZER ÚLTIMA", font=("Arial", 12, "bold"), 
                                 fg_color="#a33535", hover_color="#7a2828", state="disabled", command=desfazer_entrada)
    btn_desfazer.grid(row=0, column=3, padx=10, pady=15)

    # --- Frame Inferior (Tabela de Stock Atual) ---
    frame_tabela = ctk.CTkFrame(frame_pai, fg_color="transparent")
    frame_tabela.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25, fieldbackground="#2b2b2b", borderwidth=0)
    style.map("Treeview", background=[("selected", "#1f538d")])
    style.configure("Treeview.Heading", background="#1e1e1e", foreground="white", font=("Arial", 10, "bold"))

    colunas = ("ID", "Nome do Produto", "Quantidade Atual", "Qtd Mínima")
    tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings")

    for col in colunas:
        tabela.heading(col, text=col)

    tabela.column("ID", width=80, anchor="center")
    tabela.column("Nome do Produto", width=350, anchor="center")
    tabela.column("Quantidade Atual", width=150, anchor="center")
    tabela.column("Qtd Mínima", width=150, anchor="center")
    
    scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scrollbar.set)
    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def carregar_produtos():
        for item in tabela.get_children():
            tabela.delete(item)
        for p in banco.listar_produtos():
            tabela.insert("", tk.END, values=(p[0], p[1], p[2], p[3]))

    carregar_produtos()