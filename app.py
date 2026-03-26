import streamlit as st
import language_tool_python
import re
from langdetect import detect, DetectorFactory
import gc

# Estabilidad para la detección
DetectorFactory.seed = 0

st.set_page_config(page_title="Faria Global QA Auditor", page_icon="🛡️")

# --- Motor Multilingüe Inteligente ---
@st.cache_resource
def get_tool(lang):
    # Soporte para los idiomas principales de Faria
    mapping = {
        'en': 'en-US', 
        'es': 'es', 
        'fr': 'fr', 
        'de': 'de', 
        'it': 'it', 
        'pt': 'pt',
        'ca': 'ca-ES'
    }
    target_lang = mapping.get(lang, 'en-US')
    try:
        # Cargamos el idioma original para que NO ignore los typos
        return language_tool_python.LanguageTool(target_lang)
    except:
        return language_tool_python.LanguageTool('en-US')

# --- Header ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.jpg", width=250)
    except:
        st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>FARIA EDUCATION GROUP</h2>", unsafe_allow_html=True)

st.write("---")

# --- Input ---
texto_input = st.text_area("Paste your global standards here (Max 1,000 lines):", height=250)

if st.button("🚀 Run Global Audit"):
    if texto_input:
        lineas = [l.strip() for l in texto_input.strip().split('\n') if l.strip()]
        total = len(lineas)
        
        if total > 1000:
            st.error(f"⚠️ Batch too large! Max 1,000 lines per session.")
        else:
            progress_bar = st.progress(0)
            error_count = 0

            st.subheader("Audit Findings:")

            for i, linea in enumerate(lineas, 1):
                line_errors = []
                
                # 1. Identificar el idioma de la línea
                try:
                    lang_code = detect(linea)
                except:
                    lang_code = "en"

                # 2. Reglas de Formato (Alertas siempre en Inglés)
                if not re.match(r'^([A-Z]|[0-9])', linea): 
                    line_errors.append("❌ **Format**: Must start with an Uppercase letter or a Number.")
                
                if "  " in linea:
                    line_errors.append("⚠️ **Format**: Double spaces detected.")

                # 3. Ortografía y Gramática (Detección Nativa + Traducción de Alerta)
                try:
                    tool = get_tool(lang_code)
                    matches = tool.check(linea)
                    for m in matches:
                        # Filtramos reglas irrelevantes o duplicadas
                        if m.ruleId not in ['UPPERCASE_SENTENCE_START', 'LC_AFTER_PERIOD', 'WHITESPACE_RULE', 'MORFOLOGIK_RULE_EN_US']:
                            
                            # Traducimos la categoría al inglés para el reporte
                            category = "Grammar/Style issue"
                            if m.category == 'TYPOS' or any(word in m.message.lower() for word in ['ortografía', 'spelling', 'faute', 'rechtschreibung']):
                                category = "Spelling mistake"
                            
                            # Sugerencias si existen
                            sugg = f" (Suggested: {', '.join(m.replacements[:2])})" if m.replacements else ""
                            
                            # Alerta final: Idioma detectado + Categoría en Inglés + Sugerencia
                            line_errors.append(f"⚠️ **({lang_code.upper()})** {category}: {m.message if len(m.message) < 100 else 'Check spelling'}{sugg}")
                except:
                    pass

                # 4. Mostrar resultados (Vista Abierta)
                if line_errors:
                    error_count += 1
                    st.markdown(f"**Line {i}:** {linea}")
                    for e in line_errors:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{e}")
                    st.write("---")
                
                progress_bar.progress(i / total)
            
            st.success(f"🎉 Audit finished. Issues found in {error_count} lines.")
            gc.collect() # Limpieza de memoria para evitar el error de "Resource Limits"
    else:
        st.warning("Please paste some text first.")
