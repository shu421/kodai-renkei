import streamlit as st

from src.app.no_school_zone.run import run_no_school_zone_app
from src.app.school_zone.run import run_school_zone_app

if __name__ == "__main__":
    st.title("街灯設置最適化")

    st.markdown("---")
    st.markdown("### シナリオ選択")
    scenario = st.selectbox("シナリオを選択してください", ["学校区域内", "学校区域外"])
    if scenario == "学校区域内":
        run_school_zone_app()
    else:
        run_no_school_zone_app()
