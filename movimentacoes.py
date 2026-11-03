import heapq
import itertools
import time

import banco
from stt import ouvir
from tts import falar


# ==========================================
# 1. MAPEAMENTO E ARMAZÉM
# ==========================================

MAPA_ARMAZEM = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
    [0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
    [0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

MAPEAMENTO_ENDERECOS = {
    ("A", 1, 2): (0, 2),
    ("A", 2, 2): (3, 2),
    ("B", 2, 1): (6, 1),
}

def obter_coordenada_produto(corredor, prateleira, lugar):
    chave = (corredor, prateleira, lugar)
    if chave in MAPEAMENTO_ENDERECOS:
        return MAPEAMENTO_ENDERECOS[chave]
    x_base = (ord(corredor.upper()) - 65) * 3
    return (x_base, lugar)


# ==========================================
# 2. ALGORITMO A* (BUSCA DE CAMINHO)
# ==========================================

class No:
    def __init__(self, posicao, parent=None):
        self.posicao = posicao
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, outro):
        return self.posicao == outro.posicao

    def __lt__(self, outro):
        return self.f < outro.f


def heuristica_manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def a_star(grid, inicio, destino):
    if inicio == destino:
        return [inicio]

    no_inicial = No(inicio)
    no_destino = No(destino)

    open_set = []
    closed_set = set()

    heapq.heappush(open_set, no_inicial)
    linhas, colunas = len(grid), len(grid[0])

    while open_set:
        no_atual = heapq.heappop(open_set)
        closed_set.add(no_atual.posicao)

        if no_atual.posicao == no_destino.posicao:
            caminho = []
            atual = no_atual
            while atual:
                caminho.append(atual.posicao)
                atual = atual.parent
            return caminho[::-1]

        movimentos = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in movimentos:
            nx, ny = no_atual.posicao[0] + dx, no_atual.posicao[1] + dy

            if not (0 <= ny < linhas and 0 <= nx < colunas) or grid[ny][nx] == 1:
                continue

            posicao_vizinho = (nx, ny)
            if posicao_vizinho in closed_set:
                continue

            vizinho = No(posicao_vizinho, no_atual)
            vizinho.g = no_atual.g + 1
            vizinho.h = heuristica_manhattan(vizinho.posicao, no_destino.posicao)
            vizinho.f = vizinho.g + vizinho.h

            if any(v for v in open_set if v.posicao == vizinho.posicao and v.f <= vizinho.f):
                continue

            heapq.heappush(open_set, vizinho)

    return None


# ==========================================
# 3. OTIMIZADOR DE SEQUÊNCIA DE COLETA (TSP)
# ==========================================

def calcular_distancia_caminho(grid, inicio, destino, cache_distancias):
    """Calcula a distância via A* reaproveitando resultados calculados."""
    par = (inicio, destino)
    if par in cache_distancias:
        return cache_distancias[par]

    caminho = a_star(grid, inicio, destino)
    distancia = len(caminho) - 1 if caminho else float('inf')
    cache_distancias[par] = distancia
    return distancia


def otimizar_ordem_coleta(pos_inicial, lista_itens, grid):
    """
    Encontra a sequência exata de produtos que minimiza o trajeto total percorrido.
    'lista_itens' contém dicionários com informações do produto e suas coordenadas.
    """
    if len(lista_itens) <= 1:
        return lista_itens

    cache_distancias = {}
    melhor_sequencia = None
    menor_distancia_total = float('inf')

    # Testa todas as permutações possíveis da ordem de coleta (Ideal para ordens de picking de até 8-10 itens)
    for permutacao in itertools.permutations(lista_itens):
        distancia_atual = 0
        ponto_atual = pos_inicial

        for item in permutacao:
            dist = calcular_distancia_caminho(grid, ponto_atual, item['coord'], cache_distancias)
            distancia_atual += dist
            ponto_atual = item['coord']

        if distancia_atual < menor_distancia_total:
            menor_distancia_total = distancia_atual
            melhor_sequencia = permutacao

    return list(melhor_sequencia)


# ==========================================
# 4. INSTRUÇÕES DE VOZ E COMUNICAÇÃO
# ==========================================

def gerar_instrucoes_voz(caminho, direcao_inicial="NORTE"):
    if not caminho or len(caminho) < 2:
        return ["Você já está no local do produto."], direcao_inicial

    vetores_direcao = {
        (0, -1): "NORTE",
        (0, 1): "SUL",
        (1, 0): "LESTE",
        (-1, 0): "OESTE"
    }

    instrucoes = []
    direcao_atual = direcao_inicial
    passos_frente = 0

    for i in range(len(caminho) - 1):
        p1, p2 = caminho[i], caminho[i + 1]
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]

        proxima_direcao = vetores_direcao.get((dx, dy), direcao_atual)

        if proxima_direcao == direcao_atual:
            passos_frente += 1
        else:
            if passos_frente > 0:
                instrucoes.append(f"Siga em frente por {passos_frente} metros.")
                passos_frente = 0
            instrucoes.append(f"Vire em direção ao {proxima_direcao}.")
            direcao_atual = proxima_direcao
            passos_frente += 1

    if passos_frente > 0:
        instrucoes.append(f"Siga em frente por {passos_frente} metros.")

    return instrucoes, direcao_atual


def comunicar_operador(texto, conexao_online=True):
    falar(texto)


def coordenada_transitavel(grid, coordenada):
    x, y = coordenada
    return (
        0 <= y < len(grid)
        and 0 <= x < len(grid[y])
        and grid[y][x] == 0
    )


# ==========================================
# 5. EXECUÇÃO DINÂMICA DE MOVIMENTAÇÃO
# ==========================================

def executar_picking_dinamico(numero_pedido, nome_colaborador, posicao_inicial=(0, 0), direcao_inicial="SUL"):
    conexao = banco.conectar()
    try:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT i.id, prod.id, prod.nome, i.quantidade,
                   prod.corredor, prod.prateleira, prod.lugar
            FROM itens_pedido i
            JOIN produtos prod ON prod.id = i.produto_id
            WHERE i.pedido_id = ?
        """, (numero_pedido,))
        linhas = cursor.fetchall()
    finally:
        conexao.close()

    if not linhas:
        comunicar_operador(f"A ordem {numero_pedido} não foi encontrada ou não tem itens.")
        return

    if not coordenada_transitavel(MAPA_ARMAZEM, posicao_inicial):
        comunicar_operador("A posição inicial do operador não é válida no mapa do armazém.")
        return

    itens = []
    for item_id, produto_id, nome, quantidade, corredor, prateleira, lugar in linhas:
        if corredor is None or prateleira is None or lugar is None:
            comunicar_operador(f"O produto {nome} não tem endereço completo cadastrado.")
            return

        loc = {
            "corredor": str(corredor).strip().upper(),
            "prateleira": prateleira,
            "lugar": lugar,
        }
        try:
            coord = obter_coordenada_produto(
                loc["corredor"], int(prateleira), int(lugar)
            )
        except (TypeError, ValueError):
            comunicar_operador(f"O endereço cadastrado para {nome} é inválido.")
            return

        if not coordenada_transitavel(MAPA_ARMAZEM, coord):
            comunicar_operador(f"O endereço do produto {nome} não corresponde a uma posição livre no mapa.")
            return

        itens.append({
            "item_id": item_id,
            "id": produto_id,
            "nome": nome,
            "quantidade": quantidade,
            "loc": loc,
            "coord": coord,
        })

    itens_otimizados = otimizar_ordem_coleta(posicao_inicial, itens, MAPA_ARMAZEM)

    # Confirma a rota inteira antes de orientar o operador ou registrar coleta.
    rota = []
    posicao_atual = posicao_inicial
    for item in itens_otimizados:
        caminho = a_star(MAPA_ARMAZEM, posicao_atual, item["coord"])
        if not caminho:
            comunicar_operador(
                f"Não há caminho até o produto {item['nome']}. A ordem não será finalizada."
            )
            return
        rota.append((item, caminho))
        posicao_atual = item["coord"]

    palavras_repetir = ("repete", "repetir", "de novo", "novamente", "repita")
    palavras_confirmar = ("confirmar", "ok", "feito", "pronto", "certo", "concluído")

    def aguardar_confirmacao(instrucao, mensagem_erro, quantidade=None):
        comunicar_operador(instrucao)
        while True:
            resposta = ouvir()
            if not resposta:
                time.sleep(0.5)
                continue

            resposta = resposta.lower()
            if any(palavra in resposta for palavra in palavras_repetir):
                comunicar_operador(instrucao)
            elif any(palavra in resposta for palavra in palavras_confirmar):
                return
            elif quantidade is not None and str(quantidade) in resposta:
                return
            else:
                comunicar_operador(mensagem_erro)

    comunicar_operador(
        f"Iniciando a ordem {numero_pedido} com {len(rota)} itens. Calculando a rota otimizada."
    )
    direcao_atual = direcao_inicial

    for index, (item, caminho) in enumerate(rota, 1):
        instrucoes, direcao_atual = gerar_instrucoes_voz(caminho, direcao_atual)
        comunicar_operador(
            f"Item {index} de {len(rota)}: corredor {item['loc']['corredor']}, "
            f"prateleira {item['loc']['prateleira']}, posição {item['loc']['lugar']}."
        )
        for comando in instrucoes:
            comunicar_operador(comando)

        aguardar_confirmacao(
            "Diga pronto quando chegar ao local ou diga repetir para ouvir novamente.",
            "Não entendi. Diga pronto ao chegar ou repetir.",
        )

        instrucao_item = f"Separe {item['quantidade']} unidades do produto {item['nome']}."
        aguardar_confirmacao(
            instrucao_item,
            "Não validado. Diga a quantidade, feito ou repetir.",
            quantidade=item["quantidade"],
        )

        conexao = banco.conectar()
        try:
            cursor = conexao.cursor()
            cursor.execute(
                "UPDATE itens_pedido SET qtd_conferida = ? WHERE id = ? AND pedido_id = ?",
                (item["quantidade"], item["item_id"], numero_pedido),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(f"Não foi possível registrar o item {item['nome']}.")
            conexao.commit()
        finally:
            conexao.close()

    banco.concluir_pedido_e_atualizar_estoque(numero_pedido, nome_colaborador)
    comunicar_operador(f"Ordem {numero_pedido} separada e finalizada com sucesso.")


if __name__ == "__main__":
    executar_picking_dinamico(1, "Operador Teste")