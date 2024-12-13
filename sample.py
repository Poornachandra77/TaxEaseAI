from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(200, 10, 'Sample Tax Document', ln=True, align='C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, ln=True, align='L')

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)

# Create PDF object
pdf = PDF()
pdf.add_page()

# Add chapter title
pdf.chapter_title("Tax Filing Details")

# Add body content
pdf.chapter_body("""
Name: John Doe
Address: 123 Main Street, Springfield, IL 62701
Tax Year: 2024
Filing Status: Single
Income: $75,000
Tax Paid: $15,000
Refund Due: $2,500
""")

# Save the PDF
pdf.output("sample_tax_document.pdf")
