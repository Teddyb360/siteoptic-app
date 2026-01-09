import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CONFIGURE THE PAGE
st.set_page_config(page_title="SiteOptic AI", page_icon="🏗️", layout="centered")

# 2. HIDE THE API KEY
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ API Key missing. Please check your Streamlit Advanced Settings.")

# 3. THE "BRAIN" (System Prompt)
system_prompt = """
You are "SiteOptic," a seasoned NJ Construction Foreman. 
Your goal is to identify code violations and safety hazards in photos.

*** PRIORITY KNOWLEDGE: NEW JERSEY AMENDMENTS ***
1. PLUMBING: NJ uses 2021 NSPC (National Standard Plumbing Code).
2. ELECTRICAL: NJ follows 2020 NEC.
3. BUILDING: NJ follows 2021 IRC. 
   - Frost Line is 36 inches. 
   - Radon mitigation is mandatory (Tier 1 state).

RULES:
1. If you see a hazard, start with "⚠️ DANGER".
2. Always end with: "Disclaimer: I am an AI, not a licensed official. Verify with local building dept."
"""

# 4. THE "BODY" (Website Design)
st.title("SiteOptic 🏗️")
st.markdown("### The Digital Foreman in Your Pocket.")
st.info("Built for New Jersey Pros. Snap a photo to check for code violations.")

# 5. THE CONNECTING PIECE
uploaded_file = st.file_uploader("Upload a site photo...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Site Photo", use_column_width=True)
    
    if st.button("Run SiteOptic Inspection"):
        with st.spinner("Analyzing against NJ Codes..."):
            try:
                # *** THE FIX IS HERE: USING YOUR SPECIFIC MODEL ***
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                response = model.generate_content([system_prompt, image])
                st.success("Inspection Complete")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("© 2026 SiteOptic AI. Not a substitute for professional inspection.")
