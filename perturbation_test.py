"""
perturbation_test.py
====================
ESS Mutant Invasion Test for MELV ABM V2.1

Biological basis (Maynard Smith 1982; Nowak 2006):
  True attractor basins are evolutionarily stable strategies (ESS):
  a resident population resists invasion by rare mutants with opposite
  i-factor strategy. This test directly answers "are these real attractor
  basins?" by:

  1. Running a population to resolution (COOP or COMP).
  2. At step 1000, injecting a pulse of opposite-strategy invaders
     (25% of population replaced with high-i agents into COOP populations,
     or low-i agents into COMP populations).
  3. Running 400 more steps and measuring whether the population returns
     to its original basin.

  Recovery rate > 85% is the biological target for ESS-consistent stability
  (following Nowak 2006; Grok review, April 2026).

Usage:
    python perturbation_test.py

Output:
    perturbation_results.csv
    figures_v2_1/figure_05_perturbation.png
    figures_v2_1/figure_06_invasion_trajectories.png

Prints recovery rate summary to console.
"""

import os
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from melv_abm_v2_1 import MELVModel, MELVAgent

# ── Styling ──────────────────────────────────────────────────────────────────
TEAL   = "#1A5276"
GREEN  = "#1E8449"
RED    = "#922B21"
ORANGE = "#CA6F1E"
GREY   = "#717D7E"

plt.rcParams.update({
    "font.family":    "sans-serif",
    "font.size":      11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.dpi":     150,
})

OUT_DIR = "figures_v2_1"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Parameters ────────────────────────────────────────────────────────────────
WARMUP_STEPS      = 1000   # steps to reach resolution before invasion
INVASION_FRACTION = 0.25   # fraction of agents replaced by invaders
RECOVERY_STEPS    = 400    # steps after invasion to assess recovery
N_TESTS           = 40     # number of resolved runs to test (20 COOP + 20 COMP)

# Representative conditions spanning the parameter space
# Format: (R, I_freq, K, epsilon, seed_base, expected_outcome)
TEST_CONDITIONS = [
    # COOP-expected: high resource, high interaction
    (3.0, 0.8, 8,  0.05,  1, "COOP"),
    (3.0, 0.8, 8,  0.10,  2, "COOP"),
    (3.0, 0.8, 8,  0.20,  3, "COOP"),
    (3.0, 0.5, 8,  0.05,  4, "COOP"),
    (3.0, 0.5, 8,  0.10,  5, "COOP"),
    (3.0, 0.8, 5,  0.10,  6, "COOP"),
    (3.0, 0.8, 3,  0.10,  7, "COOP"),
    (3.0, 0.5, 5,  0.05,  8, "COOP"),
    (3.0, 0.8, 8,  0.05,  9, "COOP"),
    (3.0, 0.8, 5,  0.20, 10, "COOP"),
    (3.0, 0.8, 8,  0.10, 11, "COOP"),
    (3.0, 0.8, 8,  0.20, 12, "COOP"),
    (3.0, 0.5, 8,  0.20, 13, "COOP"),
    (3.0, 0.8, 3,  0.05, 14, "COOP"),
    (3.0, 0.5, 5,  0.10, 15, "COOP"),
    (3.0, 0.8, 3,  0.20, 16, "COOP"),
    (3.0, 0.5, 8,  0.10, 17, "COOP"),
    (3.0, 0.8, 8,  0.10, 18, "COOP"),
    (3.0, 0.8, 5,  0.05, 19, "COOP"),
    (3.0, 0.5, 3,  0.10, 20, "COOP"),
    # COMP-expected: high resource, LOW interaction frequency
    # (resource-rich but mutualism-poor → competitive hoarding)
    (3.0, 0.2, 8,  0.20, 21, "COMP"),
    (3.0, 0.2, 8,  0.20, 22, "COMP"),
    (3.0, 0.2, 5,  0.20, 23, "COMP"),
    (3.0, 0.2, 5,  0.20, 24, "COMP"),
    (3.0, 0.2, 8,  0.10, 25, "COMP"),
    (3.0, 0.2, 8,  0.10, 26, "COMP"),
    (3.0, 0.5, 8,  0.20, 27, "COMP"),
    (3.0, 0.5, 8,  0.20, 28, "COMP"),
    (3.0, 0.5, 5,  0.20, 29, "COMP"),
    (3.0, 0.5, 5,  0.20, 30, "COMP"),
    (3.0, 0.2, 5,  0.10, 31, "COMP"),
    (3.0, 0.2, 3,  0.20, 32, "COMP"),
    (3.0, 0.2, 3,  0.20, 33, "COMP"),
    (3.0, 0.5, 3,  0.20, 34, "COMP"),
    (3.0, 0.5, 3,  0.20, 35, "COMP"),
    (3.0, 0.2, 8,  0.20, 36, "COMP"),
    (3.0, 0.5, 5,  0.20, 37, "COMP"),
    (3.0, 0.2, 5,  0.20, 38, "COMP"),
    (3.0, 0.2, 8,  0.10, 39, "COMP"),
    (3.0, 0.5, 8,  0.20, 40, "COMP"),
]


# ── Core invasion function ────────────────────────────────────────────────────

def run_invasion_test(R, I_freq, K, epsilon, seed, expected):
    """
    Run a single invasion test.
    Returns dict with pre/post-invasion mean_i and recovery trajectory.
    """
    model = MELVModel(R=R, I_freq=I_freq, K=K, epsilon=epsilon, seed=seed)

    # Warm up to resolution
    for _ in range(WARMUP_STEPS):
        model.step()
        if len(list(model.agents)) == 0:
            return None

    agents      = list(model.agents)
    n           = len(agents)
    pre_mean_i  = float(np.mean([a.i_factor for a in agents]))
    pre_outcome = "COOP" if pre_mean_i < 0.9 else ("COMP" if pre_mean_i > 1.1 else "THRESH")

    # Only test runs that actually resolved as expected
    if pre_outcome != expected:
        return None

    # ── Invasion: replace 25% with opposite-strategy agents ──────────────────
    n_invaders = max(1, int(n * INVASION_FRACTION))
    targets    = model.random.sample(agents, min(n_invaders, n))

    if pre_outcome == "COOP":
        # Inject competitive invaders (i > 1)
        invader_i = 1.8
    else:
        # Inject cooperative invaders (i < 1)
        invader_i = 0.2

    for agent in targets:
        agent.i_factor = invader_i
        agent.energy   = 1.0   # ensure survival

    post_invasion_mean_i = float(np.mean([a.i_factor for a in list(model.agents)]))

    # ── Recovery: run 400 more steps ─────────────────────────────────────────
    recovery_traj = []
    for _ in range(RECOVERY_STEPS):
        model.step()
        remaining = list(model.agents)
        if not remaining:
            break
        recovery_traj.append(float(np.mean([a.i_factor for a in remaining])))

    if not recovery_traj:
        return None

    final_mean_i  = recovery_traj[-1]
    final_outcome = "COOP" if final_mean_i < 0.9 else ("COMP" if final_mean_i > 1.1 else "THRESH")
    recovered     = (final_outcome == pre_outcome)

    return {
        "R": R, "I_freq": I_freq, "K": K, "epsilon": epsilon, "seed": seed,
        "expected":             expected,
        "pre_mean_i":           round(pre_mean_i, 4),
        "pre_outcome":          pre_outcome,
        "post_invasion_mean_i": round(post_invasion_mean_i, 4),
        "final_mean_i":         round(final_mean_i, 4),
        "final_outcome":        final_outcome,
        "recovered":            recovered,
        "recovery_trajectory":  recovery_traj,
    }


# ── Main test loop ────────────────────────────────────────────────────────────

def run_all_tests():
    results          = []
    trajectories     = {"COOP": [], "COMP": []}
    skipped          = 0

    print(f"Running {N_TESTS} invasion tests "
          f"(warmup={WARMUP_STEPS} + invasion + recovery={RECOVERY_STEPS} steps)...\n")
    print(f"{'#':>3}  {'Cond':<22}  {'Pre':>6}  {'Post-inv':>8}  "
          f"{'Final':>6}  {'Recovered':>10}")
    print("-" * 65)

    for i, (R, I_freq, K, eps, seed, expected) in enumerate(TEST_CONDITIONS, 1):
        result = run_invasion_test(R, I_freq, K, eps, seed, expected)

        if result is None:
            skipped += 1
            print(f"{i:>3}  R={R} I={I_freq} K={K} e={eps:<5}  "
                  f"{'SKIPPED (did not resolve)':>40}")
            continue

        results.append(result)
        traj = result["recovery_trajectory"]
        trajectories[expected].append(traj)

        rec_str = "YES ✓" if result["recovered"] else "NO  ✗"
        print(f"{i:>3}  R={R} I={I_freq} K={K} e={eps:<5}  "
              f"{result['pre_mean_i']:>6.3f}  "
              f"{result['post_invasion_mean_i']:>8.3f}  "
              f"{result['final_mean_i']:>6.3f}  "
              f"{rec_str:>10}")

    return results, trajectories, skipped


# ── Statistics ────────────────────────────────────────────────────────────────

def compute_recovery_stats(results):
    if not results:
        return {}
    total     = len(results)
    recovered = sum(1 for r in results if r["recovered"])
    coop_res  = [r for r in results if r["expected"] == "COOP"]
    comp_res  = [r for r in results if r["expected"] == "COMP"]

    coop_rate = sum(1 for r in coop_res if r["recovered"]) / len(coop_res) if coop_res else float("nan")
    comp_rate = sum(1 for r in comp_res if r["recovered"]) / len(comp_res) if comp_res else float("nan")

    # Mean i-factor delta: how far invasion pushed population
    invasion_delta = np.mean([
        abs(r["post_invasion_mean_i"] - r["pre_mean_i"]) for r in results
    ])

    return {
        "total":          total,
        "recovered":      recovered,
        "recovery_rate":  recovered / total,
        "coop_rate":      coop_rate,
        "comp_rate":      comp_rate,
        "invasion_delta": invasion_delta,
    }


# ── Figure 5: Recovery bar chart ─────────────────────────────────────────────

def figure_05_perturbation(results, stats, out_dir):
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    # Left: recovery rates by basin
    ax = axes[0]
    categories = ["COOP basin\n(invaded by\ncompetitors)",
                  "COMP basin\n(invaded by\ncooperators)",
                  "Overall"]
    rates   = [stats["coop_rate"] * 100,
               stats["comp_rate"] * 100,
               stats["recovery_rate"] * 100]
    colors  = [GREEN, RED, TEAL]
    bars    = ax.bar(categories, rates, color=colors, alpha=0.8, width=0.5)
    ax.axhline(85, color="black", linestyle="--", linewidth=1.5,
               label="85% ESS target")
    ax.set_ylim(0, 110)
    ax.set_ylabel("Recovery rate (%)")
    ax.set_title("Figure 5a — Basin recovery after\n25% mutant invasion")
    ax.legend(fontsize=9)
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                f"{rate:.0f}%", ha="center", va="bottom", fontsize=11, fontweight="bold")

    # Right: pre vs final mean_i scatter
    ax2 = axes[1]
    for r in results:
        color = GREEN if r["expected"] == "COOP" else RED
        marker = "o" if r["recovered"] else "x"
        ax2.scatter(r["pre_mean_i"], r["final_mean_i"],
                    color=color, marker=marker, alpha=0.7, s=60,
                    zorder=3)

    # Identity line (perfect recovery)
    lims = [0, 3.0]
    ax2.plot(lims, lims, "k--", linewidth=1, alpha=0.5, label="Perfect recovery")
    ax2.axhline(0.9, color=GREEN, linestyle=":", linewidth=1, alpha=0.6)
    ax2.axhline(1.1, color=RED,   linestyle=":", linewidth=1, alpha=0.6)
    ax2.axvline(0.9, color=GREEN, linestyle=":", linewidth=1, alpha=0.6)
    ax2.axvline(1.1, color=RED,   linestyle=":", linewidth=1, alpha=0.6)

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0],[0], marker="o", color="w", markerfacecolor=GREEN,
               markersize=9, label="COOP basin — recovered"),
        Line2D([0],[0], marker="x", color=GREEN, markersize=9,
               label="COOP basin — not recovered"),
        Line2D([0],[0], marker="o", color="w", markerfacecolor=RED,
               markersize=9, label="COMP basin — recovered"),
        Line2D([0],[0], marker="x", color=RED, markersize=9,
               label="COMP basin — not recovered"),
    ]
    ax2.legend(handles=legend_elements, fontsize=8, loc="upper left")
    ax2.set_xlabel("Pre-invasion mean i-factor")
    ax2.set_ylabel("Post-recovery mean i-factor (step +400)")
    ax2.set_title("Figure 5b — Pre vs post-recovery mean i\n(dots=recovered, crosses=not)")
    ax2.set_xlim(-0.1, 3.1)
    ax2.set_ylim(-0.1, 3.1)

    fig.tight_layout()
    path = os.path.join(out_dir, "figure_05_perturbation.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


# ── Figure 6: Invasion recovery trajectories ─────────────────────────────────

def figure_06_invasion_trajectories(trajectories, out_dir):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

    for ax, (basin, color, title) in zip(
        axes,
        [("COOP", GREEN, "COOP basin — invaded by competitors (i=1.8)"),
         ("COMP", RED,   "COMP basin — invaded by cooperators (i=0.2)")]
    ):
        trajs = trajectories[basin]
        if not trajs:
            ax.text(0.5, 0.5, "No data", transform=ax.transAxes, ha="center")
            continue

        max_len = max(len(t) for t in trajs)
        x       = np.arange(max_len)

        for traj in trajs:
            padded = traj + [traj[-1]] * (max_len - len(traj))
            ax.plot(x, padded, color=color, alpha=0.25, linewidth=1)

        # Mean trajectory
        padded_all = np.array([
            t + [t[-1]] * (max_len - len(t)) for t in trajs
        ])
        mean_traj = np.mean(padded_all, axis=0)
        ax.plot(x, mean_traj, color=color, linewidth=2.5,
                label=f"Mean (n={len(trajs)})")

        # Reference lines
        if basin == "COOP":
            ax.axhline(0.9, color="black", linestyle="--", linewidth=1.2,
                       alpha=0.7, label="COOP threshold (i=0.9)")
        else:
            ax.axhline(1.1, color="black", linestyle="--", linewidth=1.2,
                       alpha=0.7, label="COMP threshold (i=1.1)")

        ax.set_xlabel("Steps after invasion")
        ax.set_ylabel("Population mean i-factor")
        ax.set_title(f"Figure 6 — {title}")
        ax.legend(fontsize=9)

    fig.tight_layout()
    path = os.path.join(out_dir, "figure_06_invasion_trajectories.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


# ── CSV output ────────────────────────────────────────────────────────────────

def save_results_csv(results, path="perturbation_results.csv"):
    if not results:
        return
    cols = ["R","I_freq","K","epsilon","seed","expected",
            "pre_mean_i","pre_outcome","post_invasion_mean_i",
            "final_mean_i","final_outcome","recovered"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in results:
            w.writerow({k: r[k] for k in cols})
    print(f"  Saved {path}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    results, trajectories, skipped = run_all_tests()

    print(f"\n{'='*65}")
    print("INVASION TEST — SUMMARY")
    print(f"{'='*65}")

    stats = compute_recovery_stats(results)
    if stats:
        ess_pass = stats["recovery_rate"] >= 0.85
        print(f"\nTests run:       {stats['total']}  (skipped: {skipped})")
        print(f"Recovered:       {stats['recovered']} / {stats['total']}")
        print(f"Overall rate:    {stats['recovery_rate']:.1%}")
        print(f"COOP basin rate: {stats['coop_rate']:.1%}")
        print(f"COMP basin rate: {stats['comp_rate']:.1%}")
        print(f"Mean invasion delta (|Δi|): {stats['invasion_delta']:.3f}")
        print(f"\nESS criterion (>85%): {'PASS ✓' if ess_pass else 'FAIL ✗'}")
        print(f"{'='*65}\n")

    print("Generating figures...")
    figure_05_perturbation(results, stats, OUT_DIR)
    figure_06_invasion_trajectories(trajectories, OUT_DIR)
    save_results_csv(results)
    print("\nDone.")
