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
