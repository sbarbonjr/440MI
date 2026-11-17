#!/usr/bin/env python3
"""HTTP simulator for the pasteurization classroom case.

The public interface is deliberately small. Student teams only need the
``/stream`` endpoint; the remaining endpoints make the data contract explicit
and make it possible to test a solution without waiting for real time.
"""

from __future__ import annotations

import json
import os
import time
from typing import Iterator

import numpy as np
import pandas as pd
from flask import Flask, Response, jsonify, request

from synth_sensors import DT, simulate_batch


app = Flask(__name__)

DEFAULT_SPEED = float(os.environ.get("STREAM_SPEED", "8"))
MAX_SPEED = 60.0
SCENARIOS = ("nominal", "slow_heatup", "hold_undershoot", "sensor_dropout", "sensor_drift")

SENSOR_SCHEMA = {
    "timestamp": {"type": "number", "unit": "seconds since batch start"},
    "batch_id": {"type": "string", "description": "simulation run identifier"},
    "state": {"type": "string", "values": ["Idle", "Fill", "HeatUp", "Hold", "Cool", "Discharge"]},
    "T": {"type": "number|null", "unit": "degC"},
    "pH": {"type": "number|null", "unit": "pH"},
    "Kappa": {"type": "number|null", "unit": "mS/cm"},
    "Mu": {"type": "number|null", "unit": "cP"},
    "Tau": {"type": "number|null", "unit": "relative"},
    "Q_in": {"type": "number|null", "unit": "process units"},
    "Q_out": {"type": "number|null", "unit": "process units"},
    "P": {"type": "number|null", "unit": "bar"},
    "dTdt": {"type": "number|null", "unit": "degC/sample"},
}


@app.after_request
def allow_classroom_clients(response: Response) -> Response:
    """Allow browser clients hosted in the teams' repositories."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Accept, Content-Type, Last-Event-ID"
    return response


def _scenario_from_request() -> str:
    scenario = request.args.get("scenario", "nominal").strip().lower()
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario '{scenario}'; choose one of: {', '.join(SCENARIOS)}")
    return scenario


def _speed_from_request() -> float:
    raw_speed = request.args.get("speed", DEFAULT_SPEED)
    try:
        return min(max(float(raw_speed), 0.1), MAX_SPEED)
    except (TypeError, ValueError) as exc:
        raise ValueError("speed must be a number") from exc


def simulate_scenario(batch_id: str, scenario: str) -> pd.DataFrame:
    """Create one batch and apply a failure mode without exposing its label."""
    df, _ = simulate_batch(batch_id)
    df = df.copy()

    if scenario == "slow_heatup":
        mask = df["state"].eq("HeatUp")
        values = df.loc[mask, "T"].to_numpy()
        if len(values):
            # The line heats, but never gets close enough to the 72C setpoint.
            df.loc[mask, "T"] = np.linspace(values[0], 64.0, len(values))
    elif scenario == "hold_undershoot":
        mask = df["state"].eq("Hold")
        df.loc[mask, "T"] -= 3.5
    elif scenario == "sensor_dropout":
        mask = df.index.to_series().mod(11).eq(0) & df["state"].isin(["HeatUp", "Hold"])
        df.loc[mask, ["T", "pH", "dTdt"]] = np.nan
    elif scenario == "sensor_drift":
        # A progressively biased temperature measurement, not a process fault.
        df["T"] += np.linspace(0.0, 3.0, len(df))
        df["dTdt"] = df["T"].diff().fillna(0.0) / DT

    return df


def event_stream(df: pd.DataFrame, speed: float) -> Iterator[str]:
    """Serialize a DataFrame as a Server-Sent Events stream."""
    yield ": connected to the pasteurization simulator\n\n"
    interval = DT / speed
    for event_id, (_, row) in enumerate(df.iterrows()):
        # pandas handles NumPy scalars and serializes NaN as JSON null.
        yield f"id: {event_id}\nevent: sensor-reading\ndata: {row.to_json()}\n\n"
        time.sleep(interval)


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        service="Synthetic Pasteurization Stream API",
        version="1.0",
        endpoints={
            "health": "/health",
            "schema": "/schema",
            "stream": "/stream?team=G01&scenario=nominal&speed=8",
            "replay": "/replay?scenario=nominal",
            "batch": "/batch?scenario=nominal",
            "point": "/point?t=0",
        },
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok", service="pasteurization-simulator")


@app.route("/schema", methods=["GET"])
def schema():
    return jsonify(version="1.0", transport="Server-Sent Events", event="sensor-reading", fields=SENSOR_SCHEMA)


@app.route("/stream", methods=["GET"])
def stream():
    try:
        scenario = _scenario_from_request()
        speed = _speed_from_request()
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    team = request.args.get("team", "anonymous").strip()[:40] or "anonymous"
    response = Response(event_stream(simulate_scenario(team, scenario), speed), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache, no-transform"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@app.route("/replay", methods=["GET"])
def replay():
    """Return a complete batch immediately, for tests and demonstrations."""
    try:
        scenario = _scenario_from_request()
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    team = request.args.get("team", "validation").strip()[:40] or "validation"
    return Response(simulate_scenario(team, scenario).to_json(orient="records"), mimetype="application/json")


@app.route("/batch", methods=["GET"])
def batch():
    """Compatibility endpoint returning one complete batch as JSON."""
    try:
        scenario = _scenario_from_request()
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    return Response(simulate_scenario("batch", scenario).to_json(orient="records"), mimetype="application/json")


@app.route("/point", methods=["GET"])
def point():
    """Compatibility endpoint for a single instantaneous simulated reading."""
    try:
        timestamp = float(request.args.get("t", 0))
    except ValueError:
        return jsonify(error="t must be a number"), 400
    df = simulate_scenario("point", "nominal")
    row_index = int(timestamp / DT) % len(df)
    return jsonify(json.loads(df.iloc[row_index].to_json()))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8001"))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
