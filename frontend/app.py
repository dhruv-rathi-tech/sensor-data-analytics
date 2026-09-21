import json
import sys
import time
from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.database import get_connection

DATA_FILE = BASE_DIR / "data" / "processed" / "sensor_readings_clean.csv"
QUALITY_FILE = BASE_DIR / "reports" / "data_quality_report.json"


st.set_page_config(
    page_title="SensorLens — DBMS Project",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session state initialization
if "sql_query" not in st.session_state:
    st.session_state["sql_query"] = "SELECT * FROM processed_data LIMIT 10"
if "last_df" not in st.session_state:
    st.session_state["last_df"] = None
if "splash_shown" not in st.session_state:
    st.session_state["splash_shown"] = True
    time.sleep(1.2)

# --- SPLASH SCREEN AND THEME STYLING ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Orbitron:wght@600;800&family=Inter:wght@400;500;600;700&display=swap');

#splash-screen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #0b0c10, #1f2833);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 99999;
    color: #66fcf1;
    font-family: 'Anton', sans-serif;
    font-size: 64px;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 3px;
    text-shadow: 0 0 20px rgba(102, 252, 241, 0.6), 2px 2px 6px #ffcc00;
    animation: liftUp 0.8s ease-out forwards, fadeOut 0.5s ease forwards 1.2s;
    pointer-events: none;
}

@keyframes liftUp {
    0% { transform: translateY(30px); opacity: 0; }
    100% { transform: translateY(0); opacity: 1; }
}

@keyframes fadeOut {
    0% { opacity: 1; }
    100% { opacity: 0; display: none; visibility: hidden; }
}

/* Header Box */
.header-box {
    background: linear-gradient(135deg, #111422, #1f2538 50%, #2b1b3d);
    padding: 24px 20px;
    border-radius: 14px;
    text-align: center;
    border: 1px solid rgba(102, 252, 241, 0.2);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    margin-bottom: 24px;
    animation: zoomIn 1s ease-out forwards;
}

@keyframes zoomIn {
    0% { transform: scale(0.95); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}

.project-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 42px;
    font-weight: 800;
    color: #66fcf1;
    text-shadow: 0 0 15px rgba(102, 252, 241, 0.5), 2px 2px 8px #000000;
    margin-bottom: 8px;
    letter-spacing: 2px;
}

.project-sub {
    font-size: 15px;
    margin: 3px 0;
    font-family: 'Inter', sans-serif;
}

.label-text { color: #c5c6c7; font-weight: 600; }
.name-text { color: #ffd166; font-weight: 700; }
.id-text { color: #ffffff; font-weight: 500; }
.faculty-text { color: #06d6a0; font-weight: 700; }

/* Custom Buttons */
.stButton button {
    background: linear-gradient(135deg, #1f2833, #0b0c10);
    color: #66fcf1;
    border: 1px solid #45a29e;
    font-weight: 600;
    border-radius: 8px;
    transition: all 0.2s ease-in-out;
}
.stButton button:hover {
    background: linear-gradient(135deg, #45a29e, #66fcf1);
    color: #0b0c10;
    border-color: #66fcf1;
    box-shadow: 0 0 12px rgba(102, 252, 241, 0.5);
}
</style>

<div id="splash-screen">DATA VISUALISATION</div>

<div class="header-box">
    <div class="project-title">SENSORLENS — DBMS PROJECT</div>
    <p class="project-sub"><span class="label-text">Done by:</span></p>
    <p class="project-sub"><span class="name-text">Aman Gupta</span> — <span class="id-text">23BLC1161</span> &nbsp;|&nbsp; <span class="name-text">Dhruv Rathi</span> — <span class="id-text">23BLC1164</span></p>
    <p class="project-sub"><span class="label-text">Submitted to —</span> <span class="faculty-text">Dr. Sobitha Ahila</span></p>
</div>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])
    return df


@st.cache_data
def load_quality():
    return json.loads(QUALITY_FILE.read_text(encoding="utf-8"))


df = load_data()
quality = load_quality()

# --- SIDEBAR: QUERY SHORTCUTS & FILTERS ---
QUERY_SHORTCUTS = {
    "First 10 Rows": "SELECT * FROM processed_data ORDER BY Date_Col DESC, Time_Col DESC LIMIT 10",
    "Total No. of Records": "SELECT COUNT(*) AS total_records FROM processed_data",
    "Unique No. of Sensors": "SELECT COUNT(DISTINCT Sensor_ID) AS unique_sensors FROM processed_data",
    "Average Temperature": "SELECT ROUND(AVG(Temp), 2) AS avg_temp FROM processed_data",
    "Average Humidity": "SELECT ROUND(AVG(Humidity), 2) AS avg_humidity FROM processed_data",
    "Last Updated Timestamp": "SELECT MAX(CONCAT(Date_Col, ' --- ', Time_Col)) AS last_update FROM processed_data",
    "Top 10 Sensors by Usage": "SELECT Sensor_ID, COUNT(*) AS usage_count FROM processed_data GROUP BY Sensor_ID ORDER BY COUNT(*) DESC LIMIT 10",
    "Top 10 Sensors by Latest Activity": "SELECT Sensor_ID, MAX(CONCAT(Date_Col, ' --- ', Time_Col)) AS last_seen FROM processed_data GROUP BY Sensor_ID ORDER BY MAX(CONCAT(Date_Col, ' ', Time_Col)) DESC LIMIT 10",
    "Sensor Summary (Sensors Table)": "SELECT sensor_id, reading_count, active_state_count, first_seen, last_seen FROM sensors ORDER BY reading_count DESC LIMIT 10",
    "Daily Metrics (View)": "SELECT * FROM vw_daily_sensor_metrics",
    "Rule-based Anomalies (View)": "SELECT * FROM vw_anomalies LIMIT 15",
}

with st.sidebar:
    st.header("📌 Query Shortcuts")
    st.caption("Click any shortcut to load into the SQL console:")
    for label, query in QUERY_SHORTCUTS.items():
        if st.button(label, key=f"btn_{label}"):
            st.session_state["sql_query"] = query

    st.divider()
    st.header("📊 Visual Filters")
    selected_sensors = st.multiselect("Sensor", sorted(df["Sensor_ID"].unique()), key="filter_sensors")
    selected_states = st.multiselect("State", sorted(df["State"].unique()), key="filter_states")
    min_date, max_date = df["timestamp"].min().date(), df["timestamp"].max().date()
    date_range = st.date_input("Date range", (min_date, max_date), min_value=min_date, max_value=max_date)

    st.divider()
    st.caption("🟢 **Database**: MySQL 8.0 (`sensorlens_db`)")


# --- MAIN INTERFACE: TABS ---
tab_sql, tab_analytics, tab_quality = st.tabs([
    "💻 SQL Query Console",
    "📊 Visual Analytics & Trends",
    "🛡️ Data Quality & Audit",
])

# ==========================================
# TAB 1: SQL QUERY CONSOLE
# ==========================================
with tab_sql:
    st.subheader("💻 Interactive SQL Query Runner")
    st.caption("Execute direct SQL queries against the live MySQL database (`processed_data`, `sensors`, `sensor_readings`, `vw_daily_sensor_metrics`, `vw_anomalies`).")

    sql_query = st.text_area(
        "Enter Your SQL Query:",
        value=st.session_state["sql_query"],
        height=130,
        key="sqlQueryBox",
    )

    c_run, c_export, c_clear = st.columns([1.2, 1.2, 5])
    with c_run:
        run_query = st.button("▶ Run Query", type="primary")
    with c_export:
        export_placeholder = st.empty()

    if run_query:
        try:
            t0 = time.time()
            conn = get_connection()
            query_df = pd.read_sql(sql_query, conn)
            conn.close()
            elapsed = time.time() - t0

            st.session_state["last_df"] = query_df
            st.success(f"✅ Query executed successfully in {elapsed:.3f}s — returned **{len(query_df)}** rows")
            st.dataframe(query_df, use_container_width=True)
        except Exception as e:
            st.error(f"❌ SQL Execution Error: {e}")
    elif st.session_state["last_df"] is not None:
        st.info(f"Displaying last query result ({len(st.session_state['last_df'])} rows):")
        st.dataframe(st.session_state["last_df"], use_container_width=True)

    if st.session_state["last_df"] is not None and not st.session_state["last_df"].empty:
        csv_data = st.session_state["last_df"].to_csv(index=False).encode("utf-8")
        with c_export:
            st.download_button("📥 Export CSV", data=csv_data, file_name="query_results.csv", mime="text/csv")


# ==========================================
# TAB 2: VISUAL ANALYTICS & TRENDS
# ==========================================
with tab_analytics:
    filtered = df.copy()
    if selected_sensors:
        filtered = filtered[filtered.Sensor_ID.isin(selected_sensors)]
    if selected_states:
        filtered = filtered[filtered.State.isin(selected_states)]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
        filtered = filtered[(filtered.timestamp >= start) & (filtered.timestamp < end)]

    anomalies = filtered[(filtered.Temp < 10) | (filtered.Temp > 35) | (filtered.Humidity < 30) | (filtered.Humidity > 70)]

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Readings", f"{len(filtered):,}")
    k2.metric("Sensors", f"{filtered.Sensor_ID.nunique():,}")
    k3.metric("Avg Temperature", f"{filtered.Temp.mean():.1f} °C" if len(filtered) else "N/A")
    k4.metric("Avg Humidity", f"{filtered.Humidity.mean():.1f} %" if len(filtered) else "N/A")
    k5.metric("Anomalies", f"{len(anomalies):,}")

    st.divider()

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Temperature Trend")
        temp = filtered.set_index("timestamp")["Temp"].sort_index()
        st.line_chart(temp, height=280)
    with col_r:
        st.subheader("Humidity Trend")
        hum = filtered.set_index("timestamp")["Humidity"].sort_index()
        st.line_chart(hum, height=280)

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.subheader("Sensor Activity (Top 10)")
        activity = filtered.groupby("Sensor_ID").size().sort_values(ascending=False).head(10)
        st.bar_chart(activity, height=280)
    with col_b2:
        st.subheader("State Distribution")
        state_counts = filtered["State"].value_counts()
        st.bar_chart(state_counts, height=280)

    st.subheader("⚠️ Rule-based Anomalies")
    if anomalies.empty:
        st.success("No anomalies found matching current filters.")
    else:
        anomaly_view = anomalies[["timestamp", "Sensor_ID", "State", "Temp", "Humidity"]].copy()
        anomaly_view["anomaly_type"] = anomaly_view.apply(
            lambda r: "Temperature outlier" if r.Temp < 10 or r.Temp > 35 else "Humidity outlier", axis=1
        )
        st.dataframe(anomaly_view, use_container_width=True, hide_index=True)

    st.subheader("Filtered Readings")
    st.dataframe(filtered[["timestamp", "Sensor_ID", "State", "Temp", "Humidity"]], use_container_width=True, hide_index=True)
    filtered_csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Filtered Readings", filtered_csv, "filtered_sensor_readings.csv", "text/csv")


# ==========================================
# TAB 3: DATA QUALITY & AUDIT
# ==========================================
with tab_quality:
    st.subheader("🛡️ Data Quality Audit")
    st.caption("Verification and audit metrics generated from raw dataset ingestion and validation pipeline.")

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Quality Score", f"{quality['quality_score_pct']:.2f}%")
    q2.metric("Valid Clean Records", f"{quality['valid_records']:,}")
    q3.metric("Rejected Records", f"{quality['rejected_records']:,}")
    q4.metric("Source Raw Records", f"{quality['source_records']:,}")

    st.write("### Validation Failure Breakdown")
    fail_df = pd.DataFrame(
        list(quality.get("validation_failures", {}).items()),
        columns=["Check Rule", "Failure Count"],
    )
    st.dataframe(fail_df, use_container_width=True, hide_index=True)

    rejected_file = BASE_DIR / "data" / "processed" / "rejected_records.csv"
    if rejected_file.exists():
        st.write("### Rejected Records Inspection")
        rej_df = pd.read_csv(rejected_file)
        st.dataframe(rej_df, use_container_width=True, hide_index=True)
        rej_csv = rej_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Rejected Records Log", rej_csv, "rejected_records.csv", "text/csv")

