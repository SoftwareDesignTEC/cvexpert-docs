# Estado de entrega · Fase II

## Artefactos verificados

- Cinco contratos OpenAPI fijados por commit y SHA Git blob. El [manifiesto](../contratos/fuentes.json) registra además las tres colecciones originales, el esquema de eventos, la guía de Notificaciones y los clientes revisados.
- 45 operaciones REST en la [matriz](matriz-trazabilidad.md). ARM registra 40 en `cv-api`. Las cinco restantes son dos sondas directas y tres operaciones de plantillas de Notificaciones. El registro en el gateway acredita configuración de rutas.
- La [colección](../postman/README.md) incluye 75 solicitudes. Hay un caso principal por operación y casos adicionales de encadenamiento, aislamiento, validación, ausencia de credenciales, eliminación y conflicto.
- El [esquema de eventos](../contratos/evento-notificacion.schema.json) se valida como Draft 2020-12. Los cuatro ejemplos de origen cumplen el esquema. Las pruebas del evento de curso comprueban campos requeridos, tipos, URL y opcionales.

## Ejecuciones

| Comprobación | Resultado observado |
| --- | --- |
| Sincronización desde los clones de `main` fijados | Los cinco OpenAPI, las tres colecciones originales y el JSON Schema coinciden con sus blobs de origen. La guía incorpora los enlaces centrales. |
| Validación documental y JavaScript | Contratos, referencias, operaciones, cuerpos positivos, correspondencia con Postman, eventos, enlaces y patrones de secretos comprobados. Se mantiene la excepción de Usuarios documentada en la [auditoría](auditoria.md). |
| Newman, entorno de ejemplo | 75 omitidas, 0 solicitudes HTTP, 0 aserciones. |
| Newman, Brecha en loopback | `GET /health` → `200`. `GET /skills-gap` sin certificado → `403 APIM_CERTIFICATE_REQUIRED`. 2 solicitudes, 7 aserciones, 0 fallos. |
| Newman, API principal de APIM | `GET /api/v1/cvs` devolvió `401` sin token y con un valor inválido. 2 solicitudes, 2 aserciones, 0 fallos. |
| Usuarios, `mvn test` | 15 aprobadas, 0 fallos y 0 omitidas. |
| Newman, ciclo local de CVs | `200 → 201 → 200 → 200 → 200 → 204 → 404`. 7 solicitudes, 30 aserciones y 0 fallos. Se usaron los routers de CVs y los dobles de base de datos y publicador de sus pruebas. |
| CVs, `python -m pytest -q` | 38 aprobadas, con una advertencia de compatibilidad de TestClient. |
| Brecha, `npm test` | 53 aprobadas, 0 fallos y 0 omitidas. |
| Notificaciones, `dotnet test Notificaciones.sln` | 190 aprobadas, 0 fallos y 0 omitidas con .NET 8. Incluye registro de dispositivos, FCM con dobles, plantillas, consumo de eventos y negociación. |
| Ofertas y postulaciones, Maven | 74 aprobadas en la selección sin Docker. La corrida amplia registró 17 errores en `PersistenceAdaptersTest` y `SwaggerUiTest` por Testcontainers sin motor Docker. |
| Azure, plano de administración | Inventario de operaciones, destinos, políticas de identidad y metadatos de certificado cliente de los App Services visibles. Consulte [seguridad](seguridad-apim.md). |

En una sesión anterior, Android registró `200` en `GET /api/v1/cvs` y `GET /api/v1/jobs`, y `409 SKILLS_INPUT_REQUIRED` en `GET /api/v1/skills-gap`. El antecedente carece de traza que identifique la revisión desplegada.

## Alcance E2E confirmado por el equipo — 8 de noviembre de 2026

El equipo informó que **Android 0.7.2** está disponible en Firebase App Distribution.
Esta publicación **no certifica** el inicio de sesión en esa APK: las respuestas
`200` registradas previamente para `/api/v1/cvs` y `/api/v1/jobs` corresponden a
una ejecución de Android en modo *debug*. Si la autenticación falla en 0.7.2,
registrar el texto exacto del error, el dispositivo, la versión instalada y
la fecha/hora, sin compartir ID tokens ni datos personales.

**Plan de pruebas de Fase II:**

- **E2E disponibles para ejecución:** Ofertas, Postulaciones, Brecha y Notificaciones.
  «Disponibles» no significa «pasaron»: registrar cada ejecución, código HTTP,
  condiciones y resultado. Las operaciones administrativas de plantillas de
  Notificaciones requieren comprobar primero su publicación en APIM.
- **E2E temporalmente bloqueados:** CVs, generación de PDF y operaciones de IA.
  Según el estado comunicado por el equipo, Pérez debe cargar las plantillas y
  resolver la respuesta `500` de IA. Las pruebas locales de CVs que figuran más
  arriba siguen siendo evidencia **local**, no validación de estas E2E.
- **Trabajo futuro, fuera del cierre de Fase II:** ciclo FCM del **cliente Android**
  (registro, renovación y eliminación del token, recepción en primer y segundo
  plano, navegación al aviso). Se conservan el contrato de dispositivos, el
  código de FCM del backend y sus pruebas. Las pruebas del backend no demuestran
  entrega real a un dispositivo.

El objetivo inmediato es completar las E2E disponibles con cuentas y datos
sintéticos, sin alterar información productiva.

## Pendientes concretos

| Responsable | Acción requerida |
| --- | --- |
| APIM | Aplicar y comprobar el rol administrativo en las escrituras de ofertas. Acordar la publicación de plantillas de Notificaciones con autorización de administrador. Entregar trazas depuradas de enrutamiento, encabezados y autorización. |
| App Service y responsables de backend | Verificar mTLS, huella activa, bloqueo de acceso directo y revisión desplegada. Facilitar la configuración efectiva de Ofertas. |
| Entorno de ensayo | Proporcionar una base aislada, cuentas propietaria/ajena/admin/sin instantánea y datos sintéticos. Ejecutar los escenarios autenticados y las escrituras según el [plan](plan-pruebas.md). |
| Usuarios | Corregir las comillas del ejemplo de dirección en el contrato original y documentar las cabeceras de sesión. |
| Brecha y Notificaciones | Acordar la transformación de cursos y el disparador, implementar el productor y verificar Service Bus, deduplicación y entrega. |
| Ofertas y entorno local | Iniciar Docker y ejecutar la suite Maven completa para cubrir persistencia y Swagger con Testcontainers. |
| Android y Notificaciones | El ciclo FCM del cliente Android queda como **trabajo futuro fuera del cierre de Fase II**. Se conserva la cobertura documental y las pruebas del backend. |
