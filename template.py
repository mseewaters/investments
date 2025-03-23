import streamlit as st
import pandas as pd
import json
from streamlit_option_menu import option_menu

# Page config
st.set_page_config(page_title="Retirement", layout="wide")

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


# --- Backend Calculation Function ---
def calculate_growth(investment, monthly_contribution, years, rate):
    months = years * 12
    values = []
    total = investment
    for m in range(months):
        total *= (1 + rate / 12)
        total += monthly_contribution
        values.append(total)
    dates = pd.date_range(start="2025-01-01", periods=months, freq='ME')
    return pd.Series(values, index=dates)

# --- Streamlit App ---
st.title("Simple Investment Growth Model")

# Define all variables with default values
if "initial_investment" not in st.session_state:
    st.session_state.initial_investment = 10000
    st.session_state.monthly_contribution = 500
    st.session_state.projection_years = 30
    st.session_state.investment_return = 0.05

# --- Simulated tabs with sidebar selectbox ---
with st.sidebar:
    selected = option_menu(None, ["Home", "Upload",  "Tasks", 'Settings'], 
        icons=['house', 'airplane', "list-task", 'gear'], 
        menu_icon="cast", default_index=0, orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "10px"}, 
            "nav-link": {"font-size": "10px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "green"},
        }
    )
    selected
    
tab = st.sidebar.radio("Choose Input Group", ["💵 Income & Savings", "🧾 Spending & Retirement"])

# --- Sidebar with Expanders ---
if selected == "Home":
    with st.sidebar.expander("Savings ", expanded=True, icon="🔥"):
        st.number_input("Initial Investment ($)", key="initial_investment")
        st.number_input("Monthly Contribution ($)", key="monthly_contribution")

    with st.sidebar.expander("💼 Income"):
        st.slider("Years to Model", 1, 50, st.session_state.projection_years, key="projection_years")
        st.slider("Investment Return (%)", 0.0, 15.0, st.session_state.investment_return * 100, key="return_slider")

        st.session_state.investment_return = st.session_state.return_slider / 100

elif selected == "Upload":
    with st.sidebar.expander("🧾 Spending"):
        retirement_spend = st.number_input("Monthly Retirement Spending ($)", value=4000)
        inflation_rate = st.slider("Inflation Rate (%)", 0.0, 10.0, 2.5)

    with st.sidebar.expander("🏖️ Retirement"):
        current_age = st.number_input("Current Age", value=40)
        retirement_age = st.number_input("Planned Retirement Age", value=65)
        investment_return = st.slider("Expected Annual Return (%)", 0.0, 15.0, 6.0) / 100
        projection_years = st.slider("Years to Model", 1, 50, 30)

# Backend calculation
growth = calculate_growth(
    st.session_state.initial_investment,
    st.session_state.monthly_contribution,
    st.session_state.projection_years,
    st.session_state.investment_return
)

# Plot
tab1, tab2 = st.tabs(["📊 Graph", "📋 Data"])
with tab1:
    st.subheader("Projected Investment Value Over Time ")
    st.line_chart(growth)
with tab2:
    st.subheader("Data Table")
    st.write(growth)

if st.button("💾 Save Inputs"):
    save_state()
    st.success("Inputs saved!")



