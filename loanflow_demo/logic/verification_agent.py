"""
loanflow_demo/logic/verification_agent.py - UPDATED VERSION

Adds pre-approved limits for 3-scenario logic
"""

import re
import random

# PAN validation
def validate_pan(pan):
    if not pan:
        return False
    return bool(re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", pan.upper()))

# Enhanced mock bureau data with pre-approved limits
MOCK_BUREAU_DB = {
    "ABCDE1234F": {
        "name": "Rajesh Kumar",
        "credit_score": 735,
        "loans": [{"type": "Personal Loan", "emi": 6500}],
        "overdue": False,
        "pre_approved_limit": 500000,  # ₹5L
        "monthly_salary": 80000
    },
    "PQRSX9988L": {
        "name": "Bobby Smith",
        "credit_score": 680,
        "loans": [{"type": "Credit Card", "emi": 4200}],
        "overdue": False,
        "pre_approved_limit": 300000,  # ₹3L
        "monthly_salary": 50000
    },
    "WXYZA5678M": {
        "name": "Ali Khan",
        "credit_score": 612,
        "loans": [{"type": "Home Loan", "emi": 12000}],
        "overdue": True,
        "pre_approved_limit": 200000,  # ₹2L (lower due to overdue)
        "monthly_salary": 45000
    },
    "LMNOP3456Q": {
        "name": "Sneha Reddy",
        "credit_score": 790,
        "loans": [{"type": "Business Loan", "emi": 15000}],
        "overdue": False,
        "pre_approved_limit": 800000,  # ₹8L (high score)
        "monthly_salary": 120000
    },
    "FGHIJ7890K": {
        "name": "Vikram Singh",
        "credit_score": 720,
        "loans": [],
        "overdue": False,
        "pre_approved_limit": 600000,  # ₹6L
        "monthly_salary": 95000
    },
    "QWERT1234Y": {
        "name": "Ananya Iyer",
        "credit_score": 655,
        "loans": [{"type": "Auto Loan", "emi": 8000}],
        "overdue": False,
        "pre_approved_limit": 250000,  # ₹2.5L
        "monthly_salary": 48000
    },
    "ZXCVB9876N": {
        "name": "Rohan Mehta",
        "credit_score": 810,
        "loans": [{"type": "Gold Loan", "emi": 3000}],
        "overdue": False,
        "pre_approved_limit": 1000000,  # ₹10L (excellent score)
        "monthly_salary": 150000
    },
    "ASDFG4567H": {
        "name": "Kavya Nair",
        "credit_score": 640,
        "loans": [{"type": "Personal Loan", "emi": 7500}],
        "overdue": False,
        "pre_approved_limit": 180000,  # ₹1.8L
        "monthly_salary": 42000
    },
    "POIUY8765T": {
        "name": "Karthik Rao",
        "credit_score": 775,
        "loans": [{"type": "Education Loan", "emi": 9000}],
        "overdue": False,
        "pre_approved_limit": 700000,  # ₹7L
        "monthly_salary": 110000
    },
    "MNBVC2345R": {
        "name": "Divya Joshi",
        "credit_score": 695,
        "loans": [{"type": "Two Wheeler Loan", "emi": 4500}],
        "overdue": False,
        "pre_approved_limit": 400000,  # ₹4L
        "monthly_salary": 65000
    }
}

# Fetch bureau info with pre-approved limits
def fetch_bureau_data(pan):
    """
    Fetches customer data including pre-approved loan limit
    """
    pan = pan.upper()
    if pan in MOCK_BUREAU_DB:
        return MOCK_BUREAU_DB[pan]

    # Generate synthetic profile for unknown PANs
    score = random.randint(650, 800)
    salary = random.choice([40000, 55000, 75000, 95000, 120000])
    
    # Pre-approved limit based on score and salary
    # Rule: 4-8x monthly salary depending on credit score
    multiplier = 4 + ((score - 650) / 150) * 4  # 4x at 650, 8x at 800
    pre_approved = int(salary * multiplier)
    
    loans = []
    if random.random() < 0.3:
        loans = [{"type": "Personal Loan", "emi": random.choice([2500, 3500, 5000])}]

    return {
        "name": "Guest User",
        "credit_score": score,
        "loans": loans,
        "overdue": random.random() < 0.1,
        "pre_approved_limit": pre_approved,
        "monthly_salary": salary
    }

# Main verification agent
def verify_applicant(pan):
    """
    Verification Agent - validates PAN and fetches customer profile
    """
    if not validate_pan(pan):
        return {"status": "invalid_pan"}

    bureau = fetch_bureau_data(pan)
    total_emi = sum(l["emi"] for l in bureau["loans"])

    return {
        "status": "verified",
        "name": bureau.get("name", "Guest User"),
        "credit_score": bureau["credit_score"],
        "loans": bureau["loans"],
        "existing_emi": total_emi,
        "overdue": bureau["overdue"],
        "pre_approved_limit": bureau["pre_approved_limit"],
        "monthly_salary": bureau.get("monthly_salary", 0)
    }


def determine_scenario(requested_amount, pre_approved_limit):
    """
    Determines which scenario (A, B, or C) applies
    
    Scenario A: requested ≤ pre-approved → Instant approval
    Scenario B: requested ≤ 2x pre-approved → Conditional (salary slip needed)
    Scenario C: requested > 2x pre-approved → Rejection
    """
    
    if requested_amount <= pre_approved_limit:
        return {
            "scenario": "A",
            "label": "Instant Approval",
            "description": "Amount within pre-approved limit",
            "requires_salary_slip": False,
            "icon": "✅"
        }
    
    elif requested_amount <= (2 * pre_approved_limit):
        return {
            "scenario": "B",
            "label": "Conditional Approval",
            "description": "Requires salary slip verification",
            "requires_salary_slip": True,
            "icon": "📄"
        }
    
    else:
        return {
            "scenario": "C",
            "label": "Exceeds Limit",
            "description": f"Requested amount exceeds 2× pre-approved (₹{2 * pre_approved_limit:,})",
            "requires_salary_slip": False,
            "icon": "❌"
        }