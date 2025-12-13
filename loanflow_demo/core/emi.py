# core/emi.py

def calculate_emi(principal, rate_annual, tenure_months):
    """
    Standard EMI formula:
    -EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    """
    rate = rate_annual / (12 * 100)

    if rate == 0:
        return round(principal / tenure_months, 2)

    emi = principal * rate * ((1 + rate)**tenure_months) / (((1 + rate)**tenure_months) - 1)
    return round(emi, 2)
