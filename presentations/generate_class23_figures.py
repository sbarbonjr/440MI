"""Generate the figures used in the Class 23 slides.

Run from anywhere with the project environment:  python presentations/generate_class23_figures.py

Both figures are SCHEMATIC. They carry no measured data: the curves and the positions are drawn to
make one point about matching process to risk, and each figure says so on its face.

Figures
-------
class23_uncertainty_vs_control.pdf  Schematic: uncertainty falls as a team learns, the control a system
                                    needs rises as it commits, and operation reopens uncertainty.
class23_process_positioning.pdf     Schematic: where the course cases sit when uncertainty and
                                    governance need are judged by the team (a judgment, not a measurement).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(exist_ok=True)

# Course palette (same hexes as common.tex). Text always wears INK; colour rides on marks.
BLUE, GOLD, GREEN = "#12355B", "#C98A2E", "#2F6B4F"
RED = "#A23B2A"
INK, GRAY, MUTED = "#12355B", "#4B5563", "#6B7280"
ICE, HAIR = "#EEF3F8", "#CBD5E1"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 7.5,
    "axes.labelcolor": INK,
    "text.color": INK,
    "axes.edgecolor": HAIR,
    "xtick.color": GRAY,
    "ytick.color": GRAY,
    "pdf.fonttype": 42,
})


def stamp(ax, text, x=1.0, y=1.0, ha="right", va="bottom"):
    """The honesty label: says on the figure that nothing here is measured."""
    ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va, fontsize=6.3, color=MUTED, style="italic")


# --------------------------------------------------------------------------------------
# 1. Uncertainty falls, required control rises, operation reopens uncertainty
# --------------------------------------------------------------------------------------
def draw_uncertainty_vs_control():
    x = np.linspace(0, 4, 400)
    # uncertainty: logistic fall until stabilisation, then a small rise (drift reopens it)
    fall = 1 / (1 + np.exp(3.2 * (x - 1.6)))
    rise = 0.20 / (1 + np.exp(-6 * (x - 3.5)))
    uncertainty = 0.08 + 0.87 * fall + rise
    control = 0.08 + 0.84 / (1 + np.exp(-3.2 * (x - 2.5)))

    fig, ax = plt.subplots(figsize=(3.6, 2.75))
    ax.axvspan(-0.5, 2.5, color=GOLD, alpha=0.10, linewidth=0, zorder=0)
    ax.axvspan(2.5, 4.5, color=BLUE, alpha=0.08, linewidth=0, zorder=0)
    ax.text(1.0, 1.12, "exploratory: agile loops", ha="center", va="center", fontsize=6.8, color=INK,
            fontweight="bold")
    ax.text(3.5, 1.12, "controlled: gated delivery", ha="center", va="center", fontsize=6.8, color=INK,
            fontweight="bold")
    ax.plot(x, uncertainty, color=GOLD, lw=2.2, solid_capstyle="round", zorder=3)
    ax.plot(x, control, color=BLUE, lw=2.2, solid_capstyle="round", zorder=3)
    ax.text(0.15, 0.58, "uncertainty\nabout data and\nrequirements", ha="left", va="center", fontsize=7.2,
            color=INK, fontweight="bold", linespacing=1.1)
    ax.text(0.15, 0.24, "control the\nsystem needs", ha="left", va="center", fontsize=7.2, color=INK,
            fontweight="bold", linespacing=1.1)
    ax.annotate("drift reopens\nuncertainty", xy=(4.0, uncertainty[-1]), xytext=(3.35, 0.50), ha="center",
                va="center", fontsize=6.4, color=GRAY, linespacing=1.1,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8, shrinkA=2, shrinkB=2))
    ax.set_xticks(range(5))
    ax.set_xticklabels(["Discover", "Explore", "Prototype", "Stabilize", "Operate"], fontsize=6.4)
    ax.set_yticks([])
    ax.set_xlim(-0.5, 4.5)
    ax.set_ylim(0, 1.25)
    ax.set_ylabel("relative level")
    ax.spines[["top", "right"]].set_visible(False)
    stamp(ax, "schematic: shape only, no measured data", y=1.0)
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / "class23_uncertainty_vs_control.pdf")
    plt.close(fig)


# --------------------------------------------------------------------------------------
# 2. Where the course cases sit (a judgment of the team, not a measurement)
# --------------------------------------------------------------------------------------
def draw_positioning():
    fig, ax = plt.subplots(figsize=(3.4, 2.85))
    zones = [  # (x0, y0, w, h, label, colour, label position)
        (0.0, 0.5, 0.5, 0.5, "plan-driven", BLUE, (0.25, 0.95)),
        (0.5, 0.5, 0.5, 0.5, "hybrid", GREEN, (0.75, 0.95)),
        (0.5, 0.0, 0.5, 0.5, "agile", GOLD, (0.75, 0.05)),
        (0.0, 0.0, 0.5, 0.5, "either, kept light", GRAY, (0.25, 0.05)),
    ]
    for x0, y0, w, h, label, colour, (lx, ly) in zones:
        ax.add_patch(Rectangle((x0, y0), w, h, facecolor=colour, alpha=0.10, edgecolor="white", lw=1.5))
        ax.text(lx, ly, label, ha="center", va="center", fontsize=7.4, fontweight="bold", color=INK)
    cases = [  # label, uncertainty, governance, text offset, alignment
        ("Hospital ML tool", 0.58, 0.80, (0.035, 0.0), "left"),
        ("Pasteurization", 0.56, 0.62, (0.035, 0.0), "left"),
        ("Fraud API", 0.70, 0.40, (0.0, -0.075), "center"),
    ]
    for label, cx, cy, (dx, dy), ha in cases:
        ax.plot([cx], [cy], "o", color=INK, markersize=7, markeredgecolor="white", markeredgewidth=1.4, zorder=4)
        ax.text(cx + dx, cy + dy, label, ha=ha, va="center", fontsize=7, fontweight="bold", color=INK,
                zorder=5, bbox=dict(fc="white", ec="none", pad=0.8, alpha=0.9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([0.05, 0.95])
    ax.set_xticklabels(["low", "high"])
    ax.set_yticks([0.05, 0.95])
    ax.set_yticklabels(["low", "high"], rotation=90, va="center")
    ax.tick_params(length=0)
    ax.set_xlabel("uncertainty about requirements and data")
    ax.set_ylabel("governance need (regulation, criticality)")
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    stamp(ax, "illustrative placement: a judgment, not a measurement", y=1.01)
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / "class23_process_positioning.pdf")
    plt.close(fig)


if __name__ == "__main__":
    draw_uncertainty_vs_control()
    draw_positioning()
    print("figures written to", OUT)
