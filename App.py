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
/* Target footer specifically */
footer + div {display: none !important;}
div[class*="footer"], 
div[class*="Footer"] {display: none !important;}
/* Catch any remaining elements */
[data-testid="stFooter"], 
[data-testid="footer"] {display: none !important;}
div[class*="viewerBadge"], 
[class*="viewerBadge"], 
footer + div, 
.styles_viewerBadge__1yB5_ {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    height: 0 !important;
    width: 0 !important;
}
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

st.title("🏛️ TRNUC YouTube Index Explorer")
st.markdown("Search and browse Truth, Reconciliation and National Unity Commission records.")

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

    # 3. Filter Controls with heading and button on same line
    col_heading, col_button = st.columns([0.85, 0.15])
    with col_heading:
        st.markdown("### 🔍 Filters")
    
    with st.form(key='search_form'):
        search_term = st.text_input("Search by Participant Name", "")
        
        col1, col2 = st.columns([0.85, 0.15])
        with col2:
            st.form_submit_button(label="Apply Filter")

    # 4. Apply Filters
    filtered_df = df.copy()

    if search_term:
        filtered_df = filtered_df[filtered_df['Participant'].str.contains(search_term, case=False, na=False)]

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
