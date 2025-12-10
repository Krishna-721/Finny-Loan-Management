# utils.py — FIXED FOR PROTOTYPE

import datetime
import html
import re
import streamlit as st


def calculate_emi(principal, rate_annual, tenure_months):
    rate = rate_annual / (12 * 100)
    if rate == 0:
        return principal / tenure_months
    emi = principal * rate * ((1 + rate)**tenure_months) / (((1 + rate)**tenure_months) - 1)
    return round(emi)


def sanitize_input(text):
    if isinstance(text, str):
        clean = html.escape(text)
        clean = re.sub(r"['\";]", "", clean)
        return clean
    return text


def redact_pii(text):
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL]', str(text))
    text = re.sub(r'[A-Z]{5}[0-9]{4}[A-Z]', '[PAN]', text)
    text = re.sub(r'\d{10}', '[PHONE]', text)
    return text


def secure_log(action):
    if "logs" not in st.session_state:
        st.session_state.logs = []
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.logs.append(f"[{ts}] {redact_pii(action)}")


def render_header():
    """Render the main header for the LoanFlow application"""
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.markdown("### 🏦 **LoanFlow AI** — Your Personal Loan Assistant")
    with col2:
        st.markdown("*Powered by Agents*")
    st.divider()


def get_loan_summary(data):
    """Generate a summary dictionary of loan details"""
    summary = {
        "applicant": data.get("name", "N/A"),
        "pan": data.get("pan", "N/A"),
        "phone": data.get("phone", "N/A"),
        "requested_amount": data.get("loan_amount", 0),
        "tenure_months": data.get("tenure", 12),
        "annual_rate": data.get("rate", 10.5),
        "monthly_salary": data.get("income", 0) / 12,
        "employment_type": data.get("employment", "Salaried"),
        "existing_emis": data.get("existing_emis", 0),
        "credit_score": data.get("credit_score", 0),
        "purpose": data.get("purpose", "Personal")
    }
    return summary


def format_currency(amount):
    """Format amount as Indian currency (₹)"""
    if isinstance(amount, (int, float)):
        return f"₹{amount:,.0f}"
    return str(amount)


def format_percentage(value, decimals=2):
    """Format value as percentage"""
    return f"{value:.{decimals}f}%"

