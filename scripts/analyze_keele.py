"""Analyze two candidate Keele EGG windows; data and outputs stay local."""

import argparse
import hashlib
import io
import json
import wave
import zipfile
from pathlib import Path

import numpy as np

import ICEEMDAN as module
from ICEEMDAN import ICEEMDAN as Model
from scripts.fetch_public_data import SOURCES, verify

ROOT = Path(__file__).resolve().parents[1]
WINDOWS = (("fig8", 17.275, 0.180), ("fig10", 25.925, 0.100))
RECORD = "KEELE/f1nw0000/laryngograph.wav"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ROOT / "data" / "KEELE.zip")
    parser.add_argument("--out", type=Path, default=ROOT / "outputs" / "keele")
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--save-local-arrays", action="store_true")
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("trials must be positive")
    if not args.archive.is_file():
        parser.error(f"missing {args.archive}; run scripts.fetch_public_data keele")
    archive_sha256 = verify(args.archive, "keele")
    module_sha256 = hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
    args.out.mkdir(parents=True, exist_ok=True)
    results = []
    with (
        zipfile.ZipFile(args.archive) as archive,
        wave.open(io.BytesIO(archive.read(RECORD))) as wav,
    ):
        fs = wav.getframerate()
        if wav.getnchannels() != 1 or wav.getsampwidth() != 2:
            raise ValueError("expected mono 16-bit Keele EGG")
        for label, start_s, duration_s in WINDOWS:
            wav.setpos(round(start_s * fs))
            x = -np.frombuffer(
                wav.readframes(round(duration_s * fs)), dtype="<i2"
            ).astype(float)
            if len(x) != round(duration_s * fs):
                raise ValueError(f"incomplete window: {label}")
            t = np.arange(len(x)) / fs
            model = Model(trials=args.trials, epsilon=0.2, seed=0)
            parts = model(x, T=t)
            row = {
                "window": label,
                "source_record": RECORD,
                "source_identification": "candidate from earlier visual matching; unconfirmed",
                "archive_url": SOURCES["keele"]["url"],
                "archive_sha256": archive_sha256,
                "module_sha256": module_sha256,
                "start_s": start_s,
                "duration_s": duration_s,
                "sample_rate_hz": fs,
                "archive_polarity_multiplier": -1,
                "trials": args.trials,
                "epsilon": 0.2,
                "seed": 0,
                "components": len(parts) - 1,
                "stop_reason": model.diagnostics_["stop_reason"],
                "reconstruction_linf": float(np.max(np.abs(parts.sum(axis=0) - x))),
            }
            if args.save_local_arrays:
                np.savez_compressed(args.out / f"{label}.npz", x=x, t=t, parts=parts)
            results.append(row)
    (args.out / "metrics.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(results))


if __name__ == "__main__":
    main()
