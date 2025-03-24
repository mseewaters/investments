# Initialize defaults only if not already in session_state
defaults = {
    "menu_selection": "Income",
    "current_investment": 100000,
    "current_cash": 100000,
    "current_contribution_self": 10000,
    "current_contribution_spouse": 10000,
    "retire_income_self": 10000,
    "retire_income_spouse": 10000,
    "retire_need_spend": 10000,
    "retire_luxury_spend": 1000,
    "retire_assisted": 15000,
    "birthdate_self": datetime.date(1972, 8, 9),
    "birthdate_spouse": datetime.date(1960, 2, 22),
    "retire_date_self": datetime.date(2020, 1, 1),
    "retire_date_spouse": datetime.date(2020, 1, 1),
    "assisted_age_self": 90,
    "assisted_age_spouse": 90,
    "inflation": 0.02,
    "return_cash": 0.02,
    "return_investment": 0.08,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value



menu_items = ["Income", "Spend", "Timing", "Rates"]

# Menu
selected = option_menu(
    None, menu_items,
    icons=['bank2', 'cash-coin', "calendar-heart", 'percent'],
    styles={
        "container": {"padding": "0!important", "background-color": "#28A745", "color": "#F4F4ED"},
        "icon": {"color": "#F4F4ED", "font-size": "12px"},
        "nav-item": {"border-right": "1px solid #F4F4ED", "padding": "0 0px"},
        "nav-link": {"font-size": "12px", "text-align": "left", "margin": "0px", "--hover-color": "#8B8BAE", "color": "#F4F4ED", "font-weight": "bold"},
        "nav-link-selected": {"background-color": "#093824", "color": "#F4F4ED", "font-weight": "bold"},
    }
)

# Update menu selection
if st.session_state.menu_selection != selected:
    st.session_state.menu_selection = selected

# Save state after any input change
save_state()


# Calculations
import numpy as np
import datetime

# --- Inputs
defaults = {
    "current_investment": 100000,
    "current_cash": 100000,
    "current_contribution_self": 10000,
    "current_contribution_spouse": 10000,
    "retire_income_self": 10000,
    "retire_income_spouse": 10000,
    "retire_need_spend": 10000,
    "retire_luxury_spend": 1000,
    "retire_assisted": 15000,
    "birthday_self": datetime.date(1972, 8, 9),
    "birthday_spouse": datetime.date(1960, 2, 22),
    "retire_date_self": datetime.date(2020, 1, 1),
    "retire_date_spouse": datetime.date(2020, 1, 1),
    "assisted_age_self": 90,
    "assisted_age_spouse": 90,
    "inflation": 0.02,
    "return_cash": 0.02,
    "return_investment": 0.08,
    "projection_years": 30,
    "cash_set_point": 5000,
}

# --- Time Setup
months = defaults["projection_years"] * 12
dates = np.array([datetime.date.today() + datetime.timedelta(days=30*i) for i in range(months)])

# --- Monthly Rates
r_invest = (1 + defaults["return_investment"]) ** (1/12) - 1
r_cash = (1 + defaults["return_cash"]) ** (1/12) - 1
r_infl = (1 + defaults["inflation"]) ** (1/12) - 1

# --- Initialize arrays
investment = np.zeros(months)
cash = np.zeros(months)
need_spend = np.full(months, defaults["retire_need_spend"])
luxury_spend = np.zeros(months)
contributions = np.zeros(months)
retire_income = np.zeros(months)
assisted_spend = np.zeros(months)

# --- Time Checks
def age_on_date(birthdate, date):  # age in years
    return (date - birthdate).days // 365

# Compute retirement months
retire_self_idx = np.searchsorted(dates, defaults["retire_date_self"])
retire_spouse_idx = np.searchsorted(dates, defaults["retire_date_spouse"])

# --- Contributions until retirement
contributions[:retire_self_idx] += defaults["current_contribution_self"]
contributions[:retire_spouse_idx] += defaults["current_contribution_spouse"]

# --- Retirement income after retirement
retire_income[retire_self_idx:] += defaults["retire_income_self"]
retire_income[retire_spouse_idx:] += defaults["retire_income_spouse"]

# --- Inflation-adjust need_spend monthly
need_spend = need_spend * (1 + r_infl) ** np.arange(months)

# --- Conditional luxury spend (only when return > inflation + 0.04)
if defaults["return_investment"] > defaults["inflation"] + 0.04:
    luxury_spend = np.full(months, defaults["retire_luxury_spend"]) * (1 + r_infl) ** np.arange(months)

# --- Assisted living spending (once per year after certain age)
for i, d in enumerate(dates):
    age_self = age_on_date(defaults["birthday_self"], d)
    age_spouse = age_on_date(defaults["birthday_spouse"], d)
    if age_self >= defaults["assisted_age_self"] and d.month == 1:
        assisted_spend[i] += defaults["retire_assisted"] * (1 + defaults["inflation"]) ** (age_self - defaults["assisted_age_self"])
    if age_spouse >= defaults["assisted_age_spouse"] and d.month == 1:
        assisted_spend[i] += defaults["retire_assisted"] * (1 + defaults["inflation"]) ** (age_spouse - defaults["assisted_age_spouse"])

# --- Initialize balances
investment[0] = defaults["current_investment"]
cash[0] = defaults["current_cash"]

# --- Simulation loop
for i in range(1, months):
    total_spend = need_spend[i] + luxury_spend[i] + assisted_spend[i]
    total_income = retire_income[i] + contributions[i]

    net = total_income - total_spend

    # Base cash and investment update
    new_cash = cash[i-1]
    new_invest = investment[i-1]

    if net >= 0:
        new_cash += net
    else:
        cash_used = min(new_cash, -net)
        inv_needed = -net - cash_used
        new_cash -= cash_used
        new_invest = max(0, new_invest - inv_needed)

    # Transfer from investment to cash if cash drops below set point
    if new_cash < defaults["cash_set_point"] and new_invest > 0:
        transfer = min(defaults["cash_set_point"] - new_cash, new_invest)
        new_cash += transfer
        new_invest -= transfer

    # Apply growth
    cash[i] = new_cash * (1 + r_cash)
    investment[i] = new_invest * (1 + r_invest)

