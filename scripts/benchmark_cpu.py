"""Full serial ICEEMDAN timing on the synthetic signal; opt-in long run."""

import argparse
import hashlib
import json
import os
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy

import ICEEMDAN
from ICEEMDAN import ICEEMDAN as Model
from scripts.synthetic_signal import signal_parts

ROOT = Path(__file__).resolve().parents[1]
SIZES = (50, 100, 200, 400, 800)


def measured_run(size, signal):
    start = time.perf_counter()
    model = Model(trials=size, epsilon=0.2, seed=0, parallel=False)
    parts = model(signal)
    elapsed = time.perf_counter() - start
    return (
        elapsed,
        hashlib.sha256(parts.tobytes()).hexdigest(),
        model.diagnostics_["stop_reason"],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run", action="store_true", help="Execute; otherwise print the plan"
    )
    parser.add_argument("--sizes", nargs="+", type=int, default=SIZES)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--out", type=Path, default=ROOT / "outputs" / "benchmark.json")
    args = parser.parse_args()
    if any(size < 1 for size in args.sizes) or args.warmup < 0 or args.repeats < 1:
        parser.error("sizes and repeats must be positive; warmup must be nonnegative")
    if not args.run:
        print(
            f"DRY RUN: {args.warmup} warmup + {args.repeats} timed full serial runs for each I={args.sizes}"
        )
        return

    _, _, signal = signal_parts()
    rows = []
    for size in args.sizes:
        warmups = [measured_run(size, signal)[0] for _ in range(args.warmup)]
        measured = [measured_run(size, signal) for _ in range(args.repeats)]
        durations = [item[0] for item in measured]
        rows.append(
            {
                "I": size,
                "warmup_s": warmups,
                "samples_s": durations,
                "median_s": statistics.median(durations),
                "min_s": min(durations),
                "max_s": max(durations),
                "output_sha256": [item[1] for item in measured],
                "stop_reason": [item[2] for item in measured],
            }
        )
        print(
            f"I={size} median={rows[-1]['median_s']:.3f}s range={rows[-1]['min_s']:.3f}-{rows[-1]['max_s']:.3f}s",
            flush=True,
        )
    payload = {
        "utc": datetime.now(timezone.utc).isoformat(),
        "protocol": "one warmup and three timed full serial decompositions per I by default; model construction inside timer",
        "sizes": args.sizes,
        "warmup": args.warmup,
        "repeats": args.repeats,
        "epsilon": 0.2,
        "seed": 0,
        "signal_sha256": hashlib.sha256(signal.tobytes()).hexdigest(),
        "module_sha256": hashlib.sha256(
            Path(ICEEMDAN.__file__).read_bytes()
        ).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
        },
        "results": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
