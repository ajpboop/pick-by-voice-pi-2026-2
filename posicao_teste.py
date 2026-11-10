import heapq
import itertools
import time
import matplotlib.pyplot as plt

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
# 3. OTIMIZADOR DE SEQUÊNCIA (TSP)
# ==========================================

def otimizar_ordem_coleta(pos_inicial, lista_itens, grid):
    if len(lista_itens) <= 1:
        return lista_itens

    cache_distancias = {}
    melhor_sequencia = None
    menor_distancia_total = float('inf')

    def dist_caminho(inicio, destino):
        par = (inicio, destino)
        if par not in cache_distancias:
            c = a_star(grid, inicio, destino)
            cache_distancias[par] = len(c) - 1 if c else float('inf')
        return cache_distancias[par]

    for permutacao in itertools.permutations(lista_itens):
        dist_atual = 0
        ponto_atual = pos_inicial

        for item in permutacao:
            dist_atual += dist_caminho(ponto_atual, item['coord'])
            ponto_atual = item['coord']

        if dist_atual < menor_distancia_total:
            menor_distancia_total = dist_atual
            melhor_sequencia = permutacao

    return list(melhor_sequencia)


# ==========================================
# 4. VISUALIZAÇÃO EM TEMPO REAL (MATPLOTLIB)
# ==========================================

def desenhar_trajeto_tempo_real(pos_inicial, itens, grid, velocidade=0.2):
    """
    Desenha em tempo real a linha percorrida pelo operador no mapa.
    """
    # 1. Otimiza a ordem dos produtos
    itens_otimizados = otimizar_ordem_coleta(pos_inicial, itens, grid)

    # 2. Gera o caminho completo nó a nó
    caminho_completo = []
    ponto_atual = pos_inicial

    for item in itens_otimizados:
        sub_caminho = a_star(grid, ponto_atual, item['coord'])
        if sub_caminho:
            # Evita duplicar o ponto de transição entre um trecho e outro
            if caminho_completo:
                caminho_completo.extend(sub_caminho[1:])
            else:
                caminho_completo.extend(sub_caminho)
            ponto_atual = item['coord']

    # 3. Configura o gráfico Matplotlib
    plt.ion()  # Ativa o modo interativo
    fig, ax = plt.subplots(figsize=(12, 6))

    linhas, colunas = len(grid), len(grid[0])

    # Desenha a grade do armazém (0 = caminho/branco, 1 = prateleira/cinza escuro)
    ax.imshow(grid, cmap='binary', origin='upper')

    # Ajusta os eixos e a grade visual
    ax.set_xticks(range(colunas))
    ax.set_yticks(range(linhas))
    ax.grid(True, which='both', color='lightgray', linestyle='-', linewidth=0.5)
    ax.set_title("Simulação Visual em Tempo Real - Trajeto de Coleta (Picking)", fontsize=14)
    ax.set_xlabel("Colunas (X)")
    ax.set_ylabel("Linhas (Y)")

    # Marca a posição inicial do operador (Ponto Verde)
    ax.plot(pos_inicial[0], pos_inicial[1], 'go', markersize=12, label='Início (Operador)')

    # Marca os pontos de destino / produtos (Estrelas Vermelhas)
    for idx, item in enumerate(itens_otimizados, 1):
        x, y = item['coord']
        ax.plot(x, y, 'r*', markersize=14, label='Produto' if idx == 1 else "")
        ax.text(x + 0.15, y - 0.15, f"{idx}. {item['nome']}", color='red', fontsize=10, fontweight='bold')

    ax.legend(loc='upper right')
    plt.draw()
    plt.pause(1)  # Pausa inicial para o usuário observar o mapa antes de começar

    # 4. Desenha as retas trecho a trecho em tempo real
    for i in range(len(caminho_completo) - 1):
        p1 = caminho_completo[i]
        p2 = caminho_completo[i + 1]

        # Traça a linha azul entre p1 (x1, y1) e p2 (x2, y2)
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='blue', linewidth=3, alpha=0.8)

        # Atualiza a posição atual do operador com um ponto azul
        ponto_atual_plot, = ax.plot(p2[0], p2[1], 'bo', markersize=7)

        plt.draw()
        plt.pause(velocidade)  # Delay para simular a movimentação em tempo real

        # Remove o marcador do ponto atual para o próximo frame (deixando apenas a linha rastreada)
        if i < len(caminho_completo) - 2:
            ponto_atual_plot.remove()

    # Destaca a posição final do operador
    ax.plot(caminho_completo[-1][0], caminho_completo[-1][1], 'mX', markersize=12, label='Fim da Rota')
    ax.legend(loc='upper right')

    plt.ioff()  # Desativa o modo interativo para manter a janela aberta no final
    print("Trajeto concluído com sucesso!")
    plt.show()


# ==========================================
# 5. EXECUÇÃO DE TESTE
# ==========================================

if __name__ == "__main__":
    # Posição inicial do operador no armazém
    POSICAO_INICIAL = (0, 0)

    # Simulação de produtos cadastrados e suas coordenadas livres no mapa
    PRODUTOS_TESTE = [
        {"nome": "Caixa A", "coord": (0, 2)},
        {"nome": "Caixa B", "coord": (3, 2)},
        {"nome": "Caixa C", "coord": (6, 1)},
        {"nome": "Caixa D", "coord": (12, 3)},
        {"nome": "Caixa E", "coord": (18, 6)},
    ]

    # Executa a simulação visual com intervalo de 0.2 segundos por passo
    desenhar_trajeto_tempo_real(POSICAO_INICIAL, PRODUTOS_TESTE, MAPA_ARMAZEM, velocidade=0.15)
