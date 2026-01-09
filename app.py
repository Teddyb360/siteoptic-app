import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="SiteOptic Pro", page_icon="🏗️", layout="wide")

# 2. API SETUP
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ API Key missing. Check Streamlit Advanced Settings.")

# 3. SIDEBAR SETTINGS (Language Toggle)
with st.sidebar:
    st.header("⚙️ Settings / Ajustes")
    spanish_mode = st.toggle("🇪🇸 Modo Español / Spanish Mode")
    st.markdown("---")
    st.markdown("### SiteOptic Pro")
    st.caption("v6.0 - Multi-Trade & Bilingual")

# 4. DEFINE THE BRAIN (Dynamic System Prompt)
# We change the instructions based on the sidebar toggle
if spanish_mode:
    language_instruction = "OUTPUT LANGUAGE: SPANISH (Español). Use NJ Construction terminology in Spanish."
else:
    language_instruction = "OUTPUT LANGUAGE: ENGLISH."

system_prompt = f"""
You are "SiteOptic," an expert General Contractor and Estimator.
{language_instruction}

*** GOAL ***
Inspect the photo, identify code issues (NJ Codes), and estimate Home Depot costs.

*** OUTPUT SECTIONS ***
You must provide the output in these 3 distinct sections:

SECTION 1: 🧐 INSPECTION & CODES
- Identify scope of work.
- Flag NJ Code Violations (NEC 2020, IRC 2021, NSPC).
- If dangerous, start with "⚠️ DANGER".

SECTION 2: 📋 HOME DEPOT ESTIMATE
- List Materials (Behr Paint, Ryobi tools, Lumber, etc.).
- Material Cost ($).
- Labor Hours estimate.
- **TOTAL BUDGET RANGE**.

SECTION 3: 📱 CLIENT TEXT DRAFT
- Write a polite, professional text message (SMS) I can send to the homeowner.
- Summarize the issue politely and give the price. 
- Do NOT mention code violations aggressively; sound helpful.

"""

# 5. SESSION STATE (The Memory)
# This keeps the image and chat history from disappearing
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

# File Uploader
uploaded_file = st.file_uploader("Upload Site Photo...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Load and Display Image
    image = Image.open(uploaded_file)
    st.image(image, caption="Site Condition", width=400)
    
    # Save image to memory
    st.session_state.last_image = image

    # THE ANALYZE BUTTON
    analyze_btn_text = "Analizar Obra" if spanish_mode else "Generate Estimate & Report"
    
    if st.button(analyze_btn_text, type="primary"):
        with st.spinner("Analyzing... (Thinking in " + ("Spanish" if spanish_mode else "English") + ")"):
            try:
                # Call Gemini
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content([system_prompt, image])
                
                # Store the result in chat history
                st.session_state.messages = [] # Clear old chat
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.session_state.analysis_done = True
                
            except Exception as e:
                st.error(f"Error: {e}")

# 7. DISPLAY RESULTS (Tabs & Chat)
if st.session_state.analysis_done:
    
    # Get the main analysis text
    main_response = st.session_state.messages[0]["content"]
    
    # Create Tabs for cleaner view
    tab1, tab2 = st.tabs(["📋 Inspection & Estimate", "📱 Client Text Draft"])
    
    with tab1:
        st.markdown(main_response)
        
    with tab2:
        st.info("Copy and paste this to your client:")
        # We try to extract just the text message part, or user can copy from main text
        st.code(main_response.split("CLIENT TEXT DRAFT")[-1], language="text")

    st.markdown("---")
    st.subheader("💬 Chat with SiteOptic")
    
    # Display Chat History
    for message in st.session_state.messages[1:]: # Skip the first big report
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask a follow-up question (e.g., 'Is there a cheaper way?')..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                model = genai.GenerativeModel('gemini-2.5-flash')
                # We send the image + the chat history so it knows context
                chat_context = [system_prompt, st.session_state.last_image]
                for msg in st.session_state.messages:
                    chat_context.append(msg["content"])
                
                response = model.generate_content(chat_context)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

# Footer
st.markdown("---")
st.caption("© 2026 SiteOptic AI. Estimates are for guidance only.")
