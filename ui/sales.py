import streamlit as st
import pandas as pd
import plotly.express as px
from plotly_theme import BRAND_TEMPLATE
from typing import Optional
from streamlit.delta_generator import DeltaGenerator


def render_sales(
    df_sales: Optional[pd.DataFrame],
    parent: DeltaGenerator | None = None,
):
    """Render sales analytics dashboard. If `parent` is provided, all Streamlit calls will be invoked on it.
    Assumes `df_sales` has Date, Customer, Total_Amount at least."""
    s = parent if parent is not None else st

    s.markdown("<br>", unsafe_allow_html=True)
    if df_sales is None:
        s.info(
            "Sales dashboard disabled — dataset is missing Date/Customer/Total_Amount columns."
        )
        return

    s.markdown("## Sales Analytics Dashboard")
    s.info("Sales dataset detected - Specialized visualizations enabled")

    tabs = ["Sales Over Time", "Sales by Customer", "Product Analysis", "Key Metrics"]
    if "sales_active_tab" not in st.session_state:
        st.session_state.sales_active_tab = tabs[0]

    cols = s.columns(len(tabs))
    for i, name in enumerate(tabs):
        if cols[i].button(name, key=f"sales_tab_btn_{i}"):
            st.session_state.sales_active_tab = name

    selected = st.session_state.sales_active_tab

    # Sales Over Time
    if selected == "Sales Over Time":
        s.markdown("### Sales Trends Over Time")
        col1, col2 = s.columns(2)

        # Left column charts
        daily_sales = df_sales.groupby("Date")["Total_Amount"].sum().reset_index()
        fig_daily = px.line(
            daily_sales,
            x="Date",
            y="Total_Amount",
            title="Daily Sales Trend",
            labels={"Total_Amount": "Sales ($)", "Date": "Date"},
            template=BRAND_TEMPLATE,
        )
        fig_daily.update_traces(line_color="#1f77b4", line_width=2, fill="tozeroy")
        col1.plotly_chart(fig_daily, width='stretch')

        monthly_sales = (
            df_sales.groupby("Month_Year")["Total_Amount"].sum().reset_index()
        )
        fig_monthly = px.bar(
            monthly_sales,
            x="Month_Year",
            y="Total_Amount",
            title="Monthly Sales",
            labels={"Total_Amount": "Sales ($)", "Month_Year": "Month"},
            color="Total_Amount",
            color_continuous_scale="Viridis",
            template=BRAND_TEMPLATE,
        )
        col1.plotly_chart(fig_monthly, width='stretch')

        # Right column charts
        daily_sales["Cumulative_Sales"] = daily_sales["Total_Amount"].cumsum()
        fig_cumulative = px.area(
            daily_sales,
            x="Date",
            y="Cumulative_Sales",
            title="Cumulative Sales Growth",
            labels={"Cumulative_Sales": "Cumulative Sales ($)", "Date": "Date"},
            template=BRAND_TEMPLATE,
        )
        col2.plotly_chart(fig_cumulative, width='stretch')

        yearly_sales = df_sales.groupby("Year")["Total_Amount"].sum().reset_index()
        fig_yearly = px.bar(
            yearly_sales,
            x="Year",
            y="Total_Amount",
            title="Year-over-Year Sales",
            labels={"Total_Amount": "Sales ($)", "Year": "Year"},
            text="Total_Amount",
            color="Total_Amount",
            color_continuous_scale="Blues",
            template=BRAND_TEMPLATE,
        )
        fig_yearly.update_traces(texttemplate="$%{text:.2s}", textposition="outside")
        col2.plotly_chart(fig_yearly, width='stretch')

    # Sales by Customer
    elif selected == "Sales by Customer":
        s.markdown("### Sales by Customer Analysis")
        customer_stats = (
            df_sales.groupby("Customer")
            .agg({"Total_Amount": ["sum", "mean", "count"]})
            .round(2)
        )
        customer_stats.columns = ["Total_Sales", "Avg_Transaction", "Transaction_Count"]
        customer_stats = customer_stats.reset_index().sort_values(
            "Total_Sales", ascending=False
        )

        col1, col2 = s.columns(2)

        top_n = s.slider(
            "Number of top customers to display",
            5,
            20,
            10,
            key="top_customers_slider",
        )
        top_customers = customer_stats.head(top_n)

        fig_customers = px.bar(
            top_customers,
            x="Customer",
            y="Total_Sales",
            title=f"Top {top_n} Customers by Total Sales",
            labels={"Total_Sales": "Total Sales ($)", "Customer": "Customer"},
            color="Total_Sales",
            color_continuous_scale="Plasma",
            text="Total_Sales",
            template=BRAND_TEMPLATE,
        )
        fig_customers.update_traces(texttemplate="$%{text:.2s}", textposition="outside")
        fig_customers.update_layout(xaxis_tickangle=-45)
        col1.plotly_chart(fig_customers, width='stretch')

        fig_pie = px.pie(
            top_customers,
            values="Total_Sales",
            names="Customer",
            title=f"Revenue Distribution - Top {top_n} Customers",
            hole=0.4,
            template=BRAND_TEMPLATE,
        )
        col2.plotly_chart(fig_pie, width='stretch')

        s.markdown("<br>", unsafe_allow_html=True)
        s.markdown("### Customer Statistics Table")
        s.dataframe(
            customer_stats.head(15).style.format(
                {
                    "Total_Sales": "${:,.2f}",
                    "Avg_Transaction": "${:,.2f}",
                    "Transaction_Count": "{:.0f}",
                }
            ),
            width='stretch',
        )

    # Product Analysis
    elif selected == "Product Analysis":
        s.markdown("### Product Performance Analysis")
        if "Product" in df_sales.columns:
            col1, col2 = s.columns(2)

            product_sales = (
                df_sales.groupby("Product")["Total_Amount"].sum().reset_index()
            )
            product_sales = product_sales.sort_values("Total_Amount", ascending=False)
            fig_products = px.bar(
                product_sales,
                x="Product",
                y="Total_Amount",
                title="Sales by Product",
                labels={"Total_Amount": "Sales ($)", "Product": "Product"},
                color="Total_Amount",
                color_continuous_scale="Sunset",
                template=BRAND_TEMPLATE,
            )
            fig_products.update_layout(xaxis_tickangle=-45)
            col1.plotly_chart(fig_products, width='stretch')

            if "Quantity" in df_sales.columns:
                product_qty = (
                    df_sales.groupby("Product")["Quantity"].sum().reset_index()
                )
                product_qty = product_qty.sort_values("Quantity", ascending=False)
                fig_qty = px.bar(
                    product_qty,
                    x="Product",
                    y="Quantity",
                    title="Units Sold by Product",
                    labels={"Quantity": "Units Sold", "Product": "Product"},
                    color="Quantity",
                    color_continuous_scale="Greens",
                    template=BRAND_TEMPLATE,
                )
                fig_qty.update_layout(xaxis_tickangle=-45)
                col1.plotly_chart(fig_qty, width='stretch')

            fig_product_pie = px.pie(
                product_sales.head(10),
                values="Total_Amount",
                names="Product",
                title="Top 10 Products Revenue Share",
                hole=0.3,
                template=BRAND_TEMPLATE,
            )
            col2.plotly_chart(fig_product_pie, width='stretch')

            product_timeline = (
                df_sales.groupby(["Month_Year", "Product"])["Total_Amount"]
                .sum()
                .reset_index()
            )
            top_5_products = product_sales.head(5)["Product"].tolist()
            product_timeline_top = product_timeline[
                product_timeline["Product"].isin(top_5_products)
            ]
            fig_product_trend = px.line(
                product_timeline_top,
                x="Month_Year",
                y="Total_Amount",
                color="Product",
                title="Top 5 Products Sales Trend",
                labels={"Total_Amount": "Sales ($)", "Month_Year": "Month"},
                template=BRAND_TEMPLATE,
            )
            col2.plotly_chart(fig_product_trend, width='stretch')
        else:
            s.info("Product column not found in the dataset.")

    # Key Metrics
    elif selected == "Key Metrics":
        s.markdown("### Key Performance Metrics")
        total_revenue = df_sales["Total_Amount"].sum()
        total_transactions = len(df_sales)
        avg_transaction = df_sales["Total_Amount"].mean()
        total_customers = df_sales["Customer"].nunique()
        avg_per_customer = total_revenue / total_customers if total_customers > 0 else 0

        metric_col1, metric_col2, metric_col3, metric_col4 = s.columns(4)

        metric_col1.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")
        metric_col1.metric(label="Total Transactions", value=f"{total_transactions:,}")

        metric_col2.metric(label="Avg Transaction", value=f"${avg_transaction:,.2f}")
        metric_col2.metric(label="Total Customers", value=f"{total_customers:,}")

        metric_col3.metric(label="Avg per Customer", value=f"${avg_per_customer:,.2f}")
        if "Product" in df_sales.columns:
            total_products = df_sales["Product"].nunique()
            metric_col3.metric(label="Total Products", value=f"{total_products:,}")

        date_range_days = (df_sales["Date"].max() - df_sales["Date"].min()).days
        metric_col4.metric(label="Date Range (Days)", value=f"{date_range_days:,}")
        daily_avg = total_revenue / max(date_range_days, 1)
        metric_col4.metric(label="Avg Daily Sales", value=f"${daily_avg:,.2f}")

        s.markdown("---")
        col1, col2 = s.columns(2)

        col1.markdown("### Top Performers")
        daily_sales = df_sales.groupby("Date")["Total_Amount"].sum().reset_index()
        best_day = daily_sales.loc[daily_sales["Total_Amount"].idxmax()]
        col1.write(
            f"**Best Sales Day:** {best_day['Date'].strftime('%Y-%m-%d')} (${best_day['Total_Amount']:,.2f})"
        )

        customer_stats = (
            df_sales.groupby("Customer")
            .agg({"Total_Amount": ["sum", "mean", "count"]})
            .round(2)
        )
        customer_stats.columns = [
            "Total_Sales",
            "Avg_Transaction",
            "Transaction_Count",
        ]
        customer_stats = customer_stats.reset_index().sort_values(
            "Total_Sales", ascending=False
        )
        best_customer = customer_stats.iloc[0]
        col1.write(
            f"**Top Customer:** {best_customer['Customer']} (${best_customer['Total_Sales']:,.2f})"
        )

        if "Product" in df_sales.columns:
            product_sales = (
                df_sales.groupby("Product")["Total_Amount"].sum().reset_index()
            )
            product_sales = product_sales.sort_values("Total_Amount", ascending=False)
            best_product = product_sales.iloc[0]
            col1.write(
                f"**Top Product:** {best_product['Product']} (${best_product['Total_Amount']:,.2f})"
            )

        col2.markdown("### Distribution Insights")
        if "Region" in df_sales.columns:
            region_sales = (
                df_sales.groupby("Region")["Total_Amount"].sum().reset_index()
            )
            region_sales = region_sales.sort_values("Total_Amount", ascending=False)
            fig_region = px.bar(
                region_sales,
                x="Region",
                y="Total_Amount",
                title="Sales by Region",
                color="Total_Amount",
                color_continuous_scale="Blues",
                template=BRAND_TEMPLATE,
            )
            col2.plotly_chart(fig_region, width='stretch')
        else:
            col2.info("Regional data not available")
