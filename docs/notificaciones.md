# Integración de Notificaciones

La [guía del servicio](../contratos/notificaciones.origen.md) conserva los ejemplos y las secciones «Push (FCM)» y «Preguntas abiertas». Su revisión y el hash del archivo original están en [fuentes.json](../contratos/fuentes.json). Los cambios de FCM y plantillas entraron en el repositorio del servicio mediante los PR [#8](https://github.com/SoftwareDesignTEC/cvexpert-ms-notificaciones/pull/8) y [#12](https://github.com/SoftwareDesignTEC/cvexpert-ms-notificaciones/pull/12).

## Persistencia y canales

El consumidor valida el evento y usa `eventId` para deduplicar. La notificación persistida es consultable por REST y tiene un identificador propio. SignalR, push y correo son entregas del mismo aviso, sujetas a configuración. Correo usa Azure Communication Services y el correo/idioma del directorio. SignalR con Azure configurado devuelve una URL y un token efímero en `POST /notifications/hub/negotiate`. Después de negociar vía APIM, el cliente se conecta directamente a Azure SignalR. En desarrollo, el fallback local utiliza la negociación estándar de SignalR y su respuesta difiere del contrato para Azure.

**Push en Android:** el ciclo completo de FCM está integrado desde la versión 0.9.5 de la app ([PR #43 de cvexpert-mobile](https://github.com/SoftwareDesignTEC/cvexpert-mobile/pull/43), 2026-11-15): registro y baja del token, recepción del push y aviso con la app abierta.

## Push Android

- El backend registra el token con `POST /notifications/devices` y plataforma `android`. Responde `201` para un token nuevo y `200` para un registro previo. Si cambia la cuenta que registró el mismo token, el registro pasa a la última cuenta.
- `DELETE /notifications/devices/{token}` elimina el registro propio. La ruta recibe el token codificado para URL y devuelve `204` también si el registro no existe o pertenece a otra cuenta.
- Se envía a todos los tokens registrados para el destinatario. El objeto `notification` contiene `title` y `body` renderizados. `data` contiene `notificationId` y `type` como cadenas. El identificador corresponde al aviso persistido, que puede consultarse en `GET /notifications` y marcarse mediante `PATCH /notifications/{id}/read`.
- En segundo plano, Android muestra el aviso del payload `notification`. En primer plano lo recibe `CvMessagingService.onMessageReceived`, que lo muestra igual y actualiza la campana. `PushTokenSync` registra el token al iniciar sesión y cuando FCM entrega uno nuevo, y lo elimina al cerrar sesión.
- El canal elimina los tokens que Firebase marca como `Unregistered`. Los demás fallos se registran sin borrar el token. El backend habilita el canal con `Firebase:ServiceAccountJson`, provisionado como secreto `Firebase--ServiceAccountJson` cuando se usa Key Vault. El cliente debe corresponder al mismo proyecto Firebase.

El backend contiene `DevicesController`, `FcmNotificationChannel`, `FirebaseFcmSender` y pruebas de canal y registro. Android sincroniza el directorio, consume el historial, el contador y las acciones de lectura por REST, y recibe el push con `CvMessagingService` y `PushTokenSync`. El push solo se activa si el APK se compila con `NOTIFICATIONS_ENABLED=true` y `google-services.json` del mismo proyecto Firebase que usa el backend. [Backend](https://github.com/SoftwareDesignTEC/cvexpert-ms-notificaciones/tree/501cd20d9c0d70ac6baa9340dac669bf527a1295/src/Notificaciones.Api) · [Android](https://github.com/SoftwareDesignTEC/cvexpert-mobile/tree/7932a1236e06cb7a5a5f024db66a08ffa86340f6/app/src/main/java/com/cvpro/app/data/notifications)

## Plantillas editables

`TemplateResponse` omite `updatedBy` cuando es nulo. Las plantillas por defecto tienen `updatedAt: 0` y omiten esa propiedad. El siguiente ejemplo muestra la respuesta por defecto con texto de prueba.

```json
{
  "type": "application.status_changed",
  "language": "es",
  "title": "Actualización de postulación",
  "body": "El estado de tu postulación cambió.",
  "updatedAt": 0
}
```

Una edición administrativa almacena la fecha en milisegundos y el correo del administrador. Las plantillas validan marcadores por tipo de evento. La colección comprueba la semántica del valor por defecto cuando se encuentra una plantilla sin editar.

## Contrato de mensajería

Un mensaje por destinatario en `notificaciones-eventos`. El sobre admite `schemaVersion: 1`, `eventId` UUID v4, `type`, `userId` como identificador de usuario, `occurredAt` en epoch milisegundos UTC, `source` y `data`. En Service Bus, use `messageId = eventId`, `subject = type` y `contentType = application/json`. Los reintentos del mismo evento conservan su identidad. El esquema rechaza campos adicionales en el sobre y admite extensiones en `data`.

| Tipo | Productor en código | Disparador o estado |
| --- | --- | --- |
| `application.status_changed` | Ofertas y postulaciones | Cambio administrativo de estado |
| `job.new` | Ofertas y postulaciones | Alta de oferta, para usuarios con alertas habilitadas y compatibilidad suficiente |
| `cv.generated` | CVs | Creación del CV tras un uso registrado de las operaciones de experiencia. El publicador se selecciona por configuración |
| `course.recommended` | Pendiente en Brecha y cursos | Consumidor, esquema y plantillas disponibles. El código de Brecha devuelve resultados REST y carece de publicador Service Bus |

El consumidor envía a la cola de mensajes fallidos por `InvalidJson` o `SchemaValidationFailed`. Los fallos transitorios siguen los reintentos de Service Bus. Verifique configuración de la cola, permisos de envío/escucha, deduplicación y entregas por canal en un ambiente aislado.

## Adaptación de `course.recommended`

`source` debe ser `brecha-cursos`. El [esquema](../contratos/evento-notificacion.schema.json) exige `title` y `platform` como cadenas no vacías, `url` absoluta HTTP o HTTPS e `isPaid` booleano. Permite omitir `duration` y `skill` o enviarlos como `null`. Los valores presentes se expresan como cadenas.

| Modelo REST de Brecha | Adaptación necesaria para el evento |
| --- | --- |
| `title`, `platform`, `url` | Transferir cuando cumplen los tipos y la URL HTTP/HTTPS del esquema. |
| `isPaid` | Transferir el valor conocido. `CourseSuggestion` lo admite como opcional, por lo que una sugerencia sin ese dato requiere una fuente verificable antes de publicar. |
| `durationHours` entero o nulo | Convertir las horas conocidas a texto de presentación si se decide enviar `duration`. Una duración desconocida se puede omitir o enviar como nula. |
| `skills` arreglo | Seleccionar la habilidad que motivó la recomendación si el productor puede identificarla. Si falta el criterio, omitir `skill` o enviarla nula. |
| `id`, `logoUrl` | Campos del modelo REST sin equivalente obligatorio en `data`. |

Brecha y Notificaciones deben acordar cuándo publicar, la fuente de `isPaid` en cada sugerencia, la selección de una habilidad y el formato/idioma de la duración. Falta implementar el productor y verificar entrega, duplicados y cola de errores. La coincidencia del esquema por sí sola acredita la forma del mensaje. [Código de Brecha](https://github.com/SoftwareDesignTEC/cvexpert-ms-brecha-cursos/tree/f08d8a37f33435456849a76b1afac26df77a1865/src)
