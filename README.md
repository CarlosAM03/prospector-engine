# Prospector Engine — 0.1.0.dev0

Paquete Python independiente y síncrono de extracción Google Maps, enriquecimiento
de websites y normalización. Primera extracción física desde **Prospector CLI v1.0.0**,
commit congelado `bd50cf7cbba76ccd75517d06037662dff4797b05`, tag anotado
`35088b4d53c31bb4fdde6c079b5e3d2f31873a32`, verificados localmente y en GitHub.

**Estado: desarrollo; sin release estable independiente.** La estabilidad de CLI
acredita procedencia, no aceptación de Engine v1.0.0. Se preservan íntegros el
[README inicial](docs/history/README-initial.md) y el [Handoff inicial](docs/history/Handoff-initial.md).

## Implementado

- `search()` y `search_many()` secuencial de 1–5 consultas.
- Google Maps: navegación, selectors/elector/lazycharge, feed virtual, resumen y detalle.
- Website Engine y BrowserRuntime propio por búsqueda.
- Límite predeterminado 50 y máximo solicitado 150 por consulta de Google Maps.
  Los valores fuera del rango se rechazan; la fuente puede devolver menos resultados.
- Normalización obligatoria; originales y normalizados independientes, alineados 1:1.
- Issues recuperables, resultados parciales y errores fatales tipados.
- Identidad verificada P92 y deduplicación estricta entre consultas, sin matching comercial.
- Identidad pública alineada, observador público y cancelación cooperativa.
- Edge predeterminado; Chromium configurable; Docker con usuario no root.

El paquete no incluye CLI, Rich, exportadores, portable Windows, FastAPI, HTTP, jobs,
colas, auth, tenants, campañas, CRM ni persistencia.

## Instalación y runtime

Requiere **Python >=3.11**. Dependencias directas: Playwright 1.61.0 y BeautifulSoup4
4.15.0. [constraints.txt](requirements/constraints.txt) fija transitivas/herramientas.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -c requirements/constraints.txt -e ".[dev]"
```

Microsoft Edge Stable instalado es el baseline Windows; `headless=False` es el default.
Para Chromium, instalar `python -m playwright install chromium` y seleccionar
`EngineConfig(headless=True, browser_channel=None)`. En Linux se requieren también
las bibliotecas de `python -m playwright install --with-deps chromium`.
El import no descarga ni inicia browsers. [runtime.md](docs/runtime.md) describe
la adaptación de este host Windows con rutas largas deshabilitadas.

## Uso Python

Este ejemplo requiere browser y acceso real a Google Maps:

```python
from prospector_engine import EngineConfig, ProspectorEngine, SearchQuery, Source

engine = ProspectorEngine(EngineConfig(limit=10))
query = SearchQuery(Source.GOOGLE_MAPS, "dentistas", "Tijuana")
result = engine.search(query)

for business, identity in zip(result.businesses, result.source_identities):
    source_identifier = identity.verified.value if identity.verified else None
    print(business.name, business.phone, source_identifier)
```

La API pública incluye modelos individuales/batch, errores, identidad,
`ExecutionEvent`, `EngineObserver`, `observe_execution`, `CancellationToken`,
`CancellationRequested` y `cancellation_scope`. Véase [public-api.md](docs/public-api.md).
El paquete instalado no necesita que exista Prospector CLI.

## Arquitectura

```text
Consumidor Python -> ProspectorEngine
    -> BrowserRuntime + Google Maps + Website Engine
    -> normalización global -> SearchResult (originales, normalizados, identidad, issues)
    -> batch secuencial y selección por identidad verificada
```

Layout `src/prospector_engine`; organización interna conservada para facilitar
comparación con el tag. [Arquitectura](docs/architecture.md),
[inventario por archivo](docs/extraction-inventory.md).

## Pruebas y distribución

```powershell
python -m compileall -q src
python -m ruff check .
python -m ruff format --check .
python -m pytest tests/unit -q
python -m pytest tests/integration -q
python -m pytest -q -m "not e2e"
python -m build
python scripts/wheel_smoke.py
```

Integración requiere Chromium y utiliza localhost o dobles controlados, sin Google
Maps público. `wheel_smoke.py` instala un wheel en otra venv e importa con Python
aislado desde site-packages. Instalación distribuible:
`python -m pip install dist/prospector_engine-0.1.0.dev0-py3-none-any.whl`.
[testing.md](docs/testing.md) y [validation-results.json](docs/validation-results.json)
separan evidencia local, Linux, CI remoto y live. Ruff lint cubre todo el código;
el formato de archivos portados se conserva con exclusiones explícitas.

## Docker

```powershell
docker build -t prospector-engine:dev .
docker run --rm --init --shm-size=1g --cap-drop=ALL --security-opt=no-new-privileges prospector-engine:dev
```

La imagen instala el wheel real, Python 3.11 y Chromium 1228; ejecuta UID 10001.
Su diagnóstico navega a HTTP localhost y verifica cleanup; no es un servidor HTTP
de producto ni scraping público. Base fijada por digest y constraints Python.
Para importación solamente, añadir `python -m prospector_engine.diagnostics`.
[Runtime, recursos y límites](docs/runtime.md).

## CI y gobierno

[ci.yml](.github/workflows/ci.yml): quality, integration, package y docker-build;
Python 3.11/3.13, integración Ubuntu/Windows; push main/rama feature, PR main y dispatch.
Permisos mínimos contents read. El live no es required check ni se publican releases.

El remoto configurado es `CarlosAM03/prospector-engine`. Los resultados de CI de
la extracción se registran en [validation-results.json](docs/validation-results.json).
La evidencia del candidato se mantiene en el [informe de aceptación](docs/v1.0.0/acceptance-report.md).

## Integración, versión y límites

Service consumirá la API Python y adaptará datos/events/errors a HTTP; ese adaptador
no se implementó aquí. [Preparación y mapping](docs/integration-readiness.md).
El Engine no recibe datos SaaS. La integración permanece CONDITIONAL por drifts
HTTP y aceptación productiva del browser.

Localhost no prueba confiabilidad Google Maps headless ni equivalencia Edge/Chromium.
No se ejecutó live E2E de esta extracción. Google Maps puede cambiar; un límite no
garantiza completitud. UNVERIFIED se conserva y permite aparentes duplicados.
Contact/about/content_type conservan limitaciones del baseline; concurrencia no
certificada. Cancelación espera checkpoints y no ofrece resume ni protocolo HTTP.

[Decisiones pendientes](docs/decisions-pending.md): browser productivo, contratos
Service/Platform, progreso/issues/cancelación HTTP y acceso remoto. Versionado
independiente pre-1.0; release estable y freeze requieren aceptación propia.
Licencia [MIT](LICENSE), preservada del original.
