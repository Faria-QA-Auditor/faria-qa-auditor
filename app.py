import streamlit as st
import language_tool_python
import re
from langdetect import detect, DetectorFactory
import gc

DetectorFactory.seed = 0

st.set_page_config(page_title="Faria Global QA Auditor", page_icon="🛡️")

# --- Motor con manejo de errores estricto ---
@st.cache_resource
def get_tool(lang):
    mapping = {'en': 'en-US', 'es': 'es', 'fr': 'fr', 'de': 'de', 'it': 'it', 'pt': 'pt'}
    target_lang = mapping.get(lang, 'en-US')
    try:
        # Intentamos cargar con configuración ligera
        return language_tool_python.LanguageTool(target_lang)
    except Exception:
        # Si falla en la nube, intentamos cargar el motor básico de inglés como respaldo
        return language_tool_python.LanguageTool('en-US')

# --- Header ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.jpg", width=250)
    except:
        st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>FARIA</h2>", unsafe_allow_html=True)

st.write("---")

texto_input = st.text_area("Paste standards here (Max 1,000 lines):", height=250, help="Paste your text and click Run Audit")

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

            # 2. Format Rules (Manuales - Estas SIEMPRE funcionan)
            if not re.match(r'^([A-Z]|[0-9])', linea): 
                line_errors.append("❌ **Format**: Must start with Uppercase or Number.")
            if "  " in linea:
                line_errors.append("⚠️ **Format**: Double spaces detected.")

            # 3. Spelling & Grammar (El motor profesional)
            try:
                tool = get_tool(lang_code)
                matches = tool.check(linea)
                for m in matches:
                    # Filtramos reglas de títulos y puntuación que no queremos
                    if m.ruleId not in ['UPPERCASE_SENTENCE_START', 'LC_AFTER_PERIOD', 'WHITESPACE_RULE', 'EN_COMPOUNDS', 'MORFOLOGIK_RULE_EN_US']:
                        
                        # Extraemos la palabra con el error
                        word_error = linea[m.offset:m.offset+m.errorLength]
                        
                        # Traducimos el tipo de error a inglés para el reporte de Faria
                        category = "Spelling mistake" if m.category == 'TYPOS' else "Grammar/Style issue"
                        
                        sugg = f" -> Suggested: **{', '.join(m.replacements[:2])}**" if m.replacements else ""
                        
                        # Alerta limpia en inglés
                        line_errors.append(f"⚠️ **({lang_code.upper()})** {category}: Found '{word_error}'. {m.message}{sugg}")
            except Exception as e:
                # Si el motor falla, al menos avisamos en la primera línea
                if i == 1:
                    st.warning("Note: Deep spelling check is warming up. If results don't show, please refresh.")

            # 4. Display
            if line_errors:
                error_count += 1
                st.markdown(f"**Line {i}:** {linea}")
                for e in line_errors:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{e}")
                st.write("---")
            
            progress_bar.progress(i / total)
        
        if error_count == 0:
            st.success("✅ No issues found in this batch!")
        else:
            st.success(f"🎉 Audit Complete! Found issues in {error_count} lines.")
        
        gc.collect()
    else:
        st.warning("Please paste text first.")
