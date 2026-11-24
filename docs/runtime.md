# Runtime y contenedor

Baseline conservado: Windows, Microsoft Edge Stable, `channel="msedge"`, Visible
por defecto. Background fue menos fiable en la validación CLI. Chromium requiere
opt-in: `EngineConfig(browser_channel=None, headless=True)`; para diagnóstico,
`BrowserRuntime(channel=None, headless=True)`. No hay fallback automático.

El runtime posee browser/páginas/driver por búsqueda. Cleanup intenta cerrar todo
incluso con excepción/cancelación; preserva la causa original y marca fallo de
cleanup. El override Windows de spawn permanece acotado al arranque síncrono;
no implica concurrencia certificada ni API pública de señales.

## Imagen y ejecución

Base `python:3.11.18-slim-bookworm`, digest
`sha256:a83ba18aef0f865b1a4a611c2cf460fe446f2795673bbb9fe43be570439e3b39`.
Playwright 1.61.0 fija Chromium 1228 (149.0.7827.55). Python y transitivas se fijan
por constraints. Los paquetes Debian se obtienen de apt y pueden recibir cambios;
no se promete reconstrucción byte por byte sin snapshot Debian. Conservar el digest
final de imagen para despliegue inmutable.

Dos etapas: build del wheel real y runtime sin toolchain de desarrollo. UID/GID
10001, sin credenciales, `.env`, rutas personales ni repositorios externos.
Browser `/opt/playwright`. No se exponen puertos. El servidor de diagnóstico sirve
sólo localhost y se cierra al terminar.

```sh
docker build -t prospector-engine:dev .
docker run --rm --init --shm-size=1g --cap-drop=ALL --security-opt=no-new-privileges prospector-engine:dev
docker run --rm --network=none --init prospector-engine:dev python -m prospector_engine.diagnostics
```

`--init` recolecta hijos; shm evita la memoria compartida mínima del default Docker.
No requiere privileged, root, host network ni acceso al daemon desde la imagen.
El consumidor debe medir CPU/memoria para sus consultas, no hay sizing universal.
`--rm` elimina sólo el filesystem efímero de esa ejecución.

Se conserva la política de launch del baseline; no se habilita explícitamente el
sandbox Chromium. Usuario no root/cap-drop no sustituyen evaluación de aislamiento
productivo. La [documentación oficial Playwright](https://playwright.dev/python/docs/docker)
recomienda usuario separado/perfil seccomp para navegación no confiable. No se
introdujeron stealth, CAPTCHA bypass ni evasión.

## Evidencia

[testing.md](testing.md) y [validation-results.json](validation-results.json)
registran cada gate. Smokes localhost prueban disponibilidad/navegación/cierre,
no Google Maps público, confiabilidad headless, capacidad universal 100 o concurrencia.
Aceptación productiva Linux/headless permanece NOT VERIFIED; live E2E no ejecutado.

## Rutas largas de este host

El workspace supera MAX_PATH y el host no tiene soporte general habilitado. Se
utilizó `subst P: <raíz Engine>` exclusivamente para este repositorio, con venv,
cachés browser/pip, temporales y evidencias dentro de él. No se cambió el registro.
ensurepip se invocó por la ruta P: del intérprete. El backend editable generó una
ruta física larga en su .pth local; se añadió el prefijo Windows de ruta extendida
en ese archivo del entorno. No es una modificación del paquete distribuido.

Windows construyó wheel/sdist en invocaciones separadas por un fallo de tarfile
al mezclar separadores en temporales extendidos. El gate estándar `python -m build`
se comprueba también en Linux. El wheel instalado en otra venv no usa .pth ni
sys.path manual. Tras revisión, `subst P: /D` elimina sólo el alias; el entorno
editable local depende de él hasta recrearse en una ruta apta.
