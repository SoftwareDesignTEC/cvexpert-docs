# Plan de verificación E2E

## Preparación

1. El responsable de APIM confirma el inventario de operaciones, revisión, destino y políticas para el entorno de ensayo. El responsable de cada servicio confirma la revisión desplegada y sus dependencias.
2. Preparar una cuenta usuaria propietaria, otra ajena, una administradora y una cuenta sin instantánea de habilidades. Usar bases y cola de ensayo aisladas. Para FCM, reservar un dispositivo del proyecto Firebase de prueba.
3. Configurar el [entorno Postman](../postman/README.md), comprobar que el ID token corresponde a la audiencia del entorno y validar la disponibilidad de los datos de prueba. Separar las corridas con y sin credenciales.

## Orden de ejecución

| Paso | Resultado que debe verificarse |
| --- | --- |
| Lecturas | Esquema de respuesta, paginación, consulta de una entidad conocida y lectura de configuraciones preparadas. Negotiate devuelve URL y token de Azure SignalR cuando está configurado. |
| Perfil y alertas | Alta o carga del perfil, actualización parcial, sesión/exportación y persistencia de alertas. |
| CVs | Crear con plantilla del catálogo, leer por ID, actualizar, volver a leer, eliminar y obtener `404`. Ejecutar las operaciones de experiencia aparte con proveedor habilitado. |
| Ofertas y postulaciones | Crear oferta como administrador, editar, postular como usuario, comprobar duplicado `409`, aislamiento `404` para otra cuenta, cambio de estado administrativo y limpieza por ID. |
| Brecha | Guardar instantánea, consultar con éxito y, con una cuenta diferente sin instantánea, verificar `409 SKILLS_INPUT_REQUIRED`. Confirmar que APIM alcanza el backend real. |
| Notificaciones | Actualizar directorio, registrar y volver a registrar el token, eliminarlo y repetir la baja. Verificar lectura y contador con avisos de prueba. Administrar plantillas en una base descartable. |
| Seguridad | Probar token ausente, inválido, vencido o con audiencia ajena, usuario sin permiso, suplantación de encabezados y acceso directo sin certificado válido. |
| Mensajería | Generar un evento mediante un productor implementado o publicar un mensaje de prueba autorizado. Correlacionar `eventId` con historial, SignalR, correo y FCM. Reenviar el mismo ID y comprobar deduplicación. Probar mensaje inválido y su razón en la cola de errores. |

En la fase de limpieza, conservar los IDs devueltos por el entorno privado hasta que se confirme la baja de los recursos creados. Si se interrumpe un flujo, revisar los registros de ensayo antes de reintentarlo. Las instantáneas, los perfiles, las alertas y las ediciones de plantillas requieren restaurar los datos de prueba o descartar el entorno.

## Evidencia

Registrar fecha, revisión, canal, nombre de solicitud, código esperado y recibido, aserciones y razón de cada omisión. Conservar solo resúmenes depurados en [evidencias](../evidencias/README.md). La [matriz](matriz-trazabilidad.md) y el [estado de entrega](estado-entrega.md) separan cobertura definida, ejecución local y pruebas de gateway.
