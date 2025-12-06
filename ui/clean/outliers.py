import pandas as pd
import streamlit as st

from eda import outlier_summary


def render_outlier_detection(df: pd.DataFrame) -> None:
    """Render the Outlier Detection configuration and summary.

    This component corresponds to the original Cleaning tab's Outlier Detection
    section. It sets up session state defaults for detection method parameters,
    exposes UI controls to the user, and renders a summary dataframe showing
    outlier counts/percentages per numeric column.
    """
    st.markdown("### Outlier Detection Configuration")

    # Session state defaults (persist between tabs/reruns)
    if "detection_method" not in st.session_state:
        st.session_state["detection_method"] = "iqr"
    if "iqr_factor" not in st.session_state:
        st.session_state["iqr_factor"] = 1.5
    if "zscore_threshold" not in st.session_state:
        st.session_state["zscore_threshold"] = 3.0

    col1, col2 = st.columns([1, 2])

    with col1:
        st.session_state["detection_method"] = st.selectbox(
            "Detection Method",
            ["iqr", "zscore"],
            key="detection_method_select",
            format_func=lambda x: "IQR (Interquartile Range)"
            if x == "iqr"
            else "Z-Score",
            help=(
                "Choose the statistical algorithm used to identify outliers. "
                "IQR is better for skewed data; Z-Score is better for normal "
                "distributions."
            ),
        )

        if st.session_state["detection_method"] == "iqr":
            st.session_state["iqr_factor"] = st.slider(
                "IQR Factor (k)",
                1.0,
                3.0,
                st.session_state["iqr_factor"],
                0.1,
                key="iqr_factor_slider",
                help=(
                    "Determines the sensitivity. A lower value (e.g., 1.0) "
                    "detects more outliers; a higher value (e.g., 3.0) detects "
                    "only extreme outliers. Standard is 1.5."
                ),
            )
            summary = outlier_summary(
                df, method="iqr", factor=st.session_state["iqr_factor"]
            )
        else:
            st.session_state["zscore_threshold"] = st.slider(
                "Z-Score Threshold",
                2.0,
                5.0,
                st.session_state["zscore_threshold"],
                0.1,
                key="zscore_threshold_slider",
                help=(
                    "Determines how many standard deviations from the mean a "
                    "point must be to be considered an outlier. Standard is 3.0."
                ),
            )
            summary = outlier_summary(
                df, method="zscore", threshold=st.session_state["zscore_threshold"]
            )

    with col2:
        st.markdown("#### Outlier Summary by Column")
        # If summary is empty or not a DataFrame, handle gracefully
        if isinstance(summary, pd.DataFrame) and not summary.empty:
            st.dataframe(summary, width="stretch")
        else:
            # Create a helpful empty message / placeholder
            st.write(
                "No numeric columns detected or no outliers found with current settings."
            )
        st.info(
            "This table shows the count and percentage of outliers detected in each numeric column based on the settings on the left."
        )
