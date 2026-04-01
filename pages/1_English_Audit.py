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
            # Busca límites de palabra para evitar resaltar letras dentro de otras palabras
            pattern = rf"(?i)\b{clean_word}\b"
            highlighted = re.sub(pattern, rf"<span class='highlight'>{word}</span>", highlighted, count=1)
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
        p_errors = 0 
        
        for i, linea in enumerate(lineas, 1):
            progress_bar.progress(i / len(lineas))
            status_text.text(f"Auditing line {i} of {len(lineas)}...")
            
            if linea.lower().strip() == "hide details": continue
            if "show details" in linea.lower():
                st.info(f"Line {i} ℹ️ **'Show details' detected.**")
                continue

            alertas = []
            to_highlight = []

            # --- REGLA: Símbolos de Sublime (Excepción al inicio) ---
            sublime_tags = [r'\{\{', r'%%', r'\?\?', r'\$\$', r'<<', r'##', r'!!', r'\[\[', r'@@', r'&&', r'<br/>', r'\*\*']
            linea_audit = linea
            
            for tag in sublime_tags:
                # Si el tag está al inicio pero hay más de 2 (ej: $$$) o está en otra posición -> Alerta
                if re.search(tag, linea):
                    # Validar si es un par exacto al inicio
                    if not re.match(rf"^{tag}(?![^{tag[0]}]*{tag[0]})", linea):
                         alertas.append(f"⚠️ **Format:** Symbol '{tag.replace('\\','')}' must be a pair at the START of the line.")
                    # Limpiar para la API de gramática
                    linea_audit = re.sub(tag, '', linea_audit)

            # --- REGLA: Doble Espacio ---
            if "  " in linea_audit:
                alertas.append("❌ **Spacing:** Double space detected within the sentence.")

            # --- REGLA 1: Dialecto (Oxford Friendly) ---
            if "US" in dialect:
                if re.search(r'\b\w+ise\b', linea_audit): 
                    alertas.append("⚠️ **Dialect:** Detected '-ise' (UK). Use '-ize' for US.")
                if re.search(r'\b\w+our\b', linea_audit):
                    alertas.append("⚠️ **Dialect:** Detected '-our' (UK). Use '-or' for US.")
            else: # UK
                if re.search(r'\b\w+our\b', linea_audit) is None and any(word in linea_audit.lower() for word in ["color", "behavior", "flavor"]):
                    alertas.append("⚠️ **Dialect:** US spelling detected. Use '-our' for UK.")
                # Flexibilidad -ize / -ise: No marcamos error manual, dejamos que LanguageTool decida.

            # --- REGLA 2: Tono Académico ---
            forbidden = {"get": "acquire", "thing": "element", "stuff": "material"}
            for word, sug in forbidden.items():
                if re.search(rf'\b{word}\b', linea_audit.lower()):
                    alertas.append(f"⚠️ **Tone:** Use **{sug}** instead of '{word}'.")
                    to_highlight.append(word)

            # --- API LANGUAGETOOL ---
            lang_code = "en-US" if "US" in dialect else "en-GB"
            try:
                res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea_audit, 'language': lang_code}).json()
                for m in res.get('matches', []):
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
