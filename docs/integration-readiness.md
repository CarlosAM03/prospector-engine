# Preparación para un consumidor Service

Estado: interfaz Python IMPLEMENTED. Integración con Service CONDITIONAL; no se implementó HTTP.

| Entrada del consumidor | Engine |
|---|---|
| keyword, location, source | SearchQuery; validar strings no vacíos en consumidor |
| limit | EngineConfig, rango 1–100; default 50 |
| política de browser | Edge por defecto; Chromium opt-in con headless explícito |
| progreso | observe_execution en el thread del worker |
| cancelación cooperativa | cancellation_scope con token compartido; outcome explícito |

El Engine no recibe tenantId, campaignId, userId, jobId, callbackUrl, API keys,
JWT, request HTTP ni DTOs de Platform. El futuro adaptador será responsabilidad de Service.
El Engine síncrono debe ejecutarse fuera del event loop HTTP. No se certificó ejecución
paralela; comenzar con una invocación activa es una política conservadora del consumidor.

| Salida Engine | Mapping propuesto para el adaptador |
|---|---|
| NormalizedBusiness: name/category/address/phone/email/website/language | Campos equivalentes de BusinessResult |
| result.query.source.value | source |
| source_identities[i].verified.value (Maps/google_place_id) | sourceIdentifier |
| UNVERIFIED | sourceIdentifier=null |
| website_title, website_description, has_contact_page, has_about_page, website_status | metadata del consumidor, con naming acordado |
| issues | Conservar en diagnósticos; política de callback pendiente |

El contrato HTTP consultado sólo exige `limit >= 1`: carece de máximo 100 y de reglas
de texto no vacío. `PipelineProgress` exige porcentaje cuando existe, pero permite
progreso null. Recomendación: enviar null hasta definir una política de porcentaje;
no presentar el ratio de una etapa como progreso global.
No existe endpoint interno de cancelación en ese baseline. No se alteró el contrato.

| Error Python | Categoría sugerida del adaptador, pendiente de ratificación |
|---|---|
| ProspectorConfigurationError | CONFIGURATION_ERROR |
| ProspectorSourceError (antes de ExtractionError) | UNSUPPORTED_SOURCE |
| ProspectorNavigationError | NAVIGATION_FAILED |
| ProspectorExtractionError | EXTRACTION_FAILED |
| ProspectorRuntimeError | RUNTIME_UNAVAILABLE |
| BatchInterruptedError | Fallo crítico con prefijo Python recuperable |
| CancellationRequested | Outcome de cancelación, sin redefinir HTTP |

El adaptador debe capturar `CancellationRequested` explícitamente y no enviar causas,
stack traces, HTML o rutas internas a Platform. La disponibilidad de browser en localhost
no certifica Google Maps live, confiabilidad headless, concurrencia ni capacidad universal
100. Website contact/about y content_type siguen con las limitaciones del baseline.

Pendientes externos: validar drifts HTTP, aceptación live del browser productivo y
prueba end-to-end del futuro adaptador. Ninguno autoriza escribir en Backend o Service.
