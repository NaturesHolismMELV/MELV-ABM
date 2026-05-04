"""
batch_run_v2_1_2000.py
======================
MELV ABM V2.1 — full sweep at 2000 steps.

Biological rationale (Grok / Maynard Smith 1982; Melian et al. 2011):
  Evolutionary resolution requires generational depth. 800 steps truncates
  slow drift near the threshold, particularly under low R / low I_freq.
  2000 steps gives marginal populations time to resolve without artificially
  forcing outcomes.
"""

import itertools, math, csv, time
from melv_abm_v2_1 import MELVModel

R_values       = [0.3, 1.0, 3.0]
I_freq_values  = [0.2, 0.5, 0.8]
K_values       = [3,   5,   8  ]
epsilon_values = [0.05, 0.10, 0.20]
N_REPLICATES   = 5
N_STEPS        = 2000

conditions = list(itertools.product(R_values, I_freq_values, K_values, epsilon_values))

SUMMARY_FILE    = "validation_summary_v2_1_2000.csv"
TRAJECTORY_FILE = "validation_data_v2_1_2000.csv"

TRAJ_COLS = [
    "condition_id","replicate","step","n_agents","mean_i","sd_i","min_i","max_i",
    "cooperation_level","cooperative_count","mean_phi","mean_beta","mean_phi_beta",
    "i_predicted_master_eq","R","I_freq","K","epsilon",
]
SUMM_COLS = [
    "condition_id","replicate","R","I_freq","K","epsilon",
    "final_mean_i","final_sd_i","final_cooperation_level","final_n_agents",
    "final_mean_phi","final_mean_phi_beta","outcome","crossing_step",
    "late_mean_i","late_std_i","resolved",
]

def classify(mean_i):
    if mean_i < 0.9:  return "COOP"
    if mean_i > 1.1:  return "COMP"
    return "THRESH"

def crossing(history):
    return next((r["step"] for r in history if r["mean_i"] < 0.9), float("nan"))

def late_stats(history, last_n=200):
    """Mean and std of mean_i over the last_n sample points."""
    import numpy as np
    tail = [r["mean_i"] for r in history[-last_n:]]
    if not tail:
        return float("nan"), float("nan")
    return float(np.mean(tail)), float(np.std(tail))

def is_resolved(mean_i, std_i, threshold=0.08, stability=0.05):
    """
    A THRESH run is 'resolved' if it is stable (low rolling std)
    AND displaced from the boundary (|mean_i - 1.0| > threshold).
    Biologically: population has settled into one basin but hasn't
    crossed the 0.9/1.1 classification lines yet.
    """
    if math.isnan(std_i):
        return False
    return std_i < stability and abs(mean_i - 1.0) > threshold

t0    = time.time()
total = len(conditions) * N_REPLICATES

print(f"MELV ABM V2.1 — 2000-step sweep")
print(f"81 conditions × {N_REPLICATES} replicates × {N_STEPS} steps = {total} runs\n")

with open(TRAJECTORY_FILE,"w",newline="") as tf, \
     open(SUMMARY_FILE,   "w",newline="") as sf:
    tw = csv.DictWriter(tf, fieldnames=TRAJ_COLS); tw.writeheader()
    sw = csv.DictWriter(sf, fieldnames=SUMM_COLS); sw.writeheader()

    for ci, (R, I_freq, K, epsilon) in enumerate(conditions, 1):
        for rep in range(1, N_REPLICATES + 1):
            seed  = ci * 100 + rep
            model = MELVModel(R=R, I_freq=I_freq, K=K, epsilon=epsilon, seed=seed)

            for _ in range(N_STEPS):
                model.step()
                if len(list(model.agents)) == 0:
                    break

            for row in model.history:
                tw.writerow({"condition_id": ci, "replicate": rep, **row})

            if model.history:
                last           = model.history[-1]
                cs             = crossing(model.history)
                lm, ls         = late_stats(model.history)
                outcome        = classify(last["mean_i"])
                resolved_flag  = is_resolved(lm, ls) if outcome == "THRESH" else True

                sw.writerow({
                    "condition_id":            ci,
                    "replicate":               rep,
                    "R": R, "I_freq": I_freq, "K": K, "epsilon": epsilon,
                    "final_mean_i":            round(last["mean_i"], 4),
                    "final_sd_i":              round(last["sd_i"],   4),
                    "final_cooperation_level": round(last["cooperation_level"], 4),
                    "final_n_agents":          last["n_agents"],
                    "final_mean_phi":          round(last["mean_phi"],     4),
                    "final_mean_phi_beta":     round(last["mean_phi_beta"],4),
                    "outcome":                 outcome,
                    "crossing_step":           cs if not math.isnan(cs) else "",
                    "late_mean_i":             round(lm, 4),
                    "late_std_i":              round(ls, 4),
                    "resolved":                resolved_flag,
                })
            else:
                sw.writerow({
                    "condition_id": ci, "replicate": rep,
                    "R": R, "I_freq": I_freq, "K": K, "epsilon": epsilon,
                    "outcome": "EXTINCT", "final_n_agents": 0, "resolved": False,
                    **{k: "" for k in SUMM_COLS if k not in
                       ["condition_id","replicate","R","I_freq","K","epsilon",
                        "outcome","final_n_agents","resolved"]}
                })

        if ci % 9 == 0 or ci == 81:
            elapsed = time.time() - t0
            done    = ci * N_REPLICATES
            rate    = done / elapsed if elapsed > 0 else 1
            eta     = (total - done) / rate
            print(f"  {ci:>3}/81 ({100*ci/81:5.1f}%)  "
                  f"runs={done}/{total}  "
                  f"elapsed={elapsed:.0f}s  ETA={eta:.0f}s", flush=True)

elapsed = time.time() - t0
print(f"\nDone. {total} runs in {elapsed:.1f}s")
print(f"  Trajectory : {TRAJECTORY_FILE}")
print(f"  Summary    : {SUMMARY_FILE}")
