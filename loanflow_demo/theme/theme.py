import streamlit as st

def apply_theme():
    """Apply modern dark theme with glassmorphism effects"""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@700&display=swap');

    /* Base Dark Theme */
    html, body, .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%) !important;
        color: #E8EAED !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px !important;
    }

    /* Modern Cards with Glassmorphism */
    .fintech-card {
        background: rgba(30, 35, 60, 0.7) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 16px !important;
        padding: 28px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .fintech-card:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 40px rgba(139, 92, 246, 0.2) !important;
        border-color: rgba(139, 92, 246, 0.5) !important;
    }

    /* Input Fields - Modern Dark */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(20, 25, 45, 0.8) !important;
        border: 1.5px solid rgba(139, 92, 246, 0.4) !important;
        border-radius: 10px !important;
        color: #E8EAED !important;
        padding: 14px 18px !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: rgba(139, 92, 246, 0.8) !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
    }
    
    /* Buttons - Gradient Style */
    div.stButton > button {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4) !important;
        background: linear-gradient(135deg, #9d6ff8 0%, #7477f3 100%) !important;
    }
    
    /* Stepper - Modern Design */
    .stepper-container {
        display: flex;
        justify-content: space-between;
        margin: 35px 0;
        position: relative;
        padding: 0 20px;
    }
    
    .stepper-container::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 2px;
        background: rgba(139, 92, 246, 0.2);
        z-index: 0;
    }
    
    .step {
        flex: 1;
        text-align: center;
        font-size: 0.9rem;
        font-weight: 600;
        color: #666B7A;
        position: relative;
        z-index: 1;
    }
    
    .step::before {
        content: '';
        display: block;
        width: 40px;
        height: 40px;
        margin: 0 auto 12px;
        background: rgba(30, 35, 60, 0.8);
        border: 2px solid rgba(139, 92, 246, 0.3);
        border-radius: 50%;
        transition: all 0.3s ease;
    }
    
    .step.active {
        color: #8b5cf6;
    }
    
    .step.active::before {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        border-color: #8b5cf6;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
    }
    
    .step.completed {
        color: #10b981;
    }
    
    .step.completed::before {
        background: #10b981;
        border-color: #10b981;
    }

    /* Metric Boxes - Neon Glow */
    .metric-box {
        text-align: center;
        padding: 24px;
        background: rgba(20, 25, 45, 0.6);
        border-radius: 12px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        transition: all 0.3s ease;
    }
    
    .metric-box:hover {
        transform: translateY(-4px);
        border-color: rgba(139, 92, 246, 0.5);
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 12px 0;
    }
    
    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #9CA3AF;
        font-weight: 600;
    }

    /* Progress Bar */
    .progress-bar {
        width: 100%;
        height: 6px;
        background: rgba(139, 92, 246, 0.1);
        border-radius: 10px;
        overflow: hidden;
        margin: 12px 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #8b5cf6, #6366f1, #10b981);
        border-radius: 10px;
        transition: width 0.5s ease;
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
    }

    /* Chat Bubbles */
    .chat-bubble {
        padding: 14px 18px;
        border-radius: 14px;
        margin: 10px 0;
        max-width: 85%;
        animation: slideIn 0.3s ease;
    }
    
    .chat-user {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        color: white;
        margin-left: auto;
        text-align: right;
        border-bottom-right-radius: 4px;
    }
    
    .chat-ai {
        background: rgba(30, 35, 60, 0.8);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-bottom-left-radius: 4px;
    }

    /* Slider Styling */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #8b5cf6, #6366f1) !important;
    }

    /* File Upload */
    .uploadedFile {
        border: 1px solid rgba(16, 185, 129, 0.5) !important;
        background: rgba(20, 25, 45, 0.6) !important;
        border-radius: 10px !important;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(139, 92, 246, 0.3); }
        50% { box-shadow: 0 0 30px rgba(139, 92, 246, 0.6); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease;
    }
    
    .glow {
        animation: glow 2s ease-in-out infinite;
    }

    /* Header Gradient Text */
    .gradient-text {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 50%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(20, 25, 45, 0.6);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #9CA3AF;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        color: white;
    }

    /* Info/Warning boxes */
    .stAlert {
        background: rgba(30, 35, 60, 0.8) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 10px !important;
    }

    /* Checkbox styling */
    .stCheckbox {
        color: #E8EAED !important;
    }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)