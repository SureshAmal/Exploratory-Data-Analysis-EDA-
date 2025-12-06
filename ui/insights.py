import os
import streamlit as st
from plotly_theme import BRAND_TEMPLATE


def render_insights(data_for_insights, supervisor):
    """Render the AI Insights tab. Expects a supervisor agent instance to handle queries."""
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## AI-Powered Insights")
    st.markdown(
        '<div class="insights-preface">We distill statistical texture, temporal shifts, cohort behaviors and emergent anomalies into a concise narrative. Generate automatic synthesis or interrogate with custom prompts.</div>',
        unsafe_allow_html=True,
    )

    api_key = os.getenv("GEMINI_API_KEY")

    tab1, tab2 = st.tabs(["Automatic Analysis", "Custom Query"])

    with tab1:
        st.info(
            "Generate comprehensive visual insights automatically using AI analysis of your dataset."
        )

        if "auto_insights_generated" not in st.session_state:
            st.session_state.auto_insights_generated = False
            st.session_state.auto_insights_figures = []
            st.session_state.auto_insights_text = None

        if st.button("Generate Insights", key="gen_auto_insights_btn"):
            if not api_key:
                st.error("API key not configured. Please add GEMINI_API_KEY to your .env file.")
            else:
                with st.spinner("Analyzing data and generating visualizations..."):
                    try:
                        figures, insights_text = supervisor.handle_query(
                            data_for_insights,
                            query="Analyze this dataset and provide key findings, trends, and anomalies.",
                            api_key=api_key,
                        )
                        error = None if figures or insights_text else "Agent returned no results."
                        if isinstance(insights_text, str) and insights_text.startswith("Error"):
                            error = insights_text

                        if error:
                            st.error(f"Error generating insights: {error}")
                            st.session_state.auto_insights_generated = False
                        else:
                            st.session_state.auto_insights_figures = figures
                            st.session_state.auto_insights_text = insights_text
                            st.session_state.auto_insights_generated = True

                    except Exception as e:
                        st.error(f"Error generating insights: {str(e)}")
                        st.session_state.auto_insights_generated = False

        if st.session_state.auto_insights_generated:
            if st.session_state.auto_insights_figures:
                st.markdown("### Visual Insights")
                for idx, fig in enumerate(st.session_state.auto_insights_figures):
                    st.plotly_chart(fig, width="stretch", key=f"auto_insight_chart_{idx}")

            if st.session_state.auto_insights_text:
                with st.expander("View Analysis Summary", expanded=False):
                    st.markdown(st.session_state.auto_insights_text)

            if st.button("Clear Results", key="clear_auto_insights"):
                st.session_state.auto_insights_generated = False
                st.session_state.auto_insights_figures = []
                st.session_state.auto_insights_text = None
                st.rerun()

    with tab2:
        st.info("Ask specific questions to generate targeted visual insights based on your data requirements.")

        if "custom_insights_generated" not in st.session_state:
            st.session_state.custom_insights_generated = False
            st.session_state.custom_insights_figures = []
            st.session_state.custom_insights_text = None

        custom_prompt = st.text_area(
            "Enter your question:",
            key="custom_prompt_text_area",
            height=100,
            placeholder="Example: Show me sales trends by customer over time",
        )

        if st.button("Generate Insights", key="gen_custom_insights_btn"):
            if not api_key:
                st.error("API key not configured. Please add GEMINI_API_KEY to your .env file.")
            elif not custom_prompt:
                st.warning("Please enter a question.")
            else:
                with st.spinner("Analyzing data and generating visualizations..."):
                    try:
                        figures, insights_text = supervisor.handle_query(
                            data_for_insights, query=custom_prompt, api_key=api_key
                        )
                        error = None if figures or insights_text else "Agent returned no results."
                        if isinstance(insights_text, str) and insights_text.startswith("Error"):
                            error = insights_text

                        if error:
                            st.error(f"Error generating insights: {error}")
                            st.session_state.custom_insights_generated = False
                        else:
                            st.session_state.custom_insights_figures = figures
                            st.session_state.custom_insights_text = insights_text
                            st.session_state.custom_insights_generated = True

                    except Exception as e:
                        st.error(f"Error generating insights: {str(e)}")
                        st.session_state.custom_insights_generated = False

        if st.session_state.custom_insights_generated:
            if st.session_state.custom_insights_figures:
                st.markdown("### Visual Insights")
                for idx, fig in enumerate(st.session_state.custom_insights_figures):
                    st.plotly_chart(fig, width="stretch", key=f"custom_insight_chart_{idx}")

            if st.session_state.custom_insights_text:
                with st.expander("View Analysis Summary", expanded=False):
                    st.markdown(st.session_state.custom_insights_text)

            if st.button("Clear Results", key="clear_custom_insights"):
                st.session_state.custom_insights_generated = False
                st.session_state.custom_insights_figures = []
                st.session_state.custom_insights_text = None
                st.rerun()
