# core/interest.py

def calculate_base_interest_rate(
    tenure_months,
    employment_type="Salaried",
    loan_purpose="Personal",
    loan_amount=500000,
    credit_score=720
):
    """
    Dynamic real-world prototype interest rate calculator.
    """

    # Base rates by loan purpose
    purpose_rates = {
        "Personal": 12.5,
        "Home": 8.75,
        "Business": 15.0,
        "Education": 10.5,
        "Medical": 11.5
    }

    base_rate = purpose_rates.get(loan_purpose, 12.5)

    # Employment-based adjustments
    if employment_type == "Self-Employed":
        base_rate += 1.25
    elif employment_type == "Business Owner":
        base_rate += 1.50

    # Loan amount impact
    if loan_amount >= 20_00_000:
        base_rate -= 0.50
    elif loan_amount >= 10_00_000:
        base_rate -= 0.25
    elif loan_amount <= 1_00_000:
        base_rate += 0.50

    # Tenure impact
    if tenure_months >= 60:
        base_rate -= 0.25
    elif tenure_months <= 12:
        base_rate += 0.25

    # Credit Score impact
    if credit_score >= 750:
        base_rate -= 0.50
    elif credit_score < 700:
        base_rate += 1.00

    # Clamp between 8% and 24%
    return round(min(24.0, max(8.0, base_rate)), 2)
