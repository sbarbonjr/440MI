#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit dashboard for pasteurization process sensors.
Reads from the classroom pasteurization simulator through its SSE /stream
endpoint. The public Render deployment is the default; a local or alternative
deployment can still be selected from the sidebar.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
import time
import plotly.graph_objects as go
from urllib.parse import quote
from plotly.subplots import make_subplots


DEFAULT_SIMULATOR_URL = "https://four40mi-pasteurization-simulator.onrender.com"
STATE_ICONS = {
    "Idle": "⚪",
    "Fill": "🔵",
    "HeatUp": "🟠",
    "Hold": "🔴",
    "Cool": "❄️",
    "Discharge": "🟣",
}
STATE_COLORS = {
    "Idle": "#94a3b8",
    "Fill": "#38bdf8",
    "HeatUp": "#fb923c",
    "Hold": "#ef4444",
    "Cool": "#60a5fa",
    "Discharge": "#a78bfa",
}

# -----------------------------
# STREAMLIT CONFIG
# -----------------------------
st.set_page_config(page_title="Pasteurization Dashboard", layout="wide")

if "current_state" not in st.session_state:
    st.session_state.current_state = "Waiting for data"
if "latest_sample" not in st.session_state:
    st.session_state.latest_sample = {}

title_col, state_col = st.columns([3, 2], vertical_alignment="center")
with title_col:
    st.title("Pasteurization Process")
    st.caption("Live operational dashboard · globally synchronized classroom simulator")
state_card = state_col.empty()


def render_status(sample: dict | None = None) -> None:
    """Render the compact operational status in the page header."""
    sample = sample or st.session_state.latest_sample
    state = st.session_state.current_state
    icon = STATE_ICONS.get(state, "⏳")
    with state_card.container():
        st.caption("LIVE PROCESS STATUS")
        st.metric("Current state", f"{icon} {state}")
        if sample:
            st.caption(f"Batch {sample.get('batch_id', '—')} · event {sample.get('event_id', '—')}")
        else:
            st.caption("Connecting to the simulator…")


def format_measurement(value, precision: int, unit: str = "") -> str:
    """Display unavailable sensor readings without breaking the live dashboard."""
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):.{precision}f}{unit}"


def state_intervals(df: pd.DataFrame, x: pd.Series):
    """Yield contiguous state intervals for subtle background bands."""
    if df.empty or "state" not in df:
        return

    start = 0
    states = df["state"].fillna("Unknown").tolist()
    for index in range(1, len(states) + 1):
        if index == len(states) or states[index] != states[start]:
            yield states[start], x.iloc[start], x.iloc[index - 1]
            start = index


def sensor_figure(df: pd.DataFrame) -> go.Figure:
    """Build an interactive small-multiples view of all sensor signals."""
    titles = [f"{sensor}" for sensor in SENSORS]
    fig = make_subplots(
        rows=3,
        cols=3,
        subplot_titles=titles,
        shared_xaxes=True,
        vertical_spacing=0.09,
        horizontal_spacing=0.07,
    )

    # A relative axis remains easy to read while global timestamp/event_id
    # continue to identify the same observation across all student clients.
    x = df["timestamp"] - df["timestamp"].iloc[0]
    cycle_time = df["cycle_time"] if "cycle_time" in df else df["timestamp"]
    states = df["state"] if "state" in df else pd.Series("Unknown", index=df.index)
    customdata = list(zip(cycle_time, states))

    for index, sensor in enumerate(SENSORS):
        row, column = divmod(index, 3)
        fig.add_trace(
            go.Scatter(
                x=x,
                y=df[sensor],
                mode="lines",
                line={"width": 2},
                name=sensor,
                showlegend=False,
                customdata=customdata,
                hovertemplate=(
                    f"<b>{sensor}</b>: %{{y:.3g}}<br>"
                    "Visible time: %{x:.1f} s<br>"
                    "Cycle time: %{customdata[0]:.1f} s<br>"
                    "State: %{customdata[1]}<extra></extra>"
                ),
            ),
            row=row + 1,
            col=column + 1,
        )
        fig.update_yaxes(range=Y_RANGES[sensor], row=row + 1, col=column + 1, gridcolor="#e5e7eb")

    for state, x0, x1 in state_intervals(df, x):
        fig.add_vrect(
            x0=x0,
            x1=x1,
            fillcolor=STATE_COLORS.get(state, "#cbd5e1"),
            opacity=0.10,
            line_width=0,
            layer="below",
            row="all",
            col="all",
        )

    fig.update_xaxes(title_text="Time in visible window (s)", gridcolor="#e5e7eb", zeroline=False)
    fig.update_layout(
        height=840,
        hovermode="x unified",
        # Preserve the client-side Plotly scene, including zoom and pan,
        # while incoming samples replace the trace data.
        uirevision="pasteurization-live-chart",
        margin={"l": 25, "r": 25, "t": 55, "b": 35},
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    return fig


def render_live_sensor_component(stream_url: str) -> None:
    """Render a browser-side SSE client that appends points without redraw flicker."""
    sensor_specs = [
        {"name": sensor, "range": Y_RANGES[sensor]}
        for sensor in SENSORS
    ]
    html = """
    <style>
      body { margin: 0; background: transparent; font-family: sans-serif; }
      #connection { color: #64748b; font-size: 0.85rem; margin: 0 0 0.6rem 0.2rem; }
      #charts { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.55rem; }
      .chart { border: 1px solid #e2e8f0; border-radius: 0.5rem; overflow: hidden; background: white; }
      @media (max-width: 720px) { #charts { grid-template-columns: 1fr; } }
    </style>
    <div id="connection">Connecting to live simulator…</div>
    <div id="charts"></div>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <script>
      const streamUrl = __STREAM_URL__;
      const sensors = __SENSORS__;
      const maxPoints = 300;
      const charts = {};
      const palette = ["#2563eb", "#16a34a", "#9333ea", "#ea580c", "#0891b2", "#dc2626", "#4f46e5", "#be123c", "#475569"];
      const chartContainer = document.getElementById("charts");
      const connectionLabel = document.getElementById("connection");

      sensors.forEach((sensor, index) => {
        const chart = document.createElement("div");
        chart.className = "chart";
        chart.id = `sensor-${sensor.name}`;
        chartContainer.appendChild(chart);
        Plotly.newPlot(
          chart,
          [{ x: [], y: [], type: "scatter", mode: "lines", line: { color: palette[index], width: 2 }, hovertemplate: `${sensor.name}: %{y:.3g}<br>Time: %{x:.1f} s<extra></extra>` }],
          {
            title: { text: sensor.name, font: { size: 14 } },
            height: 240,
            margin: { l: 48, r: 15, t: 35, b: 35 },
            xaxis: { title: { text: "Visible time (s)", font: { size: 10 } }, gridcolor: "#e5e7eb" },
            yaxis: { range: sensor.range, gridcolor: "#e5e7eb" },
            paper_bgcolor: "white",
            plot_bgcolor: "white",
            showlegend: false,
          },
          { displaylogo: false, scrollZoom: true, responsive: true },
        );
        charts[sensor.name] = chart;
      });

      let firstTimestamp = null;
      const source = new EventSource(streamUrl);
      source.addEventListener("sensor-reading", (event) => {
        const sample = JSON.parse(event.data);
        if (firstTimestamp === null) firstTimestamp = sample.timestamp;
        const visibleTime = sample.timestamp - firstTimestamp;
        sensors.forEach((sensor) => {
          const value = sample[sensor.name];
          if (Number.isFinite(value)) {
            Plotly.extendTraces(charts[sensor.name], { x: [[visibleTime]], y: [[value]] }, [0], maxPoints);
          }
        });
        connectionLabel.textContent = `Live · ${sample.state} · ${sample.batch_id} · event ${sample.event_id}`;
      });
      source.onerror = () => { connectionLabel.textContent = "Reconnecting to live simulator…"; };
    </script>
    """
    html = html.replace("__STREAM_URL__", json.dumps(stream_url))
    html = html.replace("__SENSORS__", json.dumps(sensor_specs))
    components.html(html, height=805, scrolling=False)


render_status()
st.divider()

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
with st.sidebar.expander("Stream contract", expanded=False):
    st.write("Transport: Server-Sent Events (SSE)")
    st.write("Event: `sensor-reading`")
    st.link_button("Open schema", f"{simulator_url.rstrip('/')}/schema")

# -----------------------------
# PARAMETERS
# -----------------------------
REFRESH_INTERVAL = st.sidebar.slider("Refresh interval (seconds)", 0.1, 5.0, 1.0)
MAX_POINTS = st.sidebar.slider("Number of samples to show", 100, 1000, 300)

# Fixed y-axis ranges for each sensor
Y_RANGES = {
    "T": (0, 80),
    "pH": (6.0, 7.2),
    "Kappa": (3.0, 5.5),
    "Mu": (1.4, 2.4),
    "Tau": (0.0, 1.5),
    "Q_in": (0.0, 2.0),
    "Q_out": (0.0, 2.0),
    "P": (0.8, 1.6),
    "dTdt": (-1.05, 1.05),
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
    st.session_state.data = pd.DataFrame(columns=["timestamp", "visible_time"] + SENSORS)
if "display_epoch" not in st.session_state:
    st.session_state.display_epoch = None

if st.sidebar.button("Reset graph", help="Clear the locally displayed history; the shared simulator keeps running."):
    st.session_state.data = pd.DataFrame(columns=["timestamp", "visible_time"] + SENSORS)
    st.session_state.current_state = "Waiting for data"
    st.session_state.latest_sample = {}
    st.session_state.display_epoch = None
    st.session_state.pop("analysis_data", None)
    st.rerun()

metric_placeholder = st.empty()
st.subheader("Live sensor trends")
st.caption("The browser appends SSE samples directly to the charts; it does not redraw the dashboard for each point.")
render_live_sensor_component(STREAM_URL)

with st.expander("Latest sensor readings", expanded=False):
    table_placeholder = st.empty()
with st.expander("Interactive analysis", expanded=False):
    refresh_analysis = st.button("Refresh analysis from visible data")
    analysis_placeholder = st.empty()
    if refresh_analysis and not st.session_state.data.empty:
        st.session_state.analysis_data = st.session_state.data.copy()
    if "analysis_data" in st.session_state and not st.session_state.analysis_data.empty:
        analysis_placeholder.plotly_chart(
            sensor_figure(st.session_state.analysis_data),
            use_container_width=True,
            config={"displaylogo": False, "scrollZoom": True},
        )
    else:
        analysis_placeholder.caption("Use this panel for a rich, static Plotly inspection of the current visible window.")

# -----------------------------
# LIVE PLOTTING LOOP
# -----------------------------
data_gen = stream_data(STREAM_URL)
last_render = 0.0

for sample in data_gen:
    st.session_state.current_state = sample.get("state", "Unknown")
    st.session_state.latest_sample = sample

    if st.session_state.display_epoch is None:
        st.session_state.display_epoch = sample["timestamp"]
    display_sample = dict(sample)
    display_sample["visible_time"] = sample["timestamp"] - st.session_state.display_epoch

    df = st.session_state.data
    df = pd.concat([df, pd.DataFrame([display_sample])], ignore_index=True)

    if len(df) > MAX_POINTS:
        df = df.iloc[-MAX_POINTS:]

    st.session_state.data = df

    # Read every event but redraw less frequently so the dashboard keeps up
    # with the shared stream without accumulating an artificial delay.
    if time.monotonic() - last_render < REFRESH_INTERVAL:
        continue

    render_status(sample)
    with metric_placeholder.container():
        metric_columns = st.columns(4)
        metric_columns[0].metric("Temperature", format_measurement(sample.get("T"), 1, " °C"))
        metric_columns[1].metric("Pressure", format_measurement(sample.get("P"), 2, " bar"))
        metric_columns[2].metric("pH", format_measurement(sample.get("pH"), 2))
        metric_columns[3].metric("Visible samples", f"{len(df)} / {MAX_POINTS}")

    table_placeholder.dataframe(df.tail(12), hide_index=True, use_container_width=True)
    last_render = time.monotonic()
