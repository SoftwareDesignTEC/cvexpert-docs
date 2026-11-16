# Seguridad de Azure API Management

## Cliente y autenticación

La API principal `cv-api` del gateway `gabriel-api-management` publica la base `https://gabriel-api-management.azure-api.net/api/v1`. El [inventario de ARM](../contratos/apim-rutas.json) confirma 40 operaciones de producto y sus destinos configurados. Las APIs de dominio también tienen prefijos propios, por ejemplo `/api/v1/ofertas` y `/api/v1/notificaciones`. La matriz y la colección usan la API principal que consumen los clientes. En las operaciones revisadas, `set-backend-service` elige el destino y no se observó un `rewrite-uri` específico.

- El cliente envía el ID token de Google en `Authorization: Bearer <id_token>`. La política `validate-jwt` usa el descubrimiento OIDC de Google, una audiencia configurada y los emisores `accounts.google.com` y `https://accounts.google.com`. APIM requiere firma y expiración por defecto. La política devuelve `401` ante fallo de validación. [Google Identity](https://developers.google.com/identity/gsi/web/guides/verify-google-id-token) · [Política de APIM](https://learn.microsoft.com/en-us/azure/api-management/validate-jwt-policy)
- La política sobrescribe `X-User-Id` con el sujeto del token validado y `X-User-Email` con su correo. Las aplicaciones cliente envían su token, y los backends leen esos encabezados detrás de la frontera de confianza. Ayuda y legales heredan autenticación de APIM aunque sus controladores de backend no requieran identidad.
- En las rutas administrativas, APIM comprueba el correo derivado del token contra una lista configurada, devuelve `403` si no corresponde e inyecta `X-User-Role: admin` al autorizar. Desde el 13 de noviembre de 2026 la regla cubre el cambio de estado de postulaciones, las tres escrituras de ofertas (`POST /jobs`, `PUT /jobs/{id}`, `DELETE /jobs/{id}`) y las tres operaciones de plantillas de Notificaciones, en la API principal y en la API por recurso. Falta comprobarla con un token de administrador y otro sin ese rol.
- Las operaciones de plantillas de Notificaciones, IA de CVs (`generate-text`, `generate-cv`), Brecha (`evaluate`, `recommendations`) y `POST /jobs/refresh` se registraron después del inventario de [apim-rutas.json](../contratos/apim-rutas.json). Sin token responden `401`, lo que confirma que APIM las reconoce.

Como antecedente, Android obtuvo `401` con una audiencia diferente a la del cliente OAuth configurado. Con la audiencia de CI, `GET /api/v1/cvs` y `GET /api/v1/jobs` respondieron `200`. El antecedente se limita a esas solicitudes y a la sesión registrada.

## APIM a App Service

`authentication-certificate` en la política de API referencia `cvexpert-client-cert` para presentar el certificado cliente al backend. La consulta del recurso de APIM no mostró un vínculo a Key Vault para ese certificado. Cuando se usa un certificado de Key Vault, la política puede referenciar el identificador del certificado y la identidad de APIM debe tener acceso. Las credenciales de Firebase y otros servicios siguen la configuración de su backend. [Política de certificado cliente](https://learn.microsoft.com/en-us/azure/api-management/authentication-certificate-policy)

| Servicio | Configuración de App Service consultada | Validación pendiente |
| --- | --- | --- |
| Usuarios | HTTPS, certificado cliente habilitado y modo `Required` con excepción `/actuator/health`. La aplicación valida la huella de `X-ARR-ClientCert`. Prueba directa (13 nov 2026): sin certificado `403`, con certificado autofirmado ajeno `403` aunque se envíen `X-User-Id` y `X-User-Email`, `X-ARR-ClientCert` falso `403`, `/actuator/health` `200` | Probar una operación con identidad en el flujo real |
| CVs | HTTPS, certificado cliente habilitado y modo `Required` con excepción `/health` (8 nov 2026). La aplicación valida la huella de `X-ARR-ClientCert`. Prueba directa: sin certificado `403`, con certificado autofirmado ajeno `403`, `/health` `200` | Probar una operación con identidad en el flujo real |
| Ofertas y postulaciones | Destino registrado en APIM. La aplicación valida vigencia y huella de certificado reenviado. Su App Service no apareció en el inventario de la suscripción consultada | Responsable de Ofertas debe facilitar la configuración efectiva de App Service y la prueba TLS |
| Brecha y cursos | HTTPS, certificado cliente habilitado y modo `Required`, sin exclusiones registradas | Verificar la huella activa y el paso de certificado e identidad en el flujo real |
| Notificaciones | HTTPS, certificado cliente habilitado y modo `Required` con excepción `/health` | Confirmar el certificado permitido por la aplicación y probar una operación con identidad |

Los App Services visibles tienen acceso de red pública habilitado. En los backends que usan `X-ARR-ClientCert`, App Service debe derivar ese encabezado del certificado recibido en TLS. Un valor HTTP introducido por el cliente no demuestra posesión de la clave. El ID token autentica al usuario ante APIM. El certificado autentica la conexión del gateway al backend.

## Reproducir el inventario

Con acceso de lectura a Azure, consulte la API `cv-api` con `az apim api operation list` y contraste `method` y `urlTemplate` con el prefijo de `az apim api show`. Revise la política de API y operación en ARM para confirmar el destino y los controles heredados. Publique únicamente los campos de trazabilidad de [apim-rutas.json](../contratos/apim-rutas.json).

## Evidencia que falta

- **Operación de APIM.** Facilitar una traza depurada de una solicitud aceptada por dominio que muestre revisión, operación, política de identidad y backend efectivo. Repetir con token vencido, audiencia ajena y cabeceras de identidad del cliente. Comprobar roles una vez corregidas las escrituras de ofertas.
- **Administración de App Service y responsables de backend.** Verificar TLS y huellas sin exponer material privado. Probar rechazo de acceso directo sin certificado y con certificado ajeno, incluida la configuración efectiva de CVs y Ofertas.
- **Responsable del entorno de prueba.** Proporcionar cuentas y credenciales vigentes para la audiencia de ensayo y un entorno aislado para pruebas de escritura. El resultado observado por Newman se detalla en el [estado de entrega](estado-entrega.md).
