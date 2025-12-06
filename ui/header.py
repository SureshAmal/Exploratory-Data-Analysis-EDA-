import streamlit as st


def render_header():
    st.columns([0.25, 3, 0.5])
    st.markdown(
        """<div class="page-header" style="padding: 1rem  1.25rem; margin-bottom: 1rem;">
            <div class="page-title">Data Alchemy Lab</div>
            <div class="page-subtitle">Turn raw files into refined, decision-grade intelligence — profile, cleanse, synthesize, and narrate your data story.</div>
        </div>""",
        unsafe_allow_html=True,
    )
