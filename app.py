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
    st.caption("v8.0 - Directed Mode")

# 4. SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_image" not in st.session_state:
    st.session_state.last_image = None
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# PDF GENERATOR FUNCTION
def create_pdf(text, image):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="SiteOptic Inspection Report", ln=True, align='C')
    pdf.ln(10)
    if image:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            image.save(tmp_file.name)
            pdf.image(tmp_file.name, x=55, y=30, w=100)
            pdf.ln(85)
    pdf.set_font("Arial", size=10)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

# 5. MAIN APP LAYOUT
st.title("SiteOptic Pro 🏗️")
if spanish_mode:
    st.markdown("### El Capataz Digital (The Digital Foreman)")
else:
    st.markdown("### The Digital General Contractor")

# File Uploader
uploaded_file = st.file_uploader("Upload Site Photo...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Site Condition", width=400)
    st.session_state.last_image = image

    # *** NEW FEATURE: SPECIFIC REQUEST BOX ***
    st.markdown("---")
    st.subheader("🎯 What do you want to check?")
    
    # Pre-filled options or custom text
    request_type = st.radio(
        "Select an option:",
        ["Everything (Full Inspection)", "Paint Estimate Only", "Electrical Only", "Plumbing Only", "Custom Request..."]
    )
    
    user_instruction = ""
    if request_type == "Custom Request...":
        user_instruction = st.text_input("Type your specific request here:", placeholder="e.g., Quote me for replacing this floor.")
    elif request_type != "Everything (Full Inspection)":
        user_instruction = f"Focus ONLY on {request_type}. Ignore other trades unless dangerous."

    # BUILD THE PROMPT DYNAMICALLY
    if spanish_mode:
        language_instruction = "OUTPUT LANGUAGE: SPANISH (Español)."
    else:
        language_instruction = "OUTPUT LANGUAGE: ENGLISH."

    # We add the user's specific instruction to the brain
    system_prompt = f"""
    You are "SiteOptic," an expert General Contractor.
    {language_instruction}
    
    *** USER INSTRUCTION ***
    The user wants: "{user_instruction if user_instruction else 'Full Inspection'}"
    STRICTLY FOLLOW THIS INSTRUCTION. If they ask for Paint, DO NOT talk about plumbing (unless it's an emergency).

    *** OUTPUT SECTIONS ***
    SECTION 1: INSPECTION & SCOPE
    - Address the User's specific request.
    - Flag NJ Code Violations (ONLY if relevant to the request or DANGEROUS).

    SECTION 2: HOME DEPOT ESTIMATE
    - List Materials relevant to the request.
    - Material Cost ($).
    - Labor Hours estimate.
    - TOTAL BUDGET RANGE.

    SECTION 3: CLIENT TEXT DRAFT
    - Write a polite text message for the homeowner regarding this specific request.
    """

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

# 6. DISPLAY RESULTS
if st.session_state.analysis_done:
    main_response = st.session_state.messages[0]["content"]
    
    tab1, tab2 = st.tabs(["📋 Inspection & Estimate", "📱 Client Text Draft"])
    
    with tab1:
        st.markdown(main_response)
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
