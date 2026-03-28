import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA E IDENTIDAD VISUAL
st.set_page_config(page_title="Faria Global Auditor", page_icon="🌎", layout="wide")

# CSS para botones horizontales, alertas de colores y diseño Faria
st.markdown("""
    <style>
    div.stButton > button { width: 100%; border-radius: 8px; height: 3.5em; font-weight: bold; }
    .stTextArea textarea { border-radius: 10px; }
    .translation-box { background-color: #f0f2f6; border-left: 5px solid #1a237e; padding: 12px; margin: 10px 0; font-style: italic; border-radius: 0 8px 8px 0; }
    .highlight { background-color: #fff3cd; font-weight: bold; color: #d9534f; text-decoration: underline; padding: 0 2px; }
    /* Semaforización Smart Triage */
    .critico { background-color: #ffdde1; border-left: 5px solid #ff4b4b; padding: 10px; color: #900; margin-bottom: 5px; }
    .advertencia { background-color: #fff4e0; border-left: 5px solid #ffa500; padding: 10px; color: #856404; margin-bottom: 5px; }
    .informativo { background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 10px; color: #0c5460; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE APOYO (EL MOTOR) ---

def normalize_text(text):
    return unicodedata.normalize('NFC', text)

def translate_to_english(text, source_lang='auto'):
    if not text or len(text.strip()) < 2: return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl=en&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5).json()
        return res[0][0][0]
    except: return "[Translation N/A]"

def highlight_errors(text, words):
    text = normalize_text(text)
    for word in sorted(set(words), key=len, reverse=True):
        if len(word.strip()) <= 1: continue
        norm_word = normalize_text(word.strip())
        text = re.sub(rf"\b({re.escape(norm_word)})\b", r"<span class='highlight'>\1</span>", text)
    return text

def check_bloom_verb(line, lang):
    """Valida que la línea empiece con infinitivo (Taxonomía de Bloom)"""
    if not line: return True
    first_word = line.split()[0].strip(',.;').lower()
    # Ejemplos de terminaciones de infinitivo
    infinitives = {
        'es': r'.*(ar|er|ir)$',
        'fr': r'.*(er|ir|re)$',
        'en': r'^[a-z]+' # En inglés es más complejo, pero buscamos verbos de acción
    }
    if lang in ['es', 'fr']:
        return re.match(infinitives[lang], first_word) is not None
    return True

# --- NAVEGACIÓN (SESSION STATE) ---
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

def set_page(page_name):
    st.session_state.page = page_name

# 2. HEADER Y BOTONES (5 HORIZONTALES)
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=250) # Logo Faria
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("</div>", unsafe_allow_html=True)

st.title("Global Standards Auditor")
st.write("---")

# Fila limpia de 5 idiomas
col1, col2, col3, col4, col5 = st.columns(5)
with col1: 
    if st.button("🇬🇧 English"): set_page('English')
with col2: 
    if st.button("🇪🇸 Spanish"): set_page('Spanish')
with col3: 
    if st.button("🇫🇷 French"): set_page('French')
with col4: 
    if st.button("🇦🇪 Arabic"): set_page('Arabic')
with col5: 
    if st.button("🌎 Mixed"): set_page('Mixed')

# 3. CONTENIDO DINÁMICO
if st.session_state.page == 'Home':
    st.subheader("Welcome to the Global Audit System")
    st.info("Select a specialized auditor above or use the sidebar to begin your data scrub.")

else:
    # Botón de regreso universal
    if st.button("⬅️ Back to Home"):
        set_page('Home')
        st.rerun()

    st.header(f"Auditing: {st.session_state.page} Standards")
    texto_raw = st.text_area("Paste standards here:", height=300)

    if texto_raw:
        lineas_raw = texto_raw.split('\n')
        lineas_limpias = [l.strip() for l in lineas_raw if l.strip()]
        st.write(f"**Line Count:** {len(lineas_limpias)} / 1000")

        if st.button(f"🚀 Run {st.session_state.page} Audit"):
            texto_norm = normalize_text(texto_raw)
            lineas = [l.strip() for l in texto_norm.split('\n') if l.strip()]

            for i, linea in enumerate(lineas, 1):
                linea_lower = linea.lower()
                
                # REGLA 1: HIDE DETAILS (Ignorar)
                if "hide details" in linea_lower: continue

                # REGLA 2: SHOW DETAILS (RECUADRO AZUL - SMART TRIAGE)
                show_detected = False
                if "show details" in linea_lower:
                    st.markdown(f"<div class='informativo'>Line {i} 🔵 <b>Informativo:</b> 'Show details' detected. Verify integrity of hidden data.</div>", unsafe_allow_html=True)
                    show_detected = True

                alertas = []
                to_highlight = []

                # REGLA 3: Bloom Taxonomy & Paralelismo (Verbo Infinitivo)
                current_lang = 'fr' if st.session_state.page == 'French' else ('es' if st.session_state.page == 'Spanish' else 'en')
                if not check_bloom_verb(linea, current_lang) and not show_detected:
                    alertas.append(f"<div class='critico'>🔴 <b>Critical:</b> Verb is not in infinitive or lacks pedagogical consistency.</div>")

                # REGLA 4: API Audit (Con traducciones al inglés)
                try:
                    lang_code = 'fr' if st.session_state.page == 'French' else ('es' if st.session_state.page == 'Spanish' else 'en')
                    res = requests.post('https://api.languagetool.org/v2/check', data={'text': linea, 'language': lang_code}).json()
                    
                    for m in res.get('matches', []):
                        # Ignorar puntuación francesa de espacios
                        if any(x in m['rule']['id'] for x in ["FRENCH_WHITESPACE", "FR_PUNCTUATION"]): continue
                        
                        bad = normalize_text(linea[m['offset']:m['offset']+m['length']])
                        if bad.lower() in ["show", "details", "show details"] or len(bad) <= 1: continue
                        
                        to_highlight.append(bad)
                        
                        # Traducción "Al vuelo" de mensajes comunes
                        msg = m['message'].lower()
                        msg_en = "Grammar/Spelling issue"
                        if "accord" in msg or "concordancia" in msg: msg_en = "Agreement issue"
                        elif "orthographe" in msg or "ortografía" in msg: msg_en = "Spelling error"
                        
                        sug = f" (Try: <b>{m['replacements'][0]['value']}</b>)" if m['replacements'] else ""
                        alertas.append(f"<div class='advertencia'>🟡 <b>{msg_en}:</b> Issue in '{bad}'. {sug}</div>")
                except: pass

                # RENDERIZADO FINAL
                if alertas:
                    with st.expander(f"Line {i} ⚠️ Issues Found", expanded=True):
                        st.markdown(f"<div>{highlight_errors(linea, to_highlight)}</div>", unsafe_allow_html=True)
                        # Traducción automática en tiempo real para el equipo
                        if current_lang != 'en':
                            st.markdown(f"<div class='translation-box'><b>English Context:</b> {translate_to_english(linea, current_lang)}</div>", unsafe_allow_html=True)
                        for a in alertas: st.markdown(a, unsafe_allow_html=True)
                elif not show_detected:
                    st.success(f"Line {i} ✅ Perfect")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group | 2026")
