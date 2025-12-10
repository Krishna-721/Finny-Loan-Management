"""
loanflow_demo/app_chat.py - NEW CHAT-FIRST VERSION

This is the updated main app that uses conversational interface
driven by Master Agent.

To use: Replace your current app.py with this, or run separately.
"""

import streamlit as st
import random
import time
from ai.master_agent import MasterAgent, format_agent_handoff
from theme.theme import apply_theme
from logic.verification_agent import verify_applicant
from logic.underwriting import run_underwriting_engine
from logic.sanction_agent import generate_sanction_letter
from logic.utils import secure_log, render_header, calculate_emi
#from logic.validation import validate_pan

st.set_page_config(
    page_title="LoanFlow AI | Agentic Loan Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_theme()

# ================================
# SESSION STATE INITIALIZATION
# ================================
if "master_agent" not in st.session_state:
    st.session_state.master_agent = MasterAgent()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": "👋 Hi! I'm **Mr. Finn**, your personal loan advisor from LoanFlow AI.\n\nI'm here to help you get a personal loan approved in minutes. Ready to get started?"
        }
    ]

if "app_data" not in st.session_state:
    st.session_state.app_data = {
        "name": "", "pan": "", "phone": "",
        "income": 0, "loan_amount": 0, "tenure": 12,
        "rate": 10.5, "employment": "Salaried",
        "existing_emis": 0, "credit_score": 0,
        "purpose": "Personal", "pre_approved_limit": 0
    }

if "verification_result" not in st.session_state:
    st.session_state.verification_result = None

if "underwriting_result" not in st.session_state:
    st.session_state.underwriting_result = None

if "application_id" not in st.session_state:
    st.session_state.application_id = f"LF{random.randint(10000, 99999)}"

if "logs" not in st.session_state:
    st.session_state.logs = []

if "waiting_for_action" not in st.session_state:
    st.session_state.waiting_for_action = None


# ================================
# HELPER FUNCTIONS
# ================================

def extract_pan_from_message(message):
    """Extract PAN number from user message"""
    import re
    # Look for pattern: 5 letters, 4 digits, 1 letter
    match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', message.upper())
    return match.group(0) if match else None


def extract_amount_from_message(message):
    """Extract loan amount from user message"""
    import re
    # Look for patterns like: 5L, 5 lakh, 500000, 5,00,000
    
    # Pattern for "5L" or "5 lakh"
    match = re.search(r'(\d+\.?\d*)\s*(?:l|lakh|lakhs)', message.lower())
    if match:
        return int(float(match.group(1)) * 100000)
    
    # Pattern for direct numbers
    match = re.search(r'₹?\s*(\d[\d,]*)', message)
    if match:
        amount_str = match.group(1).replace(',', '')
        return int(amount_str)
    
    return None


def extract_tenure_from_message(message):
    """Extract tenure from user message"""
    import re
    match = re.search(r'(\d+)\s*(?:month|months|yr|year|years)', message.lower())
    if match:
        value = int(match.group(1))
        # If mentioned in years, convert to months
        if 'yr' in message.lower() or 'year' in message.lower():
            value *= 12
        return value
    return None


def extract_purpose_from_message(message):
    """Extract loan purpose from user message"""
    message_lower = message.lower()
    purposes = {
        "home": ["home", "house", "property", "renovation"],
        "education": ["education", "study", "college", "course"],
        "medical": ["medical", "health", "hospital", "treatment"],
        "business": ["business", "startup", "expansion"],
        "personal": ["personal", "vacation", "wedding", "emergency"]
    }
    
    for purpose, keywords in purposes.items():
        if any(kw in message_lower for kw in keywords):
            return purpose.capitalize()
    
    return "Personal"


# ================================
# MAIN UI
# ================================

render_header()

# Application Status Bar
st.markdown(f"""
<div style='background: rgba(30, 35, 60, 0.8); padding: 20px; border-radius: 12px; margin-bottom: 25px;'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div>
            <div style='font-size: 0.8rem; opacity: 0.7;'>Application ID</div>
            <div style='font-weight: 700; font-size: 1.1rem;'>{st.session_state.application_id}</div>
        </div>
        <div>
            <div style='font-size: 0.8rem; opacity: 0.7;'>Conversation Stage</div>
            <div style='font-weight: 700; font-size: 1.1rem; color: #8b5cf6;'>{st.session_state.master_agent.stage}</div>
        </div>
        <div>
            <div style='font-size: 0.8rem; opacity: 0.7;'>Status</div>
            <div style='font-weight: 700; font-size: 1.1rem; color: #10b981;'>Active</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ================================
# CHAT INTERFACE
# ================================

st.markdown("### 💬 Loan Application Chat")

# Chat container
chat_container = st.container()

with chat_container:
    for idx, msg in enumerate(st.session_state.chat_messages):
        if msg["role"] == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("user"):
                st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Type your message here...", key="user_input")

if user_input:
    # Add user message to chat
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_input
    })
    
    secure_log(f"User input: {user_input[:50]}")
    
    # Extract data from message based on stage
    stage = st.session_state.master_agent.stage
    
    if stage == "COLLECT_PAN":
        pan = extract_pan_from_message(user_input)
        if pan:
            st.session_state.app_data["pan"] = pan
            secure_log(f"PAN extracted: {pan}")
    
    elif stage == "VERIFICATION_COMPLETE":
        amount = extract_amount_from_message(user_input)
        if amount:
            st.session_state.app_data["loan_amount"] = amount
            secure_log(f"Loan amount extracted: ₹{amount:,}")
    
    elif stage == "COLLECT_DETAILS":
        # Extract various details
        purpose = extract_purpose_from_message(user_input)
        st.session_state.app_data["purpose"] = purpose
        
        tenure = extract_tenure_from_message(user_input)
        if tenure:
            st.session_state.app_data["tenure"] = tenure
        
        amount = extract_amount_from_message(user_input)
        if amount and "salary" in user_input.lower() or "income" in user_input.lower():
            st.session_state.app_data["income"] = amount * 12  # Convert monthly to annual
    
    # Build context for master agent
    context = {
        **st.session_state.app_data,
        "decision": st.session_state.underwriting_result.get("scenario_label", "") if st.session_state.underwriting_result else ""
    }
    
    if st.session_state.verification_result:
        context.update(st.session_state.verification_result)
    
    # Get response from Master Agent
    with st.spinner("🤖 Mr. Finn is thinking..."):
        ai_response, action, next_stage = st.session_state.master_agent.process_message(
            user_input, 
            context
        )
    
    # Add AI response
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": ai_response
    })
    
    # Execute worker agent actions
    if action == "VERIFY":
        # Show agent handoff
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": format_agent_handoff("VERIFY", "calling")
        })
        
        with st.spinner("🔍 Verification Agent working..."):
            time.sleep(1)  # Simulate processing
            pan = st.session_state.app_data.get("pan", "")
            result = verify_applicant(pan)
            
            if result["status"] == "verified":
                st.session_state.verification_result = result
                st.session_state.app_data["credit_score"] = result["credit_score"]
                st.session_state.app_data["pre_approved_limit"] = result["pre_approved_limit"]
                st.session_state.app_data["existing_emis"] = result["existing_emi"]
                st.session_state.app_data["name"] = result.get("name", "Guest")
                
                secure_log(f"Verification complete: Score={result['credit_score']}, Pre-approved=₹{result['pre_approved_limit']:,}")
                
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": format_agent_handoff("VERIFY", "complete")
                })
                
                # Auto-continue conversation
                continue_msg = f"""
Great news, **{result['name']}**! Here's what I found:

✅ **Credit Score:** {result['credit_score']}/900  
💰 **Pre-Approved Limit:** ₹{result['pre_approved_limit']:,}  
📊 **Existing EMIs:** ₹{result['existing_emi']:,}/month

You have a {"strong" if result['credit_score'] >= 750 else "good"} credit profile! 

**How much would you like to borrow?**  
💡 *For amounts up to ₹{result['pre_approved_limit']:,}, I can approve instantly!*
"""
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": continue_msg
                })
                
                st.session_state.master_agent.stage = "VERIFICATION_COMPLETE"
            else:
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": "⚠️ I couldn't verify that PAN number. Please check and try again."
                })
    
    elif action == "UNDERWRITE":
        # Show agent handoff
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": format_agent_handoff("UNDERWRITE", "calling")
        })
        
        with st.spinner("⚖️ Underwriting Agent evaluating..."):
            result = run_underwriting_engine(
                st.session_state.app_data,
                st.session_state.verification_result
            )
            
            st.session_state.underwriting_result = result
            secure_log(f"Underwriting complete: Scenario={result['scenario']}, Eligible={result['eligible']}")
            
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": format_agent_handoff("UNDERWRITE", "complete")
            })
            
            # Format decision message
            if result['eligible']:
                decision_msg = f"""
🎉 **Congratulations!** Your loan is **APPROVED**!

**{result['scenario_icon']} Scenario {result['scenario']}: {result['scenario_label']}**

📋 **Loan Details:**
- Amount: ₹{st.session_state.app_data['loan_amount']:,}
- Tenure: {st.session_state.app_data['tenure']} months
- Interest Rate: {result['final_rate']}%
- **Monthly EMI: ₹{result['emi']:,}**

📊 **Your Metrics:**
- Credit Score: {result['score']}
- FOIR: {result['foir']}%
- Risk Level: {result['risk']}

Let me generate your sanction letter now...
"""
            else:
                reasons_text = "\n".join([f"• {r}" for r in result['reasons']])
                decision_msg = f"""
😔 Unfortunately, your application couldn't be approved at this time.

**{result['scenario_icon']} Scenario {result['scenario']}: {result['scenario_label']}**

**Reasons:**
{reasons_text}

**Recommendations:**
"""
                for rec in result['recommendations']:
                    decision_msg += f"\n{rec}"
            
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": decision_msg
            })
            
            st.session_state.master_agent.stage = "UNDERWRITING_COMPLETE"
    
    elif action == "SANCTION":
        if st.session_state.underwriting_result and st.session_state.underwriting_result['eligible']:
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": format_agent_handoff("SANCTION", "calling")
            })
            
            with st.spinner("📄 Sanction Agent generating letter..."):
                time.sleep(1)
                pdf_buffer = generate_sanction_letter(
                    st.session_state.app_data,
                    st.session_state.underwriting_result,
                    st.session_state.application_id
                )
                
                st.session_state.sanction_pdf = pdf_buffer
                secure_log("Sanction letter generated")
                
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": format_agent_handoff("SANCTION", "complete")
                })
                
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": """
✅ **Your sanction letter is ready!**

Please download it below. This letter contains all your loan details and terms & conditions.

**What's next?**
1. Download and review your sanction letter
2. Our team will contact you within 24 hours
3. Keep your documents ready for final verification

Is there anything else I can help you with?
"""
                })
                
                st.session_state.master_agent.stage = "COMPLETE"
    
    st.rerun()


# ================================
# SANCTION LETTER DOWNLOAD
# ================================

if st.session_state.underwriting_result and st.session_state.underwriting_result.get('eligible'):
    if hasattr(st.session_state, 'sanction_pdf'):
        st.divider()
        st.markdown("### 📄 Your Sanction Letter")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.download_button(
                label="📥 Download Sanction Letter (PDF)",
                data=st.session_state.sanction_pdf,
                file_name=f"Sanction_Letter_{st.session_state.application_id}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        with col2:
            if st.button("🔄 New Application", use_container_width=True):
                # Reset everything
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()


# ================================
# AUDIT LOGS (Collapsible)
# ================================

with st.expander("🔒 View Audit Logs"):
    if st.session_state.logs:
        logs_text = "\n".join(st.session_state.logs[-20:])
        st.code(logs_text, language="log")
    else:
        st.info("No logs yet")


# ================================
# FOOTER
# ================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center; opacity:0.7; padding: 20px 0; font-size: 0.85rem;'>
        <strong>LoanFlow AI</strong> - Powered by Agentic AI Architecture<br>
        Master Agent + 4 Worker Agents | Built for EY Techathon 6.0<br>
        © 2024 All rights reserved
    </div>
    """,
    unsafe_allow_html=True
)