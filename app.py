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

# லாகின்
if "login" not in st.session_state:
    st.title("🔐 AROKIAM OFFICIAL ACCESS")
    pwd = st.text_input("Password", type="password")
    if st.button("Access"):
        if pwd == "04044": st.session_state["login"] = True; st.rerun()
    st.stop()

# --- 2. கட்டிட வகை லாஜிக் ---
def get_smart_works(b_type):
    works = [
        "Earthwork excavation for foundation in all types of soil",
        "P.C.C (1:4:8) for foundation with 40mm HBG metal",
        "Brick Work in C.M 1:6 for main walls (9 inch)",
        "", # RCC Row
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

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("📋 Configuration")
    cust_name = st.text_input("Customer Name:", "Nantha")
    reg_no = st.text_input("Engineer Reg No:", "LS/RE/........")
    building_type = st.selectbox("Select Building Type:", ["Residential Building", "Commercial Building", "Industrial Construction", "Institutional", "Educational"])
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
        b_ft, d_ft = b_in / 12, d_in / 12
        qty = l * b_ft * d_ft
        
        if any(k in work for k in ["Plumbing", "Electrical", "Woodwork", "Septic", "Harvesting", "Termite"]):
            qty = 1.0

        amt = qty * rate
        total_amt += amt
        processed_data.append({"S.No": i+1, "Work Details": work, "L(ft)": l, "B(in)": b_in, "D(in)": d_in, "Qty": round(qty, 2), "Rate": rate, "Amount": round(amt, 2)})

    df_final = pd.DataFrame(processed_data)
    st.table(df_final)
    st.metric("GRAND TOTAL VALUE", f"₹ {total_amt:,.2f}")

    # --- 5. PDF தயாரிப்பு (பிழை இல்லாமல்) ---
    def generate_pdf(name, df, total, rno, n, s, e, w):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16); pdf.cell(190, 10, COMPANY, ln=True, align='C')
        pdf.set_font("Arial", '', 10); pdf.cell(190, 5, f"{ER_NAME} | Reg No: {rno}", ln=True, align='C'); pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(100, 8, f"Customer: {name}")
        pdf.cell(90, 8, f"Date: {date.today()}", ln=True, align='R')
        pdf.cell(190, 8, f"Boundaries: N: {n} | S: {s} | E: {e} | W: {w}", ln=True); pdf.ln(5)
        
        # Table Header
        pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", 'B', 7)
        headers = ["S.No", "Work Details", "L(ft)", "B(in)", "D(in)", "Qty", "Rate", "Amount"]
        w_cols = [8, 70, 10, 10, 10, 18, 24, 40]
        for i in range(len(headers)): pdf.cell(w_cols[i], 8, headers[i], 1, 0, 'C', True)
        pdf.ln()
        
        # Table Body (டேட்டா எடுக்கும் முறை திருத்தப்பட்டது)
        pdf.set_font("Arial", '', 7)
        for index, row in df.iterrows():
            pdf.cell(w_cols[0], 7, str(row['S.No']), 1, 0, 'C')
            pdf.cell(w_cols[1], 7, str(row['Work Details']), 1, 0, 'L')
            pdf.cell(w_cols[2], 7, str(row['L(ft)']), 1, 0, 'C')
            pdf.cell(w_cols[3], 7, str(row['B(in)']), 1, 0, 'C')
            pdf.cell(w_cols[4], 7, str(row['D(in)']), 1, 0, 'C')
            pdf.cell(w_cols[5], 7, str(row['Qty']), 1, 0, 'C')
            pdf.cell(w_cols[6], 7, str(row['Rate']), 1, 0, 'R')
            pdf.cell(w_cols[7], 7, str(row['Amount']), 1, 0, 'R')
            pdf.ln()
            
        pdf.ln(5); pdf.set_font("Arial", 'B', 11)
        pdf.cell(190, 10, f"TOTAL VALUE: Rs. {total:,.2f}", ln=True, align='R')
        return pdf.output(dest='S').encode('latin-1')

    if st.button("📄 Generate & Download Final Report"):
        pdf_bytes = generate_pdf(cust_name, df_final, total_amt, reg_no, n, s, e, w)
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="Valuation_{cust_name}.pdf">Download PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

except Exception as ex:
    st.error(f"Error: {ex}")