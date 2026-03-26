import streamlit as st
import requests
import re

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="English QA Auditor", page_icon="🇺🇸", layout="centered")

# --- CSS PERSONALIZADO (Estilo Faria, Botones Morados) ---
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
    /* Estilo para las alertas de error (Rojo Faria) */
    .stAlert {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. HEADER
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.markdown("<h1 style='color: #4a148c;'>🇺🇸 English Standards Auditor</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #666;'>Locked to English (US, UK, AU) with strict formatting rules.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.write("---")

# 3. ENTRADA DE TEXTO
texto_input = st.text_area("Paste English standards here (one per line):", height=300, placeholder="e.g.\n2.1. Verify user credentials.\nEnsure data integrity.")

# 4. BOTÓN DE ACCIÓN
if st.button("🚀 Run Specialized Audit"):
    if not texto_input.strip():
        st.warning("⚠️ Please paste some text first.")
    else:
        # Procesar línea por línea
        lineas = [l.strip() for l in texto_input.split('\n') if l.strip()]
        
        st.subheader("Audit Results")
        st.write(f"Analyzed {len(lineas)} standards.")
        st.write("---")

        for i, linea in enumerate(lineas, 1):
            errores_linea = []
            
            # --- REGLA 1 y 2: Formato de Inicio (Mayúscula o Numero.Numero.) ---
            # Expresión regular: ^(comienzo) ( Mayúscula O (Numero . Numero .) )
            patron_inicio = r'^([A-Z]|\d+\.\d+\.)'
            if not re.match(patron_inicio, linea):
                errores_linea.append({
                    'message': "Does not start with a capital letter or 'number.number.' format (e.g., 2.1.).",
                    'suggestions': [{"value": f"Make it '{linea[0].upper()}{linea[1:]}' or add 'X.X.' prefix."}]
                })

            # --- REGLA 3: Espacios Extra ---
            # Buscamos dos o más espacios seguidos
            if re.search(r' {2,}', linea):
                linea_corregida = re.sub(r' {2,}', ' ', linea)
                errores_linea.append({
                    'message': "Contains extra spaces between words.",
                    'suggestions': [{"value": linea_corregida}]
                })

            # --- REGLA 4 y 5: Ortografía y Punctuation (Múltiples variantes) ---
            # Llamamos a LanguageTool para el resto. Forzamos 'en' (genérico) 
            # pero le pedimos que respete las 3 variantes principales en la motherTag.
            try:
                res = requests.post('https://api.languagetool.org/v2/check', 
                                    data={'text': linea, 
                                          'language': 'en', # Idioma base
                                          'motherTag': 'en-US,en-GB,en-AU' # Acepta estas 3 variantes
                                         }).json()
                
                # Filtrar y formatear los errores de LT para que coincidan con nuestro formato
                for m in res.get('matches', []):
                    # Simplificamos los mensajes de la API para que sean claros
                    clean_message = m['message'].replace("Check for", "Verify").replace("Did you mean", "Consider using")
                    errores_linea.append({
                        'message': f"Grammar/Spelling: {clean_message}",
                        'suggestions': m['replacements'][:2] # Tomamos las primeras 2 sugerencias
                    })
            except Exception as e:
                errores_linea.append({'message': f"Error calling spellcheck API: {str(e)}", 'suggestions': []})

            # --- MOSTRAR RESULTADOS DE LA LÍNEA ---
            if not errores_linea:
                st.success(f"Line {i}: ✅ Perfect")
            else:
                with st.expander(f"Line {i}: ⚠️ {len(errores_linea)} issues found", expanded=True):
                    st.write(f"**Original:** {linea}")
                    for error in errores_linea:
                        st.error(f"- {error['message']}")
                        
                        # Mostrar sugerencias si existen
                        if error['suggestions']:
                            suggs = ", ".join([f"`{s['value']}`" for s in error['suggestions']])
                            st.info(f"💡 Suggestion: {suggs}")
                    st.write("---")

st.write("---")
st.caption("Standards & Services Team | Faria Education Group")
