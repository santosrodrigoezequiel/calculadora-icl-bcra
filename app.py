import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Calculadora ICL (BCRA)",
    page_icon="📈",
    layout="centered"
)

# Mostrar imagen portada
st.image(".streamlit/app-image.png", use_container_width=True)

# Título
st.markdown("## 📊 Calculadora ICL (BCRA)")
st.markdown(
    "Calcula la actualización de alquiler según el Índice para Contratos de Locación (ICL) "
    "publicado por el Banco Central de la República Argentina."
)

# Instrucciones
st.markdown("---")
st.markdown("### 📌 Instrucciones para obtener el ICL")
st.markdown("""
1. Ingresá a la página oficial del BCRA: [Principales variables](https://www.bcra.gob.ar/PublicacionesEstadisticas/Principales_variables.asp).
2. Buscá el índice llamado **Índice para Contratos de Locación (ICL)**.
3. Tomá el valor correspondiente a la fecha que te interese (por ejemplo, el 1º de cada mes).
4. Ingresalo manualmente en los campos de abajo.
""")

# Separador
st.markdown("---")
st.markdown("### 📝 Ingresar datos")

# Inputs del usuario
col1, col2 = st.columns(2)
with col1:
    alquiler_anterior = st.number_input("Alquiler anterior ($)", min_value=0.0, format="%.2f")
with col2:
    icl_anterior = st.number_input("ICL anterior", min_value=0.0000, format="%.6f")

col3, col4 = st.columns(2)
with col3:
    icl_actual = st.number_input("ICL actual", min_value=0.0000, format="%.6f")
with col4:
    meses_transcurridos = st.slider("Meses transcurridos", 0, 36, 12)

# Cálculo
if icl_anterior > 0 and icl_actual > 0 and alquiler_anterior > 0:
    porcentaje_actualizacion = (icl_actual / icl_anterior)
    nuevo_alquiler = alquiler_anterior * porcentaje_actualizacion

    st.markdown("---")
    st.success(f"📌 **Nuevo alquiler estimado:** ${nuevo_alquiler:,.2f}")
    st.caption(f"Incremento del {((porcentaje_actualizacion - 1)*100):.2f}% en {meses_transcurridos} meses.")
else:
    st.info("🔍 Ingresá todos los valores para obtener el resultado.")
