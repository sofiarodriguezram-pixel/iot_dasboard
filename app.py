import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from influxdb_client import InfluxDBClient

# ======================================================
# CONFIGURACIÓN DE LA PÁGINA
# ======================================================

st.set_page_config(
    page_title="Wellness Pod Dashboard",
    page_icon="🌿",
    layout="wide"
)

# ======================================================
# ESTILOS PERSONALIZADOS
# ======================================================

st.markdown("""
<style>

/* Fondo general */
.stApp {
    background-color: #f5f7fb;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e5e7eb;
}

/* Títulos */
h1, h2, h3 {
    color: #111827;
}

/* Texto */
p, label, div {
    color: #374151;
}

/* Cards métricas */
[data-testid="metric-container"] {
    background-color: white;
    border: 1px solid #e5e7eb;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
}

/* Alertas */
.stAlert {
    border-radius: 15px;
}

/* Tablas */
[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 15px;
    border: 1px solid #e5e7eb;
}

/* Botones */
.stButton > button {
    background-color: #22c55e;
    color: white;
    border-radius: 10px;
    border: none;
}

/* Sidebar títulos */
.sidebar-title {
    font-size: 20px;
    font-weight: bold;
    color: #111827;
}

/* Caja estado ambiente */
.status-box {
    background-color: #ecfdf5;
    border: 1px solid #bbf7d0;
    padding: 20px;
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER
# ======================================================

col_header1, col_header2 = st.columns([4,1])

with col_header1:
    st.title("🌿 Wellness Pod Dashboard")
    st.markdown(
        "### Monitoreo ambiental y movimiento en tiempo real"
    )

with col_header2:
    st.markdown("""
    <div style="
        background:white;
        padding:15px;
        border-radius:15px;
        border:1px solid #e5e7eb;
        text-align:center;
        margin-top:20px;
    ">
        <p style="margin:0;font-size:14px;">Estado</p>
        <h4 style="color:#22c55e;">● En vivo</h4>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.markdown(
    '<p class="sidebar-title">⚙ Panel de Control</p>',
    unsafe_allow_html=True
)

mode = st.sidebar.selectbox(
    "Modo del espacio",
    [
        "Relajación",
        "Trabajo",
        "Concentración"
    ]
)

ideal_temp = st.sidebar.slider(
    "Temperatura ideal (°C)",
    15,
    35,
    24
)

time_range = st.sidebar.selectbox(
    "Rango de tiempo",
    [
        "-30m",
        "-1h",
        "-6h",
        "-12h"
    ]
)

alerts = st.sidebar.toggle(
    "Activar alertas",
    value=True
)

st.sidebar.markdown("---")

# ======================================================
# CONEXIÓN INFLUXDB
# ======================================================

url = "https://us-east-1-1.aws.cloud2.influxdata.com"

token = "JoKdx3OFaBCFPmYQgiVWE8hjrtJ0lDkjwWZzT9djWJlvg98rtTgF9iRgKhQtAkKIA2UQsU6zsrJlv1BH6lfsVw=="

org = "miguelcmo"

bucket = "iot_telemetry_data"

client = InfluxDBClient(
    url=url,
    token=token,
    org=org
)

query_api = client.query_api()

# ======================================================
# CONSULTA TEMPERATURA
# ======================================================

temp_query = f'''
from(bucket: "{bucket}")
  |> range(start: {time_range})
  |> filter(fn: (r) => r._measurement == "environment")
  |> filter(fn: (r) => r._field == "temperature")
'''

temp_df = query_api.query_data_frame(temp_query)

# ======================================================
# CONSULTA HUMEDAD
# ======================================================

humidity_query = f'''
from(bucket: "{bucket}")
  |> range(start: {time_range})
  |> filter(fn: (r) => r._measurement == "environment")
  |> filter(fn: (r) => r._field == "humidity")
'''

humidity_df = query_api.query_data_frame(humidity_query)

# ======================================================
# CONSULTA MPU6050
# ======================================================

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

# ======================================================
# VALORES ACTUALES
# ======================================================

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

movement_state = "Movimiento Bajo"

avg_accel = 0

if not accel_df.empty:

    avg_accel = accel_df["_value"].mean()

    if avg_accel > 1.5:
        movement_state = "Movimiento Alto"

# ======================================================
# ESTADO GENERAL
# ======================================================

comfort = "Espacio óptimo"

if latest_temp > ideal_temp + 5:
    comfort = "Espacio caluroso"

elif latest_temp < ideal_temp - 5:
    comfort = "Espacio frío"

# ======================================================
# MÉTRICAS
# ======================================================

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

st.markdown("")

# ======================================================
# ALERTAS
# ======================================================

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
            "✅ Ambiente estable"
        )

# ======================================================
# GRÁFICAS
# ======================================================

graph_col1, graph_col2 = st.columns(2)

# TEMPERATURA
with graph_col1:

    if not temp_df.empty:

        fig_temp = px.line(
            temp_df,
            x="_time",
            y="_value",
            title="Temperatura (°C)"
        )

        fig_temp.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font_color="#111827"
        )

        st.plotly_chart(
            fig_temp,
            use_container_width=True
        )

# HUMEDAD
with graph_col2:

    if not humidity_df.empty:

        fig_humidity = px.line(
            humidity_df,
            x="_time",
            y="_value",
            title="Humedad (%)"
        )

        fig_humidity.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font_color="#111827"
        )

        st.plotly_chart(
            fig_humidity,
            use_container_width=True
        )

# ======================================================
# SEGUNDA FILA
# ======================================================

graph_col3, graph_col4 = st.columns(2)

# ACELERACIÓN
with graph_col3:

    if not accel_df.empty:

        fig_accel = px.line(
            accel_df,
            x="_time",
            y="_value",
            color="_field",
            title="Aceleración MPU6050"
        )

        fig_accel.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font_color="#111827"
        )

        st.plotly_chart(
            fig_accel,
            use_container_width=True
        )

# MAGNITUD
with graph_col4:

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

        fig_mag.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font_color="#111827"
        )

        st.plotly_chart(
            fig_mag,
            use_container_width=True
        )

# ======================================================
# TABLA
# ======================================================

st.markdown("## 📋 Datos recientes")

if not temp_df.empty:

    recent_data = temp_df[
        ["_time", "_value"]
    ].tail(10)

    recent_data.columns = [
        "Tiempo",
        "Temperatura"
    ]

    st.dataframe(
        recent_data,
        use_container_width=True
    )

# ======================================================
# SIDEBAR ESTADO
# ======================================================

st.sidebar.markdown("""
<div class="status-box">
    <h4 style="color:#16a34a;">
        🌿 Estado del ambiente
    </h4>

    <p>
        El sistema detecta un ambiente estable y adecuado
        para actividades de concentración y bienestar.
    </p>
</div>
""", unsafe_allow_html=True)

# ======================================================
# FOOTER
# ======================================================

st.markdown("---")

st.markdown(
    """
    <center>
    <p style="color:#6b7280;">
        Proyecto IoT · Diseño Interactivo · Wellness Pod
    </p>
    </center>
    """,
    unsafe_allow_html=True
)
