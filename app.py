import streamlit as st
import pandas as pd
import base64
from fpdf import FPDF
from datetime import date
# --- 1. நிறுவன விபரங்கள் ---
COMPANY = "AROKIAM DIGITAL ESTIMATION"
ER_NAME = "Er. M. Balasubiramani, B.E. (Civil)"
# REG_NO = "" # உங்களுக்கு நம்பர் வந்தவுடன் இங்கே சேர்த்துக்கொள்ளலாம்
PHONE = "8124380805"
st.set_page_config(page_title=COMPANY, layout="wide")
# லாகின்
if "login" not in st.session_state:
    st.title("🔐 AROKIAM OFFICIAL ACCESS")
    pwd = st.text_input("Admin Password", type="password")
    if st.button("Access System"):
        if pwd == "04044": st.session_state["login"] = True; st.rerun()
    st.stop()
# --- 2. SIDEBAR: PWD News & Guidelines ---
with st.sidebar:
    st.header("📢 PWD & Govt Updates")
    st.info("""
    **Latest SoR Update:** அரசு அங்கீகாரம் பெற்ற புதிய PWD Schedule of Rates (2024-25) அடிப்படையில் இந்த எஸ்டிமேட் கணக்கிடப்படுகிறது.
    """)
    st.warning("""
    **Bank Loan Tips:**
    வங்கி லோன் பெற 2D Drawing-ல் உள்ள அளவுகளும், எஸ்டிமேட் அளவுகளும் (L, B, D) துல்லியமாக இருக்க வேண்டும்.
    """)
    st.write("---")
    st.write(f"📅 Date: {date.today()}")
st.title(f"🏗️ {COMPANY}")
# --- 3. லேஅவுட் (டிராயிங் + இன்புட்) ---
col_plan, col_data = st.columns([1, 1.2])
with col_plan:
    st.header("📂 2D Approval Drawing")
    drawing = st.file_uploader("Upload Plan", type=["jpg", "png", "jpeg"])
    if drawing:
        st.image(drawing, caption="கஸ்டமர் கொடுத்த அப்ரூவல் பிளான்", use_container_width=True)
    else:
        st.info("டிராயிங்கை இங்கே அப்லோட் செய்யவும்.")
with col_data:
    st.header("📏 Dimensions")
    cust_name = st.text_input("Customer Name:", "ஆறுமுகம்")
    l_val = st.number_input("Building Length (ft):", value=30.0)
    b_val = st.number_input("Building Breadth (ft):", value=15.0)
    wall_total = (l_val + b_val) * 2.2 
# --- 4. 15 பணிகள் பட்டியல் ---
works_final = [
    "1. Earthwork excavation for foundation in all types of soil",
    "2. P.C.C (1:4:8) for foundation with 40mm HBG metal",
    "3. Brick Work in C.M 1:6 for main walls (9 inch)",
    "4. R.C.C (1:1.5:3) for Roof Slab and Staircase",
    "5. Steel Reinforcement - Supply, bending and binding",
    "6. Plastering with C.M 1:4 for internal and external walls",
    "7. Flooring with Vitrified Tiles / Granite and skirting",
    "8. Plumbing, Sanitary and Water Supply internal/external",
    "9. Electrical Points, Wiring, Switches and Main panel",
    "10. Painting with 2 coats Putty, Primer and Emulsion",
    "11. Compound Wall construction with Main Steel Gate",
    "12. Septic Tank (10 user) and UG Sump (6000 Liters)",
    "13. Rain Water Harvesting System with filtration pit",
    "14. Anti-Termite Treatment for foundation and basement",
    "15. Front Elevation, Architectural Design and Arch works"
]
data = {
    "S.No": range(1, 16),
    "Work Description": works_final,
    "L": [l_val, l_val, wall_total, l_val+12, 1.0, wall_total, l_val, 1.0, 1.0, wall_total, 90.0, 1.0, 1.0, 1.0, 1.0],
    "B": [b_val, b_val, 0.75, b_val, 1.0, 1.0, b_val, 1.0, 1.0, 1.0, 0.75, 1.0, 1.0, 1.0, 1.0],
    "D/H": [4.0, 0.5, 10.0, 0.45, 1.0, 10.0, 1.0, 1.0, 1.0, 10.0, 5.0, 1.0, 1.0, 1.0, 1.0],
    "Rate": [180, 4800, 45, 550, 78, 35, 120, 65000, 55000, 25, 1200, 75000, 15000, 8000, 50000]
}
df = pd.DataFrame(data)
df["Qty"] = df["L"] * df["B"] * df["D/H"]
for i in [4, 7, 8, 11, 12, 13, 14]: df.at[i, "Qty"] = 1.0
# --- 5. டேபிள் காட்சி ---
st.subheader("📊 Official PWD Valuation Table (1 to 15)")
edited_df = st.data_editor(
    df, 
    column_order=("S.No", "Work Description", "L", "B", "D/H", "Qty", "Rate"),
    use_container_width=True, 
    hide_index=True, 
    height=600 
)
# தொகை கணக்கீடு
edited_df["Amount"] = edited_df["Qty"] * edited_df["Rate"]
total_amt = edited_df["Amount"].sum()
final_val = total_amt * 1.19 # 19% Tax & Contingency
st.divider()
c1, c2 = st.columns(2)
c1.info(f"Sub Total: ₹ {total_amt:,.2f}")
c2.success(f"**Final Valuation (Bank Value): ₹ {final_val:,.2f}**")
# --- 6. புதிய விரிவான PDF டவுன்லோட் ஃபங்க்ஷன் ---
def get_pdf_download_link(customer, df_final, final_amt):
    pdf = FPDF()
    pdf.add_page()
    # லெட்டர் ஹெட்
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, COMPANY, ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(200, 8, f"Engineer: {ER_NAME}", ln=True, align='C')
    pdf.cell(200, 8, f"Phone: {PHONE}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"Construction Estimate for: {customer}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(200, 8, f"Date: {date.today()}", ln=True)
    pdf.ln(5)
    # அட்டவணை தலைப்புகள் (Table Headers)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(15, 10, "S.No", 1)
    pdf.cell(80, 10, "Description", 1)
    pdf.cell(20, 10, "Qty", 1)
    pdf.cell(30, 10, "Rate", 1)
    pdf.cell(40, 10, "Amount", 1)
    pdf.ln()
    # 15 பணிகளையும் பிடிஎப்-ல் சேர்த்தல்
    pdf.set_font("Arial", '', 9)
    for index, row in df_final.iterrows():
        pdf.cell(15, 10, str(int(row['S.No'])), 1)
        # நீண்ட விளக்கத்தைச் சுருக்கிக் காட்டுதல்
        desc = row['Work Description'][:45]
        pdf.cell(80, 10, desc, 1)
        pdf.cell(20, 10, str(round(row['Qty'], 1)), 1)
        pdf.cell(30, 10, str(row['Rate']), 1)
        pdf.cell(40, 10, str(round(row['Amount'], 2)), 1)
        pdf.ln()
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"GRAND TOTAL VALUATION: Rs. {final_amt:,.2f}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(200, 10, "Note: This estimate follows PWD Schedule of Rates.", ln=True)
    # PDF-ஐ என்கோட் செய்து லிங்க் உருவாக்குதல்
    pdf_output = pdf.output(dest='S').encode('latin-1')
    b64 = base64.b64encode(pdf_output).decode()
    return f'''
        <a href="data:application/pdf;base64,{b64}" download="Detailed_Valuation_{customer}.pdf" style="text-decoration:none;">
            <button style="background-color:#4CAF50; color:white; padding:10px 24px; border:none; border-radius:4px; cursor:pointer;">
                📥 Download Full Detailed Report
            </button>
        </a>
    '''
# டவுன்லோட் பட்டன்
if st.button("📄 Prepare Official Report"):
    st.balloons()
    # எடிட் செய்யப்பட்ட டேபிளை வைத்து PDF உருவாக்குதல்
    st.markdown(get_pdf_download_link(cust_name, edited_df, final_val), unsafe_allow_html=True)