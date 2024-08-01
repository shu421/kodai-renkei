import numpy as np
import pulp
import streamlit as st


def solve_streetlight_problem(
    locations: int,
    positions: np.ndarray,
    coverage_range: int,
    max_lamps: int,
    mandatory_points: list[int],
    verbose: bool = True,
) -> tuple[np.array, list[pulp.value], list[pulp.value]]:
    # カバー行列の更新
    locations = len(positions)  # 全位置の数の更新
    cover = np.zeros((locations, locations), dtype=int)
    for i in range(locations):
        for j in range(locations):
            if np.linalg.norm(positions[i] - positions[j]) <= coverage_range:
                cover[i, j] = 1

    # PuLPの問題設定
    prob = pulp.LpProblem("Street_Light_Placement", pulp.LpMaximize)

    # 変数
    x = pulp.LpVariable.dicts("x", range(locations), cat="Binary")
    y = pulp.LpVariable.dicts("y", range(locations), cat="Binary")

    # 目的関数
    prob += pulp.lpSum(y[j] for j in range(locations))

    # 制約条件
    for j in range(locations):
        prob += y[j] <= pulp.lpSum(cover[i][j] * x[i] for i in range(locations))
    prob += pulp.lpSum(x[i] for i in range(locations)) <= max_lamps

    # 特定の地点を必ずカバーする制約
    for j in mandatory_points:
        prob += y[j] == 1

    # 求解
    prob.solve()

    # 結果の表示
    lamp_status = [pulp.value(x[i]) for i in range(locations)]
    point_covered = [pulp.value(y[j]) for j in range(locations)]

    if verbose:
        st.write(f"最適化結果 (街灯数={max_lamps}): {pulp.LpStatus[prob.status]}")
    return positions, lamp_status, point_covered
