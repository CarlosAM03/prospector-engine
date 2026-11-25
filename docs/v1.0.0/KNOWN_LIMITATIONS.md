# Limitaciones conocidas del candidato Engine

- El máximo de 150 es una entrada por consulta. El feed de Google Maps puede
  terminar antes o devolver un resultado parcial con incidencias recuperables.
- Los indicadores de páginas contact/about y el content type conservan las
  limitaciones del código congelado. La disponibilidad de sitios externos varía.
- Batch ejecuta de una a cinco consultas en orden. La supresión por identidad
  afecta la selección entre consultas, conserva las listas originales y mantiene
  las observaciones `UNVERIFIED`. Los históricos pertenecen al consumidor.
- La cancelación es cooperativa y se observa en checkpoints. Una operación
  bloqueante de Playwright debe devolver el control antes de que el Engine pueda
  observar la señal. La cancelación no devuelve un prefijo parcial.
- Edge visible es el perfil predeterminado. Chromium administrado por Playwright
  se selecciona con `browser_channel=None`. La validación controlada no mide
  fiabilidad live, equivalencia entre browsers, uso bajo concurrencia o un SLA.
- El contenedor ejecuta como UID 10001. El perfil Linux de Service debe solicitar
  explícitamente el sandbox con `PROSPECTOR_CHROMIUM_SANDBOX=1` y validar
  namespaces, seccomp y egress en el host productivo. El perfil predeterminado
  de la biblioteca sigue siendo Edge instalado.

La distribución sigue en desarrollo como `0.1.0.dev0`. El perfil productivo,
la prueba live acotada y la promoción a v1.0.0 requieren revisión del propietario.
El runtime controlado está probado en localhost. El navegador productivo y
Google Maps live se registran como NOT_RUN. Los reportes automatizados del
propietario están NO_PROVIDED. El
[registro de hardening](dependency-hardening.md) recoge los riesgos pendientes
del navegador, el driver y las bibliotecas del sistema.
