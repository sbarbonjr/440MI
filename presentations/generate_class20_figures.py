"""Generate the data figures used in the Class 20 slides.

Run from anywhere with the project environment:  python presentations/generate_class20_figures.py

Figures
-------
class20_api_behavior.pdf    Measured: how the low- and high-quality services answer six requests.
class20_cost_schematic.pdf  Schematic (no measured data): cumulative cost of a long-lived system.
class20_sse_stream.pdf      Measured: one simulated pasteurization batch as the server streams it.
"""
import importlib.util
import json
import sys
import tempfile
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(exist_ok=True)

# Course palette (same hexes as common.tex). Text always wears INK; colour rides on marks.
BLUE, GOLD, GREEN = "#12355B", "#C98A2E", "#2F6B4F"
RED = "#A23B2A"          # status colour: failure (same family as the fraud class in Class 18 figures)
INK, GRAY, MUTED = "#12355B", "#4B5563", "#6B7280"
ICE, HAIR = "#EEF3F8", "#CBD5E1"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.labelcolor": INK,
    "text.color": INK,
    "axes.edgecolor": HAIR,
    "xtick.color": GRAY,
    "ytick.color": GRAY,
    "pdf.fonttype": 42,
})
MONO = {"family": "DejaVu Sans Mono"}


# --------------------------------------------------------------------------------------
# 1. API behaviour matrix (measured by calling both implementations with the Flask test client)
# --------------------------------------------------------------------------------------
def load_fraud_api():
    spec = importlib.util.spec_from_file_location("fraud_api", ROOT / "serving" / "fraud_api.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.LOG_PATH = Path(tempfile.mkdtemp()) / "predictions.jsonl"  # keep the repo's logs/ untouched
    return module


def load_legacy_client():
    """Execute the real source of Class6_model_api.py, patching only the missing pickle path."""
    src = (ROOT / "Class6_model_api.py").read_text()
    src = src.replace("notebooks/best_random_forest_model.pkl", str(ROOT / "streamlit" / "model.pkl"))
    namespace = {"__name__": "legacy_api"}
    exec(compile(src, "Class6_model_api.py", "exec"), namespace)
    namespace["app"].config["PROPAGATE_EXCEPTIONS"] = False  # unhandled errors become HTTP 500
    namespace["app"].logger.disabled = True
    return namespace["app"].test_client()


def classify(status, valid_case):
    if valid_case:
        return "ok" if status == 200 else "crash"
    if status == 200:
        return "silent"       # invalid input accepted and answered
    if 400 <= status < 500:
        return "rejected"
    return "crash"


def behaviour_matrix():
    fraud = load_fraud_api()
    good = fraud.app.test_client()
    legacy = load_legacy_client()
    mean = [float(v) for v in fraud.SCALER.mean_]
    head = ",".join(str(v) for v in mean[:-1])
    cases = [  # (label, raw body, is the request valid?)
        ("valid vector (30 numbers)", json.dumps({"features": mean}), True),
        ("no \"features\" key", json.dumps({"x": mean}), False),
        ("29 values instead of 30", json.dumps({"features": mean[:-1]}), False),
        ("text instead of a number", json.dumps({"features": mean[:-1] + ["abc"]}), False),
        ("NaN instead of a number", '{"features": [' + head + ", NaN]}", False),
        ("JSON list, not an object", json.dumps(mean), False),
    ]
    rows = []
    for label, body, valid in cases:
        row = {"label": label, "valid": valid}
        for key, client in (("legacy", legacy), ("fixed", good)):
            status = client.post("/predict", data=body, content_type="application/json").status_code
            row[key] = (status, classify(status, valid))
        rows.append(row)
    return rows


def draw_behaviour(rows):
    style = {  # kind -> (icon, text, status colour, tint strength)
        "ok": ("✓", "prediction", GREEN, 0.14),
        "rejected": ("✓", "rejected", GREEN, 0.14),
        "crash": ("✗", "crash", RED, 0.14),
        "silent": ("!", "answered anyway", RED, 0.30),
    }
    fig, ax = plt.subplots(figsize=(7.4, 3.3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(rows) + 2.15)
    ax.axis("off")
    x_label, x_leg, x_fix, w = 0.0, 4.15, 7.1, 2.9
    top = len(rows) + 1.2
    ax.text(x_leg + w / 2, top + 0.35, "Low-quality service", ha="center", va="center",
            fontsize=10.5, fontweight="bold")
    ax.text(x_fix + w / 2, top + 0.35, "High-quality service", ha="center", va="center",
            fontsize=10.5, fontweight="bold")
    ax.text(x_leg + w / 2, top - 0.08, "legacy, model path patched", ha="center", va="center",
            fontsize=8.5, color=MUTED)
    ax.text(x_fix + w / 2, top - 0.08, "corrected counterpart", ha="center", va="center",
            fontsize=8.5, color=MUTED)
    for i, row in enumerate(rows):
        y = len(rows) - i - 0.1
        ax.text(x_label, y + 0.4, row["label"], ha="left", va="center", fontsize=10.5)
        for key, x in (("legacy", x_leg), ("fixed", x_fix)):
            status, kind = row[key]
            icon, word, colour, tint = style[kind]
            ax.add_patch(FancyBboxPatch((x, y + 0.02), w, 0.76,
                                        boxstyle="round,pad=0,rounding_size=0.12",
                                        fc=colour, ec="none", alpha=tint, lw=0))
            ax.text(x + 0.18, y + 0.4, icon, ha="left", va="center", fontsize=13,
                    fontweight="bold", color=colour)
            ax.text(x + 0.62, y + 0.4, f"{status}", ha="left", va="center", fontsize=10.5,
                    fontweight="bold")
            ax.text(x + 1.2, y + 0.4, word, ha="left", va="center", fontsize=9.5)
    invalid = [r for r in rows if not r["valid"]]
    for key, x in (("legacy", x_leg), ("fixed", x_fix)):
        good = sum(r[key][1] == "rejected" for r in invalid)
        ax.text(x + w / 2, -0.28, f"invalid rejected: {good} of {len(invalid)}", ha="center",
                va="center", fontsize=10.5, fontweight="bold")
    ax.set_ylim(-0.6, len(rows) + 1.7)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "class20_api_behavior.pdf")
    plt.close(fig)


# --------------------------------------------------------------------------------------
# 2. Cost schematic (shape only: no measured data)
# --------------------------------------------------------------------------------------
def draw_cost_schematic():
    t = np.linspace(0, 8, 200)
    classic = 1 + 0.30 * t
    ml = 1 + 0.30 * t + 0.20 * t + 0.025 * t ** 2
    fig, ax = plt.subplots(figsize=(6.0, 3.5))
    ax.axhline(1, color=HAIR, linewidth=1.0, zorder=1)
    ax.fill_between(t, classic, ml, color=GOLD, alpha=0.14, linewidth=0, zorder=1)
    ax.plot(t, classic, color=BLUE, linewidth=2, solid_capstyle="round", zorder=3)
    ax.plot(t, ml, color=GOLD, linewidth=2, solid_capstyle="round", zorder=3)
    for x, y, c in ((8, classic[-1], BLUE), (8, ml[-1], GOLD)):
        ax.plot([x], [y], "o", color=c, markersize=8, markeredgecolor="white", markeredgewidth=2, zorder=4)
    ax.text(8.35, classic[-1], "software system", ha="left", va="center", fontsize=8.8)
    ax.text(8.35, ml[-1], "ML-enabled\nsystem", ha="left", va="center", fontsize=8.8)
    ax.text(10.95, 1.08, "initial development = 1", ha="right", va="bottom", fontsize=8.3, color=GRAY)
    ax.text(6.55, (classic[160] + ml[160]) / 2, "extra cost of keeping\nthe model trustworthy",
            fontsize=8, color=GRAY, ha="center", va="center", linespacing=1.15)
    ax.set_xlim(0, 11.0)
    ax.set_ylim(0.6, 7.4)
    ax.set_xlabel("years after first release")
    ax.set_ylabel("cumulative cost (relative)")
    ax.set_yticks([])
    ax.set_xticks(range(0, 9, 2))
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(0.99, 0.97, "schematic: shape only, no measured data", transform=ax.transAxes, ha="right",
            va="top", fontsize=7.5, color=MUTED, style="italic")
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / "class20_cost_schematic.pdf")
    plt.close(fig)


# --------------------------------------------------------------------------------------
# 3. One pasteurization batch, as the /stream endpoint emits it (one reading per second)
# --------------------------------------------------------------------------------------
def draw_stream(now_s=130):
    sys.path.insert(0, str(ROOT / "pasteurization"))
    from synth_sensors import simulate_batch

    df, _ = simulate_batch(1)
    t = (df["timestamp"] - df["timestamp"].iloc[0]).to_numpy()
    runs = (df["state"] != df["state"].shift()).cumsum()
    spans = [(t[g.index[0]], t[g.index[-1]], g["state"].iloc[0]) for _, g in df.groupby(runs)]
    k = int(np.argmin(np.abs(t - now_s)))

    fig, ax = plt.subplots(figsize=(9.2, 3.05))
    for i, (a, b, name) in enumerate(spans):
        if i % 2 == 0:
            ax.axvspan(a, b, color=ICE, zorder=0)
        ax.text((a + b) / 2, 1.02, name, transform=ax.get_xaxis_transform(), ha="center",
                va="bottom", fontsize=8, color=GRAY)
    ax.plot(t[k:], df["T"].to_numpy()[k:], color=HAIR, linewidth=2, solid_capstyle="round", zorder=2)
    ax.plot(t[: k + 1], df["T"].to_numpy()[: k + 1], color=BLUE, linewidth=2, solid_capstyle="round",
            zorder=3)
    ax.plot([t[k]], [df["T"].iloc[k]], "o", color=GOLD, markersize=9, markeredgecolor="white",
            markeredgewidth=2, zorder=5)
    row = df.iloc[k]
    event = (f'data: {{"timestamp": {row["timestamp"]:.1f}, "state": "{row["state"]}",\n'
             f'        "T": {row["T"]:.1f}, "pH": {row["pH"]:.2f}, ...}}')
    ax.annotate(event, xy=(t[k], df["T"].iloc[k]), xytext=(0.02, 0.68), textcoords="axes fraction",
                va="top", ha="left", fontsize=8, **MONO,
                bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=HAIR, lw=1),
                arrowprops=dict(arrowstyle="-", color=GOLD, lw=1.5, shrinkA=2, shrinkB=6,
                                connectionstyle="arc3,rad=0.0"), zorder=6)
    ax.text(t[k] - 13, 15, "already sent", ha="right", fontsize=8.5, color=GRAY)
    ax.text(t[k] + 7, 15, "not produced yet", ha="left", fontsize=8.5, color=MUTED)
    ax.set_xlabel("time $t$ [s]  (one reading per second)")
    ax.set_ylabel("temperature [°C]")
    ax.set_xlim(t[0], t[-1])
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / "class20_sse_stream.pdf")
    plt.close(fig)


if __name__ == "__main__":
    results = behaviour_matrix()
    for r in results:
        print(f'{r["label"]:<28} legacy={r["legacy"]}  fixed={r["fixed"]}')
    draw_behaviour(results)
    draw_cost_schematic()
    draw_stream()
