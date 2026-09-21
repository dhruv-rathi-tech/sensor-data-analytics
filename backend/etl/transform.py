import numpy as np
import pandas as pd

CLEAN_COLUMNS = ["Date", "Time", "Sensor_ID", "State", "Temp", "Humidity"]


def transform(df: pd.DataFrame) -> pd.DataFrame:
    # Detect rows with extraneous non-empty data beyond the 6 standard columns
    has_extra = pd.Series(False, index=df.index)
    if df.shape[1] > len(CLEAN_COLUMNS):
        extras = df.iloc[:, len(CLEAN_COLUMNS):].copy()
        extras = extras.replace(r"^\s*$", np.nan, regex=True)
        has_extra = extras.notna().any(axis=1)

    out = df.iloc[:, :len(CLEAN_COLUMNS)].copy()
    out.columns = CLEAN_COLUMNS
    out["has_extraneous_columns"] = has_extra

    for col in ["Sensor_ID", "State"]:
        out[col] = out[col].astype("string").str.strip().str.upper()
    out["Temp"] = pd.to_numeric(out["Temp"], errors="coerce")
    out["Humidity"] = pd.to_numeric(out["Humidity"], errors="coerce")
    out["timestamp"] = pd.to_datetime(
        out["Date"].astype(str).str.strip() + " " + out["Time"].astype(str).str.strip(),
        format="%y-%m-%d %H:%M:%S.%f",
        errors="coerce",
    )
    out["reading_date"] = out["timestamp"].dt.date
    out["reading_hour"] = out["timestamp"].dt.hour
    out["temp_humidity_gap"] = (out["Temp"] - out["Humidity"]).abs()
    return out

