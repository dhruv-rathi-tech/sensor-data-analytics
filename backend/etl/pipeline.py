from pathlib import Path
import json
import pandas as pd
from .extract import extract_csv
from .transform import transform
from .validate import validate

BASE_DIR = Path(__file__).resolve().parents[2]
RAW = BASE_DIR / "data" / "raw" / "dataset.csv"
PROCESSED = BASE_DIR / "data" / "processed" / "sensor_readings_clean.csv"
REJECTED = BASE_DIR / "data" / "processed" / "rejected_records.csv"
REPORT = BASE_DIR / "reports" / "data_quality_report.json"


def run_pipeline():
    raw = extract_csv(RAW)
    transformed = transform(raw)
    before_dedup = len(transformed)
    transformed = transformed.drop_duplicates(subset=["timestamp", "Sensor_ID", "State", "Temp", "Humidity"]).copy()
    duplicates_removed = before_dedup - len(transformed)
    valid, rejected, checks = validate(transformed)

    # Clean temporary helper columns from output
    if "has_extraneous_columns" in valid.columns:
        valid = valid.drop(columns=["has_extraneous_columns"])
    if "has_extraneous_columns" in rejected.columns:
        rejected = rejected.drop(columns=["has_extraneous_columns"])

    # Stable business-friendly ordering.
    valid = valid.sort_values("timestamp").reset_index(drop=True)
    valid.to_csv(PROCESSED, index=False)
    rejected.to_csv(REJECTED, index=False)


    quality = {
        "source_records": int(len(raw)),
        "duplicate_records_removed": int(duplicates_removed),
        "valid_records": int(len(valid)),
        "rejected_records": int(len(rejected)),
        "quality_score_pct": round((len(valid) / len(transformed) * 100) if len(transformed) else 0, 2),
        "unique_sensors": int(valid["Sensor_ID"].nunique()),
        "min_temperature": float(valid["Temp"].min()),
        "max_temperature": float(valid["Temp"].max()),
        "min_humidity": float(valid["Humidity"].min()),
        "max_humidity": float(valid["Humidity"].max()),
        "validation_failures": checks,
    }
    REPORT.write_text(json.dumps(quality, indent=2), encoding="utf-8")
    return quality


if __name__ == "__main__":
    print(json.dumps(run_pipeline(), indent=2))
