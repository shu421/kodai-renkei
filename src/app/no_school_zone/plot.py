import numpy as np
import pulp
from plotly import graph_objects as go

from src.app.no_school_zone.solver import solve_streetlight_problem


def create_2d_plot(
    positions: np.ndarray,
    lamp_status: list[pulp.value],
    point_covered: list[pulp.value],
    coverage_range: int,
    mandatory_points: list[int],
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


def create_coverage_plot(
    locations: int,
    positions: np.ndarray,
    coverage_range: int,
    max_lamps_list: list[int],
    mandatory_points: list[int],
    verbose: bool = False,
) -> go.Figure:
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