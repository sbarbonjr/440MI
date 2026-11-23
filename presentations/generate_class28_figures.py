"""Generate the figure used in the Class 28 slides.

Run from anywhere with the project environment:  python presentations/generate_class28_figures.py

The figure is SCHEMATIC. The readings are invented to show the three kinds of evidence a team should
collect from the live stream; it is not data from the simulator, and the figure says so on its face.

Figures
-------
class28_evidence_stream.pdf  Schematic sensor signal in three stretches: (1) normal behavior, (2) a configured
                             limit crossed by three consecutive readings, which raises one alert, and
                             (3) a disconnection that leaves a gap in the data.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(exist_ok=True)

# Course palette (same hexes as common.tex). Text always wears INK; colour rides on marks.
BLUE, GOLD, GREEN = "#12355B", "#C98A2E", "#2F6B4F"
RED = "#A23B2A"
INK, GRAY, MUTED = "#12355B", "#4B5563", "#6B7280"
ICE, HAIR = "#EEF3F8", "#CBD5E1"

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


def stamp(ax, text, x=1.0, y=1.0, ha="right", va="bottom"):
    """The honesty label: says on the figure that nothing here is measured."""
    ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va, fontsize=7.4, color=MUTED, style="italic")


def draw_evidence():
    rng = np.random.default_rng(7)
    t = np.arange(0, 31)
    limit = 0.62
    y = 0.50 + rng.normal(0, 0.018, t.size)
    # stretch 2: a ramp that crosses the limit for three consecutive readings (t = 13, 14, 15)
    y[11:19] = [0.55, 0.59, 0.66, 0.70, 0.68, 0.60, 0.55, 0.52]
    # stretch 3: disconnection, no readings from t = 21 to t = 26
    gap = (t >= 21) & (t <= 26)
    y_plot = np.where(gap, np.nan, y)

    fig, ax = plt.subplots(figsize=(4.4, 2.55))
    ax.axvspan(-0.5, 9.5, color=GREEN, alpha=0.08, linewidth=0, zorder=0)
    ax.axvspan(9.5, 19.5, color=GOLD, alpha=0.10, linewidth=0, zorder=0)
    ax.axvspan(19.5, 30.5, color=GRAY, alpha=0.10, linewidth=0, zorder=0)
    for x, label in ((4.5, "1  normal"), (14.5, "2  threshold crossing"), (25.0, "3  disconnection")):
        ax.text(x, 0.800, label, ha="center", va="center", fontsize=8, fontweight="bold", color=INK)

    ax.axhline(limit, color=GOLD, lw=1.6, ls="--", zorder=2)
    ax.text(0.0, limit + 0.012, "configured limit", fontsize=7.6, color=INK, ha="left", va="bottom")

    ax.plot(t, y_plot, color=BLUE, lw=1.8, marker="o", ms=3.4, mfc="white", mew=1.2, zorder=3)
    # the three consecutive readings above the limit
    ax.plot(t[13:16], y[13:16], "o", ms=5, color=RED, zorder=4)
    ax.annotate("3 consecutive readings\nabove the limit: one alert", xy=(15, y[15]), xytext=(20.5, 0.705),
                fontsize=7.6, color=INK, ha="left", va="center", linespacing=1.1,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8, shrinkA=2, shrinkB=3))
    ax.text(23.5, 0.50, "no data", ha="center", va="center", fontsize=8, color=MUTED, style="italic")

    ax.set_xlim(-0.5, 30.5)
    ax.set_ylim(0.40, 0.84)
    ax.set_yticks([])
    ax.set_xticks([0, 10, 20, 30])
    ax.set_xlabel("time (successive readings)")
    ax.set_ylabel("sensor value")
    ax.spines[["top", "right"]].set_visible(False)
    stamp(ax, "schematic: invented data", y=1.01)
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / "class28_evidence_stream.pdf")
    plt.close(fig)


if __name__ == "__main__":
    draw_evidence()
    print("figure written to", OUT)
