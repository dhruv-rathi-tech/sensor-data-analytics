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
    page_title="SensorLens — Sensor Data Analytics Platform",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session state initialization
if "sql_query" not in st.session_state:
    st.session_state["sql_query"] = "SELECT * FROM processed_data LIMIT 10"
if "last_df" not in st.session_state:
    st.session_state["last_df"] = None

# --- MODERN ENTERPRISE STYLING ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

code, pre, .stCodeBlock {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Header Container */
.header-box {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    padding: 28px 24px;
    border-radius: 12px;
    text-align: center;
    border: 1px solid #334155;
    box-shadow: 0 4px 24px -2px rgba(0, 0, 0, 0.3);
    margin-bottom: 24px;
}

.project-badge {
    display: inline-block;
    background: rgba(56, 189, 248, 0.1);
    color: #38bdf8;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 9999px;
    border: 1px solid rgba(56, 189, 248, 0.25);
    margin-bottom: 10px;
}

.project-title {
    font-size: 32px;
    font-weight: 800;
    color: #f8fafc;
    letter-spacing: -0.5px;
    margin-bottom: 8px;
}

.project-sub {
    font-size: 14px;
    color: #94a3b8;
    margin: 4px 0;
}

/* Clean UI Buttons */
.stButton button {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #334155;
    font-weight: 500;
    border-radius: 6px;
    transition: all 0.15s ease;
}
.stButton button:hover {
    background-color: #334155;
    border-color: #475569;
    color: #ffffff;
}
.stButton button[kind="primary"] {
    background-color: #0284c7;
    border-color: #0369a1;
    color: #ffffff;
}
.stButton button[kind="primary"]:hover {
    background-color: #0369a1;
    border-color: #075985;
}
</style>

<div class="header-box">
    <div class="project-badge">Sensor Data Analytics Platform</div>
    <div class="project-title">📡 SensorLens</div>
    <p class="project-sub">ETL Pipeline • MySQL Relational Analytics • Interactive Streamlit Reporting</p>
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

