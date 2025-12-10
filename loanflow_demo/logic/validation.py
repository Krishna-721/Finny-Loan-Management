# validation.py — FIXED FOR PROTOTYPE

import re

def validate_email(email):
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$', email))

def validate_phone(phone):
    return bool(re.match(r'^[6-9]\d{9}$', str(phone)))

def validate_financials(amount, monthly_salary):
    # Prototype-friendly limits
    if amount < 50000 or amount > 1_00_00_000:
        return False, "Loan must be ₹50,000 to ₹1,00,00,000."

    if monthly_salary < 10000:
        return False, "Monthly income too low."

    if amount > (monthly_salary * 60):  # 5× annual income
        return False, "Loan exceeds 5× your annual income."

    return True, "Valid"
