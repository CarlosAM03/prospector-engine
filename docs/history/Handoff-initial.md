
# 1. Estado real de Prospector CLI v1.0.0

La release estable está correctamente identificada:

```text
Tag:
v1.0.0

Annotated tag:
35088b4d53c31bb4fdde6c079b5e3d2f31873a32

Frozen source:
bd50cf7cbba76ccd75517d06037662dff4797b05

PR:
#1 V1.0.0
v1.0.0 → main
MERGED
```

La documentación de cierre registra:

```text
STABLE / RELEASED / COMPLETE

229 unit PASS
69 integration PASS
298 offline PASS
1 owner-run live E2E PASS
freeze audit PASS
owner acceptance COMPLETE
```

El artefacto Windows publicado corresponde a:

```text
Prospector-CLI-v1.0.0-win64.zip
53,658,917 bytes
```

El `main` actual está en:

```text
63e018d0d7ce574f24f3233beadcccd63af5a876
```

y está sólo **3 commits por delante del source congelado**. La comparación `bd50cf7... → main` muestra únicamente documentación y backlog; **no hay cambios posteriores en `src/`**.

Por tanto:

```text
v1.0.0 tagged source
        ==
current extraction implementation
```

a nivel de código.

Para extraer el Engine usaría como autoridad reproducible:

```text
v1.0.0
bd50cf7cbba76ccd75517d06037662dff4797b05
```

y no `main`, aunque actualmente el código sea equivalente.

Hay dos observaciones de governance que no invalidan la release, pero no repetiría en Engine/Service: `main` de CLI no está protegido y el repositorio no tiene actualmente un workflow GitHub Actions versionado. La evidencia de estabilidad proviene del freeze y sus pruebas locales, no de CI remoto.

---

# 2. Alcance cerrado de Prospector CLI v1.0.0

La v1.0.0 estable implementa este pipeline:

```text
SearchQuery
    ↓
ProspectorEngine
    ↓
BrowserRuntime
    ↓
Google Maps
    ↓
feed / summary extraction
    ↓
detail-panel enrichment
    ↓
Website Engine
    ↓
Business[]
    ↓
Global Normalization
    ↓
NormalizedBusiness[]
    ↓
SearchResult
```

El contrato programático principal ya existe:

```python
ProspectorEngine(config).search(query) -> SearchResult
```

y también:

```python
ProspectorEngine(config).search_many(queries) -> BatchSearchResult
```

La v1.0.0 soporta hoy:

| Capacidad | Estado |
|---|---|
| Google Maps | Completo |
| Una búsqueda | Completo |
| Batch Engine 1–5 queries | Completo |
| CLI batch 2–3 queries | Completo |
| Límite Engine 1–100 | Completo |
| Default CLI 50 | Completo |
| Summary extraction | Completo |
| Detail enrichment | Completo |
| Website enrichment | Completo |
| Normalización global | Completo |
| `Business` original | Completo |
| `NormalizedBusiness` | Completo |
| Recoverable issues | Completo |
| Typed fatal errors | Completo |
| Identidad Google Place ID verificada | Completo bajo política estricta |
| Deduplicación cross-query por identidad verificada | Completo |
| CSV | Completo |
| XLSX | Completo |
| Browser visible | Completo |
| Browser background/headless | Soportado, menos fiable que visible |
| Windows portable | Completo |

No implementa:

```text
HTTP API
FastAPI
Jobs
queue
persistencia
SaaS
campaigns
multi-tenant
distributed execution
checkpoint/resume
background service
durable cancellation
```

Y eso es correcto: **no eran parte del producto CLI v1.0.0**.

---

# 3. Qué código realmente constituye el Engine

La arquitectura interna ya hizo gran parte del trabajo de desacoplamiento.

El test suite incluso garantiza que:

```text
engines/
scraper/
models/
```

no importen Rich.

`ProspectorEngine` tampoco importa:

```text
CLI
ExportService
app paths
terminal presentation
```

Así que hay una frontera bastante limpia.

## Código que SÍ debe extraerse a `PROSPECTOR_ENGINE`

El núcleo es:

```text
src/engines/
```

completo:

```text
_observability.py
_timing.py
browser_runtime.py
config.py
errors.py
global_pipeline.py
issue_collector.py
prospector_engine.py

batch/
navigation/
normalization/
selector/
website/
```

También:

```text
src/models/
```

incluyendo:

```text
Business
NormalizedBusiness
SearchQuery
SearchResult
SearchIssue

BatchQuery
BatchQueryResult
BatchSearchResult

SourceIdentityEvidence
VerifiedSourceIdentity

WebsiteDocument
WebsiteMetadata
```

Y:

```text
src/scraper/google_maps/
```

completo:

```text
search
scraper
result_list
detail_panel
parser
selectors
source_identity
website_enrichment
```

Finalmente existe una dependencia pequeña:

```text
src/utils/parser.py
```

porque Google Maps parser consume `is_phone`.

Conceptualmente:

```text
PROSPECTOR_ENGINE
│
├── Engine facade
├── domain models
├── normalization
├── browser runtime
├── navigation
├── selector infrastructure
├── lazy/dynamic synchronization
├── website engine
├── Google Maps source
├── identity
├── batch
├── issues/errors
└── observability
```

---

# 4. Qué NO debe extraerse al Engine

Esto debe quedarse fuera:

```text
src/main.py
src/cli_app.py
src/cli_runtime.py
src/app_paths.py
```

porque pertenece a:

```text
Prospector CLI
```

También dejaría fuera del Engine:

```text
src/exporters/
src/services/export_service.py
src/services/_export_directory.py
src/utils/file_naming.py
```

Aunque `ExportService` es reusable y está clasificado como `PUBLIC_STABLE`, arquitectónicamente **no pertenece al extraction core**.

Esto coincide con la propia arquitectura v1.0.0:

```text
ProspectorEngine
      ↓
 SearchResult
      ↓
consumer

CLI consumer ──→ ExportService
```

Para SaaS, el export debe terminar perteneciendo a Platform Backend, no al Engine.

Y definitivamente no migraría:

```text
scripts/build_windows_portable.py
portable Windows logic
Rich
PyInstaller
CLI logging directories
Ctrl+C terminal UX
```

---

# 5. Tests que deben acompañar al Engine

No debemos extraer sólo código. El valor real de esta v1.0.0 está en su regresión.

Migraría al repositorio Engine los tests relacionados con:

```text
EngineConfig
ProspectorEngine
BrowserRuntime
Execution observability
typed failures
SearchResult / models
SearchIssue
Normalization
Google Maps navigation
virtual feed
detail panel
source identity
Website Engine
LazyCharge
selectors
timing budgets
batch contracts
batch coordinator
batch deduplication
global normalization
controlled Google Maps pipeline
website integration
identity sidecar
partial results
```

Dejaría en CLI:

```text
CLI menus
Rich rendering
CLI cancellation UX
portable paths
CSV/XLSX presentation
Windows portable
PyInstaller
```

Así, Engine nace conservando la evidencia técnica importante, no como un fork vacío.

---

# 6. Dependencias del Engine

No copiaría `requirements.txt` de CLI tal cual.

Actualmente contiene muchas dependencias históricas que no son parte directa del extraction core.

Las dependencias externas claramente usadas por Engine son principalmente:

```text
playwright==1.61.0
beautifulsoup4==4.15.0
```

y sus transitivas.

`openpyxl` es export.

`rich` es CLI.

PyInstaller es packaging CLI.

El nuevo Engine debería tener un:

```text
pyproject.toml
```

propio y mínimo.

---

# 7. Problema físico actual: todavía no es un paquete Python limpio

Aunque conceptualmente está desacoplado, físicamente sigue usando imports como:

```python
from engines...
from models...
from scraper...
```

porque todo el `src` del CLI actúa como raíz de imports.

Eso funciona en el repo CLI, pero no es una frontera de distribución limpia.

Para el repositorio nuevo recomiendo algo equivalente a:

```text
prospector-engine/
│
├── pyproject.toml
├── src/
│   └── prospector_engine/
│       ├── __init__.py
│       ├── config.py
│       ├── errors.py
│       ├── engine.py
│       ├── observability.py
│       ├── models/
│       ├── pipeline/
│       ├── browser/
│       ├── navigation/
│       ├── normalization/
│       ├── selector/
│       ├── website/
│       └── sources/
│           └── google_maps/
└── tests/
```

No hace falta reescribir la lógica; sí hay que convertir imports a un namespace instalable.

---

# 8. Los tres contratos que debemos distinguir

Aquí está la parte más importante.

Actualmente existen **dos contratos**, pero falta un tercero.

### A. Contrato público Python del Engine — EXISTE

Está congelado por Prospector CLI v1.0.0:

```text
ProspectorEngine.search()
ProspectorEngine.search_many()

EngineConfig
SearchQuery
SearchResult

Business
NormalizedBusiness
SearchIssue

Batch*
ProspectorError*
```

La documentación de v1.0.0 los clasifica explícitamente como:

```text
PUBLIC_STABLE
```

Ésta es nuestra materia prima.

---

### B. Contrato Platform Backend ↔ Prospector Service — EXISTE

Ya está definido en:

```text
saas-platform-backend
Docs/Contracts/prospector-service-api.v1.yaml
```

El Platform enviará:

```http
POST /api/v1/prospecting/jobs
X-API-Key: ...
```

con:

```json
{
  "jobId": "...",
  "tenantId": "...",
  "query": {
    "keyword": "...",
    "location": "...",
    "source": "google_maps",
    "limit": 50
  },
  "callbackUrl": "..."
}
```

Service responde:

```text
202 Accepted
```

con:

```text
jobId
status = QUEUED
acceptedAt
```

Y Service → Platform usa:

```http
POST /api/v1/internal/prospecting-jobs/{jobId}/events
X-API-Key
```

con:

```text
eventId
jobId
sequence
status
timestamp
progress
results
error
```

Eso ya está diseñado.

---

### C. Contrato Prospector Service ↔ Prospector Engine — NO EXISTE FORMALMENTE

Éste es el hueco actual.

Hoy una futura API podría simplemente importar:

```python
ProspectorEngine
EngineConfig
SearchQuery
```

pero no existe una especificación que diga:

```text
qué debe recibir el Engine desde Service
qué debe devolver
cómo reporta progreso
cómo se cancela
cómo expone identidad
cómo clasifica errores
```

Este es el contrato que tenemos que cerrar antes de implementar Service de verdad.

---

# 9. Input Service → Engine: casi ya existe

El request de Platform:

```text
keyword
location
source
limit
```

mapea casi directamente a:

```python
SearchQuery(
    source=Source.GOOGLE_MAPS,
    keyword=...,
    location=...,
)

EngineConfig(
    limit=...,
    headless=...,
    website_enrichment=...,
)
```

Por tanto **no necesitamos meter `tenantId`, `jobId` ni `callbackUrl` dentro del Engine**.

Esto sería incorrecto:

```text
Engine
├── tenant
├── campaign
├── job
├── callback
└── API key
```

Engine debe permanecer ajeno a todo eso.

La arquitectura correcta es:

```text
FastAPI Service
│
├── jobId
├── tenantId
├── callback
├── queue
├── API key
└── lifecycle
       │
       ↓
ProspectorEngine
├── query
├── limit
├── runtime config
└── extraction
```

---

# 10. Primer drift contractual encontrado: `limit`

Engine v1.0.0 tiene una regla cerrada:

```text
1 ≤ limit ≤ 100
```

Y rechaza:

```text
101+
```

antes de abrir browser.

Pero Platform actualmente sólo dice:

```text
minimum: 1
```

y su DTO NestJS sólo tiene:

```text
@Min(1)
```

No existe `@Max(100)`.

El contrato interno Service también sólo define:

```text
minimum: 1
```

Por tanto hoy existe un drift real:

```text
Platform acepta 500
        ↓
Service contract acepta 500
        ↓
Engine rechaza 500
```

Esto debe corregirse antes de integrar.

Mi recomendación:

```text
ProspectingQuery.limit

minimum: 1
maximum: 100
```

en:

```text
Platform public OpenAPI
NestJS DTO
Platform ↔ Service OpenAPI
FastAPI Pydantic
Flutter DTO validation
```

El máximo 100 ya está aprobado y probado por Engine.

---

# 11. Segundo drift: keyword/location vacíos

CLI v1.0.0 obliga a ingresar:

```text
keyword no vacío
location no vacío
```

pero `SearchQuery` como dataclass no valida contenido.

Y NestJS actualmente sólo exige:

```text
@IsString()
```

Por tanto:

```json
{
  "keyword": "",
  "location": ""
}
```

es contractualmente posible desde Platform.

Para API debemos cerrar:

```text
trimmed non-empty keyword
trimmed non-empty location
```

idealmente en el contrato HTTP y Service, no confiar en una UI.

---

# 12. El mayor gap de output: `sourceIdentifier`

Platform espera:

```text
BusinessResult
├── name
├── category
├── address
├── phone
├── email
├── website
├── source
├── sourceIdentifier
├── language
└── metadata
```

Engine actual entrega normalizado:

```text
NormalizedBusiness
├── name
├── category
├── address
├── phone
├── website
├── email
├── language
├── website_title
├── website_description
├── has_contact_page
├── has_about_page
└── website_status
```

Los campos principales mapean perfectamente.

`source` también:

```text
SearchResult.query.source
→ google_maps
```

Pero `sourceIdentifier` tiene un problema.

Engine sí calcula una identidad verificada:

```text
VerifiedSourceIdentity(
    source=GOOGLE_MAPS,
    kind="google_place_id",
    value="ChIJ..."
)
```

pero en búsqueda individual esa información permanece en un **sidecar privado**:

```text
_GlobalExecution.identities
```

y no aparece en `SearchResult`.

En batch sí termina reflejada en provenance.

Para Service necesitamos acceso público.

### Gap del Engine

Debemos exponer de manera pública y alineada:

```text
source identity por resultado
```

sin obligar a Service a importar:

```python
_run_google_maps
_GlobalExecution
```

que son privados.

---

# 13. ¿Es `sourceIdentifier` bloqueante?

Contractualmente no:

```text
sourceIdentifier
nullable
```

Service podría enviar:

```json
"sourceIdentifier": null
```

y cumplir OpenAPI.

Pero hacerlo desperdiciaría una de las mejores capacidades que ya tiene el Engine: **Google Place ID verificado**.

Para v1.0.0 de Engine/Service recomiendo preservar:

```text
verified Google Place ID
→ BusinessResult.sourceIdentifier
```

y:

```text
UNVERIFIED
→ null
```

Eso nos ayudará enormemente para deduplicación futura en Platform.

---

# 14. `metadata` tampoco tiene mapping definido

Platform permite:

```text
metadata: object | null
```

Engine tiene información que no cabe como propiedades top-level de `BusinessResult`:

```text
website_title
website_description
has_contact_page
has_about_page
website_status
```

No debemos perderla.

Hay que definir un mapping contractual.

Por ejemplo, Service puede producir:

```json
{
  "metadata": {
    "websiteTitle": "...",
    "websiteDescription": "...",
    "hasContactPage": true,
    "hasAboutPage": false,
    "websiteStatus": 200
  }
}
```

Sólo con valores realmente disponibles.

Esto es responsabilidad del **adapter Service ↔ Engine**, no de Platform UI.

---

# 15. Recoverable issues no tienen destino

Engine tiene un contrato excelente:

```text
SearchResult.issues
```

para:

```text
partial_results
identity_unverifiable
website inspection unavailable
normalization field unavailable
...
```

La filosofía es:

```text
problema recuperable
≠
Job FAILED
```

Pero el callback actual sólo tiene:

```text
progress
results
error
```

No tiene:

```text
issues
warnings
partial
```

Por tanto tenemos una decisión pendiente.

Un Engine puede devolver:

```text
20 BusinessResult válidos
+
feed/partial_results
```

¿Qué debe ver Platform?

### Opción mínima v1

```text
Job = COMPLETED
results = válidos
issues = sólo logs Service
```

No requiere cambiar contrato.

### Opción más rica

Añadir al callback:

```text
issues[]
```

y posteriormente permitir que Platform los exponga.

Mi recomendación para el MVP es **no bloquear integración por esto**:

```text
recoverable issues
→ COMPLETED
→ resultados preservados
→ logs del Service
```

pero registrar la pérdida de observabilidad como deuda contractual.

---

# 16. Progreso: existe infraestructura, pero todavía es privada

Engine ya emite eventos muy útiles:

```text
execution_started
stage_started
stage_completed
progress_updated
metric_updated
recoverable_issue_observed
execution_completed
execution_failed
```

Y stages como:

```text
navigation
feed
detail
website
normalization
result_assembly
```

Esto es exactamente la información que el Service necesitará.

Pero hoy está en:

```text
engines._observability
```

El prefijo `_` importa: la propia v1.0.0 no lo declara contrato público.

Service no debería acoplarse permanentemente a un módulo privado.

Necesitamos promover una interfaz pública, por ejemplo conceptualmente:

```text
EngineExecutionEvent
EngineObserver
observe_execution()
```

con contrato estable.

---

# 17. `PipelineProgress.percentage` todavía no existe como semántica Engine

Platform requiere:

```text
stage
message
percentage 0–100
```

Engine emite:

```text
current
total
stage
```

pero no un porcentaje global.

El Service puede construirlo, pero necesitamos decidir la política.

Ejemplo:

```text
navigation        0–10
feed             10–40
detail           40–70
website          70–90
normalization    90–98
assembly         98–100
```

No afirmo que ésos deban ser los porcentajes concretos; ésa es una política que debemos fijar.

Una alternativa más simple para primera integración:

```text
RUNNING
progress = null
```

porque el contrato lo permite.

Y añadir porcentaje real después.

Eso permitiría integrar Jobs antes sin inventar una métrica falsa.

---

# 18. Cancellation: el Engine no tiene todavía un contrato reutilizable

CLI v1.0.0 sí puede cancelar de forma controlada mediante:

```text
Ctrl+C
CancellationState
ExecutionCancelled
observability checkpoints
```

Pero:

```text
CancellationState
```

vive en:

```text
cli_runtime.py
```

Es deliberadamente CLI-only.

FastAPI no puede depender de Ctrl+C.

Para Service necesitamos algo como:

```text
CancellationToken
request_cancel()
is_cancelled
raise_if_cancelled()
```

consumible por Engine en safe checkpoints.

Éste es un cambio real requerido para soportar:

```http
POST /prospecting-jobs/{id}/cancel
```

de manera limpia.

---

# 19. Y además falta el contrato HTTP interno de cancelación

Hay otro problema independiente.

Platform pública ya tiene:

```http
POST /api/v1/prospecting-jobs/{id}/cancel
```

pero:

```text
prospector-service-api.v1.yaml
```

NO tiene actualmente una ruta:

```text
Platform → Service → cancel
```

Una ruta que había existido fue eliminada explícitamente del baseline.

Así que cancelación tiene dos gaps:

```text
1. Service HTTP cancel contract
2. Engine cancellation contract
```

No debemos implementarla silenciosamente.

Necesita decisión formal antes.

---

# 20. BrowserRuntime: principal gap de despliegue

Este probablemente es el mayor impedimento técnico para llamar al Engine “Service-ready”.

Actualmente está hardcodeado:

```python
playwright.chromium.launch(
    channel="msedge",
    ...
)
```

Y v1.0.0 fue aceptado bajo esta política:

```text
Windows
Microsoft Edge Stable
Visible default
Background supported
```

Prospector Service probablemente correrá como:

```text
Docker
Linux
headless
```

Eso NO ha sido certificado por la release CLI.

Además la documentación de v1.0.0 reconoce que:

```text
Background
```

resultó menos fiable que Visible en validaciones acotadas.

Por tanto no podemos simplemente copiar el código a un contenedor y declarar Engine listo.

---

# 21. Decisión de browser para Service

Tenemos dos caminos razonables.

### Camino conservador

Mantener:

```text
Microsoft Edge Stable
```

también dentro del contenedor Linux.

Ventaja:

```text
menor diferencia respecto a la v1.0.0 aceptada
```

Desventaja:

```text
imagen Docker más compleja
Edge instalado explícitamente
headless sigue necesitando validación
```

### Camino más natural para contenedor

Usar:

```text
Playwright Chromium
```

Ventaja:

```text
ecosistema Docker Playwright mucho más natural
```

Desventaja:

```text
cambia el browser certificado por CLI v1.0.0
requiere regresión completa y live acceptance
```

Yo empezaría intentando preservar Edge en una prueba containerizada. Si la experiencia es mala, entonces haría configurable el navegador.

En cualquier caso, Engine necesita dejar de asumir que una única política de browser sirve para todos los consumidores.

---

# 22. Compatibilidad Python también debe validarse

La evidencia del CLI menciona Python:

```text
3.13.4
```

en su entorno histórico/regresión.

El Service originalmente se había planteado con Python 3.11.

El código parece usar features compatibles con 3.11, pero eso **no equivale a certificación**.

Antes de cerrar Engine:

```text
full Engine suite on Python 3.11
```

debe ser un gate.

---

# 23. Sin concurrencia certificada

`BrowserRuntime` posee un browser por búsqueda, lo cual es bueno.

Pero la v1.0.0 no certifica:

```text
N búsquedas simultáneas
```

`search_many()` es deliberadamente:

```text
secuencial
```

y el propio diseño dice que no existe global browser lock.

Por tanto el primer Service no debería empezar con:

```text
10 workers paralelos
```

Mi recomendación para v1.0:

```text
FastAPI
  ↓
bounded queue
  ↓
1 Engine worker
  ↓
1 Job activo
```

Luego medimos y aumentamos concurrencia.

Eso reduce enormemente el riesgo.

---

# 24. Batch Engine no debe exponerse todavía en FastAPI

Engine soporta:

```text
1–5 BatchQuery
```

pero Platform Job actual contiene exactamente:

```text
una ProspectingQuery
```

No hay motivo para ampliar el contrato SaaS ahora.

Para Platform v1:

```text
1 Job
=
1 Query
```

`search_many()` se conserva dentro del Engine porque ya está probado y es parte de su contrato reusable, pero **Service v1 no necesita exponerlo**.

Esto evita scope creep.

---

# 25. Qué debe hacer FastAPI Service

La arquitectura debería quedar:

```text
Platform Backend
     │
     │ POST /prospecting/jobs
     ▼
Prospector Service
     │
     ├── Auth X-API-Key
     ├── validation
     ├── Job queue
     ├── lifecycle
     ├── Engine adapter
     ├── callback adapter
     └── cancellation
             │
             ▼
       Prospector Engine
```

No:

```text
FastAPI
→ scraper internals
```

FastAPI debe depender exclusivamente de la API pública del Engine.

---

# 26. API FastAPI mínima requerida

### Endpoint de aceptación

Ya definido:

```http
POST /api/v1/prospecting/jobs
```

Debe:

```text
1. autenticar X-API-Key
2. validar body
3. comprobar jobId duplicado
4. encolar trabajo
5. responder inmediatamente 202
```

No debe esperar a Google Maps antes de responder.

---

# 27. FastAPI no debe devolver 422 por defecto

Esto es un detalle importante.

FastAPI/Pydantic por defecto devuelve:

```text
422 Unprocessable Entity
```

ante validation errors.

Nuestro contrato dice:

```text
400 Bad Request
```

con wrapper:

```json
{
  "success": false,
  "error": {
    "code": "...",
    "message": "...",
    "details": {},
    "timestamp": "..."
  }
}
```

Por tanto el Service debe tener un:

```text
RequestValidationError handler
```

que traduzca:

```text
422 FastAPI
→ 400 contractual
```

y el formato de error pactado.

---

# 28. Worker del Service

Engine es síncrono.

FastAPI no debe ejecutar:

```python
engine.search(...)
```

directamente en el event loop HTTP.

Necesitamos:

```text
HTTP thread/event loop
      ↓
queue
      ↓
worker
      ↓
sync ProspectorEngine
```

Para MVP:

```text
1 Service process
1 Engine worker
```

es suficiente.

No recomiendo depender sólo de `FastAPI BackgroundTasks` como si fuera una cola robusta.

---

# 29. Lifecycle Service

Service debe controlar:

```text
QUEUED
  ↓
RUNNING
  ↓
COMPLETED
FAILED
CANCELLED
```

Engine no debe conocer esos estados.

Mapping:

```text
Service accepts
→ QUEUED

worker starts
→ RUNNING

engine.search returns
→ COMPLETED

ProspectorError fatal
→ FAILED

cancel token confirmed
→ CANCELLED
```

---

# 30. Mapping de errores Engine → Service

Debemos congelar al menos una tabla semántica.

Por ejemplo:

| Engine | Job error |
|---|---|
| `ProspectorConfigurationError` | `CONFIGURATION_ERROR` |
| `ProspectorSourceError` | `UNSUPPORTED_SOURCE` |
| `ProspectorNavigationError` | `NAVIGATION_FAILED` |
| `ProspectorExtractionError` | `EXTRACTION_FAILED` |
| `ProspectorRuntimeError` | `RUNTIME_UNAVAILABLE` |
| cancellation | `CANCELLED` |
| excepción inesperada | `INTERNAL_ERROR` |

No enviar:

```text
Playwright internal exception
DOM selector internals
filesystem paths
stack traces
```

al Platform.

Eso preserva el modelo seguro que Engine ya usa.

---

# 31. Callback Service → Platform

Cada evento necesita:

```text
eventId UUID
jobId
sequence
status
timestamp
progress
results
error
```

Service deberá mantener:

```text
sequence monotónico por Job
```

y cada reintento del mismo evento debería reutilizar:

```text
mismo eventId
misma sequence
```

para permitir idempotencia en Platform.

---

# 32. Retries del callback

Callbacks son el único mecanismo actual para entregar:

```text
progress
results
failure
```

Así que no deberían ser fire-and-forget.

Necesitamos definir:

```text
timeout
retry count
backoff
```

y retener temporalmente el evento hasta recibir:

```text
HTTP 200
```

Esto pertenece al Service, no al Engine.

---

# 33. `callbackUrl` también necesita endurecimiento

El contrato actual dice:

```text
uri-reference
```

pero Prospector Service será otro proceso/máquina.

Para producción necesitamos realmente:

```text
absolute HTTP(S) URL
```

Preferiblemente:

```text
HTTPS
```

y conviene restringirla al Platform conocido para no convertir el Service en un SSRF client.

Éste es otro punto contractual que debe cerrarse.

---

# 34. Mapping final Engine → BusinessResult

La traducción recomendada queda:

| Engine | Platform |
|---|---|
| `NormalizedBusiness.name` | `name` |
| `category` | `category` |
| `address` | `address` |
| `phone` | `phone` |
| `email` | `email` |
| `website` | `website` |
| `language` | `language` |
| `SearchQuery.source` | `source` |
| verified Place ID | `sourceIdentifier` |
| website extra fields | `metadata` |

Esto permite mantener prácticamente toda la calidad actual de extracción.

---

# 35. Qué NO debe conocer Engine

Para preservar desacoplamiento:

```text
Engine NO conoce:
tenantId
campaignId
userId
jobId
callbackUrl
FastAPI
NestJS
PostgreSQL
API keys
HTTP wrappers
Job lifecycle
Platform DTOs
```

Engine simplemente hace:

```text
input extraction contract
      ↓
execution
      ↓
output extraction contract
```

El Service es el Anti-Corruption Layer entre Engine y Platform.

---

# 36. Qué falta del Engine para ser compatible

Clasificación final:

| Gap | Estado | Bloqueante |
|---|---|---:|
| Lógica Google Maps | Ya existe | No |
| Normalización | Ya existe | No |
| Website enrichment | Ya existe | No |
| Error model | Ya existe | No |
| Batch | Ya existe | No |
| Engine facade | Ya existe | No |
| Package Python independiente | Falta | Sí |
| Namespace instalable | Falta | Sí |
| requirements mínimos | Falta | Sí |
| Python Service runtime validation | Falta | Sí |
| Container/headless browser validation | Falta | **Sí crítico** |
| Browser policy configurable | Falta/decidir | Probablemente |
| Public source identity in single result | Falta | Recomendado fuerte |
| Service-facing metadata mapping | Falta | Sí para conservar alcance |
| Public observability contract | Falta | Para progreso |
| Percentage semantics | Falta | No para MVP mínimo |
| Public cancellation primitive | Falta | Sí para cancel real |
| Parallel execution certification | Falta | No si concurrency=1 |
| Limit max=100 across contracts | Drift | **Sí** |
| Non-empty query semantics | Drift | Sí |
| Recoverable issue propagation | Sin definir | No para primera integración |

---

# 37. Qué contratos debemos crear ahora

No necesitamos inventar diez contratos. Necesitamos cerrar cuatro.

### ENG-CONTRACT-01 — Engine Public API

Congelar:

```text
EngineConfig
SearchQuery
ProspectorEngine.search()
SearchResult
ProspectorError hierarchy
```

más el mecanismo público que permita obtener identidad.

---

### ENG-CONTRACT-02 — Engine Execution Events

Definir contrato público para:

```text
execution start
stage changes
progress
completion
failure
recoverable issues
```

sin Rich ni FastAPI.

---

### ENG-CONTRACT-03 — Engine Cancellation

Algo equivalente a:

```text
CancellationToken
```

con cancelación únicamente en safe checkpoints.

---

### SVC-CONTRACT-01 — Service ↔ Engine Adapter

Definir formalmente:

```text
Platform query
→ SearchQuery + EngineConfig

SearchResult + identities
→ BusinessResult[]

ProspectorError
→ JobEventError

Engine events
→ PipelineProgress
```

Éste es el contrato que actualmente falta por completo.

---

# 38. Contratos HTTP existentes que NO debemos reinventar

Ya tenemos:

```text
prospector-service-api.v1.yaml
```

Por tanto FastAPI debe implementarlo, no diseñar otro API paralelo.

Necesitamos sólo corregir/ratificar:

```text
limit maximum 100
keyword/location nonempty
callbackUrl absolute/HTTPS policy
cancel endpoint
recoverable issues policy
```

El resto ya ofrece una base suficiente.

---

# 39. Alcance recomendado de Prospector Engine v1.0.0

Yo cerraría el primer Engine independiente con este alcance:

```text
Google Maps only
single search
batch 1–5 retained
1–100 result policy
mandatory normalization
website enrichment
verified source identity
safe recoverable issues
typed fatal errors
execution observer
safe cancellation token
one BrowserRuntime per execution
no persistence
no HTTP
no jobs
no tenant
no SaaS
no exports
no CLI
```

Y sólo después de validar:

```text
Python target
Linux/container runtime
headless browser
full offline regression
live Google Maps smoke
```

lo etiquetaría:

```text
prospector-engine v1.0.0
```

No lo etiquetaría hoy sólo porque el código proviene de CLI v1.0.0.

---

# 40. Alcance recomendado de Prospector Service v1.0.0

Después:

```text
FastAPI
X-API-Key
POST accept Job
bounded in-memory queue
single worker initially
Engine adapter
callback client
monotonic sequence
event UUID
callback retries
error mapping
result mapping
health/live/ready
structured logging
Docker
```

Y posteriormente:

```text
cancel endpoint
```

cuando cerremos su contrato y Engine cancellation.

No necesita:

```text
database
Prisma
CRM
campaign persistence
prospect persistence
CSV export
XLSX export
multi-tenant DB
```

Esas responsabilidades permanecen en Platform.

---

# 41. Arquitectura objetivo

Queda muy limpia:

```text
Flutter
   │
   ▼
Platform Backend NestJS
   │
   │ REST / X-API-Key
   ▼
Prospector Service FastAPI
   │
   │ Python in-process API
   ▼
Prospector Engine
   │
   ├── BrowserRuntime
   ├── Google Maps
   ├── Website Engine
   └── Normalization
```

Y resultados:

```text
Engine
   ↓
SearchResult
   ↓
Service adapter
   ↓
BusinessResult[]
   ↓ callback
Platform
   ↓
cache temporal
   ↓
Flutter
```

---

# 42. Checklist para comenzar la extracción

### Prospector CLI v1.0.0

```text
[x] Stable tag verified
[x] Frozen source identified
[x] Current main source equivalent to tag
[x] Engine facade exists
[x] Models exist
[x] Google Maps pipeline exists
[x] Normalization exists
[x] Identity exists
[x] Batch exists
[x] Error model exists
[x] Regression suite exists
```

### Prospector Engine

```text
[ ] Crear repositorio físico PROSPECTOR_ENGINE
[ ] Extraer desde bd50cf7
[ ] Crear namespace prospector_engine
[ ] Migrar engine/models/scraper
[ ] Migrar parser helper requerido
[ ] Migrar tests relevantes
[ ] Crear pyproject.toml mínimo
[ ] Eliminar dependencias CLI/export
[ ] Definir public __init__ API
[ ] Exponer identity de single-search
[ ] Formalizar observability pública
[ ] Formalizar cancellation token
[ ] Validar Python objetivo
[ ] Resolver browser runtime de servidor
[ ] Ejecutar offline regression
[ ] Ejecutar container regression
[ ] Ejecutar live E2E
[ ] Tag Engine v1.0.0
```

### Prospector Service

```text
[ ] Crear repositorio PROSPECTOR_SERVICE
[ ] Copiar/sincronizar prospector-service-api.v1.yaml
[ ] Crear contract parity test
[ ] FastAPI bootstrap
[ ] API-key dependency
[ ] Error wrapper
[ ] FastAPI 422 → 400
[ ] POST /prospecting/jobs
[ ] 202 accepted
[ ] Job registry/queue
[ ] Single Engine worker
[ ] Engine adapter
[ ] Result adapter
[ ] Callback adapter
[ ] Sequence/eventId
[ ] Retry/timeout callbacks
[ ] health/live/ready
[ ] Docker
[ ] E2E Service → Engine
```

### Contratos / decisiones

```text
[ ] max limit = 100
[ ] keyword/location nonempty
[ ] callbackUrl policy
[ ] sourceIdentifier mapping
[ ] metadata mapping
[ ] recoverable issues policy
[ ] progress semantics
[ ] cancel Service endpoint
[ ] Engine cancellation semantics
[ ] concurrency v1 = 1
```

---

## Veredicto

**Prospector CLI v1.0.0 es una base muy buena para el nuevo Engine.** No tenemos que reescribir el scraper ni reconstruir el pipeline: Google Maps, navegación, BrowserRuntime, detalle, Website Engine, normalización, identidad, batch, errores y casi toda la observabilidad ya existen y están ampliamente probados.

La brecha hacia la Plataforma no está principalmente en scraping. Está aquí:

```text
CLI ENGINE CODE
ya maduro
        ↓
PHYSICAL ENGINE PACKAGE
pendiente
        ↓
SERVICE↔ENGINE CONTRACT
pendiente
        ↓
SERVER BROWSER RUNTIME
pendiente crítico
        ↓
FASTAPI JOB ORCHESTRATION
pendiente
        ↓
CALLBACK LIFECYCLE
pendiente
        ↓
PLATFORM INTEGRATION
pendiente
```
 **dos drifts que conviene corregir antes de escribir FastAPI**: la Plataforma todavía no expresa el máximo `limit=100`, y ni Platform ni Service formalizan que `keyword/location` deban ser no vacíos.

El trabajo siguiente debería empezar por **definir y crear `PROSPECTOR_ENGINE` desde el tag congelado**, no por FastAPI. Una vez que podamos instalar el Engine como paquete independiente y ejecutar `ProspectorEngine.search()` desde un proceso externo al CLI, tendremos una frontera estable sobre la que construir el Service sin arrastrar la interfaz, los exporters ni el portable de Windows.