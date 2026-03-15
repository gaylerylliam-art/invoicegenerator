import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
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
    if 'items' not in st.session_state:
        st.session_state.items = [{"description": "Service Alpha", "sub_description": "Standard service", "quantity": 1, "price": 100.0}]

    if 'invoice_data' not in st.session_state:
        st.session_state.invoice_data = {
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
            "bank_details": {"bank_name": "", "account_name": "", "account_number": "", "iban": "", "swift": ""}
        }

def main():
    init_session_state()
    st.title("📄 Professional Invoice Generator")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Invoice Details")
        
        with st.expander("Business Details", expanded=True):
            st.session_state.invoice_data["business"]["name"] = st.text_input("Business Name", value=st.session_state.invoice_data["business"]["name"])
            st.session_state.invoice_data["business"]["trn"] = st.text_input("Business TRN/Tax ID", value=st.session_state.invoice_data["business"]["trn"])
            st.session_state.invoice_data["business"]["address"] = st.text_area("Business Address", value=st.session_state.invoice_data["business"]["address"])
            
        with st.expander("Client Details", expanded=True):
            st.session_state.invoice_data["client"]["name"] = st.text_input("Client Name", value=st.session_state.invoice_data["client"]["name"])
            st.session_state.invoice_data["client"]["trn"] = st.text_input("Client TRN/Tax ID", value=st.session_state.invoice_data["client"]["trn"])
            st.session_state.invoice_data["client"]["address"] = st.text_area("Client Address", value=st.session_state.invoice_data["client"]["address"])
            
        with st.expander("Invoice Info", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.session_state.invoice_data["invoice_number"] = st.text_input("Invoice #", value=st.session_state.invoice_data["invoice_number"])
            with c2:
                st.session_state.invoice_data["date"] = st.date_input("Date", value=st.session_state.invoice_data["date"])
            with c3:
                st.session_state.invoice_data["currency"] = st.selectbox("Currency", ["USD", "AED", "EUR", "GBP", "INR"], index=0)

        st.subheader("Line Items")
        for i, item in enumerate(st.session_state.items):
            with st.container():
                cols = st.columns([4, 2, 2, 1])
                with cols[0]:
                    st.session_state.items[i]["description"] = st.text_input(f"Desc {i+1}", value=item["description"], key=f"desc_{i}")
                    st.session_state.items[i]["sub_description"] = st.text_input(f"Sub-desc {i+1}", value=item["sub_description"], key=f"subdesc_{i}")
                with cols[1]:
                    st.session_state.items[i]["quantity"] = st.number_input(f"Qty {i+1}", value=float(item["quantity"]), key=f"qty_{i}")
                with cols[2]:
                    st.session_state.items[i]["price"] = st.number_input(f"Price {i+1}", value=float(item["price"]), key=f"price_{i}")
                with cols[3]:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.items.pop(i)
                        st.rerun()
        
        if st.button("➕ Add Item"):
            st.session_state.items.append({"description": "", "sub_description": "", "quantity": 1, "price": 0.0})
            st.rerun()

        with st.expander("Taxes & Terms"):
            st.session_state.invoice_data["tax_rate"] = st.number_input("Tax Rate (%)", value=float(st.session_state.invoice_data["tax_rate"]))
            st.session_state.invoice_data["terms"] = st.text_input("Payment Terms", value=st.session_state.invoice_data["terms"])
            st.session_state.invoice_data["notes"] = st.text_area("Notes", value=st.session_state.invoice_data["notes"])
            st.session_state.invoice_data["terms_conditions"] = st.text_area("Terms & Conditions", value=st.session_state.invoice_data["terms_conditions"])

    with col2:
        st.header("Live Preview")
        
        # Calculation
        subtotal = sum(item["quantity"] * item["price"] for item in st.session_state.items)
        tax = (subtotal * st.session_state.invoice_data["tax_rate"]) / 100
        total = subtotal + tax
        
        # Simple HTML Preview
        preview_html = f"""
        <div style="padding: 20px; background: white; border: 1px solid #ddd; border-radius: 10px; color: black; font-family: sans-serif;">
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <h2 style="color: #8b4513;">{st.session_state.invoice_data["business"]["name"]}</h2>
                    <p>{st.session_state.invoice_data["business"]["address"].replace('\\n', '<br>')}</p>
                </div>
                <div style="text-align: right;">
                    <h1>INVOICE</h1>
                    <p>#{st.session_state.invoice_data["invoice_number"]}<br>{st.session_state.invoice_data["date"]}</p>
                </div>
            </div>
            <hr>
            <div style="margin-top: 20px;">
                <strong>Bill To:</strong><br>
                {st.session_state.invoice_data["client"]["name"]}<br>
                {st.session_state.invoice_data["client"]["address"].replace('\\n', '<br>')}
            </div>
            <table style="width: 100%; margin-top: 30px; border-collapse: collapse;">
                <thead>
                    <tr style="border-bottom: 2px solid #8b4513;">
                        <th style="text-align: left; padding: 10px;">Description</th>
                        <th style="text-align: right; padding: 10px;">Qty</th>
                        <th style="text-align: right; padding: 10px;">Price</th>
                        <th style="text-align: right; padding: 10px;">Total</th>
                    </tr>
                </thead>
                <tbody>
        """
        for item in st.session_state.items:
            preview_html += f"""
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 10px;">{item["description"]}<br><small>{item["sub_description"]}</small></td>
                    <td style="text-align: right; padding: 10px;">{item["quantity"]}</td>
                    <td style="text-align: right; padding: 10px;">{st.session_state.invoice_data["currency"]} {item["price"]:,.2f}</td>
                    <td style="text-align: right; padding: 10px;">{st.session_state.invoice_data["currency"]} {item["quantity"]*item["price"]:,.2f}</td>
                </tr>
            """
        
        preview_html += f"""
                </tbody>
            </table>
            <div style="margin-top: 20px; text-align: right;">
                <p>Subtotal: {st.session_state.invoice_data["currency"]} {subtotal:,.2f}</p>
                <p>Tax ({st.session_state.invoice_data["tax_rate"]}%): {st.session_state.invoice_data["currency"]} {tax:,.2f}</p>
                <h3 style="color: #8b4513;">Total: {st.session_state.invoice_data["currency"]} {total:,.2f}</h3>
            </div>
        </div>
        """
        st.markdown(preview_html, unsafe_allow_html=True)
        
        st.divider()
        
        if st.button("📥 Download PDF"):
            pdf_data = generate_invoice_pdf(st.session_state.invoice_data, st.session_state.items, subtotal, tax, total)
            st.download_button(
                label="Click here to download",
                data=pdf_data,
                file_name=f"invoice-{st.session_state.invoice_data['invoice_number']}.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
