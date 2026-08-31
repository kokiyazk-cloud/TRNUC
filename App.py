import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="TRNUC YouTube Index Explorer",
    page_icon="🏛️",
    layout="wide"
)

# CSS to block text selection/copying, style links, and hide cloud badges
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden !important; display: none !important;}
header {visibility: hidden;}
div[data-testid="stToolbar"] {display: none !important;}
div[data-testid="stDecoration"] {display: none !important;}
/* Completely disable highlighting and copying text inside the table */
table {
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
    -ms-user-select: none !important;
    user-select: none !important;
}
/* Force text wrapping and styling inside table cells */
table td, table th {
    white-space: normal !important;
    word-break: break-word !important;
}
/* Standard practice: Blue and underlined hyperlinks */
table a, table a:link, table a:visited {
    color: #2563eb !important;
    text-decoration: underline !important;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# JavaScript to remove profile preview and other bottom-right icons
hide_icons_script = """
<script>
setTimeout(function() {
    // Remove profile preview avatar
    const profilePreview = document.querySelector('[data-testid="appCreatorAvatar"]');
    if (profilePreview) profilePreview.closest('div').style.display = 'none';
    
    // Remove the share/crown icon button
    const buttons = document.querySelectorAll('button');
    buttons.forEach(btn => {
        if (btn.innerHTML.includes('share') || btn.textContent.includes('Share')) {
            btn.style.display = 'none';
        }
    });
    
    // Remove any remaining footer links to Streamlit/GitHub
    const links = document.querySelectorAll('a[href*="streamlit"]');
    links.forEach(link => link.style.display = 'none');
}, 100);
</script>
"""
st.markdown(hide_icons_script, unsafe_allow_html=True)

st.title("🏛️ TRNUC YouTube Index Explorer")
st.markdown("Search and browse Truth, Reconciliation and National Unity Commission records.")

# ... rest of your code

# 2. Load Data from Local Repository File
@st.cache_data
def load_data():
    df = pd.read_csv('TRNUC_Index.csv')
    
    required_cols = ['SequenceNo', 'DatePres', 'Participant', 'YouTube Link']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing expected column in CSV: '{col}'")
            
    df['YouTube Link'] = df['YouTube Link'].fillna('')
    df['ParsedDate'] = pd.to_datetime(df['DatePres'], errors='coerce')
    
    # Format markdown links cleanly so only the participant text is shown as a link
    def make_clickable(row):
        participant = str(row['Participant'])
        link = str(row['YouTube Link'])
        if link and link.startswith('http'):
            return f"[{participant}]({link})"
        return participant

    df['ParticipantLink'] = df.apply(make_clickable, axis=1)
    return df

try:
    df = load_data()

    # 3. Filter Controls inside a Form with a clear submit button for Mobile
    st.markdown("### 🔍 Filters")
    
    with st.form(key='search_form'):
        search_term = st.text_input("Search by Participant Name", "")
        seq_filter = st.text_input("Filter by Sequence No", "")

        valid_dates = df['ParsedDate'].dropna()
        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
            date_range = st.date_input(
                "Filter by Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        else:
            date_range = None

        submit_button = st.form_submit_button(label="🔍 Apply Search Filters")

    # 4. Apply Filters
    filtered_df = df.copy()

    if search_term:
        filtered_df = filtered_df[filtered_df['Participant'].str.contains(search_term, case=False, na=False)]

    if seq_filter:
        filtered_df = filtered_df[filtered_df['SequenceNo'].astype(str).str.contains(seq_filter, case=False, na=False)]

    if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['ParsedDate'].dt.date >= start_date) & 
            (filtered_df['ParsedDate'].dt.date <= end_date)
        ]

    # 5. Display the Data using st.table (prevents text copying and cell highlighting)
    st.markdown("---")
    st.write(f"**Showing {len(filtered_df)} records**")

    display_df = filtered_df[['SequenceNo', 'DatePres', 'ParticipantLink']].copy()
    display_df.columns = ['Seq', 'Date', 'Participant - Click for YouTube Video']

    st.table(display_df)

except FileNotFoundError:
    st.error("Error: Could not find 'TRNUC_Index.csv' in the local repository directory. Please check file placement.")
except Exception as e:
    st.error(f"Error loading data: {e}")
