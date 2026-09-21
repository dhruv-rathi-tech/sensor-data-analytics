import os
from pathlib import Path
import mysql.connector

# Load .env file if available
_env_file = Path(__file__).resolve().parents[1] / ".env"
if _env_file.exists():
    for line in _env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())


def get_connection():
    """Create a MySQL connection from environment variables.

    Environment variables:
        MYSQL_HOST: Database server host (default: localhost)
        MYSQL_PORT: Database server port (default: 3306)
        MYSQL_USER: Database user (default: root)
        MYSQL_PASSWORD: User password (default: "")
        MYSQL_DATABASE: Database name (default: sensorlens_db)
    """
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "sensorlens_db"),
    )


def load_to_mysql(csv_path: str | Path) -> int:
    """Load cleaned sensor readings CSV into MySQL relational tables."""
    import pandas as pd

    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Drop child table first, then parent table
            cur.execute("DROP TABLE IF EXISTS sensor_readings")
            cur.execute("DROP TABLE IF EXISTS sensors")

            cur.execute("""
                CREATE TABLE sensors (
                    sensor_id VARCHAR(20) PRIMARY KEY,
                    first_seen DATETIME NOT NULL,
                    last_seen DATETIME NOT NULL,
                    reading_count INT NOT NULL,
                    active_state_count INT NOT NULL
                ) ENGINE=InnoDB
            """)

            cur.execute("""
                CREATE TABLE sensor_readings (
                    reading_id INT AUTO_INCREMENT PRIMARY KEY,
                    sensor_id VARCHAR(20) NOT NULL,
                    reading_ts DATETIME NOT NULL,
                    state VARCHAR(20) NOT NULL,
                    temperature DECIMAL(8,2) NOT NULL,
                    humidity DECIMAL(8,2) NOT NULL,
                    CONSTRAINT fk_sensor_readings_sensor FOREIGN KEY (sensor_id) REFERENCES sensors(sensor_id),
                    CONSTRAINT ck_sensor_temp CHECK (temperature BETWEEN -20 AND 80),
                    CONSTRAINT ck_sensor_humidity CHECK (humidity BETWEEN 0 AND 100)
                ) ENGINE=InnoDB
            """)

            cur.execute("CREATE INDEX idx_sensor_readings_sensor_ts ON sensor_readings(sensor_id, reading_ts)")
            cur.execute("CREATE INDEX idx_sensor_readings_ts ON sensor_readings(reading_ts)")

            summary = df.groupby("Sensor_ID").agg(
                first_seen=("timestamp", "min"),
                last_seen=("timestamp", "max"),
                reading_count=("Sensor_ID", "size"),
                active_state_count=("State", lambda s: int((s.isin(["ON", "OPEN", "PRESENT"])).sum())),
            ).reset_index()

            sensor_rows = [
                (
                    row.Sensor_ID,
                    row.first_seen.strftime("%Y-%m-%d %H:%M:%S.%f") if hasattr(row.first_seen, "strftime") else str(row.first_seen),
                    row.last_seen.strftime("%Y-%m-%d %H:%M:%S.%f") if hasattr(row.last_seen, "strftime") else str(row.last_seen),
                    int(row.reading_count),
                    int(row.active_state_count),
                )
                for row in summary.itertuples(index=False)
            ]

            cur.executemany(
                "INSERT INTO sensors (sensor_id, first_seen, last_seen, reading_count, active_state_count) "
                "VALUES (%s, %s, %s, %s, %s)",
                sensor_rows,
            )

            readings_rows = [
                (
                    r.Sensor_ID,
                    r.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f") if hasattr(r.timestamp, "strftime") else str(r.timestamp),
                    str(r.State),
                    float(r.Temp),
                    float(r.Humidity),
                )
                for r in df.itertuples(index=False)
            ]

            cur.executemany(
                "INSERT INTO sensor_readings (sensor_id, reading_ts, state, temperature, humidity) "
                "VALUES (%s, %s, %s, %s, %s)",
                readings_rows,
            )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return len(df)


# Alias for backward compatibility
load_to_database = load_to_mysql

