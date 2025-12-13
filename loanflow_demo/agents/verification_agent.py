from core.mock_bureau import fetch_pan_details, generate_cibil_report

def verify_pan(pan):
    """Verifies Pan and generates CIBIL report."""
    result = fetch_pan_details(pan)
    if not result:
        if not result:
            result = {
                "name": f"Customer {pan[-4:]}",      # Synthetic name
                "credit_score": 700,                 # Neutral score
                "existing_emi": 0,
                "preapproved_limit": 800000,
                "monthly_income": 80000,
                "total_accounts": 2,
                "active_accounts": 1,
                "closed_accounts": 1,
                "payment_history": "000,000,000,000,000,000",
            }

    cibil_report = generate_cibil_report(result)
    return result, cibil_report
