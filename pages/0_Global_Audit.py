import streamlit as st
import requests
import re
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Global Mixed Auditor", page_icon="🌍", layout="centered")

# --- CSS CORPORATIVO FARIA (FUCSIA) ---
st.markdown("""
    <style>
    /* Botón Fucsia */
    .stButton>button { 
        width: 100%; border-radius: 12px; background-color: #e91e63; 
        color: white; font-weight: bold; height: 3em; border: none;
    }
    .stButton>button:hover { background-color: #d81b60; color: white; }
    
    /* Barra de Progreso Fucsia */
    .stProgress > div > div > div > div { background-color: #e91e63; }
    
    /* Estilos de Cajas */
    .translation-box { 
        background-color: #f8f9fa; border-left: 5px solid #e91e63; 
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
    # Ordenar por longitud para no romper etiquetas HTML anidadas
    for word in sorted(set(words), key=len, reverse=True):
        if word and len(word.strip()) > 0:
            highlighted = re.sub(f"({re.escape(word)})", r"<span class='highlight'>\1</span>", highlighted)
    return highlighted

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try: 
    st.image("logo.jpg", width=250)
except: 
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Global Mixed Standards Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# 3. INPUT Y CONTADOR (2500 LÍNEAS)
texto_raw = st.text_area("Paste mixed standards here:", height=350, placeholder="Supports Spanish, French, Arabic, Turkish, English...")

if texto_raw:
    # Normalización para manejar caracteres como la 'ñ' correctamente
    texto_raw = unicodedata.normalize('NFC', texto_raw)
    lineas_reales = [l for l in texto_raw.split('\n') if l.strip()]
    total_lines = len(lineas_reales)
    st.markdown(f"**Total Line Count:** {total_lines} / 2500")
    if total_lines > 2500:
        st.error("⚠️ **Warning:** Document exceeds the 2,500-line limit.")
    st.write("---")

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

            # --- FILTRO 1: BOTONES DE BASE DE DATOS (Ignorar auditoría) ---
            if "hide details" in linea_lower:
                continue
            
            if "show details" in linea_lower:
                st.markdown(f"<div class='db-info-box'>Line {i} ℹ️ <b>'Show details' detected:</b> Verify hidden database content.</div>", unsafe_allow_html=True)
                continue

            # --- FILTRO 2: CORRECCIÓN PREVENTIVA (Caso 'manana') ---
            # Si detectamos 'manana' como palabra completa, la tratamos como 'mañana'
            linea_audit = re.sub(r'\bmanana\b', 'mañana', linea, flags=re.IGNORECASE)

            alertas = []
            to_highlight = []

            # --- AUDITORÍA EXTERNA (LanguageTool) ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', 
                                    data={'text': linea_audit, 'language': 'auto'}, timeout=8).json()
                
                for m in res.get('matches', []):
                    # Extraer la palabra con error del texto original
                    bad = linea[m['offset']:m['offset']+m['length']]
                    
                    # Evitar errores por palabras de sistema o duplicados
                    if bad.lower() in ["show", "details", "hide"] or bad in to_highlight:
                        continue
                    
                    # Filtro de sugerencia idéntica (Evita errores como de -> De)
                    if m['replacements']:
                        best_sug = m['replacements'][0]['value']
                        if best_sug.strip() == bad.strip():
                            continue
                        
                        sug_text = f" (Try: **{best_sug}**)"
                    else:
                        sug_text = ""

                    to_highlight.append(bad)
                    alertas.append(f"❌ **Grammar/Spelling:** Issue in '{bad}'{sug_text}")
            except:
                pass

            # --- RENDERIZADO DE RESULTADOS ---
            if alertas:
                with st.expander(f"Line {i} ⚠️ Issues found", expanded=True):
                    # Mostramos el texto original con resaltado
                    linea_html = highlight_errors(linea, to_highlight)
                    st.markdown(f"<div style='background: white; padding: 15px; border: 1px solid #ddd; border-radius: 8px;'>{linea_html}</div>", unsafe_allow_html=True)
                    
                    # Traducción para contexto en inglés
                    contexto = translate_to_english(linea)
                    st.markdown(f"<div class='translation-box'><b>English Context:</b> {contexto}</div>", unsafe_allow_html=True)
                    
                    for a in alertas:
                        st.write(a)
            else:
                st.success(f"Line {i} ✅ Perfect")

        status_text.text("Global Audit complete!")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
