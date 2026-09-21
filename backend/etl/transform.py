import pandas as pd

CLEAN_COLUMNS = ["Date", "Time", "Sensor_ID", "State", "Temp", "Humidity"]


def transform(df: pd.DataFrame) -> pd.DataFrame:
    out = df[CLEAN_COLUMNS].copy()
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
