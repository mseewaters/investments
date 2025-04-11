# --- Custom CSS for enhanced styling ---
def load_enhanced_css():
    """Load custom CSS for enhanced UI appearance"""
    st.markdown("""
    <style>
        /* Overall sidebar styling */
        .sidebar-content {
            background-color: #f8f9fa;
        }
        
        /* Section headers */
        .section-header {
            color: #0c4b33;
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 0.5rem;
        }
        
        /* Sub-section headers */
        .subsection-header {
            color: #155724;
            font-weight: 500;
            font-size: 0.95rem;
            margin: 0.7rem 0;
            padding-top: 0.5rem;
        }
        
        /* Help text and captions */
        .help-text {
            color: #6c757d;
            font-size: 0.8rem;
            font-style: italic;
            margin-top: 0.3rem;
        }
        
        /* Input field styling (via streamlit elements) */
        div[data-testid="stNumberInput"] label {
            font-size: 0.9rem;
            color: #495057;
        }
        
        div[data-testid="stNumberInput"] input {
            border-radius: 5px;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            font-weight: 600;
            color: #2c3e50;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        
        .streamlit-expanderContent {
            border-left: 1px solid #e9ecef;
            padding-left: 1rem;
        }
        
        /* Button styling */
        .stButton button {
            border-radius: 5px;
            font-weight: 500;
            transition: all 0.2s ease;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        }
        
        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.1);
        }
        
        /* Input labels */
        div[data-testid="stForm"] label {
            font-weight: 500;
        }
        
        /* Data ID display */
        .data-id-display {
            background-color: #e9f7ef;
            padding: 0.5rem;
            border-radius: 5px;
            font-family: monospace;
            margin-bottom: 1rem;
            border-left: 3px solid #28a745;
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 2.5rem;
            white-space: pre-wrap;
            background-color: #f8f9fa;
            border-radius: 4px 4px 0 0;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }

        .stTabs [aria-selected="true"] {
            background-color: #e9ecef;
            border-radius: 4px 4px 0 0;
            border-right: 1px solid #dee2e6;
            border-left: 1px solid #dee2e6;
            border-top: 2px solid #28a745;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Improved Sidebar UI Components ---
def render_sidebar_ui():
    """Render the entire sidebar UI with all input sections"""
    
    # Load enhanced CSS
    load_enhanced_css()
    
    st.sidebar.markdown('<div class="section-header">📊 Retirement Calculator</div>', unsafe_allow_html=True)
    
    # Data management should be prominent, not in an expander
    render_data_management_ui()
    
    st.sidebar.markdown('<div class="section-header">📝 Your Financial Profile</div>', unsafe_allow_html=True)
    
    # Render each section of the sidebar
    render_income_section()
    render_spending_section()
    render_timing_section()
    render_portfolio_section()
    render_rates_section()

def render_income_section():
    """Render the income section with improved styling"""
    with st.sidebar.expander("💰 Monthly Income", expanded=False):
        st.markdown('<div class="subsection-header">Primary Earner</div>', unsafe_allow_html=True)
        
        # Use columns for more compact layout
        col1, col2 = st.columns([3, 2])
        with col1:
            st.number_input("Pre-Retirement Savings", 
                           key="current_contribution_self", 
                           step=1000,
                           help="Monthly amount saved before retirement")
        with col2:
            st.markdown('<div class="help-text">$/month</div>', unsafe_allow_html=True)
            
        col1, col2 = st.columns([3, 2])
        with col1:
            st.number_input("Pension/Annuity", 
                           key="retire_income_self", 
                           step=1000,
                           help="Monthly pension or annuity income during retirement")
        with col2:
            st.markdown('<div class="help-text">$/month</div>', unsafe_allow_html=True)
            
        col1, col2 = st.columns([3, 2])
        with col1:
            st.number_input("Social Security", 
                           key="socsec_income_self", 
                           step=1000,
                           help="Expected monthly Social Security benefit")
        with col2:
            st.markdown('<div class="help-text">$/month</div>', unsafe_allow_html=True)

        st.markdown('<div class="subsection-header">Spouse/Partner</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.number_input("Pre-Retirement Savings", 
                           key="current_contribution_spouse", 
                           step=1000,
                           help="Monthly amount saved before retirement")
        with col2:
            st.markdown('<div class="help-text">$/month</div>', unsafe_allow_html=True)
            
        col1, col2 = st.columns([3, 2])
        with col1:
            st.number_input("Pension/Annuity", 
                           key="retire_income_spouse", 
                           step=1000,
                           help="Monthly pension or annuity income during retirement")
        with col2:
            st.markdown('<div class="help-text">$/month</div>', unsafe_allow_html=True)
            
        col1, col2 = st.columns([3, 2])
        with col1:
            st.number_input("Social Security", 
                           key="socsec_income_spouse", 
                           step=1000,
                           help="Expected monthly Social Security benefit")
        with col2:
            st.markdown('<div class="help-text">$/month</div>', unsafe_allow_html=True)

def render_spending_section():
    """Render the spending section with improved styling"""
    with st.sidebar.expander("💳 Monthly Expenses", expanded=False):
        st.markdown('<div class="subsection-header">Retirement Expenses</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.number_input("Essential Expenses", 
                           key="retire_need_spend", 
                           step=1000,
                           help="Monthly essential expenses like housing, food, healthcare")
        with col2:
            st.markdown('<div class="help-text">$/month</div>', unsafe_allow_html=True)
            
        col1, col2 = st.columns([3, 2])
        with col1:
            st.number_input("Discretionary Spending", 
                           key="retire_luxury_spend", 
                           step=1000,
                           help="Optional spending for travel, dining out, etc. (only when market performs well)")
        with col2:
            st.markdown('<div class="help-text">$/month</div>', unsafe_allow_html=True)
            
        st.markdown('<div class="subsection-header">Late Retirement Care</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.number_input("Assisted Living", 
                           key="retire_assisted", 
                           step=1000,
                           help="Monthly cost for assisted living or long-term care")
        with col2:
            st.markdown('<div class="help-text">$/month</div>', unsafe_allow_html=True)

def render_timing_section():
    """Render the timing section with improved styling"""
    with st.sidebar.expander("📅 Key Dates & Ages", expanded=False):
        # Self timing inputs
        st.markdown('<div class="subsection-header">Primary Earner</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.date_input("Date of Birth", 
                         key="birthday_self", 
                         min_value=min_birthdate, 
                         max_value=today_date,
                         help="Your date of birth")
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.date_input("Retirement Date", 
                         key="retire_date_self", 
                         min_value=min_retiredate, 
                         max_value=max_retire_date_self,
                         help="When you plan to stop working")
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.date_input("Pension Start Date", 
                         key="pension_date_self", 
                         min_value=min_retiredate, 
                         max_value=max_retire_date_self,
                         help="When pension or distributions begin")
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.date_input("Social Security Start", 
                         key="socsec_date_self", 
                         min_value=min_retiredate, 
                         max_value=max_retire_date_self,
                         help="When you'll begin taking Social Security")
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Assisted Living Age", 
                           key="assisted_age_self", 
                           step=1,
                           help="Age when you anticipate needing assisted living")
        with col2:
            st.number_input("Life Expectancy", 
                           key="life_expectancy_self", 
                           step=1,
                           help="Your estimated life expectancy")

        # Spouse timing inputs
        st.markdown('<div class="subsection-header">Spouse/Partner</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.date_input("Date of Birth", 
                         key="birthday_spouse", 
                         min_value=min_birthdate, 
                         max_value=today_date,
                         help="Your spouse's date of birth")
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.date_input("Retirement Date", 
                         key="retire_date_spouse", 
                         min_value=min_retiredate, 
                         max_value=max_retire_date_spouse,
                         help="When your spouse plans to stop working")
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.date_input("Pension Start Date", 
                         key="pension_date_spouse", 
                         min_value=min_retiredate, 
                         max_value=max_retire_date_spouse,
                         help="When spouse's pension or distributions begin")
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.date_input("Social Security Start", 
                         key="socsec_date_spouse", 
                         min_value=min_retiredate, 
                         max_value=max_retire_date_spouse,
                         help="When your spouse will begin taking Social Security")
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Assisted Living Age", 
                           key="assisted_age_spouse", 
                           step=1,
                           help="Age when spouse may need assisted living")
        with col2:
            st.number_input("Life Expectancy", 
                           key="life_expectancy_spouse", 
                           step=1,
                           help="Spouse's estimated life expectancy")
        
        st.markdown('<div class="help-text">Use 2020/01/01 for dates in the past</div>', unsafe_allow_html=True)

def render_portfolio_section():
    """Render the portfolio section with improved styling"""
    with st.sidebar.expander("📈 Investment Portfolio", expanded=False):
        st.markdown('<div class="subsection-header">Current Assets</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.number_input("Cash Reserves", 
                           key="current_cash", 
                           step=1000,
                           help="Emergency fund and short-term cash needs")
        with col2:
            st.markdown('<div class="help-text">$</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])    
        with col1:
            st.number_input("Target Cash Balance", 
                           key="cash_set_point", 
                           step=1000,
                           help="Desired minimum cash balance to maintain")
        with col2:
            st.markdown('<div class="help-text">$</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.number_input("Investment Portfolio", 
                           key="current_investment", 
                           step=1000,
                           help="Current value of investment accounts (401k, IRA, etc.)")
        with col2:
            st.markdown('<div class="help-text">$</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="subsection-header">Asset Allocation</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.number_input("Pre-Retirement Stocks", 
                          key="stock_allocation_pre_retirement", 
                          step=10, 
                          min_value=0, 
                          max_value=100,
                          help="Percentage of portfolio in stocks before retirement")
        with col2:
            st.markdown('<div class="help-text">%</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.number_input("Post-Retirement Stocks", 
                          key="stock_allocation_post_retirement", 
                          step=10, 
                          min_value=0, 
                          max_value=100,
                          help="Percentage of portfolio in stocks after retirement")
        with col2:
            st.markdown('<div class="help-text">%</div>', unsafe_allow_html=True)

def render_rates_section():
    """Render the rates section with improved styling"""
    # Hide selectbox label visually
    st.markdown("<style>div[data-testid='stSelectbox'] label {display: none;}</style>", unsafe_allow_html=True)
    
    with st.sidebar.expander("📊 Market Assumptions", expanded=False):
        st.markdown('<div class="subsection-header">Projection Mode</div>', unsafe_allow_html=True)
        
        rate_mode = st.selectbox(
            " ", 
            ["User Input", "Historical", "Simulation"], 
            index=2, 
            key="rate_mode",
            help="Choose how to model future returns"
        )

        if rate_mode == "User Input":
            st.markdown('<div class="subsection-header">Custom Rate Inputs</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 2])
            with col1:
                st.number_input("Inflation Rate", 
                              key="inflation", 
                              step=0.1, 
                              min_value=0.1, 
                              max_value=10.0,
                              help="Annual inflation rate")
            with col2:
                st.markdown('<div class="help-text">% per year</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 2])
            with col1:
                st.number_input("Cash Return", 
                              key="return_cash", 
                              step=0.1, 
                              min_value=0.1, 
                              max_value=10.0,
                              help="Expected return on cash/money market")
            with col2:
                st.markdown('<div class="help-text">% per year</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 2])
            with col1:
                st.number_input("Stock Return", 
                              key="return_stock", 
                              step=0.1, 
                              min_value=0.1, 
                              max_value=15.0,
                              help="Expected return on stocks")
            with col2:
                st.markdown('<div class="help-text">% per year</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 2])
            with col1:
                st.number_input("Bond Return", 
                              key="return_bond", 
                              step=0.1, 
                              min_value=0.1, 
                              max_value=15.0,
                              help="Expected return on bonds")
            with col2:
                st.markdown('<div class="help-text">% per year</div>', unsafe_allow_html=True)
        else:
            if rate_mode == "Historical":
                info_text = "Uses long-term historical average returns from 1928-2024"
            else:  # Simulation
                info_text = "Runs 100 scenarios using randomly sampled historical returns"
                
            st.markdown(f'<div class="help-text">{info_text}</div>', unsafe_allow_html=True)

# --- Enhanced Data Management UI ---
def render_data_management_ui():
    """Render the data management UI with improved styling"""
    # Check if user has a stored ID
    has_user_id = 'user_id' in st.session_state and st.session_state['user_id']
    
    if has_user_id:
        # RETURNING USER EXPERIENCE
        st.sidebar.markdown('<div class="subsection-header">Your Saved Profile</div>', unsafe_allow_html=True)
        st.sidebar.markdown(f'<div class="data-id-display">{st.session_state["user_id"]}</div>', unsafe_allow_html=True)
        
        # Password field
        password = st.sidebar.text_input(
            "Your Password", 
            type="password",
            help="Enter your password to save or load data"
        )
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            save_btn = st.button("💾 Save Data", type="primary", use_container_width=True)
            if save_btn:
                if not password:
                    st.sidebar.error("Please enter your password")
                else:
                    if save_state_to_s3(st.session_state['user_id'], password):
                        st.sidebar.success("Data saved successfully!")
        
        with col2:
            load_btn = st.button("🔄 Load Data", use_container_width=True)
            if load_btn:
                if not password:
                    st.sidebar.error("Please enter your password")
                else:
                    if load_state_from_s3(st.session_state['user_id'], password):
                        st.sidebar.success("Data loaded successfully!")
        
        st.sidebar.markdown('<div class="help-text">Keep your Data ID safe to access your profile in the future</div>', unsafe_allow_html=True)
        st.sidebar.divider()
    
    else:
        # FIRST-TIME USER EXPERIENCE
        st.sidebar.markdown('<div class="subsection-header">Save Your Progress</div>', unsafe_allow_html=True)
        
        # Use tabs for clear navigation
        tab1, tab2 = st.sidebar.tabs(["📝 New Profile", "📂 Load Profile"])
        
        with tab1:
            st.markdown('<div class="help-text">Create a new profile to save your data</div>', unsafe_allow_html=True)
            
            password = st.text_input(
                "Create a Password", 
                type="password",
                key="new_password",
                help="This password will encrypt your data"
            )
            
            if st.button("🆕 Create New Profile", type="primary", use_container_width=True):
                if not password:
                    st.error("Please enter a password")
                else:
                    new_user_id = str(uuid.uuid4())
                    if save_state_to_s3(new_user_id, password):
                        st.success(f"Profile created successfully!")
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
            st.markdown('<div class="help-text">Have a profile already? Load it here</div>', unsafe_allow_html=True)
            
            existing_id = st.text_input(
                "Your Data ID",
                help="Enter the Data ID from your previous session"
            )
            
            password = st.text_input(
                "Your Password", 
                type="password",
                key="existing_password",
                help="The password you used previously"
            )
            
            if st.button("📂 Load My Data", use_container_width=True):
                if not existing_id:
                    st.error("Please enter your Data ID")
                elif not password:
                    st.error("Please enter your password")
                else:
                    if load_state_from_s3(existing_id, password):
                        st.success("Data loaded successfully!")
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