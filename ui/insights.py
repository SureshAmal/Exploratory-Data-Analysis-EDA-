import os
import streamlit as st
# Assuming the BRAND_TEMPLATE usage is for styling figures, kept as is.
# from plotly_theme import BRAND_TEMPLATE


def render_insights(data_for_insights, supervisor):
    """Render the AI Insights tab. Expects a supervisor agent instance to handle queries."""

    # --- UI Setup ---
    st.markdown("## AI-Powered Insights")
    st.markdown(
        "We distill statistical texture, temporal shifts, cohort behaviors and emergent anomalies into a concise narrative. **Generate automatic synthesis or interrogate with custom prompts.**",
    )

    api_key = os.getenv("GEMINI_API_KEY")

    # --- Status Placeholders ---
    status_placeholder = st.empty()

    tab1, tab2 = st.tabs(["Automatic Analysis", "Custom Query"])

    # --- Core Logic to Handle Agent Call (Refactored) ---
    def generate_results(query, state_key_prefix, is_auto=False):
        """Reusable function to call the agent and update session state."""
        status_placeholder.empty()  # Clear previous status messages

        if not api_key:
            status_placeholder.error(
                "API key not configured. Please add **GEMINI_API_KEY** to your .env file."
            )
            st.session_state[f"{state_key_prefix}_generated"] = False
            return

        if not is_auto and not query:
            status_placeholder.warning(
                "Please enter a question before generating insights."
            )
            return

        with st.spinner(
            f"Analyzing data and generating visualizations for: '{query[:40]}...'"
        ):
            try:
                # Call the supervisor agent
                figures, insights_text = supervisor.handle_query(
                    data_for_insights,
                    query=query,
                    api_key=api_key,
                )

                # Basic error checks
                error = None
                if isinstance(insights_text, str) and insights_text.lower().startswith(
                    "error"
                ):
                    error = insights_text
                elif not figures and not insights_text:
                    error = "Agent returned no results."

                if error:
                    status_placeholder.error(f"Error generating insights: {error}")
                    st.session_state[f"{state_key_prefix}_generated"] = False
                else:
                    st.session_state[f"{state_key_prefix}_figures"] = figures
                    st.session_state[f"{state_key_prefix}_text"] = insights_text
                    st.session_state[f"{state_key_prefix}_generated"] = True
                    status_placeholder.success("Insights generated successfully!")

            except Exception as e:
                status_placeholder.error(f"An unexpected error occurred: {str(e)}")
                st.session_state[f"{state_key_prefix}_generated"] = False

    # --- Logic to Display Results (Refactored for 2 Columns) ---
    def display_results(state_key_prefix):
        """Renders the figures and text summary from the session state."""

        figures = st.session_state.get(f"{state_key_prefix}_figures", [])
        text = st.session_state.get(f"{state_key_prefix}_text")

        # 1. Display Text Summary
        if text:
            st.markdown("### Analysis Summary")
            st.markdown(text)
            st.markdown("---")  # Separator

        # 2. Display Figures in Two Columns
        if figures:
            st.markdown("### Visual Insights")

            # Create two columns once
            col_left, col_right = st.columns(2)

            for idx, fig in enumerate(figures):
                # Alternate placing figures into the two columns
                if idx % 2 == 0:
                    with col_left:
                        st.plotly_chart(
                            fig,
                            use_container_width=True,
                            key=f"{state_key_prefix}_chart_{idx}",
                        )
                else:
                    with col_right:
                        st.plotly_chart(
                            fig,
                            use_container_width=True,
                            key=f"{state_key_prefix}_chart_{idx}",
                        )

        # 3. Clear Button
        if figures or text:
            st.markdown("---")
            if st.button("Clear Results", key=f"clear_{state_key_prefix}_btn"):
                st.session_state[f"{state_key_prefix}_generated"] = False
                st.session_state[f"{state_key_prefix}_figures"] = []
                st.session_state[f"{state_key_prefix}_text"] = None
                st.rerun()

    # ============================================================================
    # TAB 1: AUTOMATIC ANALYSIS
    # ============================================================================
    with tab1:
        # Initialize state for this tab
        if "auto_insights_generated" not in st.session_state:
            st.session_state.auto_insights_generated = False
            st.session_state.auto_insights_figures = []
            st.session_state.auto_insights_text = None

        # st.info removed, text moved to button help

        # Generator Button (Help argument provides the informational tooltip)
        if st.button(
            "Generate Auto-Analysis",
            key="gen_auto_insights_btn",
            type="primary",
            help="Click to generate a comprehensive, AI-driven analysis, including key findings, trends, and anomalies from your entire dataset.",
        ):
            generate_results(
                query="Analyze this dataset and provide key findings, trends, and anomalies.",
                state_key_prefix="auto_insights",
                is_auto=True,
            )

        # Display results if generated
        if st.session_state.auto_insights_generated:
            st.markdown("---")
            display_results("auto_insights")

    # ============================================================================
    # TAB 2: CUSTOM QUERY
    # ============================================================================
    with tab2:
        # Initialize state for this tab
        if "custom_insights_generated" not in st.session_state:
            st.session_state.custom_insights_generated = False
            st.session_state.custom_insights_figures = []
            st.session_state.custom_insights_text = None

        # st.info is REMOVED here.

        # Input for custom prompt (Help argument provides the informational tooltip)
        custom_prompt = st.text_area(
            "Enter your question:",
            key="custom_prompt_text_area",
            height=100,
            placeholder="Example: Show me sales trends over time, segmented by customer type.",
            help="Ask specific questions or request custom visualizations (e.g., 'Show me sales by region with a bar chart').",
        )

        # UX Improvement: Clear old results when the user starts typing a new query
        if custom_prompt != st.session_state.get("last_custom_prompt", ""):
            if st.session_state.custom_insights_generated:
                st.session_state.custom_insights_generated = False
                st.session_state.custom_insights_figures = []
                st.session_state.custom_insights_text = None

        # Store the current prompt to check against next run
        st.session_state["last_custom_prompt"] = custom_prompt

        # Generator Button
        if st.button("Ask AI", key="gen_custom_insights_btn", type="primary"):
            generate_results(
                query=custom_prompt,
                state_key_prefix="custom_insights",
            )

        # Display results if generated
        if st.session_state.custom_insights_generated:
            st.markdown("---")
            display_results("custom_insights")
