import numpy as np
import streamlit as st

from src.app.school_zone.plot import create_2d_plot, create_coverage_plot
from src.app.school_zone.solver import solve_streetlight_problem


def run_school_zone_app() -> None:
    st.markdown("---")
    st.markdown("## 学校区域内")

    st.markdown("---")
    st.markdown("### パラメータ")
    locations = st.number_input("地点数", min_value=10, max_value=500, value=100, step=1)
    locations = int(locations)
    coverage_range = st.slider(
        "街灯がカバーできる距離", min_value=0.1, max_value=5.0, value=1.0, step=0.1
    )
    mandatory_points = st.multiselect(
        "必ずカバーすべき地点のインデックス",
        options=list(range(int(locations))),
        default=[0, 5, 10],
    )

    # 駅の位置を入力
    station_position_x = st.number_input("駅のx座標", min_value=0, max_value=10, value=1, step=1)
    station_position_y = st.number_input("駅のy座標", min_value=0, max_value=10, value=1, step=1)
    station_position = np.array([station_position_x, station_position_y])

    # 学校の位置を入力
    school_position_x = st.number_input("学校のx座標", min_value=0, max_value=10, value=9, step=1)
    school_position_y = st.number_input("学校のy座標", min_value=0, max_value=10, value=9, step=1)
    school_position = np.array([school_position_x, school_position_y])

    # 通学路上の追加地点数を入力
    num_intermediate_points = st.number_input(
        "通学路上の追加地点数", min_value=1, max_value=10, value=10, step=1
    )
    num_intermediate_points = int(num_intermediate_points)

    # 乱数シードを入力
    seed = st.number_input("乱数シード", min_value=0, max_value=100, value=0, step=1)

    # データの生成
    np.random.seed(seed)
    positions = np.random.rand(int(locations), 2) * 10

    station_index = locations
    school_index = locations + 1

    intermediate_positions = np.linspace(
        station_position, school_position, num=num_intermediate_points + 2
    )[1:-1]
    mandatory_points.extend(list(range(locations + 2, locations + 2 + num_intermediate_points)))
    positions = np.vstack([positions, station_position, school_position, intermediate_positions])
    route_points = list(range(locations + 2, locations + 2 + num_intermediate_points))

    st.markdown("---")
    st.markdown("### 結果の可視化")
    max_lamps = st.number_input(
        "設置可能な街灯の最大数", min_value=1, max_value=locations, value=20, step=1
    )
    max_lamps = int(max_lamps)
    if st.button("結果の可視化"):
        positions, lamp_status, point_covered = solve_streetlight_problem(
            locations,
            positions,
            coverage_range,
            max_lamps,
            mandatory_points,
        )
        fig = create_2d_plot(
            positions,
            lamp_status,
            point_covered,
            coverage_range,
            mandatory_points,
            station_index,
            school_index,
            route_points,
        )
        st.plotly_chart(fig)

    st.markdown("---")
    st.markdown("### カバー率のプロット")
    min_max_lamps = st.slider("街灯数の最小値", min_value=1, max_value=100, value=10, step=1)
    max_max_lamps = st.slider("街灯数の最大値", min_value=1, max_value=100, value=20, step=1)
    verbose = st.checkbox("最適化結果のステータスを表示する")
    assert min_max_lamps <= max_max_lamps, "最小値が最大値より大きいです"

    if st.button("カバー率のプロット"):
        max_lamps_list = list(range(min_max_lamps, max_max_lamps + 1))

        fig = create_coverage_plot(
            locations,
            positions,
            coverage_range,
            max_lamps_list,
            mandatory_points,
            verbose=verbose,
        )
        st.plotly_chart(fig)
