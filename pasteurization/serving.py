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
# A fixed epoch makes the process independent of Render restarts. Every client
# maps the same wall-clock instant to the same point in the simulated batch.
SIMULATION_EPOCH = float(os.environ.get("SIMULATION_EPOCH", "1767225600"))
SCENARIOS = ("nominal", "slow_heatup", "hold_undershoot", "sensor_dropout", "sensor_drift")

# Generated once with the seeded generator in synth_sensors. Do not create a
# batch per connection: doing so would give each team a different process.
BASE_BATCH, _ = simulate_batch("template")

SENSOR_SCHEMA = {
    "event_id": {"type": "integer", "description": "global, monotonically increasing SSE event id"},
    "timestamp": {"type": "number", "unit": "simulated seconds since the global epoch"},
    "cycle_time": {"type": "number", "unit": "simulated seconds since the current batch began"},
    "batch_id": {"type": "string", "description": "globally synchronized simulation batch identifier"},
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


def simulate_scenario(scenario: str) -> pd.DataFrame:
    """Apply a failure mode to the shared, deterministic base batch."""
    df = BASE_BATCH.copy()

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


def _global_event_id(now: float | None = None) -> int:
    """Return the process sample that corresponds to a real wall-clock instant."""
    if now is None:
        now = time.time()
    return max(0, int((now - SIMULATION_EPOCH) * DEFAULT_SPEED / DT))


def _global_sample(df: pd.DataFrame, event_id: int) -> pd.Series:
    """Select a cyclic batch sample and attach globally meaningful metadata."""
    batch_length = len(df)
    row = df.iloc[event_id % batch_length].copy()
    row["event_id"] = event_id
    row["timestamp"] = event_id * DT
    row["cycle_time"] = (event_id % batch_length) * DT
    row["batch_id"] = f"B-{event_id // batch_length + 1:06d}"
    return row


def event_stream(df: pd.DataFrame) -> Iterator[str]:
    """Stream the sample selected by the global simulation clock.

    A client joining half-way through a cycle starts at the current state rather
    than receiving the first Idle event. Clients reconnecting at the same time
    receive the same event id and sensor values.
    """
    yield ": connected to the pasteurization simulator\n\n"
    previous_event_id = -1
    while True:
        event_id = _global_event_id()
        if event_id != previous_event_id:
            row = _global_sample(df, event_id)
            # pandas handles NumPy scalars and serializes NaN as JSON null.
            yield f"id: {event_id}\nevent: sensor-reading\ndata: {row.to_json()}\n\n"
            previous_event_id = event_id

        next_sample_at = SIMULATION_EPOCH + (event_id + 1) * DT / DEFAULT_SPEED
        time.sleep(max(0.01, next_sample_at - time.time()))


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        service="Synthetic Pasteurization Stream API",
        version="1.0",
        endpoints={
            "health": "/health",
            "schema": "/schema",
            "stream": "/stream?team=G01&scenario=nominal",
            "replay": "/replay?scenario=nominal",
            "batch": "/batch?scenario=nominal",
            "point": "/point?t=0",
        },
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        status="ok",
        service="pasteurization-simulator",
        synchronization="global-clock",
        simulation_speed=DEFAULT_SPEED,
    )


@app.route("/schema", methods=["GET"])
def schema():
    return jsonify(
        version="1.1",
        transport="Server-Sent Events",
        event="sensor-reading",
        synchronization="All clients are aligned to one global simulation clock.",
        simulation_speed=DEFAULT_SPEED,
        fields=SENSOR_SCHEMA,
    )


@app.route("/stream", methods=["GET"])
def stream():
    try:
        scenario = _scenario_from_request()
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    response = Response(event_stream(simulate_scenario(scenario)), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache, no-transform"
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["X-Simulation-Speed"] = str(DEFAULT_SPEED)
    return response


@app.route("/replay", methods=["GET"])
def replay():
    """Return a complete batch immediately, for tests and demonstrations."""
    try:
        scenario = _scenario_from_request()
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    return Response(simulate_scenario(scenario).to_json(orient="records"), mimetype="application/json")


@app.route("/batch", methods=["GET"])
def batch():
    """Compatibility endpoint returning one complete batch as JSON."""
    try:
        scenario = _scenario_from_request()
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    return Response(simulate_scenario(scenario).to_json(orient="records"), mimetype="application/json")


@app.route("/point", methods=["GET"])
def point():
    """Compatibility endpoint for a single instantaneous simulated reading."""
    try:
        timestamp = float(request.args.get("t", 0))
    except ValueError:
        return jsonify(error="t must be a number"), 400
    df = simulate_scenario("nominal")
    row_index = int(timestamp / DT) % len(df)
    return jsonify(json.loads(df.iloc[row_index].to_json()))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8001"))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
