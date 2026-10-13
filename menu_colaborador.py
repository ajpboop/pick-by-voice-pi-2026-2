import customtkinter as ctk
import visualizar_pedidos

def abrir_menu_colab(usuario):
    janela_menu = ctk.CTk()
    janela_menu.title("Painel do Colaborador")
    janela_menu.geometry("500x400")
    largura_tela = janela_menu.winfo_screenwidth()
    altura_tela = janela_menu.winfo_screenheight()
    janela_menu.geometry(f"{largura_tela}x{altura_tela}+0+0")

    # Configura o grid para centralizar o frame principal
    janela_menu.grid_rowconfigure(0, weight=1)
    janela_menu.grid_columnconfigure(0, weight=1)

    # Frame central invisível para agrupar e centrar os elementos
    frame_central = ctk.CTkFrame(janela_menu, fg_color="transparent")
    frame_central.grid(row=0, column=0)

    titulo = ctk.CTkLabel(frame_central, text="VOICE PICKING - OPERAÇÃO", font=("Arial", 28, "bold"))
    titulo.pack(pady=(20, 10))

    subtitulo = ctk.CTkLabel(frame_central, text=f"Operador: {usuario}", font=("Arial", 14))
    subtitulo.pack(pady=(0, 40))

    def abrir_selecao():
        visualizar_pedidos.abrir_tela_pedidos_colab(janela_menu, usuario)  # Passa o usuário para a função

    ctk.CTkButton(
        frame_central, 
        text="VER PEDIDOS E INICIAR SEPARAÇÃO", 
        width=300, height=60, font=("Arial", 14, "bold"),
        fg_color="#1f538d", hover_color="#14375e", 
        command=abrir_selecao
    ).pack(pady=20)
    
    # --- NOVA FUNÇÃO PARA TROCAR USUÁRIO ---
    def fazer_logout():
        janela_menu.destroy() # Fecha a tela do colaborador
        import login
        login.abrir_login() # Abre a tela de login novamente

    # Botão atualizado para fazer o logout e voltar ao login
    ctk.CTkButton(
        frame_central, 
        text="SAIR / TROCAR USUÁRIO", 
        width=300, height=40, 
        font=("Arial", 12, "bold"),
        fg_color="#a33535", hover_color="#7a2828", 
        command=fazer_logout
    ).pack(pady=10)

    janela_menu.mainloop()