# Run code:  streamlit run scenarios_strmlt.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit interface for user inputs
st.title("Retirement Savings Model")

# Create two columns for the inputs
col1, col2 = st.columns(2)

# Input fields in the first column
with col1:
    current_investments = float(st.number_input("Current Investments ($)", min_value=0, value=5000000))
    annual_return = st.number_input("Annual Investment Return (%)", min_value=0.0, value=5.0)
    monthly_spend = float(st.number_input("Monthly Spend ($)", min_value=0, value=10000))

# Input fields in the second column
with col2:
    annual_inflation = st.number_input("Annual Inflation Rate (%)", min_value=0.0, value=2.0)
    retirement_year = st.number_input("Year of Retirement", min_value=2025, value=2055)

# Set the time range for projections (50 years)
years = list(range(2025, 2075))

# Algorithm for calculating savings each year
savings_by_year = []
spend_by_year = []
returns_by_year = []
savings = current_investments
returns = 0.0  # Initialize returns as a float

for year in years:
    # Calculate the return on investments
    savings *= (1 + annual_return / 100)
    returns = savings * annual_return / 100
    
    # Adjust monthly spend for inflation
    adjusted_spend = monthly_spend * 12 * (1 + annual_inflation / 100) ** (year - 2025)
    
    # Subtract the adjusted spend from savings
    savings -= adjusted_spend
    
    # Save the calculated savings for this year
    savings_by_year.append(savings)
    spend_by_year.append(adjusted_spend)
    returns_by_year.append(returns)

# Convert savings to millions and returns to thousands for easier visualization
savings_in_millions = [f"{savings / 1_000_000:.2f}" for savings in savings_by_year]
returns_in_thousands = [f"{returns / 1_000:.2f}" for returns in returns_by_year]
spend_in_thousands = [f"{adjusted_spend / 1_000:.2f}" for adjusted_spend in spend_by_year]
savings_plot = [round(savings / 1_000_000, 2) for savings in savings_by_year]

# Create a DataFrame for displaying savings over time
df_savings = pd.DataFrame({
    "Year": years,
    "Savings ($)": savings_plot,
    "Savings ($M)": savings_in_millions,
    "Spend ($K)": spend_in_thousands,
    "Returns ($K)": returns_in_thousands
})


tab1, tab2 = st.tabs(["📊 Graph", "📋 Data"])
with tab1:
    fig, ax = plt.subplots()
    ax.plot(df_savings["Year"], df_savings["Savings ($)"], marker='o')
    ax.set_title("Retirement Savings Projection")
    ax.set_xlabel("Year")
    ax.set_ylabel("Savings ($M)")
    ax.grid(True)
    st.pyplot(fig)
with tab2:
    st.dataframe(df_savings)

## Create two columns for the graph and table (2/3 width for graph, 1/3 for table)
col3, col4 = st.columns([2, 1])

# Plot the savings over time in the first column (2/3 width)
with col3:
    fig, ax = plt.subplots()
    ax.plot(df_savings["Year"], df_savings["Savings ($)"], marker='o')
    ax.set_title("Retirement Savings Projection")
    ax.set_xlabel("Year")
    ax.set_ylabel("Savings ($M)")
    ax.grid(True)
    st.pyplot(fig)

# Display the savings table in the second column (1/3 width)
with col4:
    st.write(df_savings)

