"""Create the repository's original, synthetic decomposition illustration."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from ICEEMDAN import ICEEMDAN

plt.rcParams["svg.hashsalt"] = "iceemdan-cpu"


def main():
    n = np.arange(256)
    x = np.sin(2 * np.pi * 0.045 * n) + 0.35 * np.sin(2 * np.pi * 0.17 * n)
    parts = ICEEMDAN(trials=4, epsilon=0.2, seed=7)(x, max_imf=3)
    fig, axes = plt.subplots(len(parts) + 1, 1, figsize=(9, 7), sharex=True)
    axes[0].plot(n, x, color="#1b365d", lw=1)
    axes[0].set_ylabel("signal")
    for index, (axis, part) in enumerate(zip(axes[1:], parts)):
        axis.plot(
            n, part, color="#007c78" if index < len(parts) - 1 else "#be5a2c", lw=1
        )
        axis.set_ylabel(f"c{index + 1}" if index < len(parts) - 1 else "residue")
    axes[-1].set_xlabel("sample")
    fig.suptitle("Synthetic example: 4 trials, ε = 0.2, seed 7")
    fig.tight_layout()
    path = (
        Path(__file__).resolve().parents[1] / "assets" / "synthetic_decomposition.svg"
    )
    fig.savefig(path, metadata={"Date": None})
    plt.close(fig)
    svg = (
        "\n".join(
            line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()
        )
        + "\n"
    )
    with path.open("w", encoding="utf-8", newline="\n") as output:
        output.write(svg)
    print(path)


if __name__ == "__main__":
    main()
