"""Run controlled Linux gates against the image's installed package.

Mount only this Engine at /work and run as the image's ordinary user.
Generated distributions, tests and build logs remain associated with this repo.
"""

import os
from pathlib import Path
import subprocess
import sys

root = Path.cwd()
scratch = Path("/tmp/prospector-engine-gates")
scratch.mkdir(parents=True, exist_ok=True)
os.environ["TMPDIR"] = str(scratch)
os.environ["PROSPECTOR_CONSUMER_TMP"] = str(scratch)
artifacts = root / "artifacts"
artifacts.mkdir(exist_ok=True)
commands = [
    (
        "install",
        [
            "-m",
            "pip",
            "install",
            "--user",
            "--no-cache-dir",
            "-c",
            "requirements/constraints.txt",
            "pytest",
            "ruff",
            "build",
            "setuptools",
            "wheel",
        ],
    ),
    ("compile", ["-m", "compileall", "-q", "src"]),
    ("lint", ["-m", "ruff", "check", "."]),
    ("format", ["-m", "ruff", "format", "--check", "."]),
    ("unit", ["-m", "pytest", "tests/unit", "-q", "--basetemp=.tmp/linux/unit", "--tb=short"]),
    (
        "integration",
        [
            "-m",
            "pytest",
            "tests/integration",
            "-q",
            "--basetemp=.tmp/linux/integration",
            "--tb=short",
        ],
    ),
    (
        "offline",
        ["-m", "pytest", "-q", "-m", "not e2e", "--basetemp=.tmp/linux/offline", "--tb=short"],
    ),
    ("build", ["-m", "build", "--no-isolation"]),
    ("wheel-isolation", ["scripts/wheel_smoke.py"]),
]
for name, args in commands:
    print(f"Linux Python {sys.version.split()[0]}: {name}", flush=True)
    with (artifacts / f"{name}-linux.txt").open("w") as output:
        completed = subprocess.run([sys.executable, *args], stdout=output, stderr=subprocess.STDOUT)
    print((artifacts / f"{name}-linux.txt").read_text()[-2500:], flush=True)
    if completed.returncode:
        raise SystemExit(completed.returncode)
