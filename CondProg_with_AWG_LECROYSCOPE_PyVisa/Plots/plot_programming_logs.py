""" 
    plot_programming_logs.py

    This script reads a CSV log file from a memristor programming session and generates plots
    for conductance, error, and pulse parameters over iterations or attempts.

    Usage:
        python plot_programming_logs.py <path_to_csv> [--outdir <output_directory>] [--show]

    The script will save the generated plots in the specified output directory or in the same
    directory as the CSV file if no output directory is specified.
    """ 
import argparse
import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt

def load_rows(csv_path):
    rows = []
    with open(csv_path, newline="") as f:
        r = csv.DictReader(f)
        for d in r:
            # convert selected fields to float when possible
            for k in ["attempt","G_prev_uS","G_uS","G_target_uS","err_uS","rel_err",
                      "alpha","beta","scaling_factor","K","pw_scale","np_scale",
                      "stuck_counter","PW_s","NP","Amplitude_V"]:
                if k in d and d[k] != "":
                    try:
                        d[k] = float(d[k])
                    except Exception:
                        pass
            rows.append(d)
    return rows

def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def plot_conductance(reads, outdir, stem, show):
    its = list(range(len(reads)))
    G  = [r["G_uS"] for r in reads]
    Gt = [reads[0]["G_target_uS"] for _ in reads]

    plt.figure()
    plt.plot(its, G, label="Measured G (µS)")
    plt.plot(its, Gt, linestyle="--", label="Target (µS)")
    plt.xlabel("Iteration (read index)")
    plt.ylabel("Conductance (µS)")
    plt.title(f"Conductance vs Iteration — {stem}")
    plt.legend()
    out = os.path.join(outdir, f"{stem}_G_vs_iter.png")
    plt.tight_layout()
    plt.savefig(out, dpi=140, bbox_inches="tight")
    if show: plt.show()
    plt.close()
    return out

def plot_error(reads, outdir, stem, show):
    its = list(range(len(reads)))
    G  = [r["G_uS"] for r in reads]
    Gt = [reads[0]["G_target_uS"] for _ in reads]
    err = [abs(gt - g) for gt, g in zip(Gt, G)]

    plt.figure()
    plt.plot(its, err, label="|Error| (µS)")
    plt.xlabel("Iteration (read index)")
    plt.ylabel("|Error| (µS)")
    plt.title(f"Absolute Error vs Iteration — {stem}")
    plt.legend()
    out = os.path.join(outdir, f"{stem}_ERR_vs_iter.png")
    plt.tight_layout()
    plt.savefig(out, dpi=140, bbox_inches="tight")
    if show: plt.show()
    plt.close()
    return out

def plot_pulse_params(rows, outdir, stem, show):
    # Use programming rows (mode inc/dec) to see how PW and NP changed over attempts
    prog = [r for r in rows if r["mode"] in ("inc","dec")]
    if not prog:
        return []

    # Sort by attempt just in case
    prog = sorted(prog, key=lambda r: float(r["attempt"]))

    attempts = [r["attempt"] for r in prog]
    pw_used  = [r.get("PW_s", 0.0) for r in prog]
    np_used  = [r.get("NP", 0.0) for r in prog]

    # Plot PW vs attempt
    plt.figure()
    plt.plot(attempts, pw_used, label="PW (s)")
    plt.xlabel("Attempt")
    plt.ylabel("PW (s)")
    plt.title(f"Pulse Width vs Attempt — {stem}")
    plt.legend()
    out1 = os.path.join(outdir, f"{stem}_PW_vs_attempt.png")
    plt.tight_layout()
    plt.savefig(out1, dpi=140, bbox_inches="tight")
    if show: plt.show()
    plt.close()

    # Plot NP vs attempt
    plt.figure()
    plt.plot(attempts, np_used, label="NP (# pulses)")
    plt.xlabel("Attempt")
    plt.ylabel("NP (#)")
    plt.title(f"Pulse Count vs Attempt — {stem}")
    plt.legend()
    out2 = os.path.join(outdir, f"{stem}_NP_vs_attempt.png")
    plt.tight_layout()
    plt.savefig(out2, dpi=140, bbox_inches="tight")
    if show: plt.show()
    plt.close()

    return [out1, out2]

def main():
    ap = argparse.ArgumentParser(description="Plot memristor programming logs.")
    ap.add_argument("csv", help="Path to the log CSV produced by the program.")
    ap.add_argument("--outdir", help="Directory to save plots (default: same folder as CSV).", default=None)
    ap.add_argument("--show", help="Also show plots interactively.", action="store_true")
    args = ap.parse_args()

    csv_path = Path(args.csv).resolve()
    rows = load_rows(csv_path)
    if not rows:
        print("No rows found in CSV.")
        return

    # Determine stem and outdir
    stem = csv_path.stem
    outdir = args.outdir if args.outdir is not None else str(csv_path.parent)
    ensure_dir(outdir)

    reads = [r for r in rows if r.get("mode") == "read" and isinstance(r.get("G_uS"), (int,float))]
    if not reads:
        print("No 'read' rows found. Plots will be limited to pulse parameters.")
    else:
        gplot = plot_conductance(reads, outdir, stem, args.show)
        eplot = plot_error(reads, outdir, stem, args.show)
        print("Saved:", gplot)
        print("Saved:", eplot)

    pplots = plot_pulse_params(rows, outdir, stem, args.show)
    for p in pplots:
        print("Saved:", p)

if __name__ == "__main__":
    main()
