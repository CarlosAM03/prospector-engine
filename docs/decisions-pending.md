# Decisiones del propietario y dependencias externas

| ID | Hallazgo / contrato | Alternativas y riesgo | Recomendación y decisión requerida | Trabajo independiente |
|---|---|---|---|---|
| OWN-01 | Browser productivo servidor; CLI certificó Windows Edge visible | Edge Linux/headless frente a Chromium; localhost no prueba equivalencia Maps | Elegir política tras aceptación live acotada; mantener Edge default entretanto | Paquete, tests, Chromium configurable y Docker |
| OWN-02 | Platform/Service aceptan límites >100 y strings vacíos | Rechazar en consumidor o ampliar contratos; no cambiar silenciosamente Engine | Ratificar máximo 100 y texto no vacío en contratos de los repos correspondientes | Engine conserva baseline y documenta frontera |
| OWN-03 | Progreso global e incidencias sin mapping completo en callback | progress null / política por etapas; issues logs / extensión callback | Definir en Service; usar null sin porcentaje inventado | Eventos y SearchIssue públicos disponibles |
| OWN-04 | Cancelación HTTP no está definida en contrato interno | Endpoint futuro o diferir; riesgo de prometer cancelación instantánea | Ratificar protocolo y traducción del token/outcome Python | Primitiva cooperativa probada, sin HTTP |
| OWN-05 | Engine carece de remote verificado | URL del Engine y acceso de publicación/admin necesarios; no usar remote CLI | Proporcionar repo inequívoco, publicar rama, ejecutar CI y proteger main antes de merge | Todo trabajo local, workflow y guía de ruleset |

No se pide autorización para packaging, organización interna, gates ni tests ya
autorizados. Release estable y merge a main requieren aceptación del propietario.
La concurrencia queda DEFERRED; no se propone ampliar el alcance de esta extracción.

Estados externos: REMOTE CI NOT VERIFIED; MAIN PROTECTION NOT VERIFIED. Una búsqueda
del propietario `CarlosAM03` encontró el repositorio CLI, sin identificar uno Engine.
No se inventó URL, no se añadió remote, no se creó repositorio ni se hizo push.
