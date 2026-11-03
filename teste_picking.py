import time
import re
import logging
import banco
from tts import falar
from stt import ouvir

# ---------------------------------------------------------------
# Configuração de logging
# ---------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------
# Constantes de configuração
# ---------------------------------------------------------------
TIMEOUT_RESPOSTA = 30        # segundos máximos esperando resposta válida
MAX_TENTATIVAS_INVALIDAS = 3 # após N respostas inválidas, avança com aviso
PAUSA_LOOP = 0.5             # pausa entre tentativas de ouvir()

PALAVRAS_REPETIR = ["repete", "repetir", "de novo", "novamente", "repita"]
PALAVRAS_CONFIRMAR = ["confirmar", "ok", "feito", "pronto", "certo", "concluído", "concluido"]
PALAVRAS_CANCELAR = ["cancelar", "cancela", "parar", "abortar", "sair"]

# Mapa de números por extenso -> inteiro (para validar quantidade falada)
NUMERAIS_EXTENSO = {
    "zero": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2, "três": 3, "tres": 3,
    "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10,
    "onze": 11, "doze": 12, "treze": 13, "quatorze": 14, "catorze": 14,
    "quinze": 15, "dezesseis": 16, "dezessete": 17, "dezoito": 18, "dezenove": 19,
    "vinte": 20, "trinta": 30, "quarenta": 40, "cinquenta": 50,
    "sessenta": 60, "setenta": 70, "oitenta": 80, "noventa": 90,
    "cem": 100, "cento": 100, "duzentos": 200, "trezentos": 300,
    "quatrocentos": 400, "quinhentos": 500, "seiscentos": 600,
    "setecentos": 700, "oitocentos": 800, "novecentos": 900, "mil": 1000,
}


# ---------------------------------------------------------------
# Exceções customizadas
# ---------------------------------------------------------------
class OperacaoCancelada(Exception):
    """Levantada quando o operador pede para cancelar a separação."""


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def _normalizar(texto: str) -> str:
    """Minúsculas, sem acentos e sem pontuação, para comparação robusta."""
    if not texto:
        return ""
    texto = texto.lower().strip()
    # remove acentos
    acentos = {
        "á": "a", "à": "a", "â": "a", "ã": "a", "ä": "a",
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "í": "i", "ì": "i", "î": "i", "ï": "i",
        "ó": "o", "ò": "o", "ô": "o", "õ": "o", "ö": "o",
        "ú": "u", "ù": "u", "û": "u", "ü": "u",
        "ç": "c", "ñ": "n",
    }
    for k, v in acentos.items():
        texto = texto.replace(k, v)
    texto = re.sub(r"[^\w\s]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def _contem_alguma(texto: str, palavras: list) -> bool:
    """Verifica se o texto contém alguma das palavras (já normalizadas)."""
    texto_norm = _normalizar(texto)
    return any(_normalizar(p) in texto_norm for p in palavras)


def _extrair_numero(texto: str):
    """
    Extrai um número inteiro do texto, seja em dígitos ("3") ou por extenso
    ("três", "vinte e três"). Retorna None se não encontrar.
    """
    if not texto:
        return None

    texto_norm = _normalizar(texto)

    # 1) Tenta dígitos primeiro
    match = re.search(r"\b(\d+)\b", texto_norm)
    if match:
        return int(match.group(1))

    # 2) Tenta por extenso — soma tokens reconhecidos (ex.: "vinte e tres" = 23)
    tokens = texto_norm.split()
    total = 0
    encontrou_algum = False
    for token in tokens:
        if token == "e":
            continue
        if token in NUMERAIS_EXTENSO:
            valor = NUMERAIS_EXTENSO[token]
            # tratamento simplificado: soma (funciona para dezenas + unidades)
            total += valor
            encontrou_algum = True
    return total if encontrou_algum else None


def _validar_quantidade(resposta: str, quantidade_esperada: int) -> bool:
    """
    Retorna True se a resposta corresponde à quantidade esperada.
    Compara por igualdade exata (evita 'um' casar com 'onze').
    """
    numero_falado = _extrair_numero(resposta)
    return numero_falado is not None and numero_falado == quantidade_esperada


def _falar_seguro(mensagem: str) -> None:
    """Wrapper com tratamento de erro para TTS."""
    try:
        falar(mensagem)
    except Exception as exc:
        log.error("Falha no TTS ao falar %r: %s", mensagem, exc)


def _ouvir_seguro():
    """Wrapper com tratamento de erro para STT."""
    try:
        return ouvir()
    except Exception as exc:
        log.error("Falha no STT: %s", exc)
        return None


def _aguardar_confirmacao(
    instrucao: str,
    descricao_confirmacao: str,
    validador=None,
    timeout: float = TIMEOUT_RESPOSTA,
) -> None:
    """
    Loop genérico de confirmação por voz.

    :param instrucao: frase a ser falada inicialmente
    :param descricao_confirmacao: mensagem de ajuda quando resposta inválida
    :param validador: callable(resposta) -> bool, além dos sinônimos padrão.
                      Se None, só aceita sinônimos de confirmação.
    :param timeout: segundos antes de desistir e seguir adiante com aviso
    :raises OperacaoCancelada: se o operador pedir para cancelar
    """
    _falar_seguro(instrucao)
    inicio = time.time()
    tentativas_invalidas = 0

    while True:
        # --- Verificações de tempo e tentativas ---
        if time.time() - inicio > timeout:
            _falar_seguro("Tempo esgotado. Seguindo para o próximo item.")
            log.warning("Timeout aguardando confirmação de: %s", instrucao)
            return

        if tentativas_invalidas >= MAX_TENTATIVAS_INVALIDAS:
            _falar_seguro("Muitas respostas inválidas. Seguindo para o próximo item.")
            log.warning(
                "Máximo de tentativas inválidas atingido (%d) para: %s",
                tentativas_invalidas, instrucao,
            )
            return

        # --- Captura de voz ---
        resposta = _ouvir_seguro()
        if not resposta:
            time.sleep(PAUSA_LOOP)
            continue

        log.info("Resposta recebida: %r", resposta)

        # --- Cancelamento ---
        if _contem_alguma(resposta, PALAVRAS_CANCELAR):
            raise OperacaoCancelada(f"Operador cancelou: {resposta!r}")

        # --- Repetir instrução ---
        if _contem_alguma(resposta, PALAVRAS_REPETIR):
            _falar_seguro(instrucao)
            inicio = time.time()  # renova o timeout
            continue

        # --- Confirmação por sinônimo ---
        if _contem_alguma(resposta, PALAVRAS_CONFIRMAR):
            return

        # --- Confirmação por validador customizado (ex.: quantidade) ---
        if validador and validador(resposta):
            _falar_seguro("Item confirmado.")
            return

        # --- Resposta inválida ---
        tentativas_invalidas += 1
        _falar_seguro(descricao_confirmacao)


# ---------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------
def iniciar_separacao_por_voz(numero_pedido, nome_colaborador):
    conexao = None
    try:
        conexao = banco.conectar()
        cursor = conexao.cursor()
        cursor.execute(
            '''
            SELECT prod.nome, i.quantidade, prod.corredor, prod.prateleira, prod.lugar
            FROM itens_pedido i
            JOIN produtos prod ON i.produto_id = prod.id
            WHERE i.pedido_id = ?
            ''',
            (numero_pedido,),
        )
        itens = cursor.fetchall()
    except Exception as exc:
        log.exception("Erro ao consultar itens do pedido %s", numero_pedido)
        _falar_seguro("Erro ao consultar o banco de dados. Separação cancelada.")
        return
    finally:
        if conexao is not None:
            conexao.close()

    if not itens:
        _falar_seguro(f"A ordem {numero_pedido} não foi encontrada ou não tem itens.")
        log.warning("Pedido %s sem itens.", numero_pedido)
        return

    _falar_seguro(f"Iniciando separação da ordem {numero_pedido}.")
    time.sleep(1)

    itens_processados = 0

    try:
        for idx, item in enumerate(itens, start=1):
            nome_produto = item[0]
            quantidade = item[1]
            corredor = item[2] if item[2] else "não definido"
            prateleira = item[3] if item[3] else "não definida"
            lugar = item[4] if item[4] else "não definido"

            log.info(
                "Item %d/%d: %s (qtd=%s) @ C%s/P%s/L%s",
                idx, len(itens), nome_produto, quantidade, corredor, prateleira, lugar,
            )

            # --- PASSO 1: LOCALIZAÇÃO ---
            instrucao_local = (
                f"Ir para Corredor {corredor}, "
                f"Prateleira {prateleira}, Posição {lugar}."
            )
            _aguardar_confirmacao(
                instrucao=instrucao_local,
                descricao_confirmacao=(
                    "Diga 'pronto' quando chegar, ou 'repetir' para ouvir de novo."
                ),
            )

            # --- PASSO 2: ITEM E QUANTIDADE ---
            instrucao_item = (
                f"Separar {quantidade} unidades do item {nome_produto}."
            )
            _aguardar_confirmacao(
                instrucao=instrucao_item,
                descricao_confirmacao=(
                    f"Não validado. Diga a quantidade, 'feito' ou 'repetir'."
                ),
                validador=lambda resp, q=quantidade: _validar_quantidade(resp, q),
            )

            itens_processados += 1

    except OperacaoCancelada as exc:
        log.warning("Separação cancelada pelo operador: %s", exc)
        _falar_seguro(
            f"Separação da ordem {numero_pedido} cancelada. "
            f"{itens_processados} de {len(itens)} itens processados."
        )
        return

    # --- FINALIZAÇÃO ---
    _falar_seguro("Ordem finalizada com sucesso. Sistema atualizado.")
    try:
        banco.concluir_pedido_e_atualizar_estoque(numero_pedido, nome_colaborador)
        log.info("Pedido %s concluído por %s.", numero_pedido, nome_colaborador)
    except Exception:
        log.exception(
            "Falha ao concluir pedido %s no banco — intervenção manual necessária!",
            numero_pedido,
        )
        _falar_seguro(
            "Atenção: falha ao atualizar o sistema. Contate o supervisor."
        )
        raise


if __name__ == "__main__":
    iniciar_separacao_por_voz(1, "Operador Teste")
