# Inventario de extracción

Origen: `CarlosAM03/prospector-cli`, tag `v1.0.0`, objeto anotado
`35088b4d53c31bb4fdde6c079b5e3d2f31873a32`, commit `bd50cf7cbba76ccd75517d06037662dff4797b05`.
Verificado en Git local y mediante GitHub. Se leyó el objeto del tag; no se hizo checkout ni modificación de CLI.

Se preserva la organización interna `engines/models/scraper/utils` bajo un único
namespace instalable para facilitar comparación. No se copió todo `src`.
El [manifiesto JSON](extraction-manifest.json) contiene por archivo commit,
SHA-256 origen/destino, dependencias, clasificación, motivo, contrato y tests.
La equivalencia AST se comprueba después de adaptar únicamente imports.

| Origen | Destino | Clasificación | Cambio |
|---|---|---|---|
| `src/engines/__init__.py` | `src/prospector_engine/engines/__init__.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/_observability.py` | `src/prospector_engine/engines/_observability.py` | AMPLIADO CON CONTRATO NUEVO | Check cooperative token before existing execution events |
| `src/engines/_timing.py` | `src/prospector_engine/engines/_timing.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/batch/__init__.py` | `src/prospector_engine/engines/batch/__init__.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/batch/deduplication.py` | `src/prospector_engine/engines/batch/deduplication.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/browser_runtime.py` | `src/prospector_engine/engines/browser_runtime.py` | AMPLIADO CON CONTRATO NUEVO | Configurable browser and actionable Chromium failure; Windows constant fallback |
| `src/engines/config.py` | `src/prospector_engine/engines/config.py` | AMPLIADO CON CONTRATO NUEVO | Add browser_channel (Edge default unchanged); raise per-query maximum from 100 to 150 |
| `src/engines/errors.py` | `src/prospector_engine/engines/errors.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/global_pipeline.py` | `src/prospector_engine/engines/global_pipeline.py` | AMPLIADO CON CONTRATO NUEVO | Promote existing aligned evidence into result |
| `src/engines/issue_collector.py` | `src/prospector_engine/engines/issue_collector.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/navigation/__init__.py` | `src/prospector_engine/engines/navigation/__init__.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/navigation/google_maps_navigation.py` | `src/prospector_engine/engines/navigation/google_maps_navigation.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/navigation/navigation_engine.py` | `src/prospector_engine/engines/navigation/navigation_engine.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/normalization/__init__.py` | `src/prospector_engine/engines/normalization/__init__.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/normalization/normalization_engine.py` | `src/prospector_engine/engines/normalization/normalization_engine.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/normalization/rules.py` | `src/prospector_engine/engines/normalization/rules.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/prospector_engine.py` | `src/prospector_engine/engines/prospector_engine.py` | AMPLIADO CON CONTRATO NUEVO | Forward opt-in Chromium configuration for single/batch |
| `src/engines/selector/__init__.py` | `src/prospector_engine/engines/selector/__init__.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/selector/elector_engine.py` | `src/prospector_engine/engines/selector/elector_engine.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/selector/lazycharge.py` | `src/prospector_engine/engines/selector/lazycharge.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/selector/profiles.py` | `src/prospector_engine/engines/selector/profiles.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/selector/registry.py` | `src/prospector_engine/engines/selector/registry.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/selector/selector_engine.py` | `src/prospector_engine/engines/selector/selector_engine.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/website/__init__.py` | `src/prospector_engine/engines/website/__init__.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/website/crawler.py` | `src/prospector_engine/engines/website/crawler.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/website/email.py` | `src/prospector_engine/engines/website/email.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/website/extractor.py` | `src/prospector_engine/engines/website/extractor.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/website/lenguaje.py` | `src/prospector_engine/engines/website/lenguaje.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/website/metadata.py` | `src/prospector_engine/engines/website/metadata.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/website/parser.py` | `src/prospector_engine/engines/website/parser.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/engines/website/website_engine.py` | `src/prospector_engine/engines/website/website_engine.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/models/__init__.py` | `src/prospector_engine/models/__init__.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/models/batch.py` | `src/prospector_engine/models/batch.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/models/business.py` | `src/prospector_engine/models/business.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/models/normalized_business.py` | `src/prospector_engine/models/normalized_business.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/models/search_issue.py` | `src/prospector_engine/models/search_issue.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/models/search_query.py` | `src/prospector_engine/models/search_query.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/models/search_result.py` | `src/prospector_engine/models/search_result.py` | AMPLIADO CON CONTRATO NUEVO | Add keyword-only aligned source_identities with unknown defaults |
| `src/models/source_identity.py` | `src/prospector_engine/models/source_identity.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/models/website_document.py` | `src/prospector_engine/models/website_document.py` | REFACTORIZADO SIN CAMBIO SEMÁNTICO | Trim trailing whitespace inside module docstring only |
| `src/models/website_metadata.py` | `src/prospector_engine/models/website_metadata.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/scraper/__init__.py` | `src/prospector_engine/scraper/__init__.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/scraper/google_maps/__init__.py` | `src/prospector_engine/scraper/google_maps/__init__.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/scraper/google_maps/detail_panel.py` | `src/prospector_engine/scraper/google_maps/detail_panel.py` | REFACTORIZADO SIN CAMBIO SEMÁNTICO | Remove unused parser import (lint) |
| `src/scraper/google_maps/parser.py` | `src/prospector_engine/scraper/google_maps/parser.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/scraper/google_maps/result_list.py` | `src/prospector_engine/scraper/google_maps/result_list.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/scraper/google_maps/scraper.py` | `src/prospector_engine/scraper/google_maps/scraper.py` | AMPLIADO CON CONTRATO NUEVO | Pass configurable channel, preserving default call |
| `src/scraper/google_maps/search.py` | `src/prospector_engine/scraper/google_maps/search.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/scraper/google_maps/selectors.py` | `src/prospector_engine/scraper/google_maps/selectors.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/scraper/google_maps/source_identity.py` | `src/prospector_engine/scraper/google_maps/source_identity.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/scraper/google_maps/website_enrichment.py` | `src/prospector_engine/scraper/google_maps/website_enrichment.py` | ADAPTADO POR PACKAGING | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |
| `src/utils/__init__.py` | `src/prospector_engine/utils/__init__.py` | REFACTORIZADO SIN CAMBIO SEMÁNTICO | Explicit re-export alias (lint) |
| `src/utils/parser.py` | `src/prospector_engine/utils/parser.py` | COPIADO SIN CAMBIO FUNCIONAL | Namespace imports / trailing-whitespace cleanup only; AST equivalent after packaging |

## Exclusiones

- `src/app_paths.py` — NO EXTRAÍDO: CLI, presentation, export, application paths or portable boundary
- `src/cli_app.py` — NO EXTRAÍDO: CLI, presentation, export, application paths or portable boundary
- `src/cli_runtime.py` — NO EXTRAÍDO: CLI, presentation, export, application paths or portable boundary
- `src/exporters/__init__.py` — NO EXTRAÍDO: CLI, presentation, export, application paths or portable boundary
- `src/exporters/base.py` — NO EXTRAÍDO: CLI, presentation, export, application paths or portable boundary
- `src/exporters/csv.py` — NO EXTRAÍDO: CLI, presentation, export, application paths or portable boundary
- `src/exporters/excel.py` — NO EXTRAÍDO: CLI, presentation, export, application paths or portable boundary
- `src/exporters/export_view.py` — NO EXTRAÍDO: CLI, presentation, export, application paths or portable boundary
- `src/main.py` — NO EXTRAÍDO: CLI, presentation, export, application paths or portable boundary
- `src/services/_export_directory.py` — NO EXTRAÍDO: CLI, presentation, export, application paths or portable boundary
- `src/services/export_service.py` — NO EXTRAÍDO: CLI, presentation, export, application paths or portable boundary
- `src/utils/file_naming.py` — NO EXTRAÍDO: CLI, presentation, export, application paths or portable boundary
- `src/version.py` — NO EXTRAÍDO: CLI, presentation, export, application paths or portable boundary

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
