import re
from datetime import datetime
import streamlit as st
# ==================== LOAN TYPES ====================
LOAN_TYPES = {
    "Personal": {"base_rate": 12.5, "min_tenure": 6, "max_tenure": 60},
    "Home": {"base_rate": 8.75, "min_tenure": 12, "max_tenure": 240},
    "Education": {"base_rate": 10.5, "min_tenure": 12, "max_tenure": 84},
    "Business": {"base_rate": 15.0, "min_tenure": 12, "max_tenure": 60},
}

def validate_pan(pan):
    return bool(re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", pan.upper())) if pan else False


def get_interest_rate(loan_type, tenure, credit_score, employment="Salaried"):
    base_rate = LOAN_TYPES[loan_type]["base_rate"]
    if employment == "Self-Employed": base_rate += 1.5
    if credit_score >= 750: base_rate -= 0.5
    elif credit_score < 700: base_rate += 1.0
    if tenure >= 60: base_rate -= 0.25
    elif tenure <= 12: base_rate += 0.25
    return round(base_rate, 2)

def log_action(action):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {action}")