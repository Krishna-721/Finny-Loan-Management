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
from ai.groq_client import get_llama_response


# ========================================
# CONFIGURATION & SETUP
# ========================================

st.set_page_config(
    page_title="LoanFlow | Smart Loan Assistant",
    page_icon="🏦",
    layout="centered",
    initial_sidebar_state="auto"
)


# ========================================
# UTILITY FUNCTIONS
# ========================================

def log_event(role: str, content: str, level: str = "INFO") -> None:
    """Enhanced audit logging with error handling and levels"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("conversation_logs.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [{level}] {role}: {content}\n")
    except Exception as e:
        st.error(f"Logging error: {str(e)}")


def format_currency(amount: int) -> str:
    """Format currency in Indian style"""
    return f"₹{amount:,}"


def calculate_emi(principal: float, rate: float, tenure: int) -> float:
    """Calculate EMI using standard formula"""
    r = rate / (12 * 100)
    emi = principal * r * ((1 + r) ** tenure) / (((1 + r) ** tenure) - 1)
    return round(emi, 2)


def add_message(role: str, content: str, message_type: str = "message") -> None:
    """Add message to chat history with logging"""
    st.session_state.chat_history.append({
        "type": message_type,
        "role": role,
        "content": content,
        "timestamp": datetime.now()
    })
    log_event(role.upper(), content)


def show_progress_bar(step: int, total_steps: int = 6) -> None:
    """Display application progress"""
    progress_names = [
        "Welcome", "Loan Details", "Verification", 
        "Underwriting", "Documents", "Approval"
    ]
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(99, 102, 241, 0.15)); 
                padding: 20px; border-radius: 15px; margin: 20px 0;
                border: 1px solid rgba(139, 92, 246, 0.3);
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
        <div style='display: flex; justify-content: space-between; margin-bottom: 12px; align-items: center;'>
            <span style='color: #a78bfa; font-weight: 700; font-size: 1.1em;'>📊 Application Progress</span>
            <span style='background: rgba(139, 92, 246, 0.3); padding: 6px 14px; border-radius: 20px; 
                         color: #c4b5fd; font-weight: 600; font-size: 0.95em;'>Step {step} of {total_steps}</span>
        </div>
        <div style='background: rgba(255,255,255,0.08); height: 10px; border-radius: 10px; overflow: hidden; 
                    box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);'>
            <div style='background: linear-gradient(90deg, #8b5cf6, #6366f1, #7c3aed); 
                        height: 100%; width: {(step/total_steps)*100}%; 
                        transition: width 0.5s ease-in-out;
                        box-shadow: 0 0 10px rgba(139, 92, 246, 0.6);'></div>
        </div>
        <div style='color: rgba(255,255,255,0.8); font-size: 0.95em; margin-top: 12px; 
                    display: flex; align-items: center; gap: 8px;'>
            <span style='color: #22c55e;'>●</span>
            <span>Current Stage: <strong style='color: #c4b5fd;'>{progress_names[min(step-1, len(progress_names)-1)]}</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ========================================
# ENHANCED STYLING
# ========================================

st.markdown("""
<style>
    /* Main background with subtle pattern */
    .main { 
        background: linear-gradient(135deg, #0a0e27, #1a1f3a); 
        color: #E8EAED;
    }
    
    /* Buttons with hover effects */
    .stButton>button {
        background: linear-gradient(135deg, #8b5cf6, #6366f1);
        color: white;
        border: none;
        padding: 14px 32px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 16px;
        transition: all 0.3s ease;
        width: 100%;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
        letter-spacing: 0.5px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.6);
        background: linear-gradient(135deg, #9d6fff, #7b82ff);
    }
    
    .stButton>button:active {
        transform: translateY(-1px);
    }
    
    /* Input fields with focus effects */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background: rgba(255, 255, 255, 0.08);
        border: 2px solid rgba(139, 92, 246, 0.4);
        border-radius: 10px;
        color: white;
        padding: 12px 16px;
        transition: all 0.3s ease;
        font-size: 15px;
    }
    
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.25);
        background: rgba(255, 255, 255, 0.12);
    }
    
    /* Select boxes */
    .stSelectbox>div>div {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        border: 2px solid rgba(139, 92, 246, 0.4);
        transition: all 0.3s ease;
    }
    
    .stSelectbox>div>div:hover {
        border-color: #8b5cf6;
    }
    
    /* Slider styling */
    .stSlider>div>div>div {
        background: rgba(139, 92, 246, 0.3);
    }
    
    .stSlider>div>div>div>div {
        background: linear-gradient(90deg, #8b5cf6, #6366f1);
    }
    
    /* File uploader */
    .stFileUploader>div {
        background: rgba(139, 92, 246, 0.12);
        border: 2px dashed rgba(139, 92, 246, 0.5);
        border-radius: 12px;
        padding: 25px;
        transition: all 0.3s ease;
    }
    
    .stFileUploader>div:hover {
        border-color: #8b5cf6;
        background: rgba(139, 92, 246, 0.18);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(139, 92, 246, 0.15);
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid rgba(139, 92, 246, 0.3);
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(139, 92, 246, 0.25);
    }
    
    /* Success/Error/Info messages */
    .stAlert {
        border-radius: 12px;
        padding: 18px;
        border-left: 4px solid;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Chat input */
    .stChatInput>div {
        border-radius: 12px;
        border: 2px solid rgba(139, 92, 246, 0.4);
        background: rgba(255, 255, 255, 0.08);
    }
    
    .stChatInput>div:focus-within {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.25);
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.6);
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(139, 92, 246, 0.8);
    }
    
    /* Fade in animation for content */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Loading spinner */
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)


# ========================================
# SESSION STATE INITIALIZATION
# ========================================

def initialize_session_state():
    """Initialize all session state variables"""
    if "master_agent" not in st.session_state:
        st.session_state.master_agent = MasterAgent()
        st.session_state.chat_history = []
        st.session_state.app_data = {}
        st.session_state.application_id = f"LF{random.randint(100000, 999999)}"
        st.session_state.waiting_for = None
        st.session_state.errors = []
        st.session_state.start_time = datetime.now()
        log_event("SYSTEM", f"New session started: {st.session_state.application_id}", "INFO")

initialize_session_state()


# ========================================
# ENHANCED HEADER WITH METRICS
# ========================================

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #8b5cf6, #6366f1); 
                padding: 28px; border-radius: 15px; 
                box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4);
                border: 1px solid rgba(255,255,255,0.1);
                animation: fadeIn 0.6s ease-out;'>
        <h1 style='color: white; margin: 0; font-size: 2.2em; font-weight: 800; 
                   text-shadow: 0 2px 10px rgba(0,0,0,0.3);'>
            🏦 LoanFlow 
        </h1>
        <p style='color: rgba(255,255,255,0.95); margin: 10px 0 0 0; font-size: 1.15em; font-weight: 500;'>
            Smart Conversational Loan Assistant
        </p>
        <p style='color: rgba(255,255,255,0.8); margin: 8px 0 0 0; font-size: 1em; font-weight: 400; font-style: italic;'>
            Powered by Finn, the master agent
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(99, 102, 241, 0.2)); 
                padding: 20px; border-radius: 12px; 
                border: 2px solid rgba(139, 92, 246, 0.4); text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                animation: fadeIn 0.6s ease-out 0.2s backwards;'>
        <div style='color: rgba(255,255,255,0.7); font-size: 0.85em; margin-bottom: 6px; 
                    text-transform: uppercase; letter-spacing: 1px;'>Application ID</div>
        <div style='color: #c4b5fd; font-weight: 800; font-size: 1.15em; 
                    font-family: monospace;'>{st.session_state.application_id}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    steps_completed = len([x for x in st.session_state.chat_history if x.get("type") == "message" and x.get("role") == "system"])
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(99, 102, 241, 0.2)); 
                padding: 20px; border-radius: 12px; 
                border: 2px solid rgba(139, 92, 246, 0.4); text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                animation: fadeIn 0.6s ease-out 0.4s backwards;'>
        <div style='color: rgba(255,255,255,0.7); font-size: 0.85em; margin-bottom: 6px;
                    text-transform: uppercase; letter-spacing: 1px;'>Steps Done</div>
        <div style='color: #c4b5fd; font-weight: 800; font-size: 1.15em;'>{steps_completed}/6</div>
    </div>
    """, unsafe_allow_html=True)

# Progress indicator
current_step = 1
if st.session_state.waiting_for in ["loan_purpose", "loan_type", "amount"]:
    current_step = 2
elif st.session_state.waiting_for in ["pan", "verification_processing"]:
    current_step = 3
elif st.session_state.waiting_for in ["underwriting_trigger"]:
    current_step = 4
elif st.session_state.waiting_for in ["document_upload", "document_verification"]:
    current_step = 5
elif st.session_state.waiting_for in ["sanction_letter"]:
    current_step = 6

show_progress_bar(current_step)

st.markdown("""
<div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(99, 102, 241, 0.1)); 
            padding: 15px 20px; border-radius: 10px; 
            margin: 18px 0; text-align: center; 
            border: 1px solid rgba(139, 92, 246, 0.25);
            box-shadow: 0 2px 10px rgba(0,0,0,0.15);
            animation: fadeIn 0.6s ease-out 0.6s backwards;'>
    <span style='color: rgba(255,255,255,0.85); font-size: 0.95em;'>
        💡 <strong>Quick Tip:</strong> Refresh page for new application | All conversations are securely logged
    </span>
</div>
""", unsafe_allow_html=True)


# ========================================
# CHAT HISTORY RENDERER
# ========================================

with st.container():
    for msg in st.session_state.chat_history:
        if msg["type"] == "message":
            render_chat_message(msg["role"], msg["content"])
            
        elif msg["type"] == "loading":
            render_agent_loading(msg["agent"])
            
        elif msg["type"] == "report":
            with st.expander("📊 View CIBIL Credit Report", expanded=False):
                st.code(msg["content"], language="text")
            if "download_data" in msg:
                st.download_button(
                    label="📥 Download CIBIL Report (TXT)",
                    data=msg["content"],
                    file_name=f"CIBIL_Report_{st.session_state.application_id}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                
        elif msg["type"] == "sanction":
            st.markdown("""
            <div style='background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(16, 185, 129, 0.15)); 
                        padding: 25px; border-radius: 15px; 
                        border: 2px solid rgba(34, 197, 94, 0.4); margin: 25px 0;
                        box-shadow: 0 6px 20px rgba(34, 197, 94, 0.2);
                        animation: fadeIn 0.5s ease-out;'>
                <h3 style='color: #22c55e; margin-top: 0; display: flex; align-items: center; gap: 10px;'>
                    🎉 Sanction Letter Generated Successfully!
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📄 View Sanction Letter", expanded=True):
                st.code(msg["content"], language="text")
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download as TXT",
                    data=msg["content"],
                    file_name=f"Sanction_Letter_{st.session_state.application_id}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                st.download_button(
                    label="📧 Email Copy",
                    data=msg["content"],
                    file_name=f"Sanction_Letter_{st.session_state.application_id}.txt",
                    mime="text/plain",
                    use_container_width=True
                )


# ========================================
# CONVERSATION FLOW HANDLERS
# ========================================

# INITIAL GREETING
if len(st.session_state.chat_history) == 0:
    greeting = (
        "👋 Hi, I'm Mr. Finn, your personal loan assistant!\n\n"
        "I'm here to help you secure the perfect loan for your needs. "
        "The process is simple, secure, and typically takes just a few minutes.\n\n"
        "**What I'll need from you:**\n"
        "• Basic loan requirements\n"
        "• PAN verification\n"
        "• Income details\n\n"
        "Shall we get started?"
    )
    add_message("agent", greeting)
    st.session_state.waiting_for = "start_confirmation"
    st.rerun()


# START CONFIRMATION
elif st.session_state.waiting_for == "start_confirmation":
    user_input = st.chat_input("Type 'yes' to begin your loan application...")
    
    if user_input:
        add_message("user", user_input)
        
        if user_input.lower().strip() in ["yes", "y", "ok", "okay", "sure", "start", "begin", "proceed"]:
            sales_msg = (
                "Excellent! Let's begin. 🚀\n\n"
                "First, I'd like to understand your financial needs better. "
                "**What's the primary purpose of your loan?**\n\n"
                "*For example: buying a home, vehicle, education, business expansion, medical emergency, etc.*"
            )
            add_message("agent", sales_msg)
            st.session_state.waiting_for = "loan_purpose"
        else:
            add_message("agent", "No worries! When you're ready to proceed, just type 'yes' and we'll get started. 😊")
        
        st.rerun()


# LOAN PURPOSE + AI RECOMMENDATION
elif st.session_state.waiting_for == "loan_purpose":
    purpose = st.chat_input("Tell me your loan purpose...")
    
    if purpose:
        add_message("user", purpose)
        st.session_state.app_data["loan_purpose"] = purpose
        
        # AI-powered loan recommendation
        with st.spinner("🤔 Analyzing your needs..."):
            prompt = f"""
            You are a financial advisor. A customer wants a loan for: "{purpose}"

            Analyze their need and:
            1. Recommend the BEST loan type from: Personal Loan, Home Loan, Auto Loan, Business Loan, Education Loan
            2. Provide a 1 sentence explanation of why this loan type suits them, keep it short and nice (max 50 words)
            3. Mention 1-2 point (short and crisp) key benefits of this loan type
            4. Everything must be in a readable format.

            Format your response naturally and conversationally. End with:
            RECOMMENDED: <LoanType>
            """
            
            try:
                ai_reply = get_llama_response(prompt)
                add_message("agent", ai_reply)
                
                # Extract recommendation
                if "RECOMMENDED:" in ai_reply:
                    rec = ai_reply.split("RECOMMENDED:")[1].strip()
                    st.session_state.app_data["recommended_loan_type"] = rec
                    log_event("AI_RECOMMENDATION", rec, "INFO")
                    
            except Exception as e:
                log_event("AI_ERROR", str(e), "ERROR")
                add_message("agent", "Based on your requirement, I can help you find the right loan. Let's proceed!")
        
        msg = st.session_state.master_agent.get_message("COLLECT_LOAN_TYPE")
        add_message("agent", msg)
        st.session_state.waiting_for = "loan_type"
        st.rerun()


# LOAN TYPE SELECTION
elif st.session_state.waiting_for == "loan_type":
    with render_widget_container():
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(99, 102, 241, 0.15)); 
                    padding: 25px; border-radius: 15px; margin: 20px 0;
                    border: 2px solid rgba(139, 92, 246, 0.3);
                    box-shadow: 0 6px 20px rgba(0,0,0,0.2);'>
            <h3 style='color: #c4b5fd; margin-top: 0; display: flex; align-items: center; gap: 10px;'>
                📋 Loan Configuration
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        recommended = st.session_state.app_data.get("recommended_loan_type")
        options = list(LOAN_TYPES.keys())
        default_index = options.index(recommended) if recommended in options else 0
        
        col1, col2 = st.columns(2)
        
        with col1:
            loan_type = st.selectbox(
                "Loan Type",
                options,
                index=default_index,
                help="Select the type of loan you need"
            )
            
            # Show loan details
            if loan_type in LOAN_TYPES:
                loan_info = LOAN_TYPES[loan_type]
                st.info(f"💰 Interest Rate: {loan_info.get('base_rate', 'N/A')}% p.a.\n\n"
                       f"📅 Max Tenure: {loan_info.get('max_tenure', 'N/A')} months")
        
        with col2:
            employment = st.selectbox(
                "Employment Type",
                ["Salaried", "Self-Employed"],
                help="Your current employment status"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Continue →", use_container_width=True):
            st.session_state.app_data["loan_type"] = loan_type
            st.session_state.app_data["employment_type"] = employment
            
            add_message("user", f"I selected {loan_type} and I'm {employment}")
            
            msg = st.session_state.master_agent.get_message("COLLECT_AMOUNT")
            add_message("agent", msg)
            
            st.session_state.waiting_for = "amount"
            st.rerun()


# AMOUNT + TENURE
elif st.session_state.waiting_for == "amount":
    with render_widget_container():
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(99, 102, 241, 0.15)); 
                    padding: 25px; border-radius: 15px; margin: 20px 0;
                    border: 2px solid rgba(139, 92, 246, 0.3);
                    box-shadow: 0 6px 20px rgba(0,0,0,0.2);'>
            <h3 style='color: #c4b5fd; margin-top: 0; display: flex; align-items: center; gap: 10px;'>
                💰 Loan Amount & Tenure
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            loan_amount = st.number_input(
                "Loan Amount (₹)",
                min_value=50000,
                max_value=10000000,
                value=500000,
                step=50000,
                help="Enter the amount you want to borrow"
            )
            
        with col2:
            tenure = st.slider(
                "Tenure (months)",
                min_value=12,
                max_value=240,
                value=36,
                step=6,
                help="Loan repayment period"
            )
        
        # EMI Calculator Preview
        loan_info = LOAN_TYPES.get(st.session_state.app_data.get("loan_type", "Personal"), {})
        rate = loan_info.get("base_rate", 10.5)
        estimated_emi = calculate_emi(loan_amount, rate, tenure)
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(99, 102, 241, 0.2)); 
                    padding: 20px; border-radius: 12px; margin: 20px 0;
                    border: 2px solid rgba(139, 92, 246, 0.4);
                    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <div style='color: rgba(255,255,255,0.7); font-size: 0.9em; margin-bottom: 6px;'>
                        💳 Estimated Monthly EMI
                    </div>
                    <div style='color: #c4b5fd; font-size: 2em; font-weight: 800; 
                                font-family: monospace;'>₹{estimated_emi:,.2f}</div>
                </div>
                <div style='text-align: right;'>
                    <div style='color: rgba(255,255,255,0.7); font-size: 0.9em; margin-bottom: 6px;'>
                        📊 Interest Rate
                    </div>
                    <div style='color: #c4b5fd; font-size: 1.5em; font-weight: 700;'>{rate}% p.a.</div>
                </div>
            </div>
            <div style='margin-top: 15px; padding-top: 15px; 
                        border-top: 1px solid rgba(139, 92, 246, 0.4);'>
                <span style='color: rgba(255,255,255,0.7); font-size: 0.9em;'>
                    💰 Total Amount Payable: <strong style='color: #c4b5fd;'>₹{(estimated_emi * tenure):,.2f}</strong>
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Continue →", use_container_width=True):
            st.session_state.app_data["loan_amount"] = loan_amount
            st.session_state.app_data["tenure"] = tenure
            st.session_state.app_data["emi"] = estimated_emi
            
            add_message("user", f"I need {format_currency(loan_amount)} for {tenure} months (EMI: ₹{estimated_emi:,.2f})")
            
            msg = st.session_state.master_agent.get_message("COLLECT_PAN")
            add_message("agent", msg)
            
            st.session_state.waiting_for = "pan"
            st.rerun()

# Continuation of app.py - PAN entry onwards

# PAN ENTRY
elif st.session_state.waiting_for == "pan":
    with render_widget_container():
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(99, 102, 241, 0.15)); 
                    padding: 25px; border-radius: 15px; margin: 20px 0;
                    border: 2px solid rgba(139, 92, 246, 0.3);
                    box-shadow: 0 6px 20px rgba(0,0,0,0.2);'>
            <h3 style='color: #c4b5fd; margin-top: 0; display: flex; align-items: center; gap: 10px;'>
                🔐 Identity Verification
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("🔒 Your PAN is required for credit verification and regulatory compliance. All data is encrypted and secure.")
        
        pan = st.text_input(
            "Enter PAN Number",
            max_chars=10,
            placeholder="ABCDE1234F",
            help="10-character PAN format: 5 letters, 4 digits, 1 letter"
        ).upper()
        
        # Real-time validation feedback
        if pan:
            if validate_pan(pan):
                st.success("✅ Valid PAN format")
            else:
                st.error("❌ Invalid PAN format. Expected: ABCDE1234F")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Verify PAN →", use_container_width=True, disabled=not validate_pan(pan)):
            st.session_state.app_data["pan"] = pan
            add_message("user", f"PAN: {pan}")
            st.session_state.chat_history.append({"type": "loading", "agent": "Verification"})
            st.session_state.waiting_for = "verification_processing"
            st.rerun()


# VERIFICATION AGENT
elif st.session_state.waiting_for == "verification_processing":
    time.sleep(3)  # Simulate processing time
    pan = st.session_state.app_data["pan"]
    
    try:
        bureau_data, cibil_report = verify_pan(pan)
        st.session_state.chat_history.pop()  # Remove loading indicator
        
        if bureau_data:
            st.session_state.app_data.update({
                "name": bureau_data["name"],
                "credit_score": bureau_data["credit_score"],
                "existing_emi": bureau_data["existing_emi"],
                "pre_approved_limit": bureau_data["preapproved_limit"],
                "monthly_salary": bureau_data.get("monthly_income", 80000)
            })
            
            log_event("VERIFICATION_SUCCESS", bureau_data["name"], "INFO")
            
            # Enhanced verification message
            score = bureau_data["credit_score"]
            score_emoji = "🟢" if score >= 750 else "🟡" if score >= 650 else "🔴"
            
            add_message(
                "system",
                f"✅ Verification Successful\n\n"
                f"Welcome, **{bureau_data['name']}**!\n\n"
                f"{score_emoji} **CIBIL Score:** {score}\n\n"
                f"💳 **Pre-approved Limit:** {format_currency(bureau_data['preapproved_limit'])}\n"
                f"💰 **Existing EMI:** {format_currency(bureau_data['existing_emi'])}/month"
            )
            
            st.session_state.chat_history.append({
                "type": "report",
                "content": cibil_report,
                "download_data": True
            })
            
            msg = st.session_state.master_agent.get_message("VERIFICATION_DONE", bureau_data)
            add_message("agent", msg)
            
            st.session_state.waiting_for = "underwriting_trigger"
            st.rerun()
            
        else:
            log_event("VERIFICATION_FAILED", pan, "WARNING")
            add_message("system", "❌ Verification Failed\n\nUnable to verify PAN. Please check and try again.")
            st.session_state.waiting_for = "pan"
            st.rerun()
            
    except Exception as e:
        log_event("VERIFICATION_ERROR", str(e), "ERROR")
        add_message("system", "❌ System Error \n\nPlease try again or contact support.")
        st.session_state.waiting_for = "pan"
        st.rerun()


# UNDERWRITING
elif st.session_state.waiting_for == "underwriting_trigger":
    st.session_state.chat_history.append({"type": "loading", "agent": "Underwriting"})
    time.sleep(3)
    st.session_state.chat_history.pop()
    
    try:
        uw_result = run_underwriting(
            loan_amount=st.session_state.app_data["loan_amount"],
            tenure=st.session_state.app_data["tenure"],
            credit_score=st.session_state.app_data["credit_score"],
            existing_emi=st.session_state.app_data["existing_emi"],
            income=st.session_state.app_data["monthly_salary"],
            employment_type=st.session_state.app_data["employment_type"],
            loan_purpose=st.session_state.app_data["loan_purpose"],
            preapproved_limit=st.session_state.app_data["pre_approved_limit"]
        )
        
        decision = uw_result["decision"]
        log_event("UNDERWRITING_DECISION", decision, "INFO")
        
        st.session_state.app_data.update(uw_result)
        
        # Enhanced decision badge
        if decision == "APPROVED":
            badge_color = "#22c55e"
            badge_bg = "rgba(34, 197, 94, 0.2)"
            badge_icon = "✅"
        elif decision == "REJECTED":
            badge_color = "#ef4444"
            badge_bg = "rgba(239, 68, 68, 0.2)"
            badge_icon = "❌"
        else:
            badge_color = "#f59e0b"
            badge_bg = "rgba(245, 158, 11, 0.2)"
            badge_icon = "⏳"
        
        add_message(
            "system",
            f"""
            <div style='background: {badge_bg}; 
                        padding: 20px; border-radius: 12px;
                        border: 2px solid {badge_color};
                        box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
                <div style='color: {badge_color}; font-size: 1.3em; font-weight: 800; 
                            display: flex; align-items: center; gap: 10px;'>
                    {badge_icon} Underwriting Decision: {decision}
                </div>
            </div>
            """
        )
        
        # Handle rejection with AI explanation
        if decision == "REJECTED":
            reject_prompt = f"""
            You are a compassionate loan officer. A customer's loan application was rejected. Explain why in a supportive tone.

            Customer Details:
            - Loan Amount Requested: ₹{st.session_state.app_data['loan_amount']:,}
            - Tenure: {st.session_state.app_data['tenure']} months
            - Credit Score: {st.session_state.app_data['credit_score']}
            - Monthly Income: ₹{st.session_state.app_data['monthly_salary']:,}
            - Existing EMI: ₹{st.session_state.app_data['existing_emi']:,}
            - Pre-approved Limit: ₹{st.session_state.app_data['pre_approved_limit']:,}

            Decision: REJECTED

            Provide:
            1. A polite, empathetic explanation (2-3 sentences) short and crisp
            2. Specific reasons (e.g., low credit score, high FOIR, exceeds pre-approved limit)
            3. Actionable suggestions to improve (e.g., improve credit score, reduce existing EMI, apply for lower amount)

            Keep it professional, supportive, and under 100 words.
            """
            
            try:
                ai_explanation = get_llama_response(reject_prompt)
                add_message("agent", ai_explanation)
            except:
                add_message("agent", "Unfortunately, we're unable to approve your loan at this time. Please contact our support team for more details.")
            
            st.session_state.waiting_for = None
            st.rerun()
        
        # Need documents
        elif decision == "NEED_SALARY_SLIP":
            add_message(
                "agent",
                "📄 To proceed further, I'll need to verify your income.\n\n"
                "Please upload your latest **salary slip** or **bank statement** (last 3 months)."
            )
            st.session_state.waiting_for = "document_upload"
            st.rerun()
        
        # Approved
        elif decision == "APPROVED":
            add_message("agent", "🎉 **Great news!** Your loan has been approved. Let me generate your sanction letter...")
            st.session_state.waiting_for = "sanction_letter"
            st.rerun()
            
    except Exception as e:
        log_event("UNDERWRITING_ERROR", str(e), "ERROR")
        add_message("system", "❌ System error during underwriting. Please try again.")
        st.session_state.waiting_for = None
        st.rerun()


# DOCUMENT UPLOAD
elif st.session_state.waiting_for == "document_upload":
    with render_widget_container():
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(99, 102, 241, 0.15)); 
                    padding: 25px; border-radius: 15px; margin: 20px 0;
                    border: 2px solid rgba(139, 92, 246, 0.3);
                    box-shadow: 0 6px 20px rgba(0,0,0,0.2);'>
            <h3 style='color: #c4b5fd; margin-top: 0; display: flex; align-items: center; gap: 10px;'>
                📄 Document Upload
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("📌 **Accepted formats:** PDF, JPG, PNG | **Max size:** 5MB")
        
        uploaded = st.file_uploader(
            "Upload Salary Slip / Bank Statement",
            type=["pdf", "jpg", "png", "jpeg"],
            help="Latest salary slip or last 3 months bank statement"
        )
        
        if uploaded:
            st.success(f"✅ File uploaded: **{uploaded.name}** ({uploaded.size / 1000:.1f} KB)")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Verify Document →", use_container_width=True):
                st.session_state.uploaded_file = uploaded
                st.session_state.chat_history.append({"type": "loading", "agent": "Document Verification"})
                st.session_state.waiting_for = "document_verification"
                st.rerun()


# DOCUMENT VERIFICATION
elif st.session_state.waiting_for == "document_verification":
    time.sleep(2)
    
    try:
        result = verify_salary_slip(st.session_state.uploaded_file)
        st.session_state.chat_history.pop()  # Remove loading
        
        verified, message = result
        log_event("DOCUMENT_VERIFICATION", f"Verified: {verified}", "INFO")
        
        if verified:
            add_message("agent", f"✅ **Document Verified Successfully!**\n\n{message}")
            
            # Recalculate eligibility
            salary = st.session_state.app_data["monthly_salary"]
            emi = st.session_state.app_data["emi"]
            existing_emi = st.session_state.app_data.get("existing_emi", 0)
            
            total_emi = emi + existing_emi
            foir = (total_emi / salary) * 100
            
            if foir <= 50:
                st.session_state.app_data["decision"] = "APPROVED"
                add_message("system", f"✅ FOIR Check Passed ({foir:.1f}% ≤ 50%)")
            else:
                st.session_state.app_data["decision"] = "REJECTED"
                add_message("system", f"❌ FOIR Check Failed ({foir:.1f}% > 50%)")
            
            st.session_state.waiting_for = "sanction_letter"
            st.rerun()
            
        else:
            add_message("agent", f"❌ **Document Verification Failed**\n\n{message}\n\nPlease upload a valid document.")
            st.session_state.waiting_for = "document_upload"
            st.rerun()
            
    except Exception as e:
        log_event("DOCUMENT_ERROR", str(e), "ERROR")
        add_message("system", "❌ Error processing document. Please try again.")
        st.session_state.waiting_for = "document_upload"
        st.rerun()


# SANCTION LETTER
elif st.session_state.waiting_for == "sanction_letter":
    try:
        if st.session_state.app_data.get("decision") == "APPROVED":
            sanction_text = create_sanction_letter(st.session_state.app_data)
            
            log_event("SANCTION_GENERATED", st.session_state.application_id, "INFO")
            
            st.session_state.chat_history.append({
                "type": "sanction",
                "content": sanction_text
            })
            
            # Calculate total time taken
            time_taken = (datetime.now() - st.session_state.start_time).seconds // 60
            
            add_message(
                "agent",
                f"""
🎊 Congratulations! Your loan has been sanctioned!

Your sanction letter is ready for download. Here's what happens next:

**Next Steps:**
1. ✅ Download your sanction letter
2. 📧 Check your email for detailed terms
3. 🔏 Complete KYC verification (if required)
4. 💳 Loan disbursement within 24-48 hours

**Application Summary:**
- ⏱️ Time taken: ~{time_taken} minutes
- 💰 Sanctioned Amount: {format_currency(st.session_state.app_data['loan_amount'])}
- 📅 Tenure: {st.session_state.app_data['tenure']} months
- 💳 EMI: ₹{st.session_state.app_data['emi']:,.2f}

Thank you for choosing LoanFlow AI! 🙏

*Need help? Contact our support team 24/7.*
                """
            )
            
        else:
            add_message(
                "agent",
                "Unfortunately, we couldn't approve your loan at this time. "
                "Please review the reasons above and feel free to reapply after addressing them."
            )
        
        st.session_state.waiting_for = None
        st.rerun()
        
    except Exception as e:
        log_event("SANCTION_ERROR", str(e), "ERROR")
        add_message("system", "❌ Error generating sanction letter. Please contact support.")
        st.session_state.waiting_for = None
        st.rerun()


# ========================================
# ENHANCED FOOTER
# ========================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 25px; 
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(99, 102, 241, 0.08)); 
            border-radius: 12px; margin-top: 30px;
            border: 1px solid rgba(139, 92, 246, 0.2);'>
    <p style='color: rgba(255,255,255,0.7); font-size: 1em; margin-bottom: 12px;'>
        🔒 <strong>Secure & Encrypted</strong> | 
        💬 <strong>24/7 Support</strong> | 
        ⚡ <strong>Instant Approvals</strong>
    </p>
    <p style='margin-top: 15px; color: rgba(255,255,255,0.5); font-size: 0.9em;'>
        © 2025 LoanFlow AI. All rights reserved.
    </p>
    <p style='margin-top: 8px; font-size: 0.85em; color: rgba(255,255,255,0.4);'>
        By using this service, you agree to our <a href="#" style='color: #8b5cf6;'>Terms of Service</a> 
        and <a href="#" style='color: #8b5cf6;'>Privacy Policy</a>
    </p>
</div>
""", unsafe_allow_html=True)