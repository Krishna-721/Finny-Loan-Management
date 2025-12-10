# theme.py — FIXED (minor cleanup)

import streamlit as st

def apply_theme():
    css = """
    <style>
    html, body, .stApp {
        background: linear-gradient(135deg, #0a0e27, #1a1f3a);
        color: #E8EAED;
        font-family: 'Inter', sans-serif;
    }
    
    .fintech-card {
        background: rgba(30, 35, 60, 0.65);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(139,92,246,0.3);
        backdrop-filter: blur(20px);
    }

    div.stButton > button {
        background: linear-gradient(135deg, #8b5cf6, #6366f1);
        color: white;
        border-radius: 10px;
        padding: 12px 24px;
        border: none;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
