import networkx as nx
import numpy as np
import plotly.graph_objects as go


def create_2d_plot(
    G: nx.Graph,
    positions: dict[int, tuple[int, int]],
    lamp_status: list[float],
    point_covered: list[float],
    important_points: list[int],
    school_index: int,
    pre_lit_values: dict[int, float],
    commute_route_nodes: list[int] = [],
    node_weights: dict[int, int] = {},
) -> go.Figure:
    # 凡例の表示状態を保持するフラグ
    is_display_legend_placed_lamps = True
    is_display_legend_station = True
    is_display_legend_school = True
    is_display_legend_covered_points = True
    is_display_legend_uncovered_points = True
    is_display_legend_pre_lit_points = True

    fig = go.Figure()

    # 照度によるエッジの影響度を描画
    for edge in G.edges:
        node1, node2 = edge
        pos1 = positions[node1]
        pos2 = positions[node2]

        # エッジの影響度を計算
        distance = np.linalg.norm(np.array(pos1) - np.array(pos2))
        default_influence = 0.5
        influence = default_influence

        # 隣接ノードに対する影響
        if lamp_status[node1] == 1 or lamp_status[node2] == 1:
            influence += np.ones_like(distance) / distance

        # 2点先のノードに対する影響
        second_neighbors1 = set(G.neighbors(node1)).difference([node2])
        second_neighbors2 = set(G.neighbors(node2)).difference([node1])

        for neighbor in second_neighbors1:
            if lamp_status[neighbor] == 1:
                influence += 0.5 / np.linalg.norm(np.array(pos1) - np.array(positions[neighbor]))

        for neighbor in second_neighbors2:
            if lamp_status[neighbor] == 1:
                influence += 0.5 / np.linalg.norm(np.array(pos2) - np.array(positions[neighbor]))

        # エッジの太さと色を影響度に基づいて設定
        edge_width = influence * 5  # 影響度を拡大して太さに反映
        if influence > default_influence:
            edge_color = (
                f"rgba(255, 0, 0, {min(influence / 3, 0.8)})"  # 影響度に応じて透明度を設定
            )
        else:
            edge_color = "rgba(0, 0, 0, 1.0)"  # デフォルトの色（黒）で表示

        fig.add_trace(
            go.Scatter(
                x=[pos1[0], pos2[0]],
                y=[pos1[1], pos2[1]],
                mode="lines",
                line=dict(color=edge_color, width=edge_width),
                showlegend=False,
            )
        )

    # 通学路のエッジ重みを別のレイヤーで描画
    for edge in G.edges:
        node1, node2 = edge
        pos1 = positions[node1]
        pos2 = positions[node2]

        # 通学路のエッジは別の色で描画し、重みに応じて太さを変更
        if node1 in commute_route_nodes and node2 in commute_route_nodes:
            edge_color = "rgba(0, 255, 255, 1.0)"  # Cyan color for commute route edges
            weight = max(node_weights.get(node1, 1), node_weights.get(node2, 1))
            edge_width = weight * 2  # 通学路の重みに応じた太さ

            fig.add_trace(
                go.Scatter(
                    x=[pos1[0], pos2[0]],
                    y=[pos1[1], pos2[1]],
                    mode="lines",
                    line=dict(color=edge_color, width=edge_width),
                    showlegend=False,
                )
            )

    # ノードを描画
    for i, (node, pos) in enumerate(positions.items()):
        lamp = lamp_status[i]
        cover = point_covered[i]

        if node in important_points:
            color = "blue"
            opacity = 1
            size = 15
            name = "住宅地や駅など"
            showlegend = is_display_legend_station
            is_display_legend_station = False
        elif node == school_index:
            color = "green"
            opacity = 1
            size = 15
            name = "日立北高校"
            showlegend = is_display_legend_school
            is_display_legend_school = False
        elif node in pre_lit_values:
            color = "purple"  # 既に照度を持つ地点は紫で表示
            opacity = 1
            size = 10
            name = "既に明るい地点"
            showlegend = is_display_legend_pre_lit_points
            is_display_legend_pre_lit_points = False
        elif lamp == 1:
            color = "red"
            opacity = 1
            size = 20
            name = "街灯の位置"
            showlegend = is_display_legend_placed_lamps
            is_display_legend_placed_lamps = False
        else:
            # カバーされているかどうかでノードの色とサイズを調整
            if cover > 0:
                color = "yellow"
                opacity = 0.5
                size = int(10 + 10 * cover)  # 照度に応じてサイズを拡大
                name = "照らされている地点"
                showlegend = is_display_legend_covered_points
                is_display_legend_covered_points = False
            else:
                color = "black"
                opacity = 1
                size = 8
                name = "照らされていない地点"
                showlegend = is_display_legend_uncovered_points
                is_display_legend_uncovered_points = False

        fig.add_trace(
            go.Scatter(
                x=[pos[0]],
                y=[pos[1]],
                mode="markers",
                marker=dict(
                    color=color, size=size, opacity=opacity, line=dict(color="black", width=1)
                ),
                name=name,
                showlegend=showlegend,
            )
        )

    fig.update_layout(
        title="街灯設置の結果",
        xaxis_title="x 座標",
        yaxis_title="y 座標",
        legend_title="凡例",
        width=800,
        height=650,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    )

    return fig


def create_initial_plot(
    G: nx.Graph,
    positions: dict[int, tuple[int, int]],
    important_points: list[int],
    school_index: int,
    pre_lit_values: dict[int, float],
    commute_route_nodes: list[int] = [],
    node_weights: dict[int, int] = {},
) -> go.Figure:
    # 凡例の表示状態を保持するフラグ
    is_display_legend_station = True
    is_display_legend_school = True
    is_display_legend_pre_lit_points = True

    fig = go.Figure()

    # 通学路のエッジ重みを先に描画
    for edge in G.edges:
        node1, node2 = edge
        pos1 = positions[node1]
        pos2 = positions[node2]

        if node1 in commute_route_nodes and node2 in commute_route_nodes:
            edge_color = "rgba(0, 255, 255, 0.6)"  # Cyan color for commute route edges
            weight1 = node_weights.get(node1, 1)
            weight2 = node_weights.get(node2, 1)
            edge_width = (weight1 + weight2) / 2 * 2  # 通学路の重みに応じた太さ

            fig.add_trace(
                go.Scatter(
                    x=[pos1[0], pos2[0]],
                    y=[pos1[1], pos2[1]],
                    mode="lines",
                    line=dict(color=edge_color, width=edge_width),
                    showlegend=False,
                )
            )

    # 基本的なエッジの描画
    for edge in G.edges:
        node1, node2 = edge
        pos1 = positions[node1]
        pos2 = positions[node2]
        edge_color = "black"
        edge_width = 2

        fig.add_trace(
            go.Scatter(
                x=[pos1[0], pos2[0]],
                y=[pos1[1], pos2[1]],
                mode="lines",
                line=dict(color=edge_color, width=edge_width),
                showlegend=False,
            )
        )

    # ノードの描画
    for node, pos in positions.items():
        if node in important_points:
            color = "blue"
            size = 20
            name = "駅"
            showlegend = is_display_legend_station
            is_display_legend_station = False
        elif node == school_index:
            color = "green"
            size = 20
            name = "日立北高校"
            showlegend = is_display_legend_school
            is_display_legend_school = False
        elif node in pre_lit_values:
            color = "purple"  # 既に照度を持つ地点は紫で表示
            size = 10
            name = "既に明るい地点"
            showlegend = is_display_legend_pre_lit_points
            is_display_legend_pre_lit_points = False
        else:
            color = "black"
            size = 10
            name = "ノード"
            showlegend = False

        fig.add_trace(
            go.Scatter(
                x=[pos[0]],
                y=[pos[1]],
                mode="markers",
                marker=dict(color=color, size=size, line=dict(color="black", width=1)),
                name=name,
                showlegend=showlegend,
            )
        )

    fig.update_layout(
        title="初期データ",
        xaxis_title="x 座標",
        yaxis_title="y 座標",
        legend_title="凡例",
        width=800,
        height=650,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    )

    return fig
