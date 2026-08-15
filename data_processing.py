import pandas as pd
import numpy as np

REQUIRED_COLUMNS = [
    "Número de Ticket", "FECHA DE SOLICITUD", "WEEK", "RESPONSABLE",
    "CRITICIDAD", "TECNOLOGIAS AFECTADAS", "SERVICIOS AFECTADOS",
    "TIPO DE EVENTO", "IMPACTO", "CIUDAD", "ZONA AFECTADA",
    "CRONOLOGIA DEL EVENTO", "SEGUIMIENTO 1RA LINEA", "CELL ID",
    "FECHA INICIO", "FECHA FIN", "HORA INICIO", "HORA FIN",
    "DURACION", "CAUSA", "RESPONSABLE CIERRE DEL EVENTO",
    "RESPONSABLE 1RA LINEA", "RESPONSABLE 2DA LINEA"
]

def parse_duration_to_hours(val) -> float:
    if pd.isna(val):
        return 0.0
    if isinstance(val, pd.Timedelta):
        return val.total_seconds() / 3600.0
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).strip()
    try:
        parts = val_str.split(':')
        if len(parts) == 3:
            h, m, s = map(float, parts)
            return h + (m / 60.0) + (s / 3600.0)
        elif len(parts) == 2:
            h, m = map(float, parts)
            return h + (m / 60.0)
    except Exception:
        pass
    return 0.0

def load_and_clean_data(file_source) -> pd.DataFrame:
    df = pd.read_excel(file_source)
    df.columns = [str(col).strip() for col in df.columns]
    
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"El archivo Excel no cumple con la estructura requerida. "
            f"Faltan las siguientes columnas: {', '.join(missing_cols)}"
        )
    
    df = df[REQUIRED_COLUMNS].copy()
    
    text_columns = [
        "RESPONSABLE", "CRITICIDAD", "TECNOLOGIAS AFECTADAS", "SERVICIOS AFECTADOS",
        "TIPO DE EVENTO", "IMPACTO", "CIUDAD", "ZONA AFECTADA", "CELL ID",
        "CAUSA", "RESPONSABLE CIERRE DEL EVENTO", "RESPONSABLE 1RA LINEA", "RESPONSABLE 2DA LINEA"
    ]
    for col in text_columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace(["nan", "None", "NaN", ""], "NO ESPECIFICADO")
    
    date_cols = ["FECHA DE SOLICITUD", "FECHA INICIO", "FECHA FIN"]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    df["WEEK"] = pd.to_numeric(df["WEEK"], errors='coerce').fillna(0).astype(int)
    df["DURACION_HORAS"] = df["DURACION"].apply(parse_duration_to_hours)
    
    mask_recalc = (df["DURACION_HORAS"] <= 0) & df["FECHA INICIO"].notna() & df["FECHA FIN"].notna()
    if mask_recalc.any():
        calculated_hours = (df.loc[mask_recalc, "FECHA FIN"] - df.loc[mask_recalc, "FECHA INICIO"]).dt.total_seconds() / 3600.0
        df.loc[mask_recalc, "DURACION_HORAS"] = np.maximum(calculated_hours, 0)
    
    df["DURACION_HORAS"] = df["DURACION_HORAS"].round(2)
    return df
