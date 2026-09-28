"""Focused CPU regressions against saved synthetic oracle outputs."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.interpolate import CubicSpline

import ICEEMDAN as product


def _baseline():
    directory = Path(__file__).with_name("fixtures")
    path = directory / "ordinary_baselines.npz"
    metadata = json.loads(
        (directory / "ordinary_baselines.json").read_text(encoding="utf-8")
    )
    assert metadata["reference_sha256"] == (
        "d697bfb841ab2b099a1961a4575b671ba08867748e5cee63225f55a4be365b3a"
    )
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest()
        == metadata["fixture_sha256"]
        == ("5bb522c9ecd2751ced8bbaaac0f0f4ebd66ceb0c94a7fd509635288d4c4260a3")
    )
    with np.load(path, allow_pickle=False) as arrays:
        return {key: arrays[key] for key in arrays.files}, metadata


def test_backend_rejects_nonfinite_reconstruction_defect():
    class Backend:
        def __init__(self, modes, residue):
            self.modes, self.residue = modes, residue

        def emd(self, signal, t, max_imf):
            pass

        def get_imfs_and_residue(self):
            return self.modes, self.residue

    signal = np.full(8, 1e-300)
    t = np.arange(len(signal), dtype=float)
    with pytest.raises(product.BackendContractError, match="reconstruction"):
        product._backend_parts(
            Backend(np.full((1, 8), 1e308), np.full(8, -1e308)), signal, t, 1
        )
    modes, residue, _ = product._backend_parts(
        Backend(np.array([np.full(8, 1e308), np.full(8, -1e308)]), signal.copy()),
        signal,
        t,
        2,
    )
    np.testing.assert_array_equal(modes.sum(axis=0) + residue, signal)


def test_epsilon_zero_without_extractable_imf_terminates():
    signal = CubicSpline(
        np.linspace(0, 63, 7),
        [
            1.6324326927834527,
            -1.877901750973295,
            -1.6079837666476737,
            -1.317525148354537,
            -0.08275273999265884,
            0.033899292086251885,
            0.029076569410149824,
        ],
    )(np.arange(64.0))
    assert product.EMD()(signal).shape == (1, len(signal))
    model = product.ICEEMDAN(trials=2, epsilon=0)
    result = model(signal)
    assert result.shape == (1, len(signal))
    np.testing.assert_allclose(result[0], signal, rtol=0, atol=1e-14)
    assert model.diagnostics_["stop_reason"] == "emd_has_no_extractable_imf"
    assert model.diagnostics_["natural_termination"] is True


def test_epsilon_zero_with_zero_mode_still_raises():
    class ZeroMode:
        def emd(self, signal, t, max_imf):
            self.signal = signal

        def get_imfs_and_residue(self):
            return np.zeros((1, len(self.signal))), self.signal.copy()

    t = np.arange(128.0)
    signal = np.sin(0.7 * t) + 0.3 * np.cos(0.13 * t)
    with pytest.raises(product.SiftingConvergenceError, match="no progress"):
        product.ICEEMDAN(trials=1, epsilon=0, ext_EMD=ZeroMode())(signal, max_imf=1)


def test_first_noise_mode_subnormal_scale():
    t = np.arange(192.0)
    signal = np.sin(0.73 * t) + 0.5 * np.cos(0.14 * t)
    w = np.sin(0.34 * t)
    results = []
    for factor in (1.0, 1e-310, 1e150):
        model = product.ICEEMDAN(trials=1)
        model.generate_noise = lambda scale, size, factor=factor: (
            (factor * w).copy() * scale
        )
        out = model(signal, max_imf=1)
        assert out.shape == (2, len(signal)) and np.isfinite(out).all()
        assert model.diagnostics_["stop_reason"] == "max_imf"
        results.append(out)
    for out in results[1:]:
        np.testing.assert_allclose(out, results[0], rtol=1e-7, atol=1e-8)


def test_ordinary_shared_noise_preserves_oracle():
    fixture, metadata = _baseline()
    t = np.arange(192.0)
    signal = np.sin(0.71 * t) + 0.5 * np.sin(0.21 * t) + 0.3 * np.sin(0.035 * t)
    W = np.random.default_rng(7).normal(size=(4, len(t)))
    candidate = product.ICEEMDAN(trials=4)
    rows = iter(W)
    candidate.generate_noise = lambda scale, size: next(rows).copy() * scale
    expected = fixture["shared_components"]
    actual = candidate(signal, max_imf=3)
    assert actual.shape == expected.shape and actual.dtype == expected.dtype
    np.testing.assert_allclose(actual, expected, rtol=1e-9, atol=1e-10, equal_nan=False)
    assert candidate.diagnostics_["stop_reason"] == metadata["shared"]["stop_reason"]
    assert (
        candidate.diagnostics_["noise_mode_counts"]
        == metadata["shared"]["noise_mode_counts"]
    )
    assert [s["sift_iterations"] for s in candidate.diagnostics_["stages"]] == metadata[
        "shared"
    ]["sift_iterations"]


def test_ordinary_seeded_noise_preserves_oracle():
    fixture, metadata = _baseline()
    t = np.arange(128.0)
    signal = np.sin(0.73 * t) + 0.3 * np.cos(0.12 * t)
    candidate = product.ICEEMDAN(trials=3, seed=42)
    expected = fixture["seeded_components"]
    actual = candidate(signal, max_imf=2)
    assert actual.shape == expected.shape and actual.dtype == expected.dtype
    np.testing.assert_allclose(actual, expected, rtol=1e-9, atol=1e-10, equal_nan=False)
    assert candidate.diagnostics_["stop_reason"] == metadata["seeded"]["stop_reason"]
    assert (
        candidate.diagnostics_["noise_mode_counts"]
        == metadata["seeded"]["noise_mode_counts"]
    )
    assert candidate.random.bit_generator.state == metadata["seeded"]["rng_state_after"]


def test_small_parallel_seeded_run_matches_serial():
    t = np.arange(96.0)
    signal = np.sin(0.71 * t) + 0.3 * np.cos(0.13 * t)
    serial = product.ICEEMDAN(trials=2, seed=7)
    parallel = product.ICEEMDAN(trials=2, seed=7, parallel=True, processes=2)
    expected = serial(signal, max_imf=1)
    actual = parallel(signal, max_imf=1)
    assert actual.shape == expected.shape and actual.dtype == expected.dtype
    np.testing.assert_allclose(actual, expected, rtol=1e-9, atol=1e-10, equal_nan=False)
    assert parallel.diagnostics_["stop_reason"] == serial.diagnostics_["stop_reason"]
    assert repr(parallel.random.bit_generator.state) == repr(
        serial.random.bit_generator.state
    )
