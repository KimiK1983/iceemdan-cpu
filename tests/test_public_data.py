"""Minimal checks for the local CUDB decoder."""

import numpy as np

from scripts.analyze_cudb import decode_212, vf_onsets


def test_cudb_format_and_annotation():
    np.testing.assert_array_equal(decode_212(bytes([255, 127, 255])), [-1, 2047])
    assert vf_onsets(bytes([25, 128, 0, 0])) == [25]
