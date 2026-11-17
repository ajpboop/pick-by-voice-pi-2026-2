import queue
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


PORTA_AUDIO = 8765
_fila_audio = queue.Queue()
_servidor = None
_trava = threading.Lock()

_PAGINA = """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Áudio do Voice Picking</title>
  <style>
    body { font: 16px sans-serif; max-width: 36rem; margin: 4rem auto; padding: 0 1rem; }
    button { font: inherit; padding: .8rem 1rem; }
  </style>
</head>
<body>
  <h1>Áudio do Voice Picking</h1>
  <p id="status">Clique para ativar o áudio neste navegador.</p>
  <button id="ativar">Ativar áudio</button>
  <script>
    const status = document.getElementById("status");
    let ativo = false;

    document.getElementById("ativar").addEventListener("click", async () => {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) {
        status.textContent = "Este navegador não oferece suporte à reprodução de áudio.";
        return;
      }

      const contextoAudio = new AudioContext();
      await contextoAudio.resume();
      ativo = true;
      status.textContent = "Áudio ativado. Aguardando instruções...";
      document.getElementById("ativar").disabled = true;
      while (ativo) {
        try {
          const resposta = await fetch("/proximo-audio");
          if (resposta.status === 204) continue;
          if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
          const bytes = await resposta.arrayBuffer();
          const audio = await contextoAudio.decodeAudioData(bytes);
          const fonte = contextoAudio.createBufferSource();
          fonte.buffer = audio;
          fonte.connect(contextoAudio.destination);
          await new Promise((resolve) => {
            fonte.addEventListener("ended", resolve, { once: true });
            fonte.start();
          });
        } catch (erro) {
          status.textContent = `Erro ao receber áudio: ${erro.message}`;
          await new Promise((resolve) => setTimeout(resolve, 1000));
        }
      }
    });
  </script>
</body>
</html>""".encode("utf-8")


class _ServidorAudio(ThreadingHTTPServer):
    daemon_threads = True


class _ManipuladorAudio(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            conteudo = _PAGINA
            tipo = "text/html; charset=utf-8"
        elif self.path == "/proximo-audio":
            try:
                conteudo = _fila_audio.get(timeout=1)
            except queue.Empty:
                self.send_response(204)
                self.end_headers()
                return
            tipo = "audio/wav"
        else:
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(conteudo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(conteudo)

    def log_message(self, formato, *argumentos):
        return


def iniciar_servidor_audio():
    global _servidor
    with _trava:
        if _servidor is not None:
            return
        _servidor = _ServidorAudio(("0.0.0.0", PORTA_AUDIO), _ManipuladorAudio)
        threading.Thread(target=_servidor.serve_forever, daemon=True).start()
    print(
        f"Canal de audio disponivel na porta {PORTA_AUDIO}. "
        "Abra essa porta no VS Code e clique em 'Ativar áudio'."
    )


def enviar_audio(audio):
    if _servidor is not None:
        _fila_audio.put(audio)
        return True
    return False


def canal_ativo():
    return _servidor is not None
