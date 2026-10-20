# Revisión de integración de los cinco contratos

**Estado:** informe de diferencias observadas, no decisiones unilaterales.
**Revisado:** 20-10-2026. Ver las versiones y commits exactos en [`fuentes.md`](fuentes.md).

## 1. Identidad, APIM y exposición

Los contratos de Usuarios, CVs, Ofertas/Postulaciones y Notificaciones describen el uso de `X-User-Id` como identificador derivado del `sub` de Google, inyectado por APIM. También aparece `X-User-Email`; para algunas rutas administrativas, `X-User-Role`. Los clientes no deberían poder elegir estos valores.

**Por confirmar con APIM:** validación del token, eliminación/sobrescritura de encabezados aportados por el cliente, autorización por rol, rutas y prefijo `/api/v1`, certificados de cliente requeridos por los backends y bloqueo del acceso directo a sus App Services. La documentación no prueba que esas medidas funcionen hoy.

El contrato de Brecha/Cursos documenta `/skills-gap` **solo con datos DEMO** en entornos `development`/`test` y un `/courses` **propuesto y NO implementado**. La eventual seguridad de `/courses` permanece pendiente; no interpretar la ausencia de seguridad OpenAPI como permiso de acceso anónimo.

## 2. Contradicciones / decisiones a cerrar

| Tema | Evidencia en los contratos | Decisión pendiente |
|---|---|---|
| **Errores HTTP** | Usuarios propone `{status,message,path,timestamp}`; CVs `{statusCode,error,message,errors?}`; Notificaciones `{status,message,errors?}`. Ofertas tiene su propio esquema `Error`. | ¿Unificar representación externa desde APIM o documentar explícitamente diferencias por servicio? Web y Android deben poder interpretar los errores efectivos. |
| **Paginación** | Cursos/Brecha y CVs: `pageSize` predeterminado `20`; Ofertas/Postulaciones: `10`; otros contratos definen sus reglas. | Consenso sobre defaults, máximos y la forma `{items,page,pageSize,totalRecords}`; no cambiarlos en los repos sin consentimiento. |
| **Versiones OpenAPI** | Cuatro especificaciones usan `3.0.3`; Ofertas/Postulaciones usa `3.1.0`. | Confirmar compatibilidad con herramientas de APIM, Swagger y validadores de la entrega. |
| **Fechas e IDs** | Diversos contratos indican epoch en **milisegundos UTC** e IDs de recursos como texto; algunas descripciones de negocio difieren. | Confirmar que todos los clientes convierten fechas y manejan IDs de forma consistente. |
| **Brecha/Cursos** | `/skills-gap` disponible solo como DEMO y `/courses` propuesto; `CatalogCourse.durationHours` permite `null`, pero `CourseSuggestion.durationHours` no. | Acordar fuente de habilidades, escala de niveles y compatibilidad con web/Android; implementar endpoints reales. |
| **Notificaciones: rama versus implementación** | En `docs/contratos`, el contrato propone `POST /notifications/hub/negotiate` y Azure SignalR Service. En `main`, `Program.cs` registra actualmente `MapHub<NotificationsHub>("/hubs/notifications")` y solo un `HealthController`. | Samuel debe decidir cómo y cuándo migrar del hub actual al contrato planeado. **No anunciar como funcional el negotiate documentado.** |
| **Eventos Service Bus** | Esquema `evento-notificacion.schema.json`, cola `notificaciones-eventos`, cuatro tipos y campos específicos. | Validar publicadores, SAS solo `Send`, `messageId=eventId`, idempotencia y sus pruebas de integración. |
| **Estado real de endpoints** | Los archivos especifican operaciones existentes y propuestas, no necesariamente cubiertas por código o despliegue. | Cada dueño presenta pruebas Swagger/Postman y evidencia APIM. |

## 3. Acuerdos de integración a validar

- **Identidad:** `X-User-Id` representa el `sub` Google; el backend no debe aceptar identidades arbitrarias aportadas por cliente.
- **Rutas:** APIM publica las URLs de cara al cliente y reenvía al microservicio correcto. El contrato de cada dominio conserva sus rutas backend. **Confirmar** el prefijo APIM con Cabrera.
- **Fechas:** milisegundos desde Unix epoch UTC; no confundir con segundos ni con fechas ISO.
- **Mensajería:** contratos Service Bus separados de REST/OpenAPI; un mensaje por destinatario, `eventId` único y esquema versionado. El patrón de entrega al menos una vez obliga idempotencia.
- **Privacidad:** jamás copiar datos reales de estudiantes, correos, tokens o cadenas de conexión en ejemplos, pruebas y capturas.
- **Evolución:** los contratos copiados son instantáneas de referencia; la fuente funcional de cada dominio sigue siendo su repositorio.

## 4. Lista de revisión de los responsables

- [ ] **Usuarios:** confirmar endpoints y errores actuales, autenticar identidad de APIM y estados HTTP.
- [ ] **CVs:** confirmar compatibilidad con web y Android, rutas IA, fechas e identidad.
- [ ] **Ofertas/Postulaciones:** cerrar métodos propuestos vs implementados, compatibilidad y evento `job.new`.
- [ ] **Brecha/Cursos:** aprobar contrato de `/courses`, implementar brecha real, poblar catálogo real y evento `course.recommended`.
- [ ] **Notificaciones:** fusionar o revisar `docs/contratos`; reconciliar `/notifications/hub/negotiate` versus `/hubs/notifications` y documentar pruebas de cola.
- [ ] **APIM:** validar `/api/v1`, cabeceras inyectadas, rol admin, certificados cliente y prohibición de saltarse el gateway.
- [ ] **Web/Android:** confirmar consumo de rutas, modelos y errores.
- [ ] **Equipo:** revisar y aprobar este inventario sin dar por completos los endpoints pendientes.

**Criterio de cierre:** los cinco responsables confirman compatibilidad y las diferencias se resuelven en contratos originales mediante PR. Una copia consolidada no sustituye esa aprobación.
