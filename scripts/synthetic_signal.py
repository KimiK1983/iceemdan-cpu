"""The two-component synthetic signal used for the paper comparison."""

import numpy as np


def signal_parts():
    n = np.arange(1, 1001)
    fast = np.zeros(1000)
    fast[500:750] = np.sin(2 * np.pi * 0.255 * (n[500:750] - 501))
    slow = np.sin(2 * np.pi * 0.065 * (n - 1))
    return fast, slow, fast + slow
