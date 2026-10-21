"""Build outputs must already exist; install a wheel into a fresh isolated venv.

All generated files remain under the Engine. Run from a short Windows checkout
when long paths are disabled. No source path is injected into the consumer.
"""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv

ROOT = Path.cwd()
wheel = next((ROOT / "dist").glob("prospector_engine-*-py3-none-any.whl"))
if "editable" in wheel.name:
    wheel = next(w for w in (ROOT / "dist").glob("*.whl") if "editable" not in w.name)
scratch = Path(os.environ.get("PROSPECTOR_CONSUMER_TMP", str(ROOT / ".tmp")))
scratch.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix="consumer-", dir=scratch) as directory:
    base = Path(directory)
    venv.EnvBuilder(with_pip=False).create(base / "venv")
    python = base / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)
    # Call the requested interpreter path directly: venv's internal pip helper
    # resolves SUBST drives to the long physical path on Windows.
    subprocess.run([str(python), "-m", "ensurepip"], check=True, env=environment)
    subprocess.run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-c",
            str(ROOT / "requirements/constraints.txt"),
            str(wheel),
        ],
        check=True,
        env=environment,
    )
    code = """
from pathlib import Path
import prospector_engine as api
from prospector_engine import ProspectorEngine, EngineConfig, SearchQuery, Source
assert 'site-packages' in str(Path(api.__file__))
assert EngineConfig().limit == 50
assert ProspectorEngine.ENGINE_MAX_LIMIT == 100
assert SearchQuery(Source.GOOGLE_MAPS, 'cafe', 'TJ').source is Source.GOOGLE_MAPS
assert api.__version__ == '0.1.0.dev0'
from types import SimpleNamespace
from unittest.mock import patch
def controlled_source(query, limit, **options):
    return SimpleNamespace(query=query, businesses=[api.Business(' cafe ')], issues=[],
                           identities=[api.SourceIdentityEvidence.unverified()])
query = SearchQuery(Source.GOOGLE_MAPS, 'cafe', 'TJ')
with patch('prospector_engine.engines.prospector_engine._run_google_maps', controlled_source):
    engine = ProspectorEngine(EngineConfig(limit=1))
    result = engine.search(query)
    assert result.businesses[0].name == 'CAFE'
    assert result.original_businesses[0].name == ' cafe '
    assert result.source_identities[0].verified is None
    batch = engine.search_many([api.BatchQuery(query, 1)])
    assert batch.total_exportable == 1
print('isolated wheel consumer PASS:', api.__file__)
"""
    subprocess.run([str(python), "-I", "-c", code], cwd=base, check=True, env=environment)
print(f"Wheel isolation PASS on {sys.version.split()[0]}")
