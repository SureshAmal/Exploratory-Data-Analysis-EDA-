import streamlit as st
from eda import basic_profile, column_profile


def render_profile(df):
    """Render the Profile tab: dataset metrics and column profile."""
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## Dataset Profile")

    profile = basic_profile(df)

    profile_col1, profile_col2, profile_col3, profile_col4 = st.columns(4)

    # NOTE: Use streamlit metrics: https://docs.streamlit.io/develop/api-reference/data/st.metric

    total_missing = sum(profile["missing"].values())
    memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    profile_col1.metric("Total Rows", f"{profile['rows']:,}", "")
    profile_col2.metric("Total Columns", f"{profile['columns']:,}", "")
    profile_col3.metric("Missing Values", f"{total_missing:,}", "")
    profile_col4.metric("Memory Usage", f"{memory_mb:.2f} MB", "")

    st.markdown("### Column Profile")
    column_prof = column_profile(df)
    if "sample_values" in column_prof:
        st.dataframe(
            column_prof,
            column_config={
                "sample_values": st.column_config.ListColumn(
                    "sample values",
                    help="file column sample values",
                    width="medium",
                ),
            },
            hide_index=True,
        )
    else:
        st.dataframe(column_profile(df), width="stretch")
