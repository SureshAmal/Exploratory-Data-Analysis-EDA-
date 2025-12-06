from typing import Optional

import pandas as pd
import streamlit as st

from eda import apply_cleaning


def _safe_int(value: Optional[int]) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def render_preview_apply(df: pd.DataFrame) -> None:
    """
    Render the Preview & Apply tab UI.

    Parameters:
    - df: Original DataFrame to base previews on.

    Behavior:
    - Reads cleaning configuration from `st.session_state["individual_actions"]` and
      `st.session_state["auto_drop_mask"]`.
    - When the user clicks "Generate Preview", runs the cleaning on a copy and stores
      the result in `st.session_state["cleaned_df"]`.
    - Shows impact metrics, preview table, comparisons, and download button.
    - Provides an "Apply Changes" button which writes `st.session_state["applied_cleaned_df"]`
      for downstream use (or you can choose to overwrite the input reference).
    """
    st.markdown("### Preview and Apply Changes")
    st.markdown("See the impact of your cleaning actions before committing.")

    # Ensure session state keys exist to avoid KeyErrors
    if "individual_actions" not in st.session_state:
        st.session_state["individual_actions"] = {}
    if "auto_drop_mask" not in st.session_state:
        st.session_state["auto_drop_mask"] = None

    preview_col1, preview_col2 = st.columns([1, 3])

    with preview_col1:
        preview_button = st.button(
            "Generate Preview",
            type="primary",
            width="stretch",
            key="preview_button",
            help="Run the configured cleaning steps on a copy of your data and generate the report below.",
        )

    # If a preview already exists in session, show quick access buttons
    if "cleaned_df" in st.session_state and not preview_button:
        st.info("A cleaning preview is available from your last run.")
        if st.button("Show Latest Preview", key="show_latest_preview"):
            preview_button = True

    if preview_button:
        active_actions = st.session_state.get("individual_actions", {})
        adm = st.session_state.get("auto_drop_mask")

        if (not active_actions) and (adm is None):
            st.warning(
                "No cleaning actions configured. Please configure actions in the 'Cleaning Actions' tab."
            )
            return

        # Run cleaning on a copy and capture timing feedback
        with st.spinner("Processing data..."):
            cleaned = df.copy()

            # Apply auto drop mask (if present) - remove flagged rows
            if adm is not None:
                try:
                    # Ensure mask aligns with dataframe index and is boolean
                    mask = pd.Series(adm, index=df.index).astype(bool)
                    cleaned = cleaned.loc[~mask].reset_index(drop=True)
                except Exception:
                    # Fallback: ignore mask if misaligned
                    st.error(
                        "Batch drop mask could not be applied due to alignment issues."
                    )
                    cleaned = df.copy()

            # Apply per-column actions via eda.apply_cleaning
            try:
                if active_actions:
                    cleaned = apply_cleaning(cleaned, active_actions)
            except Exception as exc:
                st.error(f"An error occurred while applying column actions: {exc}")
                # Save partial result if available
                st.session_state["cleaned_df"] = cleaned
                return

            # Persist preview
            st.session_state["cleaned_df"] = cleaned

            st.success("Cleaning preview generated successfully!")

        # Display Impact Metrics
        st.markdown("---")
        st.markdown("### Impact Analysis")

        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

        original_rows = df.shape[0]
        cleaned_rows = st.session_state["cleaned_df"].shape[0]
        rows_removed = original_rows - cleaned_rows
        pct_removed = (rows_removed / original_rows) * 100 if original_rows > 0 else 0.0

        metric_col1.metric(
            "Original Rows",
            f"{original_rows:,}",
            help="Total number of rows in the uploaded dataset.",
        )
        metric_col2.metric(
            "Cleaned Rows",
            f"{cleaned_rows:,}",
            delta=f"-{rows_removed:,}",
            delta_color="inverse",
            help="Number of rows remaining after cleaning operations.",
        )
        metric_col3.metric(
            "Rows Removed %",
            f"{pct_removed:.2f}%",
            delta=f"{rows_removed:,} total",
            delta_color="inverse",
            help="Percentage of the original dataset that was removed.",
        )

        missing_before = df.isna().sum().sum()
        missing_after = st.session_state["cleaned_df"].isna().sum().sum()
        delta_missing = missing_before - missing_after
        delta_color = "normal" if delta_missing > 0 else "inverse"

        metric_col4.metric(
            "Missing Values (Remaining)",
            f"{missing_after:,}",
            delta=f"-{_safe_int(delta_missing):,}",
            delta_color=delta_color,
            help="Total count of NaN (empty) cells remaining in the dataset. A positive delta means values were filled.",
        )

        st.markdown("---")

        # Data Preview (limit rows for performance)
        st.markdown("### Cleaned Data Preview")
        try:
            st.dataframe(
                st.session_state["cleaned_df"].head(100),
                width="stretch",
                height=400,
            )
        except Exception:
            st.write("Preview unavailable due to rendering constraints.")

        st.markdown("---")

        # Detailed Missing Value Comparison
        st.markdown("### Detailed Missing Value Comparison")
        missing_before_series = df.isna().sum().rename("Missing Before")
        missing_after_series = (
            st.session_state["cleaned_df"].isna().sum().rename("Missing After")
        )

        comparison_df = (
            pd.concat([missing_before_series, missing_after_series], axis=1)
            .fillna(0)
            .astype(int)
        )
        comparison_df["Change"] = (
            comparison_df["Missing After"] - comparison_df["Missing Before"]
        )

        # Compute % change relative to original missing count where applicable
        def pct_change(row):
            before = row["Missing Before"]
            ch = row["Change"]
            if before == 0:
                return 0.0
            return round((ch / before) * 100, 1)

        comparison_df["% Change (Original)"] = comparison_df.apply(pct_change, axis=1)

        # Show only columns that had missing values originally or after
        filtered = comparison_df[
            (comparison_df["Missing Before"] > 0) | (comparison_df["Missing After"] > 0)
        ]
        if not filtered.empty:
            st.dataframe(filtered, width="stretch")
        else:
            st.info(
                "No missing values were present in the dataset before or after cleaning."
            )

        st.markdown("---")

        # Download / Apply Section
        st.markdown("### Export & Apply Cleaned Data")
        download_col1, download_col2 = st.columns([1, 1])

        with download_col1:
            try:
                csv = st.session_state["cleaned_df"].to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download CSV",
                    data=csv,
                    file_name="cleaned_data.csv",
                    mime="text/csv",
                    width="stretch",
                    key="download_cleaned_csv",
                    help="Download the cleaned dataset as a CSV file.",
                )
            except Exception:
                st.error("Unable to prepare CSV for download.")

        with download_col2:
            # Apply changes button writes to session_state so other parts of the app can pick it up.
            if st.button(
                "Apply Changes (Persist Cleaned Data)",
                type="secondary",
                key="apply_changes_btn",
                help="Persist the cleaned dataset to session state for downstream use.",
            ):
                st.session_state["applied_cleaned_df"] = st.session_state[
                    "cleaned_df"
                ].copy()
                st.success(
                    "Cleaned dataset applied and available as `st.session_state['applied_cleaned_df']`."
                )

    # When there is no preview generated yet, show guidance
    if "cleaned_df" not in st.session_state:
        st.info(
            """
            Get Started:
            1. Configure outlier detection parameters in the first tab.
            2. Define your cleaning actions (Row Drop, Capping, Imputation) in the Cleaning Actions tab.
            3. Click 'Generate Preview' to process the data and analyze the results.
            """
        )
