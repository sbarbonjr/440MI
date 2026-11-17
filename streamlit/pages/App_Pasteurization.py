#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit dashboard for pasteurization process sensors.
Reads from the classroom pasteurization simulator through its SSE /stream
endpoint. The public Render deployment is the default; a local or alternative
deployment can still be selected from the sidebar.
"""

import streamlit as st
import pandas as pd
import requests
import json
import time
import matplotlib.pyplot as plt
from urllib.parse import quote


DEFAULT_SIMULATOR_URL = "https://four40mi-pasteurization-simulator.onrender.com"

# -----------------------------
# STREAMLIT CONFIG
# -----------------------------
st.set_page_config(page_title="Pasteurization Dashboard", layout="wide")
st.title("Pasteurization Process – Live Sensor Dashboard")

# Sidebar configuration
st.sidebar.header("🔌 Simulator connection")

simulator_url = st.sidebar.text_input(
    "Simulator URL",
    st.session_state.get("simulator_url", DEFAULT_SIMULATOR_URL),
    help="Use the Render service URL, without /stream. For local development use http://127.0.0.1:8001.",
)
team = st.sidebar.text_input("Team identifier", st.session_state.get("team", "dashboard"))

st.session_state.simulator_url = simulator_url
st.session_state.team = team

# The service controls speed with one global clock, so teams remain synchronized.
STREAM_URL = f"{simulator_url.rstrip('/')}/stream?team={quote(team or 'dashboard', safe='')}"

st.sidebar.markdown(f"**Connected to:** `{STREAM_URL}`")
st.sidebar.caption("The simulator uses one shared process clock for every team.")

# -----------------------------
# PARAMETERS
# -----------------------------
REFRESH_INTERVAL = st.sidebar.slider("Refresh interval (seconds)", 0.1, 5.0, 1.0)
MAX_POINTS = st.sidebar.slider("Number of samples to show", 100, 1000, 300)

# Fixed y-axis ranges for each sensor
Y_RANGES = {
    "T": (0, 80),
    "pH": (6.0, 7.2),
    "Kappa": (4.0, 5.5),
    "Mu": (1.4, 2.4),
    "Tau": (0.0, 1.5),
    "Q_in": (0.0, 2.0),
    "Q_out": (0.0, 2.0),
    "P": (0.8, 1.6),
    "dTdt": (-1.0, 1.0),
}
SENSORS = list(Y_RANGES.keys())

# -----------------------------
# FUNCTIONS
# -----------------------------
def stream_data(url):
    """Generator to read data lines from Flask SSE endpoint."""
    try:
        with requests.get(url, stream=True, timeout=(15, 30)) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line and line.startswith(b"data:"):
                    payload = line.replace(b"data: ", b"").decode("utf-8")
                    try:
                        yield json.loads(payload)
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        st.error(f"Stream error: {e}")


# -----------------------------
# INITIALIZE DATAFRAME
# -----------------------------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["timestamp"] + SENSORS)
if "current_state" not in st.session_state:
    st.session_state.current_state = "Waiting for data"

if st.sidebar.button("Reset graph", help="Clear the locally displayed history; the shared simulator keeps running."):
    st.session_state.data = pd.DataFrame(columns=["timestamp"] + SENSORS)
    st.session_state.current_state = "Waiting for data"
    st.rerun()

placeholder = st.empty()
state_placeholder = st.empty()
state_placeholder.metric("Current process state", st.session_state.current_state)

# -----------------------------
# LIVE PLOTTING LOOP
# -----------------------------
data_gen = stream_data(STREAM_URL)
last_render = 0.0

for sample in data_gen:
    st.session_state.current_state = sample.get("state", "Unknown")

    df = st.session_state.data
    df = pd.concat([df, pd.DataFrame([sample])], ignore_index=True)

    if len(df) > MAX_POINTS:
        df = df.iloc[-MAX_POINTS:]

    st.session_state.data = df

    # Read every event but redraw less frequently so the dashboard keeps up
    # with the shared stream without accumulating an artificial delay.
    if time.monotonic() - last_render < REFRESH_INTERVAL:
        continue

    state_placeholder.metric("Current process state", st.session_state.current_state)

    # Plotting
    fig, axes = plt.subplots(3, 3, figsize=(14, 8))
    axes = axes.flatten()

    for i, sensor in enumerate(SENSORS):
        ax = axes[i]
        ax.plot(df["timestamp"], df[sensor], label=sensor, linewidth=1.5)
        ax.set_title(sensor)
        ax.set_ylim(Y_RANGES[sensor])
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(loc="upper right")

    plt.tight_layout()
    placeholder.pyplot(fig)
    plt.close(fig)
    last_render = time.monotonic()
