from pathlib import Path
import json
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "processed" / "sensor_readings_clean.csv"
QUALITY_FILE = BASE_DIR / "reports" / "data_quality_report.json"

st.set_page_config(page_title="SensorLens — Sensor Data Analytics Platform", page_icon="📡", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])
    return df

@st.cache_data
def load_quality():
    return json.loads(QUALITY_FILE.read_text(encoding="utf-8"))

st.title("📡 SensorLens — Sensor Data Analytics Platform")
st.caption("SensorLens: ETL → Data Quality → Relational Analytics → Interactive Reporting")


df = load_data()
quality = load_quality()

with st.sidebar:
    st.header("Filters")
    selected_sensors = st.multiselect("Sensor", sorted(df["Sensor_ID"].unique()))
    selected_states = st.multiselect("State", sorted(df["State"].unique()))
    min_date, max_date = df["timestamp"].min().date(), df["timestamp"].max().date()
    date_range = st.date_input("Date range", (min_date, max_date), min_value=min_date, max_value=max_date)

filtered = df.copy()
if selected_sensors:
    filtered = filtered[filtered.Sensor_ID.isin(selected_sensors)]
if selected_states:
    filtered = filtered[filtered.State.isin(selected_states)]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
    filtered = filtered[(filtered.timestamp >= start) & (filtered.timestamp < end)]

anomalies = filtered[(filtered.Temp < 10) | (filtered.Temp > 35) | (filtered.Humidity < 30) | (filtered.Humidity > 70)]
active_states = {"ON", "OPEN", "PRESENT"}
active_readings = filtered[filtered.State.isin(active_states)]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Readings", f"{len(filtered):,}")
c2.metric("Sensors", f"{filtered.Sensor_ID.nunique():,}")
c3.metric("Avg Temperature", f"{filtered.Temp.mean():.1f} °C")
c4.metric("Avg Humidity", f"{filtered.Humidity.mean():.1f} %")
c5.metric("Anomalies", f"{len(anomalies):,}")

st.divider()

left, right = st.columns(2)
with left:
    st.subheader("Temperature Trend")
    temp = filtered.set_index("timestamp")["Temp"].sort_index()
    st.line_chart(temp, height=300)
with right:
    st.subheader("Humidity Trend")
    hum = filtered.set_index("timestamp")["Humidity"].sort_index()
    st.line_chart(hum, height=300)

left, right = st.columns(2)
with left:
    st.subheader("Sensor Activity")
    activity = filtered.groupby("Sensor_ID").size().sort_values(ascending=False).head(10)
    st.bar_chart(activity, height=300)
with right:
    st.subheader("State Distribution")
    state_counts = filtered["State"].value_counts()
    st.bar_chart(state_counts, height=300)

st.subheader("Data Quality")
q1, q2, q3, q4 = st.columns(4)
q1.metric("Quality Score", f"{quality['quality_score_pct']:.2f}%")
q2.metric("Valid Records", f"{quality['valid_records']:,}")
q3.metric("Rejected Records", f"{quality['rejected_records']:,}")
q4.metric("Duplicates Removed", f"{quality['duplicate_records_removed']:,}")

st.subheader("Anomalies")
if anomalies.empty:
    st.success("No rule-based anomalies match the current filters.")
else:
    anomaly_view = anomalies[["timestamp", "Sensor_ID", "State", "Temp", "Humidity"]].copy()
    anomaly_view["anomaly_type"] = anomaly_view.apply(
        lambda r: "Temperature outlier" if r.Temp < 10 or r.Temp > 35 else "Humidity outlier", axis=1
    )
    st.dataframe(anomaly_view, use_container_width=True, hide_index=True)

st.subheader("Filtered Readings")
st.dataframe(filtered[["timestamp", "Sensor_ID", "State", "Temp", "Humidity"]], use_container_width=True, hide_index=True)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Filtered Readings", csv, "filtered_sensor_readings.csv", "text/csv")
