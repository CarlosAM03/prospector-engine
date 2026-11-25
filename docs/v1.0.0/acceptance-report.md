# Candidato del Engine v1.0.0 para revisión

Evidencia inicial del 23 de noviembre de 2026 para el candidato de código
`307df17` en `feat/engine-v1-limit-150`. El wheel de Windows se construyó
desde `f7ccdc0`. Los commits de código posteriores sólo cambian el Dockerfile.
La distribución de desarrollo
sigue siendo `0.1.0.dev0` y requiere Python ≥3.11.

## Cambios

- `04078f3` amplía el máximo a 150 por consulta. Conserva default 50 y
  preflight completo. Agrega cobertura para 101 y 150, rechazo de 151,
  respuestas más cortas y batch con tamaños distintos.
- `f7ccdc0` actualiza los pins de build y comprueba los dos puntos de
  entrada con límite 150 desde el wheel instalado.
- `1dde01b` corrige las herramientas heredadas de la imagen y `307df17`
  fija una base actualizada de Python 3.11 por digest.

## Gates

| Gate | Estado | Evidencia |
|---|---|---|
| E-01 Procedencia | PASS | El tag local del CLI resuelve a `bd50cf7`. `scripts/audit_provenance.py` verificó 53 módulos y hashes de origen. El cotejo del manifiesto del candidato permite sólo variación del hash crudo por finales de línea. |
| E-02 API pública | PASS local | Importaciones y pruebas de fachada en Windows. Las firmas y el modelo de resultados conservan la compatibilidad. |
| E-03 Límite | PASS local | Individual 1/50/100/101/150/151, valores inválidos, batch con 150/101/150, preflight de 151 antes de I/O y feed controlado de 35/150/155 candidatos. |
| E-04 Contratos | PASS local | Suites de normalización, originales, identidad, dedup, incidencias y resultados parciales. |
| E-05 Runtime | PASS local | Chromium 149.0.7827.55 en Windows, integración con origen controlado, cleanup, cancelación cooperativa y errores tipados. |
| E-06 Calidad y build | PASS local | `compileall`, Ruff lint y formato, 214 unitarias, 39 de integración, 253 offline y una live excluida. `python -m build` generó sdist y wheel. |
| E-07 Instalación aislada | PASS local | `python scripts/wheel_smoke.py` instaló el wheel con sus dependencias en una venv limpia. El intérprete aislado importó desde `site-packages` y ejecutó single y batch con límite 150 y fuente controlada. |
| Docker local | PASS | Python 3.11.18 en Linux amd64, imagen local `prospector-engine:307df17`, manifest digest `sha256:143a0fba6ec5a8b5e971eb194034329c50306ebc77c660f3fe37190a9b75d300`. Pasaron build, diagnóstico non-root con Chromium y restricciones del workflow, `pip check`, compile, Ruff y 253 pruebas offline en un contenedor efímero. |
| E-08 CI GitHub | NOT_RUN al preparar el push | El workflow queda habilitado para pushes a `feat/engine-v1-limit-150`. Verificar la conclusión y el SHA en [Actions de la rama](https://github.com/CarlosAM03/prospector-engine/actions?query=branch%3Afeat%2Fengine-v1-limit-150). La [corrida anterior de GitHub](https://github.com/CarlosAM03/prospector-engine/actions/runs/39608150150) corresponde al baseline `70f6081`. |
| E-09 Google Maps live | NOT_RUN | La prueba depende de autorización expresa y del perfil de browser aprobado. |
| Navegador productivo | NOT_RUN | Edge sigue siendo el perfil predeterminado. El diagnóstico de Chromium cubre localhost. El perfil de despliegue requiere aceptación y validación propias. |
| E-10 Promoción estable | DEFERRED | La rama feature se prepara para revisión. El merge, el versionado estable y la release quedan pendientes de aprobación. |
| Reportes automatizados del propietario | NOT_RUN / NO_PROVIDED | La revisión se basó en fuentes primarias y en los scanners del candidato. No había reportes del propietario en el checkout. |
| SEC-01 Dependencias Python | Revisado con hallazgo residual | `pip-audit` del candidato reportó un aviso en Soup Sieve. El parser usa búsquedas por etiqueta y atributos. No se encontró la ruta de selectores afectada. Los reportes del propietario figuran como NO_PROVIDED. |
| SEC-02 Browser y SO | Abierto | Docker Scout terminó con 237 asociaciones, 38 de severidad alta y cero críticas. Queda pendiente clasificar las alertas residuales y validar una revisión del browser antes de promover. |

La regresión del baseline pasó 247 pruebas y dejó una live fuera. La validación
local usa Windows 11 x64, Python 3.13.4 y una copia del árbol versionado en una
ruta temporal corta. El checkout original supera el límite de rutas de algunas
herramientas Python. Las salidas locales se guardan en
`artifacts/engine-v1-candidate/` y `artifacts/v1-docker/`.

El 24 de noviembre se repitieron los gates sobre el checkout existente montado
en Linux amd64 con Python 3.11.18. Pasaron `pip check`, `compileall`, Ruff
lint y formato, 253 pruebas offline con una live excluida,
`python -m build --no-isolation` y `python scripts/wheel_smoke.py`.
El smoke importó el wheel instalado en una venv aislada y comprobó 150 en
single y batch. Las versiones de desarrollo se conservan para revisión.

## Solicitud de integración para Service

Propuesta para el futuro adaptador de Service. Usar la [API pública](../public-api.md)
desde un worker fuera del event loop. Pasar el límite individual mediante
`EngineConfig.limit` y ajustar la validación HTTP a 1–150 cuando se apruebe el cambio
en Service. Consumir `SearchResult`, `source_identities`, `observe_execution` y
`cancellation_scope` con los [mapeos propuestos](../integration-readiness.md).
La aceptación del adaptador debe cubrir 150 aceptado, 151 rechazado antes de
admitir la solicitud, resultados parciales, identidad no verificada, cancelación
y traducción segura de errores. La cola, la admisión y el worker pertenecen a Service.
El artefacto candidato reutiliza el nombre de distribución de desarrollo. Para
distinguirlo de builds previos, identificarlo por SHA de código y SHA-256 del wheel.
El wheel Windows de tipo `py3-none-any` tiene SHA-256
`8525dbf941f8f4a6ea74e4d07783bc28d932e5764b8108557a1e89301a60ea04`.
El sdist tiene SHA-256
`4d89699b4613f93ccb8708dfe2b3551cf63f36586081338bc42bcfc256589e36`.

Consultar las [limitaciones](KNOWN_LIMITATIONS.md), la
[matriz de equivalencia](extraction-gap-matrix.md) y el
[registro de seguridad](dependency-hardening.md) antes de promover el candidato.

## Evaluación posterior del runtime protegido

El baseline publicado `030a82d63a499a8abe65352d282ccc9bbc076ff3` pasó ocho
jobs en GitHub. El código candidato de seguridad reside en `9eb5a25`, con
el marcador de compatibilidad del wheel en `436758a`. La regresión local
usó Python 3.11.18, donde el marcador conserva el mismo pin.
Su [CI de rama](https://github.com/CarlosAM03/prospector-engine/actions?query=branch%3Afeat%2Fengine-v1-limit-150)
se debe verificar por el SHA exacto de la publicación.

El perfil y el procedimiento reproducible constan en el
[suplemento para Service](service-runtime-supplement.md). La aceptación del
host productivo, la política de egress y la prueba de Google Maps mediante el
[protocolo live](live-acceptance.md) siguen pendientes del propietario.

| Gate de esta revisión | Resultado | Evidencia |
|---|---|---|
| Contrato y regresión Linux | PASS | 256 offline, una live excluida. Incluye fixtures de navegación y extracción, batch y dedup, normalización, incidencias, observabilidad y cancelación con cleanup. |
| Calidad y paquete | PASS | Ruff lint y formato, compileall, pip check, wheel y sdist. Instalación en venv aislada y ambos puntos de entrada con 150. |
| Docker y localhost | PASS | Build Linux amd64 con Python 3.11.18. Smoke non-root sin red y HTTP localhost con el perfil protegido derivado. |
| Chromium con seccomp Docker por defecto | FAIL | Chromium detuvo el arranque con «No usable sandbox». Se propagó error tipado. |
| Chromium con perfil upstream | FAIL | El zygote falló al llamar `chroot`. Se propagó error tipado. |
| Chromium con variante de seccomp | PASS local | Se permitió sólo `chroot` además del perfil upstream. La prueba comprobó UID 10001, filtro seccomp, capacidades efectivas vacías, no-new-privileges, raíz de solo lectura, tmpfs, loopback, ausencia de `--no-sandbox` y cleanup de los procesos del navegador y temporales. |
| Docker Scout después del cambio | FAIL operativo | Sin espacio en el directorio temporal para indexar la imagen. La comparación de inventario y PyPI tiene cobertura parcial. |
| Host productivo, egress y Google Maps live | NOT_RUN | Requieren aceptación del propietario. Los reportes automatizados continúan NO_PROVIDED. |

La suite offline completa usó el perfil de compatibilidad. El diagnóstico
específico validó el perfil protegido y el HTTP localhost. Queda pendiente
ejecutar los fixtures protegidos en el host de destino y aprobar la regla
seccomp, el aislamiento de red y los avisos residuales.
