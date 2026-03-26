import streamlit as st
import language_tool_python
import re
from langdetect import detect, DetectorFactory

# Stability for language detection
DetectorFactory.seed = 0

# Page configuration
st.set_page_config(page_title="Faria Global QA Auditor", page_icon="🌍")

# Caching for language tools to save memory
@st.cache_resource
def get_tool(lang):
    try:
        return language_tool_python.LanguageTool(lang)
    except:
        return language_tool_python.LanguageTool('en-US')

# --- Header Section (Styled without external images) ---
st.markdown("""
    <div style='text-align: center; padding: 10px; border-bottom: 2px solid #FF4B4B;'>
        <h1 style='color: #FF4B4B; margin-bottom: 0;'>FARIA EDUCATION GROUP</h1>
        <p style='font-size: 1.2em; color: #555;'>Global Standards QA Auditor</p>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer
st.write("Automated format and grammar audit for curriculum standards in any language.")

# --- Input Section ---
texto_input = st.text_area("Paste your standards here (one per line):", height=300, 
                          placeholder="Example:\n1.1. Analyzing historical data.\n1.2. Analizar datos históricos.")

# --- Process Button ---
if st.button("🚀 Start Global Audit"):
    if texto_input:
        lineas = texto_input.strip().split('\n')
        
        # Progress bar
        progress_bar = st.progress(0)
        status_info = st.empty()
        
        status_info.info(f"Auditing {len(lineas)} lines... Please wait.")
        
        for i, linea in enumerate(lineas, 1):
            linea = linea.strip()
            if not linea: continue
            
            errors = []
            
            # 1. Language Detection
            try:
                lang_code = detect(linea)
                actual_lang = 'ca-ES' if lang_code == 'ca' else lang_code
            except:
                lang_code = "unknown"
                actual_lang = 'en-US'

            # 2. Faria Universal Format Rules
            # Capital/Number check
            if not re.match(r'^([A-Z]|[0-9])', linea): 
                errors.append("❌ Must start with an Uppercase letter or a Number.")
            # Period check
            if not linea.endswith('.'): 
                errors.append("❌ Missing period at the end.")
            # Double spaces
            if "  " in linea:
                errors.append("⚠️ Double spaces detected.")

            # 3. Grammar & Typos (Protected)
            try:
                tool = get_tool(actual_lang)
                matches = tool.check(linea)
                for m in matches:
                    rule_id = getattr(m, 'ruleId', '')
                    if rule_id not in ['UPPERCASE_SENTENCE_START', 'LC_AFTER_PERIOD']:
                        msg = getattr(m, 'message', 'Grammar/Spelling issue')
                        errors.append(f"⚠️ ({lang_code.upper()}) {msg}")
            except Exception:
                errors.append(f"ℹ️ Note: Grammar check skipped for this line.")

            # 4. Display Results
            if not errors:
                st.success(f"Line {i} OK: {linea[:60]}...")
            else:
                with st.expander(f"Line {i}: Issues found ({lang_code.upper()})", expanded=True):
                    st.write(f"**Source:** {linea}")
                    for err in errors:
                        st.write(err)
            
            # Update progress
            progress_bar.progress(i / len(lineas))
            
        status_info.empty()
        st.success("🎉 Audit Complete!")
        st.balloons()
    else:
        st.warning("The input area is empty. Please paste your standards.")
