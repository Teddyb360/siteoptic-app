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

# 3. THE "BRAIN" (System Prompt with ESTIMATOR LOGIC)
system_prompt = """
You are "SiteOptic," an expert Construction Foreman and Project Estimator.
Your goal is to inspect photos, identify issues, and create a ROUGH JOB ESTIMATE.

*** PRIORITY KNOWLEDGE ***
1. PLUMBING: NSPC standards.
2. ELECTRICAL: 2020 NEC.
3. BUILDING: 2021 IRC.

*** OUTPUT FORMAT ***
For every issue you find, you MUST provide this exact structure:

1. **[THE ISSUE]**: What is wrong and the Code Violation (if any).
2. **[THE FIX]**: How to repair it properly.
3. **[📋 JOB ESTIMATE]**:
   - **Materials Needed**: List the parts (e.g., "2x4 studs, 1/2" drywall").
   - **Material Cost**: Estimated range (e.g., "$50 - $75").
   - **Labor Estimate**: Time to fix (e.g., "2-3 hours").
   - **Total Budget**: A conservative range for the whole job.

RULES:
1. If you see a hazard, start with "⚠️ DANGER".
2. Always end with: "Disclaimer: Estimates are based on national averages. Actual local prices may vary."
"""

# 4. THE "BODY" (Marketing Text Updated)
st.title("SiteOptic 🏗️")
st.markdown("### The Digital Foreman in Your Pocket.")

# *** CHANGE: Broader Marketing Text ***
st.info("Professional Grade. Snap a photo for code checks & instant job estimates.")

# 5. THE CONNECTING PIECE
uploaded_file = st.file_uploader("Upload a site photo...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Site Photo", use_column_width=True)
    
    if st.button("Generate Estimate & Inspection"):
        with st.spinner("Calculating Materials & Costs..."):
            try:
                # Using the Gemini 2.5 Flash model
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                response = model.generate_content([system_prompt, image])
                st.success("Estimate Generated")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("© 2026 SiteOptic AI. Estimates are for guidance only.")
