#!/usr/bin/env python
"""Generate sample sales dataset for demonstration purposes."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Generate dates for the past 2 years
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Customer names
customers = [
    'Acme Corp', 'TechStart Inc', 'Global Solutions', 'Innovate Ltd', 
    'FutureTech', 'DataDrive Co', 'CloudNine Systems', 'SmartBiz Inc',
    'NextGen Solutions', 'Digital Dynamics', 'Enterprise Plus', 'Metro Solutions',
    'Apex Industries', 'Quantum Corp', 'Zenith Systems'
]

# Product categories
products = [
    'Software License', 'Cloud Storage', 'Consulting Services', 'Hardware',
    'Training Package', 'Support Contract', 'Data Analytics Tool', 'API Access',
    'Custom Development', 'Security Suite'
]

# Regions
regions = ['North', 'South', 'East', 'West', 'Central']

# Sales representatives
sales_reps = ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Emma Brown']

# Generate sales data
num_transactions = 2000
data = []

for _ in range(num_transactions):
    date = np.random.choice(date_range)
    customer = np.random.choice(customers)
    product = np.random.choice(products)
    region = np.random.choice(regions)
    sales_rep = np.random.choice(sales_reps)
    
    # Generate sales amount with some variation
    base_price = {
        'Software License': 5000,
        'Cloud Storage': 1200,
        'Consulting Services': 8500,
        'Hardware': 3500,
        'Training Package': 2000,
        'Support Contract': 4500,
        'Data Analytics Tool': 6000,
        'API Access': 1500,
        'Custom Development': 12000,
        'Security Suite': 7500
    }
    
    amount = base_price[product] * np.random.uniform(0.7, 1.5)
    quantity = np.random.randint(1, 11)
    total_sale = amount * quantity
    
    # Add some discount randomly
    discount_pct = np.random.choice([0, 5, 10, 15, 20], p=[0.5, 0.2, 0.15, 0.1, 0.05])
    final_amount = total_sale * (1 - discount_pct/100)
    
    data.append({
        'Date': date.strftime('%Y-%m-%d'),
        'Customer': customer,
        'Product': product,
        'Region': region,
        'Sales_Rep': sales_rep,
        'Quantity': quantity,
        'Unit_Price': round(amount, 2),
        'Discount_Percent': discount_pct,
        'Total_Amount': round(final_amount, 2)
    })

# Create DataFrame
df = pd.DataFrame(data)

# Sort by date
df = df.sort_values('Date').reset_index(drop=True)

# Save to CSV
df.to_csv('sales_data.csv', index=False)
print(f"✓ Generated {len(df)} sales transactions")
print(f"✓ Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"✓ Total sales: ${df['Total_Amount'].sum():,.2f}")
print(f"✓ Saved to sales_data.csv")
print("\nSample data:")
print(df.head(10))
