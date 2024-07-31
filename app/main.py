import numpy as np
import streamlit as st

from src.app.plot import create_2d_plot, create_coverage_plot, solve_streetlight_problem

if __name__ == "__main__":
    st.title("街灯設置最適化")

    st.markdown("---")
    st.markdown("### パラメータ")
    locations = st.number_input(
        "街灯を設置できる場所の数", min_value=10, max_value=100, value=20, step=1
    )
    coverage_range = st.slider(
        "街灯がカバーできる距離", min_value=0.1, max_value=5.0, value=2.0, step=0.1
    )
    mandatory_points = st.multiselect(
        "必ずカバーすべき地点のインデックス",
        options=list(range(int(locations))),
        default=[0, 5, 10],
    )

    seed = st.number_input("乱数シード", min_value=0, max_value=100, value=0, step=1)

    # データの生成
    np.random.seed(seed)
    positions = np.random.rand(int(locations), 2) * 10

    st.markdown("---")
    st.markdown("### 結果の可視化")
    max_lamps = st.number_input(
        "設置可能な街灯の最大数", min_value=1, max_value=locations, value=5, step=1
    )
    if st.button("結果の可視化"):
        positions, lamp_status, point_covered = solve_streetlight_problem(
            int(locations),
            positions,
            coverage_range,
            int(max_lamps),
            mandatory_points,
        )
        fig = create_2d_plot(
            positions, lamp_status, point_covered, coverage_range, mandatory_points
        )
        st.plotly_chart(fig)

    st.markdown("---")
    st.markdown("### カバー率のプロット")
    min_max_lamps = st.slider("街灯数の最小値", min_value=1, max_value=locations, value=5, step=1)
    max_max_lamps = st.slider("街灯数の最大値", min_value=1, max_value=locations, value=10, step=1)
    verbose = st.checkbox("最適化結果のステータスを表示する")
    assert min_max_lamps <= max_max_lamps, "最小値が最大値より大きいです"

    if st.button("カバー率のプロット"):
        max_lamps_list = list(range(min_max_lamps, max_max_lamps + 1))

        fig = create_coverage_plot(
            int(locations),
            positions,
            coverage_range,
            max_lamps_list,
            mandatory_points,
            verbose=verbose,
        )
        st.plotly_chart(fig)
