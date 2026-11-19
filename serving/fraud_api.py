"""Fraud scoring service: the corrected counterpart of Class6_model_api.py (Class 31).

Differences from the minimal endpoint:
- loads an artifact that exists in the repository, together with its scaler
  (same preprocessing as in training: no training-serving skew);
- validates the input before calling the model;
- returns the probability, the decision threshold, and the model version;
- records every prediction as one JSON line, for later monitoring;
- exposes a health endpoint and runs without the debugger.

Run from the repository root:  python serving/fraud_api.py
"""

import hashlib
import json
import math
import os
import pickle
import time
import uuid
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, request

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "streamlit" / "model.pkl"
SCALER_PATH = ROOT / "streamlit" / "scaler.pkl"
LOG_PATH = ROOT / "logs" / "predictions.jsonl"

# Explicit, documented decision threshold (see Class 18); override with FRAUD_THRESHOLD.
THRESHOLD = float(os.environ.get("FRAUD_THRESHOLD", "0.5"))

with open(MODEL_PATH, "rb") as f:
    MODEL = pickle.load(f)
# One request = one sample: parallel trees (n_jobs=-1, as trained) only add scheduling overhead.
MODEL.n_jobs = 1
with open(SCALER_PATH, "rb") as f:
    SCALER = pickle.load(f)

FEATURES = list(SCALER.feature_names_in_)  # Time, V1..V28, Amount
MODEL_VERSION = hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest()[:12]

app = Flask(__name__)


def validate(payload):
    """Return (features, None) if the request is valid, otherwise (None, error message)."""
    if not isinstance(payload, dict) or "features" not in payload:
        return None, 'body must be a JSON object with a "features" field'
    values = payload["features"]
    if not isinstance(values, list) or len(values) != len(FEATURES):
        return None, f'"features" must be a list of {len(FEATURES)} numbers ({", ".join([FEATURES[0], FEATURES[1], "...", FEATURES[-1]])})'
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in values):
        return None, '"features" must contain only finite numbers'
    return values, None


@app.route("/health")
def health():
    return jsonify({"status": "ok", "model_version": MODEL_VERSION, "threshold": THRESHOLD})


@app.route("/predict", methods=["POST"])
def predict():
    start = time.perf_counter()
    values, error = validate(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    x = SCALER.transform(pd.DataFrame([values], columns=FEATURES))
    probability = float(MODEL.predict_proba(x)[0, 1])
    response = {
        "request_id": str(uuid.uuid4()),
        "model_version": MODEL_VERSION,
        "fraud_probability": round(probability, 4),
        "threshold": THRESHOLD,
        "is_fraud": probability >= THRESHOLD,
        "latency_ms": round((time.perf_counter() - start) * 1000, 2),
    }

    LOG_PATH.parent.mkdir(exist_ok=True)
    with open(LOG_PATH, "a") as log:
        log.write(json.dumps({**response, "timestamp": time.time(), "features": values}) + "\n")
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
