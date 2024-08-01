import numpy as np
import plotly.graph_objects as go
import pulp

from src.app.school_zone.solver import solve_streetlight_problem


def create_2d_plot(
    positions: np.ndarray,
    lamp_status: list[pulp.value],
    point_covered: list[pulp.value],
    coverage_range: int,
    mandatory_points: list[int],
    station_index: int,
    school_index: int,
    route_points: list[int],
) -> go.Figure:
    is_display_legend_placed_lamps = True
    is_display_legend_not_placed_lamps = True
    is_display_legend_covered_points = True
    is_display_legend_mandatory_points = True

    fig = go.Figure()
    # Add a path for the commuting route
    route_positions = [positions[idx] for idx in [station_index, *route_points, school_index]]
    fig.add_trace(
        go.Scatter(
            x=[pos[0] for pos in route_positions],
            y=[pos[1] for pos in route_positions],
            mode="lines+markers",
            line=dict(color="black", width=4),
            marker=dict(color="black", size=10, symbol="diamond"),
            name="通学路",
        )
    )

    for i, (pos, lamp, cover) in enumerate(zip(positions, lamp_status, point_covered)):
        # Add a larger square for streetlamps
        if lamp == 1:
            fig.add_shape(
                type="circle",
                xref="x",
                yref="y",
                x0=pos[0] - 0.3,
                y0=pos[1] - 0.3,
                x1=pos[0] + 0.3,
                y1=pos[1] + 0.3,
                line_color="red",
                opacity=1.0,
                line_width=2,
                name="街灯位置",
                showlegend=is_display_legend_placed_lamps,
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
                line_color="yellow",
                fillcolor="yellow",
                opacity=0.3,
                showlegend=False,
            )
        if i == station_index or i == school_index:
            # Mark station and school positions
            symbol, color, label = (
                ("x", "brown", "駅") if i == station_index else ("cross", "purple", "学校")
            )
            fig.add_trace(
                go.Scatter(
                    x=[pos[0]],
                    y=[pos[1]],
                    mode="markers",
                    marker=dict(color=color, symbol=symbol, size=15),
                    name=label,
                    showlegend=True,
                )
            )
        elif i in mandatory_points:
            # Mark mandatory points
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
        elif cover == 0:
            # Mark uncovered points
            fig.add_trace(
                go.Scatter(
                    x=[pos[0]],
                    y=[pos[1]],
                    mode="markers",
                    marker=dict(color="black", symbol="circle", size=10),
                    name="カバーされていない地点",
                    showlegend=is_display_legend_covered_points,
                )
            )
            is_display_legend_covered_points = False
        else:
            # Mark covered points
            fig.add_trace(
                go.Scatter(
                    x=[pos[0]],
                    y=[pos[1]],
                    mode="markers",
                    marker=dict(color="blue", symbol="square", size=12),
                    name="カバーされた地点",
                    showlegend=is_display_legend_not_placed_lamps,
                )
            )
            is_display_legend_not_placed_lamps = False

    coverage = sum(point_covered) / len(positions)

    fig.update_layout(
        title=f"街灯設置の結果: カバー率={coverage:.2f}",
        xaxis_title="x 座標",
        yaxis_title="y 座標",
        legend_title="凡例",
        width=800,
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
    verbose: bool = True,
) -> go.Figure:
    # カバー率の計算
    coverage = []
    for max_lamps in max_lamps_list:
        _, _, point_covered = solve_streetlight_problem(
            locations, positions, coverage_range, max_lamps, mandatory_points, verbose
        )
        coverage.append(sum(point_covered) / locations)

    # グラフの作成
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=max_lamps_list,
            y=coverage,
            mode="lines+markers",
            marker=dict(size=10),
            line=dict(width=2),
        )
    )
    fig.update_layout(
        title="カバー率の変化",
        xaxis_title="街灯数",
        yaxis_title="カバー率",
        xaxis=dict(tickvals=max_lamps_list),
    )
    return fig
