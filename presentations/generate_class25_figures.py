"""Generate the figures used in the Class 25 slides.

Run from anywhere with the project environment:  python presentations/generate_class25_figures.py

Both figures are SCHEMATIC. The numbers are invented to make one point each about how to read a
sprint chart; they are not measurements of any team, and each figure says so on its face.

Figures
-------
class25_burndown.pdf  Schematic sprint burndown: a flat stretch (blocked work), a step up (scope added
                      mid-sprint) and an end above zero (unfinished work returns to the backlog).
class25_velocity.pdf  Schematic velocity over six sprints: committed versus completed points, and the
                      rolling average of the last three sprints used as planning capacity.
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


# --------------------------------------------------------------------------------------
# 1. Burndown of one two-week sprint (10 working days), invented numbers
# --------------------------------------------------------------------------------------
def draw_burndown():
    days = np.arange(0, 11)
    total = 30
    ideal = total - total * days / 10
    # remaining story points at the end of each day
    actual = np.array([30, 29, 27, 27, 27, 31, 27, 21, 14, 8, 4])

    fig, ax = plt.subplots(figsize=(3.7, 2.2))
    ax.axvspan(2.0, 4.0, color=RED, alpha=0.08, linewidth=0, zorder=0)
    ax.plot(days, ideal, color=HAIR, lw=1.6, ls="--", zorder=2)
    ax.plot(days, actual, color=BLUE, lw=2.2, marker="o", ms=3.6, mfc="white", mew=1.4,
            solid_capstyle="round", zorder=3)

    ax.text(10.15, 0.0, "ideal", color=MUTED, fontsize=8, va="center", ha="left")
    ax.annotate("blocked: no data yet", xy=(3.0, 27), xytext=(3.0, 34.6), ha="center", va="center",
                fontsize=8, color=INK, arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8, shrinkB=3))
    ax.annotate("scope added", xy=(5, 31), xytext=(6.9, 33.6), ha="center", va="center", fontsize=8, color=INK,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8, shrinkB=3))
    ax.annotate("4 points unfinished:\nback to the backlog", xy=(10, 4), xytext=(9.3, 21.5), ha="center",
                va="center", fontsize=8, color=INK, linespacing=1.1,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8, shrinkB=3))

    ax.set_xlim(0, 11.6)
    ax.set_ylim(-1, 37)
    ax.set_xticks([0, 2, 4, 6, 8, 10])
    ax.set_xlabel("sprint day")
    ax.set_ylabel("points remaining")
    ax.spines[["top", "right"]].set_visible(False)
    stamp(ax, "schematic: invented data", y=1.01)
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / "class25_burndown.pdf")
    plt.close(fig)


# --------------------------------------------------------------------------------------
# 2. Velocity over six sprints, invented numbers
# --------------------------------------------------------------------------------------
def draw_velocity():
    sprints = np.arange(1, 7)
    committed = np.array([20, 22, 24, 20, 22, 20])
    completed = np.array([14, 18, 21, 17, 20, 19])
    capacity = completed[-3:].mean()  # rolling average of the last three sprints

    fig, ax = plt.subplots(figsize=(3.7, 2.2))
    w = 0.36
    ax.bar(sprints - w / 2, committed, w, facecolor=ICE, edgecolor=HAIR, lw=1.0, zorder=2)
    ax.bar(sprints + w / 2, completed, w, facecolor=BLUE, edgecolor="white", lw=0.6, zorder=3)
    ax.axhline(capacity, color=GOLD, lw=1.8, ls="--", zorder=4)
    ax.annotate(f"planning capacity ≈ {capacity:.0f} points\n(mean of the last 3 sprints)",
                xy=(2.55, capacity), xytext=(0.55, 29.5), ha="left", va="center", fontsize=8, color=INK,
                linespacing=1.1, zorder=6,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8, shrinkA=2, shrinkB=2))

    # legend drawn by hand: two swatches, text in ink
    ax.text(5.55, 31.9, "committed", fontsize=8, color=INK, ha="left", va="center")
    ax.text(5.55, 29.3, "completed", fontsize=8, color=INK, ha="left", va="center")
    ax.add_patch(plt.Rectangle((5.18, 31.3), 0.3, 1.2, facecolor=ICE, edgecolor=HAIR, lw=1.0, clip_on=False))
    ax.add_patch(plt.Rectangle((5.18, 28.7), 0.3, 1.2, facecolor=BLUE, edgecolor="white", lw=0.6, clip_on=False))

    ax.set_xlim(0.4, 7.1)
    ax.set_ylim(0, 34)
    ax.set_xticks(sprints)
    ax.set_xlabel("sprint")
    ax.set_ylabel("story points")
    ax.spines[["top", "right"]].set_visible(False)
    stamp(ax, "schematic: invented data", y=1.01)
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / "class25_velocity.pdf")
    plt.close(fig)


if __name__ == "__main__":
    draw_burndown()
    draw_velocity()
    print("figures written to", OUT)
