import streamlit as st
import pandas as pd
import base64
from fpdf import FPDF
from datetime import date

# --- 1. Identity & Sheet Config ---
COMPANY = "AROKIAM DIGITAL ESTIMATION"
ER_NAME = "Er. M. Balasubiramani, B.E. (Civil)"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1qCp_m98zndwyZu0LOBQzSDIewTr-JCnRQB80oNNPxl0/export?format=csv"

st.set_page_config(page_title=COMPANY, layout="wide")

# Login Security
if "login" not in st.session_state:
    st.title("🔐 AROKIAM OFFICIAL ACCESS")
    pwd = st.text_input("Password", type="password")
    if st.button("Access"):
        if pwd == "04044": st.session_state["login"] = True; st.rerun()
    st.stop()

# --- 2. Smart Logic ---
def get_smart_works(b_type):
    works = [
        "Earthwork excavation for foundation in all types of soil",
        "P.C.C (1:4:8) for foundation with 40mm HBG metal",
        "Brick Work in C.M 1:6 for main walls (9 inch)",
        "", # RCC Row (Place Holder)
        "ISI Brand TMT Steel Reinforcement - Supply & Bending",
        "Plastering with C.M 1:4 for internal and external walls",
        "Flooring with Vitrified Tiles / Granite and skirting",
        "Plumbing, Sanitary and Water Supply internal/external",
        "Electrical Points, Wiring (ISI Brand) and Main panel",
        "Painting with 2 coats Putty, Primer and Emulsion",
        "Woodwork for Doors (Teak wood) and Windows (UPVC/Teak)",
        "Compound Wall construction with Main Steel Gate",
        "Septic Tank (10 user) and UG Sump (6000 Liters)",
        "Rain Water Harvesting System with filtration pit",
        "Anti-Termite Treatment for foundation and basement"
    ]
    if b_type == "Industrial Construction":
        works[3] = "R.C.C (1:1:2) M40 Grade for Heavy Duty Structure"
    elif b_type in ["Commercial Building", "Institutional", "Educational"]:
        works[3] = "R.C.C (1:1.2:2.4) M25 Grade for High Strength Structure"
    else:
        works[3] = "R.C.C (1:1.5:3) M20 Grade for Roof Slab and Staircase"
    return works

# --- 3. Sidebar Setup ---
with st.sidebar:
    st.header("📋 Configuration")
    cust_name = st.text_input("Customer Name:", "Nantha")
    reg_no = st.text_input("Engineer Reg No:", "LS/RE/........")
    b_type = st.selectbox("Building Type:", ["Residential Building", "Commercial Building", "Industrial Construction", "Institutional", "Educational"])
    st.header("🗺️ Boundaries")
    n, s, e, w = st.text_input("North:"), st.text_input("South:"), st.text_input("East:"), st.text_input("West:")

st.title(f"🏗️ {COMPANY}")

# --- 4. Processing ---
try:
    df_raw = pd.read_csv(SHEET_URL)
    l_vals = pd.to_numeric(df_raw.iloc[:, 1], errors='coerce').fillna(1).tolist()
    b_vals = pd.to_numeric(df_raw.iloc[:, 2], errors='coerce').fillna(1).tolist()
    d_vals = pd.to_numeric(df_raw.iloc[:, 3], errors='coerce').fillna(1).tolist()
    rates = pd.to_numeric(df_raw.iloc[:, 4], errors='coerce').fillna(0).tolist()

    smart_works = get_smart_works(b_type)
    final_list = []
    grand_total = 0

    for i in range(15):
        name = smart_works[i]
        l, b_in, d_in, r = l_vals[i], b_vals[i], d_vals[i], rates[i]
        
        # Calculation Logic
        qty = (l * (b_in/12) * (d_in/12))
        if any(k in name for k in ["Plumbing", "Electrical", "Woodwork", "Septic", "Harvesting", "Termite"]):
            qty = 1.0
        
        amt = qty * r
        grand_total += amt
        final_list.append([i+1, name, l, b_in, d_in, round(qty, 2), r, round(amt, 2)])

    df_display = pd.DataFrame(final_list, columns=["S.No", "Work Details", "L(ft)", "B(in)", "D(in)", "Qty", "Rate", "Amount"])
    st.table(df_display)
    st.metric("GRAND TOTAL VALUE", f"₹ {grand_total:,.2f}")

    # --- 5. Simplified PDF Generation ---
    def make_pdf(c_name, data, total, rno, bnd):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16); pdf.cell(190, 10, COMPANY, ln=True, align='C')
        pdf.set_font("Arial", '', 10); pdf.cell(190, 5, f"{ER_NAME} | Reg: {rno}", ln=True, align='C'); pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(100, 7, f"Customer: {c_name}")
        pdf.cell(90, 7, f"Date: {date.today()}", ln=True, align='R')
        pdf.cell(190, 7, f"Boundaries: {bnd}", ln=True); pdf.ln(5)
        
        # Header
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", 'B', 7)
        cols = [8, 75, 10, 10, 10, 15, 22, 35]
        heads = ["S.No", "Description", "L", "B", "D", "Qty", "Rate", "Amount"]
        for j in range(len(heads)): pdf.cell(cols[j], 8, heads[j], 1, 0, 'C', True)
        pdf.ln()
        
        # Data
        pdf.set_font("Arial", '', 7)
        for row in data:
            for k in range(len(row)):
                align = 'L' if k == 1 else 'C'
                pdf.cell(cols[k], 7, str(row[k]), 1, 0, align)
            pdf.ln()
            
        pdf.ln(5); pdf.set_font("Arial", 'B', 10)
        pdf.cell(190, 10, f"TOTAL ESTIMATED VALUE: Rs. {total:,.2f}", ln=True, align='R')
        
        # Professional Notes
        pdf.ln(5); pdf.set_font("Arial", 'I', 8)
        pdf.multi_cell(190, 5, "NOTES:\n1. Prepared as per Govt Approved Plan.\n2. Rates based on current PWD SOR.\n3. Market trends considered for valuation.")
        
        return pdf.output(dest='S').encode('latin-1')

    if st.button("📄 Download PDF Report"):
        b_text = f"N: {n} | S: {s} | E: {e} | W: {w}"
        pdf_out = make_pdf(cust_name, final_list, grand_total, reg_no, b_text)
        b64 = base64.b64encode(pdf_out).decode()
        st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="Report_{cust_name}.pdf">Click here to Download PDF</a>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error Loading Data: {e}")