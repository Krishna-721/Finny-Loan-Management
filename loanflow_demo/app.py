import streamlit as st
import random
import time
from datetime import datetime

from agents.verification_agent import verify_pan
from agents.underwriting_agent import run_underwriting
from agents.document_agent import verify_salary_slip
from agents.sanction_agent import create_sanction_letter
from core.utils import validate_pan, LOAN_TYPES
from theme.chat_ui import render_chat_message, render_agent_loading, render_widget_container
from ai.persona import MasterAgent

st.set_page_config(
    page_title="LoanFlow AI | Loan Agent ",
    page_icon="🏦",
    layout="centered"
)

# Global CSS
st.markdown("""
<style>
.main { 
    background: linear-gradient(135deg, #0a0e27, #1a1f3a); 
    color: #E8EAED; 
}
.stButton>button {
    background: linear-gradient(135deg, #8b5cf6, #6366f1);
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}
</style>
""", unsafe_allow_html=True)

st.markdown("Refresh the page to start a new conversation.")

# Session State
if "master_agent" not in st.session_state:
    st.session_state.master_agent = MasterAgent()
    st.session_state.chat_history = []
    st.session_state.app_data = {}
    st.session_state.application_id = f"LF{random.randint(10000, 99999)}"
    st.session_state.waiting_for = None  # Track what we're waiting for

# Header
st.markdown("""
<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #8b5cf6, #6366f1); border-radius: 10px; margin-bottom: 20px;'>
    <h1 style='color: white; margin: 0;'>🏦 LoanFlow AI</h1>
    <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0;'>Conversational Loan Assistant | Application ID: {application_id}</p>
</div>
""", unsafe_allow_html=True)

# Main Chat Container
chat_container = st.container()

with chat_container:
    
    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["type"] == "message":
            render_chat_message(msg["role"], msg["content"])
        elif msg["type"] == "loading":
            render_agent_loading(msg["agent"])
        elif msg["type"] == "report":
            # CIBIL Report
            with st.expander("📊 View CIBIL Credit Report"):
                st.code(msg["content"], language="text")
            if "download_data" in msg:
                st.download_button(
                    label="📥 Download CIBIL Report",
                    data=msg["content"],
                    file_name=f"CIBIL_Report_{st.session_state.application_id}.txt",
                    mime="text/plain"
                )
        elif msg["type"] == "sanction":
            # Sanction Letter
            st.code(msg["content"], language="text")
            st.download_button(
                label="📥 Download Sanction Letter",
                data=msg["content"],
                file_name=f"Sanction_Letter_{st.session_state.application_id}.txt",
                mime="text/plain",
                use_container_width=True
            )

# Initial greeting
if len(st.session_state.chat_history) == 0:
    greeting = st.session_state.master_agent.get_message("GREETING")
    st.session_state.chat_history.append({"type": "message", "role": "agent", "content": greeting})
    st.session_state.waiting_for = "start_confirmation"
    st.rerun()

# === STAGE: Waiting for Start Confirmation ===
if st.session_state.waiting_for == "start_confirmation":
    user_input = st.chat_input("Type 'yes' to start...")
    
    if user_input:
        st.session_state.chat_history.append({"type": "message", "role": "user", "content": user_input})
        
        if any(word in user_input.lower() for word in ["yes", "sure", "ok", "start"]):
            st.session_state.master_agent.stage = "COLLECT_LOAN_TYPE"
            msg = st.session_state.master_agent.get_message("COLLECT_LOAN_TYPE")
            st.session_state.chat_history.append({"type": "message", "role": "agent", "content": msg})
            st.session_state.waiting_for = "loan_type"
            st.rerun()

# === STAGE: Collect Loan Type ===
elif st.session_state.waiting_for == "loan_type":
    
    with render_widget_container():
        col1, col2 = st.columns(2)
        
        with col1:
            loan_type = st.selectbox(
                "Select Loan Type",
                options=list(LOAN_TYPES.keys()),
                key="loan_type_select"
            )
        
        with col2:
            employment = st.selectbox(
                "Employment Type",
                options=["Salaried", "Self-Employed"],
                key="employment_select"
            )
        
        if st.button("Continue →", key="btn_loan_type"):
            st.session_state.app_data["loan_type"] = loan_type
            st.session_state.app_data["employment_type"] = employment
            
            # Add to chat
            st.session_state.chat_history.append({
                "type": "message",
                "role": "user",
                "content": f"I selected {loan_type} loan and I'm {employment}"
            })
            
            # Next stage
            st.session_state.master_agent.stage = "COLLECT_AMOUNT"
            msg = st.session_state.master_agent.get_message("COLLECT_AMOUNT")
            st.session_state.chat_history.append({"type": "message", "role": "agent", "content": msg})
            st.session_state.waiting_for = "amount"
            st.rerun()

# === STAGE: Collect Amount & Tenure ===
elif st.session_state.waiting_for == "amount":
    
    with render_widget_container():
        loan_amount = st.number_input(
            "Loan Amount (₹)",
            min_value=50000,
            max_value=10000000,
            value=500000,
            step=50000,
            key="loan_amount_input"
        )
        
        tenure = st.slider(
            "Tenure (months)",
            min_value=12,
            max_value=180,
            value=36,
            step=2,
            key="tenure_slider"
        )
        
        # Show interest rate info
        loan_type = st.session_state.app_data.get("loan_type", "Personal")
        rate_ranges = {
            "Personal": "10.5% - 24%",
            "Home": "8.3% - 11%",
            "Auto": "8% - 13%",
            "Education": "9% - 14%",
            "Business": "11% - 24%"
        }
        
        st.info(f"📌 Typical Interest Rate for {loan_type}: {rate_ranges.get(loan_type, 'Varies')}")
        
        if st.button("Continue →", key="btn_amount"):
            st.session_state.app_data["loan_amount"] = loan_amount
            st.session_state.app_data["tenure"] = tenure
            
            st.session_state.chat_history.append({
                "type": "message",
                "role": "user",
                "content": f"₹{loan_amount:,} for {tenure} months"
            })
            
            # Next stage
            st.session_state.master_agent.stage = "COLLECT_PAN"
            msg = st.session_state.master_agent.get_message("COLLECT_PAN")
            st.session_state.chat_history.append({"type": "message", "role": "agent", "content": msg})
            st.session_state.waiting_for = "pan"
            st.rerun()

# === STAGE: Collect PAN ===
elif st.session_state.waiting_for == "pan":
    
    with render_widget_container():
        pan = st.text_input(
            "Enter PAN Number",
            placeholder="ABCDE1234F",
            max_chars=10,
            key="pan_input"
        ).upper()
        
        if st.button("Verify PAN →", key="btn_pan"):
            if not validate_pan(pan):
                st.error("❌ Invalid PAN format. Use: ABCDE1234F")
            else:
                st.session_state.app_data["pan"] = pan
                
                st.session_state.chat_history.append({
                    "type": "message",
                    "role": "user",
                    "content": f"My PAN is {pan}"
                })
                
                # Show loading
                st.session_state.chat_history.append({
                    "type": "loading",
                    "agent": "Verification"
                })
                
                st.session_state.waiting_for = "verification_processing"
                st.rerun()

# === STAGE: Verification Processing ===
elif st.session_state.waiting_for == "verification_processing":
    
    # Simulate processing
    time.sleep(2)
    
    # Call Verification Agent
    pan = st.session_state.app_data["pan"]
    bureau_data, cibil_report = verify_pan(pan)
    
    if bureau_data:
        st.session_state.app_data.update({
            "name": bureau_data["name"],
            "credit_score": bureau_data["credit_score"],
            "existing_emi": bureau_data["existing_emi"],
            "pre_approved_limit": bureau_data["preapproved_limit"],
            "monthly_salary": bureau_data.get("monthly_income", 80000)
        })
        
        # Remove loading, add system message
        st.session_state.chat_history.pop()  # Remove loading
        st.session_state.chat_history.append({
            "type": "message",
            "role": "system",
            "content": f"✅ Verification Agent: Verified {bureau_data['name']} | CIBIL Score: {bureau_data['credit_score']}"
        })
        
        # Add CIBIL report
        st.session_state.chat_history.append({
            "type": "report",
            "content": cibil_report,
            "download_data": True
        })
        
        # Agent message
        context = {
            "name": bureau_data["name"],
            "credit_score": bureau_data["credit_score"],
            "pre_approved_limit": bureau_data["preapproved_limit"]
        }
        msg = st.session_state.master_agent.get_message("VERIFICATION_DONE", context)
        st.session_state.chat_history.append({"type": "message", "role": "agent", "content": msg})
        
        st.session_state.waiting_for = "underwriting_trigger"
        st.rerun()
    else:
        st.session_state.chat_history.pop()
        st.session_state.chat_history.append({
            "type": "message",
            "role": "system",
            "content": "❌ Verification Agent: PAN not found"
        })
        st.session_state.waiting_for = "pan"
        st.rerun()
# === STAGE: Trigger Underwriting Automatically ===
elif st.session_state.waiting_for == "underwriting_trigger":

    # Immediately run underwriting without asking user
    st.session_state.chat_history.append({
        "type": "loading",
        "agent": "Underwriting"
    })

    time.sleep(2)

    uw_result = run_underwriting(
    loan_amount=st.session_state.app_data["loan_amount"],
    tenure=st.session_state.app_data["tenure"],
    credit_score=st.session_state.app_data["credit_score"],
    existing_emi=st.session_state.app_data["existing_emi"],
    income=st.session_state.app_data["monthly_salary"],
    employment_type=st.session_state.app_data["employment_type"],
    loan_purpose=st.session_state.app_data["loan_type"]
)


    # Remove loading spinner
    st.session_state.chat_history.pop()

    # Add underwriting system summary
    st.session_state.chat_history.append({
        "type": "message",
        "role": "system",
        "content": (
            f"Underwriting Complete | Decision: {uw_result['decision']} | "
            f"EMI: ₹{uw_result['emi']:,} | FOIR: {uw_result['foir']}%"
        )
    })

    # Agent Finn message
    msg = st.session_state.master_agent.get_message(
        "UNDERWRITING_APPROVED" if uw_result["decision"] == "APPROVED"
        else "UNDERWRITING_REJECTED",
        uw_result
    )
    st.session_state.chat_history.append({
        "type": "message",
        "role": "agent",
        "content": msg
    })

    # Store underwriting output
    st.session_state.app_data["emi"] = uw_result["emi"]
    st.session_state.app_data["interest_rate"] = uw_result["interest_rate"]
    st.session_state.app_data["foir"] = uw_result["foir"]
    st.session_state.app_data["uw_decision"] = uw_result["decision"]

    # If rejected: stop
    if uw_result["decision"] != "APPROVED":
        st.session_state.waiting_for = None
        st.rerun()

    # Continue to doc upload stage
    st.session_state.waiting_for = "document_upload"
    st.rerun()


# === STAGE: Salary Slip Upload (Pause Required) ===
elif st.session_state.waiting_for == "document_upload":

    with render_widget_container():
        uploaded = st.file_uploader("Upload Salary Slip", type=["pdf", "jpg", "png"])

        if uploaded and st.button("Verify Document →"):

            st.session_state.chat_history.append({
                "type": "loading",
                "agent": "Document Verification"
            })

            st.session_state.uploaded_file = uploaded
            st.session_state.waiting_for = "document_verification"
            st.rerun()


# === STAGE: Salary Slip Verification ===
elif st.session_state.waiting_for == "document_verification":

    time.sleep(2)

    result = verify_salary_slip(st.session_state.uploaded_file)

    # Remove loading spinner
    st.session_state.chat_history.pop()

    verified = result[0]
    message = result[1]

    if verified:
        st.session_state.chat_history.append({
            "type": "message",
            "role": "agent",
            "content": "✅ Salary Slip Verified Successfully!"
        })

        st.session_state.waiting_for = "sanction_letter"
        st.rerun()
    
    else:
        st.session_state.chat_history.append({
            "type": "message",
            "role": "agent",
            "content": "❌ Document verification failed. Please upload a valid salary slip."
        })

        st.session_state.waiting_for = "document_upload"
        st.rerun()


# === STAGE: Sanction Letter ===
elif st.session_state.waiting_for == "sanction_letter":

    sanction_text = create_sanction_letter(st.session_state.app_data)

    # Display sanction letter block
    st.session_state.chat_history.append({
        "type": "sanction",
        "content": sanction_text
    })

    # Add final closing message
    st.session_state.chat_history.append({
        "type": "message",
        "role": "agent",
        "content": (
            "🎉 **Congratulations! Your sanction letter is ready.**\n\n"
            "Thank you for using **LoanFlow AI**. If you have any more queries, "
            "I'm always here to help!"
        )
    })

    st.session_state.waiting_for = None
    st.rerun()

# ============================
# AUDIT LOGGING FUNCTION (HIDDEN FROM USER)
# ============================
def log_event(role, content):
    """Append every chat event to conversation_logs.txt silently."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("conversation_logs.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {role.upper()}: {content}\n")
    except Exception as e:
        # Never expose errors to user; fail silently
        pass
