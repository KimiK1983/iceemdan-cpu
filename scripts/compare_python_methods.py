"""Optional Python-only comparison; this is not a MATLAB Fig. 2 reproduction."""

import argparse
import json
from pathlib import Path

import numpy as np

from ICEEMDAN import EMD, ICEEMDAN
from scripts.synthetic_signal import signal_parts

ROOT = Path(__file__).resolve().parents[1]


def complementary_eemd(signal, trials, seed):
    """Pair opposite noise draws and average aligned EMD rows."""
    rng = np.random.default_rng(seed)
    beta = 0.2 * np.std(signal, ddof=1)
    modes = []
    residues = []
    emd = EMD()
    for _ in range(trials // 2):
        noise = beta * rng.normal(size=len(signal))
        for sign in (1, -1):
            emd.emd(signal + sign * noise)
            imfs, residue = emd.get_imfs_and_residue()
            modes.append(imfs)
            residues.append(residue)
    aligned = np.zeros((max(map(len, modes)), len(signal)))
    for imfs in modes:
        aligned[: len(imfs)] += imfs / trials
    return np.vstack((aligned, np.mean(residues, axis=0)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=50)
    parser.add_argument(
        "--out", type=Path, default=ROOT / "outputs" / "python_methods.json"
    )
    args = parser.parse_args()
    if args.trials < 2 or args.trials % 2:
        parser.error("trials must be positive and even for complementary EEMD")
    try:
        from PyEMD import CEEMDAN, EEMD
    except ImportError as exc:
        parser.error(f"install optional EMD-signal for PyEMD comparison: {exc}")
    fast, _, signal = signal_parts()
    beta = 0.2 * np.std(signal, ddof=1)
    eemd = EEMD(
        trials=args.trials,
        noise_width=beta / np.ptp(signal),
        ext_EMD=EMD(),
        parallel=False,
    )
    eemd.noise_seed(0)
    results = {
        "EMD": EMD().emd(signal),
        "EEMD_PyEMD": eemd.eemd(signal),
        "complementary_EEMD_proxy": complementary_eemd(signal, args.trials, 0),
        "CEEMDAN_PyEMD": CEEMDAN(
            trials=args.trials,
            epsilon=0.2,
            beta_progress=False,
            ext_EMD=EMD(),
            parallel=False,
            seed=0,
        ).ceemdan(signal),
        "ICEEMDAN_CPU": ICEEMDAN(trials=args.trials, epsilon=0.2, seed=0)(signal),
    }
    summary = {
        name: {
            "rows": len(parts),
            "first_component_rrse": float(
                np.linalg.norm(parts[0] - fast) / np.linalg.norm(fast)
            ),
            "sum_rrse": float(
                np.linalg.norm(parts.sum(axis=0) - signal) / np.linalg.norm(signal)
            ),
        }
        for name, parts in results.items()
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
