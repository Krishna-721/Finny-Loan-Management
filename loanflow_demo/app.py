"""
LoanFlow AI - Complete 5-Agent Prototype with CIBIL Report Integration
Real-world banking process with clear agent orchestration
"""

import streamlit as st
import random
import time
from datetime import datetime
# import re

# from agents.sales_agent import collect_sales_info
from agents.verification_agent import verify_pan
from agents.underwriting_agent import run_underwriting
from agents.document_agent import verify_salary_slip
from agents.sanction_agent import create_sanction_letter
# from core.mock_bureau import fetch_pan_details
from core.utils import ( validate_pan, get_interest_rate, LOAN_TYPES, log_action )
from theme.chat_components import CHAT_BOX_STYLE, chat_popup_container
from ai.groq_client import get_llama_response
 


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

# ===================== LOAN RATES =====================
LOAN_TENURE_LIMITS = {
    "Personal": (12, 60),        # 1 to 5 years
    "Home": (60, 480),           # 5 to 40 years
    "Auto": (12, 96),            # 1 to 8 years
    "Education": (60, 180),      # 5 to 15 years
    "Business": (12, 60),        # 1 to 5 years
    "LAP": (60, 240),            # 5 to 20 years
}

LOAN_INTEREST_RANGES = {
    "Personal": "10.5% – 24%",
    "Home": "8.3% – 11%",
    "Auto": "8% – 13%",
    "Education": "9% – 14%",
    "Business": "11% – 24%",
    "LAP": "9% – 14%",
}

# ==================== SESSION STATE ====================
if "stage" not in st.session_state:
    st.session_state.stage = "SALES"
    st.session_state.app_data = {
        "name": "", "pan": "", "loan_type": "Personal", 
        "loan_amount": 0, "tenure": 12, "employment_type": "Salaried"
    }
    st.session_state.agent_status = {
        "sales": {"status": "idle", "result": None},
        "verification": {"status": "idle", "result": None},
        "underwriting": {"status": "idle", "result": None},
        "document": {"status": "idle", "result": None},
        "sanction": {"status": "idle", "result": None}
    }
    st.session_state.logs = []
    st.session_state.application_id = f"LF{random.randint(10000, 99999)}"
    st.session_state.cibil_report = None

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
    <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0;'>5-Agent Intelligent Loan Processing System with CIBIL Integration</p>
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
                loan_type = st.selectbox("Loan Type*", LOAN_TYPES.keys())
                loan_amount = st.number_input("Loan Amount (₹)*", min_value=50000, max_value=10000000, value=500000, step=50000)
            with col2:
                # Enable tenure only after loan type is selected
                min_t, max_t = LOAN_TENURE_LIMITS.get(loan_type, (12, 60))

                tenure = st.slider(
                    "Select Tenure (in months)*",
                    min_value=min_t,
                    max_value=max_t,
                    value=min_t,
                    step=2
                )

                # Show indicative interest rate range for this loan type
                st.markdown(
                    f"""
                    <div style="
                        margin-top: 10px;
                        padding: 12px;
                        border-radius: 6px;
                        background: rgba(139, 92, 246, 0.15);
                        border-left: 4px solid #8b5cf6;
                    ">
                        <strong>📌 Typical Interest Rate Range:</strong><br>
                        {LOAN_INTEREST_RANGES.get(loan_type, 'Varies')}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                employment = st.selectbox("Employment Type*", ["Salaried", "Self-Employed"])
                pan = st.text_input("PAN Number*", placeholder="ABCDE1234F", max_chars=10).upper()
            
            submitted = st.form_submit_button("Submit Application →", use_container_width=True)
            
            if submitted:
                if not all([ loan_type, loan_amount, tenure, pan]) or not validate_pan(pan):
                    st.error("❌ Please fill all fields correctly (PAN format: ABCDE1234F)")
                else:
                    st.session_state.app_data.update({
                        "loan_type": loan_type, "loan_amount": loan_amount, 
                        "tenure": tenure, "employment_type": employment, "pan": pan
                    })
                    rate = get_interest_rate(loan_type, tenure, 720, employment)
                    st.session_state.app_data["rate"] = rate
                    st.session_state.agent_status["sales"]["status"] = "complete"
                    st.session_state.agent_status["sales"]["result"] = f"Collected: {loan_type}, ₹{loan_amount:,} | Rate: {rate}%"
                    log_action(f"Sales Agent: Data collected for {loan_type}")
                    st.session_state.stage = "VERIFICATION"
                    time.sleep(1)
                    st.rerun()
    
    # ==================== STAGE 2: VERIFICATION AGENT ====================
    elif st.session_state.stage == "VERIFICATION":
        st.session_state.agent_status["verification"]["status"] = "working"
        log_action("Verification Agent: Validating PAN and fetching CIBIL report")
        
        st.markdown("#### 🔍 Verification Agent")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔍 Validating PAN format...")
        time.sleep(1)
        progress_bar.progress(33)
        
        pan = st.session_state.app_data["pan"]
        bureau_data, cibil_report = verify_pan(pan)
        
        if bureau_data:
            status_text.text("🔍 Fetching CIBIL credit report...")
            time.sleep(1)
            progress_bar.progress(66)
            
            status_text.text("✅ Verification complete!")
            progress_bar.progress(100)
            time.sleep(0.5)
            
            st.session_state.app_data.update({
                "name": bureau_data["name"],
                "credit_score": bureau_data["credit_score"],
                "existing_emi": bureau_data["existing_emi"],
                "pre_approved_limit": bureau_data["preapproved_limit"],
                "monthly_salary": bureau_data.get("monthly_income", 80000)
            })
            
            st.session_state.cibil_report = cibil_report
            
            st.session_state.agent_status["verification"]["status"] = "complete"
            st.session_state.agent_status["verification"]["result"] = f"Verified: {bureau_data['name']} | CIBIL: {bureau_data['credit_score']}"
            log_action(f"Verification Agent: Verified {bureau_data['name']}, CIBIL: {bureau_data['credit_score']}")
            
            progress_bar.empty()
            status_text.empty()
            
            st.success("✅ Verification Successful!")
            
            # Display CIBIL Report Summary
            st.markdown("### 📊 CIBIL Credit Report Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Name", bureau_data["name"])
            with col2: st.metric("CIBIL Score", bureau_data["credit_score"])
            with col3: st.metric("Existing EMI", f"₹{bureau_data['existing_emi']:,}")
            with col4: st.metric("Pre-Approved", f"₹{bureau_data['preapproved_limit']:,}")
            
            # Show detailed CIBIL report in expander
            if cibil_report:
                with st.expander("📄 View Full CIBIL Credit Report"):
                    st.code(cibil_report, language="text")
            
            # User-controlled navigation
            st.info("Review your CIBIL report above. Click Next when you're ready to continue.")

            if st.button("Proceed to Underwriting", use_container_width=True):
                st.session_state.stage = "UNDERWRITING"
                st.rerun()

        else:
            progress_bar.empty()
            status_text.empty()
            st.session_state.agent_status["verification"]["status"] = "error"
            log_action("Verification Agent: PAN not found")
            st.error("❌ PAN not found in bureau database")
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
        
        # Run underwriting using agent
        underwriting_result = run_underwriting(
            loan_amount=data["loan_amount"],
            tenure=data["tenure"],
            credit_score=data["credit_score"],
            existing_emi=data["existing_emi"],
            income=data["monthly_salary"],
            employment_type=data["employment_type"],
            loan_purpose=data["loan_type"]
        )
        
        progress_bar.empty()
        status_text.empty()
        
        # Determine scenario
        requested = data["loan_amount"]
        pre_approved = data["pre_approved_limit"]
        
        if requested <= pre_approved:
            scenario, scenario_label, scenario_icon = "A", "Instant Approval", "✅"
        elif requested <= (2 * pre_approved):
            scenario, scenario_label, scenario_icon = "B", "Conditional Approval", "📄"
        else:
            scenario, scenario_label, scenario_icon = "C", "Exceeds Limit", "❌"
        
        risk = "Low" if underwriting_result["foir"] < 40 and data["credit_score"] >= 750 else "Medium" if underwriting_result["foir"] < 50 else "High"
        
        st.session_state.underwriting_result = {
            "scenario": scenario,
            "scenario_label": scenario_label,
            "scenario_icon": scenario_icon,
            "eligible": underwriting_result["decision"] == "APPROVED",
            "reasons": [underwriting_result.get("reason")] if underwriting_result.get("reason") else [],
            "emi": underwriting_result["emi"],
            "foir": underwriting_result["foir"],
            "risk": risk,
            "final_rate": underwriting_result["interest_rate"],
            "credit_score": data["credit_score"]
        }
        
        st.session_state.agent_status["underwriting"]["status"] = "complete"
        st.session_state.agent_status["underwriting"]["result"] = f"Scenario {scenario}: {scenario_label} | EMI: ₹{underwriting_result['emi']:,} | FOIR: {underwriting_result['foir']:.1f}%"
        log_action(f"Underwriting: Scenario {scenario}, Eligible: {underwriting_result['decision']}")
        
        st.markdown(f"### {scenario_icon} Scenario {scenario}: {scenario_label}")
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Monthly EMI", f"₹{underwriting_result['emi']:,}")
        with col2: st.metric("FOIR", f"{underwriting_result['foir']:.1f}%")
        with col3: st.metric("Risk Level", risk)
        with col4: st.metric("Interest Rate", f"{underwriting_result['interest_rate']}%")
        
        if underwriting_result["decision"] == "APPROVED":
            st.success("🎉 Loan **APPROVED**")
            st.session_state.stage = "DOCUMENT"
            time.sleep(2)
            st.rerun()
        else:
            st.error("❌ Loan Application Rejected")
            if underwriting_result.get("reason"):
                st.markdown(f"- {underwriting_result['reason']}")
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
                    
                    ok, msg = verify_salary_slip(uploaded_file)
                    
                    if ok:
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
                        st.error(f"❌ {msg}")
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
        
        sanction_data = {
            "application_id": st.session_state.application_id,
            "name": data['name'],
            "pan": data['pan'],
            "loan_type": data['loan_type'],
            "loan_amount": data['loan_amount'],
            "tenure": data['tenure'],
            "interest_rate": underwriting['final_rate'],
            "emi": underwriting['emi'],
            "credit_score": underwriting['credit_score'],
            "foir": underwriting['foir'],
            "risk": underwriting['risk'],
            "scenario": underwriting['scenario'],
            "scenario_label": underwriting['scenario_label']
        }
        
        letter_filename = create_sanction_letter(sanction_data)
        
        # Generate text version for display
        letter_content = f"""
╔═══════════════════════════════════════════════╗
║     LOANFLOW AI - LOAN SANCTION LETTER        ║
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
            label="📥 Download Sanction Letter (TXT)",
            data=letter_content,
            file_name=f"Sanction_Letter_{st.session_state.application_id}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        st.session_state.stage = "COMPLETE"
        
        if st.button("🔄 Process New Application", use_container_width=True):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

# ==================== CHAT POPUP ====================
st.markdown(CHAT_BOX_STYLE, unsafe_allow_html=True)

# Floating chat button icon
st.markdown("""
<style>
.chat-launcher {
    position: fixed;
    bottom: 25px;
    right: 25px;
    width: 60px;
    height: 60px;
    background: #2D7FF9;
    border-radius: 50%;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    font-size: 28px;
    cursor: pointer;
    z-index: 99999;
}
</style>

""", unsafe_allow_html=True)

# Chat Window Container (Hidden by default)
st.markdown(f"""
<div id="chat-window" style="display:none;">
    {chat_popup_container()}
</div>
""", unsafe_allow_html=True)


# ==================== CHAT MESSAGE HANDLING ====================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Placeholder where chat messages will be rendered
chat_container = st.empty()

def render_chat():
    chat_html = ""
    for sender, message in st.session_state.chat_history:
        if sender == "user":
            chat_html += f"<div class='chat-bubble-user'>{message}</div>"
        else:
            chat_html += f"<div class='chat-bubble-ai'>{message}</div>"

    chat_container.markdown(
        f"""
        <div class='chat-messages'>
            {chat_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# Chat input box (inside popup)
user_msg = st.text_input(
    "🤖 Mr. Finn:",
    key="finn_chat",
    placeholder="Ask me anything about your loan..."
)

if user_msg:
    # Add user message
    st.session_state.chat_history.append(("user", user_msg))

    # LLM reply via Groq
    ai_reply = get_llama_response(user_msg)
    st.session_state.chat_history.append(("ai", ai_reply))

# Render chat messages
render_chat()

# ==================== AUDIT LOG ====================
with st.expander("🔒 Audit Log"):
    if st.session_state.logs:
        st.code("\n".join(st.session_state.logs[-20:]), language="log")
    else:
        st.info("No logs yet")

st.markdown("---")
st.markdown("<div style='text-align:center; opacity:0.7; padding: 20px;'><strong>LoanFlow AI</strong> | Powered by 5-Agent Architecture with CIBIL Integration</div>", unsafe_allow_html=True)