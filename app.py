import streamlit as st
import google.generativeai as genai
from PIL import Image
from fpdf import FPDF
import tempfile

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="SiteOptic Pro", page_icon="🏗️", layout="wide")

# 2. API SETUP
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ API Key missing. Check Streamlit Advanced Settings.")

# 3. SIDEBAR SETTINGS
with st.sidebar:
    st.header("⚙️ Settings / Ajustes")
    spanish_mode = st.toggle("🇪🇸 Modo Español / Spanish Mode")
    st.markdown("---")
    st.markdown("### SiteOptic Pro")
    st.caption("v7.0 - PDF Reports")

# 4. DEFINE THE BRAIN
if spanish_mode:
    language_instruction = "OUTPUT LANGUAGE: SPANISH (Español)."
else:
    language_instruction = "OUTPUT LANGUAGE: ENGLISH."

system_prompt = f"""
You are "SiteOptic," an expert General Contractor and Estimator.
{language_instruction}

*** GOAL ***
Inspect the photo, identify code issues (NJ Codes), and estimate Home Depot costs.

*** OUTPUT SECTIONS ***
You must provide the output in these 3 distinct sections:

SECTION 1: INSPECTION & CODES
- Identify scope of work.
- Flag NJ Code Violations (NEC 2020, IRC 2021, NSPC).
- If dangerous, start with "DANGER".

SECTION 2: HOME DEPOT ESTIMATE
- List Materials (Behr Paint, Ryobi tools, Lumber, etc.).
- Material Cost ($).
- Labor Hours estimate.
- TOTAL BUDGET RANGE.

SECTION 3: CLIENT TEXT DRAFT
- Write a polite text message for the homeowner.
"""

# PDF GENERATOR FUNCTION
def create_pdf(text, image):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="SiteOptic Inspection Report", ln=True, align='C')
    pdf.ln(10)
    
    # Add Image
    if image:
        # Save image to a temp file so PDF can read it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            image.save(tmp_file.name)
            # Resize image to fit page (width 100)
            pdf.image(tmp_file.name, x=55, y=30, w=100)
            pdf.ln(85) # Move cursor down past image

    # Add Text (Cleaned of emojis to prevent crash)
    pdf.set_font("Arial", size=10)
    # Encode/Decode to handle special characters smoothly
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    
    return pdf.output(dest='S').encode('latin-1')

# 5. SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_image" not in st.session_state:
    st.session_state.last_image = None
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# 6. MAIN APP LAYOUT
st.title("SiteOptic Pro 🏗️")
if spanish_mode:
    st.markdown("### El Capataz Digital (The Digital Foreman)")
else:
    st.markdown("### The Digital General Contractor")

uploaded_file = st.file_uploader("Upload Site Photo...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Site Condition", width=400)
    st.session_state.last_image = image

    analyze_btn_text = "Analizar Obra" if spanish_mode else "Generate Estimate & Report"
    
    if st.button(analyze_btn_text, type="primary"):
        with st.spinner("Analyzing..."):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content([system_prompt, image])
                
                st.session_state.messages = []
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.session_state.analysis_done = True
                
            except Exception as e:
                st.error(f"Error: {e}")

# 7. DISPLAY RESULTS
if st.session_state.analysis_done:
    main_response = st.session_state.messages[0]["content"]
    
    # TABS
    tab1, tab2 = st.tabs(["📋 Inspection & Estimate", "📱 Client Text Draft"])
    
    with tab1:
        st.markdown(main_response)
        
        # --- PDF DOWNLOAD BUTTON ---
        st.markdown("---")
        pdf_data = create_pdf(main_response, st.session_state.last_image)
        st.download_button(
            label="📄 Download Official PDF Report",
            data=pdf_data,
            file_name="SiteOptic_Report.pdf",
            mime="application/pdf"
        )
        
    with tab2:
        st.info("Copy and paste this to your client:")
        st.code(main_response.split("SECTION 3")[-1], language="text")

    # CHAT SECTION
    st.markdown("---")
    st.subheader("💬 Chat")
    
    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a follow-up..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                model = genai.GenerativeModel('gemini-2.5-flash')
                chat_context = [system_prompt, st.session_state.last_image]
                for msg in st.session_state.messages:
                    chat_context.append(msg["content"])
                
                response = model.generate_content(chat_context)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

st.markdown("---")
st.caption("© 2026 SiteOptic AI.")
