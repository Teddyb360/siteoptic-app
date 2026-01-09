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
    st.error("⚠️ API Key missing. Check Streamlit Advanced Settings.")

# 3. THE "BRAIN" (Multi-Trade Home Depot Estimator)
system_prompt = """
You are "SiteOptic," an expert General Contractor and Estimator.
Your goal is to inspect photos and generate a detailed Material & Labor estimate.

*** PRICING SOURCE ***
All material prices must be based on standard **HOME DEPOT** retail pricing. 
Name specific brands carried there (e.g., Behr, Hampton Bay, Leviton, Ryobi, Carlon).

*** TRADE KNOWLEDGE ***
1. **PAINTING:** Estimate wall sq ft. Quote "Behr Premium Plus" gallons + roller/tape costs.
2. **FRAMING:** Quote "2x4 KD Whitewood Studs". Estimate count based on 16" OC spacing.
3. **PLUMBING/ELEC:** Follow NJ Codes (NSPC/NEC). Quote specific boxes/fittings.
4. **GENERAL:** Flooring, Drywall, Finish Carpentry.

*** OUTPUT FORMAT ***
For the photo provided, generate this Report:

1. **[🧐 THE SCOPE]**: What needs to be done (Fixing, Building, or Painting).
2. **[⚠️ CODE CHECK]**: Flag any NJ Code Violations (if applicable).
3. **[🛒 HOME DEPOT CART]**:
   - **Materials**: List specific items (e.g., "2 Gal Behr Ultra Pure White Satin").
   - **Unit Price**: Est. price (e.g., "~$38.00/gal").
   - **Subtotal**: Total for materials.
4. **[👷 LABOR ESTIMATE]**:
   - Hours needed vs. Difficulty.
5. **[💰 GRAND TOTAL]**: A realistic Budget Range for the whole job.

"""

# 4. THE "BODY" (Updated Interface)
st.title("SiteOptic 🏗️")
st.markdown("### The Digital General Contractor")
st.info("Snap a photo of ANY job (Framing, Paint, Electric) for a Home Depot price list.")

# 5. THE CONNECTING PIECE
uploaded_file = st.file_uploader("Upload a site photo...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Site Photo", use_column_width=True)
    
    # We changed the button text to match the new features
    if st.button("Get Price Estimate & Code Check"):
        with st.spinner("Checking Home Depot Prices..."):
            try:
                # Using the smart 2.5 Flash model
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                response = model.generate_content([system_prompt, image])
                st.success("Estimate Ready")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("© 2026 SiteOptic AI. Prices are estimates based on Home Depot averages.")
