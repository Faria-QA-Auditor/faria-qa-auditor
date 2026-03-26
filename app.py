import streamlit as st
import language_tool_python
import re
from langdetect import detect, DetectorFactory

# Stability for language detection
DetectorFactory.seed = 0

# Page configuration
st.set_page_config(page_title="Faria Global QA Auditor", page_icon="🌍")

# Caching for language tools
@st.cache_resource
def get_tool(lang):
    # Try to load specific language, fallback to English if it fails
    try:
        return language_tool_python.LanguageTool(lang)
    except:
        return language_tool_python.LanguageTool('en-US')

# --- Header with Logo and Title ---
# Faria Logo
st.image("https://raw.githubusercontent.com/fariaedu/fariaedu.github.io/master/assets/img/faria-education-group-logo.png", width=300)

# Main Title and Description
st.title("🌍 Global QA Auditor")
st.write("Automated format and grammar audit for standards in any language.")
st.write("---") # Visual separator

# --- Input Section ---
texto_input = st.text_area("Paste your standards here (one per line):", height=300, placeholder="1.1. Drawing conclusions...\n1.2. Extraer conclusiones...")

# --- Process Button ---
if st.button("🚀 Start Audit"):
    if texto_input:
        lineas = texto_input.strip().split('\n')
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty() # Placeholder for status text
        
        status_text.info(f"Processing {len(lineas)} lines...")
        
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
            # Rule 1: Must start with Uppercase or Number
            if not re.match(r'^([A-Z]|[0-9])', linea): 
                errors.append("❌ Must start with an Uppercase letter or a Number.")
            
            # Rule 2: Missing period at the end
            if not linea.endswith('.'): 
                errors.append("❌ Missing period at the end.")
            
            # Rule 3: Double spaces
            if "  " in linea:
                errors.append("⚠️ Double spaces detected.")

            # 3. Protected Grammar Validation
            try:
                tool = get_tool(actual_lang)
                matches = tool.check(linea)
                for m in matches:
                    rule_id = getattr(m, 'ruleId', '')
                    # Ignore start-of-sentence casing rules (already validated manually)
                    if rule_id not in ['UPPERCASE_SENTENCE_START', 'LC_AFTER_PERIOD']:
                        msg = getattr(m, 'message', 'Grammar/Spelling issue')
                        errors.append(f"⚠️ ({lang_code.upper()}) {msg}")
            except Exception:
                errors.append(f"ℹ️ Note: Grammar check was skipped for this line.")

            # 4. Display Results
            if not errors:
                st.success(f"Line {i} OK: {linea[:50]}...")
            else:
                with st.expander(f"Line {i}: Issues found ({lang_code.upper()})", expanded=True):
                    st.write(f"**Text:** {linea}")
                    for err in errors:
                        st.write(err)
            
            # Update progress bar
            progress_bar.progress(i / len(lineas))
            
        status_text.empty() # Clear status info
        st.success("🎉 Audit complete!")
        st.balloons() # Celebration!
    else:
        st.warning("Please paste some text before starting.")
