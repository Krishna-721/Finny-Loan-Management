"""
Loan Explanation Agent
Uses Groq LLM to convert underwriting results & CIBIL data into
human-friendly explanations.
"""

from ai.groq_client import get_llama_response
from ai.persona import EXPLANATION_PERSONA


def explain_underwriting(uw_result, app_data):
    """
    Generate natural-language explanation of underwriting decision.
    """

    prompt = f"""
    {EXPLANATION_PERSONA}

    Explain the underwriting result in simple English.

    Decision: {uw_result.get('decision')}
    Reason: {uw_result.get('reason')}
    Loan Amount: ₹{app_data.get('loan_amount')}
    Tenure: {app_data.get('tenure')} months
    EMI: ₹{uw_result.get('emi')}
    Interest Rate: {uw_result.get('interest_rate')}%
    FOIR: {uw_result.get('foir')}%
    Monthly Income: ₹{app_data.get('income')}

    Explain:
    - Why this decision was made
    - What FOIR means in this case
    - Whether the customer can improve eligibility
    - Keep it short and friendly.
    """

    return get_llama_response(prompt)



def explain_cibil(cibil_data):
    """
    Convert CIBIL report fields into a friendly explanation.
    """

    prompt = f"""
    {EXPLANATION_PERSONA}

    Explain the customer's CIBIL health:

    Credit Score: {cibil_data.get('credit_score')}
    Total Accounts: {cibil_data.get('total_accounts')}
    Active Accounts: {cibil_data.get('active_accounts')}
    Closed Accounts: {cibil_data.get('closed_accounts')}
    Payment History: {cibil_data.get('payment_history')}

    Explain:
    - Whether the credit score is good or bad
    - What the account history indicates
    - Whether payment pattern is healthy
    """

    return get_llama_response(prompt)
