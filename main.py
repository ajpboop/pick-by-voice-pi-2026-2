import banco
import login
from audio_port import iniciar_servidor_audio


def iniciar_sistema():
    print("A iniciar o sistema Voice Picking...")

    try:
        iniciar_servidor_audio()
    except OSError as erro:
        print(f"Aviso: nao foi possivel iniciar o canal de audio ({erro}).")

    banco.criar_tabelas()

    login.abrir_login()


if __name__ == "__main__":
    iniciar_sistema()