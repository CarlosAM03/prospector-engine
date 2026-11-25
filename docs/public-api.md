# Contrato público Python

Estado: IMPLEMENTED; regresión en [testing](testing.md). No es el contrato HTTP de Service.

```python
from prospector_engine import EngineConfig, ProspectorEngine, SearchQuery, Source

engine = ProspectorEngine(EngineConfig(limit=50))
result = engine.search(SearchQuery(Source.GOOGLE_MAPS, "dentistas", "Tijuana"))
```

`EngineConfig(limit=50, headless=False, website_enrichment=True, browser_channel="msedge")`
mantiene defaults congelados. La fachada rechaza límites fuera de 1–150 sin ajuste automático y antes de iniciar el browser;
el dataclass conserva su validación histórica de entero positivo. `browser_channel=None`
selecciona explícitamente Chromium administrado por Playwright. No hay fallback silencioso.
`SearchQuery(source, keyword, location)` conserva la semántica original: no exige texto
no vacío. El consumidor debe validarlo; cambiar esa garantía requiere decisión aparte.

`search(query) -> SearchResult`; `search_many(Sequence[BatchQuery]) -> BatchSearchResult`.
Batch acepta 1–5 solicitudes ordenadas, hace preflight y snapshot completos antes de
ejecutar. Cada consulta usa su propio `BatchQuery.limit` de 1 a 150 y un runtime
independiente. La ejecución es síncrona. La fuente puede devolver menos resultados.
El límite se aplica antes de la selección por identidad.

`SearchResult.businesses` son `NormalizedBusiness`; `original_businesses` son `Business`
independientes y alineados 1:1 en orden. Ambos conservan sus doce campos comerciales.
`total_found` cuenta extraídos, sin descontar supresiones batch; `execution_time` incluye
normalización. `issues` conserva incidencias recuperables y datos parciales.

## Identidad pública aditiva

`result.source_identities` es una tupla de `SourceIdentityEvidence` alineada con ambas
listas. `evidence.verified` es `VerifiedSourceIdentity` o `None`; `verification_state`
es `VerificationState.VERIFIED` o `UNVERIFIED`. El identificador de Maps sólo se obtiene
de `verified.value` cuando `source == Source.GOOGLE_MAPS` y `kind == "google_place_id"`.
Una observación desconocida se traduce a `None`, nunca a un token de navegación.

Se expone el mismo sidecar ya verificado por el pipeline P92, sin verificar de nuevo
ni inferir IDs. No se añade ningún campo a Business. El campo es keyword-only;
constructores históricos de SearchResult siguen funcionando y reciben evidencia
UNVERIFIED por defecto. El constructor valida cardinalidad y tipo. Los resultados
son modelos mutables históricos: si el consumidor modifica sus listas después,
debe preservar su correspondencia; no son contenedores con edición sincronizada.
Construir manualmente `VerifiedSourceIdentity` tampoco certifica evidencia real.

`BatchQueryResult` preserva resultados completos, `status`, `error`, `export_indices`,
`suppressed`, `unverified_identity_indices` y `observations`. Los nombres de selección
heredados de exportación son índices puros; no escriben CSV/XLSX.

## Observabilidad

```python
from prospector_engine import observe_execution

with observe_execution(lambda event: print(event.kind, event.stage, event.current, event.total)):
    result = engine.search(query)
```

`ExecutionEvent` es frozen y contiene `kind`, `stage`, `name`, `value`, `current`,
`total`, `query_index`. `EngineObserver` es un Protocol callable tipado. Se reutilizan
los ocho eventos del baseline: execution_started, stage_started, stage_completed,
progress_updated, metric_updated, recoverable_issue_observed, execution_completed,
execution_failed. Las incidencias observadas identifican etapa/código; los detalles
seguros se consultan en `result.issues`. Las métricas llegan como eventos individuales.

El context manager restaura el observador, incluso al fallar. Excepciones ordinarias
del callback se registran y no cambian resultados. Los callbacks son síncronos;
deben ser rápidos. No existe porcentaje global contractual. El scope debe crearse
en el thread que ejecuta el Engine; no depende de Rich ni de señales.

## Errores y parcialidad

`ProspectorError` agrupa `ProspectorConfigurationError`, `ProspectorSourceError`,
`ProspectorNavigationError`, `ProspectorExtractionError`, `ProspectorRuntimeError` y
`BatchInterruptedError`. Conservan causas encadenadas para diagnóstico local.
Los fallos esperados de navegación/extracción de una consulta batch pueden dar FAILED
y permitir continuar. Fallos críticos o cleanup no confiable interrumpen con
`BatchInterruptedError.completed`, índice interrumpido y consultas restantes.
Las incidencias de feed/detalle/website/normalización no se convierten automáticamente
en fallos fatales. Un resultado parcial puede contener negocios válidos.

## Cancelación cooperativa

```python
from prospector_engine import CancellationRequested, CancellationToken, cancellation_scope

token = CancellationToken()
# Otro thread puede llamar token.request_cancel().
try:
    with cancellation_scope(token):
        result = engine.search(query)
except CancellationRequested:
    pass  # El consumidor decide su lifecycle; no hay protocolo HTTP aquí.
```

El token es de un solo uso. Se comprueba antes de cada evento existente, incluso sin
observador: antes del source y en transiciones, métricas y progreso por negocio.
La excepción hereda `BaseException` deliberadamente para atravesar handlers ordinarios
de extracción, batch y observadores; debe capturarse explícitamente. El unwind usa
los context managers de recursos existentes. No interrumpe una llamada Playwright
bloqueante ni mata procesos. Descarta el valor de retorno de la invocación cancelada;
no ofrece partial-prefix, persistencia ni resume. Si cleanup falla se conserva el
indicador `_prospector_cleanup_failed`; el consumidor no debe asumir cierre exitoso.
La traducción a cancelación HTTP sigue DEFERRED.
