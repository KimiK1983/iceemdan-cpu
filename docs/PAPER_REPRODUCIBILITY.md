# Paper comparison and source limits

The paper is Colominas et al. (2014), DOI [10.1016/j.bspc.2014.06.009](https://doi.org/10.1016/j.bspc.2014.06.009). The [authors' MATLAB implementation](https://zenodo.org/records/5580793) provides algorithm code but not the paper's individual random draws or all plotted source vectors. This repository does not claim sample-for-sample equivalence to the paper. Historical local exploration used an earlier Python source and is not a validated result for this release; the current 500-run sweep remains unexecuted.

| Paper figures | Source and test | Reproducibility status here |
|---|---|---|
| 1 | ICEEMDAN recurrence | The method is described in [METHOD.md](METHOD.md); no paper figure is copied. |
| 2 | Five decomposition methods on the first synthetic signal | `scripts/compare_python_methods.py` offers an optional **Python proxy** for EMD, EEMD, CEEMDAN and ICEEMDAN. PyEMD is not the authors' MATLAB toolbox. Random draws and exact figure cannot be matched. |
| 3–5 | First synthetic signal, 100 repetitions for each `I=50,100,200,400,800` | `scripts/run_synthetic_sweep.py` is prepared for the 500-run ICEEMDAN arm only. This release has **no new full-run result**. Other methods are outside this sweep. |
| 6–7 | Second synthetic signal | The printed phase `-acos(13)` is not real-valued, and the stated sample range differs from the plotted range. The intended vector/script is needed. |
| 8–11 | Two Keele EGG windows | `scripts/analyze_keele.py` uses candidate windows in `f1nw0000/laryngograph.wav` at 17.275–17.455 s and 25.925–26.025 s, with inverted source polarity. Earlier local image matching suggested these windows, but published component arrays and random seeds are unavailable. No PDF crop or signal is included. |
| 12–13 | ECG before and during ventricular fibrillation | `scripts/analyze_cudb.py` tests `cu01`, 206–222 s; its VFON annotation is at 214.184 s. The paper does not name the record, so this is a candidate and cannot be confirmed as the source. |
| 14–15 | Intracranial EEG | No record identifier or 75 s sample vector is supplied. No substitute patient waveform is presented. |

The first synthetic signal is defined explicitly in `scripts/synthetic_signal.py`. `rrse_fast` compares its known high-frequency component with the first extracted component; `rrse_slow_residue` compares the first residue with the known slow component. `rrse_reconstruction` checks summation. Reconstruction checks completeness, not component correctness or paper matching. The output includes individual rows, a manifest, and a summary so that any eventual result can be audited.

Optional source archives are [KEELE.zip, Zenodo record 3921794](https://zenodo.org/records/3921794) and [CUDB 1.0.0, PhysioNet](https://physionet.org/content/cudb/1.0.0/). `scripts/fetch_public_data.py` verifies the published Keele MD5 and CUDB record SHA-256 checksums in its versioned archive. Dataset licenses and attribution apply independently of this repository's Apache-2.0 code license. All downloaded archives and generated biomedical arrays remain outside version control.
