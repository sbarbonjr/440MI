"""Generate the figure used in the Class 27 slides.

Run from anywhere with the project environment:  python presentations/generate_class27_figures.py

The figure is SCHEMATIC. The values are invented to show how a performance metric decays, how crossing
an agreed limit starts a retraining run, and how a newly promoted model restores it; it is not data from
any model in this course, and the figure says so on its face. It is drawn at the size it appears on the
slide (6.6 cm wide), so the text is legible without scaling.

Figures
-------
class27_triggers.pdf  One trigger in action (performance decay). The model in use decays, crosses the
                      agreed limit, a train-and-gate run starts (the old model keeps serving during it),
                      and a promoted model restores performance. The cycle then repeats.
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
    """One cycle told clearly: decay -> limit crossed -> train + gate -> promoted model -> decay again."""
    limit, top, run_len = 0.80, 0.93, 6.0

    def decay(t):
        return top - 0.0066 * t - 0.00004 * t * t

    t_cross = float(np.interp(limit, [decay(x) for x in np.arange(60, 0, -0.01)], np.arange(60, 0, -0.01)))
    t_x = [0.0, t_cross + run_len]                     # first cycle: old model, then promotion
    t_x.append(t_x[1] + t_cross + run_len)             # second cycle
    xmax = 56.0

    fig, ax = plt.subplots(figsize=(2.6, 1.55))
    ax.axhline(limit, color=GOLD, lw=1.1, ls="--", zorder=2)
    ax.text(0.8, limit - 0.004, "agreed limit", fontsize=6.4, color=INK, ha="left", va="top")

    marks = []
    for a, b in zip(t_x[:-1], t_x[1:]):
        t = np.linspace(a, min(b, xmax), 200)
        ax.plot(t, decay(t - a), color=BLUE, lw=1.4, zorder=3)
        tc = a + t_cross
        if tc < xmax:
            ax.axvspan(tc, min(tc + run_len, xmax), color=GREEN, alpha=0.16, lw=0, zorder=1)
            ax.plot([tc], [limit], "o", ms=3.6, color=RED, zorder=4)
            marks.append(tc)
        if b < xmax:   # the promoted model replaces the old one
            ax.annotate("", xy=(b, top), xytext=(b, decay(b - a)),
                        arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.0, ls="--", shrinkA=0, shrinkB=0),
                        zorder=4)
    last = t_x[-1]
    t = np.linspace(last, xmax, 60)
    ax.plot(t, decay(t - last), color=BLUE, lw=1.4, zorder=3)

    c1 = marks[0]
    ax.text(1.0, 0.972, "model decays", fontsize=6.4, color=INK, ha="left", va="center")
    ax.text(c1 - 0.8, 0.762, "trigger fires", fontsize=6.4, color=INK, ha="right", va="center")
    ax.annotate("", xy=(c1, limit - 0.006), xytext=(c1 - 0.6, 0.772),
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.6, shrinkA=0, shrinkB=0))
    ax.text(c1 + 2.4, 0.885, "train + gate", fontsize=6.0, color=GREEN, ha="center", va="center",
            rotation=90, fontweight="bold")
    ax.text(t_x[1] + 1.0, 0.953, "new model promoted", fontsize=6.4, color=INK, ha="left", va="center")

    ax.set_xlim(0, xmax)
    ax.set_ylim(0.74, 0.99)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("time", fontsize=6.8, labelpad=2)
    ax.set_ylabel("model performance", fontsize=6.8, labelpad=2)
    ax.set_title("Example: the performance-decay trigger", fontsize=7, fontweight="bold", loc="left", pad=3)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.99, 0.015, "schematic: invented data", fontsize=5.8, color=MUTED, style="italic", ha="right", va="bottom")
    fig.tight_layout(pad=0.3, rect=(0, 0.045, 1, 1))
    fig.savefig(OUT / "class27_triggers.pdf")
    plt.close(fig)
    return marks


if __name__ == "__main__":
    events = draw_triggers()
    print("figure written to", OUT, "| limit crossed at", [round(e, 1) for e in events])
