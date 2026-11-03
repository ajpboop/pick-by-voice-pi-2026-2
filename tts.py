import hashlib
import io
import os
import tempfile
import urllib.parse
import urllib.request
import wave

import pyttsx3

import audio_port

PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))

# --- Configurações do VoiceRSS ---
VOICERSS_URL = "https://api.voicerss.org/"
VOICERSS_IDIOMA = "pt-br"
VOICERSS_VOZ = ""  # Vazio = voz padrão do idioma
VOICERSS_VELOCIDADE = 0  # De -10 (lenta) a 10 (rápida)
VOICERSS_FORMATO = "44khz_16bit_mono"
ARQUIVO_CHAVE = os.path.join(PASTA_PROJETO, "voicerss_key.txt")
PASTA_CACHE = os.path.join(PASTA_PROJETO, "cache_voz")


def obter_chave():
    """
    Lê a chave da API da variável de ambiente VOICERSS_KEY ou do arquivo voicerss_key.txt.
    """
    chave = os.environ.get("VOICERSS_KEY", "").strip()
    if not chave and os.path.exists(ARQUIVO_CHAVE):
        with open(ARQUIVO_CHAVE, encoding="utf-8") as arquivo:
            chave = arquivo.read().strip()
    return chave


def baixar_audio(texto, chave):
    """
    Pede ao VoiceRSS o áudio (WAV) do texto. Lança exceção se a API devolver erro.
    """
    parametros = {
        "key": chave,
        "hl": VOICERSS_IDIOMA,
        "src": texto,
        "r": str(VOICERSS_VELOCIDADE),
        "c": "WAV",
        "f": VOICERSS_FORMATO,
    }
    if VOICERSS_VOZ:
        parametros["v"] = VOICERSS_VOZ

    dados = urllib.parse.urlencode(parametros).encode("utf-8")
    with urllib.request.urlopen(VOICERSS_URL, data=dados, timeout=10) as resposta:
        audio = resposta.read()

    # Em caso de falha a API responde com um texto iniciado por "ERROR" em vez do áudio
    if audio[:5] == b"ERROR":
        raise RuntimeError(audio.decode("utf-8", errors="replace"))
    return audio


def obter_audio(texto, chave):
    """
    Devolve o áudio do texto, usando o cache em disco para não gastar requisições repetidas.
    """
    identificador = f"{VOICERSS_IDIOMA}|{VOICERSS_VOZ}|{VOICERSS_VELOCIDADE}|{VOICERSS_FORMATO}|{texto}"
    nome_arquivo = hashlib.sha1(identificador.encode("utf-8")).hexdigest() + ".wav"
    caminho = os.path.join(PASTA_CACHE, nome_arquivo)

    if os.path.exists(caminho):
        with open(caminho, "rb") as arquivo:
            return arquivo.read()

    audio = baixar_audio(texto, chave)
    os.makedirs(PASTA_CACHE, exist_ok=True)
    with open(caminho, "wb") as arquivo:
        arquivo.write(audio)
    return audio


def reproduzir_wav(audio):
    enviado_para_navegador = audio_port.enviar_audio(audio)
    try:
        import pyaudio
    except ImportError as erro:
        if not enviado_para_navegador:
            raise
        print(f"Aviso: PyAudio indisponivel para reproducao local ({erro}).")
        return

    try:
        with wave.open(io.BytesIO(audio), "rb") as wav:
            player = pyaudio.PyAudio()
            stream = None
            try:
                stream = player.open(
                    format=player.get_format_from_width(wav.getsampwidth()),
                    channels=wav.getnchannels(),
                    rate=wav.getframerate(),
                    output=True,
                )
                bloco = wav.readframes(1024)
                while bloco:
                    stream.write(bloco)
                    bloco = wav.readframes(1024)
            finally:
                if stream is not None:
                    stream.stop_stream()
                    stream.close()
                player.terminate()
    except OSError as erro:
        if not enviado_para_navegador:
            raise
        print(f"Aviso: nao foi possivel reproduzir audio localmente ({erro}).")


def falar_offline(texto):
    """
    Voz de reserva (pyttsx3), usada quando o VoiceRSS não está disponível.
    """
    engine = pyttsx3.init()

    # Seleciona uma voz em português (no Linux o padrão do espeak é inglês)
    vozes_pt = [v for v in engine.getProperty('voices') if 'pt' in v.id.lower() or 'portug' in v.name.lower() or 'brazil' in v.name.lower()]
    if vozes_pt:
        vozes_br = [v for v in vozes_pt if 'br' in v.id.lower() or 'brazil' in v.name.lower()]
        vozes_preferidas = vozes_br or vozes_pt
        indice_voz = 1 if len(vozes_preferidas) > 1 else 0
        engine.setProperty('voice', vozes_preferidas[indice_voz].id)

    # Configurações opcionais de voz (velocidade e volume)
    engine.setProperty('rate', 200) # Velocidade da fala (o padrão é ~200)
    engine.setProperty('volume', 1.0) # Volume de 0.0 a 1.0

    if not audio_port.canal_ativo():
        engine.say(texto)
        engine.runAndWait()
        return

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as arquivo_temporario:
        caminho_audio = arquivo_temporario.name
    try:
        engine.save_to_file(texto, caminho_audio)
        engine.runAndWait()
        with open(caminho_audio, "rb") as arquivo:
            reproduzir_wav(arquivo.read())
    finally:
        os.unlink(caminho_audio)


def falar(texto):
    """
    Recebe um texto e o converte em áudio falado.
    Usa o VoiceRSS e, se ele falhar (sem chave, sem internet, limite diário), a voz offline.
    """
    print(f"Sistema: {texto}")

    chave = obter_chave()
    if chave:
        try:
            reproduzir_wav(obter_audio(texto, chave))
            return
        except Exception as erro:
            print(f"Aviso: VoiceRSS indisponível ({erro}). A usar a voz offline.")

    falar_offline(texto)

# Teste rápido executando apenas este arquivo
if __name__ == "__main__":
    falar("Vá para o corredor A, prateleira 2.")
