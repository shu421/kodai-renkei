import networkx as nx
import numpy as np
import pulp


def solve_streetlight_problem(
    G: nx.Graph,
    positions: dict[int, tuple[int, int]],
    max_lamps: int,
    commute_route_nodes: list[int],
    bright_threshold: float = 0.8,
    pre_lit_values: dict[int, float] = {},
    verbose: bool = True,
) -> tuple[pulp.LpProblem, list[float], list[float]]:
    num_nodes = len(G.nodes)

    # PuLPの問題設定
    prob = pulp.LpProblem("Street_Light_Placement", pulp.LpMaximize)

    # 変数
    x = pulp.LpVariable.dicts("x", range(num_nodes), cat="Binary")
    y = pulp.LpVariable.dicts("y", range(num_nodes), cat="Continuous")

    # 目的関数
    prob += pulp.lpSum(y[j] for j in range(num_nodes))

    # 各地点の照度は、その地点に設置された街灯と隣接する街灯からの影響度の合計
    for j in range(num_nodes):
        influence_sum = x[j] + pulp.lpSum(
            x[neighbor]
            * (1 / (2 * np.linalg.norm(np.array(positions[j]) - np.array(positions[neighbor]))))
            for neighbor in G.neighbors(j)
            if np.linalg.norm(np.array(positions[j]) - np.array(positions[neighbor])) > 0
        )

        # 既に照度を持つ地点の場合、その初期照度を追加
        if j in pre_lit_values:
            influence_sum += pre_lit_values[j]

        prob += y[j] <= influence_sum

    # 街灯数の制約
    prob += pulp.lpSum(x[i] for i in range(num_nodes)) <= max_lamps

    # 照度の最大値
    for j in range(num_nodes):
        prob += y[j] <= 1

    # 必須カバー地点の照度制約
    for j in commute_route_nodes:
        prob += y[j] >= bright_threshold

    # 通学路の照度制約を追加
    for j in commute_route_nodes:
        prob += y[j] >= bright_threshold

    # 求解
    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    # 結果の取得
    lamp_status = [pulp.value(x[i]) for i in range(num_nodes)]
    point_covered = [pulp.value(y[j]) for j in range(num_nodes)]

    if verbose:
        print(f"最適化結果 (街灯数={max_lamps}): {pulp.LpStatus[prob.status]}")

    return prob, lamp_status, point_covered
