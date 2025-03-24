import json
import datetime
import pandas as pd
import streamlit as st

# Page config
st.set_page_config(page_title="Retirement Calculator", layout="wide")

# --- Utilities ---
def load_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles.css")

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

    st.markdown("<br><b style='color:#093824'>Spouse</b><br>", unsafe_allow_html=True)
    st.date_input("Birthday", value=st.session_state["birthday_spouse"], key="birthday_spouse",min_value=min_birthdate, max_value=today_date)
    st.date_input("Retirement Date", value=st.session_state["retire_date_spouse"], key="retire_date_spouse", min_value=min_retiredate, max_value=max_retiredate)
    st.number_input("Assisted Living Age", value=st.session_state["assisted_age_spouse"], key="assisted_age_spouse", step=1)

# Hide selectbox label visually
st.markdown("<style>div[data-testid='stSelectbox'] label {display: none;}</style>", unsafe_allow_html=True)

with st.sidebar.expander("📈 Rates", expanded=False):
    st.markdown("<br><b>Use historical rates or custom fixed rates</b><br>", unsafe_allow_html=True)
    rate_mode = st.selectbox(" ", ["Historical", "Fixed"], key="rate_mode")

    if rate_mode == "Fixed":
        st.markdown("<br><b>Fixed Rate Inputs</b><br>", unsafe_allow_html=True)
    
        st.slider("Inflation Rate (%)", -10.0, 10.0, value=st.session_state["inflation"], step=0.1, key="inflation")
        st.slider("Return on Cash (%)", -10.0, 10.0, value=st.session_state["return_cash"], step=0.1, key="return_cash")
        st.slider("Return on Investment (%)", -25.0, 25.0, value=st.session_state["return_investment"], step=0.1, key="return_investment")
        st.slider("Years to Model", 1, 60, st.session_state.projection_years, key="projection_years")

save_state()
