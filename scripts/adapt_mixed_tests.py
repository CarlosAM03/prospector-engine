"""Record and remove only CLI/export portions of mixed frozen test modules."""

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
removals = {
    "tests/unit/test_browser_runtime.py": {"test_confirmed_ctrl_c_unwinds_through_browser_runtime"},
    "tests/integration/test_google_maps_pipeline_controlled.py": {
        "test_t_i03_partial_result_still_exports_legacy_schema"
    },
}
for file, names in removals.items():
    path = ROOT / file
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    for node in reversed(ast.parse(content).body):
        if isinstance(node, ast.FunctionDef) and node.name in names:
            del lines[node.lineno - 1 : node.end_lineno]
    content = "".join(lines)
    content = content.replace(
        "from cli_runtime import ExecutionCancelled, controlled_interrupt\n", ""
    )
    content = content.replace(
        "from services.export_service import ExportFormat, ExportService\n", ""
    )
    path.write_text(content, encoding="utf-8")

path = ROOT / "tests/unit/test_execution_observability.py"
content = path.read_text(encoding="utf-8").replace('/ "src"', '/ "src" / "prospector_engine"')
path.write_text(content, encoding="utf-8")
# This file has an interactive main(), no collected test functions.
path = ROOT / "tests/integration/test_website_engine.py"
path.unlink()
manifest = ROOT / "docs/test-migration.json"
entries = json.loads(manifest.read_text())
for entry in entries:
    if entry["source"] in removals:
        entry["excluded_functions"] = sorted(removals[entry["source"]])
        entry["notes"] = "Mixed module: CLI cancellation / CSV export functions excluded"
    if entry["source"] == "tests/integration/test_website_engine.py":
        entry.update(
            category="RESEARCH",
            migrated=False,
            notes="Interactive website probe; no pytest functions",
        )
manifest.write_text(json.dumps(entries, indent=2), encoding="utf-8")
