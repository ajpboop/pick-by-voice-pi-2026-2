import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import banco

def abrir_tela_usuarios(frame_pai):
    titulo = ctk.CTkLabel(frame_pai, text="👥 Gerenciamento de Usuários e Atribuições", font=("Arial", 22, "bold"))
    titulo.pack(pady=(15, 10), anchor="w", padx=20)

    # Configuração do modo escuro para as tabelas desta tela
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="#343638", foreground="white", rowheight=25, fieldbackground="#343638", borderwidth=0)
    style.map('Treeview', background=[('selected', '#1f538d')])
    style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")

    # Usar abas para organizar as 3 opções solicitadas
    tabview = ctk.CTkTabview(frame_pai, width=800, height=500)
    tabview.pack(fill="both", expand=True, padx=20, pady=10)

    aba_cadastrar = tabview.add("Cadastrar Usuário")
    aba_atribuir = tabview.add("Atribuir Pedidos")
    aba_excluir = tabview.add("Excluir Usuário")

    # =========================================================
    # ABA 1: CADASTRAR USUÁRIO
    # =========================================================
    ctk.CTkLabel(aba_cadastrar, text="Nome do Usuário:").pack(pady=(20, 5))
    entry_nome = ctk.CTkEntry(aba_cadastrar, width=300)
    entry_nome.pack(pady=5)

    ctk.CTkLabel(aba_cadastrar, text="Senha:").pack(pady=(10, 5))
    entry_senha = ctk.CTkEntry(aba_cadastrar, width=300, show="*")
    entry_senha.pack(pady=5)

    ctk.CTkLabel(aba_cadastrar, text="Perfil (Acesso):").pack(pady=(10, 5))
    combo_perfil = ctk.CTkComboBox(aba_cadastrar, values=["Colaborador", "Administrador"], width=300)
    combo_perfil.pack(pady=5)
    combo_perfil.set("Colaborador")

    def salvar_usuario():
        nome = entry_nome.get().strip()
        senha = entry_senha.get().strip()
        perfil = combo_perfil.get()

        if not nome or not senha:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return
        try:
            banco.adicionar_usuario(nome, senha, perfil)
            messagebox.showinfo("Sucesso", f"Usuário '{nome}' cadastrado com sucesso!")
            entry_nome.delete(0, tk.END)
            entry_senha.delete(0, tk.END)
            carregar_usuarios_exclusao() # Atualiza as listas das outras abas
            carregar_combos_atribuicao() 
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {e}")

    ctk.CTkButton(aba_cadastrar, text="CADASTRAR", fg_color="#2c7a3f", hover_color="#1f5a2d", command=salvar_usuario).pack(pady=30)


    # =========================================================
    # ABA 2: ATRIBUIR PEDIDOS AOS COLABORADORES
    # =========================================================
    frame_pedidos = ctk.CTkFrame(aba_atribuir, fg_color="transparent")
    frame_pedidos.pack(fill="both", expand=True, pady=10)

    colunas_pedidos = ("ID do Pedido", "Data de Criação", "Atribuído a")
    tabela_pedidos = ttk.Treeview(frame_pedidos, columns=colunas_pedidos, show="headings", height=8)
    for col in colunas_pedidos: tabela_pedidos.heading(col, text=col)
    
    tabela_pedidos.column("ID do Pedido", width=100, anchor="center")
    tabela_pedidos.column("Data de Criação", width=200, anchor="center")
    tabela_pedidos.column("Atribuído a", width=300, anchor="center")
    tabela_pedidos.pack(fill="both", expand=True)

    frame_controles_atrib = ctk.CTkFrame(aba_atribuir, fg_color="transparent")
    frame_controles_atrib.pack(fill="x", pady=10)

    ctk.CTkLabel(frame_controles_atrib, text="Colaborador:").grid(row=0, column=0, padx=5)
    combo_colab_atrib = ctk.CTkComboBox(frame_controles_atrib, values=[], width=200)
    combo_colab_atrib.grid(row=0, column=1, padx=5)

    def carregar_combos_atribuicao():
        # Puxa só os que são perfil "Colaborador"
        nomes = [u[1] for u in banco.listar_usuarios() if u[2].lower() == 'colaborador']
        if nomes:
            combo_colab_atrib.configure(values=nomes)
            combo_colab_atrib.set(nomes[0])
        else:
            combo_colab_atrib.configure(values=["Sem colaboradores"])
            combo_colab_atrib.set("Sem colaboradores")

    def carregar_pedidos_abertos():
        for item in tabela_pedidos.get_children(): tabela_pedidos.delete(item)
        for p in banco.listar_pedidos_abertos():
            atribuido = p[2] if p[2] else "Ninguém"
            tabela_pedidos.insert("", tk.END, values=(p[0], p[1], atribuido))

    def atribuir_pedido():
        selecionado = tabela_pedidos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um pedido na tabela!")
            return
        
        colab = combo_colab_atrib.get()
        if colab == "Sem colaboradores" or not colab: return

        pedido_id = tabela_pedidos.item(selecionado[0], 'values')[0]
        atribuido_atual = tabela_pedidos.item(selecionado[0], 'values')[2]

        novo_atribuido = colab
        # Lógica de "um ou mais": Concatena os nomes se já houver alguém atribuído
        if atribuido_atual and atribuido_atual != "Ninguém":
            if colab not in atribuido_atual:
                novo_atribuido = f"{atribuido_atual}, {colab}"
            else:
                messagebox.showinfo("Aviso", "Este colaborador já está neste pedido.")
                return

        banco.atribuir_colaboradores_pedido(pedido_id, novo_atribuido)
        messagebox.showinfo("Sucesso", f"Pedido atribuído a: {novo_atribuido}")
        carregar_pedidos_abertos()

    def limpar_atribuicao():
        selecionado = tabela_pedidos.selection()
        if not selecionado: return
        pedido_id = tabela_pedidos.item(selecionado[0], 'values')[0]
        banco.atribuir_colaboradores_pedido(pedido_id, "")
        messagebox.showinfo("Limpo", "Atribuições removidas deste pedido.")
        carregar_pedidos_abertos()

    ctk.CTkButton(frame_controles_atrib, text="ATRIBUIR (SOMA +)", fg_color="#1f538d", command=atribuir_pedido).grid(row=0, column=2, padx=10)
    ctk.CTkButton(frame_controles_atrib, text="ZERAR ATRIBUIÇÕES", fg_color="#a33535", command=limpar_atribuicao).grid(row=0, column=3, padx=10)


    # =========================================================
    # ABA 3: EXCLUIR USUÁRIO
    # =========================================================
    colunas_users = ("ID", "Nome do Usuário", "Perfil de Acesso")
    tabela_usuarios = ttk.Treeview(aba_excluir, columns=colunas_users, show="headings", height=10)
    for col in colunas_users: tabela_usuarios.heading(col, text=col)
    
    tabela_usuarios.column("ID", width=80, anchor="center")
    tabela_usuarios.column("Nome do Usuário", width=300, anchor="center")
    tabela_usuarios.column("Perfil de Acesso", width=200, anchor="center")
    tabela_usuarios.pack(fill="both", expand=True, pady=10)

    def carregar_usuarios_exclusao():
        for item in tabela_usuarios.get_children(): tabela_usuarios.delete(item)
        for u in banco.listar_usuarios():
            tabela_usuarios.insert("", tk.END, values=(u[0], u[1], u[2]))

    def excluir_usuario():
        selecionado = tabela_usuarios.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um usuário na tabela!")
            return
        
        valores = tabela_usuarios.item(selecionado[0], 'values')
        if valores[1].lower() == 'admin':
            messagebox.showerror("Acesso Negado", "O administrador principal do sistema não pode ser excluído.")
            return

        if messagebox.askyesno("Excluir", f"Tem certeza que deseja apagar o usuário '{valores[1]}'?"):
            banco.deletar_usuario(valores[0])
            messagebox.showinfo("Sucesso", "Usuário removido!")
            carregar_usuarios_exclusao()
            carregar_combos_atribuicao()

    ctk.CTkButton(aba_excluir, text="EXCLUIR USUÁRIO", fg_color="#a33535", command=excluir_usuario).pack(pady=10)

    # Inicia carregando os dados
    carregar_usuarios_exclusao()
    carregar_combos_atribuicao()
    carregar_pedidos_abertos()