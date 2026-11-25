# Suplemento de integración para Service

Baseline `030a82d63a499a8abe65352d282ccc9bbc076ff3`. El código y los pins
del runtime candidato están en `9eb5a25bc1fc25cd7354785be9a81780d38e7cba`,
con el marcador de compatibilidad del wheel en `436758a`.
Para revisión conjunta con los informes, verificar los checks del HEAD de la
[rama autorizada](https://github.com/CarlosAM03/prospector-engine/tree/feat/engine-v1-limit-150).
El Engine sigue en `0.1.0.dev0`.

- Playwright 1.61.0 → 1.65.2, Chromium 149.0.7827.55 → 159.0.8154.6 y
  driver Node.js 24.17.0 → 26.13.1 según el upstream. Reinstalar el navegador
  que corresponda a la versión de Playwright. La imagen instala libatomic1
  para el driver. Soup Sieve 3.0.3 → 4.1.3 queda fijado en el wheel y constraints.
  Playwright 1.65.2 sólo declara greenlet en su metadata Python. Se retira
  el pin obsoleto de pyee.
- El pin corregido de Soup Sieve se aplica desde Python 3.11.5 para preservar
  la instalación del wheel en Python 3.11.0–3.11.4. En esos parches antiguos,
  BeautifulSoup puede resolver una versión de Soup Sieve anterior a la corrección.
  El perfil Docker candidato usa Python 3.11.18 y el pin corregido.
- Edge instalado sigue siendo el perfil predeterminado de la biblioteca.
  El perfil Linux candidato usa `EngineConfig(headless=True, browser_channel=None)`
  con `PROSPECTOR_CHROMIUM_SANDBOX=1` en el proceso del worker. El Engine
  solicita el sandbox a Playwright y devuelve `ProspectorRuntimeError` si
  falla el arranque, después de intentar cerrar el driver.
- Perfil de contenedor a validar en el host de destino. Usar UID/GID 10001,
  init, filesystem raíz de solo lectura, tmpfs privado para `/tmp` y
  almacenamiento efímero para la caché del usuario si el navegador lo requiere.
  Mantener `cap-drop=ALL`, `no-new-privileges`, límites de memoria/PID y
  `/dev/shm` de 1 GiB. Para fixtures usar `--network none`. Para live, aplicar
  la política de egress aprobada, con bloqueo de redes internas y metadatos.
- Probar primero seccomp por defecto. Si bloquea namespaces, evaluar
  el perfil upstream de Playwright obtenido del blob Git
  [fddc05fb520affb145404e6f6f647ca96af8087d](https://api.github.com/repos/microsoft/playwright/git/blobs/fddc05fb520affb145404e6f6f647ca96af8087d).
  Su SHA-256 es
  `cc3e61cabda6bbc1e53e54d27ba4d55a9d3be829b6dd1a596f4a7b31b1cc7849`.
  Las reglas de
  namespaces y el perfil de egress requieren aprobación del propietario.

El diagnóstico protegido se ejecuta contra una imagen construida desde la
rama, con `scripts/check_runtime_isolation.py` montado de solo lectura.
En Docker Desktop Linux amd64 el perfil por defecto falló con «No usable
sandbox». El perfil upstream permitió avanzar y el zygote falló en
`chroot`. La variante local que añade sólo la llamada `chroot` pasó
manteniendo el filtro seccomp y la comprobación de capacidades del kernel.
Usar esa variante únicamente después de aprobación en el host de destino.

Para reproducir la variante, añadir una entrada a `syscalls` en el perfil
upstream verificado y conservar todas sus demás reglas. Esta excepción de
seccomp no añade `CAP_SYS_CHROOT` al proceso del contenedor.

```json
{"names":["chroot"],"action":"SCMP_ACT_ALLOW","args":[],"includes":{},"excludes":{}}
```

```bash
docker run --rm --init --network none --read-only --shm-size=1g \
  --tmpfs /tmp:rw,nosuid,nodev,size=512m --memory 2g --pids-limit 256 \
  --cap-drop=ALL --security-opt no-new-privileges \
  --security-opt "seccomp=$PWD/playwright-seccomp-chroot.json" \
  -e HOME=/tmp -e TMPDIR=/tmp -e PROSPECTOR_CHROMIUM_SANDBOX=1 \
  --mount "type=bind,source=$PWD/scripts/check_runtime_isolation.py,target=/probe.py,readonly" \
  prospector-engine:security-review python /probe.py
```

Se preservan el contrato Python, 150 por consulta, batch de 1–5 en orden,
deduplicación, identidad, normalización, observabilidad y cancelación.
Service conserva la admisión, la cola, el worker y los plazos de ejecución.
[Protocolo live](live-acceptance.md) · [Informe de aceptación](acceptance-report.md)
