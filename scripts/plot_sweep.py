"""Plot synthetic sweep metrics from the committed 500 JSONL records."""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SIZES = (50, 100, 200, 400, 800)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rows",
        type=Path,
        default=ROOT / "results" / "synthetic_20260928" / "rows.jsonl",
    )
    parser.add_argument(
        "--out", type=Path, default=ROOT / "assets" / "synthetic_sweep.svg"
    )
    args = parser.parse_args()
    rows = [
        json.loads(line) for line in args.rows.read_text(encoding="utf-8").splitlines()
    ]
    expected = [(size, seed) for size in SIZES for seed in range(100)]
    if [(row["I"], row["seed"]) for row in rows] != expected:
        raise ValueError("expected 500 ordered rows (100 seeds per ensemble size)")
    if any(row["status"] != "ok" for row in rows):
        raise ValueError("all 500 rows must succeed before plotting")
    plt.rcParams["svg.hashsalt"] = "iceemdan-cpu-sweep"
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), layout="constrained")
    for axis, key, ylabel in (
        (axes[0], "rrse_fast", "First-component RRSE"),
        (axes[1], "left_energy", "Energy outside fast-signal interval"),
    ):
        series = [[row[key] for row in rows if row["I"] == size] for size in SIZES]
        plot = axis.boxplot(
            series, tick_labels=SIZES, patch_artist=True, showfliers=False
        )
        for box in plot["boxes"]:
            box.set_facecolor("#a8d8d4")
            box.set_edgecolor("#007c78")
        for median in plot["medians"]:
            median.set_color("#be5a2c")
            median.set_linewidth(2)
        axis.set(xlabel="Ensemble size (I)", ylabel=ylabel)
        axis.grid(axis="y", alpha=0.2)
    axes[1].set_yscale("log")
    fig.suptitle("ICEEMDAN CPU on a synthetic signal · 100 seeds per size")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, metadata={"Date": None})
    plt.close(fig)
    svg = (
        "\n".join(
            line.rstrip() for line in args.out.read_text(encoding="utf-8").splitlines()
        )
        + "\n"
    )
    with args.out.open("w", encoding="utf-8", newline="\n") as output:
        output.write(svg)
    print(args.out)


if __name__ == "__main__":
    main()
