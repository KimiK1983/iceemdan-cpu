# Paper comparison and source limits

The paper is Colominas et al. (2014), DOI [10.1016/j.bspc.2014.06.009](https://doi.org/10.1016/j.bspc.2014.06.009). The [authors' MATLAB implementation](https://zenodo.org/records/5580793) provides algorithm code but not the paper's individual random draws or all plotted source vectors. This repository does not claim sample-for-sample equivalence to the paper. The final CPU module completed the [500-run synthetic ICEEMDAN arm](../results/synthetic_20260928/analysis.json), with 100 successes at each of the five ensemble sizes and zero failures. Earlier local exploration used a previous Python source and is not the release evidence.

| Figure | Status | Evidence and limit |
|---:|---|---|
| 1 | Approximation | The recurrence and flow are described in [METHOD.md](METHOD.md); the published diagram is not visually reproduced or copied. |
| 2 | Approximation | `scripts/compare_python_methods.py` compares five Python methods, including a complementary-EEMD proxy. PyEMD is not the authors' MATLAB toolbox; the exact random draws are unavailable. |
| 3 | Reproduced | The 500-run sweep reproduces the ICEEMDAN arm across the five published ensemble sizes. The full multi-method figure is only partially covered; the other MATLAB runs are unavailable. |
| 4 | Reproduced | First-component and first-residue RRSE were calculated for the ICEEMDAN arm only. Mean first-component RRSE fell from 0.078761 at I=50 to 0.075087 at I=800; the full multi-method figure is not reproduced. |
| 5 | Reproduced | Reconstruction RRSE was at most 8.23e-17 across the 500 ICEEMDAN runs. The full multi-method figure is not reproduced, and completeness does not validate component matching. |
| 6 | Not reproducible | The second synthetic signal's printed phase `-acos(13)` is not real-valued. The intended generator is needed. |
| 7 | Not reproducible | The stated sample range ends at 1000 while the plotted range reaches 2000; the intended vector is needed. |
| 8 | Candidate | Keele `f1nw0000/laryngograph.wav`, 17.275–17.455 s, matched in earlier local image analysis. The archive polarity is inverted for comparison. |
| 9 | Candidate | The Fig. 8 candidate was decomposed with 100 trials and seed 0: 9 components and residue, reconstruction error 1.82e-12 ADC. The paper's seed and arrays are unavailable. |
| 10 | Candidate | The same Keele record, 25.925–26.025 s, was suggested by earlier local image analysis. |
| 11 | Candidate | The Fig. 10 candidate was decomposed with 100 trials and seed 0: 8 components and residue, reconstruction error 1.82e-12 ADC. Sample-for-sample agreement is unverified. |
| 12 | Candidate | CUDB `cu01`, 206–222 s, has a VFON annotation at 214.184 s. The paper does not name its ECG record. |
| 13 | Candidate | The Fig. 12 candidate was decomposed with 100 trials and seed 0: 10 components and residue, reconstruction error 2.27e-13 ADC. Its source identity and component equality are unverified. |
| 14 | Not reproducible | No intracranial EEG record identifier or 75 s sample vector is supplied. |
| 15 | Not reproducible | The same unidentified patient vector is required; no substitute patient waveform is presented. |

The first synthetic signal is defined explicitly in `scripts/synthetic_signal.py`. `rrse_fast` compares its known high-frequency component with the first extracted component; `rrse_slow_residue` compares the first residue with the known slow component. `rrse_reconstruction` checks summation. Reconstruction checks completeness, not component correctness or paper matching. Audit the [500 individual rows](../results/synthetic_20260928/rows.jsonl), [run manifest](../results/synthetic_20260928/manifest.json), [summary](../results/synthetic_20260928/summary.json), [validated aggregates](../results/synthetic_20260928/analysis.json), and [separate serial timing](../results/benchmark_cpu_20260928.json).

Optional source archives are [KEELE.zip, Zenodo record 3921794](https://zenodo.org/records/3921794) and [CUDB 1.0.0, PhysioNet](https://physionet.org/content/cudb/1.0.0/). `scripts/fetch_public_data.py` verifies the published Keele MD5 and CUDB record SHA-256 checksums in its versioned archive. The small [Keele metrics](../results/public_data_20260928/keele/metrics.json) and [CUDB metrics](../results/public_data_20260928/cudb/metrics.json) contain source URL and archive SHA-256, record, window, sample rate, parameters, module SHA-256, stop reason, component count, and reconstruction error. No waveform or component array is included. Dataset licenses and attribution apply independently of this repository's Apache-2.0 code license. Downloaded archives and generated biomedical arrays remain outside version control. These are candidate visual correspondences, not confirmed paper sources or clinical validation.
