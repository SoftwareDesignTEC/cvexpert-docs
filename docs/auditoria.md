# Auditoría de contratos y código

Se revisaron las ramas `main` de los cinco servicios y los dos clientes en las revisiones de [fuentes.json](../contratos/fuentes.json). Las rutas, encabezados, DTO, errores declarados y pruebas de origen se consultan en la [matriz](matriz-trazabilidad.md). De la [consolidación del PR #1](https://github.com/SoftwareDesignTEC/cvexpert-docs/pull/1) se retoman los controles de referencias, IDs de operación y JSON Schema, además de las diferencias de errores, paginación e identidad. Los diagnósticos anteriores sobre rutas pendientes se contrastaron con el código actual.

| Servicio | Rutas REST del contrato | Contraste con `main` |
| --- | ---: | --- |
| Usuarios | 7 | `ProfileController`, `LegalController` y `HelpController` cubren el inventario. Las rutas de perfil requieren identidad propia. Una lectura puede crear el perfil, actualizar su rol y registrar actividad de sesión. `X-Client` y `User-Agent` también se leen en consulta y exportación, aunque el contrato lista `X-Client` para sesiones. |
| CVs | 9 | Los routers de CV, plantillas y experiencia implementan las rutas. Los CV se filtran por propietario. Las operaciones de experiencia usan el proveedor de lenguaje configurado y registran su uso. `GET /health` existe en el código y queda fuera del OpenAPI de producto. |
| Ofertas y postulaciones | 13 | Los controladores implementan catálogo, postulaciones, alertas y cambio administrativo de estado. Las escrituras de ofertas requieren rol administrativo. Una postulación repetida devuelve `409` y una ajena se oculta con `404`. La sonda Actuator queda fuera del inventario OpenAPI. |
| Brecha y cursos | 4 | `/courses` consulta el catálogo PostgreSQL. `PUT /skills-gap/input` reemplaza la instantánea del usuario. `GET /skills-gap` devuelve `409 SKILLS_INPUT_REQUIRED` si no existe una instantánea y el mercado está configurado. El código no contiene un publicador para `course.recommended`. |
| Notificaciones | 12 | Directorio, dispositivos, historial, contador, lectura, plantillas, salud y hub están implementados. `NotificationsHub.Path` es `/notifications/hub`. El negotiate devuelve la forma Azure únicamente con Azure SignalR configurado. |

## Diferencias que debe resolver el servicio responsable

| Responsable | Diferencia | Corrección propuesta |
| --- | --- | --- |
| Usuarios | En `components.schemas.UserProfile.properties.address`, el ejemplo de un mapa YAML en línea contiene una coma sin comillas. OpenAPI interpreta `Alajuela` como una propiedad inválida. El hash de la copia coincide con el original. | Entrecomillar el valor completo en origen. CI corrige solo ese ejemplo en memoria para el blob fijado y valida el resto del contrato de forma estricta. |
| Usuarios | Los controladores de consulta y exportación también leen `X-Client` y `User-Agent` opcionales. | Alinear la documentación de cabeceras y de los efectos de sesión con el controlador. |
| CVs | Los handlers del proveedor para las operaciones de experiencia pueden producir `429`, `502` o `503`. El OpenAPI documenta los errores de entrada e identidad. | Completar el contrato de errores del proveedor y su evidencia. |
| CVs | El DTO serializa campos opcionales como `null` en `PersonalInfo`, `TemplateSection` y `Certification`. Además, `Template.layout` declara `nullable` junto a `allOf`. | Alinear los esquemas de origen con la serialización. Postman admite solo los nulos comprobados en esos DTO y conserva los demás controles de respuesta. |
| Brecha y APIM | El OpenAPI conserva una mención al mock de APIM. El código de backend ya implementa brecha ordinal y persistencia. El bypass local del catálogo no autentica el flujo de instantáneas. | ARM registra el destino de Brecha para las tres operaciones de negocio sin una política de mock observada. Actualizar la nota de origen tras comprobar la traza y la revisión efectiva del backend. |
| Notificaciones y clientes | El payload de negotiate con token de Azure se diferencia del fallback de SignalR local. La guía FCM describe comportamiento del cliente que aún no aparece en Android. | Mantener ambos modos explícitos. Registrar el ciclo FCM del cliente Android como **trabajo futuro**, fuera del cierre de Fase II; conservar sus contratos y pruebas del backend. |
| APIM y Ofertas | APIM elimina el rol en las tres escrituras de ofertas que el backend reserva a administradores. | Aplicar la política de autorización de administrador en el gateway y probar ambos roles. |
| APIM y Notificaciones | Las tres operaciones de plantillas están ausentes del inventario de APIM revisado. | Acordar su publicación y autorización. |
| Integración | Los servicios usan distintas formas de error y límites de paginación. | Mantener los esquemas y límites de cada dominio en clientes y pruebas. Acordar cambios de compatibilidad en los servicios responsables. |

Los estados de la matriz describen el código de la revisión fijada. Los artefactos de ejecución y los bloqueos actuales están en el [estado de entrega](estado-entrega.md).

## Alcance comunicado para pruebas E2E (8 de noviembre de 2026)

Ofertas, Postulaciones, Brecha y Notificaciones pueden comenzar pruebas E2E en el entorno de ensayo. CVs, generación PDF y operaciones de IA permanecen bloqueados hasta que Pérez cargue las plantillas y se resuelva un fallo HTTP `500` de IA. La publicación de Android `0.7.2` en Firebase no certifica por sí misma su autenticación. El ciclo FCM del cliente Android queda fuera del alcance de Fase II; el backend y el contrato continúan documentados.
