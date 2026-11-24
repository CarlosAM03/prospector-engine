"""Verify frozen provenance and inventory each deliberate extraction change."""

import argparse
import ast
import hashlib
import json
from pathlib import Path

import extract_frozen as frozen

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path, help="Read-only CLI repository with frozen Git objects")
frozen.SOURCE = parser.parse_args().source
root = Path.cwd()
assert frozen.git("rev-parse", "refs/tags/v1.0.0^{commit}").decode().strip() == frozen.COMMIT
entries = json.loads((root / "docs/extraction-manifest.json").read_text(encoding="utf-8"))
extensions = {
    "src/engines/config.py": "Add browser_channel (Edge default unchanged); raise per-query maximum from 100 to 150",
    "src/engines/prospector_engine.py": "Forward opt-in Chromium configuration for single/batch",
    "src/engines/browser_runtime.py": "Configurable browser and actionable Chromium failure; Windows constant fallback",
    "src/engines/_observability.py": "Check cooperative token before existing execution events",
    "src/engines/global_pipeline.py": "Promote existing aligned evidence into result",
    "src/models/search_result.py": "Add keyword-only aligned source_identities with unknown defaults",
    "src/scraper/google_maps/scraper.py": "Pass configurable channel, preserving default call",
}
refactors = {
    "src/scraper/google_maps/detail_panel.py": "Remove unused parser import (lint)",
    "src/utils/__init__.py": "Explicit re-export alias (lint)",
    "src/models/website_document.py": "Trim trailing whitespace inside module docstring only",
}
rows = []
for entry in entries:
    target = entry["destination"]
    if target is None:
        entry.update(
            reason="CLI, presentation, export, application paths or portable boundary",
            protected_contract="Excluded from extraction core",
            tests=[],
            modification="Not copied",
        )
        continue
    raw = frozen.git("show", f"{frozen.COMMIT}:{entry['source']}")
    assert hashlib.sha256(raw).hexdigest() == entry["source_sha256"]
    adapted = frozen.adapt(raw.decode())
    actual = (root / target).read_text(encoding="utf-8")
    equivalent = ast.dump(ast.parse(adapted), include_attributes=False) == ast.dump(
        ast.parse(actual), include_attributes=False
    )
    if entry["source"] in extensions:
        entry.update(
            classification="AMPLIADO CON CONTRATO NUEVO", modification=extensions[entry["source"]]
        )
    elif entry["source"] in refactors:
        entry.update(
            classification="REFACTORIZADO SIN CAMBIO SEMÁNTICO",
            modification=refactors[entry["source"]],
        )
    else:
        assert equivalent, f"Unaccounted semantic difference: {target}"
        entry["modification"] = (
            "Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging"
        )
    entry.update(
        target_sha256=hashlib.sha256((root / target).read_bytes()).hexdigest(),
        target_lf_sha256=hashlib.sha256(actual.encode()).hexdigest(),
        ast_equivalent_after_packaging=equivalent,
        reason="Retain the complete transitive extraction core without rewriting the pipeline",
        protected_contract="Frozen extraction, normalization, identity, sequential batch and resource semantics",
        tests=["tests/unit", "tests/integration"],
    )
    dependencies = []
    for node in ast.walk(ast.parse(actual)):
        if isinstance(node, ast.ImportFrom):
            dependencies.append(node.module or "")
        elif isinstance(node, ast.Import):
            dependencies.extend(alias.name for alias in node.names)
    entry["dependencies"] = sorted(set(dependencies))
    source = entry["source"]
    suites = {
        "normalization": [
            "tests/unit/test_normalization_rules.py",
            "tests/unit/test_normalization_engine.py",
            "tests/integration/test_global_normalization_pipeline.py",
        ],
        "selector": [
            "tests/unit/test_selector_infrastructure.py",
            "tests/unit/test_lazycharge_semantics.py",
        ],
        "website": [
            "tests/unit/test_website_components.py",
            "tests/unit/test_google_maps_website_enrichment.py",
            "tests/integration/test_controlled_website_engine.py",
        ],
        "navigation": [
            "tests/unit/test_google_maps_navigation.py",
            "tests/integration/test_typed_engine_failures.py",
        ],
        "batch": [
            "tests/unit/test_batch_contracts.py",
            "tests/unit/test_batch_deduplication.py",
            "tests/integration/test_batch_coordinator.py",
            "tests/integration/test_batch_deduplication_integration.py",
        ],
        "google_maps": [
            "tests/unit/test_google_maps_detail_panel.py",
            "tests/unit/test_google_maps_result_list.py",
            "tests/unit/test_google_maps_source_identity.py",
            "tests/integration/test_google_maps_pipeline_controlled.py",
            "tests/integration/test_virtual_feed_detail_recovery.py",
        ],
        "browser_runtime": [
            "tests/unit/test_browser_runtime.py",
            "tests/integration/test_cooperative_cancellation.py",
            "tests/integration/test_browser_availability.py",
        ],
        "observability": [
            "tests/unit/test_execution_observability.py",
            "tests/unit/test_public_extensions.py",
        ],
        "config": ["tests/unit/test_engine_config.py", "tests/unit/test_prospector_engine.py"],
        "global_pipeline": [
            "tests/integration/test_global_normalization_pipeline.py",
            "tests/integration/test_source_identity_sidecar.py",
        ],
        "prospector_engine": [
            "tests/unit/test_prospector_engine.py",
            "tests/unit/test_public_extensions.py",
            "tests/integration/test_batch_coordinator.py",
        ],
        "models": [
            "tests/unit/test_models.py",
            "tests/unit/test_normalized_business.py",
            "tests/unit/test_batch_contracts.py",
            "tests/unit/test_public_extensions.py",
        ],
        "utils": [
            "tests/unit/test_parser_helpers.py",
            "tests/unit/test_summary_parser_characterization.py",
        ],
        "issue_collector": ["tests/unit/test_search_issues.py"],
        "timing": ["tests/unit/test_timing_budgets.py"],
    }
    for key, tests in suites.items():
        if key in source:
            entry["tests"] = tests
            break
    rows.append(
        f"| `{entry['source']}` | `{target}` | {entry['classification']} | {entry['modification']} |"
    )
(root / "docs/extraction-manifest.json").write_text(
    json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
heading = f"""# Inventario de extracción

Origen: `CarlosAM03/prospector-cli`, tag `v1.0.0`, objeto anotado
`35088b4d53c31bb4fdde6c079b5e3d2f31873a32`, commit `{frozen.COMMIT}`.
Verificado en Git local y mediante GitHub. Se leyó el objeto del tag; no se hizo checkout ni modificación de CLI.

Se preserva la organización interna `engines/models/scraper/utils` bajo un único
namespace instalable para facilitar comparación. No se copió todo `src`.
El [manifiesto JSON](extraction-manifest.json) contiene por archivo commit,
SHA-256 origen/destino, dependencias, clasificación, motivo, contrato y tests.
La equivalencia AST se comprueba después de adaptar únicamente imports.

| Origen | Destino | Clasificación | Cambio |
|---|---|---|---|
"""
excluded = "\n".join(
    f"- `{e['source']}` — NO EXTRAÍDO: {e['reason']}" for e in entries if e["destination"] is None
)
tail = """

## API nueva

`__init__.py`, `browser.py`, `observability.py`, `cancellation.py` y `diagnostics.py`
son módulos nuevos; no se presentan como código congelado. No hay nuevos algoritmos
de extracción, normalización o deduplicación. Las extensiones se ejercitan en
`test_public_extensions.py`, `test_cooperative_cancellation.py` y `test_browser_availability.py`.

## Regresión portada

[test-migration.json](test-migration.json) clasifica todos los archivos de tests del tag.
Se excluyeron sólo la función CSV de un módulo mixto y la función Ctrl+C de otro;
se conservaron sus pruebas del pipeline y lifecycle. El probe interactivo website
sin funciones pytest se clasifica RESEARCH. El test de observabilidad recorre ahora
el namespace real del paquete, evitando una comprobación vacía. La prueba del flag
de proceso Windows usa su constante documentada al ejecutarse en Linux.

Reauditar: `python scripts/audit_provenance.py <repositorio-cli-read-only>`.
El script no modifica CLI. Los scripts de extracción son trazabilidad de esta fase;
el extractor se niega a sobreescribir una extracción existente.
"""
(root / "docs/extraction-inventory.md").write_text(
    heading + "\n".join(rows) + "\n\n## Exclusiones\n\n" + excluded + tail, encoding="utf-8"
)
print(f"Frozen tag, source hashes and {len(rows)} extracted modules VERIFIED")
