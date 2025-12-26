import argparse
import datetime as dt
import time
from dataclasses import dataclass
from typing import List

import numpy as np
import requests


"""
Sensor simulator for generating realistic sensor data.
Generates moisture, temperature, and humidity values and sends them to the Django API.
"""


@dataclass
class SimulatorConfig:
    api_base_url: str
    access_token: str
    plot_ids: List[int]
    interval_seconds: int = 10
    steps: int = 30
    anomaly_ratio: float = 0.3


def generate_baseline_values(step: int, inject_anomaly: bool = False) -> dict:
    """Generate realistic sensor values with diurnal temperature cycle."""
    hour = (step % 24)
    
    base_temp = 18 + 10 * np.maximum(0, (1 - np.abs(hour - 12) / 12))
    temperature = base_temp + np.random.normal(0, 1.0)
    moisture = 60 + np.random.normal(0, 5.0)
    humidity = 70 - (temperature - 18) + np.random.normal(0, 5.0)

    if inject_anomaly:
        anomaly_type = np.random.choice(["low_moisture", "high_temp", "low_temp", "low_humidity", "high_humidity"])
        
        if anomaly_type == "low_moisture":
            moisture = np.random.uniform(10, 35)
        elif anomaly_type == "high_temp":
            temperature = np.random.uniform(32, 42)
        elif anomaly_type == "low_temp":
            temperature = np.random.uniform(5, 10)
        elif anomaly_type == "low_humidity":
            humidity = np.random.uniform(10, 30)
        elif anomaly_type == "high_humidity":
            humidity = np.random.uniform(85, 95)

    return {
        "moisture": round(float(np.clip(moisture, 5, 95)), 2),
        "temperature": round(float(np.clip(temperature, 5, 45)), 2),
        "humidity": round(float(np.clip(humidity, 10, 95)), 2),
    }


def post_reading(config: SimulatorConfig, plot_id: int, sensor_type: str, value: float):
    url = f"{config.api_base_url.rstrip('/')}/api/sensor-readings/"
    timestamp = dt.datetime.utcnow().isoformat() + "Z"
    payload = {
        "plot": plot_id,
        "timestamp": timestamp,
        "sensor_type": sensor_type,
        "value": value,
        "source": "simulator",
    }
    headers = {
        "Authorization": f"Bearer {config.access_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers, timeout=10)
    if response.status_code not in (200, 201):
        print(f"[ERROR] Failed to send {sensor_type} reading for plot {plot_id}: "
              f"{response.status_code} {response.text}")
    else:
        print(f"[OK] {sensor_type}={value} for plot {plot_id} at {timestamp}")


def run_simulation(config: SimulatorConfig):
    print("Starting sensor simulator...")
    print(f"API base URL: {config.api_base_url}")
    print(f"Plots: {config.plot_ids}")
    print(f"Interval: {config.interval_seconds}s, Steps: {config.steps}")
    print(f"Anomaly ratio: {config.anomaly_ratio*100:.0f}%")

    for step in range(config.steps):
        inject_anomaly = np.random.random() < config.anomaly_ratio
        values = generate_baseline_values(step, inject_anomaly)

        for plot_id in config.plot_ids:
            post_reading(config, plot_id, "moisture", values["moisture"])
            post_reading(config, plot_id, "temperature", values["temperature"])
            post_reading(config, plot_id, "humidity", values["humidity"])

        if step < config.steps - 1:
            time.sleep(config.interval_seconds)

    print("Simulation finished.")


def parse_args() -> SimulatorConfig:
    parser = argparse.ArgumentParser(
        description="Simple sensor simulator for the crop monitoring project."
    )
    parser.add_argument(
        "--api-base-url",
        default="http://127.0.0.1:8000",
        help="Base URL of the Django API (default: http://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--access-token",
        required=True,
        help="JWT access token for authentication (use /api/auth/login/).",
    )
    parser.add_argument(
        "--plots",
        required=True,
        help="Comma-separated list of plot IDs to simulate (e.g. 1,2,3).",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Seconds between steps (default: 10).",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=10,
        help="Number of simulation steps (default: 10).",
    )
    parser.add_argument(
        "--anomaly-ratio",
        type=float,
        default=0.3,
        help="Ratio of readings that should be anomalies (0.0-1.0, default: 0.3).",
    )

    args = parser.parse_args()
    plot_ids = [int(p.strip()) for p in args.plots.split(",") if p.strip()]

    return SimulatorConfig(
        api_base_url=args.api_base_url,
        access_token=args.access_token,
        plot_ids=plot_ids,
        interval_seconds=args.interval,
        steps=args.steps,
        anomaly_ratio=args.anomaly_ratio,
    )


if __name__ == "__main__":
    config = parse_args()
    run_simulation(config)


