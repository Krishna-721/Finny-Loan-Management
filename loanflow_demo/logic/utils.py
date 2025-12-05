import datetime
import html
import re
import streamlit as st

def calculate_emi(principal, rate_annual, tenure_months):
    rate_monthly = rate_annual / (12 * 100)
    if rate_monthly == 0:
        return principal / tenure_months
    emi = principal * rate_monthly * ((1 + rate_monthly)**tenure_months) / (((1 + rate_monthly)**tenure_months) - 1)
    return emi

def sanitize_input(text):
    if isinstance(text, str):
        safe_text = html.escape(text)
        safe_text = re.sub(r"['\";]", "", safe_text)
        return safe_text
    return text

def redact_pii(text):
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '[REDACTED_EMAIL]', str(text))
    text = re.sub(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', '[REDACTED_PAN]', text)
    text = re.sub(r'\d{10}', '[REDACTED_PHONE]', text)
    return text

def secure_log(action):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean_action = redact_pii(action)
    st.session_state.logs.append(f"[{timestamp}] {clean_action}")

def render_header():
    st.markdown(f"""
    <div style='text-align: center; padding: 40px 0 20px 0;' class='fade-in'>
        <h1 class='gradient-text' style='font-size: 3.5rem; margin: 0; font-weight: 900;'>
            🏦 Finny - Loan Assistance Agent
        </h1>
        <p style='font-size: 1.1rem; opacity: 0.7;'>Loan Management System</p>
        <div style='margin-top: 15px;'>
            <span style='background: rgba(139, 92, 246, 0.2); padding: 6px 16px; border-radius: 20px; 
                         font-size: 0.85rem; color: #8b5cf6;'>
                Application ID: <strong>{st.session_state.application_id}</strong>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_stepper():
    steps = ["1. Details", "2. Documents", "3. Review", "4. Decision"]
    current = st.session_state.step
    html_code = '<div class="stepper-container">'
    for i, step_name in enumerate(steps, 1):
        status = "active" if i == current else ("completed" if i < current else "")
        html_code += f'<div class="step {status}">{step_name}</div>'
    html_code += '</div>'
    st.markdown(html_code, unsafe_allow_html=True)

def render_applicant_summary():
    data = st.session_state.app_data
    status_map = {1: ("Draft", "#6B7280"), 2: ("In Progress", "#F59E0B"), 3: ("Under Review", "#3B82F6"), 4: ("Processed", "#10B981")}
    status, color = status_map.get(st.session_state.step, ("Unknown", "#6B7280"))
    
    if st.session_state.step == 4 and st.session_state.underwriting_result:
        status = "Approved ✓" if st.session_state.underwriting_result['eligible'] else "Rejected ✗"
        color = "#10B981" if st.session_state.underwriting_result['eligible'] else "#EF4444"
    
    progress = (st.session_state.step / 4) * 100
    
    st.markdown(f"""
    <div class="fintech-card fade-in glow" style="padding: 24px; margin-bottom: 30px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
            <div>
                <div style="font-size: 0.75rem; opacity: 0.6;">Applicant</div>
                <div style="font-weight: 700; font-size: 1.3rem;">{data['name'] or "Guest User"}</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 0.75rem; opacity: 0.6;">Loan Amount</div>
                <div style="font-weight: 700; font-size: 1.3rem; background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
                           -webkit-background-clip: text; -webkit-text-fill-color: transparent;">₹{data['loan_amount']:,}</div>
            </div>
            <div style="background: {color}; color: white; padding: 10px 24px; border-radius: 25px; font-size: 0.85rem; font-weight: 700;">{status}</div>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress}%;"></div>
        </div>
        <div style="font-size: 0.75rem; opacity: 0.6; margin-top: 8px; text-align: center;">Progress: {int(progress)}%</div>
    </div>
    """, unsafe_allow_html=True)