# sanction_agent.py — FIXED FOR PROTOTYPE

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import io

def generate_sanction_letter(data, underwriting, app_id):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, 10 * inch, "Loan Sanction Letter")

    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, 9.4 * inch, f"Application ID: {app_id}")
    c.drawString(1 * inch, 9.1 * inch, f"Applicant: {data['name']}")
    c.drawString(1 * inch, 8.8 * inch, f"Loan Amount: ₹{data['loan_amount']:,}")
    c.drawString(1 * inch, 8.5 * inch, f"Tenure: {data['tenure']} months")
    c.drawString(1 * inch, 8.2 * inch, f"Rate: {underwriting['final_rate']}%")
    c.drawString(1 * inch, 7.9 * inch, f"Monthly EMI: ₹{underwriting['emi']:,}")

    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, 7.3 * inch, "Terms:")
    c.drawString(1 * inch, 7.0 * inch, "- Auto-generated letter")
    c.drawString(1 * inch, 6.8 * inch, "- Subject to verification")
    c.drawString(1 * inch, 6.6 * inch, "- Conditions may apply")

    c.showPage()
    c.save()
    buffer.seek(0)

    return buffer
