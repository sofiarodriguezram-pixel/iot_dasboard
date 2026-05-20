import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

from influxdb_client import InfluxDBClient

# --------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# --------------------------------

st.set_page_config(
    page_title="Wellness Pod",
    layout="wide"
)

# --------------------------------
# ESTILOS
# --------------------------------

st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}

.metric-container {
    background-color: #1c1f26;
    padding: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------
# HEADER
# --------------------------------

st.title("🌿 Wellness Pod Dashboard")
st.subheader("Monitoreo ambiental y movimiento en tiempo real")

st.markdown("---")

# --------------------------------
# CONEXIÓN INFLUXDB
# --------------------------------

url = "https://us-east-1-1.aws.cloud2.influxdata.com"

token = "PEGA_AQUI_EL_TOKEN"

org = "miguelcmo"

bucket = "iot_telemetry_data"

client = InfluxDBClient(
    url=url,
    token=token,
    org=org
)

query_api = client.query_api()

# --------------------------------
# CONSULTA TEMPERATURA
# --------------------------------

temp_query = f'''
from(bucket: "{bucket}")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "environment")
  |> filter(fn: (r) => r._field == "temperature")
'''

temp_df = query_api.query_data_frame(temp_query)

# --------------------------------
# CONSULTA HUMEDAD
# --------------------------------

humidity_query = f'''
from(bucket: "{bucket}")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "environment")
  |> filter(fn: (r) => r._field == "humidity")
'''

humidity_df = query_api.query_data_frame(humidity_query)

# --------------------------------
# CONSULTA ACELERACIÓN
# --------------------------------

accel_query = f'''
from(bucket: "{bucket}")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "mpu6050")
  |> filter(fn: (r) =>
      r._field == "accel_x" or
      r._field == "accel_y" or
      r._field == "accel_z"
  )
'''

accel_df = query_api.query_data_frame(accel_query)

# --------------------------------
# OBTENER VALORES ACTUALES
# --------------------------------

latest_temp = temp_df["_value"].iloc[-1] if not temp_df.empty else 0

latest_humidity = humidity_df["_value"].iloc[-1] if not humidity_df.empty else 0

# --------------------------------
# ESTADO DE MOVIMIENTO
# --------------------------------

movement_state = "Estable"

if not accel_df.empty:
    avg_accel = accel_df["_value"].mean()

    if avg_accel > 1.5:
        movement_state = "Movimiento Alto"
    else:
        movement_state = "Movimiento Bajo"

# --------------------------------
# NIVEL DE CONFORT
# --------------------------------

comfort = "Óptimo"

if latest_temp > 30:
    comfort = "Caluroso"

elif latest_temp < 18:
    comfort = "Frío"

# --------------------------------
# MÉTRICAS
# --------------------------------

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
    "🧘 Confort",
    comfort
)

st.markdown("---")

# --------------------------------
# ALERTAS
# --------------------------------

if latest_temp > 30:
    st.error("⚠ Alta temperatura detectada")

elif latest_temp < 18:
    st.warning("⚠ Temperatura baja")

else:
    st.success("✅ Temperatura estable")

# --------------------------------
# GRÁFICA TEMPERATURA
# --------------------------------

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

# --------------------------------
# GRÁFICA HUMEDAD
# --------------------------------

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

# --------------------------------
# GRÁFICA ACELERACIÓN
# --------------------------------

if not accel_df.empty:

    fig_accel = px.line(
        accel_df,
        x="_time",
        y="_value",
        color="_field",
        title="Aceleración MPU6050"
    )

    st.plotly_chart(
        fig_accel,
        use_container_width=True
    )

# --------------------------------
# MAGNITUD DEL MOVIMIENTO
# --------------------------------

if not accel_df.empty:

    accel_values = accel_df["_value"]

    magnitude = np.sqrt(accel_values**2)

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

# --------------------------------
# FOOTER
# --------------------------------

st.markdown("---")

st.caption("Proyecto IoT - Diseño Interactivo")
