# Evidencias de validación

Corte actual: 16 de noviembre de 2026. [Estado de entrega](../docs/estado-entrega.md) · [Plan E2E](../docs/plan-pruebas.md) · [Auditoría](../docs/auditoria.md).

- [Validación documental actual](validacion-2026-11-16.md): comandos, resultados y límites de esta actualización.
- [Registro E2E editable](registro-e2e.csv): 28 casos con preparación, pasos y esperado. No ejecutados salvo el bloqueo explícito de emisión course.recommended; no contiene aprobaciones inventadas.
- [Histórico del corte anterior](historico-corte-anterior.md): cifras locales y observaciones conservadas con su alcance original; no se atribuyen a los commits actuales.
- [Revisiones y metadatos GitHub](../contratos/revisiones-auditoria.json): ocho main, develop, PR abiertos y jobs consultados. Los jobs de despliegue son evidencia de esa ejecución del pipeline, no del SHA actualmente activo ni del éxito E2E.

Para registrar una corrida, conservar ID de caso, fecha/hora/zona, preparación aplicada, pasos ejecutados, esperado/real, estado (aprobado, fallido, bloqueado o no ejecutado), entorno, revisión backend/APIM/clientes y enlace a evidencia saneada. Una omisión de Newman equivale a no ejecución.

Los reportes completos se conservan en almacenamiento privado. Compartir solo resúmenes depurados del [runner](../postman/README.md). Eliminar tokens de autorización/dispositivo, correos, datos personales, CV completos, identificadores de cuentas, claves, certificados privados y cadenas de conexión. Usar alias de fixtures y no publicar volcados completos de Logcat, Postman o Azure.
