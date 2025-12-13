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
        loan_purpose,
        preapproved_limit=None
    ):
    """    
    Tier 1  → Instant Approval (loan ≤ pre-approved limit)
    Tier 2  → Conditional Approval (loan ≤ 2× pre-approved → needs salary slip)
    Tier 3  → Reject (loan > 2× pre-approved OR credit score < 700)
    """

    # ---------------------------
    # 1️⃣ Credit score validation
    # ---------------------------
    if credit_score < 700:
        return {
            "decision": "REJECTED",
            "reason": f"Low credit score ({credit_score} < 700)",
            "interest_rate": None,
            "emi": None,
            "foir": None
        }

    # Interest rate calculation
    interest_rate = calculate_base_interest_rate(
        tenure_months=tenure,
        employment_type=employment_type,
        loan_purpose=loan_purpose,
        loan_amount=loan_amount,
        credit_score=credit_score
    )

    # EMI calculation
    new_emi = calculate_emi(loan_amount, interest_rate, tenure)

    # FOIR (informative — used in Tier 2 verification)
    foir = calculate_foir(existing_emi, new_emi, income)

    # Ensure pre-approved limit is available
    if preapproved_limit is None:
        # fallback (should not happen)
        preapproved_limit = income * 3  

    # ---------------------------
    # 2️⃣ Tier 1 — Instant Approval
    # ---------------------------
    if loan_amount <= preapproved_limit:
        return {
            "decision": "APPROVED",
            "reason": "Loan within pre-approved limit",
            "interest_rate": interest_rate,
            "emi": new_emi,
            "foir": round(foir, 2)
        }

    # ---------------------------
    # 3️⃣ Tier 2 — Salary Slip Required
    # ---------------------------
    if loan_amount <= 2 * preapproved_limit:
        return {
            "decision": "NEED_SALARY_SLIP",
            "reason": "Loan exceeds pre-approved limit but ≤ 2× limit",
            "interest_rate": interest_rate,
            "emi": new_emi,
            "foir": round(foir, 2)
        }

    # ---------------------------
    # 4️⃣ Tier 3 — Hard Reject
    # ---------------------------
    return {
        "decision": "REJECTED",
        "reason": "Loan exceeds 2× pre-approved limit",
        "interest_rate": interest_rate,
        "emi": new_emi,
        "foir": round(foir, 2)
    }