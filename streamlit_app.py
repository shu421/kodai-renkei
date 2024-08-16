import streamlit as st

from src.app.max_cover_continuous.run import run as run_max_cover_continuous_app
from src.app.max_cover_scenario.run import run as run_max_cover_scenario_app
from src.app.max_cover_weight.run import run as run_max_cover_weight_app
from src.app.no_school_zone.run import run_no_school_zone_app
from src.app.school_zone.run import run_school_zone_app

if __name__ == "__main__":
    st.title("街灯設置最適化")

    scenario = st.sidebar.selectbox(
        "シナリオを選択してください",
        [
            "街灯の重み付け最大カバー問題",
            "シナリオ付き連続照度最大カバー問題",
            "連続照度最大カバー問題",
            "学校区域内",
            "学校区域外",
        ],
    )
    if scenario == "街灯の重み付け最大カバー問題":
        run_max_cover_weight_app()
    elif scenario == "シナリオ付き連続照度最大カバー問題":
        run_max_cover_scenario_app()
    elif scenario == "連続照度最大カバー問題":
        run_max_cover_continuous_app()
    elif scenario == "学校区域内":
        run_school_zone_app()
    elif scenario == "学校区域外":
        run_no_school_zone_app()
    else:
        raise ValueError(f"Invalid scenario: {scenario}")
