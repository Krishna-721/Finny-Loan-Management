import re

# -----------------------------------------------------------
# Email validation
# -----------------------------------------------------------
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# -----------------------------------------------------------
# Indian phone validation
# -----------------------------------------------------------
def validate_phone(phone):
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, str(phone)) is not None


# -----------------------------------------------------------
# Financial validation
# -----------------------------------------------------------
def validate_financials(amount, salary):
    """
    Backend validation to prevent UI manipulation.
    - Max 1 crore
    - Min 50k
    - Salary must be >= 10k monthly
    - Loan <= 5× annual income
    """
    if amount < 50000 or amount > 10000000:
        return False, "Loan amount must be between ₹50,000 and ₹1,00,00,000."

    if salary < 10000:
        return False, "Monthly income is too low for eligibility."

    if amount > (salary * 60):
        return False, "Loan amount exceeds maximum eligibility (5× annual income)."

    return True, "Valid"
