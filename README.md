streamlit run template.py

sections = {
    "📥 User Inputs": [
        ("st.text_input()", "Single-line text"),
        ("st.number_input()", "Numeric input with min/max"),
        ("st.slider()", "Numeric slider"),
        ("st.selectbox()", "Dropdown menu"),
        ("st.radio()", "Choose one option"),
        ("st.checkbox()", "Boolean toggle"),
        ("st.date_input()", "Pick a date"),
        ("st.file_uploader()", "Upload CSV, image, etc."),
        ("st.color_picker()", "Select a color"),
    ],
    "📊 Output & Display": [
        ("st.write()", "Flexible output (text, data, plots)"),
        ("st.markdown()", "Rich text formatting"),
        ("st.dataframe()", "Interactive table"),
        ("st.table()", "Static table"),
        ("st.line_chart()", "Quick line plot"),
        ("st.bar_chart()", "Quick bar chart"),
        ("st.pyplot()", "Show custom matplotlib chart"),
        ("st.plotly_chart()", "Plotly integration"),
        ("st.metric()", "Show a single number + delta"),
    ],
    "🧱 Layout": [
        ("st.sidebar", "Put widgets in sidebar"),
        ("st.columns()", "Split layout into columns"),
        ("st.expander()", "Collapsible section"),
        ("st.tabs()", "Create tabbed interface"),
        ("st.container()", "Group elements (optional layout)"),
        ("st.empty()", "Placeholder for dynamic updates"),
    ],
    "🔁 Interactivity & State": [
        ("st.button()", "Run action on click"),
        ("st.form()", "Group inputs and submit together"),
        ("st.session_state", "Track variables across interactions"),
        ("@st.cache_data", "Cache data (e.g., expensive calculation)"),
        ("@st.cache_resource", "Cache non-data (e.g., model object)"),
    ],
    "📁 File & Download": [
        ("st.file_uploader()", "Upload files"),
        ("st.download_button()", "Download results, data, etc."),
    ],
    "🛠 Misc": [
        ("st.progress()", "Show progress bar"),
        ("st.spinner()", "Show loading animation"),
        ("st.toast()", "Small notifications (beta)"),
        ("st.exception()", "Show error details"),
        ("st.stop()", "Stop app execution"),
    ],
}