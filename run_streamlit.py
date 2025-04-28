import sys
sys.path.append("src")

import streamlit as st


if __name__ == "__main__":
    # Set Streamlit to wide mode
    st.set_page_config(layout="wide", page_title="Main Dashboard", page_icon="📊")

    data_visualisation_page = st.Page(
        "src/visualizer/streamlit_page.py", title="Data Visualisation", icon="📈"
    )

    pg = st.navigation(
        {
            "Visualisation Agent": [data_visualisation_page]
        }
    )

    pg.run()
