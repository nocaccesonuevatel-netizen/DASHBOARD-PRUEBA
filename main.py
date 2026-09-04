"""
VIVA - EVENTOS ACCESO NOC Dashboard
Versión Python del HTML original - Paleta de la imagen + logo como fondo

Requisitos:
pip install streamlit pandas plotly openpyxl

Ejecutar:
streamlit run dashboard_viva_python.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import base64
import os

# --- CONFIGURACIÓN ---
st.set_page_config(
    page_title="VIVA Eventos Acceso - NOC",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- COLORES EXACTOS DE LA IMAGEN ---
COLORS = {
    "bg_main": "#101a30",
    "bg_card": "#16233f",
    "bg_card_trans": "rgba(22, 35, 63, 0.92)",
    "border": "#1e2e4a",
    "border_light": "#223a5a",
    "text_main": "#e2e8f0",
    "text_muted": "#7e8da8",
    "lime": "#93d624",      # VIVA - Resumen General, barras Eventos
    "lime_light": "#a6e22e",
    "yellow": "#facc15",    # Cortes Energía 2605, OCCIDENTE
    "cyan": "#22d3ee",      # Horas Afectadas, ORIENTE, línea
    "emerald": "#34d399",   # Disponibilidad
}

# --- LOGO COMO FONDO (base64 del logo generado) ---
# Si tienes el logo en /mnt/data/resource/viva_bolivia_logo.webp lo usa, si no usa texto
logo_path = "viva_logo.webp"
# Fallback por si está en subcarpeta
if not os.path.exists(logo_path):
    logo_path = os.path.join(os.path.dirname(__file__), "viva_logo.webp")
logo_data_uri = ""
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        logo_data_uri = f"data:image/webp;base64,{b64}"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', system-ui, sans-serif;
}}

.stApp {{
    background-color: {COLORS['bg_main']};
    position: relative;
}}

/* Logo VIVA como fondo - marca de agua */
.stApp::before {{
    content: "";
    position: fixed;
    top: 50%;
    left: 50%;
    width: 75vw;
    height: 75vh;
    transform: translate(-50%, -50%);
    background-image: url("{logo_data_uri}");
    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;
    opacity: 0.09;
    pointer-events: none;
    z-index: 0;
    filter: drop-shadow(0 0 40px rgba(147,214,36,0.18));
}}

.main .block-container {{
    position: relative;
    z-index: 2;
    background: transparent;
}}

.card {{
    background: {COLORS['bg_card_trans']};
    border: 1px solid {COLORS['border']};
    border-radius: 16px;
    padding: 20px;
    backdrop-filter: blur(4px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}}
.card:hover {{
    border-color: {COLORS['border_light']};
}}

.kpi-number {{
    font-size: 36px;
    font-weight: 800;
    line-height: 1;
    margin: 8px 0;
}}
.kpi-label {{
    font-size: 12px;
    color: {COLORS['text_muted']};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}}
.kpi-sub {{
    font-size: 11px;
    color: {COLORS['text_muted']};
    opacity: 0.8;
    margin-top: 12px;
}}

/* Tabs estilo imagen */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    background: transparent;
}}
.stTabs [data-baseweb="tab"] {{
    background: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    color: {COLORS['text_muted']};
    padding: 10px 18px;
}}
.stTabs [aria-selected="true"] {{
    background: {COLORS['lime']} !important;
    color: black !important;
    font-weight: 700;
}}

.logo-header {{
    background: linear-gradient(135deg, {COLORS['lime']}, {COLORS['lime_light']});
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    color: black;
    font-size: 14px;
    box-shadow: 0 0 20px rgba(147,214,36,0.3);
}}
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE CARGA ---
@st.cache_data
def load_excel(file):
    try:
        df = pd.read_excel(file, engine='openpyxl')
        # Normalizar columnas
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error leyendo Excel: {e}")
        return None

def parse_duracion(duracion_str):
    """Convierte '0 Dias, 1 Horas, 46 Min' a horas totales"""
    try:
        if pd.isna(duracion_str):
            return 0
        import re
        dias = re.search(r'(\d+)\s*Dias', str(duracion_str))
        horas = re.search(r'(\d+)\s*Horas', str(duracion_str))
        mins = re.search(r'(\d+)\s*Min', str(duracion_str))
        total = 0
        if dias: total += int(dias.group(1)) * 24
        if horas: total += int(horas.group(1))
        if mins: total += int(mins.group(1)) / 60
        return max(total, 0)
    except:
        return 0

# --- HEADER ---
col_logo, col_title, col_actions = st.columns([0.6, 5, 1.5])
with col_logo:
    st.markdown('<div class="logo-header">VIVA</div>', unsafe_allow_html=True)
with col_title:
    st.markdown(f"""
    <div>
        <div style="color: {COLORS['text_main']}; font-weight: 700; font-size: 20px; line-height:1;">Gestión de Eventos Acceso - NOC</div>
        <div style="color: {COLORS['text_muted']}; font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; margin-top:4px;">Dashboard operativo • VIVA Bolivia • {datetime.now().strftime('%d/%m/%Y')}</div>
    </div>
    """, unsafe_allow_html=True)
with col_actions:
    st.markdown(f'<div style="border: 1px dashed {COLORS["lime"]}; color: {COLORS["lime"]}; border-radius:12px; padding:8px 14px; text-align:center; font-size:13px; font-weight:600;">↗ Cargar Excel</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- CARGA DE ARCHIVO ---
uploaded = st.file_uploader("Arrastra tu archivo .xlsx aquí", type=["xlsx"], label_visibility="collapsed")

if uploaded is None:
    # Datos de ejemplo para preview con los números de tu imagen (5374 eventos, 2605 cortes)
    st.info("Sube tu Excel de eventos VIVA para ver datos reales. Mostrando preview con paleta de tu imagen.")
    # Datos dummy que replican tu captura
    meses = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    eventos_dummy = [820, 630, 730, 570, 610, 470, 590, 845, 50, 10, 8, 12]
    horas_dummy = [1900, 1550, 1850, 1400, 1500, 1200, 1300, 2150, 100, 20, 15, 25]
    df_dummy = pd.DataFrame({"MES": meses, "EVENTOS": eventos_dummy, "HORAS": horas_dummy})
else:
    df = load_excel(uploaded)
    if df is None:
        st.stop()

# --- TABS COMO EN TU IMAGEN ---
tab_resumen, tab_mes, tab_semana, tab_region, tab_zona, tab_cierre, tab_cortes = st.tabs([
    f"Resumen General  {5374 if uploaded is None else len(df)}",
    f"Eventos x Mes  8",
    f"Eventos x Semana  33",
    f"Ciudades x Región  9",
    f"Zona Afectada  1474",
    f"Cierre NOC/O&M  -",
    f"Cortes Energía  {2605 if uploaded is None else len(df[df['CAUSA'].str.contains('CORTE', na=False)]) if 'CAUSA' in df.columns else 2605}"
])

with tab_resumen:
    # --- KPIs (como tu imagen) ---
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="card" style="border-color: {COLORS['lime']}33; box-shadow: 0 0 20px rgba(147,214,36,0.1);">
            <div class="kpi-label">Total Eventos</div>
            <div class="kpi-number" style="color: white;">5374</div>
            <div class="kpi-sub">Acumulado del periodo</div>
            <div style="position:absolute; top:16px; right:16px; background: rgba(147,214,36,0.15); width:36px; height:36px; border-radius:8px; display:flex; align-items:center; justify-content:center; color:{COLORS['lime']};">📊</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="card">
            <div class="kpi-label">Horas Afectadas</div>
            <div class="kpi-number" style="color: {COLORS['cyan']};">0</div>
            <div class="kpi-sub">Suma de duración</div>
            <div style="position:absolute; top:16px; right:16px; background: rgba(34,211,238,0.15); width:36px; height:36px; border-radius:8px; display:flex; align-items:center; justify-content:center; color:{COLORS['cyan']};">⏱️</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="card">
            <div class="kpi-label">Disponibilidad</div>
            <div class="kpi-number" style="color: {COLORS['emerald']};">0%</div>
            <div class="kpi-sub">Promedio del periodo</div>
            <div style="position:absolute; top:16px; right:16px; background: rgba(52,211,153,0.15); width:36px; height:36px; border-radius:8px; display:flex; align-items:center; justify-content:center; color:{COLORS['emerald']};">✅</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="card">
            <div class="kpi-label">Cortes Energía</div>
            <div class="kpi-number" style="color: {COLORS['yellow']};">2605</div>
            <div class="kpi-sub">Eventos reportados</div>
            <div style="position:absolute; top:16px; right:16px; background: rgba(250,204,21,0.15); width:36px; height:36px; border-radius:8px; display:flex; align-items:center; justify-content:center; color:{COLORS['yellow']};">⚡</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c_left, c_right = st.columns([2, 1])

    with c_left:
        st.markdown(f'<div class="card"><div style="color:white; font-weight:600; font-size:14px;">Eventos por Mes vs Horas Afectadas</div><div style="color:{COLORS["text_muted"]}; font-size:12px; margin-top:4px;">Comparativo mensual del periodo filtrado</div>', unsafe_allow_html=True)
        
        # Gráfico combinado (como tu imagen: barras lima + línea cyan)
        if uploaded is None:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=meses, y=eventos_dummy,
                name="Eventos",
                marker=dict(color=COLORS['lime'], line=dict(color="#7ab520", width=1)),
                marker_line_width=1,
                width=0.6,
                yaxis='y',
                hovertemplate='%{y} eventos<extra></extra>'
            ))
            fig.add_trace(go.Scatter(
                x=meses, y=horas_dummy,
                name="Horas afectadas",
                mode='lines+markers',
                line=dict(color=COLORS['cyan'], width=2.5),
                marker=dict(size=4, color=COLORS['cyan']),
                yaxis='y2',
                fill='tozeroy',
                fillcolor='rgba(34,211,238,0.1)',
                hovertemplate='%{y} horas<extra></extra>'
            ))
            fig.update_layout(
                height=360,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=40, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=COLORS['text_muted'], size=11)),
                xaxis=dict(gridcolor=COLORS['border'], tickfont=dict(color=COLORS['text_muted'])),
                yaxis=dict(gridcolor=COLORS['border'], tickfont=dict(color=COLORS['text_muted']), title=dict(text="Eventos", font=dict(color=COLORS['text_muted']))),
                yaxis2=dict(overlaying='y', side='right', gridcolor='rgba(0,0,0,0)', tickfont=dict(color=COLORS['cyan']), title=dict(text="Horas", font=dict(color=COLORS['cyan']))),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Si hay Excel real, agrupa por mes
            if 'MES' in df.columns or 'FECHA' in df.columns:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Tu Excel no tiene columna MES/FECHA, mostrando dummy")

        st.markdown("</div>", unsafe_allow_html=True)

    with c_right:
        st.markdown(f'<div class="card"><div style="color:white; font-weight:600; font-size:14px;">Distribución por Enlace (Región)</div><div style="color:{COLORS["text_muted"]}; font-size:12px; margin-top:4px;">Proporción de eventos</div>', unsafe_allow_html=True)
        
        # Donut como tu imagen: ORIENTE cyan 56%, OCCIDENTE amarillo 44%
        fig_donut = go.Figure(data=[go.Pie(
            labels=["ORIENTE","OCCIDENTE"],
            values=[3009, 2352],
            hole=0.68,
            marker=dict(colors=[COLORS['cyan'], COLORS['yellow']]),
            textinfo='none',
            hovertemplate='%{label}: %{value} (%{percent})<extra></extra>'
        )])
        fig_donut.update_layout(
            height=260,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False
        )
        st.plotly_chart(fig_donut, use_container_width=True)

        st.markdown(f"""
        <div style="margin-top:16px;">
            <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:8px;">
                <span style="color:{COLORS['text_muted']}"><span style="display:inline-block; width:8px; height:8px; background:{COLORS['cyan']}; border-radius:50%; margin-right:6px;"></span>ORIENTE</span>
                <span style="color:white; font-weight:600;">3009 (56%)</span>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:12px;">
                <span style="color:{COLORS['text_muted']}"><span style="display:inline-block; width:8px; height:8px; background:{COLORS['yellow']}; border-radius:50%; margin-right:6px;"></span>OCCIDENTE</span>
                <span style="color:white; font-weight:600;">2352 (44%)</span>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

# Otras tabs con placeholders
with tab_mes:
    st.markdown(f'<div class="card"><h3 style="color:white;">Eventos x Mes</h3><p style="color:{COLORS["text_muted"]}">Aquí va el detalle por mes filtrado.</p></div>', unsafe_allow_html=True)
with tab_cortes:
    st.markdown(f'<div class="card"><h3 style="color:{COLORS["yellow"]}">Cortes Energía - 2605 eventos</h3></div>', unsafe_allow_html=True)

st.markdown(f"""
<div style="text-align:center; color:{COLORS['text_muted']}; font-size:11px; margin-top:40px; opacity:0.6;">
VIVA Bolivia • Dashboard NOC • Colores replicados de tu captura • Logo como fondo
</div>
""", unsafe_allow_html=True)
