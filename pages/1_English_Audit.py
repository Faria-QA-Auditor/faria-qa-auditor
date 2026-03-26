import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="English QA Auditor", page_icon="🇺🇸", layout="centered")

# --- CSS PERSONALIZADO ---
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
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff4081;
        color: white;
    }
    .stAlert {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.markdown("<h1 style='color: #4a148c;'>🇺🇸 English Standards Auditor</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #666;'>Strict Format: Caps/Numbers, No Extra Spaces, Multi-Dialect English.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.write("---")

# 3. ENTRADA DE TEXTO
texto_input = st.text_area("Paste English standards here (one per line):", height=300, placeholder="e.g.\n1. First standard.\n2.1. Second standard.")

# 4. BOTÓN DE ACCIÓN
if st.button("🚀 Run Specialized Audit"):
    if not texto_input.strip():
        st.warning("⚠️ Please paste some text first.")
    else:
        lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
        
        st.subheader("Audit Results")
        st.write(f"Analyzed {len(lineas)} standards.")
        st.write("---")

        for i, linea in enumerate(lineas, 1):
            errores_linea = []
            
            # --- CONTADOR DE PALABRAS (Lógica robusta) ---
            words = linea.split()
            word_count = len(words)
            
            # --- REGLA 1 y 2: Formato de Inicio (Mayúscula o Numero. o Numero.Numero.) ---
            # Explicación del Regex:
            # ^([A-Z] -> Empieza con Mayúscula
            # | -> O
            # \d+\. -> Numero seguido de punto (ej. 1.)
            # (\d+\.)? -> Opcionalmente otro numero seguido de punto (ej. 2.1.)
            patron_inicio = r'^([A-Z]|\d+\.(\d+\.)?)'
            
            if not re.match(patron_inicio, linea):
                errores_linea.append({
                    'message': "Does not start with a capital letter or valid number format (e.g., '1.' or '2.1.').",
                    'suggestions': [{"value": f"Check start of: '{linea[:10]}...'"}]
                })

            # --- REGLA 3: Espacios Extra ---
            if re.search(r' {2,}', linea):
                linea_corregida = re.sub(r' {2,}', ' ', linea)
                errores_linea.append({
                    'message': "Contains extra spaces between words.",
                    'suggestions': [{"value": linea_corregida}]
                })

            # --- REGLA 4 y 5: Ortografía y Puntuación (Múltiples variantes) ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', 
                                    data={'text': linea, 
                                          'language': 'en',
                                          'motherTag': 'en-US,en-GB,en-AU'
                                         }).json()
                
                for m in res.get('matches', []):
                    clean_message = m['message'].replace("Check for", "Verify").replace("Did you mean", "Consider using")
                    errores_linea.append({
                        'message': f"Grammar/Spelling: {clean_message}",
                        'suggestions': m['replacements'][:2]
                    })
            except Exception as e:
                errores_linea.append({'message': f"API Error: {str(e)}", 'suggestions': []})

            # --- MOSTRAR RESULTADOS ---
            # El contador de palabras aparece ahora justo después del número de línea
            header_label = f"Line {i} | {word_count} words"
            
            if not errores_linea:
                st.success(f"{header_label} ✅ Perfect")
            else:
                with st.expander(f"{header
