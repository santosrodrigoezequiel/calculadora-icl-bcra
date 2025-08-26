import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Calculadora ICL (BCRA)", page_icon="📈", layout="centered")
st.title("📈 Calculadora ICL del Banco Central de la República Argentina")
st.caption("Calcula la actualización de alquiler según el Índice para Contratos de Locación (ICL) publicado por el BCRA.")

# ----------------------------
# Instrucciones manuales
# ----------------------------

st.subheader("📌 Instrucciones para obtener el ICL")
st.markdown("""
1. Ingresá a la página oficial del BCRA: [Principales variables](https://www.bcra.gob.ar/PublicacionesEstadisticas/Principales_variables_datos.asp)
2. Buscá el índice llamado **Índice para Contratos de Locación (ICL)**.
3. Tomá el valor correspondiente a la fecha que te interese (por ejemplo, el 1º de cada mes).
4. Ingresalo manualmente en los campos de abajo.
""")

# ----------------------------
# Ingreso manual de datos
# ----------------------------

st.divider()
st.subheader("✍️ Ingresar datos")

col1, col2 = st.columns(2)
with col1:
    alquiler_base = st.number_input("Alquiler anterior ($)", min_value=0.0, value=000000.0, step=100.0, format="%.2f")
with col2:
    icl_anterior = st.number_input("ICL anterior", min_value=0.0, value=00.00, step=0.01, format="%.2f")

col3, col4 = st.columns(2)
with col3:
    meses = st.number_input("Período (meses entre ajustes)", min_value=1, max_value=24, value=4, step=1)
with col4:
    icl_nuevo = st.number_input("ICL nuevo", min_value=0.0, value=00.00, step=0.01, format="%.2f")

# ----------------------------
# Cálculo
# ----------------------------

st.divider()
st.subheader("📊 Resultado")

if st.button("Calcular actualización"):
    try:
        aumento_pct = (icl_nuevo / icl_anterior - 1.0) * 100.0
        diferencia = alquiler_base * (icl_nuevo - icl_anterior) / icl_anterior
        nuevo_alquiler = alquiler_base + diferencia

        tabla = pd.DataFrame([
            {"Concepto": "ICL anterior", "Valor": round(icl_anterior, 2)},
            {"Concepto": "ICL nuevo", "Valor": round(icl_nuevo, 2)},
            {"Concepto": "Aumento %", "Valor": round(aumento_pct, 2)},
            {"Concepto": "Diferencia $", "Valor": round(diferencia, 2)},
            {"Concepto": "Nuevo alquiler", "Valor": round(nuevo_alquiler, 2)},
        ])

        st.dataframe(tabla, use_container_width=True)
        st.success(f"Nuevo alquiler estimado: ${nuevo_alquiler:,.2f} (aumento {aumento_pct:.2f}%)")
    except Exception as e:
        st.error(f"Ocurrió un error en el cálculo: {e}")
