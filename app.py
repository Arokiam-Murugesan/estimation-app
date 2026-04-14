import streamlit as st
import pandas as pd
import base64
from fpdf import FPDF
from datetime import date

# --- 1. நிறுவன விபரங்கள் ---
COMPANY = "AROKIAM DIGITAL ESTIMATION"
ER_NAME = "Er. M. Balasubiramani, B.E. (Civil)"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1qCp_m98zndwyZu0LOBQzSDIewTr-JCnRQB80oNNPxl0/export?format=csv"

st.set_page_config(page_title=COMPANY, layout="wide")

# லாகின் சிஸ்டம்
if "login" not in st.session_state:
    st.title("🔐 AROKIAM OFFICIAL ACCESS")
    pwd = st.text_input("Password", type="password")
    if st.button("Access"):
        if pwd == "04044": st.session_state["login"] = True; st.rerun()
    st.stop()

# --- 2. கட்டிட வகைக்கு ஏற்ப ஸ்மார்ட் ரேஷியோ (Building Type logic) ---
def get_smart_works(b_type):
    works = [
        "Earthwork excavation for foundation in all types of soil",
        "P.C.C (1:4:8) for foundation with 40mm HBG metal",
        "Brick Work in C.M 1:6 for main walls (9 inch)",
        "", # 4வது வரி (RCC) - இங்கே தான் Grade மாறும்
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
        works[3] = "R.C.C (1:1:2) M40 Grade for Heavy Duty Floors/Columns"
    elif b_type in ["Commercial Building", "Institutional", "Educational"]:
        works[3] = "R.C.C (1:1.2:2.4) M25 Grade for High Strength Structure"
    else:
        works[3] = "R.C.C (1:1.5:3) M20 Grade for Roof Slab and Staircase"
        
    return works

# --- 3. SIDEBAR (உள்ளீடுகள்) ---
with st.sidebar:
    st.header("📋 Project Configuration")
    cust_name = st.text_input("Customer Name:", "Nantha")
    reg_no = st.text_input("Engineer Reg No:", "LS/RE/........")
    st.write("---")
    building_type = st.selectbox(
        "Select Building Type:",
        ["Residential Building", "Commercial Building", "Industrial Construction", "Institutional", "Educational"]
    )
    st.write("---")
    st.header("🗺️ Boundaries")
    n = st.text_input("North:", "Road")
    s = st.text_input("South:", "Property")
    e = st.text_input("East:", "Property")
    w = st.text_input("West:", "Property")

st.title(f"🏗️ {COMPANY}")

# --- 4. டேட்டா லோடிங் & கணக்கீடு ---
try:
    df_raw = pd.read_csv(SHEET_URL)
    l_vals = pd.to_numeric(df_raw.iloc[:, 1], errors='coerce').fillna(1).tolist()
    b_vals = pd.to_numeric(df_raw.iloc[:, 2], errors='coerce').fillna(1).tolist()
    d_vals = pd.to_numeric(df_raw.iloc[:, 3], errors='coerce').fillna(1).tolist()
    rates = pd.to_numeric(df_raw.iloc[:, 4], errors='coerce').fillna(0).tolist()

    smart_works = get_smart_works(building_type)
    processed_data = []
    total_amt = 0

    for i in range(15):
        work = smart_works[i]
        l, b_in, d_in, rate = l_vals[i], b_vals[i], d_vals[i], rates[i]
        
        # Inch to Feet Converter
        b_ft, d_ft = b_in / 12, d_in / 12
        qty = l * b_ft * d_ft
        
        # Lumpsum Check
        if any(k in work for k in ["Plumbing", "Electrical", "Woodwork", "Septic", "Harvesting", "Termite"]):
            qty = 1.0

        amt = qty * rate
        total_amt += amt
        processed_data.append([i+1, work, l, b_in, d_in, round(qty, 2), rate, round(amt, 2)])

    df_final = pd.DataFrame(processed_data, columns=["S.No", "Work Details", "L(ft)", "B(in)", "D(in)", "Qty", "Rate", "Amount"])
    st.subheader(f"📊 Valuation Table: {building_type}")
    st.table(df_final)
    st.metric("GRAND TOTAL VALUE", f"₹ {total_amt:,.2f}")

except Exception as err:
    st.error(f"Sheet Access Error: {err}")

# --- 5. PDF ரிப்போர்ட் (PWD Rate & Govt Note உள்ளடக்கப்பட்டது) ---
def generate_pdf(name, df, total, rno, btype, n, s, e, w):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, COMPANY, ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(190, 5, f"{ER_NAME} | Reg No: {rno}", ln=True, align='C')
    pdf.ln(10)
    
    # Customer Details
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 8, f"Customer: {name}")
    pdf.cell(90, 8, f"Date: {date.today()}", ln=True, align='R')
    pdf.cell(190, 8, f"Structure: {btype}", ln=True)
    pdf.cell(190, 8, f"Boundaries: N: {n} | S: {s} | E: {e} | W: {w}", ln=True)
    pdf.ln(5)
    
    # Table Header
    pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", 'B', 7.5)
    w_cols = [8, 72, 10, 10, 10, 18, 22, 40]
    cols = ["S.No", "Work Details", "L(ft)", "B(in)", "D(in)", "Qty", "Rate", "Amount"]
    for i in range(len(cols)): pdf.cell(w_cols[i], 8, cols[i], 1, 0, 'C', True)
    pdf.ln()
    
    # Table Body
    pdf.set_font("Arial", '', 7)
    for index, row in df.iterrows():
        for i in range(len(w_cols)):
            align = 'R' if i == 7 else 'C'
            pdf.cell(w_cols[i], 7, str(row[i]), 1, 0, align)
        pdf.ln()
    
    pdf.ln(5); pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 10, f"TOTAL VALUATION: Rs. {total:,.2f}", ln=True, align='R')
    
    # முக்கிய குறிப்புகள் (The Final Professional Notes)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(190, 5, "IMPORTANT NOTES:", ln=True)
    pdf.set_font("Arial", 'I', 8)
    
    note1 = "1. Rates Reference: The rates used in this valuation are strictly based on the current PWD Schedule of Rates (SOR) and prevailing market trends."
    note2 = "2. Technical Basis: This estimate is prepared based on the Government Approved 2D Drawing/Blueprint provided by the client."
    note3 = "3. Compliance: Measurements are aligned with technical standards for building valuation purposes."
    
    pdf.multi_cell(190, 5, note1)
    pdf.multi_cell(190, 5, note2)
    pdf.multi_cell(190, 5, note3)

    return pdf.output(dest='S').encode('latin-1')

if st.button("📄 Generate & Download Final Report"):
    pdf_bytes = generate_pdf(cust_name, df_final, total_amt, reg_no, building_type, n, s, e, w)
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="Valuation_{cust_name}.pdf"><button style="background-color:#008CBA; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer;">Download PDF Report</button></a>'
    st.markdown(href, unsafe_allow_html=True)