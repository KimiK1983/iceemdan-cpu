# ICEEMDAN CPU

An importable, CPU-only implementation of **Improved Complete Ensemble Empirical Mode Decomposition with Adaptive Noise** (ICEEMDAN). It uses NumPy and SciPy; PyEMD is not a runtime dependency. This repository contains the wrapper and its original synthetic checks. It does not contain biomedical recordings or paper images.

![Original synthetic ICEEMDAN example](assets/synthetic_decomposition.svg)

The plotted signal is generated in `scripts/make_synthetic_figure.py`, not copied from the paper or a clinical dataset. [Leer en español](README.es.md).

## Install and use

Requires Python 3.10 or newer:

```bash
python -m pip install .
```

```python
import numpy as np
from ICEEMDAN import ICEEMDAN

t = np.arange(256, dtype=float)
x = np.sin(0.2 * t) + 0.3 * np.sin(0.7 * t)
model = ICEEMDAN(trials=50, epsilon=0.2, seed=42)
parts = model(x, T=t)
imfs, residue = model.get_imfs_and_residue()
assert np.allclose(parts.sum(axis=0), x)
print(parts.shape, model.diagnostics_["stop_reason"])
```

Each row of `parts` except the last is an extracted component; **the last row is always the residue**. Extraction does not certify that a component is a structural mode or mathematically exact IMF. `max_imf` limits extracted components. `parallel=True` uses process spawning; call it from an importable script protected by `if __name__ == "__main__":`.

See [method and numerical contracts](docs/METHOD.md) for the algorithm, stopping behavior, parameters, and limits.

## Reproducibility

The [paper reproducibility map](docs/PAPER_REPRODUCIBILITY.md) distinguishes exact code contracts, Python approximations, candidate public-data matches, and unidentified sources for figures 1–15. It does not claim numerical equality with the authors' MATLAB implementation.

Small standalone tests use an original synthetic fixture captured from a frozen reference. Run `python -m pytest -q`. The 500-run synthetic sweep and serial timing benchmark are deliberately opt-in:

```bash
python -m scripts.run_synthetic_sweep                       # plan only
python -m scripts.run_synthetic_sweep --workers 4 --run       # 500 runs
python -m scripts.run_synthetic_sweep --workers 4 --run --resume
python -m scripts.benchmark_cpu                               # plan only
python -m scripts.benchmark_cpu --run                          # full timings
```

The sweep uses the signal and five ensemble sizes from the paper comparison, with 100 numbered seeds at each size. Independent decompositions can run in separate processes with `--workers` (1–12); each decomposition itself stays serial, and JSONL rows remain in size/seed order. Manifests record versions, parameters, hashes, timing, failures, and environment details. A resumed run requires the same manifest configuration and script. [Current execution status](docs/IMPLEMENTATION_STATUS.md).

## Public recordings

Optional scripts fetch **versioned** source archives into ignored `data/` and write analysis only under ignored `outputs/`:

```bash
python -m scripts.fetch_public_data keele
python -m scripts.fetch_public_data cudb
python -m scripts.analyze_keele --save-local-arrays
python -m scripts.analyze_cudb --save-local-arrays
```

The [Keele Zenodo record](https://zenodo.org/records/3921794) states noncommercial use for the corpus. The [CUDB PhysioNet record](https://physionet.org/content/cudb/1.0.0/) provides its own attribution license and citation instructions. Review those terms before use. The ECG `cu01` window is a **candidate**, since the paper does not identify the record. The scripts do not establish clinical validity.

An optional Python method comparison uses `EMD-signal` (`PyEMD`) only when running `python -m scripts.compare_python_methods`; it is not required to import or run `ICEEMDAN`.

## License and attribution

The original wrapper is Apache-2.0. Some geometry code is adapted from PyEMD under Apache-2.0; see [third-party notices](THIRD_PARTY_NOTICES.md) and [license](LICENSE). Dataset rights are separate from the code license. No source archive, PDF crop, or recorded waveform is redistributed here.
