import streamlit as st
import language_tool_python
import re
from langdetect import detect, DetectorFactory
import gc

DetectorFactory.seed = 0

st.set_page_config(page_title="Faria Global QA Auditor", page_icon="🛡️")

@st.cache_resource
def get_tool(lang):
    try:
        return language_tool_python.LanguageTool(lang)
    except:
        return language_tool_python.LanguageTool('en-US')

# --- Header Section ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.jpg", width=250)
    except:
        st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>FARIA EDUCATION GROUP</h2>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center;'>Global Standards Auditor</h3>", unsafe_allow_html=True)
st.write("---")

# --- Input Section ---
texto_input = st.text_area("Paste standards here (Max 1,000 lines):", height=250)

if st.button("🚀 Run Audit"):
    if texto_input:
        lineas = [l.strip() for l in texto_input.strip().split('\n') if l.strip()]
        total = len(lineas)
        
        if total > 1000:
            st.error(f"⚠️ Batch too large! Please use max 1,000 lines.")
        else:
            progress_bar = st.progress(0)
            status_info = st.empty()
            
            ok_count = 0
            error_count = 0

            # Contenedor para que los resultados aparezcan aquí
            st.subheader("Audit Results:")

            for i, linea in enumerate(lineas, 1):
                line_errors = []
                
                try:
                    lang_code = detect(linea)
                    actual_lang = 'ca-ES' if lang_code == 'ca' else lang_code
                except:
                    lang_code = "en"
                    actual_lang = 'en-US'

                if not re.match(r'^([A-Z]|[0-9])', linea): 
                    line_errors.append("❌ Must start with Uppercase or Number.")
                if not linea.endswith('.'): 
                    line_errors.append("❌ Missing period at the end.")
                if "  " in linea:
                    line_errors.append("⚠️ Double spaces detected.")

                try:
                    tool = get_tool(actual_lang)
                    matches = tool.check(linea)
                    for m in matches:
                        rid = getattr(m, 'ruleId', '')
                        if rid not in ['UPPERCASE_SENTENCE_START', 'LC_AFTER_PERIOD']:
                            msg = getattr(m, 'message', 'Potential typo')
                            line_errors.append(f"⚠️ ({lang_code.upper()}) {msg}")
                except:
                    pass

                # --- 4. DISPLAY SIN MENÚ DESPLEGABLE ---
                if not line_errors:
                    ok_count += 1
                else:
                    error_count += 1
                    # Usamos st.info o st.warning con un diseño limpio
                    st.markdown(f"**Line {i}:** {linea}")
                    for e in line_errors:
                        st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;{e}") # Sangría para los errores
                    st.write("---") # Línea divisoria entre errores
                
                progress_bar.progress(i / total)
                if i % 10 == 0:
                    status_info.text(f"Processing line {i} of {total}...")
            
            status_info.empty()
            st.success(f"🎉 Done! ✅ {ok_count} Passed | ❌ {error_count} Issues found.")
            gc.collect() 
    else:
        st.warning("Please paste some text first.")
