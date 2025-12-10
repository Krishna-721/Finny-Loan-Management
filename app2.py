"""
LoanFlow AI - Complete 5-Agent Prototype
Real-world banking process with clear agent orchestration
"""

import streamlit as st
import random
import time
from datetime import datetime
import re

st.set_page_config(
    page_title="LoanFlow AI | 5-Agent System",
    page_icon="🏦",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main { background: linear-gradient(135deg, #0a0e27, #1a1f3a); color: #E8EAED; }
.agent-card {
    background: rgba(30, 35, 60, 0.8);
    border-radius: 12px;
    padding: 20px;
    border-left: 4px solid #6366f1;
    margin: 10px 0;
}
.agent-card.working { border-left-color: #8b5cf6; background: rgba(139, 92, 246, 0.2); animation: pulse 2s infinite; }
.agent-card.complete { border-left-color: #10b981; background: rgba(16, 185, 129, 0.2); }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
.metric-box { background: rgba(139, 92, 246, 0.2); border-radius: 8px; padding: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ==================== MOCK DATA ====================
MOCK_BUREAU_DB = {
    "ABCDE1234F": {"name": "Rajesh Kumar", "credit_score": 735, "existing_emi": 6500, "pre_approved_limit": 500000, "monthly_salary": 80000},
    "PQRSX9988L": {"name": "Priya Sharma", "credit_score": 680, "existing_emi": 4200, "pre_approved_limit": 300000, "monthly_salary": 50000},
    "LMNOP3456Q": {"name": "Sneha Reddy", "credit_score": 790, "existing_emi": 15000, "pre_approved_limit": 800000, "monthly_salary": 120000},
    "WXYZA5678B": {"name": "Amit Singh", "credit_score": 720, "existing_emi": 0, "pre_approved_limit": 800000, "monthly_salary": 90000},
    "GHJKL2345M": {"name": "Neha Gupta", "credit_score": 655, "existing_emi": 3000, "pre_approved_limit": 250000, "monthly_salary": 45000},
    "QWERT1234Y": {"name": "Vamshi Krishna", "credit_score": 720, "existing_emi": 12000, "pre_approved_limit": 1000000, "monthly_salary": 200000},
}

LOAN_TYPES = {
    "Personal": {"base_rate": 12.5, "min_tenure": 6, "max_tenure": 60},
    "Home": {"base_rate": 8.75, "min_tenure": 12, "max_tenure": 240},
    "Education": {"base_rate": 10.5, "min_tenure": 12, "max_tenure": 84},
    "Business": {"base_rate": 15.0, "min_tenure": 12, "max_tenure": 60},
}

# ==================== UTILITY FUNCTIONS ====================
def validate_pan(pan):
    return bool(re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", pan.upper())) if pan else False

def calculate_emi(principal, rate_annual, tenure_months):
    rate = rate_annual / (12 * 100)
    if rate == 0: return principal / tenure_months
    emi = principal * rate * ((1 + rate)**tenure_months) / (((1 + rate)**tenure_months) - 1)
    return round(emi, 2)

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

# ==================== SESSION STATE ====================
if "stage" not in st.session_state:
    st.session_state.stage = "SALES"
    st.session_state.app_data = {"name": "", "pan": "", "loan_type": "Personal", "loan_amount": 0, "tenure": 12, "employment_type": "Salaried"}
    st.session_state.agent_status = {
        "sales": {"status": "idle", "result": None},
        "verification": {"status": "idle", "result": None},
        "underwriting": {"status": "idle", "result": None},
        "document": {"status": "idle", "result": None},
        "sanction": {"status": "idle", "result": None}
    }
    st.session_state.logs = []
    st.session_state.application_id = f"LF{random.randint(10000, 99999)}"

# ==================== AGENT DISPLAY ====================
def render_agent_card(agent_name, icon, status, result=None):
    status_map = {"idle": "⚪", "working": "🔵", "complete": "✅", "error": "❌"}
    status_icon = status_map.get(status, "⚪")
    
    card_class = f"agent-card {status}"
    st.markdown(f"""
    <div class='{card_class}'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div><span style='font-size: 1.5rem;'>{icon}</span> <strong>{agent_name}</strong></div>
            <div style='font-size: 1.5rem;'>{status_icon}</div>
        </div>
        {f"<div style='margin-top: 10px; font-size: 0.9rem; color: #10b981;'>{result}</div>" if result else ""}
    </div>
    """, unsafe_allow_html=True)

# ==================== HEADER ====================
st.markdown("""
<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #8b5cf6, #6366f1); border-radius: 10px; margin-bottom: 30px;'>
    <h1 style='color: white; margin: 0;'>🏦 LoanFlow AI</h1>
    <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0;'>5-Agent Intelligent Loan Processing System</p>
</div>
""", unsafe_allow_html=True)

# Status Bar
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div class='metric-box'><div style='opacity: 0.8;'>Application ID</div><div style='font-size: 1.2rem; font-weight: bold;'>{st.session_state.application_id}</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-box'><div style='opacity: 0.8;'>Current Stage</div><div style='font-size: 1.2rem; font-weight: bold; color: #8b5cf6;'>{st.session_state.stage}</div></div>", unsafe_allow_html=True)
with col3:
    completed = sum(1 for a in st.session_state.agent_status.values() if a["status"] == "complete")
    st.markdown(f"<div class='metric-box'><div style='opacity: 0.8;'>Progress</div><div style='font-size: 1.2rem; font-weight: bold; color: #10b981;'>{completed}/5 Agents</div></div>", unsafe_allow_html=True)

st.divider()

# ==================== AGENT ORCHESTRATION ====================

# Left Column: Agent Status
col_agents, col_main = st.columns([1, 2])

with col_agents:
    st.markdown("### 🤖 Agent Status")
    render_agent_card("Sales Agent", "🤝", st.session_state.agent_status["sales"]["status"], st.session_state.agent_status["sales"]["result"])
    render_agent_card("Verification Agent", "🔍", st.session_state.agent_status["verification"]["status"], st.session_state.agent_status["verification"]["result"])
    render_agent_card("Underwriting Agent", "⚖️", st.session_state.agent_status["underwriting"]["status"], st.session_state.agent_status["underwriting"]["result"])
    render_agent_card("Document Agent", "📄", st.session_state.agent_status["document"]["status"], st.session_state.agent_status["document"]["result"])
    render_agent_card("Sanction Agent", "📋", st.session_state.agent_status["sanction"]["status"], st.session_state.agent_status["sanction"]["result"])

# Right Column: Active Agent Process
with col_main:
    st.markdown("### 📝 Application Process")
    
    # ==================== STAGE 1: SALES AGENT ====================
    if st.session_state.stage == "SALES":
        st.session_state.agent_status["sales"]["status"] = "working"
        log_action("Sales Agent: Collecting customer requirements")
        
        st.markdown("#### 🤝 Sales Agent")
        st.info("I'll help you find the perfect loan. Please provide your details:")
        
        with st.form("sales_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name*", value=st.session_state.app_data["name"])
                loan_type = st.selectbox("Loan Type*", LOAN_TYPES.keys())
                loan_amount = st.number_input("Loan Amount (₹)*", min_value=50000, max_value=10000000, value=500000, step=50000)
            with col2:
                tenure = st.selectbox("Tenure (months)*", range(6, 61, 6))
                employment = st.selectbox("Employment Type*", ["Salaried", "Self-Employed"])
                pan = st.text_input("PAN Number*", placeholder="ABCDE1234F", max_chars=10).upper()
            
            submitted = st.form_submit_button("Submit Application →", use_container_width=True)
            
            if submitted:
                if not all([name, loan_type, loan_amount, tenure, pan]) or not validate_pan(pan):
                    st.error("❌ Please fill all fields correctly (PAN format: ABCDE1234F)")
                else:
                    st.session_state.app_data.update({"name": name, "loan_type": loan_type, "loan_amount": loan_amount, "tenure": tenure, "employment_type": employment, "pan": pan})
                    rate = get_interest_rate(loan_type, tenure, 720, employment)
                    st.session_state.app_data["rate"] = rate
                    st.session_state.agent_status["sales"]["status"] = "complete"
                    st.session_state.agent_status["sales"]["result"] = f"Collected: {name}, {loan_type}, ₹{loan_amount:,} | Rate: {rate}%"
                    log_action(f"Sales Agent: Data collected for {name}")
                    st.session_state.stage = "VERIFICATION"
                    time.sleep(1)
                    st.rerun()
    
    # ==================== STAGE 2: VERIFICATION AGENT ====================
    elif st.session_state.stage == "VERIFICATION":
        st.session_state.agent_status["verification"]["status"] = "working"
        log_action("Verification Agent: Validating PAN and fetching credit profile")
        
        st.markdown("#### 🔍 Verification Agent")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔍 Validating PAN format...")
        time.sleep(1)
        progress_bar.progress(33)
        
        pan = st.session_state.app_data["pan"]
        
        if pan in MOCK_BUREAU_DB:
            bureau_data = MOCK_BUREAU_DB[pan]
            status_text.text("🔍 Fetching credit bureau data...")
            time.sleep(1)
            progress_bar.progress(66)
            
            status_text.text("✅ Verification complete!")
            progress_bar.progress(100)
            time.sleep(0.5)
            
            st.session_state.app_data.update({
                "name": bureau_data["name"],
                "credit_score": bureau_data["credit_score"],
                "existing_emi": bureau_data["existing_emi"],
                "pre_approved_limit": bureau_data["pre_approved_limit"],
                "monthly_salary": bureau_data["monthly_salary"]
            })
            
            st.session_state.agent_status["verification"]["status"] = "complete"
            st.session_state.agent_status["verification"]["result"] = f"Verified: {bureau_data['name']} | CIBIL: {bureau_data['credit_score']}"
            log_action(f"Verification Agent: Verified {bureau_data['name']}, CIBIL: {bureau_data['credit_score']}")
            
            progress_bar.empty()
            status_text.empty()
            
            st.success("✅ Verification Successful!")
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Name", bureau_data["name"])
            with col2: st.metric("CIBIL Score", bureau_data["credit_score"])
            with col3: st.metric("Existing EMI", f"₹{bureau_data['existing_emi']:,}")
            with col4: st.metric("Pre-Approved", f"₹{bureau_data['pre_approved_limit']:,}")
            
            st.session_state.stage = "UNDERWRITING"
            time.sleep(2)
            st.rerun()
        else:
            progress_bar.empty()
            status_text.empty()
            st.session_state.agent_status["verification"]["status"] = "error"
            log_action("Verification Agent: PAN not found")
            st.error("❌ PAN not found. Use test PANs: " + ", ".join(MOCK_BUREAU_DB.keys()))
            if st.button("← Go Back"):
                st.session_state.stage = "SALES"
                st.rerun()
    
    # ==================== STAGE 3: UNDERWRITING AGENT ====================
    elif st.session_state.stage == "UNDERWRITING":
        st.session_state.agent_status["underwriting"]["status"] = "working"
        log_action("Underwriting Agent: Evaluating loan eligibility")
        
        st.markdown("#### ⚖️ Underwriting Agent")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("⚖️ Calculating FOIR...")
        time.sleep(1)
        progress_bar.progress(50)
        
        status_text.text("⚖️ Determining scenario...")
        time.sleep(1)
        progress_bar.progress(100)
        
        data = st.session_state.app_data
        requested = data["loan_amount"]
        pre_approved = data["pre_approved_limit"]
        monthly_salary = data["monthly_salary"]
        credit_score = data["credit_score"]
        existing_emi = data["existing_emi"]
        
        rate = get_interest_rate(data["loan_type"], data["tenure"], credit_score, data["employment_type"])
        emi = calculate_emi(requested, rate, data["tenure"])
        total_emi = emi + existing_emi
        foir = (total_emi / monthly_salary) * 100 if monthly_salary > 0 else 999
        
        if requested <= pre_approved:
            scenario, scenario_label, scenario_icon = "A", "Instant Approval", "✅"
        elif requested <= (2 * pre_approved):
            scenario, scenario_label, scenario_icon = "B", "Conditional Approval", "📄"
        else:
            scenario, scenario_label, scenario_icon = "C", "Exceeds Limit", "❌"
        
        eligible = True
        reasons = []
        if credit_score < 700: eligible, reasons = False, [*reasons, f"Credit score {credit_score} < 700"]
        if foir > 50: eligible, reasons = False, [*reasons, f"FOIR {foir:.1f}% > 50%"]
        if scenario == "C": eligible, reasons = False, [*reasons, "Amount exceeds 2× pre-approved"]
        
        risk = "Low" if foir < 40 and credit_score >= 750 else "Medium" if foir < 50 else "High"
        
        progress_bar.empty()
        status_text.empty()
        
        st.session_state.underwriting_result = {"scenario": scenario, "scenario_label": scenario_label, "scenario_icon": scenario_icon, "eligible": eligible, "reasons": reasons, "emi": emi, "foir": foir, "risk": risk, "final_rate": rate, "credit_score": credit_score}
        st.session_state.agent_status["underwriting"]["status"] = "complete"
        st.session_state.agent_status["underwriting"]["result"] = f"Scenario {scenario}: {scenario_label} | EMI: ₹{emi:,} | FOIR: {foir:.1f}%"
        log_action(f"Underwriting: Scenario {scenario}, Eligible: {eligible}")
        
        st.markdown(f"### {scenario_icon} Scenario {scenario}: {scenario_label}")
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Monthly EMI", f"₹{emi:,}")
        with col2: st.metric("FOIR", f"{foir:.1f}%")
        with col3: st.metric("Risk Level", risk)
        with col4: st.metric("Interest Rate", f"{rate}%")
        
        if eligible:
            st.success("🎉 Loan **APPROVED**")
            st.session_state.stage = "DOCUMENT"
            time.sleep(2)
            st.rerun()
        else:
            st.error("❌ Loan Application Rejected")
            for reason in reasons: st.markdown(f"- {reason}")
            if st.button("← Start New Application"):
                for key in list(st.session_state.keys()): del st.session_state[key]
                st.rerun()
    
    # ==================== STAGE 4: DOCUMENT AGENT ====================
    elif st.session_state.stage == "DOCUMENT":
        st.session_state.agent_status["document"]["status"] = "working"
        log_action("Document Agent: Requesting salary verification")
        
        st.markdown("#### 📄 Document Agent")
        
        if "salary_verified" not in st.session_state:
            st.info("📋 Upload your salary slip for verification")
            uploaded_file = st.file_uploader("Upload Salary Slip (PDF/JPG)", type=['pdf', 'jpg', 'jpeg', 'png'])
            declared_salary = st.number_input("Declared Monthly Salary (₹)*", min_value=10000, value=st.session_state.app_data["monthly_salary"], step=5000)
            
            if st.button("Verify Document", use_container_width=True, type="primary"):
                if not uploaded_file:
                    st.error("❌ Please upload salary slip")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    status_text.text("📄 Extracting text...")
                    time.sleep(1)
                    progress_bar.progress(50)
                    status_text.text("📄 Cross-checking salary...")
                    time.sleep(1)
                    progress_bar.progress(100)
                    progress_bar.empty()
                    status_text.empty()
                    
                    extracted_salary = st.session_state.app_data["monthly_salary"]
                    variance = abs(extracted_salary - declared_salary) / extracted_salary * 100
                    
                    if variance <= 10:
                        st.success("✅ Salary verification successful!")
                        st.markdown(f"**Extracted:** ₹{extracted_salary:,} | **Declared:** ₹{declared_salary:,}")
                        st.session_state.salary_verified = True
                        st.session_state.agent_status["document"]["status"] = "complete"
                        st.session_state.agent_status["document"]["result"] = f"Salary verified: ₹{extracted_salary:,}"
                        log_action(f"Document Agent: Salary verified")
                        st.session_state.stage = "SANCTION"
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ Salary mismatch detected!")
        else:
            st.success("✅ Document verification complete")
            st.session_state.stage = "SANCTION"
            st.rerun()
    
    # ==================== STAGE 5: SANCTION AGENT ====================
    elif st.session_state.stage == "SANCTION":
        st.session_state.agent_status["sanction"]["status"] = "working"
        log_action("Sanction Agent: Generating letter")
        
        st.markdown("#### 📋 Sanction Agent")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("📋 Preparing documents...")
        time.sleep(1)
        progress_bar.progress(50)
        status_text.text("📋 Generating PDF...")
        time.sleep(1)
        progress_bar.progress(100)
        
        progress_bar.empty()
        status_text.empty()
        
        data = st.session_state.app_data
        underwriting = st.session_state.underwriting_result
        
        letter_content = f"""
╔═══════════════════════════════════════════════╗
║     TATA CAPITAL - LOAN SANCTION LETTER       ║
╚═══════════════════════════════════════════════╝

Application ID: {st.session_state.application_id}
Date: {datetime.now().strftime("%d %B %Y")}

Dear {data['name']},

Congratulations! Your loan application has been APPROVED.

LOAN DETAILS:
Applicant Name      : {data['name']}
PAN Number          : {data['pan']}
Loan Type           : {data['loan_type']} Loan
Sanctioned Amount   : ₹{data['loan_amount']:,}
Tenure              : {data['tenure']} months
Interest Rate       : {underwriting['final_rate']}% p.a.
Monthly EMI         : ₹{underwriting['emi']:,}
Total Repayment     : ₹{int(underwriting['emi'] * data['tenure']):,}

CREDIT ASSESSMENT:
CIBIL Score         : {underwriting['credit_score']}
FOIR                : {underwriting['foir']:.1f}%
Risk Category       : {underwriting['risk']}
Approval Scenario   : {underwriting['scenario']} - {underwriting['scenario_label']}

Generated by LoanFlow AI | 5-Agent Architecture
        """
        
        st.session_state.sanction_letter = letter_content
        st.session_state.agent_status["sanction"]["status"] = "complete"
        st.session_state.agent_status["sanction"]["result"] = "Letter generated successfully"
        log_action("Sanction Agent: Letter generated")
        
        st.success("✅ Sanction Letter Generated!")
        st.code(letter_content, language="text")
        
        st.download_button(
            label="📥 Download Sanction Letter",
            data=letter_content,
            file_name=f"Sanction_Letter_{st.session_state.application_id}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        st.session_state.stage = "COMPLETE"
        
        if st.button("🔄 Process New Application", use_container_width=True):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

# ==================== AUDIT LOG ====================
with st.expander("🔒 Audit Log"):
    if st.session_state.logs:
        st.code("\n".join(st.session_state.logs[-20:]), language="log")
    else:
        st.info("No logs yet")

st.markdown("---")
st.markdown("<div style='text-align:center; opacity:0.7; padding: 20px;'><strong>LoanFlow AI</strong> | Powered by 5-Agent Architecture | EY Techathon 6.0</div>", unsafe_allow_html=True)