# logic/interest.py

def calculate_base_interest_rate(tenure_months, employment_type="Salaried", loan_purpose="Personal", loan_amount=500000):
    """
    Realistic Indian banking interest rate calculation.

    Factors:
    1. Loan Purpose (major factor)
    2. Employment Type (risk)
    3. Loan Amount (bigger loans → slightly reduced rate)
    4. Tenure (very small influence)
    """

    # Base rate by purpose
    purpose_rates = {
        "Personal": 12.5,
        "Home": 8.75,
        "Business": 15.0,
        "Education": 10.5,
        "Medical": 11.5
    }
    base_rate = purpose_rates.get(loan_purpose, 12.5)

    # Employment risk adjustments
    if employment_type == "Self-Employed":
        base_rate += 1.5
    elif employment_type == "Business Owner":
        base_rate += 1.0

    # Loan amount adjustments
    if loan_amount >= 2000000:       # ≥ 20 lakh
        base_rate -= 0.5
    elif loan_amount >= 1000000:     # ≥ 10 lakh
        base_rate -= 0.25
    elif loan_amount <= 100000:      # ≤ 1 lakh
        base_rate += 0.5

    # Tenure influence — very small
    if tenure_months >= 60:
        base_rate -= 0.25
    elif tenure_months <= 12:
        base_rate += 0.25

    # Keep rate within India banking realistic limits
    final_rate = min(24.0, max(8.0, base_rate))
    return round(final_rate, 2)
