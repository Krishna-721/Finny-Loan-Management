import streamlit as st
import random
import time
from ai.advisor import get_llama_response
from theme.theme import apply_theme
from logic.interest import calculate_base_interest_rate
from logic.underwriting import run_underwriting_engine
from logic.validation import validate_email, validate_phone, validate_financials
from logic.utils import calculate_emi, sanitize_input, secure_log, render_header, render_stepper, render_applicant_summary
from logic.sanction_agent import generate_sanction_letter
from logic.verification_agent import verify_applicant
# ================================

st.set_page_config(
    page_title="Finny AI | Loan Agent",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_theme()

# ================================
# SESSION STATE INITIALIZATION
# ================================
if "step" not in st.session_state:
    st.session_state.step = 1

if "app_data" not in st.session_state:
    st.session_state.app_data = {
        "name": "", "email": "", "phone": "",
        "income": 0, "loan_amount": 0, "tenure": 12,
        "rate": 10.5, "employment": "Salaried",
        "existing_emis": 0, "credit_score": 0,
        "purpose": "Personal", "address": "",
    }

if "co_applicant" not in st.session_state:
    st.session_state.co_applicant = {
        "enabled": False, "name": "", "email": "", "phone": "",
        "income": 0, "employment": "Salaried", "relationship": "Spouse",
    }

if "docs_status" not in st.session_state:
    st.session_state.docs_status = {
        "Identity": False, "Income": False, "Collateral": False,
        "identity_file": None, "income_file": None, "collateral_file": None,
    }

if "logs" not in st.session_state:
    st.session_state.logs = []

if "underwriting_result" not in st.session_state:
    st.session_state.underwriting_result = None

if "application_id" not in st.session_state:
    st.session_state.application_id = f"LF{random.randint(10000, 99999)}"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

render_header()
render_applicant_summary()
render_stepper()

# ======================================================
# STEP 1 – APPLICATION DETAILS
# ======================================================
if st.session_state.step == 1:
    st.markdown("### 📝 Application Details")
    
    col_form, col_calc = st.columns([2, 1])
    
    with col_form:
        st.markdown('<div class="fintech-card fade-in">', unsafe_allow_html=True)
        st.markdown("#### Personal Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", 
                                value=st.session_state.app_data['name'] if st.session_state.app_data['name'] else "",
                                placeholder="Enter your full name")
            email = st.text_input("Email Address *",
                                 value=st.session_state.app_data['email'] if st.session_state.app_data['email'] else "",
                                 placeholder="your.email@example.com")
            phone = st.text_input("Phone Number *",
                                 value=st.session_state.app_data['phone'] if st.session_state.app_data['phone'] else "",
                                 placeholder="9876543210", max_chars=10)
            
            PAN = st.text_input("PAN Number *", placeholder="ABCDE1234F")
        
        with col2:
            emp_type = st.selectbox("Employment Type *",
                                   ["Salaried", "Self-Employed", "Business Owner"],
                                   index=["Salaried", "Self-Employed", "Business Owner"].index(
                                       st.session_state.app_data["employment"]))
            
            purpose = st.selectbox("Loan Purpose *",
                                  ["Personal", "Home", "Business", "Education", "Medical"],
                                  index=["Personal", "Home", "Business", "Education", "Medical"].index(
                                      st.session_state.app_data["purpose"]))
            
            address = st.text_input("City",
                                   value=st.session_state.app_data['address'] if st.session_state.app_data['address'] else "",
                                   placeholder="Enter your city")
        
        st.divider()
        st.markdown("#### Financial Details")
        
        col3, col4 = st.columns(2)
        
        with col3:
            income = st.number_input("Annual Income (₹) *",
                                    min_value=0, max_value=50000000, step=50000,
                                    value=int(st.session_state.app_data['income']) if st.session_state.app_data['income'] > 0 else 0,
                                    placeholder="Enter annual income",
                                    help="Your total annual income from all sources")
            
            existing_emis = st.number_input("Existing Monthly EMIs (₹)",
                                           min_value=0, max_value=500000, step=1000,
                                           value=int(st.session_state.app_data['existing_emis']),
                                           placeholder="Total of existing EMIs")
        
        with col4:
            amount = st.number_input("Loan Amount Requested (₹) *",
                                    min_value=0, max_value=10000000, step=25000,
                                    value=int(st.session_state.app_data['loan_amount']) if st.session_state.app_data['loan_amount'] > 0 else 0,
                                    placeholder="Enter loan amount")
            
            tenure = st.slider("Tenure (Months) *", 6, 120,
                              int(st.session_state.app_data['tenure']) if st.session_state.app_data['tenure'] >= 6 else 12)
        
        # Co-Applicant Section
        st.divider()
        st.markdown("#### 👥 Co-Applicant (Optional)")
        
        co_toggle = st.checkbox("Add Co-Applicant",
                               value=st.session_state.co_applicant['enabled'],
                               help="Improves eligibility with combined income")
        
        st.session_state.co_applicant['enabled'] = co_toggle
        
        # Initialize variables to avoid NameError
        co_income = 0
        co_name = ""
        co_email = ""
        co_phone = ""
        co_relationship = "Spouse"
        co_employment = "Salaried"

        if co_toggle:
            st.markdown('<div style="padding: 15px; background: rgba(139, 92, 246, 0.1); border-left: 3px solid #8b5cf6; border-radius: 8px; margin: 10px 0;">', unsafe_allow_html=True)
            st.caption("💡 **Benefits**: Better FOIR, -0.5% rate discount, +40 credit score")
            
            co_col1, co_col2 = st.columns(2)
            
            with co_col1:
                co_name = st.text_input("Co-Applicant Name *",
                                       value=st.session_state.co_applicant['name'] if st.session_state.co_applicant['name'] else "",
                                       placeholder="Enter co-applicant name", key="co_name")
                co_email = st.text_input("Co-Applicant Email *",
                                        value=st.session_state.co_applicant['email'] if st.session_state.co_applicant['email'] else "",
                                        placeholder="co-applicant@example.com", key="co_email")
                co_phone = st.text_input("Co-Applicant Phone *",
                                        value=st.session_state.co_applicant['phone'] if st.session_state.co_applicant['phone'] else "",
                                        placeholder="9876543210", max_chars=10, key="co_phone")
            
            with co_col2:
                co_relationship = st.selectbox("Relationship *",
                                              ["Spouse", "Parent", "Sibling", "Child", "Business Partner"],
                                              index=["Spouse", "Parent", "Sibling", "Child", "Business Partner"].index(
                                                  st.session_state.co_applicant['relationship']), key="co_rel")
                co_employment = st.selectbox("Co-Applicant Employment *",
                                            ["Salaried", "Self-Employed", "Business Owner"],
                                            index=["Salaried", "Self-Employed", "Business Owner"].index(
                                                st.session_state.co_applicant['employment']), key="co_emp")
                co_income = st.number_input("Co-Applicant Annual Income (₹) *",
                                           min_value=0, max_value=50000000, step=50000,
                                           value=int(st.session_state.co_applicant['income']) if st.session_state.co_applicant['income'] > 0 else 0,
                                           placeholder="Enter co-applicant income", key="co_inc")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Calculate rate
        total_calc_income = income
        if co_toggle and co_income > 0:
            total_calc_income = income + co_income
        
        calculated_rate = calculate_base_interest_rate(tenure, emp_type, purpose, amount)
        if co_toggle:
            calculated_rate = max(8.0, calculated_rate - 0.5)
        
        st.markdown(f"""
        <div style='padding: 15px; background: rgba(102, 126, 234, 0.1); border-left: 4px solid #667eea; border-radius: 8px; margin: 15px 0;'>
            <div style='font-size: 0.85rem; opacity: 0.8;'>Interest Rate (Auto-calculated)</div>
            <div style='font-size: 1.5rem; font-weight: 700; color: #667eea; margin-top: 5px;'>{calculated_rate}% per annum</div>
            <div style='font-size: 0.75rem; margin-top: 10px; opacity: 0.7;'>
                🎯 {purpose} | 👔 {emp_type} | 💰 ₹{amount:,} {"| 👥 Co-applicant (-0.5%)" if co_toggle else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Calculator
    with col_calc:
        st.markdown('<div class="fintech-card fade-in">', unsafe_allow_html=True)
        st.markdown("#### 💡 Quick Calculator")
        
        display_income = income
        if co_toggle and co_income > 0:
            display_income = income + co_income
        
        if amount > 0 and tenure > 0 and display_income > 0:
            temp_emi = calculate_emi(amount, calculated_rate, tenure)
            monthly_inc = display_income / 12
            temp_foir = ((temp_emi + existing_emis) / monthly_inc) * 100
            
            st.metric("Estimated EMI", f"₹{int(temp_emi):,}")
            st.metric("Monthly Income", f"₹{int(monthly_inc):,}" + (" (Combined)" if co_toggle and display_income > income else ""))
            
            foir_color = "red" if temp_foir > 50 else ("orange" if temp_foir > 40 else "green")
            st.markdown(f"""
            <div style="padding: 10px; background: rgba(0,0,0,0.05); border-radius: 8px; margin: 10px 0;">
                <div style="font-size: 0.8rem; opacity: 0.7;">FOIR (Target < 50%)</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {foir_color};">{temp_foir:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("💡 Enter loan details to see calculations")
        
        if co_toggle:
            st.success("✅ Co-applicant added!")
        else:
            st.info("💡 Add co-applicant to improve eligibility")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("Save & Continue ➔", use_container_width=True):
        errors = []
        
        if not name or len(name) < 3:
            errors.append("Name must be at least 3 characters")
        if not email or not validate_email(email):
            errors.append("Invalid email address")
        if not phone or not validate_phone(phone):
            errors.append("Phone must be 10 digits starting with 6-9")
        if income <= 0:
            errors.append("Please enter your annual income")
        if amount <= 0:
            errors.append("Please enter loan amount")
        
        if amount > 0 and income > 0:
            valid, msg = validate_financials(amount, income/12)
            if not valid:
                errors.append(msg)
        
        if co_toggle:
            if not co_name or len(co_name) < 3:
                errors.append("Co-applicant name required")
            if not co_email or not validate_email(co_email):
                errors.append("Invalid co-applicant email")
            if not co_phone or not validate_phone(co_phone):
                errors.append("Invalid co-applicant phone")
            if co_income <= 0:
                errors.append("Co-applicant income required")
        

        pan_result = verify_applicant(PAN)

        if pan_result["status"] == "invalid_pan":
            st.error("❌ Invalid PAN format. Please check again.")
            st.stop()

        # Store PAN
        st.session_state.app_data["pan"] = PAN

        # Inject bureau results into app_data
        st.session_state.app_data["credit_score"] = pan_result["credit_score"]
        st.session_state.app_data["existing_emis"] = pan_result["existing_emi"]

        secure_log(f"Verified PAN | Score={pan_result['credit_score']} | EMI={pan_result['existing_emi']}")


        if errors:
            for err in errors:
                st.error(err)
        else:
    # Update application data
            st.session_state.app_data.update({
                "name": sanitize_input(name), "email": sanitize_input(email),
                "phone": sanitize_input(phone), "employment": emp_type,
                "purpose": purpose, "address": sanitize_input(address),
                "income": income, "existing_emis": existing_emis,
                "loan_amount": amount, "tenure": tenure, "rate": calculated_rate, "PAN": PAN
            })

            if co_toggle:
                st.session_state.co_applicant.update({
                    "enabled": True, "name": sanitize_input(co_name),
                    "email": sanitize_input(co_email), "phone": sanitize_input(co_phone),
                    "income": co_income, "employment": co_employment,
                    "relationship": co_relationship
                })

            # ---------------------------------------------
            # 🔍 RUN VERIFICATION AGENT HERE
            # ---------------------------------------------
            # --- RUN PAN VERIFICATION ---
            
            pan_result = verify_applicant(PAN)

            if pan_result["status"] == "invalid_pan":
                st.error("❌ Invalid PAN number format.")
                st.stop()

            # Store verified values
            st.session_state.app_data["credit_score"] = pan_result["credit_score"]
            st.session_state.app_data["existing_emis"] = pan_result["existing_emi"]

            secure_log(
                f"PAN Verified | Score={pan_result['credit_score']} | "
                f"Existing EMI={pan_result['existing_emi']}"
            )
            
            st.session_state.step = 2
            st.success("✓ Details saved!")
            time.sleep(0.5)
            st.rerun()

# ======================================================
# STEP 2 – DOCUMENTS
# ======================================================
elif st.session_state.step == 2:
    st.markdown("### 📂 Document Verification")
    
    col_up, col_info = st.columns([2, 1])
    
    with col_up:
        st.markdown('<div class="fintech-card fade-in">', unsafe_allow_html=True)
        st.info("🔒 Secure Upload: Files processed in-memory only")
        
        st.markdown("#### Required Documents")
        id_proof = st.file_uploader("1️⃣ Identity Proof (Aadhaar/Passport)", type=['pdf', 'jpg', 'png', 'jpeg'])
        if id_proof:
            st.session_state.docs_status["Identity"] = True
            st.session_state.docs_status["identity_file"] = id_proof.name
            st.success(f"✓ {id_proof.name} ({id_proof.size/1024:.1f} KB)")
        
        inc_proof = st.file_uploader("2️⃣ Income Proof (Salary Slips/ITR)", type=['pdf', 'jpg', 'png', 'jpeg'])
        if inc_proof:
            st.session_state.docs_status["Income"] = True
            st.session_state.docs_status["income_file"] = inc_proof.name
            st.success(f"✓ {inc_proof.name} ({inc_proof.size/1024:.1f} KB)")
        
        st.markdown("#### Optional Documents")
        collat = st.file_uploader("3️⃣ Collateral Documents", type=['pdf', 'jpg', 'png', 'jpeg'])
        if collat:
            st.session_state.docs_status["Collateral"] = True
            st.session_state.docs_status["collateral_file"] = collat.name
            st.success(f"✓ {collat.name} ({collat.size/1024:.1f} KB)")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_info:
        st.markdown('<div class="fintech-card fade-in">', unsafe_allow_html=True)
        st.markdown("#### 📋 Checklist")
        
        for doc, present in [("Identity", st.session_state.docs_status["Identity"]),
                            ("Income", st.session_state.docs_status["Income"]),
                            ("Collateral", st.session_state.docs_status["Collateral"])]:
            icon = "✅" if present else "⭕"
            color = "#10B981" if present else "#6B7280"
            label = "Required" if doc in ["Identity", "Income"] else "Optional"
            st.markdown(f"""
            <div style='padding: 12px; margin-bottom: 10px; border-left: 3px solid {color}; background: rgba(0,0,0,0.02); border-radius: 6px;'>
                <div style='font-weight: 600; color: {color};'>{icon} {doc}</div>
                <div style='font-size: 0.75rem; opacity: 0.7;'>{label}</div>
            </div>
            """, unsafe_allow_html=True)
        
        completion = sum([st.session_state.docs_status["Identity"], st.session_state.docs_status["Income"]]) / 2 * 100
        st.markdown(f"""
        <div style='text-align: center; padding: 15px;'>
            <div style='font-size: 2rem; font-weight: 700; color: {"#10B981" if completion == 100 else "#F59E0B"};'>{int(completion)}%</div>
            <div style='font-size: 0.8rem; opacity: 0.7;'>Complete</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    col_b1, col_b2 = st.columns(2)
    
    if col_b1.button("⬅ Back", use_container_width=True):
        st.session_state.step = 1
        st.rerun()
    
    if col_b2.button("Review ➔", use_container_width=True):
        if st.session_state.docs_status["Identity"] and st.session_state.docs_status["Income"]:
            secure_log("Documents verified")
            st.session_state.step = 3
            st.success("✓ Documents verified!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("⚠️ Upload Identity and Income proof")

# ======================================================
# STEP 3 – REVIEW
# ======================================================
elif st.session_state.step == 3:
    st.markdown("### 🔍 Final Review")
    
    data = st.session_state.app_data
    col_review, col_summary = st.columns([2, 1])
    
    with col_review:
        st.markdown('<div class="fintech-card fade-in">', unsafe_allow_html=True)
        st.markdown("#### 👤 Personal Details")
        st.markdown(f"**Name:** {data['name']}")
        st.markdown(f"**Email:** {data['email']}")
        st.markdown(f"**Phone:** {data['phone']}")
        st.markdown(f"**Employment:** {data['employment']}")
        st.markdown(f"**City:** {data['address'] or 'Not provided'}")
        
        if st.session_state.co_applicant['enabled']:
            st.markdown("##### 👥 Co-Applicant")
            st.markdown(f"**Name:** {st.session_state.co_applicant['name']}")
            st.markdown(f"**Relationship:** {st.session_state.co_applicant['relationship']}")
            st.markdown(f"**Income:** ₹{st.session_state.co_applicant['income']:,}")
        
        st.divider()
        st.markdown("#### 💰 Loan Details")
        st.markdown(f"**Purpose:** {data['purpose']}")
        st.markdown(f"**Amount:** ₹{data['loan_amount']:,}")
        st.markdown(f"**Tenure:** {data['tenure']} months")
        st.markdown(f"**Rate:** {data['rate']}%")
        
        total_income = data['income']
        if st.session_state.co_applicant['enabled']:
            total_income += st.session_state.co_applicant['income']
            st.markdown(f"**Combined Income:** ₹{total_income:,}")
        else:
            st.markdown(f"**Income:** ₹{data['income']:,}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_summary:
        st.markdown('<div class="fintech-card fade-in">', unsafe_allow_html=True)
        st.markdown("#### 📊 Summary")
        
        prelim_emi = calculate_emi(data['loan_amount'], data['rate'], data['tenure'])
        total_payment = prelim_emi * data['tenure']
        total_interest = total_payment - data['loan_amount']
        
        st.markdown(f"""
        <div class="metric-box" style="margin-bottom: 15px;">
            <div class="metric-label">Monthly EMI</div>
            <div class="metric-value">₹{int(prelim_emi):,}</div>
        </div>
        <div class="metric-box" style="margin-bottom: 15px;">
            <div class="metric-label">Total Payment</div>
            <div class="metric-value" style="font-size: 1.3rem;">₹{int(total_payment):,}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Total Interest</div>
            <div class="metric-value" style="font-size: 1.3rem; color: #F59E0B;">₹{int(total_interest):,}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    col_b1, col_b2, col_b3 = st.columns(3)
    
    if col_b1.button("⬅ Back", use_container_width=True):
        st.session_state.step = 2
        st.rerun()
    
    if col_b2.button("✏️ Edit", use_container_width=True):
        st.session_state.step = 1
        st.rerun()
    
    if col_b3.button("🚀 Submit", type="primary", use_container_width=True):
        with st.spinner("Processing..."):
            secure_log("Submitted for underwriting")
            res = run_underwriting_engine(data)
            st.session_state.underwriting_result = res
            st.session_state.step = 4
            time.sleep(1)
        st.rerun()

# ======================================================
# STEP 4 – DECISION
# ======================================================
# ======================================================
# STEP 4 – DECISION
# ======================================================
elif st.session_state.step == 4:
    res = st.session_state.underwriting_result

    if res is None:
        st.error("Application state missing. Please restart.")
        if st.button("Restart"):
            st.session_state.step = 1
            st.rerun()

    else:

        # If APPROVED
        if res['eligible']:

            # --- Generate Sanction Letter PDF ---
            pdf_buffer = generate_sanction_letter(
                st.session_state.app_data,
                res,
                st.session_state.application_id
            )

            st.markdown("### 📄 Sanction Letter Preview")
            st.download_button(
                label="📥 Download Sanction Letter (PDF)",
                data=pdf_buffer,
                file_name=f"Sanction_Letter_{st.session_state.application_id}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            # PDF Preview
            try:
                st.pdf(pdf_buffer)
            except:
                st.info("📄 PDF preview not supported in some browsers. Please download instead.")

            # ---------- APPROVAL CARD ----------
            st.markdown(f"""
            <div class="fintech-card fade-in" 
                style="background: linear-gradient(135deg, #D1FAE5, #A7F3D0);
                       border: 2px solid #10B981; 
                       text-align: center; padding: 40px;">
                <div style="font-size: 3rem;">🎉</div>
                <h1 style="color: #065F46;">Loan Approved</h1>
                <p style="color: #047857;">
                    Application ID: <strong>{st.session_state.application_id}</strong>
                </p>
                <p style="opacity:0.7; margin-top:10px;">You can now download your sanction letter.</p>
            </div>
            """, unsafe_allow_html=True)

            st.balloons()

        # If REJECTED
        else:
            reasons_html = "<br>".join([f"• {r}" for r in res['reasons']])
            st.markdown(f"""
            <div class="fintech-card fade-in" 
                style="background: linear-gradient(135deg, #FEE2E2, #FECACA);
                       border: 2px solid #EF4444; text-align: center; padding: 40px;">
                <div style="font-size: 3rem;">❌</div>
                <h1 style="color: #991B1B;">Loan Not Approved</h1>
                <div style="color: #991B1B; margin-top: 20px;">{reasons_html}</div>
            </div>
            """, unsafe_allow_html=True)

        # ------- ANALYSIS CARDS -------
        st.markdown("### 📊 Analysis")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            score_color = "#10B981" if res['score'] >= 750 else (
                          "#F59E0B" if res['score'] >= 650 else "#EF4444")
            st.markdown(f"""
            <div class="metric-box fade-in">
                <div class="metric-label">Credit Score</div>
                <div class="metric-value" style="color: {score_color};">{res['score']}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            foir_color = "#10B981" if res['foir'] < 40 else (
                         "#F59E0B" if res['foir'] < 50 else "#EF4444")
            st.markdown(f"""
            <div class="metric-box fade-in">
                <div class="metric-label">FOIR</div>
                <div class="metric-value" style="color: {foir_color};">{res['foir']}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-box fade-in">
                <div class="metric-label">Monthly EMI</div>
                <div class="metric-value" style="color: #667eea;">₹{res['emi']:,}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            risk_color = "#10B981" if res['risk'] == "Low" else (
                         "#F59E0B" if res['risk'] == "Medium" else "#EF4444")
            st.markdown(f"""
            <div class="metric-box fade-in">
                <div class="metric-label">Risk</div>
                <div class="metric-value" style="color: {risk_color};">{res['risk']}</div>
            </div>
            """, unsafe_allow_html=True)

        # ------- Recommendations -------
        if res['recommendations']:
            st.markdown("### 💡 Recommendations")
            st.markdown('<div class="fintech-card fade-in">', unsafe_allow_html=True)
            for idx, rec in enumerate(res['recommendations'], 1):
                st.markdown(f"**{idx}.** {rec}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        if st.button("🔄 New Application", use_container_width=True):
            st.session_state.step = 1
            st.session_state.app_data = {k: "" for k in st.session_state.app_data}
            st.session_state.co_applicant["enabled"] = False
            st.session_state.underwriting_result = None
            st.session_state.application_id = f"LF{random.randint(10000, 99999)}"
            st.rerun()


# ======================================================
# AI ADVISOR
# ======================================================
st.divider()

tab1, tab2 = st.tabs(["🤖 Advisor", "🔒 Audit Logs"])

with tab1:
    st.markdown("### Ask Mr. Finn – The Loan Agent")
    st.caption("⚠️ Mr. Finn provides AI-based guidance using demo data | Responses may not reflect actual lender decisions.")
    
    col1, col2 = st.columns([4, 1])
    if col2.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
    
    if st.session_state.chat_history:
        for chat in st.session_state.chat_history[-10:]:
            bubble = "chat-user" if chat["role"] == "user" else "chat-ai"
            st.markdown(f"<div class='chat-bubble {bubble}'>{chat['message']}</div>", unsafe_allow_html=True)
    else:
        st.info("👋 Ask me anything about loans!")
    
    col_in, col_send = st.columns([5, 1])

    with col_in:
        user_q = st.text_input(
            "Ask something...",
            placeholder="How does EMI work?",
            key="user_question_input"
        )

    with col_send:
        ask_btn = st.button("Send 📤", use_container_width=True)    

# ------------------------
# Handle AI Query
# ------------------------
if ask_btn and user_q.strip():
    safe_q = sanitize_input(user_q)
    st.session_state.chat_history.append({"role": "user", "message": safe_q})

    with st.spinner("🤖 Mr. Finn is thinking..."):
        ai_text, model_used = get_llama_response(safe_q, st.session_state.app_data)

    ai_text += f"<br><span style='opacity:0.5; font-size:0.7rem;'>[{model_used}]</span>"
    st.session_state.chat_history.append({"role": "ai", "message": ai_text})

    secure_log(f"AI Query: {safe_q[:50]} | Model={model_used}")
    st.rerun()

# ======================================================
# AUDIT LOGS TAB
# ======================================================
with tab2:
    st.markdown("### 🔒 Secure Audit Trail")

    if st.session_state.logs:
        logs_text = "\n".join(st.session_state.logs[-30:])
        st.code(logs_text)

        st.download_button(
            label="📥 Download Logs",
            data=logs_text,
            file_name=f"audit_log_{st.session_state.application_id}.txt",
            mime="text/plain"
        )
    else:
        st.info("No logs yet. Start by filling the application.")

# ======================================================
# FOOTER
# ======================================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center; opacity:0.7; padding: 20px 0; font-size: 0.85rem;'>
        Outputs are generated from sample data and simplified rules; real loan assessments may differ.<br>
        <strong>Finny - Loan Assistant</strong><br>
        <br> &copy; All rights reserved  <br>
    </div>
    """,
    unsafe_allow_html=True
)