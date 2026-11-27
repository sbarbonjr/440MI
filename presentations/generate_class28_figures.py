"""Generate the figure used in the Class 28 slides.

Run from anywhere with the project environment:  python presentations/generate_class28_figures.py

The data are SYNTHETIC: one batch computed by the course simulator (pasteurization/serving.py, the same
values its /replay endpoint returns when run from this code). Nothing here is measured on a real plant.
The temperature limits are the placeholder rules BR-01 to BR-03 of the example SRS
(documents/Class28_SRS_Pasteurization_Monitoring.tex); they are not food-safety limits.

Figures
-------
class28_evidence_stream.pdf  Top: temperature over a whole nominal batch, with the process states and the
                             limits drawn only where they apply (Hold). Bottom: zoom on Hold, comparing
                             nominal with hold_undershoot, marking the critical alert in SRS 1.0 (first
                             violating reading) and 2.0 (third), and the reading that sensor_dropout loses.
                             Drawn at the size it appears on the slide (7.3 cm wide).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "pasteurization"))
from serving import simulate_scenario  # noqa: E402

OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(exist_ok=True)

# Course palette (same hexes as common.tex). Text always wears INK; colour rides on marks.
BLUE, GOLD, GREEN = "#12355B", "#C98A2E", "#2F6B4F"
RED = "#A23B2A"
INK, GRAY, MUTED = "#12355B", "#4B5563", "#6B7280"
ICE, HAIR = "#EEF3F8", "#CBD5E1"

# Placeholder limits of the example SRS, valid during Hold only.
CRITICAL_LOW, WARNING_LOW, WARNING_HIGH = 71.0, 71.5, 73.0

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 6.2,
    "axes.labelcolor": INK,
    "text.color": INK,
    "axes.edgecolor": HAIR,
    "xtick.color": GRAY,
    "ytick.color": GRAY,
    "xtick.labelsize": 5.6,
    "ytick.labelsize": 5.6,
    "pdf.fonttype": 42,
})


def draw_evidence():
    nominal = simulate_scenario("nominal").reset_index(drop=True)
    under = simulate_scenario("hold_undershoot").reset_index(drop=True)
    dropout = simulate_scenario("sensor_dropout").reset_index(drop=True)

    hold = nominal.index[nominal["state"] == "Hold"]
    first, last = int(hold.min()), int(hold.max())
    low = [i for i in hold if under.at[i, "T"] < CRITICAL_LOW]
    alert_v1, alert_v2 = low[0], low[2]          # persistence 1, then persistence 3
    missing = [i for i in hold if np.isnan(dropout.at[i, "T"])]

    fig, (top, zoom) = plt.subplots(2, 1, figsize=(2.87, 1.76), gridspec_kw={"height_ratios": [0.8, 1.5]})

    # ---- top: the whole batch
    top.plot(nominal.index, nominal["T"], color=BLUE, lw=1.1, zorder=3)
    for k, (state, part) in enumerate(nominal.groupby("state", sort=False)):
        a, b = part.index.min(), part.index.max() + 1
        top.axvspan(a, b, color=GOLD if state == "Hold" else (ICE if k % 2 == 0 else "white"),
                    alpha=0.28 if state == "Hold" else 1.0, lw=0, zorder=0)
        if state != "Hold":
            top.text((a + b) / 2 - (7 if state == "HeatUp" else 0), 90, state,
                     ha="center", va="center", fontsize=5.0, color=GRAY)
    top.text((first + last) / 2, 90, "Hold", ha="center", va="center", fontsize=5.4, fontweight="bold")
    for y in (CRITICAL_LOW, WARNING_HIGH):
        top.hlines(y, first, last, color=RED if y == CRITICAL_LOW else GOLD, lw=0.9, zorder=4)
    top.set_xlim(0, len(nominal))
    top.set_ylim(0, 99)
    top.set_yticks([0, 40, 72])
    top.set_xticks([])
    top.set_title("Temperature (°C), one nominal batch", fontsize=6.4, fontweight="bold", loc="left", pad=2)
    top.spines[["top", "right"]].set_visible(False)

    # ---- bottom: zoom on Hold
    x0, x1 = first - 5, last + 10
    zoom.axvspan(first - 0.5, last + 0.5, color=GOLD, alpha=0.10, lw=0, zorder=0)
    for y, color, label in ((WARNING_HIGH, GOLD, "73.0"), (WARNING_LOW, GOLD, "71.5"), (CRITICAL_LOW, RED, "71.0")):
        zoom.hlines(y, first - 0.5, last + 0.5, color=color, lw=0.9, ls="--", zorder=2)
        zoom.text(last + 3.7, y + {"73.0": 0, "71.5": 0.28, "71.0": -0.22}[label], label,
                  ha="left", va="center", fontsize=5.4)
    zoom.plot(nominal.index, nominal["T"], color=GREEN, lw=1.2, marker="o", ms=1.8, zorder=3)
    zoom.plot(under.index, under["T"], color=BLUE, lw=1.2, marker="o", ms=1.8, zorder=3)
    for i in missing:
        zoom.axvline(i, color=GRAY, lw=3.2, alpha=0.30, zorder=1)
        zoom.annotate(f"{i} missing in\ndropout run", xy=(i, 70.8), xytext=(i + 1.4, 70.25),
                      fontsize=5.2, ha="left", va="center", linespacing=1.1,
                      arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.6, shrinkA=1, shrinkB=1))
    zoom.plot([alert_v1], [under.at[alert_v1, "T"]], "o", ms=4.6, color=RED, zorder=5)
    zoom.plot([alert_v2], [under.at[alert_v2, "T"]], "D", ms=3.8, color=GOLD, mec=INK, mew=0.6, zorder=5)
    zoom.annotate(f"v1 alert: {alert_v1}", xy=(alert_v1, under.at[alert_v1, "T"]), xytext=(first + 0.6, 67.55),
                  fontsize=5.2, ha="left", va="center",
                  arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.6, shrinkA=1, shrinkB=2))
    zoom.annotate(f"v2 alert (3rd): {alert_v2}", xy=(alert_v2, under.at[alert_v2, "T"]), xytext=(first + 8.5, 67.55),
                  fontsize=5.2, ha="left", va="center",
                  arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.6, shrinkA=1, shrinkB=2))
    zoom.text(first + 2.0, 72.55, "1  nominal", fontsize=5.8, fontweight="bold", color=INK, va="center")
    zoom.text(first + 3.0, 68.95, "2  hold_undershoot", fontsize=5.8, fontweight="bold", color=INK, va="bottom")
    zoom.set_xlim(x0, x1)
    zoom.set_ylim(67.2, 73.7)
    zoom.set_yticks([68, 70, 72])
    zoom.set_xticks([first, 165, last])
    zoom.set_xlabel("reading number (zoom on Hold)", fontsize=5.8, labelpad=1)
    zoom.spines[["top", "right"]].set_visible(False)

    fig.text(0.995, 0.008, "synthetic simulator data; limits are assumptions", fontsize=5.0, color=MUTED,
             style="italic", ha="right", va="bottom")
    fig.tight_layout(pad=0.3, h_pad=0.4, rect=(0, 0.035, 1, 1))
    fig.savefig(OUT / "class28_evidence_stream.pdf")
    plt.close(fig)
    return alert_v1, alert_v2, missing


if __name__ == "__main__":
    v1, v2, missing = draw_evidence()
    print("figure written to", OUT, "| v1 alert", v1, "| v2 alert", v2, "| missing in Hold", missing)
