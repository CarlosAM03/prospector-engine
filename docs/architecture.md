# Arquitectura y autoridades

Estado: IMPLEMENTED. Versión independiente `0.1.0.dev0`, sin release estable.

| Orden | Autoridad | Aplicación en esta extracción |
|---|---|---|
| 1 | Instrucción explícita del propietario | Escritura sólo Engine, conservar contratos, sin merge ni release |
| 2 | Contratos congelados CLI v1.0.0; ContractInventory, FREEZE, ADR-008/009/010 | Normalización 1:1, batch 1–5, límite 1–100, identidad verificada |
| 3 | Código del tag, commit `bd50cf7cbba76ccd75517d06037662dff4797b05` | Fuente física de los 53 módulos |
| 4 | Tests del mismo commit | Regresión portada y clasificada |
| 5 | Handoff original Engine | Frontera Python, gaps de identidad, eventos y runtime |
| 6 | README inicial e historia CLI | Contexto histórico; afirmaciones de Engine estable/v0.7.0 quedan superadas |
| 7 | Propuestas de Service | Orientan integración; no cambian garantías congeladas |

Se consultaron README, arquitectura, scripting-pipeline, pipeline Maps, FREEZE,
RELEASED, KNOWN_LIMITATIONS, ContractInventory, ValidationMatrix y tests/README de CLI;
ADR-008 (normalización), ADR-009 (batch e identidad) y ADR-010 (freeze/runtime).
El contrato `Backend_Nestjs/saas-platform-backend/Docs/Contracts/prospector-service-api.v1.yaml`
y la documentación de Service se consultaron en lectura. No se copiaron secretos ni entornos.

```text
Consumidor Python
    -> prospector_engine: ProspectorEngine + EngineConfig + SearchQuery
        -> scraper/google_maps: navegación, feed, resumen, detalle, identidad
            -> engines: BrowserRuntime, selector/elector/lazycharge, website
        -> global_pipeline: normalización obligatoria, issues, ensamblado
        -> SearchResult: originales + normalizados + evidencia alineada
    -> search_many: ejecuciones secuenciales, selección entre consultas, provenance
```

El layout conserva `engines/`, `models/`, `scraper/` y el helper `utils/parser.py`
dentro de `src/prospector_engine`. Evita una reorganización masiva del código congelado.
Los imports absolutos usan exclusivamente `prospector_engine.*`; una prueba AST revisa
todos los módulos reales y prohíbe dependencias de CLI, Rich, exportadores y Service.

La selección batch sólo suprime identidades `(source, kind, value)` verificadas en
consultas anteriores. Preserva desconocidos y repeticiones dentro de una consulta.
No mezcla campos ni modifica el resultado individual. No hay matching comercial.
Se conserva el wrapper legacy como detalle interno para regresión; no forma parte
de `__all__` ni sustituye la fachada pública con máximo 100.

Un runtime posee browser y páginas por búsqueda. No hay pool, lock global certificado,
persistencia, HTTP ni tareas distribuidas. La concurrencia permanece NOT VERIFIED;
un consumidor debe serializar inicialmente las invocaciones.

La documentación inicial completa se conserva en [history](history/README-initial.md)
y [Handoff original](history/Handoff-initial.md), incluyendo el cambio local previo.
