from pandas import DataFrame
import streamlit as st


def render_overview(df: DataFrame):
    """Render the Overview tab: simple data preview."""
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## Data Preview")
    st.dataframe(df.head(100), width="stretch")
    st.markdown("## description")
    st.dataframe(df.describe(), width="stretch")
