import customtkinter as ctk
import threading
import banco
import visualizar_pedidos
from logout import eh_comando_encerrar, eh_confirmacao, eh_confirmar_saida
from stt import ouvir
from tts import falar


def abrir_menu_colab(usuario, colaborador_id):
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
        visualizar_pedidos.abrir_tela_pedidos_colab(
            janela_menu, usuario, colaborador_id,
            fazer_logout_sem_registro, iniciar_encerramento_por_voz
        )

    ctk.CTkButton(
        frame_central, 
        text="VER PEDIDOS E INICIAR SEPARAÇÃO", 
        width=300, height=60, font=("Arial", 14, "bold"),
        fg_color="#1f538d", hover_color="#14375e", 
        command=abrir_selecao
    ).pack(pady=20)
    
    # --- NOVA FUNÇÃO PARA TROCAR USUÁRIO ---
    def fazer_logout():
        pedidos_em_andamento = banco.listar_pedidos_em_andamento(colaborador_id)
        if pedidos_em_andamento:
            for pedido_id in pedidos_em_andamento:
                banco.registrar_encerramento_sessao(colaborador_id, pedido_id)
        else:
            banco.registrar_encerramento_sessao(colaborador_id)
        fazer_logout_sem_registro()

    def fazer_logout_sem_registro():
        janela_menu.destroy() # Fecha a tela do colaborador
        import login
        login.abrir_login() # Abre a tela de login novamente

    encerramento_em_andamento = {"ativo": False}

    def encerrar_por_voz(botao, status):
        encerrada = False
        try:
            falar("Diga sair ou logout para solicitar o encerramento da sessão.")
            comando = ouvir(phrase_time_limit=5)
            if not comando or not eh_comando_encerrar(comando):
                janela_menu.after(
                    0,
                    lambda: status.configure(
                        text="Comando não reconhecido. Tente novamente.",
                        text_color="#e74c3c"
                    )
                )
                return

            pedidos_em_andamento = banco.listar_pedidos_em_andamento(colaborador_id)
            if pedidos_em_andamento:
                falar("Pausar pedido? Diga sim ou ok.")
                confirmacao = ouvir(phrase_time_limit=5)
                if not confirmacao or not eh_confirmacao(confirmacao):
                    janela_menu.after(
                        0,
                        lambda: status.configure(
                            text="Pedido mantido. Sessão não encerrada.",
                            text_color="#f39c12"
                        )
                    )
                    return

                for pedido_id in pedidos_em_andamento:
                    banco.registrar_encerramento_sessao(
                        colaborador_id, pedido_id
                    )
            else:
                falar("Confirme a saída dizendo confirmar.")
                confirmacao = ouvir(phrase_time_limit=5)
                if not confirmacao or not eh_confirmar_saida(confirmacao):
                    janela_menu.after(
                        0,
                        lambda: status.configure(
                            text="Saída cancelada.",
                            text_color="#f39c12"
                        )
                    )
                    return

                banco.registrar_encerramento_sessao(colaborador_id)

            encerrada = True
            janela_menu.after(0, fazer_logout_sem_registro)
        finally:
            if not encerrada:
                def reativar_botao():
                    encerramento_em_andamento["ativo"] = False
                    if botao.winfo_exists():
                        botao.configure(state="normal")

                janela_menu.after(0, reativar_botao)

    def iniciar_encerramento_por_voz(botao, status):
        if encerramento_em_andamento["ativo"]:
            return
        encerramento_em_andamento["ativo"] = True
        botao.configure(state="disabled")
        threading.Thread(
            target=encerrar_por_voz, args=(botao, status), daemon=True
        ).start()

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