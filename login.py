import customtkinter as ctk
import sqlite3
import threading
import menu_admin
import menu_colaborador
from stt import ouvir
from tts import falar
# Adicionámos o ImageOps para cortar a imagem sem distorcer
from PIL import Image, ImageOps 

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

def abrir_login():
    app = ctk.CTk()
    app.title("Voice Picking - Autenticação")
    
    largura_tela = app.winfo_screenwidth()
    altura_tela = app.winfo_screenheight()
    app.geometry(f"{largura_tela}x{altura_tela}+0+0")

    # --- LAYOUT DE TELA DIVIDIDA (40% Login Esquerda / 60% Imagem Direita) ---
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=4) # 40% da largura (Login)
    app.grid_columnconfigure(1, weight=6) # 60% da largura (Imagem)

    # === LADO ESQUERDO (PAINEL DE LOGIN) ===
    frame_esquerda = ctk.CTkFrame(app, corner_radius=0, fg_color="#181818")
    frame_esquerda.grid(row=0, column=0, sticky="nsew")

    # Frame invisível para centralizar os elementos do login
    frame_login = ctk.CTkFrame(frame_esquerda, fg_color="transparent")
    frame_login.place(relx=0.5, rely=0.5, anchor="center")

    label_titulo = ctk.CTkLabel(frame_login, text="VOICE PICKING", font=("Arial", 28, "bold"), text_color="#3498db")
    label_titulo.pack(pady=(0, 5))

    label_subtitulo = ctk.CTkLabel(frame_login, text="Faça login para acessar a operação", font=("Arial", 14), text_color="#aaaaaa")
    label_subtitulo.pack(pady=(0, 40))

    campo_usuario = ctk.CTkEntry(frame_login, width=300, height=50, placeholder_text="Usuário", corner_radius=8, font=("Arial", 14), border_color="#333333")
    campo_usuario.pack(pady=(0, 20))

    campo_senha = ctk.CTkEntry(frame_login, width=300, height=50, placeholder_text="Senha", show="*", corner_radius=8, font=("Arial", 14), border_color="#333333")
    campo_senha.pack(pady=(0, 10))

    resultado_login = ctk.CTkLabel(frame_login, text="", font=("Arial", 13))
    resultado_login.pack(pady=(5, 15))

    dados_acesso = {"sucesso": False, "id": None, "nome": "", "perfil": ""}

    def atualizar_mensagem(texto, cor):
        if app.winfo_exists():
            resultado_login.configure(text=texto, text_color=cor)

    def preencher_campos(usuario, senha):
        if app.winfo_exists():
            campo_usuario.delete(0, 'end')
            campo_usuario.insert(0, usuario)
            campo_senha.delete(0, 'end')
            campo_senha.insert(0, senha)

    def reativar_botao():
        if app.winfo_exists() and botao_voz.winfo_exists():
            botao_voz.configure(state="normal")

    def processar_acesso(usuario, senha):
        if not usuario or not senha:
            app.after(0, lambda: atualizar_mensagem("Preencha todos os campos!", "#e74c3c"))
            return

        conn = sqlite3.connect('estoque.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, perfil FROM usuarios WHERE nome=? AND senha=?", (usuario, senha))
        resultado = cursor.fetchone() 
        conn.close()

        if resultado:
            app.after(0, lambda: atualizar_mensagem("Acesso Validado!", "#2ecc71"))
            dados_acesso["sucesso"] = True
            dados_acesso["id"] = resultado[0]
            dados_acesso["nome"] = resultado[1]
            dados_acesso["perfil"] = resultado[2].strip().lower()
            app.after(300, app.quit) 
        else:
            app.after(0, lambda: atualizar_mensagem("Usuário ou senha incorretos!", "#e74c3c"))
            if app.winfo_exists():
                app.after(0, lambda: campo_senha.delete(0, 'end'))

    def processar_codigo_colaborador(codigo):
        conn = sqlite3.connect('estoque.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nome FROM usuarios WHERE senha=? AND lower(trim(perfil))='colaborador'",
            (codigo,)
        )
        resultados = cursor.fetchall()
        conn.close()

        if len(resultados) == 1:
            dados_acesso["sucesso"] = True
            dados_acesso["id"] = resultados[0][0]
            dados_acesso["nome"] = resultados[0][1]
            dados_acesso["perfil"] = "colaborador"
            app.after(0, lambda: atualizar_mensagem("Acesso Validado!", "#2ecc71"))
            app.after(300, app.quit)
        elif resultados:
            app.after(
                0,
                lambda: atualizar_mensagem(
                    "Código compartilhado. Cada colaborador precisa de um código único.",
                    "#e74c3c"
                )
            )
        else:
            app.after(0, lambda: atualizar_mensagem("Código de colaborador inválido.", "#e74c3c"))

    def validar_login_manual(event=None):
        usuario = campo_usuario.get().strip().lower()
        senha = campo_senha.get()
        processar_acesso(usuario, senha)

    def rotina_voz():
        app.after(
            0,
            lambda: atualizar_mensagem(
                "Ouvindo... Diga seu código numérico ou usuário e senha.",
                "#f39c12"
            )
        )
        falar("Diga seu código numérico de colaborador, ou seu usuário e sua senha.")

        # Abre o microfone e reconhece a fala.
        texto_falado = ouvir(phrase_time_limit=10)

        if not texto_falado:
            app.after(0, lambda: atualizar_mensagem("Não foi possível reconhecer sua voz.", "#e74c3c"))
            app.after(0, reativar_botao)
            return

        # Limpa pontuações e converte para minúsculas.
        texto_falado = texto_falado.lower().replace(".", "").replace(",", "").replace("usuária", "usuário").strip()
        codigo = "".join(texto_falado.split())
        if codigo.isascii() and codigo.isdigit():
            processar_codigo_colaborador(codigo)
            app.after(0, reativar_botao)
            return

        if "senha" in texto_falado and "usuário" in texto_falado:
            parte1 = texto_falado.split("senha")[0]
            parte2 = texto_falado.split("senha")[1]
            usuario_falado = parte1.replace("usuário", "").strip()
            senha_falada = parte2.strip().replace(" ", "")
        else:
            palavras = texto_falado.split()
            if len(palavras) >= 2:
                usuario_falado = palavras[0]
                senha_falada = palavras[1]
            else:
                app.after(0, lambda: atualizar_mensagem("Diga: 'Usuário [X] senha [Y]'", "#e74c3c"))
                falar("Formato não reconhecido. Tente novamente.")
                app.after(0, reativar_botao)
                return

        app.after(0, lambda: preencher_campos(usuario_falado, senha_falada))
        processar_acesso(usuario_falado, senha_falada)
        app.after(0, reativar_botao)

    def iniciar_login_voz():
        botao_voz.configure(state="disabled")
        threading.Thread(target=rotina_voz, daemon=True).start()

    botao_login = ctk.CTkButton(frame_login, text="ENTRAR", width=300, height=50, font=("Arial", 14, "bold"), 
                                corner_radius=8, fg_color="#1f538d", hover_color="#14375e", command=validar_login_manual)
    botao_login.pack(pady=(10, 15))

    botao_voz = ctk.CTkButton(frame_login, text="🎤 ACESSO POR VOZ", width=300, height=50, font=("Arial", 14, "bold"), 
                              corner_radius=8, fg_color="#c0392b", hover_color="#922b21", command=iniciar_login_voz)
    botao_voz.pack(pady=(0, 20))

    # === LADO DIREITO (IMAGEM) ===
    # Fundo muito escuro para a imagem transparente se misturar e não parecer feia/estourada
    frame_direita = ctk.CTkFrame(app, corner_radius=0, fg_color="#0a0a0a")
    frame_direita.grid(row=0, column=1, sticky="nsew")

    try:
        # Puxa a imagem e garante que o fundo permite transparência (RGBA)
        imagem_original = Image.open("fundo.png").convert("RGBA")
        largura_img = int(largura_tela * 0.6)
        
        # O ImageOps.fit corta a imagem para a proporção correta, em vez de esmagar a foto
        imagem_corrigida = ImageOps.fit(imagem_original, (largura_img, altura_tela), Image.Resampling.LANCZOS)
        
        # Aplica a transparência. (255 = sólido / 0 = invisível). 90 dá um efeito lavado/cinematográfico.
        imagem_corrigida.putalpha(10)
        
        imagem_fundo = ctk.CTkImage(light_image=imagem_corrigida, dark_image=imagem_corrigida, size=(largura_img, altura_tela))
        
        label_fundo = ctk.CTkLabel(frame_direita, image=imagem_fundo, text="")
        label_fundo.place(relx=0.5, rely=0.5, anchor="center")
    except Exception as e:
        print("Imagem 'fundo.png' não encontrada ou com erro. Carregando ecrã escuro padrão.")

    app.bind('<Return>', validar_login_manual)
    app.mainloop()
    
    try:
        app.destroy()
    except:
        pass

    if dados_acesso["sucesso"]:
        if dados_acesso["perfil"] == "administrador":
            menu_admin.abrir_menu_admin(dados_acesso["nome"])
        elif dados_acesso["perfil"] == "colaborador":
            menu_colaborador.abrir_menu_colab(dados_acesso["nome"], dados_acesso["id"])
        else:
            print(f"ERRO DE ROTA: O perfil '{dados_acesso['perfil']}' não foi reconhecido.")

if __name__ == "__main__":
    abrir_login()
