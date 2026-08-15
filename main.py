import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from data_processing import load_and_clean_data

# =============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS CSS EJECUTIVOS
# =============================================================================
st.set_page_config(
    page_title="Dashboard Ejecutivo - Monitoreo de Red",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {
        background-color: #F8FAFC;
    }
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #475569;
    }
    h1, h2, h3 {
        color: #0F172A;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📡 Dashboard Ejecutivo de Incidentes y Afectaciones de Red")
st.caption("Monitoreo estratégico de indisponibilidad, causas raíz y detección de impacto")

# =============================================================================
# 2. CARGA DE ARCHIVO EN STREAMLIT
# =============================================================================
st.sidebar.header("📁 Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Subir reporte mensual (.xlsx)", type=["xlsx"])

if uploaded_file is None:
    st.info("👈 Por favor, carga el archivo Excel en la barra lateral para iniciar el análisis.")
    st.stop()

@st.cache_data(show_spinner="Procesando e ingiriendo datos...")
def get_processed_data(file):
    return load_and_clean_data(file)

try:
    df_raw = get_processed_data(uploaded_file)
except Exception as e:
    st.error(f"❌ Error al procesar el archivo Excel: {e}")
    st.stop()

# =============================================================================
# 3. FILTROS DINÁMICOS EN LA BARRA LATERAL (CORREGIDO DEFENSA)
# =============================================================================
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filtros de Control")

df_filtered = df_raw.copy()

# A. Rango de Fechas
min_date = df_raw["FECHA INICIO"].dropna().min()
max_date = df_raw["FECHA INICIO"].dropna().max()

if pd.notna(min_date) and pd.notna(max_date):
    date_range = st.sidebar.date_input(
        "Rango de Fechas",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date()
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df_filtered[
            (df_filtered["FECHA INICIO"].dt.date >= start_date) & 
            (df_filtered["FECHA INICIO"].dt.date <= end_date)
        ]

# B. Filtro por Semana (WEEK)
weeks_available = sorted([int(w) for w in df_filtered["WEEK"].dropna().unique() if str(w).isdigit()])
selected_weeks = st.sidebar.multiselect("Semana (WEEK)", options=weeks_available)
if selected_weeks:
    df_filtered = df_filtered[df_filtered["WEEK"].isin(selected_weeks)]

# C. Filtro por Ciudad
cities_available = sorted(list(set(str(c) for c in df_filtered["CIUDAD"].dropna().unique() if str(c).strip() != "")))
selected_cities = st.sidebar.multiselect("Ciudad", options=cities_available)
if selected_cities:
    df_filtered = df_filtered[df_filtered["CIUDAD"].astype(str).isin(selected_cities)]

# D. Filtro por Zona Afectada
zones_available = sorted(list(set(str(z) for z in df_filtered["ZONA AFECTADA"].dropna().unique() if str(z).strip() != "")))
selected_zones = st.sidebar.multiselect("Zona Afectada", options=zones_available)
if selected_zones:
    df_filtered = df_filtered[df_filtered["ZONA AFECTADA"].astype(str).isin(selected_zones)]

# E. Filtro por Criticidad
crit_available = sorted(list(set(str(cr) for cr in df_filtered["CRITICIDAD"].dropna().unique() if str(cr).strip() != "")))
selected_crit = st.sidebar.multiselect("Criticidad", options=crit_available)
if selected_crit:
    df_filtered = df_filtered[df_filtered["CRITICIDAD"].astype(str).isin(selected_crit)]

# F. Filtro por Causa del Evento
causes_available = sorted(list(set(str(cs) for cs in df_filtered["CAUSA"].dropna().unique() if str(cs).strip() != "")))
selected_causes = st.sidebar.multiselect("Causa del Evento", options=causes_available)
if selected_causes:
    df_filtered = df_filtered[df_filtered["CAUSA"].astype(str).isin(selected_causes)]

# G. Filtro por Tecnología Afectada
techs_available = sorted(list(set(str(t) for t in df_filtered["TECNOLOGIAS AFECTADAS"].dropna().unique() if str(t).strip() != "")))
selected_techs = st.sidebar.multiselect("Tecnología Afectada", options=techs_available)
if selected_techs:
    df_filtered = df_filtered[df_filtered["TECNOLOGIAS AFECTADAS"].astype(str).isin(selected_techs)]

if df_filtered.empty:
    st.warning("⚠️ No se encontraron registros con la combinación de filtros seleccionada.")
    st.stop()

# =============================================================================
# 4. TARJETAS DE KPIS EJECUTIVOS
# =============================================================================
st.subheader("📊 Indicadores Clave de Rendimiento (KPIs)")

total_eventos = len(df_filtered)
total_horas_afectacion = df_filtered["DURACION_HORAS"].sum()

tech_impact = df_filtered.groupby("TECNOLOGIAS AFECTADAS")["DURACION_HORAS"].sum()
top_tech = tech_impact.idxmax() if not tech_impact.empty else "N/A"
top_tech_hours = tech_impact.max() if not tech_impact.empty else 0.0

cause_count = df_filtered["CAUSA"].value_counts()
top_cause_count_val = cause_count.iloc[0] if not cause_count.empty else 0

cause_duration = df_filtered.groupby("CAUSA")["DURACION_HORAS"].sum()
top_cause_by_dur = cause_duration.idxmax() if not cause_duration.empty else "N/A"
top_cause_dur_val = cause_duration.max() if not cause_duration.empty else 0.0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Eventos", value=f"{total_eventos:,}")
with col2:
    st.metric(label="Horas Afectación", value=f"{total_horas_afectacion:,.1f} h")
with col3:
    st.metric(label="Tech Más Afectada", value=str(top_tech), delta=f"{top_tech_hours:,.1f} h", delta_color="inverse")
with col4:
    st.metric(label="Principal Causa Raíz", value=str(top_cause_by_dur), delta=f"{top_cause_dur_val:,.1f} h ({top_cause_count_val} evs)", delta_color="inverse")

st.markdown("---")

# =============================================================================
# 5. PANEL DE ALERTAS Y SITIOS RECURRENTES (TOP 10)
# =============================================================================
st.subheader("🚨 Panel de Alerta: Top 10 Sitios Recurrentes y Críticos")

df_recurrent = df_filtered[df_filtered["CELL ID"] != "NO ESPECIFICADO"].copy()

if df_recurrent.empty:
    st.info("ℹ️ No hay registros con 'CELL ID' especificado en los datos filtrados actualmente.")
else:
    top_sites = (
        df_recurrent.groupby(["CELL ID", "CIUDAD", "ZONA AFECTADA"])
        .agg(
            FRECUENCIA=("Número de Ticket", "count"),
            DURACION_TOTAL_HORAS=("DURACION_HORAS", "sum"),
            CAUSA_MAS_FRECUENTE=("CAUSA", lambda x: x.mode()[0] if not x.empty else "N/A")
        )
        .reset_index()
    )
    top_sites["DURACION_TOTAL_HORAS"] = top_sites["DURACION_TOTAL_HORAS"].round(2)
    top_sites = top_sites.sort_values(by=["FRECUENCIA", "DURACION_TOTAL_HORAS"], ascending=[False, False]).head(10)
    
    with st.container():
        st.markdown(
            """
            <div style="background-color: #FFF5F5; border-left: 6px solid #E53E3E; padding: 15px 20px; border-radius: 6px; margin-bottom: 20px;">
                <h4 style="color: #9B2C2C; margin: 0 0 8px 0;">⚠️ Atención Inmediata Requiere Operaciones & Mantenimiento</h4>
                <p style="color: #742A2A; margin: 0; font-size: 0.95rem;">
                    Los siguientes sitios acumulan la mayor cantidad de caídas y tiempo de indisponibilidad.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        col_rank, col_table = st.columns([1, 2])
        with col_rank:
            st.markdown("##### 🔝 Top 3 Más Afectados")
            top_3 = top_sites.head(3)
            rank_badges = ["1️⃣", "2️⃣", "3️⃣"]
            for idx, (_, row) in enumerate(top_3.iterrows()):
                badge = rank_badges[idx] if idx < len(rank_badges) else "📍"
                st.error(
                    f"**{badge} {row['CELL ID']}** ({row['CIUDAD']})\n\n"
                    f"- **Reincidencias:** {row['FRECUENCIA']} caídas\n"
                    f"- **Horas fuera:** {row['DURACION_TOTAL_HORAS']} h\n"
                    f"- **Causa usual:** {row['CAUSA_MAS_FRECUENTE']}"
                )
        with col_table:
            st.markdown("##### 📋 Listado Completo Top 10 Sitios Críticos")
            st.dataframe(
                top_sites.rename(columns={
                    "CELL ID": "Sitio / Cell ID", "CIUDAD": "Ciudad", "ZONA AFECTADA": "Zona",
                    "FRECUENCIA": "N° Caídas", "DURACION_TOTAL_HORAS": "Horas Afectadas (h)", "CAUSA_MAS_FRECUENTE": "Causa Recurrente"
                }),
                use_container_width=True, hide_index=True
            )

st.markdown("---")

# =============================================================================
# 6. GRÁFICOS INTERACTIVOS DE ANÁLISIS (PLOTLY)
# =============================================================================
st.subheader("📈 Análisis Gráfico de Afectaciones e Impacto")

col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    st.markdown("##### 🍕 Distribución por Causa Raíz")
    metric_cause = st.radio("Métrica de Causa:", ["Horas de Afectación", "Número de Eventos"], horizontal=True, key="radio_cause")
    
    if metric_cause == "Horas de Afectación":
        df_cause = df_filtered.groupby("CAUSA")["DURACION_HORAS"].sum().reset_index()
        val_col, title_metric = "DURACION_HORAS", "Horas Totales"
    else:
        df_cause = df_filtered["CAUSA"].value_counts().reset_index()
        df_cause.columns = ["CAUSA", "COUNT"]
        val_col, title_metric = "COUNT", "Cantidad de Eventos"
    
    fig_cause = px.pie(df_cause, names="CAUSA", values=val_col, hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
    fig_cause.update_traces(textposition='inside', textinfo='percent+label', hovertemplate='<b>%{label}</b><br>' + title_metric + ': %{value:,.1f}<extra></extra>')
    fig_cause.update_layout(showlegend=False, margin=dict(l=20, r=20, t=30, b=20), height=350)
    st.plotly_chart(fig_cause, use_container_width=True)

with col_chart2:
    st.markdown("##### 📡 Horas de Afectación Acumuladas por Tecnología")
    df_tech = df_filtered.groupby("TECNOLOGIAS AFECTADAS")["DURACION_HORAS"].sum().reset_index().sort_values(by="DURACION_HORAS", ascending=True)
    fig_tech = px.bar(df_tech, x="DURACION_HORAS", y="TECNOLOGIAS AFECTADAS", orientation='h', text_auto='.1f', color="DURACION_HORAS", color_continuous_scale="Reds")
    fig_tech.update_layout(xaxis_title="Horas Fuera de Servicio", yaxis_title="Tecnología", coloraxis_showscale=False, margin=dict(l=20, r=20, t=30, b=20), height=350)
    fig_tech.update_traces(textposition="outside")
    st.plotly_chart(fig_tech, use_container_width=True)

st.markdown("---")

col_chart3, col_chart4 = st.columns(2)
with col_chart3:
    st.markdown("##### 📅 Tendencia de Incidentes por Semana (WEEK)")
    df_trend = df_filtered.groupby("WEEK").agg(TOTAL_EVENTOS=("Número de Ticket", "count"), TOTAL_HORAS=("DURACION_HORAS", "sum")).reset_index()
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(x=df_trend["WEEK"], y=df_trend["TOTAL_EVENTOS"], name="N° Eventos", marker_color="#2B6CB0", yaxis="y"))
    fig_trend.add_trace(go.Scatter(x=df_trend["WEEK"], y=df_trend["TOTAL_HORAS"], name="Horas Afectación", mode="lines+markers", line=dict(color="#E53E3E", width=3), yaxis="y2"))
    fig_trend.update_layout(
        xaxis=dict(title="Semana del Año (WEEK)", dtick=1), yaxis=dict(title="N° de Eventos", side="left"),
        yaxis2=dict(title="Horas Afectación (h)", side="right", overlaying="y", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=20, r=20, t=30, b=20), height=380
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col_chart4:
    st.markdown("##### 🏙️ Desglose de Incidentes por Ciudad")
    df_city = df_filtered.groupby(["CIUDAD", "CRITICIDAD"])["Número de Ticket"].count().reset_index()
    fig_city = px.bar(df_city, x="CIUDAD", y="Número de Ticket", color="CRITICIDAD", barmode="stack",
                      color_discrete_map={"CRITICA": "#E53E3E", "ALTA": "#DD6B20", "MEDIA": "#D69E2E", "BAJA": "#319795"})
    fig_city.update_layout(xaxis_title="Ciudad", yaxis_title="Cantidad de Eventos", legend_title="Criticidad", margin=dict(l=20, r=20, t=30, b=20), height=380)
    st.plotly_chart(fig_city, use_container_width=True)

st.markdown("---")

# =============================================================================
# 7. TABLA EJECUTIVA DETALLADA Y EXPORTACIÓN DE DATOS
# =============================================================================
st.subheader("📑 Explorador de Eventos y Exportación")

search_term = st.text_input("🔎 Búsqueda rápida por texto (Ticket, Cell ID, Responsable, Causa):", "")

df_display = df_filtered.copy()

if search_term.strip():
    term = search_term.strip().lower()
    mask = (
        df_display["Número de Ticket"].astype(str).str.lower().str.contains(term) |
        df_display["CELL ID"].astype(str).str.lower().str.contains(term) |
        df_display["RESPONSABLE"].astype(str).str.lower().str.contains(term) |
        df_display["CAUSA"].astype(str).str.lower().str.contains(term) |
        df_display["ZONA AFECTADA"].astype(str).str.lower().str.contains(term)
    )
    df_display = df_display[mask]

st.caption(f"Mostrando {len(df_display)} registros de {len(df_filtered)} filtrados.")

st.dataframe(
    df_display.style.format({"DURACION_HORAS": "{:.2f} h"}),
    use_container_width=True,
    height=400
)

def convert_df_to_excel(df_to_export):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_to_export.to_excel(writer, index=False, sheet_name='Eventos_Filtrados')
    processed_data = output.getvalue()
    return processed_data

col_exp1, col_exp2 = st.columns([1, 4])

with col_exp1:
    excel_data = convert_df_to_excel(df_display)
    st.download_button(
        label="📥 Descargar Excel",
        data=excel_data,
        file_name="reporte_eventos_red_filtrado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col_exp2:
    csv_data = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Descargar CSV",
        data=csv_data,
        file_name="reporte_eventos_red_filtrado.csv",
        mime="text/csv"
    )
