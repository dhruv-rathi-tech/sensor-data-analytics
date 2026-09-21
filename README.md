# SensorLens — Sensor Data Analytics Platform

**SensorLens** is an end-to-end IoT sensor data analytics and operational monitoring platform. It ingests raw telemetry readings from smart-home environmental and motion sensors, performs automated data cleansing and schema validation, loads structured data into a relational MySQL store, and delivers real-time operational insights through interactive dashboards and a live SQL query console.

---

## Key Features

- **Automated Data Processing Pipeline (ETL)**: Cleanses and transforms raw multi-sensor telemetry, normalizes timestamps, enforces strict domain validation rules, and logs malformed/rejected records with granular rejection reasons.
- **Relational Data Architecture (MySQL 8.0)**: Normalized relational schema (`sensors`, `sensor_readings`) equipped with primary keys, foreign key constraints, value range checks (`temperature`, `humidity`), and composite time-series indexes for query optimization.
- **Advanced SQL Analytical Engine**: Implements complex analytical queries utilizing Common Table Expressions (CTEs), window functions (`DENSE_RANK`, `LAG`, running window frames), conditional aggregation (`CASE`), and analytical database views.
- **Interactive Web Interface (Streamlit)**:
  - **SQL Query Console**: Execute ad-hoc queries with execution timers, pre-built shortcuts, and CSV exports.
  - **Operational Telemetry Dashboard**: Real-time KPI scorecard, temperature/humidity trend charts, sensor activity distribution, and rule-based anomaly detection.
  - **Data Quality & Audit Console**: Transparent pipeline audit reporting, failure classification breakdown, and rejected record inspection.

---

## System Architecture

```text
┌─────────────────┐
│   Raw Telemetry │ (data/raw/dataset.csv)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Python Extract │ (backend/etl/extract.py)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Transform/Parse │ (backend/etl/transform.py)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Validation/DQ   │ (backend/etl/validate.py)
└────────┬────────┘
         ├───► [Rejected Records Log] (data/processed/rejected_records.csv)
         ├───► [Quality Audit Report] (reports/data_quality_report.json)
         │
         ▼
┌─────────────────┐
│ Clean Datasets  │ (data/processed/sensor_readings_clean.csv)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MySQL Database │ (`sensorlens_db` - Tables, Views, Indexes)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Streamlit UI    │ (Interactive SQL Console + Visual Dashboards)
└─────────────────┘
```

---

## Project Structure

```text
.
├── backend/
│   ├── database.py                 # MySQL connection pooling, DDL execution, and bulk loader
│   ├── preprocessing.py            # Standalone ETL pipeline entry point
│   └── etl/
│       ├── extract.py              # CSV ingestion and required column verification
│       ├── transform.py            # Timestamp derivation and type casting
│       ├── validate.py             # Schema integrity and domain boundary checks
│       └── pipeline.py             # Pipeline orchestrator and metrics aggregator
├── data/
│   ├── raw/
│   │   └── dataset.csv             # Raw sensor telemetry
│   └── processed/
│       ├── sensor_readings_clean.csv # Validated sensor readings
│       └── rejected_records.csv    # Records rejected by validation rules
├── frontend/
│   └── app.py                      # Streamlit application (SQL Studio + Visual Analytics)
├── reports/
│   └── data_quality_report.json    # Pipeline execution metrics and quality scorecard
├── sql/
│   ├── schema.sql                  # MySQL table definitions, constraints, and indexes
│   ├── views.sql                   # Operational database views (summary, daily, anomalies)
│   └── analytics_queries.sql       # Window functions, CTEs, and operational SQL queries
├── .env.example                    # Database environment variable template
├── .gitignore                      # Git exclusion rules (credentials, caches, virtualenvs)
├── requirements.txt                # Python package dependencies
└── README.md                       # Project documentation
```

---

## Getting Started

### 1. Prerequisites

- **Python**: 3.10 or higher
- **MySQL Server**: 8.0 or higher

### 2. Environment Setup

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/dhruv-rathi-tech/sensor-data-analytics.git
cd sensor-data-analytics
python -m pip install -r requirements.txt
```

### 3. Database Configuration

Copy `.env.example` to `.env` and provide your MySQL connection parameters:

```bash
cp .env.example .env
```

Configure your `.env` file:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=sensorlens_db
```

Create the schema and views in MySQL:

```bash
mysql -u root -p sensorlens_db < sql/schema.sql
mysql -u root -p sensorlens_db < sql/views.sql
```

---

## Pipeline Execution

### 1. Run Data Validation & Cleansing (ETL)

Execute the pipeline to process raw records, enforce validation, and generate data quality reports:

```bash
python backend/preprocessing.py
```

- **Clean records output**: `data/processed/sensor_readings_clean.csv`
- **Audit trail output**: `data/processed/rejected_records.csv`
- **Quality metrics**: `reports/data_quality_report.json`

### 2. Populate MySQL Database

Load the validated dataset into MySQL:

```bash
python -c "from backend.database import load_to_mysql; load_to_mysql('data/processed/sensor_readings_clean.csv')"
```

---

## Launching the Dashboard

Start the Streamlit application:

```bash
streamlit run frontend/app.py
```

Access the dashboard in your browser at `http://localhost:8501`.

### Platform Modules:
1. **SQL Query Console**: Interactive query editor with syntax execution against MySQL tables (`processed_data`, `sensors`, `sensor_readings`, etc.), execution latency reporting, and CSV data export.
2. **Visual Analytics & Trends**: High-level KPIs, temperature and humidity time-series trends, sensor utilization distribution, operational state breakdown, and rule-based anomaly detection.
3. **Data Quality Audit**: Summary of source records, validation rule failure counts, and an interactive inspector for rejected data entries.

---

## Data Quality Assurance

The ingestion pipeline audits raw telemetry data for structural anomalies:

- **Source Telemetry Records**: 201
- **Validated Clean Records**: 148
- **Rejected Records**: 53
- **Data Quality Score**: **73.63%**

**Rejection Reason**: The raw sensor stream contains 53 rows with corrupted, unmapped trailing column data. Rather than silently dropping or fabricating data, SensorLens segregates these rows into `rejected_records.csv` for audit compliance.