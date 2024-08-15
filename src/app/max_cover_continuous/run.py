import pandas as pd
import streamlit as st

from src.app.max_cover_continuous.data import create_data
from src.app.max_cover_continuous.plot import create_2d_plot, create_initial_plot
from src.app.max_cover_continuous.solver import solve_streetlight_problem


def run() -> None:
    st.sidebar.markdown("### パラメータ設定")
    grid_size = st.sidebar.slider("グリッドのサイズ", min_value=3, max_value=10, value=7, step=1)
    max_value = grid_size * (grid_size - 1) * 2
    num_random_edges = st.sidebar.slider(
        "エッジの数",
        min_value=0,
        max_value=max_value,
        step=1,
        value=max_value - 5,
    )
    G, positions = create_data(grid_size, num_random_edges=num_random_edges)

    # 必ずカバーすべき地点
    mandatory_points = st.sidebar.multiselect(
        "必ずカバーすべき地点のインデックス",
        options=list(range(grid_size**2)),  # グラフのノード数に合わせる
        default=[10, 21, 25],  # 適宜変更
    )

    # 街灯の最大数
    max_lamps = st.sidebar.number_input(
        "設置可能な街灯の最大数", min_value=1, max_value=grid_size**2, value=10, step=1
    )
    max_lamps = int(max_lamps)

    # 既に照度を持つ地点を指定
    pre_lit_points = st.sidebar.multiselect(
        "既に明るい地点のインデックス",
        options=list(range(grid_size**2)),
        default=[1, 20, 30],  # 適宜変更
    )
    pre_lit_values = {}
    for point in pre_lit_points:
        pre_lit_values[point] = st.sidebar.slider(
            f"地点 {point} の初期照度", min_value=0.1, max_value=1.0, value=0.5, step=0.1
        )

    if st.sidebar.button("データ生成"):
        fig = create_initial_plot(
            G,
            positions,
            mandatory_points,
            station_index=0,
            school_index=grid_size**2 - 1,
            pre_lit_values=pre_lit_values,
        )
        st.plotly_chart(fig)

    # 結果の可視化ボタン
    if st.sidebar.button("求解"):
        # 求解
        prob, lamp_status, point_covered = solve_streetlight_problem(
            G,
            positions,
            max_lamps,
            mandatory_points,
            pre_lit_values=pre_lit_values,
        )

        if prob.status != 1:
            st.error("最適化に失敗しました。")
            return

        # 可視化
        fig = create_2d_plot(
            G,
            positions,
            lamp_status,
            point_covered,
            mandatory_points,
            station_index=0,
            school_index=grid_size**2 - 1,
            pre_lit_values=pre_lit_values,
        )
        st.plotly_chart(fig)

        # 評価指標を表示
        objective_value = prob.objective.value()
        coverage = sum(point_covered) / len(point_covered)
        metrics_df = pd.DataFrame(
            {
                "目的関数値": [objective_value],
                "カバー率": [coverage],
            },
            index=["最適化結果"],
        )
        st.write(metrics_df)

        # 結果をテーブルで表示
        result_df = pd.DataFrame(
            {
                "ノード": list(range(grid_size**2)),
                "街灯の設置": lamp_status,
                "照度": point_covered,
            }
        )
        st.write(result_df)
