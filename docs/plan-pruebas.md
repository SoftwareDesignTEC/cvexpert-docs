# Plan de verificación E2E

## Priorización de E2E vigente (8 de noviembre de 2026)

**Prioridad actual:** ejecutar Ofertas, Postulaciones, Brecha y Notificaciones
con identidades de prueba autorizadas. Conservar los resultados reales y las
omisiones justificadas; la disponibilidad de una ruta no implica éxito del test.

**Temporalmente bloqueadas:** las E2E de CVs, generación de PDF e IA, hasta que
se carguen las plantillas y se resuelva el error HTTP `500` del proveedor de IA.
El ciclo local de CVs ya registrado es independiente de estas verificaciones.

**Push en Android (actualización del 16 de noviembre):** el ciclo FCM está
integrado desde Android `0.9.5`. La recepción del push y la administración del
token se prueban en el teléfono con la APK de distribución de esa versión o
posterior (ver los pasos de Notificaciones y Mensajería).

**Compilación distribuida:** Android `0.7.2` fue anunciada como publicada en
Firebase. No atribuirle los resultados observados en Android debug sin repetir
la prueba en la APK de distribución; ante un error de Google Sign-In, anotar el
mensaje exacto, dispositivo y versión.

## Preparación

1. El responsable de APIM confirma el inventario de operaciones, revisión, destino y políticas para el entorno de ensayo. El responsable de cada servicio confirma la revisión desplegada y sus dependencias.
2. Preparar una cuenta usuaria propietaria, otra ajena, una administradora y una cuenta sin instantánea de habilidades. Usar bases y cola de ensayo aisladas. Para FCM, instalar la APK `0.9.5` o posterior desde Firebase, iniciar sesión con la cuenta propietaria y aceptar el permiso de notificaciones.
3. Configurar el [entorno Postman](../postman/README.md), comprobar que el ID token corresponde a la audiencia del entorno y validar la disponibilidad de los datos de prueba. Separar las corridas con y sin credenciales.

## Orden de ejecución

| Paso | Resultado que debe verificarse |
| --- | --- |
| Lecturas | Esquema de respuesta, paginación, consulta de una entidad conocida y lectura de configuraciones preparadas. Negotiate devuelve URL y token de Azure SignalR cuando está configurado. |
| Perfil y alertas | Alta o carga del perfil, actualización parcial, sesión/exportación y persistencia de alertas. |
| CVs (E2E bloqueada temporalmente) | Tras la carga de plantillas y la corrección del HTTP `500` de IA: crear, leer, actualizar y eliminar CV; comprobar PDF e IA por separado. Hasta entonces, conservar únicamente la evidencia de pruebas locales ya ejecutadas. |
| Ofertas y postulaciones | Crear oferta como administrador, editar, postular como usuario, comprobar duplicado `409`, aislamiento `404` para otra cuenta, cambio de estado administrativo y limpieza por ID. |
| Brecha | Guardar instantánea, consultar con éxito y, con una cuenta diferente sin instantánea, verificar `409 SKILLS_INPUT_REQUIRED`. Confirmar que APIM alcanza el backend real. |
| Notificaciones | Validar directorio, registro/baja por API de dispositivos, historial y contador. En Android, comprobar que al iniciar sesión el token aparece en `devices` y que al cerrar sesión se elimina; no confundir esa prueba de las APIs de dispositivos con la recepción FCM en el teléfono, que se verifica en Mensajería. Las plantillas administrativas requieren ruta APIM confirmada. |
| Seguridad | Probar token ausente, inválido, vencido o con audiencia ajena, usuario sin permiso, suplantación de encabezados y acceso directo sin certificado válido. |
| Mensajería | Generar un evento mediante un productor implementado o publicar un mensaje de prueba autorizado. Correlacionar `eventId` con historial y con los canales SignalR, correo y push. Con la app en segundo plano y en primer plano, comprobar que el push llega al teléfono y que su `notificationId` corresponde al aviso del historial. Verificar duplicados y cola de errores. |

En la fase de limpieza, conservar los IDs devueltos por el entorno privado hasta que se confirme la baja de los recursos creados. Si se interrumpe un flujo, revisar los registros de ensayo antes de reintentarlo. Las instantáneas, los perfiles, las alertas y las ediciones de plantillas requieren restaurar los datos de prueba o descartar el entorno.

## Evidencia

Registrar fecha, revisión, canal, nombre de solicitud, código esperado y recibido, aserciones y razón de cada omisión. Conservar solo resúmenes depurados en [evidencias](../evidencias/README.md). La [matriz](matriz-trazabilidad.md) y el [estado de entrega](estado-entrega.md) separan cobertura definida, ejecución local y pruebas de gateway.
