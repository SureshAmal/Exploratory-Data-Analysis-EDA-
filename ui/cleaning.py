import pandas as pd
import streamlit as st
from eda import (
    detect_outliers_iqr,
    detect_outliers_zscore,
    apply_cleaning,
    outlier_summary,
)


def render_cleaning(df):
    """Render the Cleaning tab: outlier detection, action builder, preview/apply."""
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## Outlier Detection")

    factor = 1.5
    thresh = 3.0
    method = st.radio("Method", ["iqr", "zscore"])
    if method == "iqr":
        factor = st.slider("IQR factor", 1.0, 3.0, 1.5)
        summary = outlier_summary(df, method="iqr", factor=factor)
    else:
        thresh = st.slider("Z-score threshold", 2.0, 5.0, 3.0)
        summary = outlier_summary(df, method="zscore", threshold=thresh)

    st.dataframe(summary, width="stretch")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## Data Cleaning & Transformation")

    if "auto_drop_mask" not in st.session_state:
        st.session_state["auto_drop_mask"] = None

    select_all = st.checkbox("Select all columns for cleaning", value=False)
    cols_default = df.columns.tolist() if select_all else None
    cols_for_clean = st.multiselect(
        "Select columns to create cleaning actions for",
        df.columns.tolist(),
        default=cols_default,
    )

    with st.expander(
        "Quick outlier removal (auto-create drop actions)", expanded=False
    ):
        st.write("Create a global drop mask based on outliers in the selected columns.")
        col_mode = st.radio(
            "Drop mode",
            ["Any selected column (union)", "All selected columns (intersection)"],
            index=0,
        )
        if st.button("Create drop-outlier mask for selected columns"):
            if not cols_for_clean:
                st.warning("Select at least one column first.")
            else:
                mask_any = pd.Series(False, index=df.index)
                mask_all = pd.Series(True, index=df.index)
                for c in cols_for_clean:
                    if method == "iqr":
                        m = detect_outliers_iqr(df[c], factor=factor)
                    else:
                        m = detect_outliers_zscore(df[c], threshold=thresh)
                    mask_any = mask_any | m
                    mask_all = mask_all & m
                mask_to_use = mask_any if col_mode.startswith("Any") else mask_all
                st.session_state["auto_drop_mask"] = mask_to_use
                st.success(
                    f"Auto drop mask created: {int(mask_to_use.sum())} rows flagged"
                )

    actions = {}
    for c in cols_for_clean:
        with st.expander(f"Action for `{c}`", expanded=False):
            chosen = st.multiselect(
                f"Select method(s) for {c}",
                ["drop_outliers", "cap", "impute"],
                key=f"methods_{c}",
            )
            if not chosen:
                continue
            col_actions = []
            if "drop_outliers" in chosen:
                if method == "iqr":
                    mask = detect_outliers_iqr(df[c], factor=factor)
                else:
                    mask = detect_outliers_zscore(df[c], threshold=thresh)
                col_actions.append({"method": "drop", "mask": mask})
                st.write(f"Rows flagged in `{c}`: {int(mask.sum())}")
            if "cap" in chosen:
                lower = st.number_input(
                    f"Lower cap for {c} (leave empty for none)",
                    value=float("nan"),
                    key=f"lower_{c}",
                )
                upper = st.number_input(
                    f"Upper cap for {c} (leave empty for none)",
                    value=float("nan"),
                    key=f"upper_{c}",
                )
                lval = None if pd.isna(lower) else float(lower)
                uval = None if pd.isna(upper) else float(upper)
                col_actions.append({"method": "cap", "lower": lval, "upper": uval})
            if "impute" in chosen:
                strategy = st.selectbox(
                    f"Impute strategy for {c}",
                    ["median", "mean", "mode"],
                    key=f"impute_{c}",
                )
                col_actions.append({"method": "impute", "impute": strategy})

            if col_actions:
                actions[c] = col_actions

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "Tip: use the quick outlier removal to auto-flag rows, then optionally add caps or imputations per column."
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Preview cleaned dataset", key="preview_btn"):
            cleaned = df.copy()
            adm = st.session_state.get("auto_drop_mask")
            if adm is not None:
                cleaned = cleaned.loc[~adm].reset_index(drop=True)

            if actions:
                cleaned = apply_cleaning(cleaned, actions)

            st.session_state["cleaned_df"] = cleaned

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Cleaned preview")
            st.dataframe(cleaned.head(100), width="stretch", height=400)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Comparison (Before / After)")
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("Original Rows", f"{df.shape[0]:,}")
            with metric_col2:
                st.metric(
                    "Cleaned Rows",
                    f"{cleaned.shape[0]:,}",
                    delta=f"{-(df.shape[0] - cleaned.shape[0])}",
                )

            with st.expander("View missing values before", expanded=False):
                st.dataframe(df.isna().sum().to_frame("Missing Count"), width="stretch")

            with st.expander("View missing values after", expanded=False):
                st.dataframe(
                    cleaned.isna().sum().to_frame("Missing Count"), width="stretch"
                )

            csv = cleaned.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download cleaned CSV",
                data=csv,
                file_name="cleaned.csv",
                width="stretch",
            )

    if not actions and st.session_state.get("auto_drop_mask") is None:
        st.info(
            "No cleaning actions selected. Use the UI above to create actions or auto-generate an outlier drop mask."
        )
