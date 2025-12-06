import io
import streamlit as st
from eda import read_dataset


def _render_journey(uploaded_flag: bool):
    steps = [
        ("Upload Dataset", uploaded_flag),
        ("Profile & Explore", uploaded_flag),
        ("Clean & Transform", "cleaned_df" in st.session_state),
        (
            "AI Insights",
            st.session_state.get("auto_insights_generated")
            or st.session_state.get("custom_insights_generated"),
        ),
    ]
    blocks = []
    for label, done in steps:
        cls = "sidebar-journey-step active" if done else "sidebar-journey-step"
        blocks.append(f"<div class='{cls}'>{label}</div>")
    st.sidebar.markdown("### Data Journey")
    st.sidebar.markdown(
        "<div class='journey-block'>" + "".join(blocks) + "</div>",
        unsafe_allow_html=True,
    )


def render_sidebar():
    """Render uploader, journey and file-history sidebar. Returns (uploaded, loaded_from_history).
    """
    st.sidebar.markdown("### Upload Dataset")
    uploaded = st.sidebar.file_uploader(
        "Choose a file", type=["csv", "xls", "xlsx"], label_visibility="collapsed"
    )
    st.sidebar.caption("Supported formats: CSV, Excel (XLS, XLSX)")

    _render_journey(
        uploaded is not None or st.session_state.get("history_to_load") is not None
    )
    

    # NOTE: Agent activity feed is disabled for now.
    # Agent Activity Feed
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

    # File History Section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### File History")
    if st.session_state.get("file_history"):
        selected_history = st.sidebar.selectbox(
            "View past files:",
            ["Current File"]
            + [f"{h['name']} ({h['timestamp']})" for h in st.session_state.get("file_history", [])],
            key="history_selector",
        )

        if selected_history != "Current File":
            # Find the selected file in history
            for h in st.session_state.get("file_history", []):
                if f"{h['name']} ({h['timestamp']})" == selected_history:
                    st.sidebar.markdown(
                        f'<div style="background-color: rgba(38, 102, 127, 0.4); padding: 1rem; border-radius: 8px; margin: 0.5rem 0;"><p style="color: #ffffff; margin: 0.3rem 0; font-weight: 500;"><strong>Filename:</strong> {h["name"]}</p><p style="color: #ffffff; margin: 0.3rem 0; font-weight: 500;"><strong>Uploaded:</strong> {h["timestamp"]}</p><p style="color: #ffffff; margin: 0.3rem 0; font-weight: 500;"><strong>Rows:</strong> {h["rows"]}</p><p style="color: #ffffff; margin: 0.3rem 0; font-weight: 500;"><strong>Columns:</strong> {h["columns"]}</p></div>',
                        unsafe_allow_html=True,
                    )
                    if st.sidebar.button(
                        "Load This File Data", key=f"load_history_{h['timestamp']}"
                    ):
                        st.session_state["history_to_load"] = h.get("id") or h["timestamp"]
                        st.rerun()
                    break
    else:
        st.sidebar.info("No file history yet")

    loaded_from_history = None
    if (
        st.session_state.get("history_to_load") is not None
        and st.session_state.get("file_history")
    ):
        target_id = st.session_state["history_to_load"]
        for h in st.session_state.get("file_history", []):
            if (h.get("id") or h.get("timestamp")) == target_id:
                try:
                    data_bytes = h.get("data_bytes")
                    if data_bytes is not None:
                        buffer = io.BytesIO(data_bytes)
                        loaded_from_history = read_dataset(buffer)
                except Exception as e:
                    st.error(f"Failed to load historical file: {e}")
                finally:
                    st.session_state["history_to_load"] = None
                break

    return uploaded, loaded_from_history
