import io
import os
import pandas as pd
import streamlit as st
import plotly.express as px
import logging
from plotly_theme import BRAND_TEMPLATE
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # This loads GEMINI_API_KEY from .env
except ImportError:
    pass  # python-dotenv not installed, will use system env vars

from eda import read_dataset, basic_profile, summary_stats, outlier_summary, apply_cleaning, detect_outliers_iqr, detect_outliers_zscore, column_profile
from gemini_client import generate_text
from ai_visual_generator import generate_insights_with_visuals
from agents import SupervisorAgent
from memory import SessionMemory

st.set_page_config(
    page_title="Data Alchemy Lab",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)
#hi this is Harsh 

def _inject_modular_css():
    import time
    cache_bust = int(time.time())  # Force cache refresh on each run
    css_files = [
        "styles/theme_tokens.css",
        "styles/base.css",
        "styles/components.css",
        "styles/dark.css",
        "styles/motion.css",
    ]
    for path in css_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except FileNotFoundError:
            st.warning(f"Missing CSS file: {path}")
    
    # Remove header anchor links completely with JavaScript
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Remove all header anchor links
        const anchors = document.querySelectorAll('h1 a, h2 a, h3 a, h4 a, h5 a, h6 a, a.streamlit-anchor, a.headerlink');
        anchors.forEach(a => {
            if (a.parentElement) {
                const parent = a.parentElement;
                while (a.firstChild) {
                    parent.insertBefore(a.firstChild, a);
                }
                a.remove();
            }
        });
    });
    
    // Watch for dynamic content and remove anchors as they appear
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' || mutation.type === 'subtree') {
                const anchors = document.querySelectorAll('h1 a, h2 a, h3 a, h4 a, h5 a, h6 a, a.streamlit-anchor, a.headerlink');
                anchors.forEach(a => {
                    if (a.parentElement) {
                        const parent = a.parentElement;
                        while (a.firstChild) {
                            parent.insertBefore(a.firstChild, a);
                        }
                        a.remove();
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """, unsafe_allow_html=True)


def _render_journey(uploaded_flag: bool):
    steps = [
        ("Upload Dataset", uploaded_flag),
        ("Profile & Explore", uploaded_flag),
        ("Clean & Transform", 'cleaned_df' in st.session_state),
        ("AI Insights", st.session_state.get('auto_insights_generated') or st.session_state.get('custom_insights_generated')),
    ]
    blocks = []
    for label, done in steps:
        cls = "sidebar-journey-step active" if done else "sidebar-journey-step"
        blocks.append(f"<div class='{cls}'>{label}</div>")
    st.sidebar.markdown("### Data Journey")
    st.sidebar.markdown("<div class='journey-block'>" + "".join(blocks) + "</div>", unsafe_allow_html=True)


_inject_modular_css()

header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown(
        '''<div class="page-header fade-in" style="padding: 0.5rem 0 1.25rem; margin-bottom: 0.75rem;">
            <div class="page-title">Data Alchemy Lab</div>
            <div class="page-subtitle">Turn raw files into refined, decision-grade intelligence — profile, cleanse, synthesize, and narrate your data story.</div>
        </div>''',
        unsafe_allow_html=True,
    )

# Initialize file history in session state
if 'file_history' not in st.session_state:
    st.session_state['file_history'] = []

# Initialize Agent System
if 'agent_memory' not in st.session_state:
    st.session_state['agent_memory'] = SessionMemory()
if 'supervisor' not in st.session_state:
    st.session_state['supervisor'] = SupervisorAgent(st.session_state['agent_memory'])

# Move file uploader to the sidebar to declutter main canvas
st.sidebar.markdown('### Upload Dataset')
uploaded = st.sidebar.file_uploader('Choose a file', type=['csv', 'xls', 'xlsx'], label_visibility='collapsed')
_render_journey(uploaded is not None or st.session_state.get('history_to_load') is not None)
st.sidebar.caption('Supported formats: CSV, Excel (XLS, XLSX)')

# Agent Activity Feed
st.sidebar.markdown('---')
st.sidebar.markdown('### Agent Activity')
with st.sidebar.expander("View Agent Logs", expanded=True):
    if 'agent_memory' in st.session_state:
        history = st.session_state['agent_memory'].get_recent_history(10)
        if not history:
            st.caption("No activity yet.")
        else:
            for action in reversed(history):
                prefix = "Thinking:" if action.action_type == "thought" else "Action:"
                st.markdown(f"**{prefix} {action.agent_name}:** {action.content}")
                st.markdown("---")

# File History Section
st.sidebar.markdown('---')
st.sidebar.markdown('### File History')
if st.session_state['file_history']:
    selected_history = st.sidebar.selectbox(
        'View past files:',
        ['Current File'] + [f"{h['name']} ({h['timestamp']})" for h in st.session_state['file_history']],
        key='history_selector'
    )

    if selected_history != 'Current File':
        # Find the selected file in history
        for h in st.session_state['file_history']:
            if f"{h['name']} ({h['timestamp']})" == selected_history:
                st.sidebar.markdown(f'<div style="background-color: rgba(38, 102, 127, 0.4); padding: 1rem; border-radius: 8px; margin: 0.5rem 0;"><p style="color: #ffffff; margin: 0.3rem 0; font-weight: 500;"><strong>Filename:</strong> {h["name"]}</p><p style="color: #ffffff; margin: 0.3rem 0; font-weight: 500;"><strong>Uploaded:</strong> {h["timestamp"]}</p><p style="color: #ffffff; margin: 0.3rem 0; font-weight: 500;"><strong>Rows:</strong> {h["rows"]}</p><p style="color: #ffffff; margin: 0.3rem 0; font-weight: 500;"><strong>Columns:</strong> {h["columns"]}</p></div>', unsafe_allow_html=True)
                if st.sidebar.button('Load This File Data', key=f'load_history_{h["timestamp"]}'):
                    st.session_state['history_to_load'] = h.get('id') or h['timestamp']
                    st.experimental_rerun()
                break
else:
    st.sidebar.info('No file history yet')

loaded_from_history = None
if st.session_state.get('history_to_load') is not None and st.session_state['file_history']:
    target_id = st.session_state['history_to_load']
    for h in st.session_state['file_history']:
        if (h.get('id') or h.get('timestamp')) == target_id:
            try:
                data_bytes = h.get('data_bytes')
                if data_bytes is not None:
                    buffer = io.BytesIO(data_bytes)
                    loaded_from_history = read_dataset(buffer)
            except Exception as e:
                st.error(f"Failed to load historical file: {e}")
            finally:
                st.session_state['history_to_load'] = None
            break

if uploaded is not None or loaded_from_history is not None:
    df = read_dataset(uploaded) if uploaded is not None else loaded_from_history
    # Reset session state related to previous dataset insights/cleaning
    st.session_state['cleaned_df'] = None
    st.session_state['auto_drop_mask'] = None
    st.session_state['auto_insights_generated'] = False
    st.session_state['custom_insights_generated'] = False
    st.session_state['custom_insights_figures'] = []
    st.session_state['custom_insights_text'] = None
    
    # Agent: Process new upload
    with st.spinner('Supervisor Agent is analyzing the dataset...'):
        df = st.session_state['supervisor'].process_upload(df)
    
    # Save to file history
    from datetime import datetime
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_info = {
        'name': uploaded.name if uploaded is not None else 'Loaded from history',
        'timestamp': current_time,
        'rows': df.shape[0],
        'columns': df.shape[1],
        'id': f"{current_time}-{df.shape[0]}-{df.shape[1]}",
        'data_bytes': (uploaded.getvalue() if uploaded is not None else None)
    }
    
    # Check if this file is already in history (by name and avoid duplicates)
    if not any(h['name'] == uploaded.name and h['timestamp'].split()[0] == current_time.split()[0] 
               for h in st.session_state['file_history']):
        st.session_state['file_history'].insert(0, file_info)
        # Keep only last 10 files in history
        if len(st.session_state['file_history']) > 10:
            st.session_state['file_history'] = st.session_state['file_history'][:10]
    
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('## Data Preview')
    st.dataframe(df.head(100), width='stretch')

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('## Dataset Profile')
    
    # Display profile in a nicer format
    profile = basic_profile(df)
    
    profile_col1, profile_col2, profile_col3, profile_col4 = st.columns(4)
    
    with profile_col1:
        st.metric("Total Rows", f"{profile['rows']:,}")
    with profile_col2:
        st.metric("Total Columns", f"{profile['columns']:,}")
    with profile_col3:
        total_missing = sum(profile['missing'].values())
        st.metric("Missing Values", f"{total_missing:,}")
    with profile_col4:
        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        st.metric("Memory Usage", f"{memory_mb:.2f} MB")

    st.markdown('### Column Profile')
    st.dataframe(column_profile(df), width='stretch')

    # Detect if this is a sales dataset and add specialized visualizations
    is_sales_data = False
    sales_columns = {'Date', 'Customer', 'Total_Amount'}
    if sales_columns.issubset(set(df.columns)):
        is_sales_data = True
        
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown('## Sales Analytics Dashboard')
        st.info('Sales dataset detected - Specialized visualizations enabled')
        
        # Prepare data
        df_sales = df.copy()
        df_sales['Date'] = pd.to_datetime(df_sales['Date'])
        df_sales['Month_Year'] = df_sales['Date'].dt.to_period('M').astype(str)
        df_sales['Year'] = df_sales['Date'].dt.year
        
        # Create tabs for different analyses
        sales_tab1, sales_tab2, sales_tab3, sales_tab4 = st.tabs([
            "Sales Over Time", 
            "Sales by Customer", 
            "Product Analysis",
            "Key Metrics"
        ])
        
        with sales_tab1:
            st.markdown('### Sales Trends Over Time')
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Daily sales trend
                daily_sales = df_sales.groupby('Date')['Total_Amount'].sum().reset_index()
                fig_daily = px.line(
                    daily_sales,
                    x='Date',
                    y='Total_Amount',
                    title='Daily Sales Trend',
                    labels={'Total_Amount': 'Sales ($)', 'Date': 'Date'},
                    template=BRAND_TEMPLATE,
                )
                fig_daily.update_traces(line_color='#1f77b4', line_width=2, fill='tozeroy')
                st.plotly_chart(fig_daily, width='stretch')
                
                # Monthly sales
                monthly_sales = df_sales.groupby('Month_Year')['Total_Amount'].sum().reset_index()
                fig_monthly = px.bar(
                    monthly_sales,
                    x='Month_Year',
                    y='Total_Amount',
                    title='Monthly Sales',
                    labels={'Total_Amount': 'Sales ($)', 'Month_Year': 'Month'},
                    color='Total_Amount',
                    color_continuous_scale='Viridis',
                    template=BRAND_TEMPLATE,
                )
                st.plotly_chart(fig_monthly, width='stretch')
            
            with col2:
                # Cumulative sales
                daily_sales['Cumulative_Sales'] = daily_sales['Total_Amount'].cumsum()
                fig_cumulative = px.area(
                    daily_sales,
                    x='Date',
                    y='Cumulative_Sales',
                    title='Cumulative Sales Growth',
                    labels={'Cumulative_Sales': 'Cumulative Sales ($)', 'Date': 'Date'},
                    template=BRAND_TEMPLATE,
                )
                st.plotly_chart(fig_cumulative, width='stretch')
                
                # Yearly comparison
                yearly_sales = df_sales.groupby('Year')['Total_Amount'].sum().reset_index()
                fig_yearly = px.bar(
                    yearly_sales,
                    x='Year',
                    y='Total_Amount',
                    title='Year-over-Year Sales',
                    labels={'Total_Amount': 'Sales ($)', 'Year': 'Year'},
                    text='Total_Amount',
                    color='Total_Amount',
                    color_continuous_scale='Blues',
                    template=BRAND_TEMPLATE,
                )
                fig_yearly.update_traces(texttemplate='$%{text:.2s}', textposition='outside')
                st.plotly_chart(fig_yearly, width='stretch')
        
        with sales_tab2:
            st.markdown('### Sales by Customer Analysis')
            
            # Customer aggregations
            customer_stats = df_sales.groupby('Customer').agg({
                'Total_Amount': ['sum', 'mean', 'count']
            }).round(2)
            customer_stats.columns = ['Total_Sales', 'Avg_Transaction', 'Transaction_Count']
            customer_stats = customer_stats.reset_index().sort_values('Total_Sales', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top customers bar chart
                top_n = st.slider('Number of top customers to display', 5, 20, 10, key='top_customers_slider')
                top_customers = customer_stats.head(top_n)
                
                fig_customers = px.bar(
                    top_customers,
                    x='Customer',
                    y='Total_Sales',
                    title=f'Top {top_n} Customers by Total Sales',
                    labels={'Total_Sales': 'Total Sales ($)', 'Customer': 'Customer'},
                    color='Total_Sales',
                    color_continuous_scale='Plasma',
                    text='Total_Sales',
                    template=BRAND_TEMPLATE,
                )
                fig_customers.update_traces(texttemplate='$%{text:.2s}', textposition='outside')
                fig_customers.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_customers, width='stretch')
                
                # Customer transaction count
                fig_trans = px.bar(
                    top_customers,
                    x='Customer',
                    y='Transaction_Count',
                    title=f'Transaction Count - Top {top_n} Customers',
                    labels={'Transaction_Count': 'Number of Transactions', 'Customer': 'Customer'},
                    color='Transaction_Count',
                    color_continuous_scale='Teal',
                    template=BRAND_TEMPLATE,
                )
                fig_trans.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_trans, width='stretch')
            
            with col2:
                # Customer revenue pie chart
                fig_pie = px.pie(
                    top_customers,
                    values='Total_Sales',
                    names='Customer',
                    title=f'Revenue Distribution - Top {top_n} Customers',
                    hole=0.4,
                    template=BRAND_TEMPLATE,
                )
                st.plotly_chart(fig_pie, width='stretch')
                
                # Scatter: Transaction Count vs Avg Transaction
                fig_scatter = px.scatter(
                    top_customers,
                    x='Transaction_Count',
                    y='Avg_Transaction',
                    size='Total_Sales',
                    color='Total_Sales',
                    hover_name='Customer',
                    title='Customer Value Analysis',
                    labels={
                        'Transaction_Count': 'Number of Transactions',
                        'Avg_Transaction': 'Avg Transaction Value ($)',
                        'Total_Sales': 'Total Sales ($)'
                    },
                    color_continuous_scale='Viridis',
                    template=BRAND_TEMPLATE,
                )
                
                st.plotly_chart(fig_scatter, width='stretch')
            
            # Customer summary table
            st.markdown('<br>', unsafe_allow_html=True)
            st.markdown('### Customer Statistics Table')
            st.dataframe(
                customer_stats.head(15).style.format({
                    'Total_Sales': '${:,.2f}',
                    'Avg_Transaction': '${:,.2f}',
                    'Transaction_Count': '{:.0f}'
                }),
                width='stretch'
            )
        
        with sales_tab3:
            st.markdown('### Product Performance Analysis')
            
            if 'Product' in df_sales.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Product sales
                    product_sales = df_sales.groupby('Product')['Total_Amount'].sum().reset_index()
                    product_sales = product_sales.sort_values('Total_Amount', ascending=False)
                    
                    fig_products = px.bar(
                        product_sales,
                        x='Product',
                        y='Total_Amount',
                        title='Sales by Product',
                        labels={'Total_Amount': 'Sales ($)', 'Product': 'Product'},
                        color='Total_Amount',
                        color_continuous_scale='Sunset',
                        template=BRAND_TEMPLATE,
                    )
                    fig_products.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_products, width='stretch')
                    
                    # Product quantity
                    if 'Quantity' in df_sales.columns:
                        product_qty = df_sales.groupby('Product')['Quantity'].sum().reset_index()
                        product_qty = product_qty.sort_values('Quantity', ascending=False)
                        
                        fig_qty = px.bar(
                            product_qty,
                            x='Product',
                            y='Quantity',
                            title='Units Sold by Product',
                            labels={'Quantity': 'Units Sold', 'Product': 'Product'},
                            color='Quantity',
                            color_continuous_scale='Greens',
                            template=BRAND_TEMPLATE,
                        )
                        fig_qty.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_qty, width='stretch')
                
                with col2:
                    # Product pie chart
                    fig_product_pie = px.pie(
                        product_sales.head(10),
                        values='Total_Amount',
                        names='Product',
                        title='Top 10 Products Revenue Share',
                        hole=0.3,
                        template=BRAND_TEMPLATE,
                    )
                    st.plotly_chart(fig_product_pie, width='stretch')
                    
                    # Product trends over time
                    product_timeline = df_sales.groupby(['Month_Year', 'Product'])['Total_Amount'].sum().reset_index()
                    top_5_products = product_sales.head(5)['Product'].tolist()
                    product_timeline_top = product_timeline[product_timeline['Product'].isin(top_5_products)]
                    
                    fig_product_trend = px.line(
                        product_timeline_top,
                        x='Month_Year',
                        y='Total_Amount',
                        color='Product',
                        title='Top 5 Products Sales Trend',
                        labels={'Total_Amount': 'Sales ($)', 'Month_Year': 'Month'},
                        template=BRAND_TEMPLATE,
                    )
                    st.plotly_chart(fig_product_trend, width='stretch')
            else:
                st.info('Product column not found in the dataset.')
        
        with sales_tab4:
            st.markdown('### Key Performance Metrics')
            
            # Calculate metrics
            total_revenue = df_sales['Total_Amount'].sum()
            total_transactions = len(df_sales)
            avg_transaction = df_sales['Total_Amount'].mean()
            total_customers = df_sales['Customer'].nunique()
            avg_per_customer = total_revenue / total_customers
            
            # Display metrics in columns
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric(
                    label="Total Revenue",
                    value=f"${total_revenue:,.2f}",
                    delta=None
                                    )
                
                st.metric(
                    label="Total Transactions",
                    value=f"{total_transactions:,}",
                    delta=None
                                    )
                
            
            with metric_col2:
                st.metric(
                    label="Avg Transaction",
                    value=f"${avg_transaction:,.2f}",
                    delta=None
                                    )
                
                st.metric(
                    label="Total Customers",
                    value=f"{total_customers:,}",
                    delta=None
                                    )
                
            
            with metric_col3:
                st.metric(
                    label="Avg per Customer",
                    value=f"${avg_per_customer:,.2f}",
                    delta=None
                                    )
                
                if 'Product' in df_sales.columns:
                    total_products = df_sales['Product'].nunique()
                    st.metric(
                        label="Total Products",
                        value=f"{total_products:,}",
                        delta=None
                                        )
                    
            
            with metric_col4:
                date_range_days = (df_sales['Date'].max() - df_sales['Date'].min()).days
                st.metric(
                    label="Date Range (Days)",
                    value=f"{date_range_days:,}",
                    delta=None
                                    )
                
                daily_avg = total_revenue / max(date_range_days, 1)
                st.metric(
                    label="Avg Daily Sales",
                    value=f"${daily_avg:,.2f}",
                    delta=None
                                    )
                
            
            # Additional insights
            st.markdown('---')
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('### Top Performers')
                best_day = daily_sales.loc[daily_sales['Total_Amount'].idxmax()]
                st.write(f"**Best Sales Day:** {best_day['Date'].strftime('%Y-%m-%d')} (${best_day['Total_Amount']:,.2f})")
                
                best_customer = customer_stats.iloc[0]
                st.write(f"**Top Customer:** {best_customer['Customer']} (${best_customer['Total_Sales']:,.2f})")
                
                if 'Product' in df_sales.columns:
                    best_product = product_sales.iloc[0]
                    st.write(f"**Top Product:** {best_product['Product']} (${best_product['Total_Amount']:,.2f})")
            
            with col2:
                st.markdown('### Distribution Insights')
                if 'Region' in df_sales.columns:
                    region_sales = df_sales.groupby('Region')['Total_Amount'].sum().reset_index()
                    region_sales = region_sales.sort_values('Total_Amount', ascending=False)
                    fig_region = px.bar(
                        region_sales,
                        x='Region',
                        y='Total_Amount',
                        title='Sales by Region',
                        color='Total_Amount',
                        color_continuous_scale='Blues',
                        template=BRAND_TEMPLATE,
                    )
                    st.plotly_chart(fig_region, width='stretch')
                else:
                    st.info('Regional data not available')
        
        st.markdown('---')

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('## Statistical Summary')
    st.dataframe(summary_stats(df), width='stretch')

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('## Data Distributions')
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        col = st.selectbox('Choose numeric column for histogram', numeric_cols)
        fig = px.histogram(df, x=col, nbins=50, marginal='box', template=BRAND_TEMPLATE)
        st.plotly_chart(fig, width='stretch')
    else:
        st.info('No numeric columns found for distributions.')

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('## Correlation Analysis')
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()
        fig = px.imshow(corr, text_auto=True, template=BRAND_TEMPLATE)
        st.plotly_chart(fig, width='stretch')
    else:
        st.info('Need at least 2 numeric columns for correlation matrix.')

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('## Outlier Detection')
    method = st.radio('Method', ['iqr', 'zscore'])
    if method == 'iqr':
        factor = st.slider('IQR factor', 1.0, 3.0, 1.5)
        summary = outlier_summary(df, method='iqr', factor=factor)
    else:
        thresh = st.slider('Z-score threshold', 2.0, 5.0, 3.0)
        summary = outlier_summary(df, method='zscore', threshold=thresh)
    st.dataframe(summary, width='stretch')

    # Interactive cleaning (modernized)
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('## Data Cleaning & Transformation')

    if 'auto_drop_mask' not in st.session_state:
        st.session_state['auto_drop_mask'] = None

    # Select-all helper
    select_all = st.checkbox('Select all columns for cleaning', value=False)
    cols_default = df.columns.tolist() if select_all else None
    cols_for_clean = st.multiselect('Select columns to create cleaning actions for', df.columns.tolist(), default=cols_default)

    # Quick auto-drop controls
    with st.expander('Quick outlier removal (auto-create drop actions)', expanded=False):
        st.write('Create a global drop mask based on outliers in the selected columns.')
        col_mode = st.radio('Drop mode', ['Any selected column (union)', 'All selected columns (intersection)'], index=0)
        if st.button('Create drop-outlier mask for selected columns'):
            if not cols_for_clean:
                st.warning('Select at least one column first.')
            else:
                mask_any = pd.Series(False, index=df.index)
                mask_all = pd.Series(True, index=df.index)
                for c in cols_for_clean:
                    if method == 'iqr':
                        m = detect_outliers_iqr(df[c], factor=factor)
                    else:
                        m = detect_outliers_zscore(df[c], threshold=thresh)
                    mask_any = mask_any | m
                    mask_all = mask_all & m
                mask_to_use = mask_any if col_mode.startswith('Any') else mask_all
                st.session_state['auto_drop_mask'] = mask_to_use
                st.success(f'Auto drop mask created: {int(mask_to_use.sum())} rows flagged')

    # Build per-column manual actions; start with an empty dict and let users override or inspect
    actions = {}
    for c in cols_for_clean:
        with st.expander(f'Action for `{c}`', expanded=False):
            chosen = st.multiselect(f'Select method(s) for {c}', ['drop_outliers', 'cap', 'impute'], key=f'methods_{c}')
            if not chosen:
                continue
            col_actions = []
            if 'drop_outliers' in chosen:
                if method == 'iqr':
                    mask = detect_outliers_iqr(df[c], factor=factor)
                else:
                    mask = detect_outliers_zscore(df[c], threshold=thresh)
                col_actions.append({'method': 'drop', 'mask': mask})
                st.write(f'Rows flagged in `{c}`: {int(mask.sum())}')
            if 'cap' in chosen:
                lower = st.number_input(f'Lower cap for {c} (leave empty for none)', value=float('nan'), key=f'lower_{c}')
                upper = st.number_input(f'Upper cap for {c} (leave empty for none)', value=float('nan'), key=f'upper_{c}')
                lval = None if pd.isna(lower) else float(lower)
                uval = None if pd.isna(upper) else float(upper)
                col_actions.append({'method': 'cap', 'lower': lval, 'upper': uval})
            if 'impute' in chosen:
                strategy = st.selectbox(f'Impute strategy for {c}', ['median', 'mean', 'mode'], key=f'impute_{c}')
                col_actions.append({'method': 'impute', 'impute': strategy})

            if col_actions:
                actions[c] = col_actions

    # Preview / apply cleaning — clearer primary/secondary column layout
    st.markdown('<br>', unsafe_allow_html=True)
    st.info('Tip: use the quick outlier removal to auto-flag rows, then optionally add caps or imputations per column.')
    
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button('Preview cleaned dataset', key='preview_btn'):
            cleaned = df.copy()
            # apply global auto-drop mask first (if created)
            adm = st.session_state.get('auto_drop_mask')
            if adm is not None:
                cleaned = cleaned.loc[~adm].reset_index(drop=True)

            # apply per-column actions
            if actions:
                cleaned = apply_cleaning(cleaned, actions)

            # Store cleaned data in session state
            st.session_state['cleaned_df'] = cleaned

            st.markdown('<br>', unsafe_allow_html=True)
            st.subheader('Cleaned preview')
            
            # Use container to control layout and prevent overflow
            st.dataframe(
                cleaned.head(100), 
                width='stretch',
                height=400
            )

            st.markdown('<br>', unsafe_allow_html=True)
            st.markdown('### Comparison (Before / After)')
            
            # Metrics row
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric('Original Rows', f"{df.shape[0]:,}")
            with metric_col2:
                st.metric('Cleaned Rows', f"{cleaned.shape[0]:,}", delta=f"{- (df.shape[0] - cleaned.shape[0])}")
            
            st.markdown('<br>', unsafe_allow_html=True)
            
            # Missing values comparison - stacked for better visibility
            with st.expander('View missing values before', expanded=False):
                st.dataframe(df.isna().sum().to_frame('Missing Count'), width='stretch')
            
            with st.expander('View missing values after', expanded=False):
                st.dataframe(cleaned.isna().sum().to_frame('Missing Count'), width='stretch')

            st.markdown('<br>', unsafe_allow_html=True)
            csv = cleaned.to_csv(index=False).encode('utf-8')
            st.download_button('Download cleaned CSV', data=csv, file_name='cleaned.csv', width='stretch')
    
    if not actions and st.session_state.get('auto_drop_mask') is None:
        st.info('No cleaning actions selected. Use the UI above to create actions or auto-generate an outlier drop mask.')

    # Insights section - Generate visual graphs on button click (AFTER CLEANING)
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('## AI-Powered Insights')
    st.markdown('<div class="insights-preface">We distill statistical texture, temporal shifts, cohort behaviors and emergent anomalies into a concise narrative. Generate automatic synthesis or interrogate with custom prompts.</div>', unsafe_allow_html=True)
    
    # Check if we have cleaned data or use original
    if 'cleaned_df' in st.session_state and st.session_state['cleaned_df'] is not None:
        data_for_insights = st.session_state['cleaned_df']
    else:
        data_for_insights = df
    
    # Get API key from environment (no UI message)
    api_key = os.getenv('GEMINI_API_KEY')
    
    # Create tabs for different insight types
    tab1, tab2 = st.tabs(["Automatic Analysis", "Custom Query"])

    with tab1:
        st.info('Generate comprehensive visual insights automatically using AI analysis of your dataset.')
        
        # Initialize session state
        if 'auto_insights_generated' not in st.session_state:
            st.session_state.auto_insights_generated = False
            st.session_state.auto_insights_figures = []
            st.session_state.auto_insights_text = None
        
        if st.button('Generate Insights', key='gen_auto_insights_btn'):
            if not api_key:
                st.error('API key not configured. Please add GEMINI_API_KEY to your .env file.')
            else:
                with st.spinner('Analyzing data and generating visualizations...'):
                    try:
                        from ai_visual_generator import generate_insights_with_visuals
                        
                        # Agent: Handle query (Automatic)
                        figures, insights_text = st.session_state['supervisor'].handle_query(
                            data_for_insights, 
                            query="Analyze this dataset and provide key findings, trends, and anomalies.", 
                            api_key=api_key
                        )
                        error = None if figures or insights_text else "Agent returned no results."
                        if isinstance(insights_text, str) and insights_text.startswith("Error"):
                             error = insights_text
                        
                        if error:
                            st.error(f'Error generating insights: {error}')
                            st.session_state.auto_insights_generated = False
                        else:
                            st.session_state.auto_insights_figures = figures
                            st.session_state.auto_insights_text = insights_text
                            st.session_state.auto_insights_generated = True
                            
                    except Exception as e:
                        st.error(f'Error generating insights: {str(e)}')
                        st.session_state.auto_insights_generated = False
        
        # Display results if available
        if st.session_state.auto_insights_generated:
            # Display visualizations
            if st.session_state.auto_insights_figures:
                st.markdown('### Visual Insights')
                for idx, fig in enumerate(st.session_state.auto_insights_figures):
                    st.plotly_chart(fig, width='stretch', key=f'auto_insight_chart_{idx}')
            
            # Display text summary at the bottom
            if st.session_state.auto_insights_text:
                with st.expander("View Analysis Summary", expanded=False):
                    st.markdown(st.session_state.auto_insights_text)
            
            # Clear button
            if st.button('Clear Results', key='clear_auto_insights'):
                st.session_state.auto_insights_generated = False
                st.session_state.auto_insights_figures = []
                st.session_state.auto_insights_text = None
                st.rerun()

    with tab2:
        st.info('Ask specific questions to generate targeted visual insights based on your data requirements.')
        
        # Initialize session state
        if 'custom_insights_generated' not in st.session_state:
            st.session_state.custom_insights_generated = False
            st.session_state.custom_insights_figures = []
            st.session_state.custom_insights_text = None
        
        custom_prompt = st.text_area(
            "Enter your question:", 
            key='custom_prompt_text_area', 
            height=100,
            placeholder="Example: Show me sales trends by customer over time"
        )
        
        if st.button('Generate Insights', key='gen_custom_insights_btn'):
            if not api_key:
                st.error('API key not configured. Please add GEMINI_API_KEY to your .env file.')
            elif not custom_prompt:
                st.warning("Please enter a question.")
            else:
                with st.spinner('Analyzing data and generating visualizations...'):
                    try:
                        from ai_visual_generator import generate_insights_with_visuals
                        
                        # Agent: Handle query (Custom)
                        figures, insights_text = st.session_state['supervisor'].handle_query(
                            data_for_insights, 
                            query=custom_prompt, 
                            api_key=api_key
                        )
                        error = None if figures or insights_text else "Agent returned no results."
                        if isinstance(insights_text, str) and insights_text.startswith("Error"):
                             error = insights_text
                        
                        if error:
                            st.error(f'Error generating insights: {error}')
                            st.session_state.custom_insights_generated = False
                        else:
                            st.session_state.custom_insights_figures = figures
                            st.session_state.custom_insights_text = insights_text
                            st.session_state.custom_insights_generated = True
                            
                    except Exception as e:
                        st.error(f'Error generating insights: {str(e)}')
                        st.session_state.custom_insights_generated = False
        
        # Display results if available
        if st.session_state.custom_insights_generated:
            # Display visualizations
            if st.session_state.custom_insights_figures:
                st.markdown('### Visual Insights')
                for idx, fig in enumerate(st.session_state.custom_insights_figures):
                    st.plotly_chart(fig, width='stretch', key=f'custom_insight_chart_{idx}')
            
            # Display text summary at the bottom
            if st.session_state.custom_insights_text:
                with st.expander("View Analysis Summary", expanded=False):
                    st.markdown(st.session_state.custom_insights_text)
            
            # Clear button
            if st.button('Clear Results', key='clear_custom_insights'):
                st.session_state.custom_insights_generated = False
                st.session_state.custom_insights_figures = []
                st.session_state.custom_insights_text = None
                st.rerun()

else:
    # Welcome screen - clean and simple
    st.markdown('<div style="font-size: var(--fs-xl); font-family: var(--font-serif); font-weight: 600; margin-top: var(--space-6); margin-bottom: var(--space-3);">Welcome to Data Analysis Platform</div>', unsafe_allow_html=True)
    st.markdown('---')
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div style="font-size: var(--fs-lg); font-family: var(--font-serif); font-weight: 600; margin-top: var(--space-5); margin-bottom: var(--space-2);">Getting Started</div>', unsafe_allow_html=True)
        st.markdown('''
        1. Upload your CSV or Excel file using the sidebar
        2. Review the data profile and statistics
        3. Explore visualizations and correlations
        4. Detect and handle outliers
        5. Clean and transform your data
        6. Download the cleaned dataset
        ''')
        
    with col2:
        st.markdown('<div style="font-size: var(--fs-lg); font-family: var(--font-serif); font-weight: 600; margin-top: var(--space-5); margin-bottom: var(--space-2);">Platform Capabilities</div>', unsafe_allow_html=True)
        st.markdown('''
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
        ''')
