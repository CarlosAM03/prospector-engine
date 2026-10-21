# Handoff — Primera extracción física de Prospector Engine

Fecha: 2026-10-21 (America/Tijuana). Versión: `0.1.0.dev0`, desarrollo.

## Estado implementado

Paquete instalable independiente en `src/prospector_engine`, 53 módulos extraídos
desde CLI v1.0.0, commit `bd50cf7cbba76ccd75517d06037662dff4797b05`.
Tag local/remoto verificado, sin checkout ni cambios en CLI. `main` de CLI
`63e018d0d7ce574f24f3233beadcccd63af5a876` tiene source equivalente al tag;
la copia se hizo leyendo el commit congelado, no confiando en el working tree.

Conserva búsqueda single/batch 1–5, límite default 50/máximo 100, navegación,
selectors/elector/lazycharge, extracción, detalle, website, normalización obligatoria,
originales/normalizados 1:1, issues, errores tipados, parcialidad, identidad P92,
selección estricta entre consultas y provenance. No contiene CLI, exports ni HTTP.

Extensiones aditivas: identidad pública alineada, eventos/Protocol observador,
CancellationToken con checkpoints cooperativos y outcome explícito, browser_channel
configurable manteniendo Edge default, diagnóstico localhost e imagen Linux no root.
Se documentan las limitaciones de cancelación, mutabilidad del modelo y browser.

## Verificación

Windows Python 3.13.4 y Linux Python 3.11.14: regresión de 209 unitarias y 38 de
integración; full offline 247 pruebas, 1 live excluida. Compile, lint, formato,
build, aislamiento wheel y Docker se registran en
[validation-results.json](docs/validation-results.json); consultar ese archivo para
el estado final de cada gate, sin confundir intentos fallidos previos con PASS.
Google Maps live no se ejecutó. Localhost acredita disponibilidad/cierre, no aceptación
productiva headless o equivalencia Maps Edge/Chromium. Concurrencia no certificada.

## Git y aislamiento

Rama `feat/extract-cli-v1-engine`, historial inicial `4072172` -> `1092087` preservado.
No había remote. Existía un cambio previo del propietario en Handoff; su contenido
exacto se preserva en [history/Handoff-initial.md](docs/history/Handoff-initial.md).
El README inicial completo también se preserva. Se dejó `master` intacta.
No se hizo push, merge, tag estable ni modificación de otro proyecto.

CI CONFIGURED: quality/integration/package/docker-build. REMOTE CI NOT VERIFIED;
MAIN PROTECTION NOT VERIFIED. Falta URL Engine inequívoca y ejecución remota; la
[guía GitHub](docs/github.md) permite completar publicación y ruleset sin force.

## Consumidor siguiente

Service debe depender de la API pública Python, ejecutarla fuera del event loop
y mantener su propio auth/jobs/tenant/callback/lifecycle. El mapping de identidad
ahora está disponible; UNVERIFIED se conserva como null. No se cambió Backend/Service.
Ratificar drifts HTTP de máximo 100/texto no vacío, progreso/issues y cancelación HTTP.
Elegir browser productivo después de aceptación live acotada.

## Referencias

- [README actual](README.md), [arquitectura y autoridades](docs/architecture.md).
- [Inventario de extracción](docs/extraction-inventory.md), [clasificación de tests](docs/test-migration.json).
- [API pública](docs/public-api.md), [runtime](docs/runtime.md), [testing](docs/testing.md).
- [Preparación para Service](docs/integration-readiness.md), [decisiones](docs/decisions-pending.md).
- [Handoff histórico completo](docs/history/Handoff-initial.md), [README histórico](docs/history/README-initial.md).

Release independiente estable y merge a main permanecen reservados al propietario.
