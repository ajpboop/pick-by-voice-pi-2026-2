import customtkinter as ctk
import produtos
import cadastrar_pedidos
import visualizar_pedidos
import entrada_estoque
import historico 
import gerenciar_usuarios

def abrir_menu_admin(usuario):
    ctk.set_appearance_mode("dark")
    janela = ctk.CTk()
    janela.title("Körber WMS - Painel de Controle (Simulação)")
    
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight() - 80 
    janela.geometry(f"{largura_tela}x{altura_tela}+0+0")

    janela.grid_rowconfigure(0, weight=1)
    janela.grid_columnconfigure(1, weight=1) 

    # --- BARRA LATERAL (SIDEBAR) ---
    sidebar = ctk.CTkFrame(janela, width=300, corner_radius=0, fg_color="#1e1e1e")
    sidebar.grid(row=0, column=0, sticky="nsew")
    sidebar.grid_rowconfigure(10, weight=1) 

    # Título imitando o sistema real
    ctk.CTkLabel(sidebar, text="KÖRBER WMS\nMULTILOG", font=("Arial", 20, "bold"), text_color="#3498db").grid(row=0, column=0, padx=20, pady=(40, 10))
    ctk.CTkLabel(sidebar, text=f"Usuário: {usuario}\nPerfil: Administrador", font=("Arial", 14), text_color="gray").grid(row=1, column=0, padx=20, pady=(0, 40))

    area_principal = ctk.CTkFrame(janela, fg_color="transparent")
    area_principal.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    aba_atual = None

    def limpar_area_principal():
        for widget in area_principal.winfo_children():
            widget.destroy()

    def abrir_cadastro():
        nonlocal aba_atual
        if aba_atual == "cadastro": return
        limpar_area_principal()
        produtos.abrir_tela_produtos(area_principal, usuario)
        aba_atual = "cadastro"

    def abrir_tela_pedidos():
        nonlocal aba_atual
        if aba_atual == "cadastrar_pedidos": return
        limpar_area_principal()
        cadastrar_pedidos.abrir_tela_pedidos(area_principal, usuario)
        aba_atual = "cadastrar_pedidos"

    def abrir_tela_estoque():
        nonlocal aba_atual
        if aba_atual == "estoque": return
        limpar_area_principal()
        produtos.abrir_visualizar_estoque(area_principal, usuario)
        aba_atual = "estoque"
        
    def abrir_visualizar_pedidos():
        nonlocal aba_atual
        if aba_atual == "visualizar_pedidos": return
        limpar_area_principal()
        visualizar_pedidos.abrir_tela_pedidos_admin(area_principal)
        aba_atual = "visualizar_pedidos"

    def abrir_tela_entrada_estoque():
        nonlocal aba_atual
        if aba_atual == "entrada_estoque": return
        limpar_area_principal()
        entrada_estoque.abrir_tela_entrada(area_principal)
        aba_atual = "entrada_estoque"

    def abrir_tela_historico():
        nonlocal aba_atual
        if aba_atual == "historico": return
        limpar_area_principal()
        historico.abrir_tela_historico(area_principal)
        aba_atual = "historico"

    def abrir_tela_usuarios():
        nonlocal aba_atual
        if aba_atual == "usuarios": return
        limpar_area_principal()
        gerenciar_usuarios.abrir_tela_usuarios(area_principal)
        aba_atual = "usuarios"

    def mostrar_resumo():
        nonlocal aba_atual
        if aba_atual == "resumo": return
        limpar_area_principal()
        ctk.CTkLabel(area_principal, text="Resumo da Operação", font=("Arial", 24, "bold")).pack(anchor="w", pady=(10, 20))
        ctk.CTkLabel(area_principal, text="Selecione uma opção no menu lateral para iniciar.", text_color="gray").pack(anchor="w")
        aba_atual = "resumo"

    # --- BOTÕES DE NAVEGAÇÃO COM NOMENCLATURA PROFISSIONAL ---
    estilo = {"fg_color": "#555555", "hover_color": "#777777"}

    ctk.CTkButton(sidebar, text="CADASTRAR SKU / ITEM", height=40, **estilo, command=abrir_cadastro).grid(row=2, column=0, padx=20, pady=10, sticky="ew")
    ctk.CTkButton(sidebar, text="CRIAR ORDEM DE SAÍDA", height=40, **estilo, command=abrir_tela_pedidos).grid(row=3, column=0, padx=20, pady=10, sticky="ew")
    ctk.CTkButton(sidebar, text="CONSULTAR ORDENS DE SAÍDA", height=40, **estilo, command=abrir_visualizar_pedidos).grid(row=4, column=0, padx=20, pady=10, sticky="ew")
    ctk.CTkButton(sidebar, text="CONSULTA DE ITENS", height=40, **estilo, command=abrir_tela_estoque).grid(row=5, column=0, padx=20, pady=10, sticky="ew")
    ctk.CTkButton(sidebar, text="ENTRADA DE ESTOQUE", height=40, **estilo, command=abrir_tela_entrada_estoque).grid(row=6, column=0, padx=20, pady=10, sticky="ew")
    ctk.CTkButton(sidebar, text="HISTÓRICO DA OPERAÇÃO", height=40, **estilo, command=abrir_tela_historico).grid(row=7, column=0, padx=20, pady=10, sticky="ew")
    ctk.CTkButton(sidebar, text="GERENCIAR OPERADORES", height=40, **estilo, command=abrir_tela_usuarios).grid(row=8, column=0, padx=20, pady=10, sticky="ew")

    def fazer_logout():
        janela.destroy()
        import login
        login.abrir_login()

    ctk.CTkButton(sidebar, text="Sair / Trocar Usuário", fg_color="#444444", hover_color="#222222", command=fazer_logout).grid(row=11, column=0, padx=20, pady=(10, 20), sticky="ew")
    
    mostrar_resumo()
    janela.mainloop()