# Protocolo propuesto de aceptación live

Estado **NOT_RUN**. Requiere aprobación expresa del propietario para este
protocolo y para el perfil Linux sandboxed del suplemento de integración.
El operador confirma las condiciones de uso de la fuente antes de habilitar egress.

1. Fijar el SHA publicado y el digest de imagen. Registrar fecha, versión de
   Chromium y Node, perfil seccomp y hash, UID, memoria y PID máximos.
   Ejecutar primero el diagnóstico protegido sin red.
2. Habilitar egress únicamente bajo la política aprobada. Usar
   `EngineConfig(headless=True, browser_channel=None, website_enrichment=False)`
   y `PROSPECTOR_CHROMIUM_SANDBOX=1`. Excluir la inspección de sitios externos
   de esta prueba para reducir el tráfico y aislar el comportamiento de Maps.
3. Ejecutar secuencialmente una búsqueda «cafeterías», «Tijuana», máximo 3.
   Si pasa, ejecutar un batch de dos entradas con «cafeterías» y «panaderías»
   en «Tijuana», máximos individuales de 5. Si el propietario aprueba una
   etapa adicional, ejecutar una única búsqueda «cafeterías», «Tijuana», con
   máximo solicitado 150. Sin concurrencia, reintentos automáticos ni
   repetición para llenar resultados.
4. Usar presupuestos de 2 minutos para el smoke, 4 para el batch y 15 para la
   etapa de 150. Al agotarse un presupuesto se solicita cancelación. Si la
   ejecución mantiene recursos 30 segundos después, finalizar el contenedor
   desde el supervisor y registrar **FAIL** del cleanup operativo. La llamada
   Python es síncrona y la cancelación cooperativa puede esperar un checkpoint.
5. Aceptar un conteo inferior al máximo si el resultado y las incidencias lo
   justifican. Exigir correspondencia 1:1 de originales, normalizados e
   identidad, orden, límites, progreso válido y cierre de procesos y temporales.
   Si aparece un duplicado con identidad verificada en el batch, comprobar
   la referencia a la primera consulta. Si no aparece ninguno, registrar esa
   comprobación live como no observada y conservar la evidencia offline.
6. Interrumpir ante CAPTCHA, bloqueo de fuente, fallo de sandbox, fuga de
   recursos o respuesta inesperada. Registrar únicamente métricas, conteos,
   códigos de incidencias y motivos de parada. Evitar persistir datos de
   negocios, cookies, HTML o credenciales.
