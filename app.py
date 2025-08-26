import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
import streamlit.components.v1 as components

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Calculadora ICL (BCRA)",
    page_icon="📈",
    layout="centered"
)

# SEO + Rich Snippets
components.html("""
<!-- Metadatos SEO -->
<meta name="title" content="Calculadora ICL | Actualización de alquiler BCRA">
<meta name="description" content="Calculá cuánto debería ser tu nuevo alquiler según el Índice para Contratos de Locación (ICL) del Banco Central de la República Argentina.">
<meta name="robots" content="index, follow">
<meta property="og:title" content="Calculadora ICL | BCRA">
<meta property="og:description" content="Herramienta para calcular actualizaciones de alquiler según el ICL del BCRA.">
<meta property="og:url" content="https://calculadora-icl-bcra.streamlit.app">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Calculadora ICL | Actualización de alquiler">
<meta name="twitter:description" content="Calculá tu alquiler actualizado con el ICL oficial del BCRA.">
<link rel="canonical" href="https://calculadora-icl-bcra.streamlit.app">

<!-- Rich Snippet FAQ (JSON-LD) -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Qué es el ICL del BCRA?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Es el Índice para Contratos de Locación publicado diariamente por el Banco Central de la República Argentina para ajustar alquileres en contratos regulados por la Ley 27.551."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cómo se calcula el nuevo alquiler con ICL?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Se compara el ICL actual con el de la última actualización y se aplica el porcentaje de aumento al alquiler base."
      }
    }
  ]
}
</script>
""", height=0)

# TÍTULO Y DESCRIPCIÓN
st.title("📈 Calculadora ICL (BCRA)")
st.caption("Calcula la actualización de alquiler según el Índice para Contratos de Locación (ICL) publicado por el Banco Central de la República Argentina.")

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
    alquiler_base = st.number_input("Alquiler anterior ($)", min_value=0.0, value=123456.0, step=100.0, format="%.2f")
with col2:
    icl_anterior = st.number_input("ICL anterior", min_value=0.0, value=12.34, step=0.01, format="%.2f")

col3, col4 = st.columns(2)
with col3:
    meses = st.number_input("Período (meses entre ajustes)", min_value=1, max_value=24, value=4, step=1)
with col4:
    icl_nuevo = st.number_input("ICL nuevo", min_value=0.0, value=12.34, step=0.01, format="%.2f")

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
