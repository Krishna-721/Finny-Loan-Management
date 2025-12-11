from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import os

def generate_sanction_letter_pdf(data, filename=None):
    """
    Generates a professional sanction letter PDF
    """
    
    if not filename:
        app_id = data.get("Application ID", "LF00000")
        filename = f"sanction_letter_{app_id}.pdf"
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                           topMargin=0.75*inch, bottomMargin=0.75*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2D7FF9'),
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#6366f1'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=14
    )
    
    # Header
    header = Paragraph("LOANFLOW AI", title_style)
    elements.append(header)
    
    subheader = Paragraph("LOAN SANCTION LETTER", title_style)
    elements.append(subheader)
    elements.append(Spacer(1, 0.3*inch))
    
    # Application details
    app_info = [
        ["Application ID:", data.get("Application ID", "N/A")],
        ["Date:", data.get("Date", datetime.now().strftime("%d %B %Y"))]
    ]
    
    app_table = Table(app_info, colWidths=[2*inch, 4*inch])
    app_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(app_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Greeting
    greeting = Paragraph(f"Dear {data.get('Applicant Name', 'Customer')},", normal_style)
    elements.append(greeting)
    elements.append(Spacer(1, 0.15*inch))
    
    # Approval message
    approval_msg = Paragraph(
        "<b>Congratulations!</b> Your loan application has been <b>APPROVED</b>.",
        normal_style
    )
    elements.append(approval_msg)
    elements.append(Spacer(1, 0.2*inch))
    
    # Loan Details Section
    loan_heading = Paragraph("LOAN DETAILS", heading_style)
    elements.append(loan_heading)
    
    loan_details = [
        ["Applicant Name", data.get("Applicant Name", "N/A")],
        ["PAN Number", data.get("PAN Number", "N/A")],
        ["Loan Type", data.get("Loan Type", "N/A")],
        ["Sanctioned Amount", data.get("Sanctioned Amount", "N/A")],
        ["Tenure", data.get("Tenure", "N/A")],
        ["Interest Rate", data.get("Interest Rate", "N/A")],
        ["Monthly EMI", data.get("Monthly EMI", "N/A")],
        ["Total Repayment", data.get("Total Repayment", "N/A")]
    ]
    
    loan_table = Table(loan_details, colWidths=[2.5*inch, 3.5*inch])
    loan_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(loan_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Credit Assessment Section
    credit_heading = Paragraph("CREDIT ASSESSMENT", heading_style)
    elements.append(credit_heading)
    
    credit_details = [
        ["CIBIL Score", str(data.get("CIBIL Score", "N/A"))],
        ["FOIR", data.get("FOIR", "N/A")],
        ["Risk Category", data.get("Risk Category", "N/A")],
        ["Approval Scenario", data.get("Approval Scenario", "N/A")]
    ]
    
    credit_table = Table(credit_details, colWidths=[2.5*inch, 3.5*inch])
    credit_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(credit_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_text = Paragraph(
        "<i>Generated by LoanFlow AI | Demo for EY Techathon </i>",
        ParagraphStyle('Footer', parent=styles['Normal'], 
                      fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
    )
    elements.append(Spacer(1, 0.5*inch))
    elements.append(footer_text)
    
    # Build PDF
    doc.build(elements)
    
    return filepath


def generate_sanction_letter(data, filename="sanction_letter.pdf"):
    """
    Legacy function for backward compatibility
    Generates simple PDF using reportlab
    """
    from reportlab.pdfgen import canvas
    
    pdf = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width/2, height - 50, "LoanFlow AI - Sanction Letter")
    
    # Content
    pdf.setFont("Helvetica", 12)
    y_position = height - 100
    
    for key, val in data.items():
        pdf.drawString(100, y_position, f"{key}: {val}")
        y_position -= 25
    
    pdf.save()
    return filename