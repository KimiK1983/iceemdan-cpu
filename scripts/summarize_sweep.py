"""Validate the complete synthetic sweep and write auditable aggregate metrics."""

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

import ICEEMDAN

ROOT = Path(__file__).resolve().parents[1]
SIZES = (50, 100, 200, 400, 800)
METRICS = (
    "rrse_fast",
    "rrse_slow_residue",
    "left_energy",
    "right_energy",
    "rrse_reconstruction",
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--directory", type=Path, default=ROOT / "results" / "synthetic_20260928"
    )
    args = parser.parse_args()
    manifest_path = args.directory / "manifest.json"
    rows_path = args.directory / "rows.jsonl"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = [
        json.loads(line) for line in rows_path.read_text(encoding="utf-8").splitlines()
    ]
    expected = [(size, seed) for size in SIZES for seed in range(100)]
    if [(row["I"], row["seed"]) for row in rows] != expected:
        raise ValueError("expected exactly 500 ordered, unique size/seed pairs")
    if any(row["status"] != "ok" for row in rows):
        raise ValueError("one or more runs failed")
    if any(not math.isfinite(row[key]) for row in rows for key in METRICS):
        raise ValueError("non-finite metric")
    config = manifest["config"]
    if config["sizes"] != list(SIZES) or config["seeds"] != list(range(100)):
        raise ValueError("manifest does not match the expected experiment")
    if config["module_sha256"] != sha256(Path(ICEEMDAN.__file__)):
        raise ValueError("module SHA-256 differs from the run manifest")
    groups = {}
    for size in SIZES:
        group = [row for row in rows if row["I"] == size]
        groups[str(size)] = {
            "runs": len(group),
            "mean_rrse_fast": statistics.mean(row["rrse_fast"] for row in group),
            "mean_rrse_slow_residue": statistics.mean(
                row["rrse_slow_residue"] for row in group
            ),
            "mean_left_energy": statistics.mean(row["left_energy"] for row in group),
            "mean_right_energy": statistics.mean(row["right_energy"] for row in group),
            "max_rrse_reconstruction": max(row["rrse_reconstruction"] for row in group),
        }
    summary = json.loads((args.directory / "summary.json").read_text(encoding="utf-8"))
    if (
        summary["attempts"] != 500
        or summary["successes"] != 500
        or summary["failures"] != 0
    ):
        raise ValueError("run summary counts disagree")
    for size in SIZES:
        if not math.isclose(
            summary["by_I"][str(size)]["mean_rrse_fast"],
            groups[str(size)]["mean_rrse_fast"],
            rel_tol=0,
            abs_tol=1e-15,
        ):
            raise ValueError(f"run summary mean disagrees for I={size}")
    analysis = {
        "rows_sha256": sha256(rows_path),
        "manifest_sha256": sha256(manifest_path),
        "module_sha256": config["module_sha256"],
        "runs": 500,
        "failures": 0,
        "by_I": groups,
    }
    (args.directory / "analysis.json").write_text(
        json.dumps(analysis, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(analysis, indent=2))


if __name__ == "__main__":
    main()
