# SensorLens — Sensor Data Analytics Platform

An interview-ready sensor data analytics platform that turns raw smart-home sensor readings into a validated dataset, relational MySQL tables, advanced SQL analytics, and an interactive Streamlit dashboard.

## What this project demonstrates

- Python data extraction, cleansing, transformation and validation
- ETL pipeline with rejected-record logging and quality reporting
- Relational database design in MySQL with primary/foreign keys, checks, and indexes
- SQL analytics using joins, CTEs, subqueries, CASE, window functions and views
- Rule-based anomaly detection using configurable temperature/humidity thresholds
- Interactive Streamlit KPIs, filters, trends, sensor activity and exports

## Architecture

```text
Raw CSV
   ↓
Python Extract
   ↓
Transform + Normalize
   ↓
Validation + Data Quality
   ↓
Clean CSV + Rejected Records
   ↓
MySQL Relational Database
   ↓
Advanced SQL / Views
   ↓
Streamlit Analytics Dashboard (SensorLens)
```

## Project structure

```text
.
├── backend/
│   ├── database.py
│   ├── preprocessing.py
│   └── etl/
│       ├── extract.py
│       ├── transform.py
│       ├── validate.py
│       └── pipeline.py
├── data/
│   ├── raw/dataset.csv
│   └── processed/
├── frontend/app.py
├── reports/data_quality_report.json
├── sql/
│   ├── schema.sql
│   ├── views.sql
│   └── analytics_queries.sql
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Dataset

The included raw dataset contains 201 sensor records, 24 unique sensor IDs, temperature and humidity measurements, states, and timestamps. The ETL pipeline derives a normalized timestamp and removes structurally invalid/duplicate records without inventing missing values.

## Actual ETL result

Run:

```bash
python backend/preprocessing.py
```

The pipeline writes:

- `data/processed/sensor_readings_clean.csv`
- `data/processed/rejected_records.csv`
- `reports/data_quality_report.json`

The quality report is generated from the current dataset; it should be rerun whenever the raw data changes.

## MySQL setup

Create the database and schema with `sql/schema.sql`, then configure environment variables using `.env.example`:

```text
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=sensorlens_db
```


To load cleaned data into MySQL from Python:

```python
from backend.database import load_to_mysql
load_to_mysql("data/processed/sensor_readings_clean.csv")
```

## Advanced SQL

`sql/analytics_queries.sql` contains examples of:

- CTEs
- subqueries
- joins
- `CASE`
- `ROW_NUMBER` / `RANK` / `DENSE_RANK`
- `LAG`
- running counts with window frames
- grouped analytics
- anomaly classification

`sql/views.sql` contains reusable reporting views for sensor summaries, daily metrics, and anomalies.

## Dashboard

Start the Streamlit application:

```bash
streamlit run frontend/app.py
```

Dashboard features:

- Reading count
- Sensor count
- Average temperature and humidity
- Rule-based anomaly count
- Sensor/date/state filters
- Temperature and humidity trends
- Sensor activity ranking
- State distribution
- Data-quality metrics
- Filtered-data CSV export

