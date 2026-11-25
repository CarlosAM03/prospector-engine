# Equivalencia y plan del Engine v1.0.0

Auditoría del 23 de noviembre de 2026 sobre `70f6081688db5c5bc5ea612f5fabd5724aab0b20`.
`main` coincidía con `origin/main` local y con el último commit devuelto por GitHub.
El índice y los archivos seguidos estaban limpios. El harness local estaba sin seguimiento.
La distribución declara `0.1.0.dev0`. El 24 de noviembre se confirmó por Git
que `main` remoto y el ancestro común de la rama candidata siguen en ese baseline.

El tag local anotado del CLI apunta a `bd50cf7cbba76ccd75517d06037662dff4797b05`.
El cotejo se ejecutó en una copia de `git archive HEAD` para evitar los límites de rutas del host.
`scripts/audit_provenance.py` verificó el tag, los hashes de origen y los 53 módulos extraídos.
El árbol congelado contiene 66 archivos bajo `src`. El manifiesto registra 43 módulos
equivalentes por AST después de adaptar imports, 3 refactors inventariados, 7 extensiones
del Engine y 13 exclusiones. El inventario por archivo enlaza las suites correspondientes.

| Capacidad del CLI congelado | Engine y evidencia | Estado del candidato y riesgo |
|---|---|---|
| Maps, navegación, Elector, LazyCharge, feed virtual, resumen y detalle | `engines/navigation`, `engines/selector`, `scraper/google_maps`. Tests de pipeline, feed virtual, navegación y detalle | Implementado. Cambios externos en el DOM pueden afectar la extracción. |
| Enriquecimiento de sitios | `engines/website`, `website_enrichment.py`. Tests de componentes y de sitios controlados | Implementado. Se mantienen límites en contact/about/content type. |
| Normalización obligatoria y recuperación por campo (ADR-008) | `engines/normalization`, `global_pipeline.py`. Regresión de reglas, originales y orden | Implementado. El resultado añade un sidecar de identidad alineado. |
| Identidad P92, preflight, batch secuencial y dedup interconsulta (ADR-009) | `source_identity.py`, `engines/batch`, `search_many()`. Tests de identidad, orden, fallos y duplicados | Implementado. Se conservan observaciones no verificadas y el resultado individual íntegro. |
| Runtime, presentación del progreso y cancelación (ADR-010) | `BrowserRuntime`, observador Python y token cooperativo. Tests de lifecycle, cancelación y errores tipados | Edge sigue siendo el default. Chromium administrado admite sandbox explícito de proceso y error tipado si el host rechaza el arranque. |
| Límite por consulta | `EngineConfig.limit` para single, `BatchQuery.limit` para batch, máximo común en `engines/config.py` | Ampliado de 100 a 150. Default 50. Preflight de 151 antes de I/O y validación offline de feeds con menos de 150 resultados. |
| Rich, señales de terminal, exportadores y portable | Frontera de biblioteca en el manifiesto de extracción | Exclusiones deliberadas. Los consumidores son responsables de la presentación y exportación. |
| Empaquetado | `pyproject.toml`, workflow CI, Dockerfile y smoke de wheel | Validado localmente con wheel instalado y Docker. El CI del candidato se consulta por el SHA publicado. |

## Plan de commits

1. Registrar el cotejo y ampliar el máximo a 150 en la política compartida. Cubrir single,
   preflight batch, resultados inferiores al máximo y normalización alineada.
2. Ajustar los pins de build con advisories verificados y compatibilidad comprobada.
3. Registrar los gates, las limitaciones y la entrega al consumidor.

El perfil de browser productivo y la prueba live mínima requieren decisión del propietario.
La UX HTTP de cinco jobs y los criterios de certificación comercial siguen pendientes.
La concurrencia simultánea se difiere. Los reportes automatizados del propietario no se
encontraron en el checkout.
