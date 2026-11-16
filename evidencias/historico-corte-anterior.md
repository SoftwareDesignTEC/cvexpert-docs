# Resultados del corte anterior — conservación histórica

Transcripción del bloque de ejecuciones del estado documental base `61039b25ec18681ed8ff5ddfca326806e62c5c88`. Es evidencia reportada en el corte anterior del 8 de noviembre de 2026; el texto no identifica el SHA de cada backend ejecutado ni conserva aquí reportes crudos. No se ha repetido para los commits del 16 de noviembre.

La tabla conserva cifras originales, incluidas 75 omisiones; main después del PR #4 ya contenía 76 solicitudes. No usar estas cifras como validación de la colección actual. Los resultados se limitan a cada entorno descrito y no aprueban E2E actuales.

## Ejecuciones

| Comprobación | Resultado observado |
| --- | --- |
| Sincronización desde los clones de `main` fijados | Los cinco OpenAPI, las tres colecciones originales y el JSON Schema coinciden con sus blobs de origen. La guía incorpora los enlaces centrales. |
| Validación documental y JavaScript | Contratos, referencias, operaciones, cuerpos positivos, correspondencia con Postman, eventos, enlaces y patrones de secretos comprobados. Se mantiene la excepción de Usuarios documentada en la [auditoría](../docs/auditoria.md). |
| Newman, entorno de ejemplo | 75 omitidas, 0 solicitudes HTTP, 0 aserciones. |
| Newman, Brecha en loopback | `GET /health` → `200`. `GET /skills-gap` sin certificado → `403 APIM_CERTIFICATE_REQUIRED`. 2 solicitudes, 7 aserciones, 0 fallos. |
| Newman, API principal de APIM | `GET /api/v1/cvs` devolvió `401` sin token y con un valor inválido. 2 solicitudes, 2 aserciones, 0 fallos. |
| Usuarios, `mvn test` | 15 aprobadas, 0 fallos y 0 omitidas. |
| Newman, ciclo local de CVs | `200 → 201 → 200 → 200 → 200 → 204 → 404`. 7 solicitudes, 30 aserciones y 0 fallos. Se usaron los routers de CVs y los dobles de base de datos y publicador de sus pruebas. |
| CVs, `python -m pytest -q` | 38 aprobadas, con una advertencia de compatibilidad de TestClient. |
| Brecha, `npm test` | 53 aprobadas, 0 fallos y 0 omitidas. |
| Notificaciones, `dotnet test Notificaciones.sln` | 190 aprobadas, 0 fallos y 0 omitidas con .NET 8. Incluye registro de dispositivos, FCM con dobles, plantillas, consumo de eventos y negociación. |
| Ofertas y postulaciones, Maven | 74 aprobadas en la selección sin Docker. La corrida amplia registró 17 errores en `PersistenceAdaptersTest` y `SwaggerUiTest` por Testcontainers sin motor Docker. |
| Azure, plano de administración | Inventario de operaciones, destinos, políticas de identidad y metadatos de certificado cliente de los App Services visibles. Consulte [seguridad](../docs/seguridad-apim.md). |

En una sesión anterior, Android registró `200` en `GET /api/v1/cvs` y `GET /api/v1/jobs`, y `409 SKILLS_INPUT_REQUIRED` en `GET /api/v1/skills-gap`. El antecedente carece de traza que identifique la revisión desplegada.


## Comunicación histórica del equipo

El 8 de noviembre se informó disponibilidad de Android 0.7.2 en Firebase y bloqueo temporal de CVs/PDF/IA por plantillas pendientes y HTTP 500 de IA. Las lecturas de Android debug no se atribuyeron a esa APK. La clasificación antigua de todo FCM Android como futuro quedó superada por el código main revisado el 16 de noviembre. Ver [estado actual](../docs/estado-entrega.md).
