"""
Adds 3-scenario logic based on pre-approved limits
"""

import time
import streamlit as st
from logic.utils import calculate_emi, secure_log
from logic.verification_agent import determine_scenario


def run_underwriting_engine(data, verification_result=None):
    """
    Underwriting Agent - evaluates loan eligibility with 3-scenario logic
    
    NEW: Takes verification_result to access pre-approved limits
    """

    # Progress animation
    pg = st.empty()
    with pg:
        st.info("🔄 Underwriting Agent analyzing your application...")
        bar = st.progress(0)
        for p in [25, 50, 75, 100]:
            time.sleep(0.4)
            bar.progress(p)
    pg.empty()

    # Extract pre-approved limit from verification
    pre_approved_limit = 0
    credit_score = data.get("credit_score", 650)
    monthly_salary = 0
    
    if verification_result:
        pre_approved_limit = verification_result.get("pre_approved_limit", 0)
        credit_score = verification_result.get("credit_score", credit_score)
        monthly_salary = verification_result.get("monthly_salary", 0)
    
    # If salary not from verification, use income data
    if monthly_salary == 0:
        monthly_salary = data.get("income", 0) / 12

    # Determine scenario
    requested_amount = data["loan_amount"]
    scenario_info = determine_scenario(requested_amount, pre_approved_limit)
    
    secure_log(f"Scenario detected: {scenario_info['scenario']} - {scenario_info['label']}")

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

    # Apply scenario-based eligibility
    eligible = True
    reasons = []
    recommendations = []
    
    # SCENARIO A: Instant Approval
    if scenario_info["scenario"] == "A":
        secure_log("Scenario A: Instant approval path")
        
        # Still check basic eligibility
        if credit_score < 600:
            eligible = False
            reasons.append(f"Credit score {credit_score} below minimum threshold (600)")
        
        if foir > 60:  # Relaxed for pre-approved
            eligible = False
            reasons.append(f"FOIR {foir:.1f}% exceeds safe limit (60%)")
        
        if eligible:
            recommendations.append("✅ Instant approval - amount within pre-approved limit")
    
    # SCENARIO B: Conditional Approval (needs salary slip verification)
    elif scenario_info["scenario"] == "B":
        secure_log("Scenario B: Conditional approval - checking EMI ratio")
        
        # Calculate EMI as percentage of salary
        emi_ratio = (emi / monthly_salary) * 100 if monthly_salary > 0 else 999
        
        if emi_ratio <= 50:
            recommendations.append(f"✅ EMI is {emi_ratio:.1f}% of salary (within 50% limit)")
        else:
            eligible = False
            reasons.append(f"EMI {emi_ratio:.1f}% exceeds 50% of salary")
            recommendations.append("Consider reducing loan amount or extending tenure")
        
        if credit_score < 700:
            eligible = False
            reasons.append(f"Credit score {credit_score} below required threshold (700) for extended amount")
        
        if eligible:
            recommendations.append("📄 Conditional approval - salary slip verified successfully")
    
    # SCENARIO C: Exceeds Limit
    else:  # scenario_info["scenario"] == "C"
        secure_log("Scenario C: Amount exceeds limits")
        eligible = False
        reasons.append(f"Requested ₹{requested_amount:,} exceeds 2× pre-approved limit (₹{2 * pre_approved_limit:,})")
        recommendations.append(f"💡 Consider requesting up to ₹{pre_approved_limit:,} for instant approval")
        recommendations.append("💡 Or explore secured loan options with collateral")

    # Additional checks for all scenarios
    if foir > 55 and eligible:
        recommendations.append(f"⚠️ FOIR at {foir:.1f}% - consider adding co-applicant")
    
    if credit_score < 700 and eligible:
        recommendations.append("Interest rate may be slightly higher due to credit score")

    # Risk category
    risk_score = 0
    if foir > 45: risk_score += 2
    if credit_score < 700: risk_score += 2
    if scenario_info["scenario"] == "C": risk_score += 3
    elif scenario_info["scenario"] == "B": risk_score += 1

    if st.session_state.co_applicant["enabled"]:
        risk_score = max(0, risk_score - 1)

    risk = "Low" if risk_score <= 2 else "Medium" if risk_score <= 4 else "High"

    # Rate adjustment
    final_rate = data["rate"]
    if risk == "High":
        final_rate += 2
    elif risk == "Medium":
        final_rate += 1
    
    # Scenario A bonus
    if scenario_info["scenario"] == "A" and credit_score >= 750:
        final_rate = max(8.0, final_rate - 0.5)

    if st.session_state.co_applicant["enabled"]:
        final_rate = max(8.0, final_rate - 0.5)

    final_emi = calculate_emi(data["loan_amount"], final_rate, data["tenure"])

    total_repayment = final_emi * data["tenure"]
    total_interest = total_repayment - data["loan_amount"]

    secure_log(
        f"Underwriting complete: Scenario={scenario_info['scenario']}, "
        f"Eligible={eligible}, Score={credit_score}, FOIR={foir:.2f}%"
    )

    return {
        "emi": round(final_emi),
        "foir": round(foir, 2),
        "dti": round(dti, 2),
        "score": credit_score,
        "risk": risk,
        "eligible": eligible,
        "reasons": reasons,
        "recommendations": recommendations,
        "final_rate": round(final_rate, 2),
        "total_repayment": round(total_repayment),
        "total_interest": round(total_interest),
        "loan_to_income": round((requested_amount / total_income) * 100, 1),
        "combined_income": total_income,
        "scenario": scenario_info["scenario"],
        "scenario_label": scenario_info["label"],
        "scenario_icon": scenario_info["icon"],
        "scenario_description": scenario_info["description"],
        "pre_approved_limit": pre_approved_limit,
        "emi_to_salary_ratio": round((final_emi / monthly_salary) * 100, 1) if monthly_salary > 0 else 0
    }