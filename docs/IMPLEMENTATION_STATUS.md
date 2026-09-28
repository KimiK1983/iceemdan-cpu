# Local publication preparation status

Target repository: `KimiK1983/iceemdan-cpu`. This checkout is local. No remote repository, push, tag, release, or full 500-run result has been created.

| Area | Status | Evidence or next step |
|---|---|---|
| CPU source, license, metadata | Prepared | Reviewed 2.0.0 candidate copied byte-for-byte; SHA-256 `2de7564f9f01560ff1d3b1d87af12e88e34b3647152616dce5d2e90c926b695f`. |
| English and Spanish README, synthetic illustration | Prepared | Original 256-sample signal and generated SVG; no biomedical waveform or paper crop committed. |
| Standalone numerical regressions | Checked locally | Nine tests, including synthetic frozen-reference fixture, CUDB decoder, and sweep resume, pass locally. |
| Public-data scripts | Smoke checked locally | Existing Keele/CUDB archives verified; one-trial analyses succeeded. Full 100-trial analyses not run here. |
| 500-run sweep and serial E2E benchmark | Prepared, not run in full | Defaults print plans. Small 1-trial smoke runs and parallel ordering/resume checks succeeded. |
| Package build | Checked locally | `uv build` produced an sdist and a universal wheel; wheel module import and source hash matched. |
| CI | Workflow written, not observed | Windows/Ubuntu Python 3.10–3.13 and macOS 3.13; no badge or green claim. |
| Remote publication | Pending review | No GitHub operation in this phase. |
