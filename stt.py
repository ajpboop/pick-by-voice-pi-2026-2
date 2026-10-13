import speech_recognition as sr

def ouvir():
    """
    Ativa o microfone, escuta o operador e retorna o texto reconhecido.
    """
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Ajustando ruído ambiente...")
        # Calibra o microfone para ignorar ruídos de fundo (comum em armazéns)
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("Pode falar...")
        audio = recognizer.listen(source)
        
    try:
        # Usa o reconhecedor do Google (requer internet)
        texto = recognizer.recognize_google(audio, language="pt-BR")
        print(f"Operador: {texto}")
        return texto.lower()
        
    except sr.UnknownValueError:
        print("Erro: Não entendi o que foi dito.")
        return None
    except sr.RequestError as e:
        print(f"Erro de conexão com o serviço de reconhecimento: {e}")
        return None

# Teste rápido executando apenas este arquivo
if __name__ == "__main__":
    resultado = ouvir()
    if resultado:
        print(f"Comando recebido: {resultado}")