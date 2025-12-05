import time
import random
import streamlit as st
from logic.utils import calculate_emi, secure_log


def run_underwriting_engine(data):
    """Advanced underwriting engine with FOIR, DTI, score & risk."""

    # Progress animation
    pg = st.empty()
    with pg:
        st.info("🔄 Running underwriting analysis...")
        bar = st.progress(0)
        for p in [25, 50, 75, 100]:
            time.sleep(0.5)
            bar.progress(p)
    pg.empty()

    # Combine income with co-applicant
    total_income = data["income"]
    if st.session_state.co_applicant["enabled"]:
        total_income += st.session_state.co_applicant["income"]
        secure_log(f"Co-applicant income added: ₹{st.session_state.co_applicant['income']:,}")

    monthly_income = total_income / 12
    emi = calculate_emi(data["loan_amount"], data["rate"], data["tenure"])

    total_obligations = emi + data["existing_emis"]

    # FOIR
    foir = (total_obligations / monthly_income) * 100 if monthly_income > 0 else 999

    # DTI
    annual_debt = total_obligations * 12
    dti = (annual_debt / total_income) * 100 if total_income > 0 else 999

    # Base synthetic score
    base_score = 650

    # Employment bonus
    emp = data["employment"]
    if emp == "Salaried":
        base_score += 50
    elif emp == "Business Owner":
        base_score += 30

    # Co-applicant bonus
    if st.session_state.co_applicant["enabled"]:
        base_score += 40

    # Income bonus
    if monthly_income > 100000:
        base_score += 70
    elif monthly_income > 50000:
        base_score += 40

    # FOIR impact
    if foir < 30:
        base_score += 60
    elif foir < 40:
        base_score += 30
    elif foir > 60:
        base_score -= 100

    loan_to_income = (data["loan_amount"] / total_income) * 100
    if loan_to_income < 200:
        base_score += 30
    elif loan_to_income > 500:
        base_score -= 50

    final_score = min(900, max(300, base_score + random.randint(-30, 30)))

    eligible = True
    reasons = []
    recommendations = []

    # FOIR check
    if foir > 55:
        eligible = False
        reasons.append(f"FOIR too high ({foir:.1f}% > 55%)")
        if not st.session_state.co_applicant["enabled"]:
            recommendations.append("Add a co-applicant.")
        else:
            recommendations.append("Increase tenure or reduce EMIs.")

    # Credit score check
    if final_score < 600:
        eligible = False
        reasons.append(f"Low credit score ({final_score})")
        recommendations.append("Improve score before applying again.")
    elif final_score < 700:
        recommendations.append("Interest may be slightly higher due to moderate score.")

    # LTI check
    if loan_to_income > 600:
        eligible = False
        reasons.append("Loan amount too high relative to income.")
        recommendations.append("Reduce loan amount or add co-applicant.")

    if monthly_income < 25000:
        eligible = False
        reasons.append("Income below minimum threshold.")
        recommendations.append("Add co-applicant with stable income.")

    # Risk category
    risk_score = 0
    if foir > 45: risk_score += 2
    if final_score < 700: risk_score += 2
    if loan_to_income > 400: risk_score += 1

    if st.session_state.co_applicant["enabled"]:
        risk_score = max(0, risk_score - 1)

    risk = "Low" if risk_score <= 1 else "Medium" if risk_score <= 3 else "High"

    # Rate adjustment
    final_rate = data["rate"]
    if risk == "High":
        final_rate += 2
    elif risk == "Medium":
        final_rate += 1

    if st.session_state.co_applicant["enabled"]:
        final_rate = max(8.0, final_rate - 0.5)

    final_emi = calculate_emi(data["loan_amount"], final_rate, data["tenure"])

    total_repayment = final_emi * data["tenure"]
    total_interest = total_repayment - data["loan_amount"]

    secure_log(
        f"Underwriting: Eligible={eligible}, Score={final_score}, FOIR={foir:.2f}%"
    )

    return {
        "emi": round(final_emi),
        "foir": round(foir, 2),
        "dti": round(dti, 2),
        "score": final_score,
        "risk": risk,
        "eligible": eligible,
        "reasons": reasons,
        "recommendations": recommendations,
        "final_rate": round(final_rate, 2),
        "total_repayment": round(total_repayment),
        "total_interest": round(total_interest),
        "loan_to_income": round(loan_to_income, 1),
        "combined_income": total_income,
    }
