import streamlit as st
import language_tool_python
import re
from langdetect import detect, DetectorFactory
import gc

DetectorFactory.seed = 0

st.set_page_config(page_title="Faria Global QA Auditor", page_icon="🛡️")

# --- Motor Profesional con Caché ---
@st.cache_resource
def get_tool(lang):
    mapping = {'en': 'en-US', 'es': 'es', 'fr': 'fr', 'de': 'de', 'it': 'it', 'pt': 'pt'}
    target_lang = mapping.get(lang, 'en-US')
    # Forzamos que la interfaz de respuesta sea en inglés (motherTag)
    return language_tool_python.LanguageTool(target_lang, motherTag='en-US')

# --- Header ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.jpg", width=250)
    except:
        st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>FARIA</h2>", unsafe_allow_html=True)

st.write("---")

texto_input = st.text_area("Paste standards here (Max 1,000 lines):", height=250)

if st.button("🚀 Run Global Audit"):
    if texto_input:
        lineas = [l.strip() for l in texto_input.strip().split('\n') if l.strip()]
        total = len(lineas)
        
        progress_bar = st.progress(0)
        error_count = 0
        st.subheader("Audit Findings:")

        for i, linea in enumerate(lineas, 1):
            line_errors = []
            
            # 1. Detect Language
            try:
                lang_code = detect(linea)
            except:
                lang_code = "en"

            # 2. Basic Format Rules (Always English)
            if not re.match(r'^([A-Z]|[0-9])', linea): 
                line_errors.append("❌ **Format**: Must start with an Uppercase letter or a Number.")
            if "  " in linea:
                line_errors.append("⚠️ **Format**: Double spaces detected.")

            # 3. Deep Spelling & Grammar Check
            try:
                tool = get_tool(lang_code)
                # Revisamos la línea
                matches = tool.check(linea)
                for m in matches:
                    # Filtramos reglas que no queremos (como la del punto final o mayúsculas en títulos)
                    if m.ruleId not in ['UPPERCASE_SENTENCE_START', 'LC_AFTER_PERIOD', 'WHITESPACE_RULE', 'EN_COMPOUNDS']:
                        
                        # Creamos un mensaje amigable en inglés
                        rule_desc = "Spelling/Grammar"
                        if m.category == 'TYPOS':
                            rule_desc = "Spelling mistake"
                        
                        # Mostramos el error específico
                        sugg = f" -> Suggested: **{', '.join(m.replacements[:2])}**" if m.replacements else ""
                        line_errors.append(f"⚠️ **({lang_code.upper()})** {rule_desc}: '{linea[m.offset:m.offset+m.errorLength]}' {m.message}{sugg}")
            except:
                pass

            # 4. Display
            if line_errors:
                error_count += 1
                st.markdown(f"**Line {i}:** {linea}")
                for e in line_errors:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{e}")
                st.write("---")
            
            progress_bar.progress(i / total)
        
        st.success(f"🎉 Audit Complete! Found issues in {error_count} lines.")
        gc.collect()
    else:
        st.warning("Please paste text first.")
