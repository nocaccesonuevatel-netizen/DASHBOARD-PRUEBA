# =============================================================================
# 3. FILTROS DINÁMICOS EN LA BARRA LATERAL (CORREGIDO DEFENSIBO)
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

# C. Filtro por Ciudad (Ordenamiento seguro convirtiendo a string)
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
