import re


_COMANDOS_ENCERRAR = re.compile(r"\b(?:sair|logout|encerrar|parar|terminar)\b")
_CONFIRMACOES = re.compile(r"\b(?:sim|ok)\b")
_CONFIRMAR_SAIDA = re.compile(r"\bconfirmar\b")
_RECUSAS = re.compile(r"\b(?:não|nao|cancelar)\b")


def eh_comando_encerrar(texto):
    return bool(_COMANDOS_ENCERRAR.search(texto.lower()))


def eh_confirmacao(texto):
    texto = texto.lower()
    return not _RECUSAS.search(texto) and bool(_CONFIRMACOES.search(texto))


def eh_confirmar_saida(texto):
    texto = texto.lower()
    return not _RECUSAS.search(texto) and bool(_CONFIRMAR_SAIDA.search(texto))


def eh_recusa(texto):
    return bool(_RECUSAS.search(texto.lower()))
