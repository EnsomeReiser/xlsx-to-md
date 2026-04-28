import streamlit as st

def apply_custom_styles():
    st.markdown(
        """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stHeader"] {
        background: transparent !important;
        color: transparent !important;
    }
    .block-container {
        padding-top: 1.1rem;
        padding-bottom: 1.25rem;
    }
    
    /* Overall Layout Cleanliness */
    [data-testid="stAppViewContainer"] {
        display: flex !important;
        flex-direction: column !important;
    }

    [data-testid="stMain"] {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: rgba(37, 99, 235, 0.28) !important;
        background: linear-gradient(180deg, rgba(240,252,255,0.82), rgba(248,250,255,0.95));
        border-radius: 12px;
        margin-bottom: 1rem;
    }

    /* Action Buttons in Header */
    [data-testid="stColumn"]:nth-child(2) [data-testid="stHorizontalBlock"] {
        justify-content: flex-end !important;
        gap: 0.75rem !important;
        align-items: center !important;
    }

    .stDownloadButton > button, .stButton > button {
        padding: 0.5rem 1.25rem !important;
        height: 2.8rem !important;
        border-radius: 10px !important;
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton > button:hover {
        background-color: #2563eb !important;
        color: white !important;
        border-color: #2563eb !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }

    /* Form Elements Styling */
    [data-baseweb="tag"] { background-color: #2563eb !important; color: white !important; }
    [data-testid="stWidgetLabel"] + div [role="radiogroup"] [data-baseweb="radio"][aria-checked="true"] > div:nth-child(1) {
        background-color: #2563eb !important;
    }
    
    /* Adjust Column Spacing for the Header */
    [data-testid="stColumn"] {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
