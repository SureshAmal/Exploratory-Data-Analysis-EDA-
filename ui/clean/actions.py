"""
UI component for Cleaning Actions (Tab 2).

This module provides `render_cleaning_actions(df)` which implements:
- Step 1: Column selection (multiselect + toggle select all/none)
- Step 2: Optional batch outlier-row removal (generate/clear batch drop mask)
- Step 3: Per-column action configuration (drop_outliers, cap, impute)
- Global summary of configured actions and batch mask.

This is a direct, self-contained refactor of the "Cleaning Actions" portion of the
original `ui/cleaning.py` file so it can be used as a component from a split UI.
"""

from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from eda import detect_outliers_iqr, detect_outliers_zscore


def _parse_optional_float(text_val: str) -> Optional[float]:
    """Helper: parse a text input into float or return None for empty strings."""
    if text_val is None:
        return None
    text_val = str(text_val).strip()
    if text_val == "":
        return None
    try:
        return float(text_val)
    except Exception:
        return None


def render_cleaning_actions(df: pd.DataFrame) -> None:
    """
    Render the Cleaning Actions UI.

    This exposes three logical steps:
    1) Select columns to configure
    2) Optionally create a batch drop-mask based on outliers across selected columns
    3) Configure per-column transformations (drop outliers, cap, impute)

    It writes per-column configurations to `st.session_state["individual_actions"]`
    and stores a batch drop mask in `st.session_state["auto_drop_mask"]`.
    """
    st.markdown("### Configure Cleaning Actions")

    # Initialize session state containers used across tabs/components
    if "auto_drop_mask" not in st.session_state:
        st.session_state["auto_drop_mask"] = None
    if "individual_actions" not in st.session_state:
        st.session_state["individual_actions"] = {}
    if "cols_for_clean" not in st.session_state:
        st.session_state["cols_for_clean"] = []

    # --- Step 1: Column Selection ---
    st.markdown("#### Step 1: Select Columns")
    col1, col2 = st.columns([3, 1])
    all_cols = df.columns.tolist()

    with col1:
        if st.button(
            "Toggle Select All/None",
            width="content",
            key="toggle_select",
            help="Click to instantly select or deselect all columns in the list below.",
        ):
            if len(st.session_state.get("cols_for_clean", [])) == len(all_cols):
                st.session_state["cols_for_clean"] = []
            else:
                st.session_state["cols_for_clean"] = all_cols

        cols_for_clean = st.multiselect(
            "Choose columns to clean",
            all_cols,
            default=st.session_state.get("cols_for_clean", []),
            key="cols_for_clean",
            help=(
                "Select the specific columns you wish to apply transformations to "
                "(e.g., removing outliers, filling missing values)."
            ),
        )

    with col2:
        st.metric(
            "Columns Selected",
            len(cols_for_clean) if cols_for_clean else 0,
            help="Total number of columns currently selected for processing.",
        )

    st.markdown("---")

    # --- Step 2: Quick Batch Outlier Removal ---
    st.markdown("#### Step 2: Batch Row Removal (Optional)")

    if cols_for_clean:
        st.markdown(
            "Automatically create a drop mask to remove rows containing outliers in the **selected columns**."
        )

        col_mode = st.radio(
            "Drop rows where outliers are found in:",
            ["Any selected column (Union)", "All selected columns (Intersection)"],
            index=0,
            key="drop_mode",
            help="**Union**: If a row has an outlier in Column A OR Column B, it is removed.\n"
            "**Intersection**: A row is only removed if it has an outlier in Column A AND Column B.",
        )

        if st.button(
            "Generate Batch Drop Mask",
            type="primary",
            width="content",
            help="Calculates outliers based on your Step 1 settings and flags those rows for removal.",
        ):
            mask_any = pd.Series(False, index=df.index)
            mask_all = pd.Series(True, index=df.index)

            current_method = st.session_state.get("detection_method", "iqr")
            factor = st.session_state.get("iqr_factor", 1.5)
            thresh = st.session_state.get("zscore_threshold", 3.0)

            for c in cols_for_clean:
                if pd.api.types.is_numeric_dtype(df[c]):
                    if current_method == "iqr":
                        m = detect_outliers_iqr(pd.Series(df[c]), factor=factor)
                    else:
                        m = detect_outliers_zscore(pd.Series(df[c]), threshold=thresh)
                    # Ensure the mask is aligned to df.index
                    m = pd.Series(m, index=df.index)
                    mask_any = mask_any | m
                    mask_all = mask_all & m

            mask_to_use = mask_any if col_mode.startswith("Any") else mask_all
            st.session_state["auto_drop_mask"] = mask_to_use

            rows_affected = int(mask_to_use.sum())
            pct_affected = (rows_affected / len(df)) * 100 if len(df) > 0 else 0.0

            st.success(
                f"Batch drop mask created: **{rows_affected:,}** rows flagged for removal ({pct_affected:.1f}% of data)"
            )

        if st.session_state.get("auto_drop_mask") is not None:
            if st.button(
                "Clear Batch Drop Mask",
                key="clear_mask_btn",
                help="Undo the batch removal selection.",
            ):
                st.session_state["auto_drop_mask"] = None
                st.info("Batch drop mask cleared.")
    else:
        st.info("Select columns in Step 1 to enable batch removal.")

    st.markdown("---")

    # --- Step 3: Individual Column Actions ---
    st.markdown("#### Step 3: Configure Column Transformations")
    st.markdown(
        "Fine-tune cleaning for each selected column individually. Select a column from the dropdown to edit its settings."
    )

    # Remove configs for columns that are no longer selected
    current_config_keys = list(st.session_state["individual_actions"].keys())
    for k in current_config_keys:
        if k not in cols_for_clean:
            del st.session_state["individual_actions"][k]

    actions: Dict[str, List[Dict[str, Any]]] = st.session_state["individual_actions"]

    if not cols_for_clean:
        st.info("Select columns in Step 1 to configure transformations.")
    else:
        current_method = st.session_state.get("detection_method", "iqr")
        factor = st.session_state.get("iqr_factor", 1.5)
        thresh = st.session_state.get("zscore_threshold", 3.0)

        # Layout: Selection (left) and Editor (right)
        sel_col1, sel_col2 = st.columns([1, 2])

        with sel_col1:
            st.markdown("##### 1. Select Column")

            def fmt_col(col_name: str) -> str:
                return f"✅ {col_name}" if col_name in actions else col_name

            selected_col_edit = st.selectbox(
                "Pick a column to configure:",
                cols_for_clean,
                format_func=fmt_col,
                help="Select a column to view its profile and add cleaning actions (Capping, Imputation).",
            )

            n_configured = len(actions)
            n_total = len(cols_for_clean)
            st.progress(n_configured / n_total if n_total > 0 else 0)
            st.caption(f"Configured: {n_configured} / {n_total} columns")

        with sel_col2:
            c = selected_col_edit
            st.markdown(f"#### 🛠️ Configure: `{c}`")

            # Column meta
            is_numeric = pd.api.types.is_numeric_dtype(df[c])
            available_methods = ["impute"]
            if is_numeric:
                available_methods = ["drop_outliers", "cap", "impute"]

            # Current actions for this column (if any)
            # Use explicit membership check instead of dict.get(...) to satisfy
            # stricter type-checkers that may not infer the correct mapping type.
            current_acts = actions[c] if c in actions else []
            default_methods = [
                a["method"] for a in current_acts if a["method"] in available_methods
            ]

            chosen = st.multiselect(
                "Select Cleaning Methods",
                available_methods,
                default=default_methods,
                key=f"methods_{c}",
                help="Select one or more methods. They are applied in order: Drop Outliers -> Cap Values -> Impute.",
            )

            col_actions: List[Dict[str, Any]] = []

            # If user selected drop_outliers, show flags and attach mask
            if "drop_outliers" in chosen and is_numeric:
                st.markdown("##### 1. Drop Outliers")
                if current_method == "iqr":
                    mask = detect_outliers_iqr(pd.Series(df[c]), factor=factor)
                else:
                    mask = detect_outliers_zscore(pd.Series(df[c]), threshold=thresh)
                mask = pd.Series(mask, index=df.index)
                rows_flagged = int(mask.sum())
                pct_flagged = (rows_flagged / len(df)) * 100 if len(df) > 0 else 0.0

                st.warning(
                    f"Flags **{rows_flagged:,}** rows ({pct_flagged:.1f}%) for removal (based on global settings)."
                )
                col_actions.append({"method": "drop_outliers", "mask": mask})

            # Capping: present optional lower/upper inputs as text (safer for optional values)
            if "cap" in chosen and is_numeric:
                st.markdown("##### 2. Cap Values")
                cap_col1, cap_col2 = st.columns(2)

                # Retrieve existing cap values safely
                prev_cap = next((a for a in current_acts if a["method"] == "cap"), {})

                with cap_col1:
                    lower_text = st.text_input(
                        "Lower Cap Value",
                        value=""
                        if prev_cap.get("lower") is None
                        else str(prev_cap.get("lower")),
                        key=f"lower_{c}",
                        help="Values lower than this will be set to this value. Leave blank for no lower cap.",
                    )

                with cap_col2:
                    upper_text = st.text_input(
                        "Upper Cap Value",
                        value=""
                        if prev_cap.get("upper") is None
                        else str(prev_cap.get("upper")),
                        key=f"upper_{c}",
                        help="Values higher than this will be set to this value. Leave blank for no upper cap.",
                    )

                lval = _parse_optional_float(lower_text)
                uval = _parse_optional_float(upper_text)
                col_actions.append({"method": "cap", "lower": lval, "upper": uval})

            # Imputation
            if "impute" in chosen:
                st.markdown("##### 3. Impute Missing Values")
                imp_col1, imp_col2 = st.columns([2, 1])

                if is_numeric:
                    impute_opts = ["median", "mean", "mode"]
                    default_idx = 0
                else:
                    impute_opts = ["mode"]
                    default_idx = 0

                prev_imp = next(
                    (a for a in current_acts if a["method"] == "impute"), {}
                )
                prev_sel = prev_imp.get("impute", impute_opts[default_idx])

                # Determine index safely
                try:
                    curr_idx = (
                        impute_opts.index(prev_sel)
                        if prev_sel in impute_opts
                        else default_idx
                    )
                except Exception:
                    curr_idx = default_idx

                with imp_col1:
                    strategy = st.selectbox(
                        "Imputation Strategy",
                        impute_opts,
                        index=curr_idx,
                        key=f"impute_{c}",
                        help="**Median**: Good for skewed data.\n**Mean**: Good for normal data.\n**Mode**: Most frequent value.",
                    )

                with imp_col2:
                    n_missing = int(df[c].isna().sum())
                    if n_missing > 0:
                        st.info(f"Fills {n_missing} values")
                    else:
                        st.success("No missing values")

                col_actions.append({"method": "impute", "impute": strategy})

            # Persist configuration for this column
            if col_actions:
                st.session_state["individual_actions"][c] = col_actions
            else:
                # If no actions selected, remove entry if exists
                if c in st.session_state["individual_actions"]:
                    del st.session_state["individual_actions"][c]

    # Summary of actions (Global View)
    st.markdown("---")
    st.markdown("#### Summary of Configured Actions")

    final_actions = st.session_state.get("individual_actions", {})
    summary_items: List[str] = []

    if st.session_state.get("auto_drop_mask") is not None:
        rows_to_drop = int(st.session_state["auto_drop_mask"].sum())
        summary_items.append(f"- **Batch Row Drop**: {rows_to_drop:,} rows flagged")

    if final_actions:
        for col, acts in final_actions.items():
            methods = [a["method"] for a in acts]
            summary_items.append(f"- **{col}**: {', '.join(methods)}")

    if summary_items:
        st.info("\n".join(summary_items))
    else:
        st.info(
            "Tip: Configure column selections and cleaning actions (Steps 1, 2, or 3) to proceed."
        )
