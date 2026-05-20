import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

from influxdb_client import InfluxDBClient

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================

st.set_page_config(
    page_title="Wellness Pod",
    layout="wide"
)

# =====================================================
# ESTILOS PERSONALIZADOS
# =====================================================

st.markdown("""
<style>

.main {
    background-color: #0e1117;
}

h1, h2, h3, h4 {
    color: white;
}

.stMetric {
    background-color: #d0facd;
    padding: 15px;
    border-radius: 15px;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.title("🌿 Wellness Pod Dashboard")

st.subheader(
    "Sistema IoT para monitoreo ambiental y movimiento en tiempo real"
)

st.markdown("---")

# =====================================================
# PANEL INTERACTIVO
# =====================================================

st.sidebar.title("⚙ Panel de Control")

mode = st.sidebar.selectbox(
    "Selecciona el modo del espacio",
    [
        "Relajación",
        "Trabajo",
        "Concentración"
    ]
)

ideal_temp = st.sidebar.slider(
    "Temperatura ideal",
    15,
    35,
    24
)

alerts = st.sidebar.toggle(
    "Activar alertas",
    value=True
)

time_range = st.sidebar.selectbox(
    "Rango temporal",
    [
        "-30m",
        "-1h",
        "-6h",
        "-12h"
    ]
)

# =====================================================
# CONEXIÓN A INFLUXDB
# =====================================================

url = "https://us-east-1-1.aws.cloud2.influxdata.com"

token = "token: JoKdx3OFaBCFPmYQgiVWE8hjrtJ0lDkjwWZzT9djWJlvg98rtTgF9iRgKhQtAkKIA2UQsU6zsrJlv1BH6lfsVw=="

org = "miguelcmo"

bucket = "iot_telemetry_data"

client = InfluxDBClient(
    url=url,
    token=token,
    org=org
)

query_api = client.query_api()

# =====================================================
# CONSULTA TEMPERATURA
# =====================================================

temp_query = f'''
from(bucket: "{bucket}")
  |> range(start: {time_range})
  |> filter(fn: (r) => r._measurement == "environment")
  |> filter(fn: (r) => r._field == "temperature")
'''

temp_df = query_api.query_data_frame(temp_query)

# =====================================================
# CONSULTA HUMEDAD
# =====================================================

humidity_query = f'''
from(bucket: "{bucket}")
  |> range(start: {time_range})
  |> filter(fn: (r) => r._measurement == "environment")
  |> filter(fn: (r) => r._field == "humidity")
'''

humidity_df = query_api.query_data_frame(humidity_query)

# =====================================================
# CONSULTA ACELERACIÓN
# =====================================================

accel_query = f'''
from(bucket: "{bucket}")
  |> range(start: {time_range})
  |> filter(fn: (r) => r._measurement == "mpu6050")
  |> filter(fn: (r) =>
      r._field == "accel_x" or
      r._field == "accel_y" or
      r._field == "accel_z"
  )
'''

accel_df = query_api.query_data_frame(accel_query)

# =====================================================
# OBTENER VALORES ACTUALES
# =====================================================

latest_temp = (
    temp_df["_value"].iloc[-1]
    if not temp_df.empty
    else 0
)

latest_humidity = (
    humidity_df["_value"].iloc[-1]
    if not humidity_df.empty
    else 0
)

# =====================================================
# ESTADO DEL MOVIMIENTO
# =====================================================

movement_state = "Estable"

avg_accel = 0

if not accel_df.empty:

    avg_accel = accel_df["_value"].mean()

    if avg_accel > 1.5:
        movement_state = "Movimiento Alto"

    else:
        movement_state = "Movimiento Bajo"

# =====================================================
# INTERPRETACIÓN SEGÚN MODO
# =====================================================

comfort = "Óptimo"

if mode == "Relajación":

    if latest_temp > ideal_temp + 3:
        comfort = "Ambiente caluroso"

    elif latest_temp < ideal_temp - 3:
        comfort = "Ambiente frío"

    else:
        comfort = "Ambiente relajante"

elif mode == "Trabajo":

    if latest_temp > ideal_temp + 2:
        comfort = "Posible fatiga térmica"

    else:
        comfort = "Ambiente productivo"

elif mode == "Concentración":

    if movement_state == "Movimiento Alto":
        comfort = "Espacio inestable"

    else:
        comfort = "Espacio óptimo"

# =====================================================
# MÉTRICAS PRINCIPALES
# =====================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🌡 Temperatura",
    f"{latest_temp:.2f} °C"
)

col2.metric(
    "💧 Humedad",
    f"{latest_humidity:.2f} %"
)

col3.metric(
    "📳 Movimiento",
    movement_state
)

col4.metric(
    "🧘 Estado",
    comfort
)

st.markdown("---")

# =====================================================
# ALERTAS
# =====================================================

if alerts:

    if latest_temp > ideal_temp + 5:

        st.error(
            "⚠ Temperatura demasiado alta"
        )

    elif latest_temp < ideal_temp - 5:

        st.warning(
            "⚠ Temperatura demasiado baja"
        )

    else:

        st.success(
            "✅ Condiciones estables"
        )

# =====================================================
# ESTADO DEL AMBIENTE
# =====================================================

st.sidebar.subheader("🧠 Estado del ambiente")

if comfort == "Ambiente relajante":

    st.sidebar.success(
        "Nivel de bienestar alto"
    )

elif comfort == "Espacio inestable":

    st.sidebar.error(
        "Nivel de bienestar bajo"
    )

else:

    st.sidebar.info(
        "Estado moderado"
    )

# =====================================================
# GRÁFICA TEMPERATURA
# =====================================================

if not temp_df.empty:

    fig_temp = px.line(
        temp_df,
        x="_time",
        y="_value",
        title="Temperatura en tiempo real"
    )

    st.plotly_chart(
        fig_temp,
        use_container_width=True
    )

# =====================================================
# GRÁFICA HUMEDAD
# =====================================================

if not humidity_df.empty:

    fig_humidity = px.line(
        humidity_df,
        x="_time",
        y="_value",
        title="Humedad en tiempo real"
    )

    st.plotly_chart(
        fig_humidity,
        use_container_width=True
    )

# =====================================================
# GRÁFICA ACELERACIÓN
# =====================================================

if not accel_df.empty:

    fig_accel = px.line(
        accel_df,
        x="_time",
        y="_value",
        color="_field",
        title="Movimiento y aceleración MPU6050"
    )

    st.plotly_chart(
        fig_accel,
        use_container_width=True
    )

# =====================================================
# MAGNITUD DEL MOVIMIENTO
# =====================================================

if not accel_df.empty:

    magnitude = np.sqrt(
        accel_df["_value"]**2
    )

    magnitude_df = pd.DataFrame({
        "time": accel_df["_time"],
        "magnitude": magnitude
    })

    fig_mag = px.area(
        magnitude_df,
        x="time",
        y="magnitude",
        title="Magnitud del movimiento"
    )

    st.plotly_chart(
        fig_mag,
        use_container_width=True
    )

# =====================================================
# TABLA DE DATOS
# =====================================================

st.markdown("---")

st.subheader("📋 Datos recientes")

if not temp_df.empty:

    recent_data = temp_df[[
        "_time",
        "_value"
    ]].tail(10)

    recent_data.columns = [
        "Tiempo",
        "Temperatura"
    ]

    st.dataframe(
        recent_data,
        use_container_width=True
    )

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "Proyecto Final IoT - Diseño Interactivo"
)
