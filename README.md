# 🌿 Wellness Pod Dashboard

## Descripción

Wellness Pod es un sistema IoT diseñado para monitorear condiciones ambientales y movimiento en tiempo real utilizando sensores conectados a InfluxDB y visualizados mediante Streamlit.

El sistema permite interpretar el estado de confort de un espacio mediante datos de temperatura, humedad y movimiento detectado.

---

## Caso de uso

El proyecto propone una estación de bienestar ambiental capaz de detectar cambios en las condiciones del entorno y visualizar información relevante para el usuario.

La plataforma interpreta:
- temperatura ambiental,
- humedad,
- estabilidad del espacio,
- vibraciones o movimiento.

Esto permite identificar ambientes cómodos, inestables o potencialmente estresantes.

---

## Tecnologías utilizadas

- Python
- Streamlit
- InfluxDB
- Plotly
- Pandas

---

## Sensores utilizados

### DHT22
- Temperatura
- Humedad

### MPU6050
- Aceleración
- Movimiento

---

## Funcionalidades

- Dashboard en tiempo real
- Monitoreo ambiental
- Alertas automáticas
- Visualización de datos históricos
- Interpretación del estado del espacio

---

## Instalación

```bash
pip install -r requirements.txt
```

---

## Ejecución

```bash
streamlit run app.py
```
