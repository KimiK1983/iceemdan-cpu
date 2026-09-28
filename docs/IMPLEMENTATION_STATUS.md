# Local publication preparation status

Target repository: `KimiK1983/iceemdan-cpu`. This checkout is local. No remote repository, push, tag, or release has been created.

| Area | Status | Evidence or next step |
|---|---|---|
| CPU source, license, metadata | Prepared | Reviewed 2.0.0 candidate copied byte-for-byte; SHA-256 `2de7564f9f01560ff1d3b1d87af12e88e34b3647152616dce5d2e90c926b695f`. |
| English and Spanish README, synthetic illustrations | Prepared | Original 256-sample decomposition and 500-run distribution SVGs; no biomedical waveform or paper crop committed. |
| Standalone numerical regressions | Checked locally | Nine tests, including synthetic frozen-reference fixture, CUDB decoder, and sweep resume, pass locally. |
| Public-data analysis | Completed locally | Verified versioned Keele/CUDB archives. Two complete Keele windows and the complete 16 s `cu01` candidate used 100 trials each; only small provenance/metrics JSON is versioned. |
| 500-run sweep | Completed locally | 500 ordered unique pairs, 100 per size, zero failures; [analysis](../results/synthetic_20260928/analysis.json) checks source hashes, finiteness and summary means. |
| Serial E2E benchmark | Completed locally | One warmup and three timed runs per size after worker pool exit; [timings and environment](../results/benchmark_cpu_20260928.json). |
| Package build | Checked locally | `uv build` produced an sdist and a universal wheel; installed-wheel example ran outside checkout and source hash matched. |
| CI | Workflow written, not observed | Windows/Ubuntu Python 3.10–3.13 and macOS 3.13, including installed example outside checkout; no badge or green claim. |
| Remote publication | Pending review | No GitHub operation in this phase. |
