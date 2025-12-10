import streamlit as st

from agents.sales_agent import collect_sales_info
from agents.verification_agent import verify_pan
from agents.underwriting_agent import run_underwriting
from agents.document_agent import verify_salary_slip
from agents.sanction_agent import create_sanction_letter

from theme.theme import load_theme, render_header, render_agent_card, metric_box


# --------------------------------------------------
# INITIALIZE THEME & HEADER
# --------------------------------------------------
st.set_page_config(page_title="LoanFlow AI", page_icon="🏦", layout="wide")

load_theme()          # <-- APPLY CSS THEME
render_header()       # <-- SHOW GRADIENT HEADER


# --------------------------------------------------
# SESSION INITIALIZATION
# --------------------------------------------------
if "flow_step" not in st.session_state:
    st.session_state.flow_step = 1

for key in ["sales_data", "verification_data", "underwriting_data", "document_data", "sanction_data"]:
    if key not in st.session_state:
        st.session_state[key] = None


# --------------------------------------------------
# TOP METRICS (APPLICATION ID, STAGE, PROGRESS)
# --------------------------------------------------
if "application_id" not in st.session_state:
    import random
    st.session_state.application_id = f"LF{random.randint(10000,99999)}"

colA, colB, colC = st.columns(3)
with colA:
    metric_box("Application ID", st.session_state.application_id)

with colB:
    metric_box("Current Stage", f"Step {st.session_state.flow_step}", color="#8b5cf6")

with colC:
    completed = sum([
        st.session_state.sales_data is not None,
        st.session_state.verification_data is not None,
        st.session_state.underwriting_data is not None,
        st.session_state.document_data is not None,
        st.session_state.sanction_data is not None
    ])
    metric_box("Progress", f"{completed}/5 Agents", color="#10b981")

st.divider()


# --------------------------------------------------
# HELPER — Styled Section Header
# --------------------------------------------------
def section_header(title):
    return f"<h2 style='color:#2D7FF9; font-weight:700; margin-top:15px; margin-bottom:10px;'>{title}</h2>"


# --------------------------------------------------
# LEFT COLUMN AGENT STATUS
# --------------------------------------------------
def render_agent_sidebar():
    st.markdown("### 🤖 Agent Status")

    render_agent_card("Sales Agent", "🤝", "complete" if st.session_state.sales_data else "idle")
    render_agent_card("Verification Agent", "🔍", "complete" if st.session_state.verification_data else "idle")
    render_agent_card("Underwriting Agent", "⚖️", "complete" if st.session_state.underwriting_data else "idle")
    render_agent_card("Document Agent", "📄", "complete" if st.session_state.document_data else "idle")
    render_agent_card("Sanction Agent", "📋", "complete" if st.session_state.sanction_data else "idle")


# --------------------------------------------------
# STEP 1 — SALES AGENT
# --------------------------------------------------
def step_sales():
    st.markdown(section_header("Step 1: Loan Details"), unsafe_allow_html=True)

    amount = st.number_input("Loan Amount", min_value=10000)
    purpose = st.selectbox("Purpose", ["Education", "Business", "Home", "Personal", "Medical"])
    tenure = st.selectbox("Tenure (months)", [12, 24, 36, 48, 60])

    if st.button("Next → Verification"):
        st.session_state.sales_data = collect_sales_info(amount, purpose, tenure)
        st.session_state.flow_step = 2
        st.rerun()


# --------------------------------------------------
# STEP 2 — VERIFICATION AGENT
# --------------------------------------------------
def step_verification():
    st.markdown(section_header("Step 2: PAN Verification"), unsafe_allow_html=True)

    pan = st.text_input("Enter PAN (ABCDE1234F)")

    if st.button("Verify PAN"):
        details, error = verify_pan(pan)

        if error:
            st.error(error)
        else:
            st.session_state.verification_data = details
            st.success("PAN verified successfully!")
            st.json(details)
            st.session_state.flow_step = 3
            st.rerun()


# --------------------------------------------------
# STEP 3 — UNDERWRITING AGENT
# --------------------------------------------------
def step_underwriting():
    st.markdown(section_header("Step 3: Underwriting Check"), unsafe_allow_html=True)

    income = st.number_input("Monthly Income", min_value=5000)
    emp_type = st.selectbox("Employment Type", ["Salaried", "Self-Employed", "Business Owner"])

    if st.button("Run Underwriting"):
        sales = st.session_state.sales_data
        verify = st.session_state.verification_data

        result = run_underwriting(
            loan_amount=sales["loan_amount"],
            tenure=sales["loan_tenure"],
            credit_score=verify["credit_score"],
            existing_emi=verify["existing_emi"],
            income=income,
            employment_type=emp_type,
            loan_purpose=sales["loan_purpose"]
        )

        st.session_state.underwriting_data = result

        if result["decision"] == "APPROVED":
            st.success("Loan Approved!")
            st.json(result)
            st.session_state.flow_step = 4
            st.rerun()
        else:
            st.error("Loan Rejected")
            st.warning(result["reason"])


# --------------------------------------------------
# STEP 4 — DOCUMENT AGENT
# --------------------------------------------------
def step_documents():
    st.markdown(section_header("Step 4: Upload Documents"), unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload Salary Slip (PDF/Image)")

    if st.button("Verify Document"):
        ok, msg = verify_salary_slip(uploaded)

        if not ok:
            st.error(msg)
        else:
            st.success(msg)
            st.session_state.document_data = msg
            st.session_state.flow_step = 5
            st.rerun()


# --------------------------------------------------
# STEP 5 — SANCTION AGENT
# --------------------------------------------------
def step_sanction():
    st.markdown(section_header("Step 5: Sanction Letter"), unsafe_allow_html=True)

    sales = st.session_state.sales_data
    uw = st.session_state.underwriting_data

    data = {
        "Loan Amount": sales["loan_amount"],
        "Tenure": sales["loan_tenure"],
        "Interest Rate": uw["interest_rate"],
        "EMI": uw["emi"],
        "Decision": uw["decision"]
    }

    if st.button("Generate Sanction Letter"):
        filename = create_sanction_letter(data)

        with open(filename, "rb") as f:
            st.download_button("Download PDF", f, file_name=filename)

        st.success("Sanction Letter Generated!")
        st.session_state.sanction_data = filename
        st.session_state.flow_step = 6
        st.rerun()


# --------------------------------------------------
# STEP 6 — COMPLETE
# --------------------------------------------------
def step_complete():
    st.success("Loan Processing Completed 🎉")
    st.markdown("Thank you for using LoanFlow AI!")


# --------------------------------------------------
# MAIN LAYOUT: 2 COLUMNS (Agents | Active Step)
# --------------------------------------------------
left, right = st.columns([1, 2])

with left:
    render_agent_sidebar()

with right:
    step_map = {
        1: step_sales,
        2: step_verification,
        3: step_underwriting,
        4: step_documents,
        5: step_sanction,
        6: step_complete
    }
    step_map[st.session_state.flow_step]()
