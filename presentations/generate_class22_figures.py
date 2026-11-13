"""Generate the figures used in the Class 22 slides.

Run from anywhere with the project environment:  python presentations/generate_class22_figures.py

Every figure is ILLUSTRATIVE. The numbers are synthetic (seeded) or purely schematic, chosen to make
one point about writing requirements, and each figure says so on its face. None of them is a
measurement of a real system. The numbers quoted on the slides are printed by this script.

Figures
-------
class22_latency_runs.pdf         Synthetic: two simulated load tests, same mean, different tail.
class22_f1_by_category.pdf       Synthetic: a passing macro-F1 that hides one weak category.
class22_automation_tradeoff.pdf  Schematic (no data): workload versus wrong routings as automation grows.
class22_relevant_in_top5.pdf     Synthetic: relevant books among the five suggested, for 100 profiles.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(exist_ok=True)

# Course palette (same hexes as common.tex). Text always wears INK; colour rides on marks.
BLUE, GOLD, GREEN = "#12355B", "#C98A2E", "#2F6B4F"
RED = "#A23B2A"          # status colour: failure (same as the fraud/failure red of Class 20)
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


def stamp(ax, text, x=0.995, y=1.0, ha="right", va="bottom"):
    """The honesty label: says on the figure that the numbers are not measurements."""
    ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va, fontsize=6.3, color=MUTED, style="italic")


# --------------------------------------------------------------------------------------
# 1. Two simulated load tests with the same mean and a different tail
# --------------------------------------------------------------------------------------
def draw_latency():
    rng = np.random.default_rng(22)
    n, limit = 3000, 2.0
    run_a = rng.lognormal(np.log(0.9), 0.35, size=n)
    n_slow = n // 10
    run_b = np.concatenate([rng.lognormal(np.log(0.7), 0.20, size=n - n_slow),
                            rng.lognormal(np.log(3.0), 0.25, size=n_slow)])
    rng.shuffle(run_b)
    bins = np.arange(0, 5.01, 0.1)

    fig, axes = plt.subplots(2, 1, figsize=(3.55, 2.75), sharex=True)
    stats = []
    for ax, data, name in zip(axes, (run_a, run_b), ("Run A", "Run B")):
        counts, edges = np.histogram(np.clip(data, 0, 4.99), bins=bins)
        centres = edges[:-1] + 0.05
        ax.bar(centres, counts, width=0.095, color=[BLUE if c < limit else RED for c in centres], zorder=2)
        within = float((data <= limit).mean())
        mean = float(data.mean())
        ok = within >= 0.95
        top = counts.max()
        ax.axvline(limit, color=GOLD, lw=1.4, ls=(0, (4, 2)), zorder=3)
        ax.plot([mean], [0], marker="v", color=INK, markersize=5, markeredgecolor="white",
                markeredgewidth=0.8, zorder=5, clip_on=False)
        ax.text(mean + 0.12, top * 0.97, f"mean {mean:.2f} s", ha="left", va="top", fontsize=6.8, color=INK)
        ax.text(0.995, 0.93, f"{within * 100:.1f}% within {limit:.0f} s", transform=ax.transAxes, ha="right",
                va="top", fontsize=7.4, fontweight="bold", color=GREEN if ok else RED)
        ax.text(0.995, 0.66, ("✓ meets R1" if ok else "✗ fails R1"), transform=ax.transAxes,
                ha="right", va="top", fontsize=7.4, fontweight="bold", color=GREEN if ok else RED)
        ax.text(0.005, 0.93, name, transform=ax.transAxes, ha="left", va="top", fontsize=8, fontweight="bold")
        ax.set_yticks([])
        ax.set_ylim(0, top * 1.12)
        ax.set_xlim(0, 5)
        ax.spines[["top", "right", "left"]].set_visible(False)
        stats.append((name, mean, within))
    axes[0].text(limit + 0.06, axes[0].get_ylim()[1] * 0.60, "limit 2 s", ha="left", va="center",
                 fontsize=6.8, color=GOLD, fontweight="bold")
    axes[1].set_xlabel("response time [s]")
    stamp(axes[0], "synthetic illustration: 3,000 simulated requests per run", x=1.0, y=1.04)
    fig.tight_layout(pad=0.4, h_pad=0.5)
    fig.savefig(OUT / "class22_latency_runs.pdf")
    plt.close(fig)
    for name, mean, within in stats:
        print(f"latency  {name}: mean={mean:.2f} s  within 2 s={within * 100:.1f}%")


# --------------------------------------------------------------------------------------
# 2. A passing macro-F1 that hides one weak category
# --------------------------------------------------------------------------------------
def draw_f1_by_category():
    cats = ["Billing", "Account access", "Technical issue", "Shipping", "Returns", "Feedback",
            "Legal & privacy"]
    f1 = np.array([0.93, 0.90, 0.88, 0.86, 0.82, 0.74, 0.54])
    support = np.array([260, 190, 170, 120, 100, 100, 60])
    assert support.sum() == 1000
    macro = float(f1.mean())
    threshold = 0.80

    fig, ax = plt.subplots(figsize=(3.5, 2.65))
    ys = np.arange(len(cats) + 1)[::-1].astype(float)     # macro bar on top, one row above the rest
    ys[0] += 0.55
    ax.barh(ys[0], macro, height=0.62, color=GOLD, zorder=2)
    ax.barh(ys[1:], f1, height=0.62, color=[BLUE] * (len(cats) - 1) + [RED], zorder=2)
    ax.axvline(threshold, color=GOLD, lw=1.3, ls=(0, (4, 2)), zorder=3)
    ax.text(macro - 0.015, ys[0], f"{macro:.2f}", ha="right", va="center", fontsize=7.6, fontweight="bold",
            color="white")
    for y, v, k in zip(ys[1:], f1, support):
        ax.text(v + 0.015, y, f"{v:.2f}", ha="left", va="center", fontsize=7.2, zorder=5,
                bbox=dict(fc="white", ec="none", pad=0.8))
        ax.text(1.17, y, f"{k}", ha="right", va="center", fontsize=6.8, color=MUTED,
                transform=ax.get_yaxis_transform(), clip_on=False)
    ax.text(1.17, ys[0], "tickets", ha="right", va="center", fontsize=6.6, color=MUTED, style="italic",
            transform=ax.get_yaxis_transform(), clip_on=False)
    ax.set_yticks(ys)
    ax.set_yticklabels(["macro-F1\n(average)"] + cats, fontsize=7.2)
    ax.get_yticklabels()[0].set_fontweight("bold")
    ax.set_xlim(0, 1.0)
    ax.set_ylim(-0.6, ys[0] + 0.65)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel("F1 score")
    ax.text(threshold - 0.012, ys[0] + 0.55, "R2 threshold 0.80", ha="right", va="center", fontsize=6.6,
            color=GOLD, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    stamp(ax, "synthetic illustration: 1,000 held-out tickets", x=1.18, y=1.02)
    fig.subplots_adjust(left=0.30, right=0.86, top=0.93, bottom=0.15)
    fig.savefig(OUT / "class22_f1_by_category.pdf")
    plt.close(fig)
    print(f"f1       macro={macro:.2f}  weakest={cats[-1]} {f1[-1]:.2f} (n={support[-1]})")


# --------------------------------------------------------------------------------------
# 3. Automation trade-off (shape only: no measured data)
# --------------------------------------------------------------------------------------
def draw_tradeoff():
    x = np.linspace(0, 100, 200)
    workload = 1.0 - 0.85 * (x / 100)
    wrong = 0.10 + 0.90 * (x / 100) ** 2.2

    fig, ax = plt.subplots(figsize=(2.75, 2.45))
    ax.fill_between(x, workload, wrong, where=wrong > workload, color=GOLD, alpha=0.13, linewidth=0, zorder=1)
    ax.plot(x, workload, color=BLUE, lw=2, solid_capstyle="round", zorder=3)
    ax.plot(x, wrong, color=RED, lw=2, solid_capstyle="round", zorder=3)
    ax.plot([0], [workload[0]], "o", color=BLUE, markersize=6, markeredgecolor="white", markeredgewidth=1.2,
            zorder=4, clip_on=False)
    ax.plot([0], [wrong[0]], "o", color=RED, markersize=6, markeredgecolor="white", markeredgewidth=1.2,
            zorder=4, clip_on=False)
    ax.axvline(0, color=GOLD, lw=1.6, zorder=2)
    ax.text(4, 1.12, "first release:\nevery ticket confirmed", ha="left", va="top", fontsize=6.6,
            color=GOLD, fontweight="bold", linespacing=1.15)
    ax.text(6, 0.45, "operator\nworkload", ha="left", va="center", fontsize=7.4, color=BLUE,
            fontweight="bold", linespacing=1.1)
    ax.text(80, 0.90, "wrongly routed\ntickets", ha="right", va="center", fontsize=7.4, color=RED,
            fontweight="bold", linespacing=1.1)
    ax.set_xlim(-3, 100)
    ax.set_ylim(0, 1.16)
    ax.set_xticks([0, 50, 100])
    ax.set_yticks([])
    ax.set_xlabel("tickets routed without confirmation [%]")
    ax.set_ylabel("relative to today")
    ax.spines[["top", "right"]].set_visible(False)
    stamp(ax, "schematic: shape only, no measured data", x=1.0, y=1.0)
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / "class22_automation_tradeoff.pdf")
    plt.close(fig)


# --------------------------------------------------------------------------------------
# 4. How many relevant books does each reader profile receive among the five suggested?
# --------------------------------------------------------------------------------------
def draw_top5():
    counts = np.array([14, 22, 25, 20, 13, 6])           # profiles with 0, 1, ..., 5 relevant books
    assert counts.sum() == 100
    at_least_one = int(counts[1:].sum())
    three_plus = int(counts[3:].sum())
    k = np.arange(6)

    fig, ax = plt.subplots(figsize=(3.2, 2.55))
    ax.bar(k, counts, width=0.72, color=[RED] + [BLUE] * 5, zorder=2)
    for xi, c in zip(k, counts):
        ax.text(xi, c + 0.7, str(c), ha="center", va="bottom", fontsize=7.6, fontweight="bold")
    # bracket: profiles that meet L3's "at least one relevant book"
    ax.plot([0.62, 5.4], [33.5, 33.5], color=GREEN, lw=1.4)
    ax.plot([0.62, 0.62], [32.3, 33.5], color=GREEN, lw=1.4)
    ax.plot([5.4, 5.4], [32.3, 33.5], color=GREEN, lw=1.4)
    ax.text(3.0, 34.4, f"{at_least_one} of 100 profiles have at least one\nrelevant book: L3 passes",
            ha="center", va="bottom", fontsize=7, fontweight="bold", color=GREEN, linespacing=1.15)
    ax.plot([2.62, 5.4], [28.0, 28.0], color=GOLD, lw=1.4)
    ax.plot([2.62, 2.62], [27.0, 28.0], color=GOLD, lw=1.4)
    ax.plot([5.4, 5.4], [27.0, 28.0], color=GOLD, lw=1.4)
    ax.text(4.0, 28.7, f"only {three_plus} have three or more", ha="center", va="bottom", fontsize=6.9,
            fontweight="bold", color=GOLD)
    ax.set_xticks(k)
    ax.set_xlabel("relevant books among the five suggested")
    ax.set_ylabel("reader profiles")
    ax.set_xlim(-0.6, 5.6)
    ax.set_ylim(0, 41)
    ax.set_yticks([0, 10, 20, 30])
    ax.spines[["top", "right"]].set_visible(False)
    stamp(ax, "synthetic illustration: 100 simulated profiles", x=1.0, y=1.0)
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / "class22_relevant_in_top5.pdf")
    plt.close(fig)
    print(f"top5     at least one={at_least_one}  three or more={three_plus}")


if __name__ == "__main__":
    draw_latency()
    draw_f1_by_category()
    draw_tradeoff()
    draw_top5()
