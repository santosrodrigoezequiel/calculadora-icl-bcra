import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import date
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Calculadora ICL (BCRA)", page_icon="📈", layout="centered")

st.title("📈 Calculadora ICL (BCRA)")
st.caption("Calcula la actualización de alquiler por ICL (serie diaria oficial del BCRA).")

# ----------------------------
# Utilidades de carga de datos
# ----------------------------

@st.cache_data(ttl=6*60*60)  # cachea 6 horas
def _leer_xls(url: str) -> pd.DataFrame:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    bio = BytesIO(resp.content)
    # Intentamos leer todas las hojas y detectar columnas de fecha/valor de forma robusta
    # porque el formato de los .xls del BCRA puede variar levemente.
    xls = pd.ExcelFile(bio)
    frames = []
    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        # Limpieza básica
        df = df.dropna(how="all")
        # Heurística: columna fecha = aquella que al convertir tenga muchas fechas válidas
        fecha_col, valor_col = None, None
        for c in df.columns:
            try:
                conv = pd.to_datetime(df[c], errors="coerce")
                if conv.notna().sum() > len(df) * 0.5:
                    fecha_col = c
                    break
            except Exception:
                pass
        # Columna valor: numérica con muchos no-nulos
        if fecha_col is not None:
            candidates = []
            for c in df.columns:
                if c == fecha_col:
                    continue
                serie = pd.to_numeric(df[c], errors="coerce")
                if serie.notna().sum() > len(df) * 0.5:
                    candidates.append((c, serie))
            if candidates:
                # elegimos la columna con más datos válidos
                valor_col = max(candidates, key=lambda t: t[1].notna().sum())[0]
        if fecha_col and valor_col:
            out = pd.DataFrame({
                "fecha": pd.to_datetime(df[fecha_col], errors="coerce").dt.date,
                "icl": pd.to_numeric(df[valor_col], errors="coerce")
            }).dropna()
            frames.append(out)
    if not frames:
        raise ValueError(f"No se pudieron identificar columnas fecha/valor en {url}")
    df_all = pd.concat(frames, ignore_index=True)
    # Quitamos duplicados y ordenamos
    df_all = df_all.drop_duplicates(subset=["fecha"]).sort_values("fecha")
    # Filtramos valores no positivos/raros
    df_all = df_all[df_all["icl"] > 0]
    return df_all

@st.cache_data(ttl=6*60*60)
def cargar_icl_para_anios(anios):
    """Intenta primero XLS anual (iclAAAA.xls). Si no, usa diar_icl.xls."""
    frames = []
    for anio in sorted(set(anios)):
        url_anual = f"https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/icl{anio}.xls"
        try:
            frames.append(_leer_xls(url_anual))
            continue
        except Exception:
            pass
    if not frames:
        # Fallback a la serie histórica completa
        url_hist = "https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/diar_icl.xls"
        frames.append(_leer_xls(url_hist))
    df = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["fecha"]).sort_values("fecha")
    return df.reset_index(drop=True)

def valor_icl_en_fecha(df: pd.DataFrame, d: date) -> float:
    """Devuelve el ICL para d. Si no hay ese día exacto, busca hacia atrás (máx 7 días)."""
    for k in range(0, 8):
        dd = (pd.Timestamp(d) - pd.Timedelta(days=k)).date()
        hit = df.loc[df["fecha"] == dd, "icl"]
        if not hit.empty:
            return float(hit.iloc[0])
    raise ValueError(f"No se encontró ICL para {d} ni los 7 días previos.")

# ----------------------------
# UI de la calculadora
# ----------------------------

col1, col2 = st.columns(2)
with col1:
    alquiler_base = st.number_input("Alquiler base (última actualización)", min_value=0.0, value=429500.0, step=100.0, format="%.2f")
with col2:
    fecha_anterior = st.date_input("Fecha última actualización (ICL anterior)", value=date(2025, 5, 1))

col3, col4 = st.columns(2)
with col3:
    meses = st.number_input("Período (meses entre ajustes)", min_value=1, max_value=24, value=4, step=1)
with col4:
    fecha_nueva_defecto = fecha_anterior + relativedelta(months=+int(meses))
    fecha_nueva = st.date_input("Fecha del nuevo ajuste (ICL nuevo)", value=fecha_nueva_defecto)

st.divider()
st.subheader("Resultado")

if st.button("Calcular actualización"):
    try:
        anios_necesarios = [fecha_anterior.year, fecha_nueva.year]
        df_icl = cargar_icl_para_anios(anios_necesarios)

        icl_old = valor_icl_en_fecha(df_icl, fecha_anterior)
        icl_new = valor_icl_en_fecha(df_icl, fecha_nueva)

        aumento_pct = (icl_new / icl_old - 1.0) * 100.0
        diferencia = alquiler_base * (icl_new - icl_old) / icl_old
        nuevo_alquiler = alquiler_base + diferencia

        tabla = pd.DataFrame([
            {"Concepto": "ICL (anterior)", "Fecha": fecha_anterior, "Valor": round(icl_old, 2)},
            {"Concepto": "ICL (nuevo)",    "Fecha": fecha_nueva,   "Valor": round(icl_new, 2)},
            {"Concepto": "Aumento %",      "Fecha": "",            "Valor": round(aumento_pct, 2)},
            {"Concepto": "Diferencia $",   "Fecha": "",            "Valor": round(diferencia, 2)},
            {"Concepto": "Nuevo alquiler", "Fecha": "",            "Valor": round(nuevo_alquiler, 2)},
        ])

        st.dataframe(tabla, use_container_width=True)
        st.success(f"Nuevo alquiler estimado: ${nuevo_alquiler:,.2f} (aumento {aumento_pct:.2f}%)")
        st.caption("Cálculo: nuevo = base × (ICL_nuevo / ICL_anterior). Diferencia = nuevo − base.")
    except Exception as e:
        st.error(f"Ocurrió un problema al traer o procesar el ICL: {e}")
        st.info("Podés reintentar o, si el sitio del BCRA no responde, ingresar los ICL manualmente en una versión alternativa.")
