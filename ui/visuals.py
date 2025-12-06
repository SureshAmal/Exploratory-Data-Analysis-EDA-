import streamlit as st
import plotly.express as px
from plotly_theme import BRAND_TEMPLATE
from eda import summary_stats


def render_visuals(df):
    """Render the Visuals tab: summary, distributions, correlation."""
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## Statistical Summary")
    st.dataframe(summary_stats(df), width="stretch")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## Data Distributions")
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if numeric_cols:
        col = st.selectbox("Choose numeric column for histogram", numeric_cols)
        fig = px.histogram(df, x=col, nbins=50, marginal="box", template=BRAND_TEMPLATE)
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No numeric columns found for distributions.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## Correlation Analysis")
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()
        fig = px.imshow(corr, text_auto=True, template=BRAND_TEMPLATE)
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Need at least 2 numeric columns for correlation matrix.")
