import json
import datetime
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
    "retire_need_spend": 8000,
    "retire_luxury_spend": 1000,
    "retire_assisted": 7000,
    "birthday_self": datetime.date(1972, 8, 9),
    "birthday_spouse": datetime.date(1960, 2, 22),
    "retire_date_self": datetime.date(2037, 9, 1),
    "retire_date_spouse": datetime.date(2020, 1, 1),
    "assisted_age_self": 90,
    "assisted_age_spouse": 90,
    "life_expectancy_self": 95,
    "life_expectancy_spouse": 95,
    "inflation": 2.0,
    "return_cash": 2.0,
    "return_investment": 8.0,
    "projection_years": 30,
    "cash_set_point": 50000,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

today_date = datetime.date.today()
min_birthdate = datetime.date(1950, 1, 1)
min_retiredate = datetime.date(2020, 1, 1)
max_retiredate = datetime.date(2075, 12, 31)

# --- Streamlit App ---
st.title("Retirement Savings Model")

st.sidebar.markdown("<br><b style='color:#061826'>Enter your values below</b><br>", unsafe_allow_html=True)

with st.sidebar.expander("💰 Income", expanded=False):
    st.markdown("<br><b style='color:#093824'>Savings</b><br>", unsafe_allow_html=True)
    st.number_input("Current Cash Savings ($)", value=st.session_state["current_cash"], step=1000, key="current_cash")
    st.number_input("Desired Cash On Hand ($)", value=st.session_state["cash_set_point"], step=1000, key="cash_set_point")
    st.number_input("Current Investment Savings ($)", value=st.session_state["current_investment"], step=1000, key="current_investment")

    st.markdown("<br><b style='color:#093824'>Monthly Income (Self)</b><br>", unsafe_allow_html=True)
    st.number_input("Savings Before Retirement ($)", value=st.session_state["current_contribution_self"], step=100, key="current_contribution_self")
    st.number_input("Retirement Income ($)", value=st.session_state["retire_income_self"], step=100, key="retire_income_self")

    st.markdown("<br><b style='color:#093824'>Monthly Income (Spouse)</b><br>", unsafe_allow_html=True)
    st.number_input("Savings Before Retirement ($)", value=st.session_state["current_contribution_spouse"], step=100, key="current_contribution_spouse")
    st.number_input("Retirement Income ($)", value=st.session_state["retire_income_spouse"], step=100, key="retire_income_spouse")

with st.sidebar.expander("💳 Spend", expanded=False):
    st.markdown("<br><b style='color:#093824'>Monthly Spending</b><br>", unsafe_allow_html=True)
    st.number_input("Retirement Needed Spend ($)", value=st.session_state["retire_need_spend"], step=100, key="retire_need_spend")
    st.number_input("Incremental Luxury Spend ($)", value=st.session_state["retire_luxury_spend"], step=100, key="retire_luxury_spend")
    st.number_input("Assisted Living Spend ($)", value=st.session_state["retire_assisted"], step=100, key="retire_assisted")

with st.sidebar.expander("📅 Timing", expanded=False):
    st.markdown("<br><b style='color:#093824'>Self</b><br>", unsafe_allow_html=True)
    st.date_input("Birthday", value=st.session_state["birthday_self"], key="birthday_self",min_value=min_birthdate, max_value=today_date)
    st.date_input("Retirement Date", value=st.session_state["retire_date_self"], key="retire_date_self", min_value=min_retiredate, max_value=max_retiredate)
    st.number_input("Assisted Living Age", value=st.session_state["assisted_age_self"], key="assisted_age_self", step=1)
    st.number_input("Life Expectancy", value=st.session_state["life_expectancy_self"], key="life_expectancy_self", step=1)

    st.markdown("<br><b style='color:#093824'>Spouse</b><br>", unsafe_allow_html=True)
    st.date_input("Birthday", value=st.session_state["birthday_spouse"], key="birthday_spouse",min_value=min_birthdate, max_value=today_date)
    st.date_input("Retirement Date", value=st.session_state["retire_date_spouse"], key="retire_date_spouse", min_value=min_retiredate, max_value=max_retiredate)
    st.number_input("Assisted Living Age", value=st.session_state["assisted_age_spouse"], key="assisted_age_spouse", step=1)
    st.number_input("Life Expectancy", value=st.session_state["life_expectancy_spouse"], key="life_expectancy_spouse", step=1)

# Hide selectbox label visually
st.markdown("<style>div[data-testid='stSelectbox'] label {display: none;}</style>", unsafe_allow_html=True)

with st.sidebar.expander("📈 Rates", expanded=False):
    st.markdown("<br><b>Use historical rates or custom fixed rates</b><br>", unsafe_allow_html=True)
    rate_mode = st.selectbox(" ", ["Historical", "Fixed", "Simulated"], key="rate_mode")

    if rate_mode == "Fixed":
        st.markdown("<br><b>Fixed Rate Inputs</b><br>", unsafe_allow_html=True)
    
        st.slider("Inflation Rate (%)", 0.0, 5.0, value=st.session_state["inflation"], step=0.1, key="inflation")
        st.slider("Return on Cash (%)", 0.0, 5.0, value=st.session_state["return_cash"], step=0.1, key="return_cash")
        st.slider("Return on Investment (%)", 0.0, 25.0, value=st.session_state["return_investment"], step=0.1, key="return_investment")
        

save_state()

# --- Calculations ---

# --- Time Setup
# Calculate end date as the latest expected death
end_date_self = st.session_state.birthday_self.replace(year=st.session_state.birthday_self.year + st.session_state.life_expectancy_self)
end_date_spouse = st.session_state.birthday_spouse.replace(year=st.session_state.birthday_spouse.year + st.session_state.life_expectancy_spouse)

final_date = max(end_date_self, end_date_spouse)
months = (final_date.year - datetime.date.today().year) * 12 + (final_date.month - datetime.date.today().month)

dates = np.array([datetime.date.today() + datetime.timedelta(days=30*i) for i in range(months)])

# Initialize r_cash to avoid using it before assignment
r_invest = np.zeros(months)
r_cash = np.zeros(months)
r_infl = np.zeros(months)

# --- Monthly Rates
if rate_mode == "Fixed":
    r_invest = np.full(months, (1 + st.session_state.return_investment/100) ** (1/12) - 1)
    r_cash = np.full(months, (1 + st.session_state.return_cash/100) ** (1/12) - 1)
    r_infl = np.full(months, (1 + st.session_state.inflation/100) ** (1/12) - 1)
elif rate_mode == "Historical":
    r_invest = np.full(months, (1 + rate_table["Stocks"].mean()) ** (1/12) - 1)
    r_cash = np.full(months, (1 + rate_table["Cash"].mean()) ** (1/12) - 1)
    r_infl = np.full(months, (1 + rate_table["Inflation"].mean()) ** (1/12) - 1)
elif rate_mode == "Simulated":
    sampled = rate_table.sample(n=months, replace=True).reset_index(drop=True)
    r_invest = (1 + sampled["Stocks"].values) ** (1/12) - 1
    r_cash = (1 + sampled["Cash"].values) ** (1/12) - 1
    r_infl = (1 + sampled["Inflation"].values) ** (1/12) - 1

# --- Initialize arrays
investment = np.zeros(months)
cash = np.zeros(months)
need_spend = np.full(months, st.session_state.retire_need_spend)
luxury_spend = np.zeros(months)
contributions = np.zeros(months)
contrib_self = np.zeros(months)
contrib_spouse = np.zeros(months)
retire_income = np.zeros(months)
assisted_spend = np.zeros(months)
age_self_series = np.zeros(months, dtype=int)
age_spouse_series = np.zeros(months, dtype=int)
total_income_series = np.zeros(months)
total_spend_series = np.zeros(months)

# --- Time Checks
def age_on_date(birthdate, date):
    return (date - birthdate).days // 365

retire_self_idx = np.searchsorted(dates, st.session_state.retire_date_self)
retire_spouse_idx = np.searchsorted(dates, st.session_state.retire_date_spouse)


contrib_self[:retire_self_idx] = st.session_state.current_contribution_self
contrib_spouse[:retire_spouse_idx] = st.session_state.current_contribution_spouse


retire_income[retire_self_idx:] += st.session_state.retire_income_self
retire_income[retire_spouse_idx:] += st.session_state.retire_income_spouse

need_spend = need_spend * np.cumprod(1 + r_infl)

if st.session_state.return_investment > st.session_state.inflation + 0.04:
    luxury_spend = np.full(months, st.session_state.retire_luxury_spend) * np.cumprod(1 + r_infl)

for i, d in enumerate(dates):
    age_self = age_on_date(st.session_state.birthday_self, d)
    age_self_series[i] = age_self
    age_spouse = age_on_date(st.session_state.birthday_spouse, d)
    age_spouse_series[i] = age_spouse

    if age_self > st.session_state.life_expectancy_self:
        contrib_self[i] = 0
        retire_income[i] -= st.session_state.retire_income_self
    if age_spouse > st.session_state.life_expectancy_spouse:
        contrib_spouse[i] = 0
        retire_income[i] -= st.session_state.retire_income_spouse


    if age_self >= st.session_state.assisted_age_self and age_self <= st.session_state.life_expectancy_self:
        assisted_spend[i] += st.session_state.retire_assisted * (1 + st.session_state.inflation/100) ** (age_self - st.session_state.assisted_age_self)
    if age_spouse >= st.session_state.assisted_age_spouse and age_spouse <= st.session_state.life_expectancy_spouse:
        assisted_spend[i] += st.session_state.retire_assisted * (1 + st.session_state.inflation/100) ** (age_spouse - st.session_state.assisted_age_spouse)

contributions = contrib_self + contrib_spouse

investment[0] = st.session_state.current_investment
cash[0] = st.session_state.current_cash

for i in range(1, months):
    total_spend = need_spend[i] + luxury_spend[i] + assisted_spend[i]
    total_income = retire_income[i] + contributions[i]

    total_spend_series[i] = total_spend
    total_income_series[i] = total_income

    net = total_income - total_spend
    new_cash = cash[i-1]
    new_invest = investment[i-1]

    if net >= 0:
        new_cash += net
    else:
        cash_used = min(new_cash, -net)
        inv_needed = -net - cash_used
        new_cash -= cash_used
        new_invest = max(0, new_invest - inv_needed)

    if new_cash < st.session_state.cash_set_point and new_invest > 0:
        transfer = min(st.session_state.cash_set_point - new_cash, new_invest)
        new_cash += transfer
        new_invest -= transfer

    cash[i] = new_cash * (1 + r_cash[i])
    investment[i] = new_invest * (1 + r_invest[i])

results = pd.DataFrame({
    "Date": dates,
    "Investment": np.round(investment,0),
    "Cash": np.round(cash,0),
    "Total": np.round(investment,0) + np.round(cash,0),
    "Spend": np.round(total_spend_series,0),
    "Income": np.round(total_income_series,0),
    "age_self": age_self_series,
    "age_spouse": age_spouse_series,
    "Savings": np.round(contributions,0),
    "Retirement Income": np.round(retire_income,0),
    "Assisted": np.round(assisted_spend,0),
})

# Plot
tab1, tab2 = st.tabs(["📊 Graph", "📋 Data"])
with tab1:
    st.subheader("Projected Investment Value Over Time ")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(results["Date"], results["Total"], label="Total", linewidth=2)
    ax.plot(results["Date"], results["Investment"], label="Investment", linestyle="--")
    ax.plot(results["Date"], results["Cash"], label="Cash", linestyle=":")
    ax.set_xlabel("Date")
    ax.set_ylabel("Balance ($)")
    ax.legend()
    st.pyplot(fig, use_container_width=True)
with tab2:
    st.subheader("Data Table")
    st.write(results)

if st.button("💾 Save Inputs"):
    save_state()
    st.success("Inputs saved!")