import streamlit as st
import re
from langdetect import detect, DetectorFactory
import gc
from textblob import TextBlob # Librería alternativa más ligera

DetectorFactory.seed = 0

st.set_page_config(page_title="Faria Global QA Auditor", page_icon="🛡️")

# --- Header ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.jpg", width=250)
    except:
        st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>FARIA EDUCATION GROUP</h2>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center;'>Global Standards Auditor</h3>", unsafe_allow_html=True)
st.write("---")

texto_input = st.text_area("Paste standards here (Global Support):", height=250)

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

            # 2. Format Rules (Mandatory)
            if not re.match(r'^([A-Z]|[0-9])', linea): 
                line_errors.append("❌ **Format**: Must start with an Uppercase letter or a Number.")
            if "  " in linea:
                line_errors.append("⚠️ **Format**: Double spaces detected.")

            # 3. Spelling Check (Alternative Method)
            # Usamos TextBlob para inglés, para otros idiomas usamos una lógica de limpieza
            blob = TextBlob(linea)
            
            # Si es inglés, TextBlob es muy bueno detectando:
            if lang_code == 'en':
                corrected = blob.correct()
                if str(blob) != str(corrected):
                    line_errors.append(f"⚠️ **(EN) Spelling**: Possible typo detected. Check your spelling.")
            
            # Para otros idiomas (FR, ES), si TextBlob no ayuda, buscamos palabras repetidas o patrones raros
            # Este es un respaldo para asegurar que al menos detecte errores de dedo básicos
            words = re.findall(r'\w+', linea.lower())
            for word in words:
                if len(word) > 3 and any(word[j] == word[j+1] == word[j+2] for j in range(len(word)-2)):
                    line_errors.append(f"⚠️ **({lang_code.upper()}) Spelling**: Repeated characters in '{word}'.")

            # 4. Display Results
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
