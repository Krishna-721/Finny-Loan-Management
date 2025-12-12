# theme/chat_ui.py

import streamlit as st

def render_chat_message(role, content, message_type="text"):
    """
    Render a chat message bubble
    role: 'user', 'agent', 'system'
    message_type: 'text', 'widget', 'report'
    """
    
    if role == "user":
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
            padding: 15px 20px;
            border-radius: 18px;
            margin: 10px 0 10px 40%;
            animation: fadeIn 0.3s;
            box-shadow: 0 2px 8px rgba(99,102,241,0.3);
        '>
            <div style='font-weight: 500;'>👤 You</div>
            <div style='margin-top: 5px;'>{content}</div>
        </div>
        """, unsafe_allow_html=True)
    
    elif role == "agent":
        st.markdown(f"""
        <div style='
            background: rgba(139, 92, 246, 0.2);
            border-left: 4px solid #8b5cf6;
            color: #E8EAED;
            padding: 15px 20px;
            border-radius: 18px;
            margin: 10px 40% 10px 0;
            animation: fadeIn 0.3s;
        '>
            <div style='font-weight: 600; color: #8b5cf6;'>🤖 Agent Finn</div>
            <div style='margin-top: 5px;'>{content}</div>
        </div>
        """, unsafe_allow_html=True)
    
    elif role == "system":
        st.markdown(f"""
        <div style='
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #10b981;
            padding: 12px 20px;
            border-radius: 12px;
            margin: 10px 15%;
            text-align: center;
            font-size: 0.9rem;
            animation: fadeIn 0.3s;
        '>
            ⚙️ {content}
        </div>
        """, unsafe_allow_html=True)


def render_agent_loading(agent_name):
    """Show loading indicator for active agent"""
    
    icons = {
        "Verification": "🔍",
        "Underwriting": "⚖️",
        "Document": "📄",
        "Sanction": "📋"
    }
    
    icon = icons.get(agent_name, "🤖")
    
    st.markdown(f"""
    <div style='
        background: rgba(139, 92, 246, 0.2);
        border-left: 4px solid #8b5cf6;
        padding: 15px 20px;
        border-radius: 12px;
        margin: 10px 40% 10px 0;
        animation: pulse 1.5s infinite;
    '>
        <div style='font-weight: 600; color: #8b5cf6;'>{icon} {agent_name} Agent</div>
        <div style='margin-top: 8px; display: flex; align-items: center; gap: 10px;'>
            <div class='loading-spinner'></div>
            <span>Processing...</span>
        </div>
    </div>
    
    <style>
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}
    
    .loading-spinner {{
        width: 16px;
        height: 16px;
        border: 2px solid rgba(139, 92, 246, 0.3);
        border-top-color: #8b5cf6;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }}
    
    @keyframes spin {{
        to {{ transform: rotate(360deg); }}
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    """, unsafe_allow_html=True)


def render_widget_container():
    """Container for widgets that appear in chat"""
    return st.container() 