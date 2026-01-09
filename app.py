import streamlit as st
import google.generativeai as genai

st.title("SiteOptic Diagnostic 🛠️")

# 1. Setup the Key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    st.success("✅ API Key found.")
except Exception as e:
    st.error(f"❌ API Key Error: {e}")

# 2. Ask Google what models are available
st.write("Asking Google for available models...")

try:
    # List all models
    model_list = []
    for m in genai.list_models():
        # We only want models that can "generateContent" (chat)
        if 'generateContent' in m.supported_generation_methods:
            model_list.append(m.name)
            st.code(m.name) # Print the name on screen

    if not model_list:
        st.warning("⚠️ No models found! Your API Key might be valid but has no permissions.")
    else:
        st.success(f"✅ Found {len(model_list)} models. The server can see them!")

except Exception as e:
    st.error(f"❌ Connection Error: {e}")
