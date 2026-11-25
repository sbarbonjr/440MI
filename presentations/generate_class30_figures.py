"""Generate the figures used in the Class 30 slides (Pasteurization Challenge, Session 3).

Run from anywhere with the project environment:  python presentations/generate_class30_figures.py

The data are NOT invented: they come from the same code as the classroom simulator
(pasteurization/serving.py, function simulate_scenario), which is what /replay and /stream serve.
The stream is ten nominal batches followed by ten batches of a fault scenario, i.e. what a client
observes when it reconnects with ?scenario=<name>.

Monitor used in the figures and in the slides
---------------------------------------------
* Online baseline: one running mean of the temperature T per steady state (Idle, Hold, Discharge),
  updated test-then-train (the residual is computed before the reading updates the mean).
* Drift detector: one ADWIN(delta=0.002) per steady state, fed with the residual T - baseline,
  active once the state has accumulated more than 20 readings.
* Threshold rule (session 2): critical alert when T leaves 72 +/- 1 degC during Hold for
  3 consecutive readings.

Figures
-------
class30_residuals.pdf   Residual of T with respect to the online baseline, per steady state, around the
                        onset of the sensor_drift scenario, with the ADWIN detections marked.
Printed table           The scenario matrix reported on the slides.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from river import drift, stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pasteurization"))
import serving  # noqa: E402  (the classroom simulator)

OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(exist_ok=True)

BLUE, GOLD, GREEN = "#12355B", "#C98A2E", "#2F6B4F"
RED = "#A23B2A"
INK, GRAY, MUTED = "#12355B", "#4B5563", "#6B7280"
HAIR = "#CBD5E1"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.labelcolor": INK,
    "text.color": INK,
    "axes.edgecolor": HAIR,
    "xtick.color": GRAY,
    "ytick.color": GRAY,
    "pdf.fonttype": 42,
})

STEADY = ("Idle", "Hold", "Discharge")
COLOURS = {"Idle": GREEN, "Hold": RED, "Discharge": BLUE}
N_NOMINAL, N_FAULT = 10, 10
WARMUP = 20
LIMIT, PERSIST = 1.0, 3


def run(scenario):
    """Process the stream sample by sample, as a live client would."""
    nominal = serving.simulate_scenario("nominal")
    df = pd.concat([nominal] * N_NOMINAL + [serving.simulate_scenario(scenario)] * N_FAULT, ignore_index=True)
    onset = len(nominal) * N_NOMINAL
    mean = {s: stats.Mean() for s in STEADY}
    adwin = {s: drift.ADWIN(delta=0.002) for s in STEADY}
    rows, events, alerts, missing, run_len = [], [], [], 0, 0
    for i, e in df.iterrows():
        T, state = e["T"], e["state"]
        if pd.isna(T):
            missing += 1
            continue
        run_len = run_len + 1 if (state == "Hold" and abs(T - 72.0) > LIMIT) else 0
        if run_len == PERSIST:
            alerts.append(i)
        if state in STEADY:
            if mean[state].n > WARMUP:
                r = T - mean[state].get()          # test ...
                rows.append((i, state, r))
                adwin[state].update(r)
                if adwin[state].drift_detected:
                    events.append((i, state))
            mean[state].update(T)                   # ... then train
    return onset, pd.DataFrame(rows, columns=["i", "state", "r"]), events, alerts, missing


def scenario_table():
    print(f"batch length: {len(serving.simulate_scenario('nominal'))} readings; "
          f"stream speed {serving.DEFAULT_SPEED:g}x")
    for sc in serving.SCENARIOS:
        onset, _, events, alerts, missing = run(sc)
        first = {}
        for i, s in events:
            if i >= onset:
                first.setdefault(s, i - onset)
        early = sum(1 for i, _ in events if i < onset)
        first_alert = next((a - onset for a in alerts if a >= onset), None)
        print(f"{sc:16s} false drift events before onset: {early}; first drift event per state: {first}; "
              f"Hold critical alerts: {sum(a >= onset for a in alerts)} (first after {first_alert}); "
              f"missing T: {missing}")


def draw_residuals():
    onset, res, events, _, _ = run("sensor_drift")
    batch = len(serving.simulate_scenario("nominal"))
    lo, hi = onset - 2 * batch, onset + 3 * batch
    fig, ax = plt.subplots(figsize=(5.7, 3.45))
    ax.axvspan(0, hi - onset, color=GOLD, alpha=0.08, linewidth=0, zorder=0)
    for s in STEADY:
        part = res[(res.state == s) & (res.i >= lo) & (res.i < hi)]
        ax.plot(part.i - onset, part.r, "o", ms=2.2, color=COLOURS[s], label=s, zorder=2)
    for i, s in events:
        if lo <= i < hi:
            r = res.loc[res.i == i, "r"].iloc[0]
            ax.plot(i - onset, r, marker="v", ms=8, color=COLOURS[s], mec="white", mew=0.8, zorder=4)
    ax.axvline(0, color=GOLD, lw=1.4, ls="--", zorder=1)
    ax.text(6, 3.1, "reconnect with\n?scenario=sensor_drift", fontsize=7.6, color=INK, va="top")
    for k in range(-2, 3):
        ax.axvline(k * batch, color=HAIR, lw=0.6, zorder=0)
    ax.text(-2 * batch + 6, 3.1, "nominal batches", fontsize=7.6, color=INK, va="top")
    ax.plot([], [], "v", color=GRAY, ms=7, label="ADWIN detection")
    ax.set_xlim(lo - onset, hi - onset)
    ax.set_ylim(-0.4, 3.25)
    ax.set_xlabel("readings after the onset of the fault (one batch = %d readings)" % batch)
    ax.set_ylabel("residual of T (degC)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.86), frameon=False, fontsize=8, ncol=1, markerscale=1.6)
    ax.text(1.0, 1.01, "simulator data; River 0.22, ADWIN(delta=0.002)",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.0, color=MUTED, style="italic")
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / "class30_residuals.pdf")
    plt.close(fig)


if __name__ == "__main__":
    scenario_table()
    draw_residuals()
    print("figure written to", OUT)
