# Seguridad de Azure API Management — verificación requerida

## Diseño esperado por el proyecto

1. Cliente web / Android presenta un ID token de Google a APIM mediante `Authorization: Bearer <id_token>`.
2. APIM valida firma, emisor, **audiencia** (`aud`), expiración y políticas aplicables.
3. APIM deriva y **sobrescribe** los encabezados internos `X-User-Id` y `X-User-Email` (y `X-User-Role` para operaciones de administración, previa verificación de rol). El cliente no debe enviarlos.
4. APIM enruta el path público al backend correspondiente. Cada backend debe comprobar la identidad/certificado de cliente presentado por APIM según la arquitectura acordada.
5. Las credenciales de Microsoft Azure, Google o Firebase, llaves privadas y tokens reales no se publican en repositorios ni reportes.

## Evidencia que debe proporcionar el responsable de APIM

- Exportación o extractos redactados de las políticas aplicadas en **cada API/operación**, incluidos `validate-jwt` (audiencias aceptadas), `set-header`, autorización admin, y transformaciones de rutas.
- Inventario de rutas públicas y su backend real con estados de despliegue, separando operaciones no públicas (`/health`, internas).
- Evidencia de validación del certificado entre gateway y backends, sin material secreto. La sola presencia de `X-ARR-ClientCert` no constituye prueba de mTLS extremo a extremo.
- Prueba negativa de un token vencido o con `aud` incorrecto; prueba negativa de acceso directo al backend sin identidad autorizada; prueba de usuario sin rol para ruta admin.
- Referencia de Key Vault y modo de acceso a certificados y secretos, sin valores confidenciales.

## Lección confirmada en Android

Se observó que un token de Google no vencido fue rechazado con 401 cuando su `aud` no coincidía con la configuración esperada; al utilizar el Google Web Client ID de CI, dos rutas devolvieron 200. **Es un indicio fuerte de error de audiencia**, aunque la traza específica de `validate-jwt` aún no fue entregada.

> No deshabilitar validaciones JWT o certificados para hacer pasar las pruebas.
