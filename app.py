import streamlit as st
import language_tool_python
import re
from langdetect import detect, DetectorFactory

# Stability for language detection
DetectorFactory.seed = 0

st.set_page_config(page_title="Faria Global QA Auditor", page_icon="🌍")

@st.cache_resource
def get_tool(lang):
    # Try to load specific language, fallback to English if it fails
    try:
        return language_tool_python.LanguageTool(lang)
    except:
        return language_tool_python.LanguageTool('en-US')

st.title("🌍 Faria Universal QA Auditor")
st.write("Automated format and grammar audit for standards in any language.")

# Text area with English labels
texto_input = st.text_area("Paste your standards here:", height=300, placeholder="1.1. Drawing conclusions...\n1.2. Extraer conclusiones...")

if st.button("🚀 Start Audit"):
    if texto_input:
        lineas = texto_input.strip().split('\n')
        progress_bar = st.progress(0)
        
        st.info(f"Processing {len(lineas)} lines...")
        
        for i, linea in enumerate(lineas, 1):
            linea = linea.strip()
            if not linea: continue
            
            errors = []
            
            # 1. Secure Language Detection
            try:
                lang_code = detect(linea)
                actual_lang = 'ca-ES' if lang_code == 'ca' else lang_code
            except:
                lang_code = "unknown"
                actual_lang = 'en-US'

            # 2. Faria Format Rules (Universal)
            if not re.match(r'^([A-Z]|[0-9])', linea): 
                errors.append("❌ Must start with an Uppercase letter or a Number.")
            if not linea.endswith('.'): 
                errors.append("❌ Missing period at the end.")
            if "  " in linea:
                errors.append("⚠️ Double spaces detected.")

            # 3. Protected Grammar Validation
            try:
                tool = get_tool(actual_lang)
                matches = tool.check(linea)
                for m in matches:
                    rule_id = getattr(m, 'ruleId', '')
                    # Ignore start-of-sentence casing (already validated manually)
                    if rule_id not in ['UPPERCASE_SENTENCE_START', 'LC_AFTER_PERIOD']:
                        msg = getattr(m, 'message', 'Grammar/Spelling error')
                        errors.append(f"⚠️ ({lang_code.upper()}) {msg}")
            except Exception:
                errors.append(f"ℹ️ Note: Could not complete grammar check for this line.")

            # 4. Display Results
            if not errors:
                st.success(f"Line {i} OK: {linea[:50]}...")
            else:
                with st.expander(f"Line {i}: Issues found ({lang_code.upper()})", expanded=True):
                    st.write(f"**Text:** {linea}")
                    for err in errors:
                        st.write(err)
            
            progress_bar.progress(i / len(lineas))
            
        st.balloons() # A little celebration when finished!
    else:
        st.warning("Please paste some text before starting.")
