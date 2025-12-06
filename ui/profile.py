import streamlit as st
from eda import basic_profile, column_profile


def render_profile(df):
    """Render the Profile tab: dataset metrics and column profile."""
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## Dataset Profile")

    profile = basic_profile(df)

    profile_col1, profile_col2, profile_col3, profile_col4 = st.columns(4)

    with profile_col1:
        st.metric("Total Rows", f"{profile['rows']:,}")
    with profile_col2:
        st.metric("Total Columns", f"{profile['columns']:,}")
    with profile_col3:
        total_missing = sum(profile["missing"].values())
        st.metric("Missing Values", f"{total_missing:,}")
    with profile_col4:
        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        st.metric("Memory Usage", f"{memory_mb:.2f} MB")

    st.markdown("### Column Profile")
    st.dataframe(column_profile(df), width="stretch")
