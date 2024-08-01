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
    # Create coverage matrix
    cover = np.zeros((locations, locations), dtype=int)
    for i in range(locations):
        for j in range(locations):
            if np.linalg.norm(positions[i] - positions[j]) <= coverage_range:
                cover[i, j] = 1

    # Setup the optimization problem
    prob = pulp.LpProblem("Street_Light_Placement", pulp.LpMaximize)
    x = pulp.LpVariable.dicts("x", range(locations), cat="Binary")
    y = pulp.LpVariable.dicts("y", range(locations), cat="Binary")

    # Objective function
    prob += pulp.lpSum(y[j] for j in range(locations))

    # Constraints
    for j in range(locations):
        prob += y[j] <= pulp.lpSum(cover[i][j] * x[i] for i in range(locations))
    prob += pulp.lpSum(x[i] for i in range(locations)) <= max_lamps
    for j in mandatory_points:
        prob += y[j] == 1

    # Solve the problem
    prob.solve()

    # Extract results
    lamp_status = [pulp.value(x[i]) for i in range(locations)]
    point_covered = [pulp.value(y[j]) for j in range(locations)]

    if verbose:
        st.write(f"最適化結果 (街灯数={max_lamps}): {pulp.LpStatus[prob.status]}")
    return positions, lamp_status, point_covered
