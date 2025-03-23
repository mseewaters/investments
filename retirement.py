import streamlit as st
import pandas as pd
import json
import datetime
from streamlit_option_menu import option_menu

# Page config
st.set_page_config(page_title="Retirement Calculator", layout="wide")

# --- Utilities ---
def load_css(file_path):
    with open(file_path,"r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles.css")

def save_state(filename="user_inputs.json"):
    with open(filename, "w") as f:
        json.dump(st.session_state.to_dict(), f)

def load_state(filename="user_inputs.json"):
    try:
        with open(filename, "r") as f:
            saved = json.load(f)
            for k, v in saved.items():
                if k not in st.session_state:
                    st.session_state[k] = v
    except FileNotFoundError:
        pass  # First-time use

load_state()

# Define all variables with default values
if "menu_initialized" not in st.session_state:
    st.session_state.menu_initialized = False

if "menu_selection" not in st.session_state:
    st.session_state.menu_selection = "Income"

if "current_investment" not in st.session_state:
    st.session_state.current_investment = 100000
    st.session_state.current_cash = 100000
    st.session_state.current_contribution_self = 10000
    st.session_state.current_contribution_spouse = 10000
    st.session_state.retire_income_self = 10000
    st.session_state.retire_income_spouse = 10000
    st.session_state.retire_need_spend = 10000
    st.session_state.retire_luxury_spend = 1000
    st.session_state.retire_assisted = 15000
    st.session_state.birthday_self = datetime.date(1972,8,9)
    st.session_state.birthday_spouse = datetime.date(1960,2,22)
    st.session_state.retire_date_self = datetime.date(2020,1,1)
    st.session_state.retire_date_spouse = datetime.date(2020,1,1)
    st.session_state.assisted_age_self = 90
    st.session_state.assisted_age_spouse = 90
    st.session_state.inflation = 0.02
    st.session_state.return_cash = 0.02
    st.session_state.return_investment = 0.08


# --- Streamlit App ---
st.title("Retirement Savings Model")

menu_items = ["Income", "Spend", "Timing", "Rates"]

if not st.session_state.menu_initialized:
    selected = option_menu(None, menu_items, 
        icons=['bank2', 'cash-coin', "calendar-heart", 'percent'], 
        default_index=menu_items.index(st.session_state.menu_selection),
        orientation="horizontal", 
        styles={
            "container": {"padding": "0!important", "background-color": "#28A745", "color": "#F4F4ED"},
            "icon": {"color": "#F4F4ED", "font-size": "12px"}, 
            "nav-item": {"border-right": "1px solid #F4F4ED","padding": "0 0px"},
            "nav-link": {"font-size": "12px", "text-align": "left", "margin":"0px", "--hover-color": "#8B8BAE", "color": "#F4F4ED", "font-weight": "bold"},
            "nav-link-selected": {"background-color": "#093824", "color": "#F4F4ED", "font-weight": "bold"},
        }
    )
    st.session_state.menu_initialized = True
else:
    selected = option_menu(None, menu_items, 
        icons=['bank2', 'cash-coin', "calendar-heart", 'percent'], 
        orientation="horizontal", 
        styles={
            "container": {"padding": "0!important", "background-color": "#28A745", "color": "#F4F4ED"},
            "icon": {"color": "#F4F4ED", "font-size": "12px"}, 
            "nav-item": {"border-right": "1px solid #F4F4ED","padding": "0 0px"},
            "nav-link": {"font-size": "12px", "text-align": "left", "margin":"0px", "--hover-color": "#8B8BAE", "color": "#F4F4ED", "font-weight": "bold"},
            "nav-link-selected": {"background-color": "#093824", "color": "#F4F4ED", "font-weight": "bold"},
        }
    )

# Save selection persistently
st.session_state.menu_selection = selected

if st.session_state.menu_selection == "Income":
    st.sidebar.markdown("<br><b style='color:#093824'>Savings</b><br>", unsafe_allow_html=True)
    st.sidebar.number_input("Current Cash Savings ($)", key="current_cash", step=1000)
    st.sidebar.number_input("Current Investment Savings ($)", key="current_investment", step=1000)
    st.sidebar.markdown("<br><b style='color:#093824'>Monthly Income Self</b><br>", unsafe_allow_html=True)
    st.sidebar.number_input("Current Monthly Contribution ($)", key="current_contribution_self",step=100)
    st.sidebar.number_input("Retirement Income($)", key="retire_income_self",step=100)
    st.sidebar.markdown("<br><b style='color:#093824'>Monthly Income Spouse</b><br>", unsafe_allow_html=True)
    st.sidebar.number_input("Current Monthly Contribution ($)", key="current_contribution_spouse",step=100)
    st.sidebar.number_input("Retirement Income ($)", key="retire_income_spouse",step=100)

elif st.session_state.menu_selection == "Spend":
    st.sidebar.markdown("<br><b style='color:#093824'>Monthly Spending</b><br>", unsafe_allow_html=True)
    st.sidebar.number_input("Retirement Needed Spend ($)", key="retire_need_spend",step=100)
    st.sidebar.number_input("Incremental Luxury Spend ($)", key="retire_luxury_spend",step=100)
    st.sidebar.number_input("Assisted Living Spend ($)", key="retire_assisted",step=100)

elif st.session_state.menu_selection == "Timing":
    st.sidebar.markdown("<br><b style='color:#093824'>Self</b><br>", unsafe_allow_html=True)
    st.sidebar.date_input("Birthday", key="birthday_self")
    st.sidebar.date_input("Retirement Date", key="retire_date_self")
    st.sidebar.number_input("Assisted Living Age", key="assisted_age_self")
    st.sidebar.markdown("<br><b style='color:#093824'>Self</b><br>", unsafe_allow_html=True)
    st.sidebar.date_input("Birthday", key="birthday_spouse")
    st.sidebar.date_input("Retirement Date", key="retire_date_spouse")
    st.sidebar.number_input("Assisted Living Age", key="assisted_age_spouse")

elif st.session_state.menu_selection == "Rates":
    st.sidebar.markdown("<br><b>TBD</b><br>", unsafe_allow_html=True)


