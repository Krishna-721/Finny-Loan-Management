import streamlit as st

# ================================
# GLOBAL THEME INITIALIZATION
# ================================
def load_theme():
    """Inject global CSS styles for LoanFlow AI UI."""
    st.markdown("""
    <style>

    /* Global background */
    .main { 
        background: linear-gradient(135deg, #0a0e27, #1a1f3a); 
        color: #E8EAED; 
    }

    /* Agent cards (status on left side) */
    .agent-card {
        background: rgba(30, 35, 60, 0.8);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #6366f1;
        margin: 10px 0;
    }

    .agent-card.working { 
        border-left-color: #8b5cf6; 
        background: rgba(139, 92, 246, 0.2); 
        animation: pulse 2s infinite; 
    }

    .agent-card.complete { 
        border-left-color: #10b981; 
        background: rgba(16, 185, 129, 0.2); 
    }

    .agent-card.error { 
        border-left-color: #ef4444; 
        background: rgba(239, 68, 68, 0.15); 
    }

    @keyframes pulse { 
        0%, 100% { opacity: 1; } 
        50% { opacity: 0.7; } 
    }

    /* Top metrics bar boxes */
    .metric-box { 
        background: rgba(139, 92, 246, 0.2); 
        border-radius: 8px; 
        padding: 15px; 
        text-align: center; 
    }

    </style>
    """, unsafe_allow_html=True)


# ================================
# HEADER BLOCK
# ================================
def render_header():
    """Renders the purple gradient LoanFlow AI title bar."""
    st.markdown("""
    <div style='text-align: center; 
                padding: 20px; 
                background: linear-gradient(135deg, #8b5cf6, #6366f1); 
                border-radius: 10px; 
                margin-bottom: 30px;'>
        <h1 style='color: white; margin: 0;'>🏦 LoanFlow AI</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0;'>
            5-Agent Intelligent Loan Processing System
        </p>
    </div>
    """, unsafe_allow_html=True)


# ================================
# AGENT STATUS CARD
# ================================
def render_agent_card(agent_name, icon, status, result=None):
    """Reusable agent card for the left sidebar."""
    
    status_map = {
        "idle": "⚪",
        "working": "🔵",
        "complete": "✅",
        "error": "❌"
    }

    status_icon = status_map.get(status, "⚪")

    card_class = f"agent-card {status}"

    result_html = (
        f"<div style='margin-top: 10px; font-size: 0.9rem; color: #10b981;'>{result}</div>"
        if result else ""
    )

    st.markdown(f"""
    <div class='{card_class}'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div><span style='font-size: 1.5rem;'>{icon}</span> 
            <strong>{agent_name}</strong></div>
            <div style='font-size: 1.5rem;'>{status_icon}</div>
        </div>
        {result_html}
    </div>
    """, unsafe_allow_html=True)


# ================================
# TOP METRIC BOX
# (Application ID / Stage / Progress)
# ================================
def metric_box(label, value, color=None):
    """Renders a metric block with optional highlight color."""
    
    color_style = f"color:{color}; font-weight:bold;" if color else "font-weight:bold;"

    st.markdown(f"""
    <div class='metric-box'>
        <div style='opacity:0.8;'>{label}</div>
        <div style='font-size: 1.2rem; {color_style}'>{value}</div>
    </div>
    """, unsafe_allow_html=True)