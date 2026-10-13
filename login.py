import customtkinter as ctk
import sqlite3
import menu_admin
import menu_colaborador

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

def abrir_login():
    app = ctk.CTk()
    app.title("Voice Picking - Autenticação")
    app.geometry("450x550")
    # Lê a resolução do monitor atual e aplica
    largura_tela = app.winfo_screenwidth()
    altura_tela = app.winfo_screenheight()
    app.geometry(f"{largura_tela}x{altura_tela}+0+0")
    
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    frame_login = ctk.CTkFrame(app, width=350, height=450, corner_radius=20, fg_color="#2b2b2b")
    frame_login.grid(row=0, column=0)
    frame_login.pack_propagate(False)

    label_titulo = ctk.CTkLabel(frame_login, text="VOICE PICKING", font=("Arial", 26, "bold"), text_color="#3498db")
    label_titulo.pack(pady=(50, 5))

    label_subtitulo = ctk.CTkLabel(frame_login, text="Faça login para acessar a operação", font=("Arial", 12), text_color="gray")
    label_subtitulo.pack(pady=(0, 40))

    campo_usuario = ctk.CTkEntry(frame_login, width=260, height=45, placeholder_text="Usuário", corner_radius=10, font=("Arial", 14))
    campo_usuario.pack(pady=(0, 15))

    campo_senha = ctk.CTkEntry(frame_login, width=260, height=45, placeholder_text="Senha", show="*", corner_radius=10, font=("Arial", 14))
    campo_senha.pack(pady=(0, 10))

    resultado_login = ctk.CTkLabel(frame_login, text="", font=("Arial", 12))
    resultado_login.pack(pady=(0, 15))

    # Dicionário para guardar o resultado do login fora do evento do botão
    dados_acesso = {"sucesso": False, "nome": "", "perfil": ""}

    def validar_login(event=None):
        usuario = campo_usuario.get().strip().lower()
        senha = campo_senha.get()

        if not usuario or not senha:
            resultado_login.configure(text="Preencha todos os campos!", text_color="#e74c3c")
            return

        conn = sqlite3.connect('estoque.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nome, perfil FROM usuarios WHERE nome=? AND senha=?", (usuario, senha))
        resultado = cursor.fetchone() 
        conn.close()

        if resultado:
            resultado_login.configure(text="Acessando...", text_color="#2ecc71")
            
            # Salva os dados e manda o loop do Tkinter parar de forma segura
            dados_acesso["sucesso"] = True
            dados_acesso["nome"] = resultado[0]
            dados_acesso["perfil"] = resultado[1].strip().lower()
            
            # O app.quit() apenas para o ciclo, permitindo que a animação termine em paz
            app.after(300, app.quit)
        else:
            resultado_login.configure(text="Usuário ou senha incorretos!", text_color="#e74c3c")
            campo_senha.delete(0, 'end')

    botao_login = ctk.CTkButton(frame_login, text="ENTRAR", width=260, height=45, font=("Arial", 14, "bold"), 
                                corner_radius=10, fg_color="#1f538d", hover_color="#14375e", command=validar_login)
    botao_login.pack(pady=(0, 20))

    app.bind('<Return>', validar_login)
    
    # O programa fica travado aqui na tela de login até o app.quit() ser chamado
    app.mainloop()
    
    # Limpa a janela de login da memória completamente
    try:
        app.destroy()
    except:
        pass

    # Só agora, com o login encerrado, abrimos a nova tela sem causar conflitos de janelas
    if dados_acesso["sucesso"]:
        if dados_acesso["perfil"] == "administrador":
            menu_admin.abrir_menu_admin(dados_acesso["nome"])
        elif dados_acesso["perfil"] == "colaborador":
            menu_colaborador.abrir_menu_colab(dados_acesso["nome"])
        else:
            print(f"ERRO DE ROTA: O perfil '{dados_acesso['perfil']}' não foi reconhecido.")

if __name__ == "__main__":
    abrir_login()