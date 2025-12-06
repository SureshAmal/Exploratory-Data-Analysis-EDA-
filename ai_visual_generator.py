"""
AI-Powered Visual Insights Generator
Generates charts and graphs based on AI analysis of the data
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from gemini_client import generate_text


def generate_targeted_visuals(df, question):
    """
    Generate ONLY relevant visualizations based on the user's specific question.
    This avoids generating unnecessary charts and wasting API tokens.
    """
    figures = []
    question_lower = question.lower()

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # Detect what the question is asking about
    is_about_customer = "customer" in question_lower
    is_about_sales = (
        "sales" in question_lower
        or "revenue" in question_lower
        or "amount" in question_lower
    )
    is_about_time = (
        "time" in question_lower
        or "trend" in question_lower
        or "over" in question_lower
        or "date" in question_lower
    )
    is_about_product = "product" in question_lower
    is_about_region = "region" in question_lower or "location" in question_lower
    is_about_comparison = (
        "compare" in question_lower
        or "versus" in question_lower
        or "vs" in question_lower
    )
    is_about_distribution = (
        "distribution" in question_lower or "spread" in question_lower
    )

    # Find relevant columns based on question
    customer_col = None
    sales_col = None
    date_col = None
    product_col = None
    region_col = None

    for col in df.columns:
        col_lower = col.lower()
        if "customer" in col_lower and is_about_customer:
            customer_col = col
        if (
            "total" in col_lower
            or "amount" in col_lower
            or "sales" in col_lower
            or "revenue" in col_lower
        ) and is_about_sales:
            sales_col = col
        if ("date" in col_lower or "time" in col_lower) and is_about_time:
            date_col = col
        if "product" in col_lower and is_about_product:
            product_col = col
        if ("region" in col_lower or "location" in col_lower) and is_about_region:
            region_col = col

    # Generate TARGETED visualizations based on the question

    # CUSTOMER-BASED ANALYSIS
    if is_about_customer and customer_col and sales_col:
        # Sales by customer - Bar chart
        customer_sales = (
            df.groupby(customer_col)[sales_col]
            .sum()
            .sort_values(ascending=False)
            .head(15)
        )
        fig = px.bar(
            x=customer_sales.index,
            y=customer_sales.values,
            title=f"Sales by {customer_col}",
            labels={"x": customer_col, "y": f"Total {sales_col}"},
            template="plotly_white",
            color=customer_sales.values,
            color_continuous_scale="Viridis",
        )
        fig.update_layout(height=450, xaxis_tickangle=-45)
        figures.append(fig)

        # Pie chart for top customers
        top_10_customers = customer_sales.head(10)
        fig_pie = px.pie(
            values=top_10_customers.values,
            names=top_10_customers.index,
            title=f"Top 10 {customer_col} - Revenue Share",
            template="plotly_white",
            hole=0.3,
        )
        fig_pie.update_layout(height=450)
        figures.append(fig_pie)

        # Customer transaction count
        if len(df) > 0:
            customer_count = (
                df.groupby(customer_col).size().sort_values(ascending=False).head(15)
            )
            fig_count = px.bar(
                x=customer_count.index,
                y=customer_count.values,
                title=f"Number of Transactions by {customer_col}",
                labels={"x": customer_col, "y": "Transaction Count"},
                template="plotly_white",
                color=customer_count.values,
                color_continuous_scale="Teal",
            )
            fig_count.update_layout(height=450, xaxis_tickangle=-45)
            figures.append(fig_count)

    # TIME-BASED ANALYSIS
    elif is_about_time and date_col and sales_col:
        df_temp = df.copy()
        df_temp[date_col] = pd.to_datetime(df_temp[date_col])
        df_temp = df_temp.sort_values(date_col)

        # Daily/Time trend
        fig = px.line(
            df_temp,
            x=date_col,
            y=sales_col,
            title=f"{sales_col} Over Time",
            markers=True,
            template="plotly_white",
        )
        fig.update_traces(line_color="steelblue", line_width=2, fill="tozeroy")
        fig.update_layout(height=450)
        figures.append(fig)

        # Monthly aggregation if applicable
        df_temp["Month"] = df_temp[date_col].dt.to_period("M").astype(str)
        monthly = df_temp.groupby("Month")[sales_col].sum().reset_index()
        fig_monthly = px.bar(
            monthly,
            x="Month",
            y=sales_col,
            title=f"Monthly {sales_col}",
            template="plotly_white",
            color=sales_col,
            color_continuous_scale="Viridis",
        )
        fig_monthly.update_layout(height=450)
        figures.append(fig_monthly)

    # PRODUCT-BASED ANALYSIS
    elif is_about_product and product_col and sales_col:
        # Sales by product
        product_sales = (
            df.groupby(product_col)[sales_col]
            .sum()
            .sort_values(ascending=False)
            .head(15)
        )
        fig = px.bar(
            x=product_sales.index,
            y=product_sales.values,
            title=f"Sales by {product_col}",
            labels={"x": product_col, "y": f"Total {sales_col}"},
            template="plotly_white",
            color=product_sales.values,
            color_continuous_scale="Sunset",
        )
        fig.update_layout(height=450, xaxis_tickangle=-45)
        figures.append(fig)

        # Product pie chart
        top_products = product_sales.head(10)
        fig_pie = px.pie(
            values=top_products.values,
            names=top_products.index,
            title=f"Top 10 {product_col} - Revenue Share",
            template="plotly_white",
        )
        fig_pie.update_layout(height=450)
        figures.append(fig_pie)

    # REGION-BASED ANALYSIS
    elif is_about_region and region_col and sales_col:
        # Sales by region
        region_sales = (
            df.groupby(region_col)[sales_col].sum().sort_values(ascending=False)
        )
        fig = px.bar(
            x=region_sales.index,
            y=region_sales.values,
            title=f"Sales by {region_col}",
            labels={"x": region_col, "y": f"Total {sales_col}"},
            template="plotly_white",
            color=region_sales.values,
            color_continuous_scale="Blues",
        )
        fig.update_layout(height=450)
        figures.append(fig)

    # DISTRIBUTION ANALYSIS
    elif is_about_distribution and sales_col:
        # Histogram
        fig = px.histogram(
            df,
            x=sales_col,
            title=f"Distribution of {sales_col}",
            template="plotly_white",
            marginal="box",
        )
        fig.update_layout(height=450)
        figures.append(fig)

    # FALLBACK: If no specific pattern matched, create a few generic relevant charts
    if not figures:
        # Bar chart for first categorical vs first numeric
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            grouped = (
                df.groupby(cat_col)[num_col].sum().sort_values(ascending=False).head(15)
            )
            fig = px.bar(
                x=grouped.index,
                y=grouped.values,
                title=f"{num_col} by {cat_col}",
                labels={"x": cat_col, "y": num_col},
                template="plotly_white",
            )
            fig.update_layout(height=450, xaxis_tickangle=-45)
            figures.append(fig)

        # Add one more chart if available
        if len(numeric_cols) >= 2:
            fig_scatter = px.scatter(
                df,
                x=numeric_cols[0],
                y=numeric_cols[1],
                title=f"{numeric_cols[0]} vs {numeric_cols[1]}",
                template="plotly_white",
            )
            fig_scatter.update_layout(height=450)
            figures.append(fig_scatter)

    return figures


def generate_insights_with_visuals(df, custom_prompt=None, api_key=None):
    """
    Use AI to analyze data and generate appropriate visualizations
    Returns: (figures_list, insights_text, error_message)
    """

    try:
        # Prepare data summary for AI
        data_info = f"""Dataset Information:
Rows: {len(df)}
Columns: {len(df.columns)}
Column Names: {", ".join(df.columns.tolist())}

Data Types:
{df.dtypes.to_string()}

Sample Data (first 5 rows):
{df.head(5).to_string()}

Statistical Summary:
{df.describe().to_string()}
"""

        # Handle CUSTOM PROMPT differently - generate ONLY relevant visualizations
        if custom_prompt:
            prompt = f"""{custom_prompt}

{data_info}

Based on this specific question, provide a focused analysis that directly answers the question. 
Be concise and only mention relevant insights."""

            # Get AI analysis
            ai_response = generate_text(prompt, api_key=api_key, max_output_tokens=4096)

            if ai_response.startswith(
                ("Error:", "API error:", "HTTP error", "Unable to extract")
            ):
                return [], None, ai_response

            # Generate ONLY relevant visualizations based on the question
            figures = generate_targeted_visuals(df, custom_prompt.lower())

            return figures, ai_response, None

        # AUTOMATIC ANALYSIS - Create comprehensive AI prompt
        else:
            prompt = f"""{data_info}

Analyze this dataset and provide:
1. Key findings and patterns
2. Important trends
3. Anomalies or outliers
4. Business recommendations
5. Data quality observations

Be specific and actionable."""

            # Get AI analysis
            ai_response = generate_text(prompt, api_key=api_key, max_output_tokens=8192)

            if ai_response.startswith(
                ("Error:", "API error:", "HTTP error", "Unable to extract")
            ):
                return [], None, ai_response

        # Generate comprehensive visualizations for automatic analysis
        figures = []

        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        # 1. Distribution Charts for Numeric Columns
        if len(numeric_cols) >= 1:
            for i, col in enumerate(numeric_cols[:4]):  # Top 4 numeric columns
                fig = make_subplots(
                    rows=1,
                    cols=2,
                    subplot_titles=(f"{col} Distribution", f"{col} Statistics"),
                    specs=[[{"type": "histogram"}, {"type": "box"}]],
                )

                fig.add_trace(
                    go.Histogram(x=df[col], name="Frequency", marker_color="steelblue"),
                    row=1,
                    col=1,
                )

                fig.add_trace(
                    go.Box(y=df[col], name="Statistics", marker_color="coral"),
                    row=1,
                    col=2,
                )

                fig.update_layout(
                    title_text=f"Analysis of {col}",
                    showlegend=False,
                    height=350,
                    template="plotly_white",
                )

                figures.append(fig)

        # 2. Categorical Analysis
        if categorical_cols:
            for col in categorical_cols[:2]:  # Top 2 categorical columns
                value_counts = df[col].value_counts().head(10)

                # Bar chart
                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"Top Categories in {col}",
                    labels={"x": col, "y": "Count"},
                    template="plotly_white",
                )
                fig.update_traces(marker_color="steelblue")
                fig.update_layout(height=350)
                figures.append(fig)

                # Pie chart if less than 8 categories
                if len(value_counts) <= 8:
                    fig_pie = px.pie(
                        values=value_counts.values,
                        names=value_counts.index,
                        title=f"Distribution of {col}",
                        template="plotly_white",
                    )
                    fig_pie.update_layout(height=350)
                    figures.append(fig_pie)

        # 3. Correlation Analysis
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()

            fig = px.imshow(
                corr_matrix,
                title="Correlation Analysis",
                color_continuous_scale="RdBu",
                aspect="auto",
                text_auto=".2f",
                template="plotly_white",
            )
            fig.update_layout(height=500)
            figures.append(fig)

        # 4. Scatter Plot Analysis
        if len(numeric_cols) >= 2:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]

            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                title=f"{x_col} vs {y_col}",
                trendline="ols",
                color=df[categorical_cols[0]] if categorical_cols else None,
                template="plotly_white",
            )
            fig.update_layout(height=450)
            figures.append(fig)

        # 5. Time Series if date column exists
        date_cols = []
        for col in df.columns:
            if "date" in col.lower() or "time" in col.lower():
                try:
                    df_temp = df.copy()
                    df_temp[col] = pd.to_datetime(df_temp[col])
                    date_cols.append(col)
                except Exception:
                    pass

        if date_cols and numeric_cols:
            date_col = date_cols[0]
            value_col = numeric_cols[0]

            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col])
            df_temp = df_temp.sort_values(date_col)

            fig = px.line(
                df_temp,
                x=date_col,
                y=value_col,
                title=f"{value_col} Over Time",
                markers=True,
                template="plotly_white",
            )
            fig.update_traces(line_color="steelblue", line_width=2)
            fig.update_layout(height=400)
            figures.append(fig)

        # 6. Multi-variable comparison
        if len(numeric_cols) >= 3:
            # Top 3 metrics comparison
            top_3 = numeric_cols[:3]

            fig = go.Figure()
            for col in top_3:
                fig.add_trace(go.Box(y=df[col], name=col))

            fig.update_layout(
                title="Comparative Analysis",
                yaxis_title="Values",
                template="plotly_white",
                height=400,
            )
            figures.append(fig)

        return figures, ai_response, None

    except Exception as e:
        return [], None, f"Error generating insights: {str(e)}"
