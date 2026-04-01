import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Global Languages Auditor", page_icon="🌍", layout="centered")

# --- CSS PERSONALIZADO (MORADO FARIA) ---
st.markdown("""
    <style>
    .stButton>button { 
        width: 100%; border-radius: 12px; background-color: #4a148c; 
        color: white; font-weight: bold; height: 3em; border: none;
    }
    .stButton>button:hover { background-color: #6a1b9a; color: white; }
    .stProgress > div > div > div > div { background-color: #4a148c; }
    .translation-box { 
        background-color: #f8f9fa; border-left: 5px solid #4a148c; 
        padding: 12px; margin: 10px 0; font-style: italic; color: #333;
    }
    .db-info-box { 
        background-color: #e3f2fd; border-left: 5px solid #2196f3; 
        padding: 15px; color: #0c5460; margin: 10px 0; border-radius: 4px; font-weight: 500; 
    }
    .highlight { 
        background-color: #fff3cd; font-weight: bold; color: #d9534f; 
        text-decoration: underline; padding: 0 2px; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE SOPORTE ---
def translate_to_english(text):
    if not text or len(text.strip()) < 2: return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5).json()
        return res[0][0][0]
    except: return "[Translation N/A]"

def highlight_errors(text, words):
    highlighted = text
    # Ordenar por longitud descendente para evitar conflictos de reemplazo
    for word in sorted(set(words), key=len, reverse=True):
        if not word or len(word.strip()) == 0: continue
        
        clean_word = re.escape(word.strip())
        
        # Lógica de parche: Evita el "efecto dálmata" en letras sueltas o numeraciones
        if len(word.strip()) <= 2 or "." in word:
            pattern = rf"(?i)\b{clean_word}\b"
            if re.search(pattern, highlighted):
                highlighted = re.sub(pattern, rf"<span class='highlight'>{word}</span>", highlighted, count=1)
            else:
                highlighted = highlighted.replace(word, f"<span class='highlight'>{word}</span>", 1)
        else:
            highlighted = re.sub(f"({clean_word})", r"<span class='highlight'>\1</span>", highlighted, flags=re.IGNORECASE)
    return highlighted

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try: 
    st.image("logo.jpg", width=250)
except: 
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Global Languages Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. INPUT Y CONTADOR (2500 LÍNEAS)
texto_raw = st.text_area("Paste your standards here:", height=350, placeholder="Supports different languages...")

if texto_raw:
    texto_raw = unicodedata.normalize('NFC', texto_raw)
    lineas_reales = [l for l in texto_raw.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    st.markdown(f"**Total Line Count:** {total_lines} / 2500")
    if total_lines > 2500:
        st.error("⚠️ **Warning:** Document exceeds the 2,500-line limit.")

# 4. BOTÓN Y PROCESAMIENTO
if st.button("🚀 Run Global Audit"):
    if not texto_raw.strip():
        st.warning("Please paste some text first.")
    else:
        lineas = [l.strip() for l in texto_raw.split('\n') if l.strip()]
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, linea in enumerate(lineas, 1):
            progress_bar.progress(i / len(lineas))
            status_text.text(f"Auditing line {i} of {len(lineas)}...")
            
            linea_lower = linea.lower()
            if "hide details" in linea_lower: continue
            if "show details" in linea_lower:
                st.markdown(f"<div class='db-info-box'>Line {i} ℹ️ <b>'Show details' detected:</b> Verify database content.</div>", unsafe_allow_html=True)
                continue

            alertas = []
            to_highlight = []
            linea_audit = linea

            # --- REGLA: SÍMBOLOS DE SUBLIME (Validación de posición y pares) ---
            tags = ['{{', '%%', '??', '$$', '<<', '##', '!!', '[[', '@@', '&&', '<br/>', '**']
            for tag in tags:
                if tag in linea:
                    # Comprobar si es un par exacto al inicio (evita $$$ o tag en medio)
                    double_tag = tag + tag[0] if len(tag) == 2 else tag
                    if not linea.startswith(tag) or (len(tag) == 2 and linea.startswith(double_tag)):
                        alertas.append(f"⚠️ **Format:** Symbol '{tag}' must be a PAIR at the START of the line.")
                    # Limpiar el tag para que no interfiera con la gramática
                    linea_audit = linea_audit.replace(tag, "")

            # --- REGLA: DOBLE ESPACIO ---
            if "  " in linea_audit:
                alertas.append("❌ **Spacing:** Double space detected within the sentence.")

            # --- FILTRO MAÑANA ---
            linea_audit = re.sub(r'\bmanana\b', 'mañana', linea_audit, flags=re.IGNORECASE)

            # --- API LANGUAGETOOL ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', 
                                    data={'text': linea_audit, 'language': 'auto'}, timeout=8).json()
                
                for m in res.get('matches', []):
                    bad = linea_audit[m['offset']:m['offset']+m['length']]
                    if bad.lower() in ["show", "details", "hide"]: continue
                    if m['replacements']:
                        best_sug = m['replacements'][0]['value']
                        if best_sug.strip() == bad.strip(): continue
                        sug_text = f" (Try: **{best_sug}**)"
                    else:
                        sug_text = ""

                    to_highlight.append(bad)
                    alertas.append(f"❌ **Grammar/Spelling:** Issue in '{bad}'{sug_text}")
            except:
                pass

            # --- RENDERIZADO ---
            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    linea_html = highlight_errors(linea, to_highlight)
                    st.markdown(f"<div style='background: white; padding: 15px; border: 1px solid #ddd; border-radius: 8px;'>{linea_html}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='translation-box'><b>English Context:</b> {translate_to_english(linea)}</div>", unsafe_allow_html=True)
                    for a in alertas: st.write(a)
            else:
                st.success(f"Line {i} ✅ Perfect")

        status_text.text("Global Audit complete!")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
