"""Exercise the installed wheel while launched outside the source checkout."""

from pathlib import Path

import numpy as np

import ICEEMDAN
from ICEEMDAN import ICEEMDAN as Model

root = Path(__file__).resolve().parents[1]
assert not Path(ICEEMDAN.__file__).resolve().is_relative_to(root)
t = np.arange(64, dtype=float)
signal = np.sin(0.7 * t) + 0.3 * np.sin(0.12 * t)
model = Model(trials=2, epsilon=0.2, seed=42)
parts = model(signal, max_imf=2)
np.testing.assert_allclose(parts.sum(axis=0), signal, rtol=0, atol=1e-12)
assert np.array_equal(parts[-1], model.get_imfs_and_residue()[1])
print(f"installed example: {ICEEMDAN.__file__}")
