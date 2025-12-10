# agents/underwriting_agent.py

from core.interest import calculate_base_interest_rate
from core.emi import calculate_emi
from core.foir import calculate_foir

def run_underwriting(
        loan_amount,
        tenure,
        credit_score,
        existing_emi,
        income,
        employment_type,
        loan_purpose
    ):
    """
    Full underwriting logic based on:
    - Credit score
    - FOIR
    - Employment type
    - Purpose-based dynamic interest
    - Loan amount adjustments
    """

    # 1. Get interest rate from your interest.py logic
    interest_rate = calculate_base_interest_rate(
        tenure_months=tenure,
        employment_type=employment_type,
        loan_purpose=loan_purpose,
        loan_amount=loan_amount
    )

    # 2. Calculate EMI
    new_emi = calculate_emi(loan_amount, interest_rate, tenure)

    # 3. Calculate FOIR
    foir = calculate_foir(existing_emi, new_emi, income)

    # 4. Decision logic
    decision = "APPROVED"
    reason = None

    if credit_score < 650:
        decision = "REJECTED"
        reason = "Low credit score"

    elif foir > 50:
        decision = "REJECTED"
        reason = f"High FOIR ({foir}%)"

    return {
        "decision": decision,
        "reason": reason,
        "interest_rate": interest_rate,
        "emi": new_emi,
        "foir": foir
    }
