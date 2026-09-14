# -*- coding: utf-8 -*-
import os
import streamlit as st
import streamlit.components.v1 as components

# Configuración de página de Streamlit a ancho completo
st.set_page_config(page_title="Gestión de Eventos Acceso - NOC", layout="wide")

# Ocultar márgenes predeterminados de Streamlit para que el HTML tome el 100% de la pantalla
st.markdown("""
    <style>
        .block-container { padding: 0rem !important; }
        iframe { width: 100% !important; border: none !important; }
    </style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE_DIR, "codigo html evento acceso.txt")

# Leer el contenido HTML original sin recortar el <head>
with open(SRC, "r", encoding="utf-8") as f:
    html_content = f.read()

# Renderizar el HTML completo con altura suficiente
components.html(html_content, height=1200, scrolling=True)
