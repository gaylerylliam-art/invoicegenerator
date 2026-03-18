import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import base64
import io
from dotenv import load_dotenv
from supabase import create_client, Client
from pdf_utils import generate_invoice_pdf

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Page config
st.set_page_config(page_title="Invoice Generator", page_icon="📄", layout="wide")

# Custom CSS for modern look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #8b4513;
        color: white;
    }
    .stButton>button:hover {
        background-color: #a0522d;
        color: white;
    }
    .invoice-header {
        color: #8b4513;
        font-family: 'Helvetica', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

def init_session_state():
    if 'line_items' not in st.session_state or st.session_state.line_items is None:
        st.session_state.line_items = [{"description": "Service Alpha", "sub_description": "Standard service", "quantity": 1, "price": 100.0}]

    default_invoice_data = {
        "invoice_number": "INV-000001",
        "date": datetime.now().date(),
        "currency": "USD",
        "business": {"name": "Zylker Design Labs", "address": "14B, Northern Street\nNew York", "trn": "", "logo": None},
        "client": {"name": "Jack Little", "address": "3242 Chandler Hollow Road\nPittsburgh", "trn": "", "delivery_address": ""},
        "tax_rate": 5.0,
        "terms": "Due on Receipt",
        "notes": "Thanks for your business.",
        "terms_conditions": "Terms and conditions apply.",
        "show_stamp": False,
        "stamp": None,
        "seller_signature": None,
        "customer_signature_required": True,
        "bank_details": {"bank_name": "", "account_name": "", "account_number": "", "iban": "", "swift": ""}
    }

    if 'invoice_data' not in st.session_state or st.session_state.invoice_data is None:
        st.session_state.invoice_data = default_invoice_data
    else:
        # Ensure all default keys exist (for existing sessions)
        for key, value in default_invoice_data.items():
            if key not in st.session_state.invoice_data:
                st.session_state.invoice_data[key] = value
            elif isinstance(value, dict) and isinstance(st.session_state.invoice_data[key], dict):
                # Deep merge for nested dicts like bank_details
                for sub_key, sub_value in value.items():
                    if sub_key not in st.session_state.invoice_data[key]:
                        st.session_state.invoice_data[key][sub_key] = sub_value

def main():
    init_session_state()
    
    # Defensive check
    if not isinstance(st.session_state.line_items, list):
        st.session_state.line_items = []
        
    st.title("📄 Professional Invoice Generator")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Invoice Details")
        
        with st.expander("Business Details", expanded=True):
            logo_file = st.file_uploader("Business Logo", type=["png", "jpg", "jpeg"])
            if logo_file:
                st.session_state.invoice_data["business"]["logo"] = logo_file.read()
                
            stamp_file = st.file_uploader("Company Stamp", type=["png", "jpg", "jpeg"])
            if stamp_file:
                st.session_state.invoice_data["stamp"] = stamp_file.read()

            sig_file = st.file_uploader("Seller Signature", type=["png", "jpg", "jpeg"])
            if sig_file:
                st.session_state.invoice_data["seller_signature"] = sig_file.read()

            st.session_state.invoice_data["business"]["name"] = st.text_input("Business Name", value=st.session_state.invoice_data["business"]["name"])
            st.session_state.invoice_data["business"]["trn"] = st.text_input("Business TRN/Tax ID", value=st.session_state.invoice_data["business"]["trn"])
            st.session_state.invoice_data["business"]["address"] = st.text_area("Business Address", value=st.session_state.invoice_data["business"]["address"])
            
        with st.expander("Client Details", expanded=True):
            st.session_state.invoice_data["client"]["name"] = st.text_input("Client Name", value=st.session_state.invoice_data["client"]["name"])
            st.session_state.invoice_data["client"]["trn"] = st.text_input("Client TRN/Tax ID", value=st.session_state.invoice_data["client"]["trn"])
            st.session_state.invoice_data["client"]["address"] = st.text_area("Client Address", value=st.session_state.invoice_data["client"]["address"])
            st.session_state.invoice_data["client"]["contact_person"] = st.text_input("Contact Person", value=st.session_state.invoice_data["client"]["contact_person"])
            st.session_state.invoice_data["client"]["contact_detail"] = st.text_input("Client Email/Phone", value=st.session_state.invoice_data["client"]["contact_detail"])
            
        with st.expander("Invoice Info", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.session_state.invoice_data["invoice_number"] = st.text_input("Invoice #", value=st.session_state.invoice_data["invoice_number"])
            with c2:
                st.session_state.invoice_data["date"] = st.date_input("Date", value=st.session_state.invoice_data["date"])
            with c3:
                st.session_state.invoice_data["currency"] = st.selectbox("Currency", ["USD", "AED", "EUR", "GBP", "INR"], index=0)

        st.subheader("Line Items")
        for i, item in enumerate(st.session_state.line_items):
            with st.container():
                cols = st.columns([4, 2, 2, 1])
                with cols[0]:
                    st.session_state.line_items[i]["description"] = st.text_input(f"Desc {i+1}", value=item["description"], key=f"desc_{i}")
                    st.session_state.line_items[i]["sub_description"] = st.text_input(f"Sub-desc {i+1}", value=item["sub_description"], key=f"subdesc_{i}")
                with cols[1]:
                    st.session_state.line_items[i]["quantity"] = st.number_input(f"Qty {i+1}", value=float(item["quantity"]), key=f"qty_{i}")
                with cols[2]:
                    st.session_state.line_items[i]["price"] = st.number_input(f"Price {i+1}", value=float(item["price"]), key=f"price_{i}")
                with cols[3]:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.line_items.pop(i)
                        st.rerun()
        
        if st.button("➕ Add Item"):
            st.session_state.line_items.append({"description": "", "sub_description": "", "quantity": 1, "price": 0.0})
            st.rerun()

        with st.expander("Taxes & Terms"):
            st.session_state.invoice_data["tax_rate"] = st.number_input("Tax Rate (%)", value=float(st.session_state.invoice_data["tax_rate"]))
            st.session_state.invoice_data["terms"] = st.text_input("Payment Terms", value=st.session_state.invoice_data["terms"])
            st.session_state.invoice_data["notes"] = st.text_area("Notes", value=st.session_state.invoice_data["notes"])
            st.session_state.invoice_data["terms_conditions"] = st.text_area("Terms & Conditions", value=st.session_state.invoice_data["terms_conditions"])
            
            st.session_state.invoice_data["customer_signature_required"] = st.checkbox("Include Customer Signature Area", value=st.session_state.invoice_data["customer_signature_required"])
            
            st.subheader("Bank Details")
            st.session_state.invoice_data["bank_details"]["bank_name"] = st.text_input("Bank Name", value=st.session_state.invoice_data["bank_details"]["bank_name"])
            st.session_state.invoice_data["bank_details"]["account_name"] = st.text_input("Account Name", value=st.session_state.invoice_data["bank_details"]["account_name"])
            st.session_state.invoice_data["bank_details"]["account_number"] = st.text_input("Account Number", value=st.session_state.invoice_data["bank_details"]["account_number"])
            st.session_state.invoice_data["bank_details"]["iban"] = st.text_input("IBAN", value=st.session_state.invoice_data["bank_details"]["iban"])
            st.session_state.invoice_data["bank_details"]["swift"] = st.text_input("SWIFT/BIC", value=st.session_state.invoice_data["bank_details"]["swift"])

    with col2:
        st.header("Live Preview")
        
        # Calculation
        subtotal = sum(item["quantity"] * item["price"] for item in st.session_state.line_items)
        tax = (subtotal * st.session_state.invoice_data["tax_rate"]) / 100
        total = subtotal + tax
        
        # Construction of flat HTML string to avoid markdown indentation issues
        logo_html = ""
        if st.session_state.invoice_data["business"]["logo"]:
            logo_b64 = base64.b64encode(st.session_state.invoice_data["business"]["logo"]).decode()
            logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-height: 80px; margin-bottom: 10px;">'

        # TRN strings
        seller_trn = (
            f'<div style="display: flex; margin-top: 5px; font-size: 0.85em; color: #666;">'
            f'<span style="width: 50px;"><strong>TRN:</strong></span>'
            f'<span>{st.session_state.invoice_data["business"]["trn"]}</span></div>'
        ) if st.session_state.invoice_data["business"]["trn"] else ""
        
        client_contact = (
            f'<div style="margin-top: 10px; border-top: 1px solid #ddd; padding-top: 10px;">'
            f'<div style="display: flex; font-size: 0.85em; color: #666; margin-bottom: 2px;">'
            f'<span style="width: 60px;"><strong>Contact:</strong></span>'
            f'<span>{st.session_state.invoice_data["client"]["contact_person"]}</span></div>'
            f'<div style="display: flex; font-size: 0.85em; color: #666;">'
            f'<span style="width: 60px;"><strong>Email:</strong></span>'
            f'<span>{st.session_state.invoice_data["client"]["contact_detail"]}</span></div></div>'
        ) if st.session_state.invoice_data["client"]["contact_person"] else ""

        client_trn = (
            f'<div style="display: flex; margin-top: 5px; font-size: 0.85em; color: #666;">'
            f'<span style="width: 60px;"><strong>TRN:</strong></span>'
            f'<span>{st.session_state.invoice_data["client"]["trn"]}</span></div>'
        ) if st.session_state.invoice_data["client"]["trn"] else ""

        preview_html = (
            f'<div style="padding: 40px; background: white; border: 1px solid #ddd; border-radius: 10px; color: black; font-family: sans-serif; min-height: 1000px; display: flex; flex-direction: column; position: relative;">'
            f'<div style="flex-grow: 1;">'
            f'<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 50px;">'
            f'<div>{logo_html}'
            f'<h2 style="color: #8b4513; margin: 15px 0 5px 0; font-size: 1.8em;">{st.session_state.invoice_data["business"]["name"]}</h2>'
            f'<div style="margin: 2px 0; font-size: 0.9em; color: #444; max-width: 320px; line-height: 1.5;">'
            f'{st.session_state.invoice_data["business"]["address"].replace("\\n", "<br>")}</div>{seller_trn}</div>'
            f'<div style="text-align: right;">'
            f'<h1 style="margin: 0; font-size: 3.5em; font-weight: 900; color: #000; line-height: 1;">INVOICE</h1>'
            f'<div style="margin-top: 20px; font-size: 0.95em; color: #444; display: inline-block; text-align: left;">'
            f'<div style="display: flex; margin-bottom: 5px;"><span style="width: 80px; font-weight: bold;">Invoice #:</span><span>{st.session_state.invoice_data["invoice_number"]}</span></div>'
            f'<div style="display: flex;"><span style="width: 80px; font-weight: bold;">Date:</span><span>{st.session_state.invoice_data["date"]}</span></div></div></div></div>'
            f'<hr style="border: 0; border-top: 2px solid #8b4513; margin: 40px 0;">'
            f'<div style="margin-bottom: 40px; background: #f9f9f9; padding: 25px; border-radius: 8px; border-left: 5px solid #8b4513;">'
            f'<h4 style="margin: 0 0 15px 0; color: #8b4513; text-transform: uppercase; font-size: 0.85em; letter-spacing: 1.5px; font-weight: bold;">Bill To:</h4>'
            f'<p style="margin: 0 0 8px 0; font-size: 1.3em; font-weight: bold; color: #000;">{st.session_state.invoice_data["client"]["name"]}</p>'
            f'<div style="margin: 0; font-size: 0.95em; color: #444; line-height: 1.6; max-width: 450px;">'
            f'{st.session_state.invoice_data["client"]["address"].replace("\\n", "<br>")}</div>{client_trn}{client_contact}</div>'
            f'<table style="width: 100%; margin-top: 30px; border-collapse: collapse;"><thead>'
            f'<tr style="border-bottom: 2px solid #8b4513;">'
            f'<th style="text-align: left; padding: 10px;">Description</th>'
            f'<th style="text-align: right; padding: 10px;">Qty</th>'
            f'<th style="text-align: right; padding: 10px;">Price</th>'
            f'<th style="text-align: right; padding: 10px;">Total</th></tr></thead><tbody>'
        )
        
        for item in st.session_state.line_items:
            preview_html += (
                f'<tr style="border-bottom: 1px solid #eee;">'
                f'<td style="padding: 10px;">{item["description"]}<br><small style="color: #666;">{item["sub_description"]}</small></td>'
                f'<td style="text-align: right; padding: 10px;">{item["quantity"]}</td>'
                f'<td style="text-align: right; padding: 10px;">{st.session_state.invoice_data["currency"]} {item["price"]:,.2f}</td>'
                f'<td style="text-align: right; padding: 10px;">{st.session_state.invoice_data["currency"]} {item["quantity"]*item["price"]:,.2f}</td></tr>'
            )
        
        preview_html += (
            f'</tbody></table>'
            f'<div style="margin-top: 40px; display: flex; justify-content: space-between;">'
            f'<div style="font-size: 0.9em; color: #666;">'
            f'<strong>Bank Details:</strong><br>'
            f'Bank: {st.session_state.invoice_data["bank_details"]["bank_name"]}<br>'
            f'Account: {st.session_state.invoice_data["bank_details"]["account_name"]}<br>'
            f'Number: {st.session_state.invoice_data["bank_details"]["account_number"]}<br>'
            f'IBAN: {st.session_state.invoice_data["bank_details"]["iban"]}<br>'
            f'SWIFT: {st.session_state.invoice_data["bank_details"]["swift"]}</div>'
            f'<div style="text-align: right; min-width: 250px;">'
            f'<table style="width: 100%; border-collapse: collapse;">'
            f'<tr><td style="padding: 5px 0; color: #666; text-align: left;">Subtotal:</td><td style="padding: 5px 0; text-align: right;">{st.session_state.invoice_data["currency"]} {subtotal:,.2f}</td></tr>'
            f'<tr><td style="padding: 5px 0; color: #666; text-align: left;">Tax ({st.session_state.invoice_data["tax_rate"]}%):</td><td style="padding: 5px 0; text-align: right;">{st.session_state.invoice_data["currency"]} {tax:,.2f}</td></tr>'
            f'<tr style="border-top: 2px solid #eee;"><td style="padding: 10px 0; font-size: 1.2em; font-weight: bold; color: #8b4513; text-align: left;">TOTAL:</td>'
            f'<td style="padding: 10px 0; font-size: 1.5em; font-weight: bold; color: #8b4513; text-align: right;">{st.session_state.invoice_data["currency"]} {total:,.2f}</td></tr></table>'
            f'</div></div></div>' # End of flex-grow div
        )

        # Footer (Stamp and Signatures)
        stamp_img = ""
        seller_sig_img = ""
        
        if st.session_state.invoice_data["stamp"]:
            stamp_b64 = base64.b64encode(st.session_state.invoice_data["stamp"]).decode()
            stamp_img = f'<img src="data:image/png;base64,{stamp_b64}" style="max-height: 100px; position: absolute; right: 20px; bottom: 30px; opacity: 0.7;">'
        
        if st.session_state.invoice_data["seller_signature"]:
            sig_b64 = base64.b64encode(st.session_state.invoice_data["seller_signature"]).decode()
            seller_sig_img = f'<img src="data:image/png;base64,{sig_b64}" style="max-height: 60px; display: block; margin: 0 auto;">'

        customer_sig_html = ""
        if st.session_state.invoice_data["customer_signature_required"]:
            customer_sig_html = (
                f'<div style="width: 200px; text-align: center; border-top: 1px solid #ddd; padding-top: 10px;">'
                f'<p style="margin: 0; font-size: 0.8em; color: #666;">Customer Acceptance Signature</p></div>'
            )

        footer_html = (
            f'<div style="margin-top: auto; display: flex; justify-content: space-between; align-items: flex-end; position: relative; padding-top: 40px; padding-bottom: 20px;">'
            f'{customer_sig_html}'
            f'<div style="width: 250px; text-align: center; position: relative;">'
            f'{stamp_img}'
            f'{seller_sig_img}'
            f'<div style="border-top: 1px solid #ddd; padding-top: 10px;">'
            f'<p style="margin: 0; font-size: 0.8em; color: #666;">Seller Authorized Signature</p></div>'
            f'</div></div>'
        )

        preview_html += footer_html
        preview_html += '</div>'
        
        # Use components.html for consistent rendering
        st.components.v1.html(preview_html, height=1000, scrolling=True)
        
        st.divider()
        
        if st.button("📥 Download PDF"):
            pdf_data = generate_invoice_pdf(st.session_state.invoice_data, st.session_state.line_items, subtotal, tax, total)
            st.download_button(
                label="Click here to download",
                data=pdf_data,
                file_name=f"invoice-{st.session_state.invoice_data['invoice_number']}.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
