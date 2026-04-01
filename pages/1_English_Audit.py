import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="English Standards Auditor", page_icon="🇺🇸", layout="centered")

# --- CSS PERSONALIZADO (Barra de Progreso y Botón Morado) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3em;
        background-color: #4a148c; color: white; font-weight: bold; border: none;
    }
    .stButton>button:hover { background-color: #6a1b9a; color: white; }
    .stProgress > div > div > div > div { background-color: #4a148c; }
    .highlight {
        background-color: #fff3cd; font-weight: bold; color: #d9534f;
        text-decoration: underline; padding: 0 2px;
    }
    .complexity-badge {
        background-color: #ff4b4b; color: white; padding: 8px 12px;
        border-radius: 8px; font-weight: bold; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE RESALTADO (Parche anti-letras sueltas) ---
def highlight_errors(text, words):
    highlighted = text
    for word in sorted(set(words), key=len, reverse=True):
        if word and len(word.strip()) > 0:
            clean_word = re.escape(word.strip())
            pattern = rf"(?i)\b{clean_word}\b"
            if len(word) <= 2 or "." in word:
                highlighted = highlighted.replace(word, f"<span class='highlight'>{word}</span>", 1)
            else:
                highlighted = re.sub(pattern, rf"<span class='highlight'>{word}</span>", highlighted)
    return highlighted

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=250)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>English Standards Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. DIALECT SWITCH
dialect = st.radio("Select Regional Standard:", ["US (American English)", "UK (British English)"], horizontal=True)
st.info(f"Targeting: **{dialect}** rules and spelling conventions.")

# 4. INPUT Y CONTADOR POR LÍNEA
texto_input = st.text_area("Paste English standards here (one per line):", height=300, placeholder="")

if texto_input:
    lineas_reales = [l for l in texto_input.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    st.markdown(f"**Line Count:** {total_lines} / 2500")
    if total_lines > 2500:
        st.error("⚠️ **Warning:** Document exceeds the 2,500-line limit.")
    st.write("---")

# 5. PROCESAMIENTO
if st.button("🚀 Run English Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        texto_norm = unicodedata.normalize('NFC', texto_input)
        lineas = [l.strip() for l in texto_norm.split('\n') if l.strip()]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, linea in enumerate(lineas, 1):
            progress_bar.progress(i / len(lineas))
            status_text.text(f"Auditing line {i} of {len(lineas)}...")
            
            if linea.lower().strip() == "hide details": continue
            if "show details" in linea.lower():
                st.info(f"Line {i} ℹ️ **'Show details' detected.**")
                continue

            alertas = []
            to_highlight = []
            linea_audit = linea

            # --- REGLA: Símbolos de Sublime (Validación y Limpieza) ---
            sublime_tags = ['{{', '%%', '??', '$$', '<<', '##', '!!', '[[', '@@', '&&', '<br/>', '**']
            
            for tag in sublime_tags:
                if tag in linea:
                    double_tag = tag + tag[0] if len(tag) < 3 else tag
                    if not linea.startswith(tag) or (len(tag) == 2 and linea.startswith(double_tag)):
                        alertas.append(f"⚠️ **Format:** Symbol '{tag}' must be a PAIR at the START of the line.")
                    linea_audit = linea_audit.replace(tag, "")

            # --- REGLA: Doble Espacio ---
            if "  " in linea_audit:
                alertas.append("❌ **Spacing:** Double space detected.")

            # --- REGLA 1: Dialecto (Manual checks) ---
            if "US" in dialect:
                if re.search(r'\b\w+ise\b', linea_audit): 
                    alertas.append("⚠️ **Dialect:** Use '-ize' for US English.")
                if re.search(r'\b\w+our\b', linea_audit):
                    alertas.append("⚠️ **Dialect:** Use '-or' for US English.")
            else: # UK
                if "color" in linea_audit.lower() or "behavior" in linea_audit.lower():
                    alertas.append("⚠️ **Dialect:** US spelling detected. Use '-our' for UK.")

            # --- API LANGUAGETOOL (Con bloqueo de Oxford Spelling) ---
            lang_code = "en-US" if "US" in dialect else "en-GB"
            try:
                # Deshabilitamos las reglas de Oxford para que acepte -ise en UK
                payload = {
                    'text': linea_audit.strip(), 
                    'language': lang_code,
                    'disabledRules': 'MCI_OXFORD_SPELLING_Z_NOT_S,OXFORD_SPELLING_Z_NOT_S'
                }
                res = requests.post('https://api.languagetool.org/v2/check', data=payload).json()
                
                for m in res.get('matches', []):
                    # Filtro de seguridad por si la API ignora el payload
                    if 'OXFORD' in m['rule']['id'] or 'Z_NOT_S' in m['rule']['id']:
                        continue
                        
                    bad = linea_audit[m['offset']:m['offset']+m['length']]
                    if bad.strip() and bad.lower() not in ["show", "details"]:
                        to_highlight.append(bad)
                        alertas.append(f"❌ **{m['rule']['category']['name']}:** {m['message']}")
            except: pass

            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    st.markdown(f"<div>{highlight_errors(linea, to_highlight)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            else:
                st.success(f"Line {i} ✅ Perfect")

        status_text.text("Audit complete!")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
