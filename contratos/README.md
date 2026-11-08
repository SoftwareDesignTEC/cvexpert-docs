# Contratos canónicos

Las cinco especificaciones de origen están documentadas en [`fuentes.json`](fuentes.json), con su **blob SHA de Git**. Para copiar exactamente los OpenAPI completos y el esquema de evento (sin reconstruirlos ni inventar DTO), ejecutar desde la raíz:

```bash
python scripts/sincronizar_contratos.py
```

El script descarga y valida el blob antes de escribir `*.openapi.yaml` y `evento-notificacion.schema.json`. Si el original cambia, fallará y pedirá revisar el nuevo contrato antes de actualizar el manifiesto. Esto previene publicar documentación central desfasada silenciosamente.

La matriz describe 45 operaciones de los contratos consultados. Los archivos OpenAPI completos **no están presentes hasta realizar la sincronización en un equipo con acceso a GitHub**.
