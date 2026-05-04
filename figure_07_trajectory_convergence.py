"""
figure_07_trajectory_convergence.py
=====================================
Trajectory convergence figure for MELV ABM V2.1.

Reads: validation_data_v2_1_2000.csv (full trajectory data)
       validation_summary_v2_1_2000.csv (outcome labels per run)

Produces:
  figures_v2_1/figure_07_trajectory_convergence.png

Shows mean_i(t) trajectories grouped by final outcome (COOP/COMP/THRESH),
demonstrating that populations converge to and stay in their respective
attractor basins rather than simply ending bimodal by chance.

Biological interpretation:
  COOP lines: descend from near i=1 and flatten below i=0.9
  COMP lines: rise from near i=1 and flatten above i=1.1
  THRESH lines: hover near i=1.0, slow or no drift — genuine boundary ecology
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

OUT_DIR = "figures_v2_1"
os.makedirs(OUT_DIR, exist_ok=True)

TEAL   = "#1A5276"
GREEN  = "#1E8449"
RED    = "#922B21"
ORANGE = "#CA6F1E"
GREY   = "#717D7E"

plt.rcParams.update({
    "font.family":    "sans-serif",
    "font.size":      11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "legend.fontsize": 9,
    "figure.dpi":     150,
})


def load_data():
    print("Loading trajectory data...")
    traj = pd.read_csv("validation_data_v2_1_2000.csv")
    summ = pd.read_csv("validation_summary_v2_1_2000.csv")
    summ = summ[summ["outcome"].isin(["COOP","COMP","THRESH"])].copy()
    # Merge outcome label onto trajectory rows
    traj = traj.merge(
        summ[["condition_id","replicate","outcome"]],
        on=["condition_id","replicate"], how="inner"
    )
    print(f"  {len(traj):,} trajectory rows loaded")
    print(f"  Outcomes: {dict(summ['outcome'].value_counts())}")
    return traj, summ


def build_mean_trajectories(traj, outcome, max_runs=60):
    """
    For a given outcome label, return an array of mean_i time series.
    Sample up to max_runs runs to keep the plot readable.
    """
    subset = traj[traj["outcome"] == outcome]
    runs   = subset.groupby(["condition_id","replicate"])

    series_list = []
    run_keys = list(runs.groups.keys())
    if len(run_keys) > max_runs:
        rng = np.random.default_rng(42)
        run_keys = [run_keys[i] for i in
                    rng.choice(len(run_keys), max_runs, replace=False)]

    for key in run_keys:
        grp = runs.get_group(key).sort_values("step")
        series_list.append(grp["mean_i"].values)

    return series_list


def figure_07_convergence(traj, summ):
    fig = plt.figure(figsize=(14, 10))

    # Layout: 3 individual panels + 1 overlay panel
    gs = fig.add_gridspec(2, 2, hspace=0.38, wspace=0.3)
    ax_coop   = fig.add_subplot(gs[0, 0])
    ax_comp   = fig.add_subplot(gs[0, 1])
    ax_thresh = fig.add_subplot(gs[1, 0])
    ax_all    = fig.add_subplot(gs[1, 1])

    outcome_config = {
        "COOP":   (ax_coop,   GREEN,  "COOP basin  (final mean i < 0.9)",   0.9,  0.10),
        "COMP":   (ax_comp,   RED,    "COMP basin  (final mean i > 1.1)",   1.1,  2.50),
        "THRESH": (ax_thresh, ORANGE, "THRESH  (0.9 ≤ final mean i ≤ 1.1)", None, None),
    }

    mean_curves = {}

    for outcome, (ax, color, title, h_line, h_val) in outcome_config.items():
        series = build_mean_trajectories(traj, outcome, max_runs=50)
        if not series:
            ax.text(0.5, 0.5, "No data", transform=ax.transAxes, ha="center")
            continue

        max_len = max(len(s) for s in series)
        x = np.arange(max_len) * 10   # steps (sampled every 10)

        # Individual trajectories
        for s in series:
            padded = np.pad(s, (0, max_len - len(s)), mode="edge")
            ax.plot(x, padded, color=color, alpha=0.12, linewidth=0.8)

        # Mean trajectory
        padded_all = np.vstack([
            np.pad(s, (0, max_len - len(s)), mode="edge") for s in series
        ])
        mean_curve = np.mean(padded_all, axis=0)
        std_curve  = np.std(padded_all, axis=0)
        mean_curves[outcome] = (x, mean_curve, color)

        ax.plot(x, mean_curve, color=color, linewidth=2.5,
                label=f"Mean (n={len(series)})", zorder=5)
        ax.fill_between(x, mean_curve - std_curve, mean_curve + std_curve,
                        color=color, alpha=0.15)

        # Threshold reference lines
        ax.axhline(0.9, color=GREY, linestyle=":", linewidth=1.2, alpha=0.7)
        ax.axhline(1.1, color=GREY, linestyle=":", linewidth=1.2, alpha=0.7)
        ax.axhline(1.0, color="black", linestyle="--", linewidth=1.0, alpha=0.4)

        ax.set_xlabel("Simulation step")
        ax.set_ylabel("Population mean i-factor")
        ax.set_title(f"Figure 7{list(outcome_config).index(outcome)+1} — {title}")
        ax.legend(loc="best")

        # Annotate final mean
        final_val = mean_curve[-1]
        ax.annotate(f"Final: {final_val:.3f}",
                    xy=(x[-1], final_val),
                    xytext=(-80, 15), textcoords="offset points",
                    fontsize=9, color=color,
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.2))

    # Overlay panel: mean trajectories for all three outcomes
    ax_all.axhline(0.9, color=GREY, linestyle=":", linewidth=1.2, alpha=0.7,
                   label="COOP/THRESH boundary (0.9)")
    ax_all.axhline(1.1, color=GREY, linestyle=":", linewidth=1.2, alpha=0.7,
                   label="COMP/THRESH boundary (1.1)")
    ax_all.axhline(1.0, color="black", linestyle="--", linewidth=1.0,
                   alpha=0.4, label="Bifurcation threshold (i=1)")

    for outcome, (x, mean_curve, color) in mean_curves.items():
        ax_all.plot(x, mean_curve, color=color, linewidth=2.5, label=f"{outcome} mean")

    ax_all.set_xlabel("Simulation step")
    ax_all.set_ylabel("Population mean i-factor")
    ax_all.set_title("Figure 7d — Mean trajectories by outcome\n(overlay)")
    ax_all.legend(loc="center right", fontsize=8)

    fig.suptitle(
        "Figure 7 — Trajectory convergence: MELV ABM V2.1 (2000 steps)\n"
        "Populations descend to COOP attractor or rise to COMP attractor and remain stable\n"
        "THRESH populations show genuine boundary ecology — slow drift near i = 1",
        fontsize=11, y=1.01
    )

    path = os.path.join(OUT_DIR, "figure_07_trajectory_convergence.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")


def late_stability_summary(traj, summ):
    """Print late-time stability metrics for each outcome."""
    print("\nLate-time stability (last 200 steps):")
    for outcome in ["COOP", "COMP", "THRESH"]:
        subset  = traj[traj["outcome"] == outcome]
        runs    = subset.groupby(["condition_id","replicate"])
        slopes  = []
        stds    = []
        for _, grp in runs:
            tail = grp.sort_values("step").tail(20)["mean_i"].values
            if len(tail) < 5:
                continue
            stds.append(float(np.std(tail)))
            x = np.arange(len(tail))
            slope = float(np.polyfit(x, tail, 1)[0])
            slopes.append(slope)

        if slopes:
            print(f"  {outcome:6s}  n={len(slopes):3d}  "
                  f"mean_slope={np.mean(slopes):+.5f}  "
                  f"mean_late_std={np.mean(stds):.4f}  "
                  f"max_late_std={np.max(stds):.4f}")


if __name__ == "__main__":
    traj, summ = load_data()
    print("\nGenerating Figure 7 — trajectory convergence...")
    figure_07_convergence(traj, summ)
    late_stability_summary(traj, summ)
    print("\nDone.")
