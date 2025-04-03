import json
import datetime
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Page config
st.set_page_config(page_title="Retirement Calculator", layout="wide")

# --- Utilities ---
def load_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles.css")

@st.cache_data
def load_external_data():
    return pd.read_csv("hist_data.csv")

rate_table = load_external_data()

def save_state(filename="user_inputs.json"):
    def convert(o):
        if isinstance(o, datetime.date):
            return o.isoformat()
        return o

    try:
        with open(filename, "w") as f:
            json.dump({k: convert(v) for k, v in st.session_state.items()}, f, indent=4)
        # st.success("State saved successfully!")  # Feedback for debugging
    except Exception as e:
        st.error(f"Error saving state: {e}")

# Load from saved file each time
def safe_load():
    try:
        with open("user_inputs.json", "r") as f:
            saved = json.load(f)
            for k, v in saved.items():
                if "date" in k or "birthday" in k:
                    v = datetime.date.fromisoformat(v)
                if k not in st.session_state:
                    st.session_state[k] = v
    except:
        pass  # okay to ignore errors silently for now

safe_load()

defaults = {
    "current_investment": 1000000,
    "current_cash": 200000,
    "current_contribution_self": 5000,
    "current_contribution_spouse": 5000,
    "retire_income_self": 4000,
    "retire_income_spouse": 4000,
    "socsec_income_self": 0,
    "socsec_income_spouse": 0,
    "retire_need_spend": 8000,
    "retire_luxury_spend": 1000,
    "retire_assisted": 7000,
    "birthday_self": datetime.date(1980, 1, 1),
    "birthday_spouse": datetime.date(1980, 1, 1),
    "retire_date_self": datetime.date(2045, 1, 1),
    "retire_date_spouse": datetime.date(2045, 1, 1),
    "pension_date_self": datetime.date(2045, 1, 1),
    "pension_date_spouse": datetime.date(2045, 1, 1),
    "socsec_date_self": datetime.date(2045, 1, 1),
    "socsec_date_spouse": datetime.date(2045, 1, 1),
    "assisted_age_self": 90,
    "assisted_age_spouse": 90,
    "life_expectancy_self": 95,
    "life_expectancy_spouse": 95,
    "inflation": 2.0,
    "return_cash": 2.0,
    "return_stock": 11.0,
    "return_bond": 4.5,
    "projection_years": 30,
    "cash_set_point": 50000,
    "stock_allocation_pre_retirement": 80,
    "stock_allocation_post_retirement": 50,
    "rate_mode": "Simulation",
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

today_date = datetime.date.today()
min_birthdate = datetime.date(1925, 1, 1)
min_retiredate = datetime.date(2020, 1, 1)

# Calculate max retirement date based on life expectancy
max_retire_date_self = st.session_state["birthday_self"] + datetime.timedelta(days=365 * st.session_state["life_expectancy_self"])
max_retire_date_spouse = st.session_state["birthday_spouse"] + datetime.timedelta(days=365 * st.session_state["life_expectancy_spouse"])

# --- Convert dates to age
def age_on_date(birthdate, date):
    return (date - birthdate).days // 365

# --- Streamlit App ---
st.title("Retirement Savings Model")

st.sidebar.markdown("<br><b style='color:#061826'>Enter your values below</b><br>", unsafe_allow_html=True)

with st.sidebar.expander("🤑 Income", expanded=False):
    st.markdown("<br><b style='color:#093824'>Monthly Income (Self)</b><br>", unsafe_allow_html=True)
    st.number_input("Savings Before Retirement ($)", value=st.session_state["current_contribution_self"], step=1000, key="current_contribution_self")
    st.number_input("Retirement Income ($)", value=st.session_state["retire_income_self"], step=1000, key="retire_income_self")
    st.number_input("Social Security Income ($)", value=st.session_state["socsec_income_self"], step=1000, key="socsec_income_self")

    st.markdown("<br><b style='color:#093824'>Monthly Income (Spouse)</b><br>", unsafe_allow_html=True)
    st.number_input("Savings Before Retirement ($)", value=st.session_state["current_contribution_spouse"], step=1000, key="current_contribution_spouse")
    st.number_input("Retirement Income ($)", value=st.session_state["retire_income_spouse"], step=1000, key="retire_income_spouse")
    st.number_input("Social Security Income ($)", value=st.session_state["socsec_income_spouse"], step=1000, key="socsec_income_spouse")

with st.sidebar.expander("💳 Spend", expanded=False):
    st.markdown("<br><b style='color:#093824'>Monthly Spending</b><br>", unsafe_allow_html=True)
    st.number_input("Retirement Needed Spend ($)", value=st.session_state["retire_need_spend"], step=1000, key="retire_need_spend")
    st.number_input("Incremental Luxury Spend ($)", value=st.session_state["retire_luxury_spend"], step=1000, key="retire_luxury_spend")
    st.number_input("Assisted Living Spend ($)", value=st.session_state["retire_assisted"], step=1000, key="retire_assisted")


with st.sidebar.expander("📅 Timing", expanded=False):
    st.markdown("<br><b style='color:#093824'>Self</b><br>", unsafe_allow_html=True)
    st.date_input("Birthday", value=st.session_state["birthday_self"], key="birthday_self",min_value=min_birthdate, max_value=today_date)
    st.date_input("Retirement Date", value=st.session_state["retire_date_self"], key="retire_date_self", min_value=min_retiredate, max_value=max_retire_date_self)
    st.date_input("Pension/distribution start date", value=st.session_state["pension_date_self"], key="pension_date_self", min_value=min_retiredate, max_value=max_retire_date_self)
    st.date_input("Social security start date", value=st.session_state["socsec_date_self"], key="socsec_date_self", min_value=min_retiredate, max_value=max_retire_date_self)
    st.number_input("Assisted Living Age", value=st.session_state["assisted_age_self"], key="assisted_age_self", step=1)
    st.number_input("Life Expectancy", value=st.session_state["life_expectancy_self"], key="life_expectancy_self", step=1)

    st.markdown("<br><b style='color:#093824'>Spouse</b><br>", unsafe_allow_html=True)
    st.date_input("Birthday", value=st.session_state["birthday_spouse"], key="birthday_spouse",min_value=min_birthdate, max_value=today_date)
    st.date_input("Retirement Date", value=st.session_state["retire_date_spouse"], key="retire_date_spouse", min_value=min_retiredate, max_value=max_retire_date_spouse)
    st.date_input("Pension/distribution start date", value=st.session_state["pension_date_spouse"], key="pension_date_spouse", min_value=min_retiredate, max_value=max_retire_date_spouse)
    st.date_input("Social security start date", value=st.session_state["socsec_date_spouse"], key="socsec_date_spouse", min_value=min_retiredate, max_value=max_retire_date_spouse)
    st.number_input("Assisted Living Age", value=st.session_state["assisted_age_spouse"], key="assisted_age_spouse", step=1)
    st.number_input("Life Expectancy", value=st.session_state["life_expectancy_spouse"], key="life_expectancy_spouse", step=1)
    
    st.markdown("<br><small style='color:#093824'>Use 2020/01/01 for retirement, pension, and social security dates in the past.</small><br>", unsafe_allow_html=True)

with st.sidebar.expander("💰 Portfolio", expanded=False):
    st.markdown("<br><b style='color:#093824'>Savings</b><br>", unsafe_allow_html=True)
    st.number_input("Current Cash Savings ($)", value=st.session_state["current_cash"], step=1000, key="current_cash")
    st.number_input("Desired Cash On Hand ($)", value=st.session_state["cash_set_point"], step=1000, key="cash_set_point")
    st.number_input("Current Investment Savings ($)", value=st.session_state["current_investment"], step=1000, key="current_investment")
    st.number_input("Stock (vs. bonds) allocation before retirement (%)", value=st.session_state["stock_allocation_pre_retirement"],key="stock_allocation_pre_retirement", step=10, min_value=0, max_value=100)
    st.number_input("Stock (vs. bonds) allocation after retirement (%)", value=st.session_state["stock_allocation_post_retirement"],key="stock_allocation_post_retirement", step=10, min_value=0, max_value=100)

# Hide selectbox label visually
st.markdown("<style>div[data-testid='stSelectbox'] label {display: none;}</style>", unsafe_allow_html=True)

with st.sidebar.expander("📈 Rates", expanded=False):
    st.markdown("<br><b>Enter static values, use historical averages from 1928-2024, or see a simulation using past rates</b><br>", unsafe_allow_html=True)
    rate_mode = st.selectbox(" ", ["User Input","Historical","Simulation"], index=2, key="rate_mode")

    if rate_mode == "User Input":
        st.markdown("<br><b>Static Rate Inputs</b><br>", unsafe_allow_html=True)
        st.number_input("Inflation Rate (%)", value=st.session_state["inflation"], step=0.1, key="inflation", min_value=0.1, max_value=10.0)
        st.number_input("Return on Cash (%)", value=st.session_state["return_cash"], step=0.1, key="return_cash", min_value=0.1, max_value=10.0)
        st.number_input("Return on Stocks (%)", value=st.session_state["return_stock"], step=0.1, key="return_stock", min_value=0.1, max_value=15.0)
        st.number_input("Return on Bonds (%)", value=st.session_state["return_bond"], step=0.1, key="return_bond", min_value=0.1, max_value=15.0)


# --- Calculations ---

# --- Time Setup
# Calculate end date as the latest expected death
end_date_self = st.session_state.birthday_self.replace(year=st.session_state.birthday_self.year + st.session_state.life_expectancy_self)
end_date_spouse = st.session_state.birthday_spouse.replace(year=st.session_state.birthday_spouse.year + st.session_state.life_expectancy_spouse)

final_date = max(end_date_self, end_date_spouse)
months = (final_date.year - datetime.date.today().year) * 12 + (final_date.month - datetime.date.today().month)

dates = np.array([datetime.date.today() + datetime.timedelta(days=30*i) for i in range(months)])

# Initialize rates
r_stock = np.zeros(months)
r_bond = np.zeros(months)
r_cash = np.zeros(months)
r_infl = np.zeros(months)

def run_simulation(mode="Historical",rate_table_sample=None):
    if mode == "Simulation":
        if rate_table_sample is None:
            rate_table_sample = rate_table.sample(n=months, replace=True).reset_index(drop=True)
        r_stock = (1 + rate_table_sample["Stocks"].values) ** (1/12) - 1
        r_bond = (1 + rate_table_sample["Bonds"].values) ** (1/12) - 1
        r_cash = (1 + rate_table_sample["Cash"].values) ** (1/12) - 1
        r_infl = (1 + rate_table_sample["Inflation"].values) ** (1/12) - 1
    elif mode == "User Input":
        r_stock = np.full(months, (1 + st.session_state.return_stock / 100) ** (1/12) - 1)
        r_bond = np.full(months, (1 + st.session_state.return_bond / 100) ** (1/12) - 1)
        r_cash = np.full(months, (1 + st.session_state.return_cash / 100) ** (1/12) - 1)
        r_infl = np.full(months, (1 + st.session_state.inflation / 100) ** (1/12) - 1)
    else:
        geo_mean_annual = np.prod(1 + rate_table["Stocks"]) ** (1 / len(rate_table["Stocks"])) - 1
        r_stock = np.full(months, (1 + geo_mean_annual) ** (1/12) - 1)
        geo_mean_annual = np.prod(1 + rate_table["Bonds"]) ** (1 / len(rate_table["Bonds"])) - 1
        r_bond = np.full(months, (1 + geo_mean_annual) ** (1/12) - 1)
        geo_mean_annual = np.prod(1 + rate_table["Cash"]) ** (1 / len(rate_table["Cash"])) - 1
        r_cash = np.full(months, (1 + geo_mean_annual) ** (1/12) - 1)
        geo_mean_annual = np.prod(1 + rate_table["Inflation"]) ** (1 / len(rate_table["Inflation"])) - 1
        r_infl = np.full(months, (1 + geo_mean_annual) ** (1/12) - 1)

    # --- Initialize arrays
    investment_stock = np.zeros(months)
    investment_bond = np.zeros(months)
    cash = np.zeros(months)
    need_spend = np.full(months, st.session_state.retire_need_spend)
    luxury_spend = np.zeros(months)
    contributions = np.zeros(months)
    retire_income = np.zeros(months)
    assisted_spend = np.zeros(months)
    assisted = np.full(months, st.session_state.retire_assisted)
    age_self_series = np.zeros(months, dtype=int)
    age_spouse_series = np.zeros(months, dtype=int)
    total_income_series = np.zeros(months)
    total_spend_series = np.zeros(months)

    retire_self_idx = np.searchsorted(dates, st.session_state.retire_date_self)
    retire_spouse_idx = np.searchsorted(dates, st.session_state.retire_date_spouse)
    pension_self_idx = np.searchsorted(dates, st.session_state.pension_date_self)
    pension_spouse_idx = np.searchsorted(dates, st.session_state.pension_date_spouse)
    socsec_self_idx = np.searchsorted(dates, st.session_state.socsec_date_self)
    socsec_spouse_idx = np.searchsorted(dates, st.session_state.socsec_date_spouse)


    for i, d in enumerate(dates):
        age_self = age_on_date(st.session_state.birthday_self, d)
        age_self_series[i] = age_self
        age_spouse = age_on_date(st.session_state.birthday_spouse, d)
        age_spouse_series[i] = age_spouse

        if age_self < st.session_state.life_expectancy_self:
            if i < retire_self_idx:
                contributions[i] += st.session_state.current_contribution_self
            if i >= pension_self_idx:
                retire_income[i] += st.session_state.retire_income_self
            if i >= socsec_self_idx:
                retire_income[i] += st.session_state.socsec_income_self

        if age_spouse < st.session_state.life_expectancy_spouse:
            if i < retire_spouse_idx:
                contributions[i] += st.session_state.current_contribution_spouse
            if i >= pension_spouse_idx:
                retire_income[i] += st.session_state.retire_income_spouse
            if i >= socsec_spouse_idx:
                retire_income[i] += st.session_state.socsec_income_spouse


        if age_self >= st.session_state.assisted_age_self and age_self <= st.session_state.life_expectancy_self:
            assisted_spend[i] += assisted[i]
        if age_spouse >= st.session_state.assisted_age_spouse and age_spouse <= st.session_state.life_expectancy_spouse:
            assisted_spend[i] += assisted[i]

        # Update luxury spend monthly based on return vs inflation
        if r_stock[i] > r_infl[i]:
            luxury_spend[i] = st.session_state.retire_luxury_spend
        else:
            luxury_spend[i] = 0

    stock_allocation_pre = st.session_state.stock_allocation_pre_retirement / 100
    stock_allocation_post = st.session_state.stock_allocation_post_retirement / 100

    investment_stock[0] = st.session_state.current_investment * stock_allocation_pre
    investment_bond[0] = st.session_state.current_investment * (1 - stock_allocation_pre)
    cash[0] = st.session_state.current_cash

    for i in range(1, months):
        total_spend = need_spend[i] + luxury_spend[i] + assisted_spend[i]
        total_income = retire_income[i] + contributions[i]

        total_spend_series[i] = total_spend
        total_income_series[i] = total_income

        net = total_income - total_spend
        new_cash = cash[i-1]
        new_stock = investment_stock[i-1]
        new_bond = investment_bond[i-1]

        total_invest = new_stock + new_bond

        if net >= 0:
            new_cash += net
        else:
            cash_used = min(new_cash, -net)
            inv_needed = -net - cash_used
            new_cash -= cash_used
            total_invest = max(0, total_invest - inv_needed)

        if new_cash < st.session_state.cash_set_point and total_invest > 0:
            transfer = min(st.session_state.cash_set_point - new_cash, total_invest)
            new_cash += transfer
            total_invest -= transfer

        # Re-allocate investments based on retirement status
        is_retired = i >= max(retire_self_idx, retire_spouse_idx)
        stock_ratio = stock_allocation_post if is_retired else stock_allocation_pre

        investment_stock[i] = total_invest * stock_ratio * (1 + r_stock[i])
        investment_bond[i] = total_invest * (1 - stock_ratio) * (1 + r_bond[i])
        cash[i] = new_cash * (1 + r_cash[i])

    # --- Adjust all to today's dollars (real dollars)
    discount_factors = 1 / np.cumprod(1 + r_infl)
    investment_stock *= discount_factors
    investment_bond *= discount_factors
    cash *= discount_factors

    total_investment = investment_stock + investment_bond

    return pd.DataFrame({
        "Date": dates,
        "Investment": np.round(total_investment,0),
        "Cash": np.round(cash,0),
        "Total": np.round(total_investment,0) + np.round(cash,0),
        "Spend": np.round(total_spend_series,0),
        "Income": np.round(total_income_series,0),
        "age_self": age_self_series,
        "age_spouse": age_spouse_series,
        "Savings": np.round(contributions,0),
        "Retirement Income": np.round(retire_income,0),
        "Assisted": np.round(assisted_spend,0),
    })

with st.spinner("Running simulations..."):
    if rate_mode == "Simulation":
        results = run_simulation(mode="Historical")
        last_value = results['Total'].iloc[-1]
        
        n_simulations = 100
        all_totals = []
        for _ in range(n_simulations):
            sample = rate_table.sample(n=months, replace=True).reset_index(drop=True)
            sim_result = run_simulation(mode=rate_mode,rate_table_sample=sample)
            all_totals.append(sim_result["Total"].values)

        simulation_df = pd.DataFrame(all_totals).T  # Transpose so rows = months, columns = runs
        simulation_df.insert(0, "Month", sim_result["Date"])  # Add dates as first column
        simulation_df.insert(1, "Historical", results["Total"])  # Add dates as first column
        median_series = simulation_df.iloc[:, 2:].median(axis=1)
        last_value_likely = median_series.iloc[-1]

    else:
        n_simulations = 1
        results = run_simulation(mode=rate_mode)
        last_value = results['Total'].iloc[-1]

def plot_outcome(mode="Historical",results=None):
    if mode == "Simulation":
        p10 = results.iloc[:, 2:].quantile(0.10, axis=1)
        p25 = results.iloc[:, 2:].quantile(0.25, axis=1)
        p75 = results.iloc[:, 2:].quantile(0.75, axis=1)
        p90 = results.iloc[:, 2:].quantile(0.90, axis=1)
        mean = results.iloc[:, 2:].median(axis=1)
        historical = results.iloc[:, 1]
        dates = results["Month"]

        fig, ax = plt.subplots(figsize=(12, 4))

        ax.fill_between(dates, p10 / 1e6, p90 / 1e6, color="lightblue", alpha=0.5, label="10th–90th Percentile")
        ax.fill_between(dates, p25 / 1e6, p75 / 1e6, color="cornflowerblue", alpha=0.5, label="25th–75th Percentile")
        ax.plot(dates, mean / 1e6, color="blue", label="Most Likely Outcome", linewidth=2)
        ax.plot(dates, historical / 1e6, color="red", label="Historical", linewidth=2)
        ax.set_xlabel("Year")
        ax.set_ylabel("Portfolio Value ($M)")
        ax.legend()

    else:
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(results["Date"], results["Total"] / 1e6, color="blue",label="Total Savings", linewidth=2)
        ax.set_xlabel("Date")
        ax.set_ylabel("Balance ($)")
        ax.legend()

    return fig

# Plot
# Tabs for Graph and Data
tab1, tab2 = st.tabs(["📊 Graph", "📋 Data"])

with tab1:

    if rate_mode == "Simulation":
        final_val = f"${last_value_likely/1e6:,.1f}M"
        fig = plot_outcome(mode=rate_mode, results=simulation_df)
    else:
        final_val = f"${last_value/1e6:,.1f}M"
        fig = plot_outcome(mode=rate_mode, results=results)

    st.markdown("#### Projected Portfolio Value")
    st.markdown(f"<div style='font-size: 0.9em; color: #28A745; font-weight: bold'>Expected value at end of life: {final_val}</div>", unsafe_allow_html=True)

    st.caption("All values in today's dollars (inflation adjusted)")

    st.pyplot(fig, use_container_width=True)

    # Metrics and explanatory note
    if rate_mode == "Simulation":
        st.caption(
            "ℹ️ *Most Likely Outcome is typically higher than Historical due to how luxury spend is modeled.* "
            "Luxury spending only occurs when stock returns exceed inflation. In historical mode, this is applied evenly; "
            "in simulation, it's dynamically based on each month's return."
        )      

with tab2:
    if rate_mode == "Simulation":
        st.markdown("**Historical Average Returns (used in simulation baseline):**")
    st.dataframe(results, use_container_width=True)



if st.button("💾 Save Inputs"):
    save_state()
    st.success("Inputs saved!")

save_state()