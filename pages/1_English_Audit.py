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
st.markdown("<p style='color: #666;'>Strict Format: Caps/Numbers, No Extra Spaces, Broken Words, Multi-Dialect.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.write("---")

# 3. ENTRADA DE TEXTO
texto_input = st.text_area("Paste English standards here (one per line):", height=300, placeholder="e.g.\n1. First standard.\n2.1. Incomplete- standard.")

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
            
            # --- CONTADOR DE PALABRAS ---
            words = linea.split()
            word_count = len(words)
            
            # --- REGLA 1 y 2: Formato de Inicio (Mayúscula o Numero. o Numero.Numero.) ---
            patron_inicio = r'^([A-Z]|\d+\.(\d+\.)?)'
            if not re.match(patron_inicio, linea):
                errores_linea.append({
                    'message': "Does not start with a capital letter or valid number format (e.g., '1.' or '2.1.').",
                    'suggestions': [{"value": f"Fix start: {linea[:5]}..."}]
                })

            # --- REGLA 3: Espacios Extra ---
            if re.search(r' {2,}', linea):
                linea_corregida = re.sub(r' {2,}', ' ', linea)
                errores_linea.append({
                    'message': "Contains extra spaces between words.",
                    'suggestions': [{"value": linea_corregida}]
                })

            # --- NUEVA REGLA: Palabras cortadas (ej. "word-") ---
            # Busca cualquier palabra que termine en guion o guion bajo
            broken_words = re.findall(r'\b\w+[-_]\b|\b\w+[-_]\s', linea)
            if broken_words:
                errores_linea.append({
                    'message': f"Detected potentially broken or hyphenated words: {', '.join(broken_words)}",
                    'suggestions': [{"value": "Remove the trailing hyphen or join the word fragments."}]
                })

            # --- REGLA 4 y 5: Ortografía y Puntuación (Múltiples variantes) ---
            try:
                res = requests.post('https://api.languagetool.org/v2/check', 
                                    data={'text': linea, 
                                          'language': 'en',
                                          'motherTag': 'en-US,en-GB,en-AU'
                                         }).json()
                
                for m in res.get('matches', []):
                    clean_message = m['message'].replace("Check for", "Verify").replace
