import banco
import login

def iniciar_sistema():
    print("A iniciar o sistema Voice Picking...")
    

    banco.criar_tabelas()
    

    login.abrir_login()

if __name__ == "__main__":
    iniciar_sistema()