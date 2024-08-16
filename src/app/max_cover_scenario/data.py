import random

import networkx as nx


def create_data(
    grid_size: int, num_random_edges: int
) -> tuple[nx.Graph, dict[int, tuple[int, int]]]:
    random.seed(0)  # シードを固定してランダム性を再現可能に

    # グラフ構造の定義
    G = nx.Graph()
    positions = {}
    node_count = 0  # 0-indexに変更

    # ノードの追加と位置の設定
    for i in range(grid_size):
        for j in range(grid_size):
            positions[node_count] = (j + 1, grid_size - i)
            G.add_node(node_count)
            node_count += 1

    # 上下左右の隣接するノードをランダムに接続
    initial_edges = []
    for i in range(grid_size * grid_size):
        # 右隣のノードとのエッジ（ランダムに追加）
        if (i + 1) % grid_size != 0:
            initial_edges.append((i, i + 1))
        # 下隣のノードとのエッジ（ランダムに追加）
        if i + grid_size < grid_size * grid_size:
            initial_edges.append((i, i + grid_size))

    random.shuffle(initial_edges)
    G.add_edges_from(initial_edges[:num_random_edges])

    # 追加でランダムにエッジを追加する場合
    all_possible_edges = [
        (i, j)
        for i in range(grid_size * grid_size)
        for j in range(i + 1, grid_size * grid_size)
        if (i, j) not in G.edges()
        and abs(positions[i][0] - positions[j][0]) + abs(positions[i][1] - positions[j][1]) == 1
    ]

    random.shuffle(all_possible_edges)
    selected_random_edges = all_possible_edges[: max(0, num_random_edges - len(G.edges()))]

    G.add_edges_from(selected_random_edges)

    return G, positions
