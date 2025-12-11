from core.pdf_generator import generate_sanction_letter_pdf
from datetime import datetime

def create_sanction_letter(data):
    """
    Creates a sanction letter with enhanced formatting
    Returns filename of generated PDF
    """
    
    # Prepare formatted data
    formatted_data = {
        "Application ID": data.get("application_id", "LF00000"),
        "Date": datetime.now().strftime("%d %B %Y"),
        "Applicant Name": data.get("name", "N/A"),
        "PAN Number": data.get("pan", "N/A"),
        "Loan Type": f"{data.get('loan_type', 'Personal')} Loan",
        "Sanctioned Amount": f"₹{data.get('loan_amount', 0):,}",
        "Tenure": f"{data.get('tenure', 12)} months",
        "Interest Rate": f"{data.get('interest_rate', 0)}% p.a.",
        "Monthly EMI": f"₹{data.get('emi', 0):,}",
        "Total Repayment": f"₹{int(data.get('emi', 0) * data.get('tenure', 12)):,}",
        "CIBIL Score": data.get('credit_score', 0),
        "FOIR": f"{data.get('foir', 0):.1f}%",
        "Risk Category": data.get('risk', 'Medium'),
        "Approval Scenario": f"{data.get('scenario', 'A')} - {data.get('scenario_label', 'Instant Approval')}"
    }
    
    # Generate PDF
    filename = generate_sanction_letter_pdf(formatted_data)
    
    return filename