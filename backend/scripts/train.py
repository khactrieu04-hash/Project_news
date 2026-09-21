import argparse
import asyncio
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.clients import get_weather_history
from app.models import train_forecast_models


TRAINING_LOCATIONS = {
    "ha_noi": (21.0278, 105.8342),
    "da_nang": (16.0471, 108.2068),
    "ho_chi_minh": (10.8231, 106.6297),
    "can_tho": (10.0452, 105.7469),
    "hai_phong": (20.8449, 106.6881),
    "khanh_hoa": (12.2388, 109.1967),
}


async def fetch_location_history(location: tuple[str, tuple[float, float]], days: int) -> pd.DataFrame:
    location_name, (latitude, longitude) = location
    payload = await get_weather_history(latitude, longitude, days)
    frame = pd.DataFrame(payload["hourly"])
    frame["location"] = location_name
    frame["time"] = pd.to_datetime(frame["time"])
    return frame


def build_supervised_data(frames: list[pd.DataFrame]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    base_columns = [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "pressure_msl",
        "wind_speed_10m",
        "wind_gusts_10m",
        "weather_code",
    ]
    feature_frames = []
    for frame in frames:
        prepared = frame.sort_values("time").copy()
        for column in base_columns:
            prepared[column] = pd.to_numeric(prepared[column], errors="coerce")
            for lag in (1, 3, 6, 12, 24):
                prepared[f"{column}_lag_{lag}"] = prepared.groupby("location")[column].shift(lag)
            prepared[f"{column}_rolling_6"] = prepared.groupby("location")[column].transform(
                lambda values: values.rolling(6, min_periods=6).mean()
            )
        prepared["hour_sin"] = np.sin(2 * np.pi * prepared["time"].dt.hour / 24)
        prepared["hour_cos"] = np.cos(2 * np.pi * prepared["time"].dt.hour / 24)
        prepared["weekday_sin"] = np.sin(2 * np.pi * prepared["time"].dt.dayofweek / 7)
        prepared["weekday_cos"] = np.cos(2 * np.pi * prepared["time"].dt.dayofweek / 7)
        prepared["target_temperature"] = prepared.groupby("location")["temperature_2m"].shift(-1)
        prepared["target_precipitation"] = prepared.groupby("location")["precipitation"].shift(-1)
        prepared["target_wind_gust"] = prepared.groupby("location")["wind_gusts_10m"].shift(-1)
        prepared["target_storm"] = (
            prepared.groupby("location")["weather_code"].shift(-1).fillna(0).astype(int) >= 95
        ).astype(int)
        feature_frames.append(prepared)

    combined = pd.concat(feature_frames, ignore_index=True).sort_values(["time", "location"])
    ignored_columns = {"time", "location", "target_temperature", "target_precipitation", "target_wind_gust", "target_storm"}
    feature_columns = [column for column in combined.columns if column not in ignored_columns]
    target_columns = {
        "temperature": "target_temperature",
        "precipitation": "target_precipitation",
        "wind_gust": "target_wind_gust",
        "storm": "target_storm",
    }
    valid = combined[feature_columns + list(target_columns.values())].notna().all(axis=1)
    clean = combined.loc[valid]
    features = clean[feature_columns].to_numpy(dtype=float)
    targets = {name: clean[column].to_numpy(dtype=float if name != "storm" else int) for name, column in target_columns.items()}
    return features, targets


async def main(days: int, location_names: list[str]) -> None:
    selected = [(name, TRAINING_LOCATIONS[name]) for name in location_names]
    frames = []
    for location in selected:
        frames.append(await fetch_location_history(location, days))
        await asyncio.sleep(1)
    features, targets = build_supervised_data(frames)
    metrics = train_forecast_models(features, targets)
    metrics["days"] = days
    metrics["locations"] = location_names
    metrics["feature_count"] = features.shape[1]
    metrics_path = Path(__file__).resolve().parents[1] / "models" / "weather_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train time-aware weather and storm forecast models")
    parser.add_argument("--days", type=int, default=730)
    parser.add_argument("--locations", nargs="+", choices=sorted(TRAINING_LOCATIONS), default=list(TRAINING_LOCATIONS))
    arguments = parser.parse_args()
    asyncio.run(main(arguments.days, arguments.locations))
