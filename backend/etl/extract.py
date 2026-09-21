from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = ["Date", "Time", "Sensor_ID", "State", "Temp", "Humidity"]


def extract_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    df = pd.read_csv(path)
    if len(df.columns) < len(REQUIRED_COLUMNS):
        raise ValueError(f"Expected at least {len(REQUIRED_COLUMNS)} columns, found {len(df.columns)}")
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df
