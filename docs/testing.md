# Pruebas y evidencia

Fecha: 2026-10-21, America/Tijuana. Logs locales `artifacts/`, ignorados por Git.

```sh
python -m compileall -q src
python -m ruff check .
python -m ruff format --check .
python -m pytest tests/unit -q
python -m pytest tests/integration -q
python -m pytest -q -m "not e2e"
python -m build
python scripts/wheel_smoke.py
```

Windows Python 3.13.4: **209 unit PASS**, **38 integration PASS**, **247 offline PASS,
1 live deselected**. Browser Chromium 1228 en `.cache/browsers`; temporales dentro
del Engine. Son conteos reales del Engine, no los 298 de CLI. El
[inventario](test-migration.json) clasifica cada archivo y las funciones excluidas.

Cobertura portada: configuración, modelos, normalización, single/batch, fallos
tipados/prefijos recuperables, parcialidad, identidad P92, deduplicación, provenance,
navegación, feed virtual, detalle, selector/elector/lazycharge, website, timing,
observabilidad y cleanup. Nuevas pruebas: API pública, dirección de dependencias AST,
identidad pública alineada single/batch, configuración de browser, scopes, token
precancelado y cancelación con cleanup, disponibilidad browser real en localhost.

Ruff lint cubre todo el código. El formato del código/test portado se excluye
explícitamente para comparar con el frozen; módulos/scripts/tests nuevos pasan
format check. Se eliminaron imports sin uso, sin reformateo masivo. Auditoría de
provenance valida hashes de 53 módulos y equivalencia AST después de imports,
salvo las extensiones y refactors enumerados en el manifiesto.

Windows produjo wheel/sdist por separado. El smoke instala un wheel en venv nueva,
quita PYTHONPATH y ejecuta `python -I` desde otro directorio, verificando import
desde site-packages. No usa src ni CLI. Los intentos iniciales fallidos por rutas
largas no se consideran PASS; ver [runtime](runtime.md).

## Linux

`scripts/container_gates.py` ejecuta la suite usando el paquete instalado en la
imagen, UID 10001, cap-drop ALL y no-new-privileges, montando sólo Engine `/work`.
Instala dev tools en home efímero y comprueba compile/lint/format/unit/integration/
offline/build/wheel-isolation. Logs `*-linux.txt`; resultados finales en
[validation-results.json](validation-results.json).

Docker smoke verifica HTTP localhost, status/título y cierre página/browser/driver;
el smoke import también se ejecuta sin red. No se confunde localhost con Maps live.
Los tests con browser real están identificados por nombre; los demás usan dobles
controlados, sin red externa.

## Live y CI

LIVE_E2E NOT EXECUTED en esta extracción. Opt-in:

```sh
PROSPECTOR_RUN_E2E=1 python -m pytest -m e2e -q
```

La prueba live nunca es required check habitual. La evidencia histórica CLI
229/69/298 y owner live PASS es procedencia, no evidencia de este paquete.
REMOTE CI NOT VERIFIED; MAIN PROTECTION NOT VERIFIED por falta de remote Engine.
Véase [github.md](github.md).
