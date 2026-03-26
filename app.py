import streamlit as st
import language_tool_python
import re
from langdetect import detect, DetectorFactory
import gc

DetectorFactory.seed = 0

st.set_page_config(page_title="Faria Global QA Auditor", page_icon="🛡️")

# --- Optimized Language Engine (Forced English UI) ---
@st.cache_resource
def get_tool(lang):
    # Mapping for detection
    mapping = {'en': 'en-US', 'es': 'es', 'fr': 'fr', 'de': 'de', 'it': 'it', 'pt': 'pt'}
    target_lang = mapping.get(lang, 'en-US')
    
    try:
        # 'motherTag' en-US fuerza a que los mensajes de error vengan en inglés
        return language_tool_python.LanguageTool(target_lang, motherTag='en-US')
    except:
        return language_tool_python.LanguageTool('en-US')

# --- Header ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.jpg", width=250)
    except:
        st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>FARIA EDUCATION GROUP</h2>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center;'>Global Standards Auditor</h3>", unsafe_allow_html=True)
st.write("---")

texto_input = st.text_area("Paste standards here (Max 1,000 lines):", height=250)

if st.button("🚀 Run Audit"):
    if texto_input:
        lineas = [l.strip() for l in texto_input.strip().split('\n') if l.strip()]
        total = len(lineas)
        
        if total > 1000:
            st.error(f"⚠️ Batch too large! Max 1,000 lines.")
        else:
            progress_bar = st.progress(0)
            status_info = st.empty()
            error_count = 0

            st.subheader("Audit Results:")

            for i, linea in enumerate(lineas, 1):
                line_errors = []
                
                # 1. Detection
                try:
                    lang_code = detect(linea)
                except:
                    lang_code = "en"

                # 2. Format Rules (English only)
                if not re.match(r'^([A-Z]|[0-9])', linea): 
                    line_errors.append("❌ Must start with Uppercase or Number.")
                if not linea.endswith('.'): 
                    line_errors.append("❌ Missing period at the end.")
                if "  " in linea:
                    line_errors.append("⚠️ Double spaces detected.")

                # 3. Spelling & Grammar (Forced English Messages)
                try:
                    tool = get_tool(lang_code)
                    matches = tool.check(linea)
                    for m in matches:
                        # Ignoramos reglas de formato que ya cubrimos manualmente
                        if m.ruleId not in ['UPPERCASE_SENTENCE_START', 'LC_AFTER_PERIOD', 'WHITESPACE_RULE']:
                            # El mensaje m.message vendrá ahora en inglés gracias al motherTag
                            line_errors.append(f"⚠️ **({lang_code.upper()})** {m.message}")
                except:
                    pass

                # 4. Display (Vista Abierta)
                if line_errors:
                    error_count += 1
                    st.markdown(f"**Line {i}:** {linea}")
                    for e in line_errors:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{e}")
                    st.write("---")
                
                progress_bar.progress(i / total)
            
            status_info.empty()
            st.success(f"🎉 Audit Complete! Found issues in {error_count} lines.")
            gc.collect()
    else:
        st.warning("Please paste some text first.")
