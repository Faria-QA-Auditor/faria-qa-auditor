import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Arabic Auditor", page_icon="🇸🇦", layout="centered")

# --- CSS PROFESIONAL (Soporte RTL para el área de texto) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #4a148c;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ff4081;
    }
    /* Estilo para que el área de texto se vea de derecha a izquierda */
    textarea {
        direction: rtl;
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
try:
    st.image("logo.jpg", width=250)
except:
    st.title("FARIA EDUCATION GROUP")
st.markdown("<h2 style='color: #444;'>Arabic Standards Auditor</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("---")

# 3. ENTRADA DE TEXTO
texto_input = st.text_area("Paste Arabic standards here (one per line):", height=300)

# --- CONTADOR GLOBAL (SOBRE 1000 PALABRAS) ---
if texto_input:
    total_words = len(texto_input.split())
    st.markdown(f"**Word Count:** {total_words} / 1000")
    if total_words > 1000:
        st.error("⚠️ Warning: Limit exceeded.")
    st.write("---")

# 4. PROCESAMIENTO REFORZADO PARA ÁRABE
if st.button("🚀 Run Specialized Audit"):
    if not texto_input.strip():
        st.warning("Please paste some text first.")
    else:
        lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
        st.subheader("Audit Results")

        for i, linea in enumerate(lineas, 1):
            if linea.lower() == "hide details":
                continue

            errores = []
            alertas_info = []

            # REGLA: Show Details
            if "show details" in linea.lower():
                alertas_info.append("ℹ️ 'Show details' detected: Verify if text is missing.")

            # --- REGLAS DE FORMATO Y ESTRUCTURA ---
            
            # 1. Puntuación Invertida (Detectar comas occidentales)
            if "," in linea or ";" in linea:
                errores.append("Warning [Punctuation]: Found western comma (,) or semicolon (;) instead of Arabic (، / ؛).")

            # 2. Consistencia de Cifras (Mezcla de 123 con ١٢٣)
            western_nums = bool(re.search(r'[0-9]', linea))
            arabic_nums = bool(re.search(r'[٠-٩]', linea))
            if western_nums and arabic_nums:
                errores.append("Error [Format]: Mixed number systems detected (Western and Arabic-Indic). Please use only one.")

            # 3. Conector Waw (و) con espacio
            if re.search(r'\sو\s', linea) or linea.startswith('و '):
                errores.append("Error [Syntax]: Space detected after conjunction 'Waw' (و). It must be attached to the next word.")

            # --- REGLAS DE GRAMÁTICA Y ORTOGRAFÍA ---

            # 4. Tatweel (Kashida - El uso de la línea extendida ـ )
            if "ـ" in linea:
                alertas_info.append("Note [Style]: Tatweel (Kashida) detected. Consider removing it for cleaner data.")

            # 5. Ta Marbuta (ة) vs Ha (ه) al final
            # Buscamos palabras que terminen en ه pero que comúnmente requieren ة (simplificado para el script)
            if re.search(r'[^\s]ه\s|$', linea) and not re.search(r'[^\s]ة\s|$', linea):
                # Esta es una alerta sugerida, ya que depende del contexto gramatical
                alertas_info.append("Check [Orthography]: Verify if final 'Ha' (ه) should be 'Ta Marbuta' (ة).")

            # 6. Longitud de Sentencia
            if len(linea.split()) > 40:
                alertas_info.append("Note [Style]: Sentence exceeds 40 words. Consider breaking it down for pedagogical clarity.")

            # --- API LANGUAGETOOL (Detección de errores generales y traducción) ---
            try:
                payload = {'text': linea, 'language': 'ar'}
                res = requests.post('https://api.languagetool.org/v2/check', data=payload).json()
                
                for m in res.get('matches', []):
                    msg_orig = m['message'].lower()
                    
                    # Traducción al vuelo
                    if "spelling" in msg_orig or "إملاء" in msg_orig or "spell" in msg_orig:
                        final_msg = "Spelling error found (Check Hamzas or typos)."
                    elif "grammar" in msg_orig or "قواعد" in msg_orig:
                        final_msg = "Grammatical issue detected."
                    else:
                        final_msg = "Potential grammar/style issue."

                    sug = f" (Try: {m['replacements'][0]['value']})" if m['replacements'] else ""
                    errores.append(f"Grammar/Spelling: {final_msg}{sug}")
            except:
                pass

            # MOSTRAR RESULTADOS
            header = f"Line {i}"
            if not errores and not alertas_info:
                st.success(f"{header} ✅ Perfect")
            else:
                icon = "⚠️" if errores else "ℹ️"
                with st.expander(f"{header} {icon} Issues found", expanded=True):
                    # Usamos un contenedor con dirección RTL para que el texto original se lea bien
                    st.markdown(f"<div style='direction: rtl; text-align: right; border: 1px solid #eee; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>{linea}</div>", unsafe_allow_html=True)
                    for info in alertas_info: st.info(info)
                    for err in errores: st.error(f"- {err}")

st.write("---")
st.caption("Standards and Services Team | Faria Education Group")
