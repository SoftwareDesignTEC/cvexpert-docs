# Colección global Postman CVExpert

La colección central incluye **45 operaciones** de los OpenAPI originales. Cada solicitud tiene al menos una aserción de estado HTTP de éxito documentado; `GET /jobs` y `GET /cvs` también validan paginación. **No equivale a ejecución real.**

## Importar y configurar

1. Importar `cvexpert.postman_collection.json` y `apim.postman_environment.json`.
2. Configurar `apiBaseUrl` con la base **efectiva** del gateway; el valor de ejemplo se observó en Android, no garantiza que las 45 rutas estén disponibles.
3. Definir `googleIdToken` en el *Current value* local (o el mecanismo local de secretos de Postman); no compartir ni exportar el entorno con tokens.
4. Configurar IDs reales de prueba: `profileId`, `cvId`, `jobId`, `applicationId`, `notificationId`, `deviceToken`, `notificationType`, etc. Para `profileId` consultar el contrato del servicio; no asumir que es correo.
5. **Antes de habilitar `allowWrites=true`**, sustituir cada `{}` de ejemplo por un cuerpo válido conforme al OpenAPI de su servicio. Se puede ejecutar `python scripts/generar_postman_desde_openapi.py` para generar ejemplos a partir de `requestBody`. Las rutas admin requieren también `allowAdmin=true` y un token con rol.
6. Los endpoints `/health` son pruebas **directas de backend** solo si existen permisos/entorno; habilitar manualmente `allowDirectHealth=true` y configurar la URL local exacta.
7. Ejecutar GET primero. Usar un ambiente de pruebas aislado para mutaciones.

## Restricciones conocidas

- **No todas las rutas del OpenAPI son necesariamente públicas** en APIM. El gateway podría transformar paths o excluir `/health`.
- Los JSON `{}` de operaciones con body son **placeholders para no inventar DTO**. Hay que completarlos antes de marcar pruebas como ejecutadas.
- La comprobación de respuesta `200/201/204` no reemplaza pruebas de esquema o permisos: añadirlas tras integrar datos reales.
- Un `409` de `/skills-gap` por ausencia de snapshot es un escenario negativo significativo, no un éxito.
- Los scripts Postman de origen se pueden descargar a `postman/originales` usando `sincronizar_contratos.py` para evaluar casos positivos y negativos ya preparados.

## Ejecución desde línea de comandos (opcional)

Una vez instalado Newman y configurado el entorno local, ejecutar desde el repositorio:

```bash
newman run postman/cvexpert.postman_collection.json -e postman/mi_entorno_privado.postman_environment.json -r cli,json --reporter-json-export evidencias/newman-resultado.json
```

No subir `mi_entorno_privado.postman_environment.json` a Git. Redactar los reportes antes de publicarlos.
