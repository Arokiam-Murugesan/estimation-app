import streamlit as st
import pandas as pd
import base64
from fpdf import FPDF
from datetime import date
# --- 1. நிறுவன விபரங்கள் மற்றும் கூகுள் ஷீட் இணைப்பு ---
COMPANY = "AROKIAM DIGITAL ESTIMATION"
ER_NAME = "Er. M. Balasubiramani, B.E. (Civil)"
PHONE = "8124380805"
# நீங்கள் கொடுத்த கூகுள் ஷீட் லிங்க் இங்கே நிரந்தரமாக இணைக்கப்பட்டுள்ளது
sheet_url = "https://docs.google.com/spreadsheets/d/1qCp_m98zndwyZu0LOBQzSDIewTr-JCnRQB80oNNPxl0/edit?usp=drivesdk" 
st.set_page_config(page_title=COMPANY, layout="wide")
# லாகின் பகுதி
if "login" not in st.session_state:
    st.title("🔐 AROKIAM OFFICIAL ACCESS")
    pwd = st.text_input("Admin Password", type="password")
    if st.button("Access System"):
        if pwd == "04044": st.session_state["login"] = True; st.rerun()
    st.stop()
# --- 2. SIDEBAR: Professional Details ---
with st.sidebar:
    st.header("👤 Professional Details")
    reg_no = st.text_input("Engineer Reg No:", "LS/RE/........")
    building_type = st.selectbox(
        "கட்டிட வகை (Building Type):",
        ["Residential Building", "Commercial Building", "Industrial Construction", "Heavy Civil Construction"]
    )
    st.write("---")
    st.header("🗺️ Site Boundaries (எல்லைகள்)")
    north = st.text_input("North By:", "Road / Site")
    south = st.text_input("South By:", "Vacant Land")
    east = st.text_input("East By:", "Others Property")
    west = st.text_input("West By:", "Others Property")
    st.write("---")
    st.write(f"📅 Date: {date.today()}")
st.title(f"🏗️ {COMPANY}")
# --- 3. RATE UPDATE NOTIFICATION (விலை அப்டேட் செய்தி) ---
try:
    csv_url = sheet_url.replace('/edit?usp=drivesdk', '/export?format=csv').replace('/edit?usp=sharing', '/export?format=csv')
    df_rates = pd.read_csv(csv_url)
    current_rates = df_rates.iloc[:15, 1].tolist()
    st.success(f"✅ PWD Rates successfully updated from Google Sheets! (Date: {date.today()})")
except:
    current_rates = [180, 4800, 45, 550, 78, 35, 120, 65000, 55000, 25, 1200, 75000, 15000, 8000, 50000]
    st.warning("⚠️ Using offline backup rates. Check internet connection.")
# --- 4. லேஅவுட் (டிராயிங் + இன்புட்) ---
col_plan, col_data = st.columns([1, 1.2])
with col_plan:
    st.header("📂 2D Approval Drawing")
    drawing = st.file_uploader("Upload Plan", type=["jpg", "png", "jpeg"])
    if drawing:
        st.image(drawing, caption="Approval Plan", use_container_width=True)
with col_data:
    st.header("📏 Dimensions")
    cust_name = st.text_input("Customer Name:", "ஆறுமுகம்")
    l_val = st.number_input("Building Length (ft):", value=30.0)
    b_val = st.number_input("Building Breadth (ft):", value=15.0)
    sqft_total = l_val * b_val
    wall_total = (l_val + b_val) * 2.2 
# --- 5. முழுமையான 15 பணிகள் பட்டியல் ---
works_final = [
    "Earthwork excavation for foundation in all types of soil",
    "P.C.C (1:4:8) for foundation with 40mm HBG metal",
    "Brick Work in C.M 1:6 for main walls (9 inch)",
    "R.C.C (1:1.5:3) M20 Grade for Roof Slab and Staircase",
    "ISI Brand TMT Steel Reinforcement - Supply & Bending",
    "Plastering with C.M 1:4 for internal and external walls",
    "Flooring with Vitrified Tiles / Granite and skirting",
    "Plumbing, Sanitary and Water Supply internal/external",
    "Electrical Points, Wiring (ISI Brand) and Main panel",
    "Painting with 2 coats Putty, Primer and Emulsion",
    "Compound Wall construction with Main Steel Gate",
    "Septic Tank (10 user) and UG Sump (6000 Liters)",
    "Rain Water Harvesting System with filtration pit",
    "Anti-Termite Treatment for foundation and basement",
    "Front Elevation, Architectural Design and Arch works"
]
data = {
    "S.No": range(1, 16),
    "Work Description": works_final,
    "L": [l_val, l_val, wall_total, l_val+12, 1.0, wall_total, l_val, 1.0, 1.0, wall_total, 90.0, 1.0, 1.0, 1.0, 1.0],
    "B": [b_val, b_val, 0.75, b_val, 1.0, 1.0, b_val, 1.0, 1.0, 1.0, 0.75, 1.0, 1.0, 1.0, 1.0],
    "D/H": [4.0, 0.5, 10.0, 0.45, 1.0, 10.0, 1.0, 1.0, 1.0, 10.0, 5.0, 1.0, 1.0, 1.0, 1.0],
    "Rate": current_rates
}
df = pd.DataFrame(data)
df["Qty"] = df["L"] * df["B"] * df["D/H"]
# Lumpsum வேலைகளுக்கு Qty 1 என நிலைநிறுத்துதல்
for i in [4, 7, 8, 11, 12, 13, 14]: df.at[i, "Qty"] = 1.0
# --- 6. டேபிள் காட்சி மற்றும் கணக்கீடு ---
st.subheader("📊 Official PWD Valuation Table")
edited_df = st.data_editor(df, column_order=("S.No", "Work Description", "L", "B", "D/H", "Qty", "Rate"), use_container_width=True, hide_index=True, height=550)
edited_df["Amount"] = edited_df["Qty"] * edited_df["Rate"]
total_amt = edited_df["Amount"].sum()
final_val = total_amt * 1.19 
loan_amt = final_val * 0.80
margin_amt = final_val * 0.20
cost_per_sqft = final_val / sqft_total if sqft_total > 0 else 0
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Area (Sq.ft)", f"{sqft_total:,.0f}")
c2.metric("Rate / Sq.ft", f"₹ {cost_per_sqft:,.2f}")
c3.metric("Grand Total Bank Value", f"₹ {final_val:,.2f}")
# --- 7. PDF ரிப்போர்ட் உருவாக்கம் ---
def get_pdf_download_link(customer, df_final, final_amt, l_amt, m_amt, b_type, r_no, sq, cps, n, s, e, w):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, COMPANY, ln=True, align='C')
    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 8, f"{ER_NAME} | Phone: {PHONE}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"Construction Estimate for: {customer}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(100, 8, f"Date: {date.today()} | Type: {b_type}", ln=True)
    pdf.cell(200, 8, f"Engineer Reg No: {r_no}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(200, 8, "Site Boundaries:", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.cell(47, 6, f"N: {n}", 1); pdf.cell(47, 6, f"S: {s}", 1)
    pdf.cell(47, 6, f"E: {e}", 1); pdf.cell(47, 6, f"W: {w}", 1)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(10, 8, "No", 1); pdf.cell(100, 8, "Description", 1)
    pdf.cell(20, 8, "Qty", 1); pdf.cell(25, 8, "Rate", 1); pdf.cell(35, 8, "Amount", 1)
    pdf.ln()
    pdf.set_font("Arial", '', 8)
    for index, row in df_final.iterrows():
        pdf.cell(10, 8, str(int(row['S.No'])), 1)
        pdf.cell(100, 8, row['Work Description'][:55], 1)
        pdf.cell(20, 8, str(round(row['Qty'], 1)), 1)
        pdf.cell(25, 8, str(row['Rate']), 1)
        pdf.cell(35, 8, f"{row['Amount']:,.2f}", 1)
        pdf.ln()
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(200, 8, f"TOTAL VALUATION: Rs. {final_amt:,.2f}", ln=True)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 8, f"Bank Loan Amount (80%): Rs. {l_amt:,.2f}", ln=True)
    pdf.cell(200, 8, f"Margin Amount (20%): Rs. {m_amt:,.2f}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 8)
    pdf.multi_cell(190, 5, "Note: This estimate follows PWD Schedule of Rates. All structural components like steel reinforcement use ISI Brand TMT bars. Concrete mix used is M20 grade.")
    pdf_output = pdf.output(dest='S').encode('latin-1')
    b64 = base64.b64encode(pdf_output).decode()
    return f'''<a href="data:application/pdf;base64,{b64}" download="Valuation_{customer}.pdf"><button style="background-color:#4CAF50; color:white; padding:12px 24px; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">📥 Download Official Report</button></a>'''
if st.button("📄 Generate Official Detailed Report"):
    st.balloons()
    st.markdown(get_pdf_download_link(cust_name, edited_df, final_val, loan_amt, margin_amt, building_type, reg_no, sqft_total, cost_per_sqft, north, south, east, west), unsafe_allow_html=True)