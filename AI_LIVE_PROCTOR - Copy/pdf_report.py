from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import suspicious
import os

def generate_pdf():

    if not suspicious.log_data:
        print("No suspicious activity.")
        return

    if not os.path.exists("reports"):
        os.makedirs("reports")

    doc = SimpleDocTemplate("reports/Exam_Report.pdf")
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("<b>AI Exam Proctor Report</b>", styles["Title"]))
    elements.append(Spacer(1, 0.5 * inch))

    for student_id, image_path in suspicious.log_data:
        elements.append(Paragraph(f"Student ID: {student_id}", styles["Normal"]))
        elements.append(Image(image_path, width=4 * inch, height=3 * inch))
        elements.append(Spacer(1, 0.5 * inch))

    doc.build(elements)

    print("PDF Generated Successfully!")
