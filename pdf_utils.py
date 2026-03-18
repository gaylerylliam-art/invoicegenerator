from fpdf import FPDF
import io

def generate_invoice_pdf(data, items, subtotal, tax, total):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    # Logo and Company Info (LEFT)
    y_top = pdf.get_y()
    if data["business"].get("logo"):
        logo_stream = io.BytesIO(data["business"]["logo"])
        pdf.image(logo_stream, x=10, y=y_top, h=20)
        pdf.set_y(y_top + 25)
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(139, 69, 19) # Rust Color
    pdf.cell(100, 8, data["business"]["name"], ln=True)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(60, 60, 60)
    business_addr = data["business"]["address"].split("\n")
    for line in business_addr:
        pdf.cell(100, 4.5, line, ln=True)
    
    if data["business"].get("trn"):
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(10, 5, "TRN: ", ln=False)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(90, 5, data["business"]["trn"], ln=True)

    # Invoice Title and Metadata (RIGHT)
    pdf.set_xy(110, y_top)
    pdf.set_font("Helvetica", "B", 40)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(90, 20, "INVOICE", ln=True, align="R")
    
    pdf.ln(5)
    
    # Metadata Alignment (Right column, left-aligned within the block)
    meta_x = 150
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(60, 60, 60)
    
    pdf.set_xy(meta_x, pdf.get_y())
    pdf.cell(20, 5, "Invoice #:", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(30, 5, data["invoice_number"], ln=True)
    
    pdf.set_xy(meta_x, pdf.get_y())
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(20, 5, "Date:", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(30, 5, str(data["date"]), ln=True)
    
    pdf.set_y(pdf.get_y() + 10)
    pdf.set_draw_color(139, 69, 19)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)
    
    # Client details
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(139, 69, 19)
    pdf.cell(100, 6, "BILL TO:", ln=True)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 7, data["client"]["name"], ln=True)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    client_addr = data["client"]["address"].split("\n")
    for line in client_addr:
        pdf.cell(100, 5, line, ln=True)
    
    if data["client"].get("trn"):
        pdf.set_y(pdf.get_y() + 2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(10, 5, "TRN: ", ln=False)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(90, 5, data["client"]["trn"], ln=True)
        
    pdf.ln(10)
    
    # Table Header
    pdf.set_fill_color(139, 69, 19)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(100, 10, " Description", border=0, ln=False, fill=True)
    pdf.cell(30, 10, "Qty", border=0, ln=False, fill=True, align="R")
    pdf.cell(30, 10, "Price", border=0, ln=False, fill=True, align="R")
    pdf.cell(30, 10, "Total ", border=0, ln=True, fill=True, align="R")
    
    # Table Items
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    for item in items:
        # Check for page break
        if pdf.get_y() > 250:
            pdf.add_page()
            
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(100, 8, f" {item['description']}", border="B", ln=False)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(30, 8, str(item['quantity']), border="B", ln=False, align="R")
        pdf.cell(30, 8, f"{data['currency']} {item['price']:,.2f}", border="B", ln=False, align="R")
        pdf.cell(30, 8, f"{data['currency']} {item['quantity']*item['price']:,.2f} ", border="B", ln=True, align="R")
        
        if item.get("sub_description"):
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(190, 5, f"   {item['sub_description']}", ln=True)
            pdf.set_text_color(0, 0, 0)

    pdf.ln(10)
    
    # Totals
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100) # Gray for labels
    
    # Subtotal
    pdf.cell(130, 7, "", ln=False)
    pdf.cell(30, 7, "Subtotal:", ln=False, align="L")
    pdf.set_text_color(0, 0, 0)
    pdf.cell(30, 7, f"{data['currency']} {subtotal:,.2f} ", ln=True, align="R")
    
    # Tax
    pdf.set_text_color(100, 100, 100)
    pdf.cell(130, 7, "", ln=False)
    pdf.cell(30, 7, f"Tax ({data['tax_rate']}%):", ln=False, align="L")
    pdf.set_text_color(0, 0, 0)
    pdf.cell(30, 7, f"{data['currency']} {tax:,.2f} ", ln=True, align="R")
    
    pdf.ln(2)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(140, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)

    # Grand Total
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(139, 69, 19) # Rust accent color
    pdf.cell(130, 10, "", ln=False)
    pdf.cell(30, 10, "TOTAL:", ln=False, align="L")
    pdf.cell(30, 10, f"{data['currency']} {total:,.2f} ", ln=True, align="R")
    
    pdf.ln(10)
    
    # Bank Details
    if data.get("bank_details") and any(data["bank_details"].values()):
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(100, 5, "Bank Details:", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(100, 5, f"Bank: {data['bank_details']['bank_name']}", ln=True)
        pdf.cell(100, 5, f"Account: {data['bank_details']['account_name']}", ln=True)
        pdf.cell(100, 5, f"Number: {data['bank_details']['account_number']}", ln=True)
        pdf.cell(100, 5, f"IBAN: {data['bank_details']['iban']}", ln=True)
        pdf.cell(100, 5, f"SWIFT: {data['bank_details']['swift']}", ln=True)
        pdf.ln(5)

    # Signatures and Stamp at bottom of page
    y_sig = 250 # Fixed position near bottom (A4 is 297mm high)
    
    # Customer Signature
    if data.get("customer_signature_required"):
        pdf.set_font("Helvetica", "", 8)
        pdf.line(10, y_sig + 15, 70, y_sig + 15)
        pdf.text(10, y_sig + 19, "Customer Acceptance Signature")

    # Seller Signature and Stamp
    x_seller = 130
    if data.get("seller_signature"):
        sig_stream = io.BytesIO(data["seller_signature"])
        pdf.image(sig_stream, x=x_seller + 10, y=y_sig - 5, h=15)
    
    if data.get("stamp"):
        stamp_stream = io.BytesIO(data["stamp"])
        # Overlay stamp
        pdf.image(stamp_stream, x=x_seller + 30, y=y_sig - 15, h=25)

    pdf.line(x_seller, y_sig + 15, x_seller + 60, y_sig + 15)
    pdf.set_xy(x_seller, y_sig + 15)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(60, 5, "Seller Authorized Signature", ln=True, align="C")

    pdf.ln(5)
    
    # Terms & Notes
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(100, 5, "Notes:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(190, 5, data["notes"])
    
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(100, 5, "Terms & Conditions:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(190, 5, data["terms_conditions"])

    # Output to bytes
    output = io.BytesIO()
    pdf.output(output)
    return output.getvalue()
