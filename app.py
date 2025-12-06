import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from agents import SupervisorAgent
from eda import read_dataset
from memory import SessionMemory

# Modular UI components
from ui.css import inject_modular_css
from ui.header import render_header
from ui.sidebar import render_sidebar

load_dotenv()

# Clear any client-side theme overrides stored in browser localStorage.
# Some Streamlit theme editor settings are persisted client-side and can
# override server config with empty strings, causing front-end "Invalid color"
# warnings. This script removes localStorage keys that mention "theme" and
# reloads the page once so the server-provided config applies.
# components.html(
#     """
#         <script>
#         (function(){
#             try {
#                 const keys = Object.keys(localStorage || {});
#                 const themeKeys = keys.filter(k => /theme/i.test(k) || k.includes('streamlit'));
#                 if (themeKeys.length) {
#                     themeKeys.forEach(k => localStorage.removeItem(k));
#                     // reload once to apply server config
#                     window.location.reload();
#                 }
#             } catch(e) { console.error('theme-clear', e); }
#         })();
#         </script>
#         """,
#     height=0,
# )

st.set_page_config(
    page_title="Data Alchemy Lab",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# inject CSS and render header + sidebar
inject_modular_css()
render_header()

# Sidebar returns `uploaded` file-like and any `loaded_from_history`
uploaded, loaded_from_history = render_sidebar()

# Initialize file history in session state
if "file_history" not in st.session_state:
    st.session_state["file_history"] = []

# Initialize Agent System
if "agent_memory" not in st.session_state:
    st.session_state["agent_memory"] = SessionMemory()
if "supervisor" not in st.session_state:
    st.session_state["supervisor"] = SupervisorAgent(st.session_state["agent_memory"])


# NOTE: I don't Think this is necessary.
# # Agent Activity Feed
# st.sidebar.markdown("---")
# st.sidebar.markdown("### Agent Activity")
# with st.sidebar.expander("View Agent Logs", expanded=True):
#     if "agent_memory" in st.session_state:
#         history = st.session_state["agent_memory"].get_recent_history(10)
#         if not history:
#             st.caption("No activity yet.")
#         else:
#             for action in reversed(history):
#                 prefix = "Thinking:" if action.action_type == "thought" else "Action:"
#                 st.markdown(f"**{prefix} {action.agent_name}:** {action.content}")
#                 st.markdown("---")

# File history and upload UI handled by `ui.sidebar.render_sidebar()`

if uploaded is not None or loaded_from_history is not None:
    df = read_dataset(uploaded) if uploaded is not None else loaded_from_history
    # initialize sales variables to satisfy static analyzers
    df_sales = None
    sales_tab = None
    # Reset session state related to previous dataset insights/cleaning
    st.session_state["cleaned_df"] = None
    st.session_state["auto_drop_mask"] = None
    st.session_state["auto_insights_generated"] = False
    st.session_state["custom_insights_generated"] = False
    st.session_state["custom_insights_figures"] = []
    st.session_state["custom_insights_text"] = None

    # Agent: Process new upload
    with st.spinner("Supervisor Agent is analyzing the dataset..."):
        df = st.session_state["supervisor"].process_upload(df)

    # Save to file history
    from datetime import datetime

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_info = {
        "name": uploaded.name if uploaded is not None else "Loaded from history",
        "timestamp": current_time,
        "rows": df.shape[0],
        "columns": df.shape[1],
        "id": f"{current_time}-{df.shape[0]}-{df.shape[1]}",
        "data_bytes": (uploaded.getvalue() if uploaded is not None else None),
    }

    # Check if this file is already in history (by name and avoid duplicates)
    if not any(
        h["name"] == file_info["name"]
        and h["timestamp"].split()[0] == current_time.split()[0]
        for h in st.session_state["file_history"]
    ):
        st.session_state["file_history"].insert(0, file_info)
        # Keep only last 10 files in history
        if len(st.session_state["file_history"]) > 10:
            st.session_state["file_history"] = st.session_state["file_history"][:10]

    # Detect sales dataset early and prepare derived table if present
    is_sales_data = False
    sales_columns = {"Date", "Customer", "Total_Amount"}
    if sales_columns.issubset(set(df.columns)):
        is_sales_data = True
        df_sales = df.copy()
        try:
            df_sales["Date"] = pd.to_datetime(df_sales["Date"])
        except Exception:
            # keep original if conversion fails
            pass
        df_sales["Month_Year"] = df_sales["Date"].dt.to_period("M").astype(str)
        df_sales["Year"] = df_sales["Date"].dt.year
    # Top-level tabs to reduce long scrolling — always create Sales tab so static analyzers
    # see a consistently defined variable. Content will be conditional.
    overview_tab, profile_tab, visuals_tab, cleaning_tab, insights_tab, sales_tab = (
        st.tabs(["Overview", "Profile", "Visuals", "Cleaning", "AI Insights", "Sales"])
    )

    # Overview: Data preview
    from ui.overview import render_overview

    with overview_tab:
        render_overview(df)

    from ui.profile import render_profile

    with profile_tab:
        render_profile(df)

    # Sales tab: render via ui.sales module
    from ui.sales import render_sales

    # Render sales tab content (render_sales handles the case when df_sales is None)
    render_sales(df_sales, parent=sales_tab)

    from ui.visuals import render_visuals

    with visuals_tab:
        render_visuals(df)

    from ui.cleaning import render_cleaning

    with cleaning_tab:
        render_cleaning(df)

    from ui.insights import render_insights

    # select dataset for insights
    if "cleaned_df" in st.session_state and st.session_state["cleaned_df"] is not None:
        data_for_insights = st.session_state["cleaned_df"]
    else:
        data_for_insights = df

    with insights_tab:
        render_insights(data_for_insights, st.session_state["supervisor"])

else:
    # Welcome screen - clean and simple
    # Theme diagnostics: show effective theme keys to help debug empty-color warnings
    # try:
    #     with st.sidebar.expander("Theme diagnostics", expanded=False):
    #         try:
    #             theme = st.get_option("theme")
    #         except Exception:
    #             theme = None
    #         st.write("Effective theme (st.get_option('theme')):")
    #         st.write(theme)
    # except Exception:
    #     # Guard: if Streamlit version doesn't support get_option, skip diagnostics
    #     pass

    st.markdown(
        '<div style="font-size: var(--fs-xl); font-family: var(--font-serif); font-weight: 600; margin-top: var(--space-6); margin-bottom: var(--space-3);">Welcome to Data Analysis Platform</div><hr>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(
            '<div style="font-size: var(--fs-lg); font-family: var(--font-serif); font-weight: 600; margin-top: var(--space-5); margin-bottom: var(--space-2);">Getting Started</div>',
            unsafe_allow_html=True,
        )
        st.markdown("""
        1. Upload your CSV or Excel file using the sidebar
        2. Review the data profile and statistics
        3. Explore visualizations and correlations
        4. Detect and handle outliers
        5. Clean and transform your data
        6. Download the cleaned dataset
        """)

    with col2:
        st.markdown(
            '<div style="font-size: var(--fs-lg); font-family: var(--font-serif); font-weight: 600; margin-top: var(--space-5); margin-bottom: var(--space-2);">Platform Capabilities</div>',
            unsafe_allow_html=True,
        )
        st.markdown("""
        **Data Analysis**
        - Statistical profiling
        - Distribution analysis
        - Correlation matrices

        **Data Quality**
        - Outlier detection (IQR, Z-score)
        - Missing value handling
        - Data cleaning tools

        **Specialized Features**
        - Sales analytics dashboard
        - AI-powered insights
        - Export cleaned data
        """)
