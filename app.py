
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import date
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Calculadora ICL (BCRA)", page_icon="📈", layout="centered")

st.title("📈 Calculadora ICL (BCRA)")
st.caption("Calcula la actualización de alquiler por ICL (serie diaria oficial del BCRA).")

# ----------------------------
# Utilidades de carga de datos desde HTML
# ----------------------------

@st.cache_data(ttl=6*60*60)
def cargar_icl_desde_html():
    url = "https://www.bcra.gob.ar/PublicacionesEstadisticas/Principales_variables_datos.asp"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")

    tabla = soup.find("table", {"id": "tbl_datos"})
    if tabla is None:
        raise ValueError("No se encontró la tabla con ID 'tbl_datos' en la página del BCRA.")

    filas = tabla.find_all("tr")
    data = []
    for fila in filas:
        celdas = fila.find_all("td")
        if len(celdas) >= 2:
            fecha_txt = celdas[0].text.strip()
            valor_txt = celdas[1].text.strip().replace(",", ".")
            try:
                fecha = pd.to_datetime(fecha_txt, dayfirst=True).date()
                valor = float(valor_txt)
                data.append({"fecha": fecha, "icl": valor})
            except:
                continue  # ignorar filas con errores de parseo

    df = pd.DataFrame(data).sort_values("fecha")
    return df.reset_index(drop=True)

def valor_icl_en_fecha(df: pd.DataFrame, d: date) -> float:
    """Busca el valor de ICL para una fecha. Si no hay exacta, usa la más cercana previa."""
    fechas_disponibles = df[df["fecha"] <= d]
    if fechas_disponibles.empty:
        raise ValueError(f"No hay valores de ICL anteriores a {d}")
    fila = fechas_disponibles.iloc[-1]
    return float(fila["icl"])

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
        df_icl = cargar_icl_desde_html()
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
