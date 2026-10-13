import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import banco

def abrir_tela_produtos(frame_pai, usuario):
    cor_fundo = "#242424"
    cor_frame = "#2b2b2b"
    cor_texto = "white"
    cor_input = "#343638"
    
    frame_pai.configure(fg_color=cor_fundo)

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background=cor_input, foreground=cor_texto, rowheight=25, fieldbackground=cor_input, borderwidth=0)
    style.map('Treeview', background=[('selected', '#1f538d')])
    style.configure("Treeview.Heading", background="#565b5e", foreground=cor_texto, relief="flat")
    
    # --- Frame Superior (Formulário) ---
    frame_cadastro = tk.LabelFrame(frame_pai, text="Cadastrar SKU / Item", padx=10, pady=10, bg=cor_frame, fg=cor_texto)
    frame_cadastro.pack(fill="x", padx=10, pady=10)

    # LINHA 0
    tk.Label(frame_cadastro, text="Código (SKU):", bg=cor_frame, fg=cor_texto).grid(row=0, column=0, sticky="w", pady=2)
    entry_sku = tk.Entry(frame_cadastro, width=15, bg=cor_input, fg=cor_texto, insertbackground=cor_texto, relief="flat")
    entry_sku.grid(row=0, column=1, padx=5, pady=2, sticky="w")

    tk.Label(frame_cadastro, text="Descrição:", bg=cor_frame, fg=cor_texto).grid(row=0, column=2, sticky="w", pady=2)
    entry_nome = tk.Entry(frame_cadastro, width=30, bg=cor_input, fg=cor_texto, insertbackground=cor_texto, relief="flat")
    entry_nome.grid(row=0, column=3, padx=5, pady=2, sticky="w")

    # LINHA 1
    tk.Label(frame_cadastro, text="Quantidade:", bg=cor_frame, fg=cor_texto).grid(row=1, column=0, sticky="w", pady=2)
    entry_qtd = tk.Entry(frame_cadastro, width=15, bg=cor_input, fg=cor_texto, insertbackground=cor_texto, relief="flat")
    entry_qtd.grid(row=1, column=1, padx=5, pady=2, sticky="w")

    tk.Label(frame_cadastro, text="Qtd Mínima:", bg=cor_frame, fg=cor_texto).grid(row=1, column=2, sticky="w", pady=2)
    entry_min = tk.Entry(frame_cadastro, width=10, bg=cor_input, fg=cor_texto, insertbackground=cor_texto, relief="flat")
    entry_min.grid(row=1, column=3, sticky="w", padx=5, pady=2)

    tk.Label(frame_cadastro, text="Preço Unitário:", bg=cor_frame, fg=cor_texto).grid(row=1, column=4, sticky="w", pady=2)
    entry_preco = tk.Entry(frame_cadastro, width=10, bg=cor_input, fg=cor_texto, insertbackground=cor_texto, relief="flat")
    entry_preco.grid(row=1, column=5, padx=5, pady=2)

    # LINHA 2
    tk.Label(frame_cadastro, text="Corredor:", bg=cor_frame, fg=cor_texto).grid(row=2, column=0, sticky="w", pady=2)
    entry_corredor = tk.Entry(frame_cadastro, width=15, bg=cor_input, fg=cor_texto, insertbackground=cor_texto, relief="flat")
    entry_corredor.grid(row=2, column=1, padx=5, pady=2, sticky="w")

    tk.Label(frame_cadastro, text="Prateleira:", bg=cor_frame, fg=cor_texto).grid(row=2, column=2, sticky="w", pady=2)
    entry_prateleira = tk.Entry(frame_cadastro, width=10, bg=cor_input, fg=cor_texto, insertbackground=cor_texto, relief="flat")
    entry_prateleira.grid(row=2, column=3, padx=5, pady=2, sticky="w")

    tk.Label(frame_cadastro, text="Lugar:", bg=cor_frame, fg=cor_texto).grid(row=2, column=4, sticky="w", pady=2)
    entry_lugar = tk.Entry(frame_cadastro, width=10, bg=cor_input, fg=cor_texto, insertbackground=cor_texto, relief="flat")
    entry_lugar.grid(row=2, column=5, padx=5, pady=2)

    def salvar():
        try:
            sku = entry_sku.get().strip().upper()
            nome = entry_nome.get()
            qtd = int(entry_qtd.get())
            qtd_min = int(entry_min.get())
            preco = float(entry_preco.get().replace(',', '.'))
            corredor = entry_corredor.get().upper()
            prateleira = entry_prateleira.get()
            lugar = entry_lugar.get()
            
            banco.adicionar_produto(nome, qtd, qtd_min, preco, corredor, prateleira, lugar, sku)
            messagebox.showinfo("Sucesso", "Item adicionado ao armazém!")
            atualizar_tabela()
            
            for entry in [entry_sku, entry_nome, entry_qtd, entry_min, entry_preco, entry_corredor, entry_prateleira, entry_lugar]:
                entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Erro", "Preencha os dados numéricos corretamente.")

    tk.Button(frame_cadastro, text="Salvar Item", bg="#2c7a3f", fg="white", relief="flat", padx=15, command=salvar).grid(row=3, column=0, columnspan=6, pady=10)

    # --- Frame Inferior (Tabela Rápida) ---
    colunas = ("ID", "SKU", "Descrição", "Qtd", "Mínima", "Corredor", "Prateleira", "Lugar")
    tabela = ttk.Treeview(frame_pai, columns=colunas, show='headings')
    for col in colunas: tabela.heading(col, text=col)
    
    tabela.column("ID", width=40, anchor="center")
    tabela.column("SKU", width=120, anchor="center")
    tabela.column("Descrição", width=200, anchor="center")
    tabela.column("Qtd", width=50, anchor="center")
    tabela.column("Mínima", width=60, anchor="center")
    tabela.column("Corredor", width=70, anchor="center")
    tabela.column("Prateleira", width=80, anchor="center")
    tabela.column("Lugar", width=70, anchor="center")
    tabela.pack(fill="both", expand=True, padx=10, pady=10)

    frame_botoes = ctk.CTkFrame(frame_pai, fg_color="transparent")
    frame_botoes.pack(pady=10)

    def excluir():
        selecionado = tabela.selection()
        if not selecionado: return
        valores = tabela.item(selecionado[0], 'values')
        if messagebox.askyesno("Excluir", f"Apagar o item '{valores[2]}' do sistema?"):
            banco.deletar_produto(valores[0])
            atualizar_tabela()

    def abrir_edicao():
        selecionado = tabela.selection()
        if not selecionado: return
        valores = tabela.item(selecionado[0], 'values')
        id_produto = valores[0]

        janela_edicao = ctk.CTkToplevel(frame_pai)
        janela_edicao.title(f"Editar Item #{id_produto}")
        janela_edicao.geometry("450x550")
        janela_edicao.attributes('-topmost', True)

        ctk.CTkLabel(janela_edicao, text="SKU:").pack(pady=(10, 0))
        edit_sku = ctk.CTkEntry(janela_edicao, width=300, justify="center")
        edit_sku.pack()
        edit_sku.insert(0, valores[1] if valores[1] != "-" else "")

        ctk.CTkLabel(janela_edicao, text="Descrição:").pack(pady=(10, 0))
        edit_nome = ctk.CTkEntry(janela_edicao, width=300, justify="center")
        edit_nome.pack()
        edit_nome.insert(0, valores[2])
        
        ctk.CTkLabel(janela_edicao, text="Quantidade Mínima:").pack(pady=(10, 0))
        edit_min = ctk.CTkEntry(janela_edicao, width=300, justify="center")
        edit_min.pack()
        edit_min.insert(0, valores[4])

        ctk.CTkLabel(janela_edicao, text="Corredor:").pack(pady=(10, 0))
        edit_corredor = ctk.CTkEntry(janela_edicao, width=300, justify="center")
        edit_corredor.pack()
        edit_corredor.insert(0, valores[5] if valores[5] != "-" else "")

        ctk.CTkLabel(janela_edicao, text="Prateleira:").pack(pady=(10, 0))
        edit_prat = ctk.CTkEntry(janela_edicao, width=300, justify="center")
        edit_prat.pack()
        edit_prat.insert(0, valores[6] if valores[6] != "-" else "")

        ctk.CTkLabel(janela_edicao, text="Lugar:").pack(pady=(10, 0))
        edit_lugar = ctk.CTkEntry(janela_edicao, width=300, justify="center")
        edit_lugar.pack()
        edit_lugar.insert(0, valores[7] if valores[7] != "-" else "")

        def guardar_alteracoes():
            try:
                sku = edit_sku.get().strip().upper()
                nome = edit_nome.get()
                qtd_min = int(edit_min.get())
                corredor = edit_corredor.get().upper()
                prateleira = edit_prat.get()
                lugar = edit_lugar.get()
                
                for p in banco.listar_produtos():
                    if str(p[0]) == str(id_produto):
                        qtd_original = p[2]
                        preco_original = p[4]
                        break

                banco.atualizar_produto_completo(id_produto, nome, qtd_original, qtd_min, preco_original, corredor, prateleira, lugar, sku)
                janela_edicao.destroy()
                atualizar_tabela()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ctk.CTkButton(janela_edicao, text="SALVAR ALTERAÇÕES", fg_color="#1f538d", command=guardar_alteracoes).pack(pady=20)

    tk.Button(frame_botoes, text="Editar Selecionado", bg="#1f538d", fg="white", relief="flat", padx=15, command=abrir_edicao).grid(row=0, column=0, padx=10)
    tk.Button(frame_botoes, text="Excluir Selecionado", bg="#a33535", fg="white", relief="flat", padx=15, command=excluir).grid(row=0, column=1, padx=10)

    def atualizar_tabela():
        for item in tabela.get_children(): tabela.delete(item)
        for p in banco.listar_produtos():
            sku_val = p[8] if len(p) > 8 and p[8] else "-"
            corr = p[5] if len(p) > 5 and p[5] else "-"
            prat = p[6] if len(p) > 6 and p[6] else "-"
            lug = p[7] if len(p) > 7 and p[7] else "-"
            tabela.insert("", tk.END, values=(p[0], sku_val, p[1], p[2], p[3], corr, prat, lug))

    atualizar_tabela()

def abrir_visualizar_estoque(frame_pai, usuario):
    ctk.CTkLabel(frame_pai, text="📊 Consulta de SKUs / Itens", font=("Arial", 22, "bold")).pack(pady=(15, 20), anchor="w", padx=20)

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25, fieldbackground="#2b2b2b", borderwidth=0)
    style.map("Treeview", background=[("selected", "#1f538d")])
    style.configure("Treeview.Heading", background="#1e1e1e", foreground="white", font=("Arial", 10, "bold"))

    frame_tabela = ctk.CTkFrame(frame_pai, fg_color="transparent")
    frame_tabela.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    colunas = ("ID", "SKU", "Descrição", "Qtd", "Corredor", "Prateleira", "Lugar")
    tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
    for col in colunas: tabela.heading(col, text=col)

    tabela.column("ID", width=40, anchor="center")
    tabela.column("SKU", width=120, anchor="center")
    tabela.column("Descrição", width=250, anchor="center")
    tabela.column("Qtd", width=60, anchor="center")
    tabela.column("Corredor", width=70, anchor="center")
    tabela.column("Prateleira", width=80, anchor="center")
    tabela.column("Lugar", width=70, anchor="center")
    tabela.pack(fill="both", expand=True)

    for p in banco.listar_produtos():
        sku_val = p[8] if len(p) > 8 and p[8] else "-"
        corr = p[5] if len(p) > 5 and p[5] else "-"
        prat = p[6] if len(p) > 6 and p[6] else "-"
        lug = p[7] if len(p) > 7 and p[7] else "-"
        tabela.insert("", tk.END, values=(p[0], sku_val, p[1], p[2], corr, prat, lug))