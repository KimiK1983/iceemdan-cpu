"""Run the ordered 5×100 ICEEMDAN synthetic arm; no plotting or private data."""

import argparse
import hashlib
import json
import multiprocessing as mp
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from itertools import repeat
from pathlib import Path

import numpy as np
import scipy

import ICEEMDAN
from ICEEMDAN import ICEEMDAN as Model
from scripts.synthetic_signal import signal_parts

ROOT = Path(__file__).resolve().parents[1]
SIZES = (50, 100, 200, 400, 800)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_one(size, seed, fast, slow, signal):
    started = time.perf_counter()
    row = {"I": size, "seed": seed, "status": "ok"}
    try:
        model = Model(trials=size, epsilon=0.2, seed=seed, parallel=False)
        parts = model(signal)
        first = parts[0]
        r1 = signal - first
        row.update(
            modes=len(parts) - 1,
            stop_reason=model.diagnostics_["stop_reason"],
            left_energy=float(np.mean(first[10:490] ** 2)),
            right_energy=float(np.mean(first[760:990] ** 2)),
            rrse_fast=float(np.linalg.norm(first - fast) / np.linalg.norm(fast)),
            rrse_slow_residue=float(np.linalg.norm(r1 - slow) / np.linalg.norm(slow)),
            rrse_reconstruction=float(
                np.linalg.norm(parts.sum(axis=0) - signal) / np.linalg.norm(signal)
            ),
        )
    except Exception as exc:  # noqa: BLE001 - record per-run failures and continue the sweep
        row.update(status="error", error_type=type(exc).__name__, error=str(exc))
    row["elapsed_s"] = time.perf_counter() - started
    return row


def ordered_results(pairs, fast, slow, signal, workers):
    if workers == 1:
        for size, seed in pairs:
            yield run_one(size, seed, fast, slow, signal)
    else:
        with ProcessPoolExecutor(
            max_workers=workers, mp_context=mp.get_context("spawn")
        ) as pool:
            yield from pool.map(
                run_one,
                (size for size, _ in pairs),
                (seed for _, seed in pairs),
                repeat(fast),
                repeat(slow),
                repeat(signal),
                chunksize=1,
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run", action="store_true", help="Execute; otherwise print the plan"
    )
    parser.add_argument(
        "--resume", action="store_true", help="Resume a matching JSONL prefix"
    )
    parser.add_argument("--sizes", nargs="+", type=int, default=SIZES)
    parser.add_argument("--seeds", nargs="+", type=int, default=list(range(100)))
    parser.add_argument(
        "--workers", type=int, default=1, help="Independent runs in parallel, 1–12"
    )
    parser.add_argument("--out", type=Path, default=ROOT / "outputs" / "sweep")
    args = parser.parse_args()
    if (
        not args.sizes
        or not args.seeds
        or any(v < 1 for v in args.sizes)
        or any(v < 0 for v in args.seeds)
    ):
        parser.error("sizes must be positive and seeds nonnegative")
    pairs = [(size, seed) for size in args.sizes for seed in args.seeds]
    if len(set(pairs)) != len(pairs):
        parser.error("sizes and seeds must not contain duplicates")
    if not 1 <= args.workers <= 12:
        parser.error("workers must be between 1 and 12")
    if not args.run:
        print(
            f"DRY RUN: {len(pairs)} decompositions, {args.workers} workers, ordered by I then seed; output {args.out}"
        )
        return

    fast, slow, signal = signal_parts()
    config = {
        "sizes": list(args.sizes),
        "seeds": list(args.seeds),
        "epsilon": 0.2,
        "parallel_within_run": False,
        "workers_between_runs": args.workers,
        "max_imf": -1,
        "signal_formula": "fast[n=501..750]=sin(2*pi*0.255*(n-501)); slow=sin(2*pi*0.065*(n-1)); n=1..1000",
        "signal_sha256": hashlib.sha256(signal.tobytes()).hexdigest(),
        "module_sha256": digest(ICEEMDAN.__file__),
        "script_sha256": digest(__file__),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
    }
    args.out.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out / "manifest.json"
    rows_path = args.out / "rows.jsonl"
    if manifest_path.exists() or rows_path.exists():
        if not args.resume or not manifest_path.exists() or not rows_path.exists():
            parser.error("output exists; use --resume with matching manifest and rows")
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        if previous["config"] != config:
            parser.error("resume config or environment differs from existing manifest")
        existing = [
            json.loads(line)
            for line in rows_path.read_text(encoding="utf-8").splitlines()
        ]
        if [(row["I"], row["seed"]) for row in existing] != pairs[: len(existing)]:
            parser.error("existing rows are not a prefix in I/seed order")
    else:
        manifest_path.write_text(
            json.dumps(
                {
                    "started_utc": datetime.now(timezone.utc).isoformat(),
                    "config": config,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        existing = []

    with rows_path.open("a", encoding="utf-8") as log:
        pending = pairs[len(existing) :]
        for (size, seed), row in zip(
            pending, ordered_results(pending, fast, slow, signal, args.workers)
        ):
            log.write(json.dumps(row, sort_keys=True) + "\n")
            log.flush()
            existing.append(row)
            print(
                f"{len(existing)}/{len(pairs)} I={size} seed={seed} {row['status']}",
                flush=True,
            )
    summary = {
        "attempts": len(existing),
        "successes": sum(row["status"] == "ok" for row in existing),
        "failures": sum(row["status"] == "error" for row in existing),
        "by_I": {
            str(size): {
                "attempts": sum(row["I"] == size for row in existing),
                "mean_rrse_fast": float(
                    np.mean(
                        [
                            row["rrse_fast"]
                            for row in existing
                            if row["I"] == size and row["status"] == "ok"
                        ]
                    )
                )
                if any(row["I"] == size and row["status"] == "ok" for row in existing)
                else None,
            }
            for size in args.sizes
        },
    }
    (args.out / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
