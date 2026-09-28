# Local validation evidence for version 2.0.0

Recorded on 2026-09-28. These are observations from a local source snapshot; they do not imply that a later CI run or release succeeded.

| Area | Local evidence and limit |
|---|---|
| CPU source | The reviewed module SHA-256 is `2de7564f9f01560ff1d3b1d87af12e88e34b3647152616dce5d2e90c926b695f`. |
| Tests | Nine regressions passed locally on Python 3.10, 3.12 and 3.13. Ruff checks passed. |
| Synthetic experiment | [Analysis](../results/synthetic_20260928/analysis.json) verified 500 ordered, unique runs: 100 per ensemble size and zero failures. The two SVGs use synthetic signals only. |
| CPU timing | The [benchmark](../results/benchmark_cpu_20260928.json) used one warmup and three timed full serial runs per size after the worker pool exited, on an Intel Core Ultra 9 275HX. |
| Public-data candidates | Verified versioned Keele and CUDB archives. Two Keele windows and the 16 s `cu01` window used 100 trials each. Only small [Keele](../results/public_data_20260928/keele/metrics.json) and [CUDB](../results/public_data_20260928/cudb/metrics.json) provenance/metrics JSON files are versioned; source identity remains unconfirmed. |
| Package | Local wheel and sdist builds succeeded. The wheel included the Apache-2.0 license and third-party notices, required only NumPy and SciPy, and its example ran from an isolated installation outside the checkout. |
| Dependency audit | `pip-audit` 2.10.1 reported zero known vulnerabilities on 2026-09-28 for an isolated resolution with NumPy 2.5.3 and SciPy 1.18.1. This is a dated result for those versions; later advisories or other resolutions can differ. |
| CI | The workflow covers Windows and Ubuntu on Python 3.10–3.13, plus macOS on 3.13, including an installed example outside checkout. No CI outcome is asserted here. |

The [figure-by-figure paper comparison](PAPER_REPRODUCIBILITY.md) describes what the results do and do not establish. No biomedical waveform, source archive, or paper image is included in the versioned tree.
