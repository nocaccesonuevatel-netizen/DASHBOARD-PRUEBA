# -*- coding: utf-8 -*-
import os
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Gestión de Eventos Acceso - NOC", layout="wide")

# Ocultar espacios innecesarios de Streamlit
st.markdown("""
    <style>
        .block-container { padding: 0rem !important; }
        header { display: none !important; }
        footer { display: none !important; }
        iframe { width: 100% !important; border: none !important; }
    </style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE_DIR, "codigo html evento acceso.txt")

with open(SRC, "r", encoding="utf-8") as f:
    contenido_html = f.read()

# Construir un HTML5 completo inyectando Tailwind CSS y librerías necesarias
full_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestión de Eventos Acceso - NOC</title>
    
    <!-- Cargar Tailwind CSS CDN para habilitar todas las clases de diseño -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Cargar Chart.js y XLSX si las utilizas en tu dashboard -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.min.js"></script>
    
    <style>
      body {{
        background-color: #0b0e17;
        color: #ffffff;
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        margin: 0;
        padding: 1rem;
      }}
      .card {{ content-visibility: auto; contain-intrinsic-size: 220px; }}
      .select-dark:focus-visible, button:focus-visible {{ outline: 2px solid #f5b800; outline-offset: 2px; }}
    </style>
</head>
<body>
    {contenido_html}
</body>
</html>
"""

# Renderizar el HTML en Streamlit con la altura adecuada
components.html(full_html, height=1200, scrolling=True)
