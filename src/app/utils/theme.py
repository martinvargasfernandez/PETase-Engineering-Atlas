"""
Centralized Theme & Visual Identity Utility for PETase Engineering Atlas v3

Provides consistent CSS injections, color semantics, and card styling across all pages.
Palette:
- Background: #0B1220
- Primary Surface: #111827
- Raised Cards: #172033
- Primary Accent (Teal): #14B8A6
- Informational Accent (Sky Blue): #38BDF8
- Attention (Amber): #F59E0B
- Success / Available (Green): #22C55E
- Protected / Error (Red): #EF4444
- Text: #F8FAFC (Primary), #94A3B8 (Secondary)
- Border: #263244
"""

import streamlit as st


def apply_custom_css():
    """Injects centralized CSS styling for modern biotechnology dark aesthetic."""
    st.markdown("""
    <style>
    /* Global App Background */
    .stApp {
        background-color: #0B1220;
        color: #F8FAFC;
    }

    /* Primary Accent Styling for Links & Highlights */
    a {
        color: #14B8A6 !important;
    }

    /* Cards & Containers */
    div[data-testid="stMetric"], .atlas-card {
        background-color: #111827 !important;
        border: 1px solid #263244 !important;
        border-radius: 8px !important;
        padding: 16px !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0B1220 !important;
        border-right: 1px solid #263244 !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #14B8A6 !important;
        color: #0B1220 !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 6px !important;
    }
    .stButton > button:hover {
        background-color: #0D9488 !important;
        color: #FFFFFF !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #111827 !important;
        color: #F8FAFC !important;
        border-radius: 6px !important;
        border: 1px solid #263244 !important;
    }

    /* Dataframe Header */
    .stDataFrame {
        border: 1px solid #263244 !important;
        border-radius: 6px !important;
    }
    </style>
    """, unsafe_allow_html=True)
