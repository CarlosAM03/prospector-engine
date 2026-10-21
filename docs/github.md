# GitHub Actions y protección de main

CI CONFIGURED. REMOTE CI NOT VERIFIED; MAIN PROTECTION NOT VERIFIED. Sin remote
Engine inequívoco, sin push/PR/ruleset. La conexión permitió verificar CLI, pero la
búsqueda por propietario no identificó un repo Engine. No se inventó una URL.

Triggers: push main/feat-extract, pull_request main, workflow_dispatch. Permiso
contents read. Jobs: quality, integration, package, docker-build. Python 3.11/3.13;
integración Ubuntu/Windows, browser localhost, wheel/sdist e import aislado, Docker.

Checks previstos por la configuración; confirmar nombres en el primer run remoto:

```text
quality (3.11)
quality (3.13)
integration (ubuntu-latest, 3.11)
integration (ubuntu-latest, 3.13)
integration (windows-latest, 3.11)
integration (windows-latest, 3.13)
package
docker-build
```

Para terminar con el remote verificado:

1. Verificar identidad/permisos; agregar origin sólo al Engine, sin usar URL CLI.
2. Preservar los dos commits iniciales; no rebase ni force push.
3. Preparar main desde el baseline histórico tras preservar el Handoff local previo.
   Se dejó master intacta por ese cambio preexistente.
4. Publicar main inicial y rama feature según estado real del remoto, sin force.
5. Crear PR feature -> main, esperar CI real y verificar todos los checks.
6. Ruleset refs/heads/main: PR requerido, checks anteriores requeridos, bloqueo de
   non-fast-forward/force push y deletion, sin bypass amplio. Confirmar disponibilidad
   de plan/permisos. No exigir checks que aún no se hayan producido.
7. Dejar PR para revisión. Merge sólo autorizado por el propietario.

La administración de rulesets no está disponible en las herramientas conectadas.
Un YAML creado no constituye CI EXECUTED/GREEN ni protección aplicada.
