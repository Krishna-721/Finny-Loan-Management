import streamlit as st

def metric_box(label, value):
    st.markdown(
        f"""
        <div class="metric-box">
            <div style="opacity: 0.8;">{label}</div>
            <div style="font-size: 1.2rem; font-weight: bold;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


#def agent_card(agent_name, icon, status, result=None):
#    """
#    status → idle / working / complete / error
#    result → optional text that appears under card
#    """
#
#    status_map = {
#        "idle": "⚪",
#        "working": "🔵",
#        "complete": "✅",
#        "error": "❌"
#    }
#
#    st.markdown(
#        f"""
#        <div class="agent-card {status}">
#            <div class="agent-card-title">
#                <span>{icon} <strong>{agent_name}</strong></span>
#                <span style="font-size: 1.4rem;">{status_map.get(status, "⚪")}</span>
#            </div>
#
#            {f"<div class='agent-result'>{result}</div>" if result else ""}
#        </div>
#        """,
#        unsafe_allow_html=True
###    )


def section_title(icon, title):
    st.markdown(
        f"""
        <div class="section-title">{icon} {title}</div>
        """,
        unsafe_allow_html=True
    )
