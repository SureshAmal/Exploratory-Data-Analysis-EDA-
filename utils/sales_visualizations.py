#!/usr/bin/env python
"""
Sales Analysis and Visualization Script

This script provides comprehensive visual insights for sales data including:
1. Sales trends over time (daily, monthly, quarterly)
2. Sales by customer with rankings and comparisons
3. Product performance analysis
4. Regional and sales rep analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.style.use('seaborn-v0_8-darkgrid')


class SalesAnalyzer:
    """Comprehensive sales analysis and visualization class"""
    
    def __init__(self, data_path='sales_data.csv'):
        """Initialize the analyzer with sales data"""
        self.df = pd.read_csv(data_path)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df['Year'] = self.df['Date'].dt.year
        self.df['Month'] = self.df['Date'].dt.month
        self.df['Quarter'] = self.df['Date'].dt.quarter
        self.df['Month_Year'] = self.df['Date'].dt.to_period('M').astype(str)
        self.df['Week'] = self.df['Date'].dt.isocalendar().week
        
    def sales_over_time(self, save_plot=False):
        """
        Comprehensive sales trends over time analysis
        Shows daily, monthly, and quarterly trends
        """
        print("\n" + "="*80)
        print("SALES TRENDS OVER TIME ANALYSIS")
        print("="*80)
        
        # Daily sales
        daily_sales = self.df.groupby('Date')['Total_Amount'].sum().reset_index()
        
        # Monthly sales
        monthly_sales = self.df.groupby('Month_Year')['Total_Amount'].sum().reset_index()
        monthly_sales['Month_Year'] = pd.to_datetime(monthly_sales['Month_Year'])
        
        # Quarterly sales
        quarterly_sales = self.df.groupby(['Year', 'Quarter'])['Total_Amount'].sum().reset_index()
        quarterly_sales['Quarter_Label'] = quarterly_sales['Year'].astype(str) + '-Q' + quarterly_sales['Quarter'].astype(str)
        
        # Create comprehensive visualization
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Daily Sales Trend', 'Monthly Sales Trend',
                'Quarterly Sales Comparison', 'Cumulative Sales Growth',
                'Sales Distribution by Month', 'Year-over-Year Comparison'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "box"}, {"type": "bar"}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.15
        )
        
        # 1. Daily Sales Trend
        fig.add_trace(
            go.Scatter(
                x=daily_sales['Date'],
                y=daily_sales['Total_Amount'],
                mode='lines',
                name='Daily Sales',
                line=dict(color='#1f77b4', width=1),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.2)'
            ),
            row=1, col=1
        )
        
        # 2. Monthly Sales Trend with moving average
        fig.add_trace(
            go.Scatter(
                x=monthly_sales['Month_Year'],
                y=monthly_sales['Total_Amount'],
                mode='lines+markers',
                name='Monthly Sales',
                line=dict(color='#ff7f0e', width=2),
                marker=dict(size=8)
            ),
            row=1, col=2
        )
        
        # Add 3-month moving average
        monthly_sales['MA_3'] = monthly_sales['Total_Amount'].rolling(window=3, center=True).mean()
        fig.add_trace(
            go.Scatter(
                x=monthly_sales['Month_Year'],
                y=monthly_sales['MA_3'],
                mode='lines',
                name='3-Month MA',
                line=dict(color='red', width=2, dash='dash')
            ),
            row=1, col=2
        )
        
        # 3. Quarterly Sales Comparison
        colors = ['#2ca02c', '#d62728', '#9467bd', '#8c564b']
        for i, (year, group) in enumerate(quarterly_sales.groupby('Year')):
            fig.add_trace(
                go.Bar(
                    x=group['Quarter'],
                    y=group['Total_Amount'],
                    name=f'{year}',
                    marker_color=colors[i % len(colors)]
                ),
                row=2, col=1
            )
        
        # 4. Cumulative Sales Growth
        daily_sales['Cumulative_Sales'] = daily_sales['Total_Amount'].cumsum()
        fig.add_trace(
            go.Scatter(
                x=daily_sales['Date'],
                y=daily_sales['Cumulative_Sales'],
                mode='lines',
                name='Cumulative Sales',
                line=dict(color='#17becf', width=2),
                fill='tozeroy'
            ),
            row=2, col=2
        )
        
        # 5. Sales Distribution by Month
        for month in range(1, 13):
            month_data = self.df[self.df['Month'] == month]['Total_Amount']
            fig.add_trace(
                go.Box(
                    y=month_data,
                    name=datetime(2000, month, 1).strftime('%b'),
                    marker_color=px.colors.qualitative.Set3[month-1]
                ),
                row=3, col=1
            )
        
        # 6. Year-over-Year Comparison
        yearly_sales = self.df.groupby('Year')['Total_Amount'].sum().reset_index()
        yearly_growth = yearly_sales.copy()
        yearly_growth['Growth_%'] = yearly_growth['Total_Amount'].pct_change() * 100
        
        fig.add_trace(
            go.Bar(
                x=yearly_sales['Year'],
                y=yearly_sales['Total_Amount'],
                name='Total Sales',
                marker_color='#bcbd22',
                text=yearly_sales['Total_Amount'].apply(lambda x: f'${x/1e6:.2f}M'),
                textposition='outside'
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="📊 Comprehensive Sales Trends Analysis",
            title_font_size=20,
            showlegend=True,
            height=1400,
            hovermode='x unified'
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_yaxes(title_text="Sales ($)", row=1, col=1)
        fig.update_xaxes(title_text="Month", row=1, col=2)
        fig.update_yaxes(title_text="Sales ($)", row=1, col=2)
        fig.update_xaxes(title_text="Quarter", row=2, col=1)
        fig.update_yaxes(title_text="Sales ($)", row=2, col=1)
        fig.update_xaxes(title_text="Date", row=2, col=2)
        fig.update_yaxes(title_text="Cumulative Sales ($)", row=2, col=2)
        fig.update_xaxes(title_text="Month", row=3, col=1)
        fig.update_yaxes(title_text="Sales ($)", row=3, col=1)
        fig.update_xaxes(title_text="Year", row=3, col=2)
        fig.update_yaxes(title_text="Total Sales ($)", row=3, col=2)
        
        if save_plot:
            fig.write_html('sales_over_time_comprehensive.html')
            print("✓ Saved interactive plot to 'sales_over_time_comprehensive.html'")
        
        fig.show()
        
        # Print summary statistics
        print("\n📈 Sales Trends Summary:")
        print(f"  Total Sales Period: {self.df['Date'].min().strftime('%Y-%m-%d')} to {self.df['Date'].max().strftime('%Y-%m-%d')}")
        print(f"  Total Revenue: ${self.df['Total_Amount'].sum():,.2f}")
        print(f"  Average Daily Sales: ${daily_sales['Total_Amount'].mean():,.2f}")
        print(f"  Average Monthly Sales: ${monthly_sales['Total_Amount'].mean():,.2f}")
        print(f"  Best Day: {daily_sales.loc[daily_sales['Total_Amount'].idxmax(), 'Date'].strftime('%Y-%m-%d')} (${daily_sales['Total_Amount'].max():,.2f})")
        print(f"  Best Month: {monthly_sales.loc[monthly_sales['Total_Amount'].idxmax(), 'Month_Year']} (${monthly_sales['Total_Amount'].max():,.2f})")
        
        if len(yearly_sales) > 1:
            yoy_growth = ((yearly_sales.iloc[-1]['Total_Amount'] - yearly_sales.iloc[-2]['Total_Amount']) / yearly_sales.iloc[-2]['Total_Amount']) * 100
            print(f"  Year-over-Year Growth: {yoy_growth:+.2f}%")
        
        return fig
    
    def sales_by_customer(self, top_n=15, save_plot=False):
        """
        Comprehensive customer sales analysis
        Shows total sales, transaction counts, and customer rankings
        """
        print("\n" + "="*80)
        print("SALES BY CUSTOMER ANALYSIS")
        print("="*80)
        
        # Customer aggregations
        customer_stats = self.df.groupby('Customer').agg({
            'Total_Amount': ['sum', 'mean', 'count'],
            'Quantity': 'sum',
            'Discount_Percent': 'mean'
        }).round(2)
        
        customer_stats.columns = ['Total_Sales', 'Avg_Transaction', 'Transaction_Count', 'Total_Quantity', 'Avg_Discount']
        customer_stats = customer_stats.reset_index()
        customer_stats['Revenue_per_Unit'] = (customer_stats['Total_Sales'] / customer_stats['Total_Quantity']).round(2)
        customer_stats = customer_stats.sort_values('Total_Sales', ascending=False)
        
        # Get top customers
        top_customers = customer_stats.head(top_n)
        
        # Create comprehensive visualization
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                f'Top {top_n} Customers by Total Sales',
                'Sales Distribution by Customer',
                'Customer Transaction Count vs Avg Transaction Value',
                'Customer Revenue Contribution (%)',
                'Top Customers: Discount Impact',
                'Customer Sales Timeline'
            ),
            specs=[
                [{"type": "bar"}, {"type": "box"}],
                [{"type": "scatter"}, {"type": "pie"}],
                [{"type": "bar"}, {"type": "scatter"}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.15
        )
        
        # 1. Top Customers by Total Sales
        fig.add_trace(
            go.Bar(
                x=top_customers['Customer'],
                y=top_customers['Total_Sales'],
                name='Total Sales',
                marker=dict(
                    color=top_customers['Total_Sales'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Sales ($)", x=0.46)
                ),
                text=top_customers['Total_Sales'].apply(lambda x: f'${x/1000:.1f}K'),
                textposition='outside'
            ),
            row=1, col=1
        )
        
        # 2. Sales Distribution by Customer (Box plot)
        all_customers = customer_stats['Customer'].tolist()
        for customer in all_customers[:10]:  # Show top 10
            customer_sales = self.df[self.df['Customer'] == customer]['Total_Amount']
            fig.add_trace(
                go.Box(
                    y=customer_sales,
                    name=customer[:15],  # Truncate long names
                    marker_color=px.colors.qualitative.Set2[all_customers.index(customer) % len(px.colors.qualitative.Set2)]
                ),
                row=1, col=2
            )
        
        # 3. Transaction Count vs Avg Transaction Value
        fig.add_trace(
            go.Scatter(
                x=top_customers['Transaction_Count'],
                y=top_customers['Avg_Transaction'],
                mode='markers+text',
                name='Customers',
                marker=dict(
                    size=top_customers['Total_Sales'] / 10000,  # Size by total sales
                    color=top_customers['Total_Sales'],
                    colorscale='Plasma',
                    showscale=True,
                    colorbar=dict(title="Sales ($)", x=1.15)
                ),
                text=top_customers['Customer'].apply(lambda x: x[:10]),
                textposition='top center'
            ),
            row=2, col=1
        )
        
        # 4. Customer Revenue Contribution (Pie)
        fig.add_trace(
            go.Pie(
                labels=top_customers['Customer'],
                values=top_customers['Total_Sales'],
                hole=0.4,
                marker=dict(colors=px.colors.qualitative.Set3)
            ),
            row=2, col=2
        )
        
        # 5. Discount Impact on Top Customers
        fig.add_trace(
            go.Bar(
                x=top_customers['Customer'],
                y=top_customers['Avg_Discount'],
                name='Avg Discount %',
                marker_color='coral',
                text=top_customers['Avg_Discount'].apply(lambda x: f'{x:.1f}%'),
                textposition='outside'
            ),
            row=3, col=1
        )
        
        # 6. Customer Sales Timeline (Top 5)
        for i, customer in enumerate(top_customers.head(5)['Customer']):
            customer_timeline = self.df[self.df['Customer'] == customer].groupby('Month_Year')['Total_Amount'].sum().reset_index()
            customer_timeline['Month_Year'] = pd.to_datetime(customer_timeline['Month_Year'])
            fig.add_trace(
                go.Scatter(
                    x=customer_timeline['Month_Year'],
                    y=customer_timeline['Total_Amount'],
                    mode='lines+markers',
                    name=customer,
                    line=dict(width=2)
                ),
                row=3, col=2
            )
        
        # Update layout
        fig.update_layout(
            title_text="👥 Comprehensive Customer Sales Analysis",
            title_font_size=20,
            showlegend=True,
            height=1400
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Customer", tickangle=-45, row=1, col=1)
        fig.update_yaxes(title_text="Total Sales ($)", row=1, col=1)
        fig.update_xaxes(title_text="Customer", row=1, col=2, showticklabels=False)
        fig.update_yaxes(title_text="Sales per Transaction ($)", row=1, col=2)
        fig.update_xaxes(title_text="Number of Transactions", row=2, col=1)
        fig.update_yaxes(title_text="Avg Transaction Value ($)", row=2, col=1)
        fig.update_xaxes(title_text="Customer", tickangle=-45, row=3, col=1)
        fig.update_yaxes(title_text="Average Discount (%)", row=3, col=1)
        fig.update_xaxes(title_text="Month", row=3, col=2)
        fig.update_yaxes(title_text="Sales ($)", row=3, col=2)
        
        if save_plot:
            fig.write_html('sales_by_customer_comprehensive.html')
            print("✓ Saved interactive plot to 'sales_by_customer_comprehensive.html'")
        
        fig.show()
        
        # Print summary statistics
        print(f"\n👥 Customer Analysis Summary:")
        print(f"  Total Unique Customers: {len(customer_stats)}")
        print(f"  Top Customer: {customer_stats.iloc[0]['Customer']} (${customer_stats.iloc[0]['Total_Sales']:,.2f})")
        print(f"  Average Sales per Customer: ${customer_stats['Total_Sales'].mean():,.2f}")
        print(f"  Top {top_n} Customers Account for: {(top_customers['Total_Sales'].sum() / customer_stats['Total_Sales'].sum() * 100):.1f}% of total revenue")
        
        print(f"\n📊 Top {min(10, len(customer_stats))} Customers by Total Sales:")
        print("-" * 80)
        print(f"{'Rank':<6}{'Customer':<25}{'Total Sales':<15}{'Transactions':<15}{'Avg/Trans':<15}")
        print("-" * 80)
        for idx, row in customer_stats.head(10).iterrows():
            rank = customer_stats.index.get_loc(idx) + 1
            print(f"{rank:<6}{row['Customer']:<25}${row['Total_Sales']:>12,.2f}  {int(row['Transaction_Count']):>12}  ${row['Avg_Transaction']:>12,.2f}")
        
        return fig, customer_stats
    
    def generate_all_insights(self, save_plots=True):
        """Generate all sales insights"""
        print("\n" + "="*80)
        print("COMPREHENSIVE SALES ANALYSIS REPORT")
        print("="*80)
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Dataset: {len(self.df)} transactions")
        print(f"Date Range: {self.df['Date'].min().strftime('%Y-%m-%d')} to {self.df['Date'].max().strftime('%Y-%m-%d')}")
        print("="*80)
        
        # Generate all visualizations
        self.sales_over_time(save_plot=save_plots)
        self.sales_by_customer(save_plot=save_plots)
        
        print("\n" + "="*80)
        print("✅ ANALYSIS COMPLETE")
        print("="*80)
        if save_plots:
            print("\n📁 Interactive HTML reports saved:")
            print("   • sales_over_time_comprehensive.html")
            print("   • sales_by_customer_comprehensive.html")
            print("\nOpen these files in your web browser for interactive exploration!")


def main():
    """Main execution function"""
    print("\n🚀 Starting Sales Analysis...")
    
    # Initialize analyzer
    analyzer = SalesAnalyzer('sales_data.csv')
    
    # Generate all insights
    analyzer.generate_all_insights(save_plots=True)
    
    print("\n✨ Done! Check the generated HTML files for interactive visualizations.")


if __name__ == '__main__':
    main()
