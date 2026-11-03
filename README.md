# Voice Picking — Controle de Estoque por Voz

Sistema desktop de controle de estoque com separação de pedidos guiada por voz (*voice picking*). O administrador cadastra produtos e monta pedidos pela interface gráfica; o colaborador escolhe um pedido e o sistema fala quais itens buscar, aguardando ele dizer **"confirmar"** a cada item. Ao final, o estoque é baixado automaticamente e o pedido vai para o histórico.

## Funcionalidades

**Administrador**
- Cadastrar e excluir produtos (nome, quantidade, quantidade mínima, preço)
- Consultar o estoque
- Registrar entrada de estoque, com opção de desfazer a última entrada
- Cadastrar pedidos com vários itens
- Visualizar pedidos e seus itens
- Consultar o histórico de pedidos concluídos (datas e colaborador responsável)

**Colaborador**
- Ver os pedidos em aberto
- Fazer a separação por voz: o sistema fala o produto e a quantidade, e o colaborador responde "confirmar"

## Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3 | Linguagem do projeto |
| SQLite | Banco de dados local (`estoque.db`) |
| CustomTkinter + Tkinter | Interface gráfica |
| VoiceRSS (API) | Texto para fala (voz online em pt-BR) |
| pyttsx3 | Voz de reserva, offline, usada quando o VoiceRSS não está disponível |
| SpeechRecognition + PyAudio | Reconhecimento de fala pelo microfone (usa o serviço do Google, requer internet) |

## Requisitos

- Python 3.10 ou superior
- Microfone e saída de áudio
- Conexão com a internet (para o reconhecimento de fala e para a voz do VoiceRSS)
- Chave gratuita da API do VoiceRSS (opcional; sem ela o sistema usa a voz offline)

## Como baixar

Baixe a pasta do projeto (ou o arquivo `.zip` e extraia) e abra um terminal dentro dela:

```bash
cd "projeto multilog"
```

## Como instalar

### Linux (Ubuntu / Mint / Debian)

1. Instale os pacotes do sistema:

   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-tk python3-dev espeak-ng portaudio19-dev
   ```

2. Crie o ambiente virtual e instale as dependências:

   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

### Windows

1. Instale o Python em <https://www.python.org/downloads/>, marcando **"Add Python to PATH"**.
2. No Prompt de Comando, dentro da pasta do projeto:

   ```bat
   python -m venv .venv
   .venv\Scripts\pip install -r requirements.txt
   ```

## Configurar a voz (VoiceRSS)

1. Crie uma conta gratuita em <https://www.voicerss.org/> e copie a sua chave de API.
2. Na pasta do projeto, crie o arquivo `voicerss_key.txt` contendo apenas a chave (ou defina a variável de ambiente `VOICERSS_KEY`).

A chave é pessoal: não envie o `voicerss_key.txt` junto ao compartilhar o projeto.

O idioma, a voz e a velocidade ficam no topo do `tts.py` (`VOICERSS_IDIOMA`, `VOICERSS_VOZ`, `VOICERSS_VELOCIDADE`). Com `VOICERSS_VOZ` vazio é usada a voz padrão do idioma.

Cada frase nova consome uma requisição da cota diária do plano gratuito. Os áudios já gerados ficam guardados na pasta `cache_voz/` e são reutilizados sem gastar a cota; a pasta pode ser apagada a qualquer momento. Sem chave, sem internet ou com a cota esgotada, o sistema fala com a voz offline (`pyttsx3`).

## Como executar

Linux:

```bash
./run.sh
```

ou

```bash
.venv/bin/python main.py
```

Windows:

```bat
.venv\Scripts\python main.py
```


## Primeiro acesso

Quando o banco de dados ainda não tem nenhum usuário, o sistema cria automaticamente:

- **Usuário:** `admin`
- **Senha:** `admin`

Se o arquivo `estoque.db` já veio com usuários cadastrados, use um deles. Para começar do zero, apague o `estoque.db` — ele é recriado na próxima execução (todos os dados são perdidos).

A tela de gerenciamento de usuários ainda não foi implementada. Para criar um colaborador, insira direto no banco:

```bash
.venv/bin/python -c "import sqlite3; c = sqlite3.connect('estoque.db'); c.execute(\"INSERT INTO usuarios (nome, senha, perfil) VALUES ('joao', '1234', 'Colaborador')\"); c.commit()"
```

O nome de usuário deve ser gravado em minúsculas, pois o login converte o que é digitado para minúsculas.

## Como usar

1. Entre como administrador e cadastre os produtos em **Cadastrar Produto**.
2. Em **Cadastrar Pedidos**, escolha o produto, informe a quantidade, clique em **Adicionar à Lista** e depois em **Salvar e Finalizar Pedido**.
3. Saia e entre como colaborador.
4. Clique em **Ver Pedidos e Iniciar Separação**, selecione um pedido e clique em **Iniciar Voice Picking do Pedido**.
5. Ouça a instrução, recolha o item e diga **"confirmar"**. O sistema repete o processo para cada item.
6. Ao terminar, o pedido é marcado como concluído, o estoque é baixado e ele aparece em **Histórico** no painel do administrador.

## Estrutura do projeto

| Arquivo | Função |
|---|---|
| `main.py` | Ponto de entrada: cria as tabelas e abre o login |
| `banco.py` | Acesso ao banco de dados SQLite |
| `login.py` | Tela de autenticação e direcionamento por perfil |
| `menu_admin.py` | Painel do administrador com menu lateral |
| `menu_colaborador.py` | Painel do colaborador |
| `produtos.py` | Cadastro de produtos e consulta de estoque |
| `cadastrar_pedidos.py` | Criação de pedidos |
| `visualizar_pedidos.py` | Lista de pedidos (admin) e seleção para separação (colaborador) |
| `entrada_estoque.py` | Entrada de mercadoria no estoque |
| `historico.py` | Histórico de pedidos concluídos |
| `teste_picking.py` | Fluxo da separação por voz |
| `tts.py` | Texto para fala (VoiceRSS, cache, voz offline e envio de áudio ao navegador) |
| `audio_port.py` | Canal HTTP privado para ouvir as instruções no navegador |
| `stt.py` | Fala para texto |
| `movimentacoes.py` | Mapa do armazém e algoritmo A* para otimizar rotas de separação |
| `requirements.txt` | Dependências Python |
| `run.sh` | Atalho para executar no Linux |

## Banco de dados

- `usuarios` — nome, senha, perfil (`Administrador` ou `Colaborador`)
- `produtos` — nome, quantidade, quantidade mínima, preço
- `pedidos` — status (`Aberto` / `Concluído`), data de criação, data de conclusão, colaborador
- `itens_pedido` — produto e quantidade de cada item de um pedido

## Solução de problemas

- **Erro ao instalar o PyAudio (`portaudio.h` não encontrado):** falta o pacote `portaudio19-dev` (Linux).
- **A voz saiu robótica e o terminal mostra "VoiceRSS indisponível":** a mensagem traz o motivo (chave inválida, cota diária esgotada ou falta de internet); o sistema seguiu com a voz offline.
- **O sistema não fala:** no Linux, confirme que o `espeak-ng` está instalado.
- **"Erro de conexão com o serviço de reconhecimento":** verifique a internet.
- **O sistema não entende "confirmar":** verifique se o microfone correto está definido como entrada padrão e fale após a mensagem "Pode falar..." aparecer no terminal.
- **Mensagens `ALSA lib ...` ou `jack server is not running` no terminal:** são avisos do sistema de áudio do Linux e podem ser ignorados.

## Limitações conhecidas

- As senhas são armazenadas em texto puro.
- A tela de gerenciamento de usuários não está implementada.
- A baixa de estoque não verifica saldo; a quantidade pode ficar negativa.
- A quantidade mínima é registrada, mas não gera alerta.
- Os produtos não têm campo de localização (corredor, prateleira).
