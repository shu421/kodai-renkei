import numpy as np
import plotly.graph_objects as go
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


def create_2d_plot(
    positions: np.ndarray,
    lamp_status: list[pulp.value],
    point_covered: list[pulp.value],
    coverage_range: int,
) -> go.Figure:
    is_display_legend_placed_lamps = True
    is_display_legend_not_placed_lamps = True
    is_display_legend_covered_points = True
    is_display_legend_mandatory_points = True
    fig = go.Figure()
    for i, (pos, lamp, cover) in enumerate(zip(positions, lamp_status, point_covered)):
        if lamp == 1:
            if i in mandatory_points:
                fig.add_trace(
                    go.Scatter(
                        x=[pos[0]],
                        y=[pos[1]],
                        mode="markers",
                        marker=dict(color="red", symbol="star", size=15),
                        name="必須カバー地点",
                        showlegend=is_display_legend_mandatory_points,
                    )
                )
                is_display_legend_mandatory_points = False
            else:
                fig.add_trace(
                    go.Scatter(
                        x=[pos[0]],
                        y=[pos[1]],
                        mode="markers",
                        marker=dict(color="blue", symbol="triangle-up", size=12),
                        name="街灯（設置済み）",
                        showlegend=is_display_legend_placed_lamps,
                    )
                )
                is_display_legend_placed_lamps = False
            fig.add_shape(
                type="circle",
                xref="x",
                yref="y",
                x0=pos[0] - coverage_range,
                y0=pos[1] - coverage_range,
                x1=pos[0] + coverage_range,
                y1=pos[1] + coverage_range,
                line_color="red",
                fillcolor="red",
                opacity=0.3,
                name="カバー範囲",
                showlegend=False,
            )
        elif i in mandatory_points:
            show_legend = is_display_legend_mandatory_points
            fig.add_trace(
                go.Scatter(
                    x=[pos[0]],
                    y=[pos[1]],
                    mode="markers",
                    marker=dict(color="red", symbol="star", size=15),
                    name="必須カバー地点",
                    showlegend=show_legend,
                )
            )
            is_display_legend_mandatory_points = False
        elif cover == 0:
            show_legend = i not in mandatory_points and is_display_legend_covered_points
            fig.add_trace(
                go.Scatter(
                    x=[pos[0]],
                    y=[pos[1]],
                    mode="markers",
                    marker=dict(color="black", symbol="circle", size=10),
                    name="カバーされていない地点",
                    showlegend=show_legend,
                )
            )
            is_display_legend_covered_points = False
        else:
            show_legend = is_display_legend_not_placed_lamps
            fig.add_trace(
                go.Scatter(
                    x=[pos[0]],
                    y=[pos[1]],
                    mode="markers",
                    marker=dict(color="green", symbol="square", size=12),
                    name="カバーされた地点",
                    showlegend=show_legend,
                )
            )
            is_display_legend_not_placed_lamps = False

    fig.update_layout(
        title="街灯設置の結果",
        xaxis_title="x 座標",
        yaxis_title="y 座標",
        legend_title="凡例",
        width=700,
        height=650,
        xaxis=dict(range=[-1, 12]),
        yaxis=dict(range=[-1, 12]),
    )

    return fig


def create_coverage_plot(max_lamps_list: list[int], verbose: bool = False) -> go.Figure:
    coverage_rate = []
    for max_lamps in max_lamps_list:
        _, lamp_status, point_covered = solve_streetlight_problem(
            int(locations),
            positions,
            coverage_range,
            int(max_lamps),
            mandatory_points,
            verbose,
        )
        coverage_rate.append(sum(point_covered) / len(point_covered))
    fig = go.Figure(
        go.Scatter(
            x=max_lamps_list,
            y=coverage_rate,
            mode="lines+markers",
            marker=dict(size=10),
        )
    )
    fig.update_layout(
        title="カバー率の変化",
        xaxis_title="街灯数",
        yaxis_title="カバー率",
        width=700,
        height=500,
    )
    return fig


if __name__ == "__main__":
    # Streamlit interfac
    st.title("街灯設置最適化")

    st.markdown("---")
    st.markdown("### パラメータ")
    locations = st.number_input(
        "街灯を設置できる場所の数", min_value=10, max_value=100, value=20, step=1
    )
    coverage_range = st.slider(
        "街灯がカバーできる距離", min_value=1.0, max_value=5.0, value=2.0, step=0.1
    )
    mandatory_points = st.multiselect(
        "必ずカバーすべき地点のインデックス",
        options=list(range(int(locations))),
        default=[0, 5, 10],
    )

    seed = st.number_input("乱数シード", min_value=0, max_value=100, value=0, step=1)

    st.markdown("---")
    st.markdown("### 結果の可視化")
    max_lamps = st.number_input(
        "設置可能な街灯の最大数", min_value=1, max_value=locations, value=5, step=1
    )

    np.random.seed(seed)
    positions = np.random.rand(int(locations), 2) * 10

    if st.button("結果の可視化"):
        positions, lamp_status, point_covered = solve_streetlight_problem(
            int(locations), positions, coverage_range, int(max_lamps), mandatory_points
        )
        fig = create_2d_plot(positions, lamp_status, point_covered, coverage_range)
        st.plotly_chart(fig)

    st.markdown("---")
    st.markdown("### カバー率のプロット")
    min_max_lamps = st.slider("街灯数の最小値", min_value=1, max_value=locations, value=5, step=1)
    max_max_lamps = st.slider("街灯数の最大値", min_value=1, max_value=locations, value=10, step=1)
    assert min_max_lamps <= max_max_lamps, "最小値が最大値より大きいです"

    if st.button("カバー率のプロット"):
        max_lamps_list = list(range(min_max_lamps, max_max_lamps + 1))

        fig = create_coverage_plot(max_lamps_list, verbose=True)
        st.plotly_chart(fig)
