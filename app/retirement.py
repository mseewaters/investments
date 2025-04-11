import json
import datetime
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import uuid
import base64
import boto3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Page config
st.set_page_config(page_title="Retirement Calculator", layout="wide")

# --- S3 Configuration ---
S3_BUCKET_NAME = "retirement-savings-calculator" 
s3_client = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "us-east-1"))

# --- Encryption Utilities ---
def generate_key_from_password(password, salt=None):
    """Generate a Fernet key from a password and optional salt."""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_data(data, password):
    """Encrypt data using a password."""
    key, salt = generate_key_from_password(password)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(json.dumps(data).encode())
    return encrypted_data, salt

def decrypt_data(encrypted_data, password, salt):
    """Decrypt data using a password and salt."""
    key, _ = generate_key_from_password(password, salt)
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return json.loads(decrypted_data)

# --- Storage Utilities ---
def save_state_to_s3(user_id, password, filename=None):
    """Save state to S3 with encryption."""
    def convert(o):
        if isinstance(o, datetime.date):
            return o.isoformat()
        return o
    
    try:
        # Prepare data
        data = {k: convert(v) for k, v in st.session_state.items() 
                if k not in ['user_id', 'password']}
        
        # Encrypt data
        encrypted_data, salt = encrypt_data(data, password)
        
        # Add metadata
        metadata = {
            'salt': base64.b64encode(salt).decode(),
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # Save to S3
        filename = f"user_data/{user_id}.enc"
            
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=filename,
            Body=encrypted_data,
            Metadata=metadata
        )
        
        # Store user_id in session state
        st.session_state['user_id'] = user_id
        return True
    except Exception as e:
        st.error(f"Error saving state: {e}")
        return False

def load_state_from_s3(user_id, password):
    """Load state from S3 and decrypt."""
    try:
        # Get file from S3
        response = s3_client.get_object(
            Bucket=S3_BUCKET_NAME,
            Key=f"user_data/{user_id}.enc"
        )
        
        # Get encrypted data and metadata
        encrypted_data = response['Body'].read()
        metadata = response['Metadata']
        salt = base64.b64decode(metadata['salt'])
        
        # Decrypt data
        data = decrypt_data(encrypted_data, password, salt)
        
        # Update session state
        for k, v in data.items():
            if "date" in k or "birthday" in k:
                v = datetime.date.fromisoformat(v)
            st.session_state[k] = v
        
        # Store user_id in session state
        st.session_state['user_id'] = user_id
        return True
    except Exception as e:
        st.error(f"Error loading state: {e}")
        return False

# --- Streamlit User Interface for Data Management ---
def render_data_management_ui():
    """Render an improved data management UI component"""
    with st.sidebar.expander("💾 Save & Load Data", expanded=False):
        # Check if user has a stored ID
        has_user_id = 'user_id' in st.session_state and st.session_state['user_id']
        
        if has_user_id:
            # RETURNING USER EXPERIENCE
            st.markdown(f"<b>Your Data ID:</b>", unsafe_allow_html=True)
            st.markdown(f"<div style='background-color:#F4F4ED; padding:8px; border-left:3px solid #28A745; font-family:monospace; font-size:0.8rem; word-break:break-all;'>{st.session_state['user_id']}</div>", unsafe_allow_html=True)
            
            # Password field
            password = st.text_input(
                "Password for encryption", 
                type="password",
                help="Enter your password to save or load data"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 Save Data", use_container_width=True):
                    if not password:
                        st.error("Please enter your password")
                    else:
                        if save_state_to_s3(st.session_state['user_id'], password):
                            st.success("Data saved!")
            
            with col2:
                if st.button("🔄 Load Data", use_container_width=True):
                    if not password:
                        st.error("Please enter your password")
                    else:
                        if load_state_from_s3(st.session_state['user_id'], password):
                            st.success("Data loaded!")
            
            st.markdown("<small>Save your Data ID somewhere secure - you'll need it to access your data on other devices.</small>", unsafe_allow_html=True)
        
        else:
            # FIRST-TIME USER EXPERIENCE - Use tabs for clarity
            tab1, tab2 = st.tabs(["New User", "Returning User"])
            
            with tab1:
                st.markdown("<small>First time? Create a new profile to save your data</small>", unsafe_allow_html=True)
                
                password = st.text_input(
                    "Create a password", 
                    type="password",
                    key="new_password",
                    help="This password will encrypt your data"
                )
                
                if st.button("🆕 Create New Profile", use_container_width=True):
                    if not password:
                        st.error("Please enter a password")
                    else:
                        new_user_id = str(uuid.uuid4())
                        if save_state_to_s3(new_user_id, password):
                            st.success(f"Profile created!")
                            st.session_state['user_id'] = new_user_id
                            # Store in browser
                            st.markdown(
                                f"""
                                <script>
                                    localStorage.setItem('retirementCalculatorUserId', '{new_user_id}');
                                </script>
                                """,
                                unsafe_allow_html=True
                            )
                            st.rerun()
            
            with tab2:
                st.markdown("<small>Have a profile? Enter your Data ID to load it</small>", unsafe_allow_html=True)
                
                existing_id = st.text_input(
                    "Your Data ID",
                    help="Enter your Data ID from a previous session"
                )
                
                password = st.text_input(
                    "Your password", 
                    type="password",
                    key="existing_password",
                    help="The password you used to encrypt your data"
                )
                
                if st.button("📂 Load Existing Data", use_container_width=True):
                    if not existing_id:
                        st.error("Please enter your Data ID")
                    elif not password:
                        st.error("Please enter your password")
                    else:
                        if load_state_from_s3(existing_id, password):
                            st.success("Data loaded!")
                            st.session_state['user_id'] = existing_id
                            # Store in browser
                            st.markdown(
                                f"""
                                <script>
                                    localStorage.setItem('retirementCalculatorUserId', '{existing_id}');
                                </script>
                                """,
                                unsafe_allow_html=True
                            )
                            st.rerun()
                        else:
                            st.error("Failed to load data. Check your ID and password.")


# --- Sidebar UI Components ---
def render_sidebar_ui():
    """Render the entire sidebar UI with all input sections"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("<b style='font-size: 1.3em; color:#061826'>Enter your information below</b>", unsafe_allow_html=True)
    
    # Render each section of the sidebar
    render_income_section()
    render_spending_section()
    render_timing_section()
    render_portfolio_section()
    render_rates_section()


def render_income_section():
    """Render the income section with self/spouse columns"""
    with st.sidebar.expander("🤑 Monthly Income", expanded=False):
        # Header row
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<b style='color:#093824'>Self</b>", unsafe_allow_html=True)
        with col2:
            st.markdown("<b style='color:#093824'>Spouse</b>", unsafe_allow_html=True)
            
        # Pre-retirement savings
        st.markdown("Pre-Retirement Savings ($/mo)", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Savings Self", step=1000, key="current_contribution_self", 
                          help="Monthly amount saved during working years",
                          label_visibility="collapsed")
        with col2:
            st.number_input("Savings Spouse", step=1000, key="current_contribution_spouse",
                          help="Monthly amount saved during working years",
                          label_visibility="collapsed")
            
        # Retirement income  
        st.markdown("Retirement Income ($/mo)", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Retire Inc Self", step=1000, key="retire_income_self",
                          help="Monthly pension or annuity income",
                          label_visibility="collapsed")
        with col2:
            st.number_input("Retire Inc Spouse", step=1000, key="retire_income_spouse",
                          help="Monthly pension or annuity income",
                          label_visibility="collapsed")
            
        # Social Security
        st.markdown("Social Security Income ($/mo)", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("SSI Self", step=1000, key="socsec_income_self",
                          help="Expected monthly Social Security benefit",
                          label_visibility="collapsed")
        with col2:
            st.number_input("SSI Spouse", step=1000, key="socsec_income_spouse",
                          help="Expected monthly Social Security benefit",
                          label_visibility="collapsed")

def render_spending_section():
    """Render the spending section of the sidebar"""
    with st.sidebar.expander("💳 Monthly Spend", expanded=False):

        st.number_input("Retirement Needed Spend ($/mo)", step=1000, key="retire_need_spend",
                    help="Essential monthly expenses in retirement")

        st.number_input("Incremental Luxury Spend ($/mo)", step=1000, key="retire_luxury_spend",
                    help="Optional spending when market performs well")

        st.number_input("Assisted Living Spend ($/mo)", step=1000, key="retire_assisted",
                    help="Monthly assisted living or care costs")


def render_timing_section():
    """Render the timing section of the sidebar"""
    with st.sidebar.expander("📅 Timing", expanded=False):
        st.markdown("<br><b style='color:#093824'>Self</b><br>", unsafe_allow_html=True)
        
        # Self timing inputs
        st.date_input("Birthday", key="birthday_self", min_value=min_birthdate, max_value=today_date, 
                     help="Your date of birth")
        st.date_input("Retirement Date", key="retire_date_self", min_value=min_retiredate, max_value=max_retire_date_self, 
                     help="When you plan to stop working")
        st.date_input("Pension/distribution start date", key="pension_date_self", min_value=min_retiredate, max_value=max_retire_date_self,
                     help="When pension or distributions begin")
        st.date_input("Social security start date", key="socsec_date_self", min_value=min_retiredate, max_value=max_retire_date_self,
                     help="When you'll begin taking Social Security")
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Assisted Living Age", key="assisted_age_self", step=1,
                           help="Age when you might need assisted living")
        with col2:
            st.number_input("Life Expectancy", key="life_expectancy_self", step=1,
                           help="Your estimated life expectancy")

        # Spouse timing inputs
        st.markdown("<br><b style='color:#093824'>Spouse</b><br>", unsafe_allow_html=True)
        
        st.date_input("Birthday", key="birthday_spouse", min_value=min_birthdate, max_value=today_date,
                     help="Your spouse's date of birth")
        st.date_input("Retirement Date", key="retire_date_spouse", min_value=min_retiredate, max_value=max_retire_date_spouse,
                     help="When your spouse plans to retire")
        st.date_input("Pension/distribution start date", key="pension_date_spouse", min_value=min_retiredate, max_value=max_retire_date_spouse,
                     help="When spouse's pension or distributions begin")
        st.date_input("Social security start date", key="socsec_date_spouse", min_value=min_retiredate, max_value=max_retire_date_spouse,
                     help="When your spouse will begin taking Social Security")
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Assisted Living Age", key="assisted_age_spouse", step=1,
                           help="Age when spouse might need assisted living")
        with col2:
            st.number_input("Life Expectancy", key="life_expectancy_spouse", step=1,
                           help="Spouse's estimated life expectancy")
        
        st.markdown("<br><small style='color:#093824'>Use 2020/01/01 for retirement, pension, and social security dates in the past.</small><br>", unsafe_allow_html=True)

def render_portfolio_section():
    """Render the portfolio section of the sidebar"""
    with st.sidebar.expander("💰 Portfolio", expanded=False):
        st.markdown("<br><b style='color:#093824'>Savings</b><br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.number_input("Current Cash Savings", step=1000, key="current_cash",
                           help="Emergency fund and short-term cash needs")
        with col2:
            st.markdown("<div style='padding-top:33px'>$</div>", unsafe_allow_html=True)
            
        col1, col2 = st.columns([4, 1])
        with col1:
            st.number_input("Desired Cash On Hand", step=1000, key="cash_set_point",
                           help="Target minimum cash balance")
        with col2:
            st.markdown("<div style='padding-top:33px'>$</div>", unsafe_allow_html=True)
            
        col1, col2 = st.columns([4, 1])
        with col1:
            st.number_input("Current Investment Savings", step=1000, key="current_investment",
                           help="Current value of investment accounts")
        with col2:
            st.markdown("<div style='padding-top:33px'>$</div>", unsafe_allow_html=True)
            
        col1, col2 = st.columns([4, 1])
        with col1:
            st.number_input("Stock allocation before retirement", key="stock_allocation_pre_retirement", 
                          step=10, min_value=0, max_value=100,
                          help="Percentage of portfolio in stocks before retirement")
        with col2:
            st.markdown("<div style='padding-top:33px'>%</div>", unsafe_allow_html=True)
            
        col1, col2 = st.columns([4, 1])
        with col1:
            st.number_input("Stock allocation after retirement", key="stock_allocation_post_retirement", 
                          step=10, min_value=0, max_value=100,
                          help="Percentage of portfolio in stocks after retirement")
        with col2:
            st.markdown("<div style='padding-top:33px'>%</div>", unsafe_allow_html=True)

def render_rates_section():
    """Render the rates section of the sidebar"""
    # Hide selectbox label visually
    st.markdown("<style>div[data-testid='stSelectbox'] label {display: none;}</style>", unsafe_allow_html=True)
    
    with st.sidebar.expander("📈 Rates", expanded=False):
        st.markdown("<br><b>Enter static values, use historical averages from 1928-2024, or see a simulation using past rates</b><br>", unsafe_allow_html=True)
        
        rate_mode = st.selectbox(" ", ["User Input", "Historical", "Simulation"], 
                               index=2, key="rate_mode",
                               help="Choose how to model future returns")

        if rate_mode == "User Input":
            st.markdown("<br><b>Static Rate Inputs as Annual Average</b><br>", unsafe_allow_html=True)
            
            st.number_input("Inflation Rate (%)", step=0.1, key="inflation",
                               min_value=0.1, max_value=10.0,
                               help="Annual inflation rate")

            st.number_input("Return on Cash (%)", step=0.1, key="return_cash",
                               min_value=0.1, max_value=10.0,
                               help="Expected return on cash/money market")


            st.number_input("Return on Stocks (%)", step=0.1, key="return_stock", 
                               min_value=0.1, max_value=15.0,
                               help="Expected annual return on stocks")
                
            st.number_input("Return on Bonds (%)", step=0.1, key="return_bond", 
                               min_value=0.1, max_value=15.0,
                               help="Expected annual return on bonds")


# --- Utilities ---
def load_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("app/styles.css")

@st.cache_data
def load_external_data():
    return pd.read_csv("app/hist_data.csv")

# Cache rate table from csv file
rate_table = load_external_data()

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
min_retiredate = datetime.date(2000, 1, 1)

# Calculate max retirement date based on life expectancy
max_retire_date_self = st.session_state["birthday_self"] + datetime.timedelta(days=365 * st.session_state["life_expectancy_self"])
max_retire_date_spouse = st.session_state["birthday_spouse"] + datetime.timedelta(days=365 * st.session_state["life_expectancy_spouse"])

# --- Convert dates to age
def age_on_date(birthdate, date):
    return (date - birthdate).days // 365

# --- Streamlit App ---
st.title("Retirement Savings Model")

# Add the data management UI to sidebar
render_data_management_ui()

# Add the sidebar UI to the sidebar 
render_sidebar_ui()

# --- Calculations ---

# --- Time Setup
# Calculate end date as the latest expected death
end_date_self = st.session_state.birthday_self.replace(year=st.session_state.birthday_self.year + st.session_state.life_expectancy_self)
end_date_spouse = st.session_state.birthday_spouse.replace(year=st.session_state.birthday_spouse.year + st.session_state.life_expectancy_spouse)

final_date = max(end_date_self, end_date_spouse)
months = max((final_date.year - datetime.date.today().year) * 12 + (final_date.month - datetime.date.today().month),0)

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
    if st.session_state.rate_mode == "Simulation":
        results = run_simulation(mode="Historical")
        last_value = results['Total'].iloc[-1]
        
        n_simulations = 100
        all_totals = []
        for _ in range(n_simulations):
            sample = rate_table.sample(n=months, replace=True).reset_index(drop=True)
            sim_result = run_simulation(mode=st.session_state.rate_mode,rate_table_sample=sample)
            all_totals.append(sim_result["Total"].values)

        simulation_df = pd.DataFrame(all_totals).T  # Transpose so rows = months, columns = runs
        simulation_df.insert(0, "Month", sim_result["Date"])  # Add dates as first column
        simulation_df.insert(1, "Historical", results["Total"])  # Add dates as first column
        median_series = simulation_df.iloc[:, 2:].median(axis=1)
        last_value_likely = median_series.iloc[-1]

    else:
        n_simulations = 1
        results = run_simulation(mode=st.session_state.rate_mode)
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

        ax.fill_between(dates, p10 / 1e6, p90 / 1e6, color="#8B8BAE", alpha=0.5, label="10th–90th Percentile")
        ax.fill_between(dates, p25 / 1e6, p75 / 1e6, color="#28A745", alpha=0.5, label="25th–75th Percentile")
        ax.plot(dates, mean / 1e6, color="#093824", label="Most Likely Outcome", linewidth=2)
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
tab1, tab2, tab3 = st.tabs(["📊 Graph", "📋 Data", "⚙️ Methodology"])

with tab1:

    if st.session_state.rate_mode == "Simulation":
        final_val = f"${last_value_likely/1e6:,.1f}M"
        fig = plot_outcome(mode=st.session_state.rate_mode, results=simulation_df)
    else:
        final_val = f"${last_value/1e6:,.1f}M"
        fig = plot_outcome(mode=st.session_state.rate_mode, results=results)

    st.markdown("##### Projected Portfolio Value")
    st.markdown(f"<div style='font-size: 0.9em; color: #28A745; font-weight: bold'>Expected value at end of life: {final_val}</div>", unsafe_allow_html=True)

    st.caption("All values in today's dollars (inflation adjusted)")

    st.pyplot(fig, use_container_width=True)

    # Metrics and explanatory note
    if st.session_state.rate_mode == "Simulation":
        st.caption(
            "*Most Likely Outcome is typically higher than Historical due to how luxury spend is modeled.* "
            "Luxury spending only occurs when stock returns exceed inflation. In historical mode, this is applied evenly; "
            "in simulation, it's dynamically based on each month's return."
        )      

with tab2:
    if st.session_state.rate_mode == "Simulation":
        st.markdown("**Historical Average Returns (used in simulation baseline):**")
    st.dataframe(results, use_container_width=True)

with tab3:
    st.markdown("### ⚙️ How the Forecast Is Created")

    st.markdown("""
        This retirement forecast estimates your future finances month by month, starting today and continuing through the end of life for you and your spouse. It considers your income, spending, savings, and how your money might grow or shrink over time.

        ---

        #### 🗓️ 1. We Build a Timeline
        We start by figuring out how long to run the forecast — from today until the end of the longest expected life. Every month between now and then is included in the simulation.

        #### 📈 2. We Estimate Future Growth
        Each month, your investments (like cash, bonds, and stocks) are expected to change in value. These changes can come from:
        - Sampled historical data (to simulate possible futures using 100 runs),
        - Fixed return values you choose,
        - Or long-term average returns.

        We also include inflation — the general rise in prices over time — to keep everything in today’s dollars.

        #### 💰 3. We Track Money In and Out
        Every month, we calculate:
        - **Income**: Money you contribute before retirement, plus pensions and other income after.
        - **Spending**: Monthly needs, luxury spending (if the market does well), and assisted care costs in later years.

        #### 🔁 4. We Update Your Balances
        Each month:
        - Extra income adds to cash.
        - If income isn’t enough, we withdraw from cash and investments.
        - If cash gets too low, we move money from investments.
        - Your investment mix shifts gradually once you're retired.

        #### 🧮 5. We Show Everything in Today’s Dollars
        To make results meaningful, all future amounts are adjusted for inflation so you can understand them in today’s terms.

        #### 📊 6. We Share the Results
        You’ll see:
        - How your money changes over time
        - Your income and spending
        - Age-based costs
        - Whether your savings support your lifestyle

        ---

        This helps you explore different scenarios and make informed choices about your retirement plans.
        """)
