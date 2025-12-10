# interest.py — FIXED (Prototype Safe)

def calculate_base_interest_rate(tenure_months, employment_type="Salaried",
                                 loan_purpose="Personal", loan_amount=500000):

    purpose_rates = {
        "Personal": 12.5,
        "Home": 8.75,
        "Business": 15.0,
        "Education": 10.5,
        "Medical": 11.5
    }

    base_rate = purpose_rates.get(loan_purpose, 12.5)

    # Employment adjustments
    if employment_type == "Self-Employed":
        base_rate += 1.5
    elif employment_type == "Business Owner":
        base_rate += 1.0

    # Loan Amount Adjustments
    if loan_amount >= 20_00_000:
        base_rate -= 0.5
    elif loan_amount >= 10_00_000:
        base_rate -= 0.25
    elif loan_amount <= 1_00_000:
        base_rate += 0.5

    # Tenure influence
    if tenure_months >= 60:
        base_rate -= 0.25
    elif tenure_months <= 12:
        base_rate += 0.25

    return round(min(24.0, max(8.0, base_rate)), 2)
