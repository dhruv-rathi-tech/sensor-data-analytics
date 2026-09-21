import re
import pandas as pd

VALID_STATES = {"ON", "OFF", "OPEN", "CLOSE", "PRESENT", "ABSENT"}
SENSOR_PATTERN = re.compile(r"^[A-Z]\d{2}$")


def validate(df: pd.DataFrame):
    checks = {
        "missing_required_values": df[["Sensor_ID", "State", "Temp", "Humidity", "timestamp"]].isna().any(axis=1),
        "invalid_sensor_id": ~df["Sensor_ID"].fillna("").map(lambda x: bool(SENSOR_PATTERN.match(str(x)))),
        "invalid_state": ~df["State"].fillna("").isin(VALID_STATES),
        "temperature_out_of_range": (df["Temp"] < -20) | (df["Temp"] > 80),
        "humidity_out_of_range": (df["Humidity"] < 0) | (df["Humidity"] > 100),
    }
    reason = pd.Series("", index=df.index, dtype="string")
    for name, mask in checks.items():
        reason = reason.mask(mask & (reason == ""), name)
    invalid = reason != ""
    rejected = df.loc[invalid].copy()
    rejected["rejection_reason"] = reason.loc[invalid].values
    valid = df.loc[~invalid].copy()
    return valid, rejected, {name: int(mask.sum()) for name, mask in checks.items()}
