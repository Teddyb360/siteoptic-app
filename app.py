import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CONFIGURE THE PAGE
st.set_page_config(page_title="SiteOptic AI", page_icon="🏗️", layout="centered")

# 2. HIDE THE API KEY (We will set this up in Step 3)
# This looks for the key in the settings so it's not visible in the code
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. THE "BRAIN" (Your System Prompt)
system_prompt = """
You are "SiteOptic," a seasoned NJ Construction Foreman. 
Your goal is to identify code violations and safety hazards in photos.
RULES:
1. Prioritize NJ Uniform Construction Code (UCC) and 2020 NEC.
2. If you see a hazard, start with "⚠️ DANGER".
3. Always end with: "Disclaimer: I am an AI, not a licensed official."
"""

# 4. THE "BODY" (The Website Design)
st.title("SiteOptic 🏗️")
st.markdown("### The Digital Foreman in Your Pocket.")
st.info("Built for New Jersey Pros. Snap a photo to check for code violations.")

# 5. THE CONNECTING PIECE (Camera/Upload)
uploaded_file = st.file_uploader("Upload a site photo...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the image
    image = Image.open(uploaded_file)
    st.image(image, caption="Site Photo", use_column_width=True)
    
    # The "Scan" Button
    if st.button("Run SiteOptic Inspection"):
        with st.spinner("Analyzing against NJ Codes..."):
            try:
                # CONNECT TO GEMINI
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content([system_prompt, image])
                
                # SHOW THE RESULT
                st.success("Inspection Complete")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Connection Error: {e}")

# Footer
st.markdown("---")
st.caption("© 2026 SiteOptic AI. Not a substitute for professional inspection.")
