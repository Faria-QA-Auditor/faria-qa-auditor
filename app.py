import streamlit as st
import language_tool_python
import re
import pandas as pd
from langdetect import detect, DetectorFactory

# Stability for language detection
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
        st.image("logo.jpg", width=300)
    except:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>FARIA</h1>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center;'>Global Standards QA Auditor</h3>", unsafe_allow_html=True)
st.write("---")

# --- Input Section ---
texto_input = st.text_area("Paste your standards here (Max 1,000 lines):", height=300)

if st.button("🚀 Run Audit"):
    if texto_input:
        lineas = [l.strip() for l in texto_input.strip().split('\n') if l.strip()]
        total = len(lineas)
        
        if total > 1000:
            st.error(f"⚠️ **Batch too large!** Please process a maximum of 1,000 lines (Current: {total}).")
        else:
            progress_bar = st.progress(0)
            status_info = st.empty()
            
            ok_count = 0
            error_count = 0
            report_results = [] # <--- Aquí guardaremos todo para el Excel

            for i, linea in enumerate(lineas, 1):
                line_errors = []
                
                # 1. Language Detection
                try:
                    lang_code = detect(linea)
                    actual_lang = 'ca-ES' if lang_code == 'ca' else lang_code
                except:
                    lang_code = "en"
                    actual_lang = 'en-US'

                # 2. Faria Format Rules
                if not re.match(r'^([A-Z]|[0-9])', linea): 
                    line_errors.append("❌ Must start with Uppercase or Number.")
                if not linea.endswith('.'): 
                    line_errors.append("❌ Missing period at the end.")
                if "  " in linea:
                    line_errors.append("⚠️ Double spaces detected.")

                # 3. Grammar & Typos
                try:
                    tool = get_tool(actual_lang)
                    matches = tool.check(linea)
                    for m in matches:
                        if getattr(m, 'ruleId', '') not in ['UPPERCASE_SENTENCE_START', 'LC_AFTER_PERIOD']:
                            line_errors.append(f"⚠️ ({lang_code.upper()}) {getattr(m, 'message', 'Typo')}")
                except:
                    pass

                # 4. Results Display & Data Collection
                if not line_errors:
                    ok_count += 1
                else:
                    error_count += 1
                    # Guardamos para el reporte descargable
                    report_results.append({
                        "Line": i,
                        "Language": lang_code.upper(),
                        "Standard Text": linea,
                        "Issues Found": " | ".join(line_errors)
                    })
                    
                    with st.expander(f"Line {i}: Issues Found", expanded=False):
                        st.write(f"**Text:** {linea}")
                        for e in line_errors:
                            st.write(e)
                
                progress_bar.progress(i / total)
                status_info.text(f"Auditing line {i} of {total}...")

            status_info.empty()
            st.success(f"🎉 Audit Complete! ✅ {ok_count} Passed | ❌ {error_count} Issues found.")

            # --- NUEVO: Botón de Descarga ---
            if report_results:
                st.write("---")
                st.subheader("📊 Export Results")
                df = pd.DataFrame(report_results)
                csv = df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="📥 Download Audit Report (CSV)",
                    data=csv,
                    file_name="faria_audit_report.csv",
                    mime="text/csv",
                )
                st.info("The CSV file can be opened directly in Excel for easier tracking.")
    else:
        st.warning("Please paste some standards first.")
