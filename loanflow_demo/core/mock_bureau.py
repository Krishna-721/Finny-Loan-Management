from datetime import datetime
import random

# Simulated PAN database (KYC + credit info)
MOCK_PAN_DB = {
    "ABCDE1234F": {
        "name": "Rohit Sharma",
        "credit_score": 780,
        "existing_emi": 5000,
        "preapproved_limit": 400000,
        "monthly_income": 85000,
        "total_accounts": 4,
        "active_accounts": 3,
        "closed_accounts": 1,
        "payment_history": "000,000,000,000,000,000"
    },
    "XYZAB1234C": {
        "name": "Anita Kapoor",
        "credit_score": 640,
        "existing_emi": 10000,
        "preapproved_limit": 120000,
        "monthly_income": 45000,
        "total_accounts": 3,
        "active_accounts": 2,
        "closed_accounts": 1,
        "payment_history": "000,030,000,000,000,000"
    },
    "LMNOP5678D": {
        "name": "Vikram Singh",
        "credit_score": 720,
        "existing_emi": 7000,
        "preapproved_limit": 300000,
        "monthly_income": 65000,
        "total_accounts": 3,
        "active_accounts": 3,
        "closed_accounts": 0,
        "payment_history": "000,000,000,000,000,000"
    },
    "QWERT4321Z": {
        "name": "Sneha Patel",
        "credit_score": 680,
        "existing_emi": 8000,
        "preapproved_limit": 250000,
        "monthly_income": 55000,
        "total_accounts": 4,
        "active_accounts": 3,
        "closed_accounts": 1,
        "payment_history": "000,000,000,030,000,000"
    },
    "PQRST9876Y": {
        "name": "Amit Joshi",
        "credit_score": 590,
        "existing_emi": 12000,
        "preapproved_limit": 100000,
        "monthly_income": 40000,
        "total_accounts": 5,
        "active_accounts": 4,
        "closed_accounts": 1,
        "payment_history": "030,060,000,030,000,000"
    },
    "ABCPS1234K": {
        "name": "Vamshi Krishna",
        "credit_score": 782,
        "existing_emi": 8500,
        "preapproved_limit": 1000000,
        "monthly_income": 120000,
        "total_accounts": 4,
        "active_accounts": 3,
        "closed_accounts": 1,
        "payment_history": "000,000,030,000,000,000"
    }
}

def fetch_pan_details(pan):
    """Fetch basic credit bureau data for a PAN"""
    pan = pan.upper().strip()
    return MOCK_PAN_DB.get(pan)

def generate_cibil_report(bureau_data):
    """
    Generates a detailed CIBIL-style credit report based on bureau data
    """
    
    name = bureau_data["name"]
    credit_score = bureau_data["credit_score"]
    existing_emi = bureau_data["existing_emi"]
    preapproved_limit = bureau_data["preapproved_limit"]
    monthly_income = bureau_data.get("monthly_income", 80000)
    total_accounts = bureau_data.get("total_accounts", 3)
    active_accounts = bureau_data.get("active_accounts", 2)
    closed_accounts = bureau_data.get("closed_accounts", 1)
    payment_history = bureau_data.get("payment_history", "000,000,000,000,000,000")
    
    # Determine score category
    if credit_score >= 750:
        score_category = "Excellent"
    elif credit_score >= 700:
        score_category = "Good"
    elif credit_score >= 650:
        score_category = "Fair"
    else:
        score_category = "Poor"
    
    # Generate realistic account details
    accounts = []
    
    # Credit Card 1
    if total_accounts >= 1:
        cc_limit = random.randint(150000, 300000)
        cc_balance = random.randint(int(cc_limit * 0.1), int(cc_limit * 0.3))
        accounts.append({
            "type": "Credit Card",
            "bank": "HDFC Bank",
            "account_num": f"XXXX-XXXX-XXXX-{random.randint(1000, 9999)}",
            "open_date": "12-Jan-2018",
            "credit_limit": cc_limit,
            "current_balance": cc_balance,
            "overdue": 0,
            "status": "Active",
            "payment_history": "000,000,000,000,000,000"
        })
    
    # Personal Loan
    if total_accounts >= 2:
        pl_sanctioned = random.randint(300000, 500000)
        pl_balance = random.randint(int(pl_sanctioned * 0.3), int(pl_sanctioned * 0.5))
        pl_overdue = 3500 if "030" in payment_history else 0
        accounts.append({
            "type": "Personal Loan",
            "bank": "ICICI Bank",
            "account_num": f"PL-XXXX-{random.randint(1000, 9999)}",
            "open_date": "10-Oct-2020",
            "sanctioned_amount": pl_sanctioned,
            "current_balance": pl_balance,
            "overdue": pl_overdue,
            "emi": random.randint(10000, 15000),
            "status": "Active",
            "payment_history": payment_history
        })
    
    # Home Loan
    if total_accounts >= 3:
        hl_sanctioned = random.randint(2500000, 3500000)
        hl_balance = random.randint(int(hl_sanctioned * 0.6), int(hl_sanctioned * 0.8))
        accounts.append({
            "type": "Home Loan",
            "bank": "SBI",
            "account_num": f"HL-XXXX-{random.randint(1000, 9999)}",
            "open_date": "20-Mar-2015",
            "sanctioned_amount": hl_sanctioned,
            "current_balance": hl_balance,
            "overdue": 5000 if credit_score < 750 else 0,
            "emi": random.randint(25000, 35000),
            "status": "Active",
            "payment_history": "000,000,000,000,000,000"
        })
    
    # Closed Credit Card
    if closed_accounts >= 1:
        accounts.append({
            "type": "Credit Card",
            "bank": "Axis Bank",
            "account_num": f"XXXX-XXXX-XXXX-{random.randint(1000, 9999)}",
            "open_date": "05-Sep-2016",
            "close_date": "15-Jan-2023",
            "credit_limit": 150000,
            "status": "Closed"
        })
    
    # Calculate totals
    total_credit_limit = sum(acc.get("credit_limit", 0) for acc in accounts)
    total_balance = sum(acc.get("current_balance", 0) for acc in accounts)
    total_overdue = sum(acc.get("overdue", 0) for acc in accounts)
    
    # Build the report
    report = f"""-----------------------------
        CIBIL CREDIT REPORT
-----------------------------

1. CREDIT SCORE
-----------------------------
Score                : {credit_score}
Score Category       : {score_category}
Score Date           : {datetime.now().strftime("%d-%b-%Y")}

2. PERSONAL INFORMATION
-----------------------------
Name                 : {name}
Gender               : Male
Date of Birth        : 15-Aug-1992
PAN                  : ABCPS1234K
ID Type              : PAN Card

3. CONTACT INFORMATION
-----------------------------
Primary Address      :
  Flat No. 202, Green Residency
  HSR Layout, Sector 2
  Bengaluru, Karnataka - 560102
  Residence Type: Owned

Phone Numbers        :
  Mobile (Primary)   : +91-98765 43210

Email IDs            :
  Primary            : {name.lower().replace(' ', '.')}@example.com

4. EMPLOYMENT INFORMATION
-----------------------------
Occupation Type      : Salaried
Employer             : ABC Technologies Pvt. Ltd.
Annual Income        : ₹ {monthly_income * 12:,}
Income Reported On   : 01-Apr-2025

5. ACCOUNT SUMMARY
-----------------------------
Total Accounts       : {total_accounts}
Active Accounts      : {active_accounts}
Closed Accounts      : {closed_accounts}

Total Credit Limit   : ₹ {total_credit_limit:,}
Total Current Balance: ₹ {total_balance:,}
Total Overdue Amount : ₹ {total_overdue:,}

Oldest Account Opened On : 20-Mar-2015
Recent Account Opened On : 10-Sep-2023

6. ACCOUNT DETAILS (TRADE LINES)
-----------------------------"""
    
    # Add individual account details
    for idx, acc in enumerate(accounts, 1):
        report += f"\n[{idx}] {acc['type']} - {acc['bank']}\n"
        report += f"    Account Number       : {acc['account_num']}\n"
        report += f"    Account Type         : {acc['type']}\n"
        report += f"    Ownership            : Single\n"
        report += f"    Open Date            : {acc['open_date']}\n"
        
        if acc['status'] == "Closed":
            report += f"    Close Date           : {acc.get('close_date', 'N/A')}\n"
            report += f"    Credit Limit         : ₹ {acc.get('credit_limit', 0):,}\n"
        else:
            report += f"    Last Payment Date    : {datetime.now().strftime('%d-%b-%Y')}\n"
            
            if "Credit Card" in acc['type']:
                report += f"    Credit Limit         : ₹ {acc['credit_limit']:,}\n"
                report += f"    Current Balance      : ₹ {acc['current_balance']:,}\n"
            else:
                report += f"    Sanctioned Amount    : ₹ {acc['sanctioned_amount']:,}\n"
                report += f"    Current Balance      : ₹ {acc['current_balance']:,}\n"
                report += f"    EMI Amount           : ₹ {acc['emi']:,}\n"
            
            report += f"    Amount Overdue       : ₹ {acc.get('overdue', 0):,}\n"
            
        report += f"    Status               : {acc['status']}\n"
        
        if acc.get('payment_history'):
            history_months = acc['payment_history'].split(',')
            months = ["Jun-25", "Jul-25", "Aug-25", "Sep-25", "Oct-25", "Nov-25"]
            report += f"    Payment History (Last 6 Months):\n"
            report += f"      {months[0]}: {history_months[0]}   {months[1]}: {history_months[1]}   {months[2]}: {history_months[2]}\n"
            report += f"      {months[3]}: {history_months[3]}   {months[4]}: {history_months[4]}   {months[5]}: {history_months[5]}\n"
            report += f"    (000 = No Dues, 030 = 30 days late, XXX = Default)\n"
        
        report += "\n"
    
    # Add enquiry information
    report += """7. ENQUIRY INFORMATION
-----------------------------
[1]  Date of Enquiry : 18-Oct-2025
     Enquiry Purpose : Credit Card
     Enquired Amount : ₹ 2,00,000
     Institution     : HDFC Bank

[2]  Date of Enquiry : 28-Jul-2024
     Enquiry Purpose : Personal Loan
     Enquired Amount : ₹ 4,00,000
     Institution     : ICICI Bank

"""
    
    # Add remarks
    remarks = []
    if credit_score >= 750:
        remarks.append("- Excellent credit behavior.")
    elif credit_score >= 700:
        remarks.append("- Overall credit behavior is good.")
    else:
        remarks.append("- Credit behavior needs improvement.")
    
    if total_overdue > 0:
        remarks.append(f"- Outstanding overdue amount: ₹{total_overdue:,}")
        remarks.append("- Recommended to clear overdues immediately.")
    
    utilization = (total_balance / total_credit_limit * 100) if total_credit_limit > 0 else 0
    if utilization > 50:
        remarks.append(f"- High credit utilization ({utilization:.1f}%).")
        remarks.append("- Recommended to reduce credit card balances.")
    elif utilization > 30:
        remarks.append(f"- Moderate credit utilization ({utilization:.1f}%).")
    
    report += "8. REMARKS\n"
    report += "-----------------------------\n"
    for remark in remarks:
        report += f"{remark}\n"
    
    return report