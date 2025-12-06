from typing import Any

import pandas as pd
import streamlit as st

from .actions import render_cleaning_actions
from .outliers import render_outlier_detection
from .preview_apply import render_preview_apply

__all__ = [
    "render_outlier_detection",
    "render_cleaning_actions",
    "render_preview_apply",
    "render_cleaning",
]


def render_clean(df: pd.DataFrame) -> None:
    st.markdown("## Data Cleaning & Transformation")
    st.markdown(
        "Detect and handle outliers, missing values, and transform your data with confidence."
    )

    tab1, tab2, tab3 = st.tabs(
        ["Outlier Detection", "Cleaning Actions", "Preview & Apply"]
    )

    with tab1:
        # Delegate to outlier detection component
        render_outlier_detection(df)

    with tab2:
        # Delegate to cleaning actions component
        render_cleaning_actions(df)

    with tab3:
        # Delegate to preview/apply component
        render_preview_apply(df)
