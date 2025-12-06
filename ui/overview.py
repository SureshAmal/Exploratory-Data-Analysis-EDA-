from pandas import DataFrame
from pyarrow import NULL
import streamlit as st


def render_overview(df: DataFrame):
    """Render the Overview tab: simple data preview."""
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## Data Preview")
    st.dataframe(df.head(100))
    st.markdown("## description")
    st.dataframe(df.describe())

    # TODO: ADDING MORE columns CONFIGS
    # if "Unit_Price" in df.columns:
    #     st.dataframe(
    #         df,
    #         column_config={
    #             "Unit_Price": st.column_config.ProgressColumn(
    #                 "unit price",
    #                 help="The sales volume in USD",
    #                 format="$%f",
    #                 min_value=df["Unit_Price"].min(),
    #                 max_value=df["Unit_Price"].max(),
    #             ),
    #         },
    #         hide_index=True,
    #     )
