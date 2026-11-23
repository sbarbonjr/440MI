"""Generate the figure used in the Class 27 slides.

Run from anywhere with the project environment:  python presentations/generate_class27_figures.py

The figure is SCHEMATIC. The values are invented to show how a performance metric decays and how a
retraining run restores it; it is not data from any model in this course, and the figure says so on
its face.

Figures
-------
class27_triggers.pdf  Schematic model performance over time. It decays slowly, crosses an agreed
                      threshold, and each crossing launches a retraining run that restores it.
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


def stamp(ax, text, x=1.0, y=1.0, ha="right", va="bottom"):
    """The honesty label: says on the figure that nothing here is measured."""
    ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va, fontsize=7.4, color=MUTED, style="italic")


def draw_triggers():
    rng = np.random.default_rng(11)
    threshold = 0.80
    t = np.arange(0, 61)
    y = np.empty(t.size)
    retrain_at = []
    level, start = 0.93, 0
    for i in range(t.size):
        # a slow decay since the last retraining run, with a little noise
        y[i] = level - 0.0085 * (i - start) + rng.normal(0, 0.004)
        if y[i] < threshold and (i - start) > 3:
            retrain_at.append(i)
            start, level = i + 1, 0.93
    fig, ax = plt.subplots(figsize=(4.4, 2.55))
    ax.axhline(threshold, color=GOLD, lw=1.6, ls="--", zorder=2)
    ax.text(0.5, threshold - 0.007, "agreed threshold", fontsize=7.6, color=INK, ha="left", va="top")
    # split the line at each retraining run so the jump is drawn as a break, not a slope
    cuts = [0] + [r + 1 for r in retrain_at] + [t.size]
    for a, b in zip(cuts[:-1], cuts[1:]):
        ax.plot(t[a:b], y[a:b], color=BLUE, lw=1.8, zorder=3)
    for r in retrain_at:
        ax.plot([t[r]], [y[r]], "o", ms=5.2, color=RED, zorder=4)
        ax.axvline(t[r] + 0.5, color=GREEN, lw=1.2, alpha=0.9, zorder=1)
        ax.text(t[r] + 1.2, 0.965, "retrain", fontsize=7.6, color=GREEN, ha="left", va="center", fontweight="bold")
    ax.annotate("performance decays", xy=(t[6], y[6]), xytext=(0.8, 0.968), fontsize=7.6, color=INK,
                ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8, shrinkA=2, shrinkB=3))
    ax.set_xlim(0, 60)
    ax.set_ylim(0.76, 0.99)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_xlabel("time")
    ax.set_ylabel("model performance")
    ax.spines[["top", "right"]].set_visible(False)
    stamp(ax, "schematic: invented data", y=1.01)
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / "class27_triggers.pdf")
    plt.close(fig)
    return retrain_at


if __name__ == "__main__":
    events = draw_triggers()
    print("figure written to", OUT, "| retraining runs at", events)
