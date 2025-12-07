#verification_agent.py
import re
import random

# PAN validation
def validate_pan(pan):
    if not pan:
        return False
    return bool(re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", pan.upper()))

# Mock bureau data
MOCK_BUREAU_DB = {
    "ABCDE1234F": {
        "credit_score": 735,
        "loans": [{"type": "Personal Loan", "emi": 6500}],
        "overdue": False
    },
    "PQRSX9988L": {
        "credit_score": 612,
        "loans": [{"type": "Credit Card", "emi": 4200}],
        "overdue": True
    },
    "WXYZA5678M": {
        "credit_score": 680,
        "loans": [{"type": "Home Loan", "emi": 12000}],
        "overdue": False
    },
    "LMNOP3456Q": {
        "credit_score": 790,
        "loans": [{"type": "Business Loan", "emi": 15000}],
        "overdue": True
    }
}

# Fetch bureau info
def fetch_bureau_data(pan):
    pan = pan.upper()
    if pan in MOCK_BUREAU_DB:
        return MOCK_BUREAU_DB[pan]

    # Generate synthetic profile
    score = random.randint(650, 800)
    loan = []
    if random.random() < 0.3:
        loan = [{"type": "Personal Loan", "emi": random.choice([2500, 3500, 5000])}]

    return {
        "credit_score": score,
        "loans": loan,
        "overdue": random.random() < 0.1
    }

# Main verification agent
def verify_applicant(pan):
    if not validate_pan(pan):
        return {"status": "invalid_pan"}

    bureau = fetch_bureau_data(pan)
    total_emi = sum(l["emi"] for l in bureau["loans"])

    return {
        "status": "verified",
        "credit_score": bureau["credit_score"],
        "loans": bureau["loans"],
        "existing_emi": total_emi,
        "overdue": bureau["overdue"]
    }
