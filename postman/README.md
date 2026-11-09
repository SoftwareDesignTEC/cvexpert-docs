# Postman y Newman

Importe [cvexpert.postman_collection.json](cvexpert.postman_collection.json) y duplique el [entorno de ejemplo](apim.postman_environment.json). La colección combina escenarios principales, comprobaciones de seguimiento y negativas. La [matriz](../docs/matriz-trazabilidad.md) identifica la solicitud principal de cada operación. Los cuerpos se obtienen de los contratos, DTO o colecciones de origen y se validan localmente con los esquemas.

## Orden de pruebas para la entrega

Priorizar **Ofertas, Postulaciones, Brecha y Notificaciones** en el entorno E2E autorizado. Las E2E de **CVs, PDF e IA** están temporalmente bloqueadas por plantillas pendientes y un error `500` de IA; el ciclo local de CVs no sustituye esas pruebas. El registro/baja de dispositivos en Postman comprueba los endpoints REST, **no** la recepción FCM en Android, que corresponde a trabajo futuro. Android **0.7.2** fue anunciada para Firebase; los resultados de una versión debug anterior no certifican esa APK.

## Entorno APIM

| Variable | Configuración |
| --- | --- |
| `target`, `enableApim` | Use `apim` y `true` tras confirmar el destino. |
| `apiBaseUrl` | Base con prefijo, sin barra final. La API principal observada usa `https://gabriel-api-management.azure-api.net/api/v1`. Para escribir, use la base equivalente de un entorno aislado. |
| `googleIdToken` | ID token vigente de la cuenta propietaria, emitido para la audiencia aceptada por APIM. |
| `otherGoogleIdToken`, `freshGoogleIdToken` | Cuenta ajena y cuenta sin instantánea, respectivamente. |
| `adminGoogleIdToken`, `allowAdmin` | ID token de cuenta administradora de ensayo y habilitación explícita `true` para los casos administrativos. |
| `allowWrites`, `testApiBaseUrl` | Para operaciones con efectos, establezca `true` y la misma base HTTPS confirmada de ensayo en ambas variables de URL. Incluye ciertas lecturas de perfil, que registran sesión, y las solicitudes negativas con método de escritura. |
| `allowApimJobAdmin` | Habilite solo cuando el entorno entregue el rol administrativo al backend de Ofertas. La política consultada elimina ese encabezado en las escrituras. |
| `apimRouteOverrides` | Opcional. Objeto JSON con clave `servicio MÉTODO /ruta/interna` y valor de ruta relativa a la base. Conserve los marcadores de parámetros, por ejemplo `{id}`. Las operaciones de plantillas de Notificaciones requieren un mapeo confirmado en ese entorno. |

Inicie sesión con las cuentas de ensayo en el cliente configurado para esa audiencia. Use el ID token en las variables locales del entorno de Postman o en un archivo privado para Newman. Cuando expire, renueve la sesión en el cliente y sustituya el token correspondiente. Los tokens, correos e IDs de prueba se configuran fuera de Git. El [flujo de identidad](../docs/seguridad-apim.md) describe las cabeceras que inyecta el gateway.

## Variables de prueba y orden

- En **Lecturas**, configure `fixtureJobId` y `fixtureTemplateId` con IDs existentes. `GET /alerts` requiere alertas previamente guardadas. El negotiate de SignalR está en esta carpeta y emite un token efímero sin requerir el permiso de escritura.
- En **Perfil y alertas**, `profileId` corresponde al sujeto de la cuenta usuaria de ensayo. Este flujo actualiza su perfil y las alertas de esa misma cuenta.
- En **Ciclo de CV**, el catálogo aporta una plantilla. La colección guarda `runCvId`, verifica creación y edición, elimina el CV y comprueba `404`. Ejecute la carpeta completa en una sola corrida.
- **Administración de ofertas** guarda `runJobId` al crear, verifica la oferta y la edición, elimina y comprueba `404`. En **Ciclo de postulaciones**, configure `fixtureJobId` con una oferta de ensayo a la que la cuenta aún no se haya postulado. El flujo conserva `runApplicationId`, verifica duplicidad, propiedad, cambios de estado y retiro.
- En **Instantánea y brecha**, el caso positivo escribe y luego espera `200`. La carpeta **Negativas** usa la cuenta sin instantánea para verificar `409 SKILLS_INPUT_REQUIRED`. El mercado debe estar configurado para ambas pruebas.
- En **Directorio y dispositivos**, use `fixtureDeviceToken` de un dispositivo Firebase reservado para la prueba. La colección conserva el token en memoria para comprobar el registro repetido y la baja idempotente. **Lectura de avisos** requiere `fixtureNotificationId` de un aviso de esa cuenta.
- En **Administración de plantillas**, use una base descartable y el par `notificationType`/`language`. Las ediciones persisten. Para observar la respuesta por defecto, elija un par sin una edición previa.
- **APIM - Rechazo de identidad** contiene dos GET separados para token ausente e inválido. Ambos esperan `401` sin imponer un esquema de error del backend.

Las variables con prefijo `run` duran una corrida. Una solicitud dependiente sin el dato anterior se omite con el motivo. Tras una interrupción, revise el entorno de ensayo y limpie los recursos creados antes de reintentar.

## Backend directo

Use `target=local`, `allowDirect=true` y la URL de loopback del servicio, por ejemplo `brecha-cursosBaseUrl=http://127.0.0.1:3000`. Las otras bases son `usuariosBaseUrl`, `cvsBaseUrl`, `ofertas-postulacionesBaseUrl` y `notificacionesBaseUrl`. Las carpetas de backend directo separan salud y acceso sin identidad o certificado. Los casos de negocio pueden ejecutarse contra un backend local compatible con identidad de prueba.

Para los servicios con modo local documentado, configure los pares `localUserId`/`localUserEmail`, `localOtherId`/`localOtherEmail` y `localAdminId`/`localAdminEmail` según el escenario. El runner aplica la identidad solo al proceso en loopback. El negocio de Brecha exige un certificado verificado incluso con el modo local del catálogo. Ejecute su flujo autenticado vía APIM de ensayo. La negociación local de Notificaciones espera la forma del contrato Azure solo con `localSignalR=true` y el proveedor Azure configurado.

## Ejecutar e interpretar

En Postman seleccione el entorno y las carpetas en Collection Runner. La consola registra `NO EJECUTADA` cuando falta una habilitación, identidad o fixture. La solicitud omitida no tiene respuesta ni aserciones. Las carpetas de salud y negocio se pueden ejecutar por separado.

Instale Newman 6.2.3 con Node.js y ejecute las carpetas desde la raíz.

```sh
npm install --no-save --no-package-lock newman@6.2.3
node scripts/ejecutar_postman.cjs postman/mi-entorno-privado.json "Lecturas"
node scripts/ejecutar_postman.cjs postman/mi-entorno-privado.json "Ciclo de CV" "Negativas"
```

El runner muestra el código HTTP, el nombre de la solicitud y un resumen sin URLs, cabeceras ni cuerpos. Devuelve error si hubo fallos, omisiones o cero solicitudes ejecutadas. Los diagnósticos detallados de Postman o Newman pueden contener datos sensibles. Consérvelos en privado y adjunte solo el resumen depurado según el [plan de pruebas](../docs/plan-pruebas.md).
