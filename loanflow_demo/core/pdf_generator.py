from fpdf import FPDF

def generate_sanction_letter(data, filename="sanction_letter.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)

    pdf.cell(200, 10, txt="LoanFlow AI - Sanction Letter", ln=True, align='C')
    pdf.ln(10)

    for key, val in data.items():
        pdf.cell(200, 10, txt=f"{key}: {val}", ln=True)

    pdf.output(filename)
    return filename
