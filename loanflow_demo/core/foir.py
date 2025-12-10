# core/foir.py

def calculate_foir(existing_emi, proposed_emi, monthly_income):
    """
    FOIR = (Total EMI / Monthly Income) * 100
    """
    if monthly_income <= 0:
        return 999  # invalid case

    total_emi = existing_emi + proposed_emi
    return round((total_emi / monthly_income) * 100, 2)
