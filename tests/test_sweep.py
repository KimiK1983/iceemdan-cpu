"""A tiny end-to-end check of ordered, resumable sweep output."""

import json
import subprocess
import sys


def test_sweep_resume(tmp_path):
    command = [
        sys.executable,
        "-m",
        "scripts.run_synthetic_sweep",
        "--sizes",
        "1",
        "--seeds",
        "0",
        "--workers",
        "1",
        "--out",
        str(tmp_path),
        "--run",
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)
    subprocess.run(command + ["--resume"], check=True, capture_output=True, text=True)
    rows = [
        json.loads(line)
        for line in (tmp_path / "rows.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [(row["I"], row["seed"], row["status"]) for row in rows] == [(1, 0, "ok")]
    assert (
        json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))["attempts"]
        == 1
    )
