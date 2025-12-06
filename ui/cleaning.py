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

    st.markdown("## Data Cleaning & Transformation")
    st.markdown(
        "Detect and handle outliers, missing values, and transform your data with confidence."
    )

    # Create tabs for better organization
    tab1, tab2, tab3 = st.tabs(
        ["Outlier Detection", "Cleaning Actions", "Preview & Apply"]
    )

    # State initialization
    if "auto_drop_mask" not in st.session_state:
        st.session_state["auto_drop_mask"] = None
    if "individual_actions" not in st.session_state:
        st.session_state["individual_actions"] = {}

    # ============================================================================
    # TAB 1: OUTLIER DETECTION
    # ============================================================================
    with tab1:
        st.markdown("### Outlier Detection Configuration")

        # Using session state to store configuration across tabs
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
                help="Choose the statistical algorithm used to identify outliers. IQR is better for skewed data; Z-Score is better for normal distributions.",
            )

            if st.session_state["detection_method"] == "iqr":
                st.session_state["iqr_factor"] = st.slider(
                    "IQR Factor (k)",
                    1.0,
                    3.0,
                    st.session_state["iqr_factor"],
                    0.1,
                    key="iqr_factor_slider",
                    help="Determines the sensitivity. A lower value (e.g., 1.0) detects more outliers; a higher value (e.g., 3.0) detects only extreme outliers. Standard is 1.5.",
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
                    help="Determines how many standard deviations from the mean a point must be to be considered an outlier. Standard is 3.0.",
                )
                summary = outlier_summary(
                    df,
                    method="zscore",
                    threshold=st.session_state["zscore_threshold"],
                )

        with col2:
            st.markdown("#### Outlier Summary by Column")
            st.dataframe(summary, use_container_width=True)
            st.info(
                "This table shows the count and percentage of outliers detected in each numeric column based on the settings on the left."
            )

    # ============================================================================
    # TAB 2: CLEANING ACTIONS
    # ============================================================================
    with tab2:
        st.markdown("### Configure Cleaning Actions")

        # --- Step 1: Column Selection ---
        st.markdown("#### Step 1: Select Columns")
        col1, col2 = st.columns([3, 1])

        with col1:
            all_cols = df.columns.tolist()
            if st.button(
                "Toggle Select All/None",
                use_container_width=False,
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
                help="Select the specific columns you wish to apply transformations to (e.g., removing outliers, filling missing values).",
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
                """
            Automatically create a drop mask to remove rows containing outliers in the **selected columns**.
            """
            )

            col_mode = st.radio(
                "Drop rows where outliers are found in:",
                ["Any selected column (Union)", "All selected columns (Intersection)"],
                index=0,
                key="drop_mode",
                help="**Union**: If a row has an outlier in Column A OR Column B, it is removed.\n**Intersection**: A row is only removed if it has an outlier in Column A AND Column B.",
            )

            if st.button(
                "Generate Batch Drop Mask",
                type="primary",
                use_container_width=False,
                help="Calculates outliers based on your Step 1 settings and flags those rows for removal.",
            ):
                mask_any = pd.Series(False, index=df.index)
                mask_all = pd.Series(True, index=df.index)

                current_method = st.session_state["detection_method"]
                factor = st.session_state["iqr_factor"]
                thresh = st.session_state["zscore_threshold"]

                for c in cols_for_clean:
                    if pd.api.types.is_numeric_dtype(df[c]):
                        if current_method == "iqr":
                            m = detect_outliers_iqr(df[c], factor=factor)
                        else:
                            m = detect_outliers_zscore(df[c], threshold=thresh)
                        mask_any = mask_any | m
                        mask_all = mask_all & m

                mask_to_use = mask_any if col_mode.startswith("Any") else mask_all
                st.session_state["auto_drop_mask"] = mask_to_use

                rows_affected = int(mask_to_use.sum())
                pct_affected = (rows_affected / len(df)) * 100

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

        # --- Step 3: Individual Column Actions (Redesigned) ---
        st.markdown("#### Step 3: Configure Column Transformations")
        st.markdown(
            "Fine-tune cleaning for each selected column individually. Select a column from the dropdown to edit its settings."
        )

        # 1. Cleanup: Remove configs for columns that were deselected in Step 1
        current_config_keys = list(st.session_state["individual_actions"].keys())
        for k in current_config_keys:
            if k not in cols_for_clean:
                del st.session_state["individual_actions"][k]

        actions = st.session_state["individual_actions"]

        if not cols_for_clean:
            st.info("Select columns in Step 1 to configure transformations.")
        else:
            current_method = st.session_state["detection_method"]
            factor = st.session_state["iqr_factor"]
            thresh = st.session_state["zscore_threshold"]

            # --- Layout: Split into Selection (Left) and Editor (Right) ---
            sel_col1, sel_col2 = st.columns([1, 2])

            with sel_col1:
                st.markdown("##### 1. Select Column")

                # Format function adds a checkmark if the column has actions configured
                def fmt_col(col_name):
                    return f"✅ {col_name}" if col_name in actions else col_name

                selected_col_edit = st.selectbox(
                    "Pick a column to configure:",
                    cols_for_clean,
                    format_func=fmt_col,
                    help="Select a column to view its profile and add cleaning actions (Capping, Imputation).",
                )

                # Progress Indicator
                n_configured = len(actions)
                n_total = len(cols_for_clean)
                st.progress(n_configured / n_total if n_total > 0 else 0)
                st.caption(f"Configured: {n_configured} / {n_total} columns")

            with sel_col2:
                # --- Editor Card ---
                # We wrap the editor in a container with a border for visual separation
                with st.container(border=True):
                    c = selected_col_edit
                    st.markdown(f"#### 🛠️ Configure: `{c}`")

                    # Ensure only numeric columns can use Capping/Outlier methods
                    is_numeric = pd.api.types.is_numeric_dtype(df[c])
                    available_methods = ["impute"]
                    if is_numeric:
                        available_methods.extend(["drop_outliers", "cap"])

                    # --- Section A: Column Profile (Mini-Dashboard) ---
                    stat_col1, stat_col2, stat_col3 = st.columns(3)

                    with stat_col1:
                        st.caption("Data Type")
                        st.markdown(f"**{df[c].dtype}**")

                    with stat_col2:
                        n_missing = df[c].isna().sum()
                        pct_missing = (n_missing / len(df)) * 100
                        st.caption("Missing Values")
                        st.markdown(f"**{n_missing:,}** ({pct_missing:.1f}%)")

                    with stat_col3:
                        st.caption("Range / Unique")
                        if is_numeric:
                            st.markdown(
                                f"**{df[c].min():.2f}** - **{df[c].max():.2f}**"
                            )
                        else:
                            st.markdown(f"**{df[c].nunique()}** unique items")

                    st.markdown("---")

                    # --- Section B: Method Selection ---
                    # We get default selections from existing session state
                    current_acts = actions.get(c, [])
                    default_methods = [
                        a["method"]
                        for a in current_acts
                        if a["method"] in available_methods
                    ]

                    chosen = st.multiselect(
                        "Select Cleaning Methods",
                        available_methods,
                        default=default_methods,
                        key=f"methods_{c}",
                        help="Select one or more methods. They are applied in order: Drop Outliers -> Cap Values -> Impute.",
                    )

                    col_actions = []

                    if not chosen:
                        st.info("No actions selected for this column.")
                    else:
                        # --- Section C: Method Configuration Forms ---

                        # 1. Drop Outliers
                        if "drop_outliers" in chosen:
                            st.markdown("##### 1. Drop Outliers")
                            if current_method == "iqr":
                                mask = detect_outliers_iqr(df[c], factor=factor)
                            else:
                                mask = detect_outliers_zscore(df[c], threshold=thresh)

                            rows_flagged = int(mask.sum())
                            pct_flagged = (rows_flagged / len(df)) * 100

                            st.warning(
                                f"Flags **{rows_flagged:,}** rows ({pct_flagged:.1f}%) for removal (based on global settings)."
                            )
                            col_actions.append(
                                {"method": "drop_outliers", "mask": mask}
                            )

                        # 2. Capping
                        if "cap" in chosen:
                            st.markdown("##### 2. Cap Values")
                            cap_col1, cap_col2 = st.columns(2)

                            # Retrieve existing cap values safely
                            prev_cap = next(
                                (a for a in current_acts if a["method"] == "cap"), {}
                            )

                            with cap_col1:
                                lower = st.number_input(
                                    "Lower Cap Value",
                                    value=prev_cap.get("lower"),
                                    placeholder="No lower cap",
                                    key=f"lower_{c}",
                                    help="Values lower than this will be set to this value.",
                                )

                            with cap_col2:
                                upper = st.number_input(
                                    "Upper Cap Value",
                                    value=prev_cap.get("upper"),
                                    placeholder="No upper cap",
                                    key=f"upper_{c}",
                                    help="Values higher than this will be set to this value.",
                                )

                            lval = None if lower is None else float(lower)
                            uval = None if upper is None else float(upper)
                            col_actions.append(
                                {"method": "cap", "lower": lval, "upper": uval}
                            )

                        # 3. Imputation (With Safe Logic)
                        if "impute" in chosen:
                            st.markdown("##### 3. Impute Missing Values")
                            imp_col1, imp_col2 = st.columns([2, 1])

                            # Determine safe strategies
                            if is_numeric:
                                impute_opts = ["median", "mean", "mode"]
                                default_idx = 0
                            else:
                                impute_opts = ["mode"]
                                default_idx = 0

                            # Retrieve existing imputation strategy
                            prev_imp = next(
                                (a for a in current_acts if a["method"] == "impute"), {}
                            )
                            prev_sel = prev_imp.get("impute", "median")

                            # Validate prev_sel against current options
                            curr_idx = (
                                impute_opts.index(prev_sel)
                                if prev_sel in impute_opts
                                else default_idx
                            )

                            with imp_col1:
                                strategy = st.selectbox(
                                    "Imputation Strategy",
                                    impute_opts,
                                    index=curr_idx,
                                    key=f"impute_{c}",
                                    help="**Median**: Good for skewed data.\n**Mean**: Good for normal data.\n**Mode**: Most frequent value.",
                                )

                            with imp_col2:
                                if n_missing > 0:
                                    st.info(f"Fills {n_missing} values")
                                else:
                                    st.success("No missing values")

                            col_actions.append({"method": "impute", "impute": strategy})

                    # --- Save Config for this column immediately ---
                    if col_actions:
                        st.session_state["individual_actions"][c] = col_actions
                    else:
                        # If list is empty but key exists, remove it (user deselected all actions)
                        if c in st.session_state["individual_actions"]:
                            del st.session_state["individual_actions"][c]

        # Summary of actions (Global View)
        st.markdown("---")
        st.markdown("#### Summary of Configured Actions")

        # Re-fetch actions to ensure the summary is up to date
        final_actions = st.session_state["individual_actions"]
        summary_items = []

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

    # ============================================================================
    # TAB 3: PREVIEW & APPLY
    # ============================================================================
    with tab3:
        st.markdown("### Preview and Apply Changes")
        st.markdown("See the impact of your cleaning actions before committing.")

        preview_col1, preview_col2 = st.columns([1, 3])

        with preview_col1:
            preview_button = st.button(
                "Generate Preview",
                type="primary",
                use_container_width=True,
                key="preview_button",
                help="Click this to run the configured cleaning steps on a copy of your data and generate the report below.",
            )

        if preview_button:
            # We must pull actions from session state because that's where we saved them
            active_actions = st.session_state["individual_actions"]

            if not active_actions and st.session_state.get("auto_drop_mask") is None:
                st.warning(
                    "No cleaning actions configured. Please configure actions in the 'Cleaning Actions' tab."
                )
            else:
                with st.spinner("Processing data..."):
                    cleaned = df.copy()

                    # Apply auto drop mask
                    adm = st.session_state.get("auto_drop_mask")
                    if adm is not None:
                        cleaned = cleaned.loc[~adm].reset_index(drop=True)

                    # Apply individual column actions
                    if active_actions:
                        cleaned = apply_cleaning(cleaned, active_actions)

                    st.session_state["cleaned_df"] = cleaned

                    st.success("Cleaning preview generated successfully!")

                    # Impact Metrics
                    st.markdown("---")
                    st.markdown("### Impact Analysis")

                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

                    rows_removed = df.shape[0] - cleaned.shape[0]
                    pct_removed = (rows_removed / df.shape[0]) * 100

                    metric_col1.metric(
                        "Original Rows",
                        f"{df.shape[0]:,}",
                        help="Total number of rows in the uploaded dataset.",
                    )
                    metric_col2.metric(
                        "Cleaned Rows",
                        f"{cleaned.shape[0]:,}",
                        delta=f"-{rows_removed:,}",
                        delta_color="inverse",
                        help="Number of rows remaining after cleaning operations.",
                    )
                    metric_col3.metric(
                        "Rows Removed %",
                        f"{pct_removed:.2f}%",
                        delta=f"{rows_removed:,} total",
                        help="Percentage of the original dataset that was removed.",
                    )

                    missing_before = df.isna().sum().sum()
                    missing_after = cleaned.isna().sum().sum()

                    delta_missing = missing_before - missing_after
                    delta_color = "normal" if delta_missing > 0 else "inverse"

                    metric_col4.metric(
                        "Missing Values (Remaining)",
                        f"{missing_after:,}",
                        delta=f"-{delta_missing:,}",
                        delta_color=delta_color,
                        help="Total count of NaN (empty) cells remaining in the dataset. A positive delta means values were filled.",
                    )

                    st.markdown("---")

                    # Data Preview
                    st.markdown("### Cleaned Data Preview")
                    st.dataframe(
                        cleaned.head(100), use_container_width=True, height=400
                    )

                    st.markdown("---")

                    # Detailed Comparisons
                    st.markdown("### Detailed Missing Value Comparison")

                    missing_before_series = df.isna().sum().rename("Missing Before")
                    missing_after_series = cleaned.isna().sum().rename("Missing After")

                    comparison_df = (
                        pd.concat([missing_before_series, missing_after_series], axis=1)
                        .fillna(0)
                        .astype(int)
                    )
                    comparison_df["Change"] = (
                        comparison_df["Missing After"] - comparison_df["Missing Before"]
                    )
                    comparison_df["% Change (Original)"] = (
                        (
                            (comparison_df["Change"] / comparison_df["Missing Before"])
                            * 100
                        )
                        .round(1)
                        .fillna(0)
                    )

                    st.dataframe(
                        comparison_df[comparison_df["Missing Before"] > 0],
                        use_container_width=True,
                    )

                    st.markdown("---")

                    # Download Section
                    st.markdown("### Export Cleaned Data")

                    download_col1, download_col2 = st.columns([1, 1])

                    with download_col1:
                        csv = cleaned.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "Download CSV",
                            data=csv,
                            file_name="cleaned_data.csv",
                            mime="text/csv",
                            use_container_width=True,
                            type="primary",
                            help="Download the cleaned dataset as a CSV file.",
                        )

        # Show help when no preview generated
        if "cleaned_df" not in st.session_state:
            st.info("""
            **Get Started**:
            1. Configure outlier detection parameters in the first tab.
            2. Define your cleaning actions (Row Drop, Capping, Imputation) in the second tab.
            3. Click "Generate Preview" to process the data and analyze the results.
            """)
