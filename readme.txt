# 📈 Calculadora ICL (BCRA)

Calculadora para actualizar el valor de alquiler según el **Índice para Contratos de Locación (ICL)** publicado por el Banco Central de la República Argentina (BCRA).

---

## 🧮 ¿Qué hace?

Permite calcular el **nuevo valor de alquiler** ingresando:

- El valor del alquiler anterior
- El valor del ICL al momento del contrato
- El nuevo ICL más reciente
- El período de ajuste en meses

---

## 🚀 Cómo usar

1. Ingresá a la web oficial del BCRA:  
   👉 [Principales variables](https://www.bcra.gob.ar/PublicacionesEstadisticas/Principales_variables_datos.asp)

2. Buscá el valor actualizado del **Índice para Contratos de Locación (ICL)**.

3. Ingresá los datos en la calculadora para conocer el aumento porcentual y el nuevo valor del alquiler.

---

## 💻 Tecnologías

- [Streamlit](https://streamlit.io)
- [Pandas](https://pandas.pydata.org)
- [Python-dateutil](https://dateutil.readthedocs.io/)

---

## 🛠️ Cómo correr localmente

```bash
pip install -r requirements.txt
streamlit run app.py
