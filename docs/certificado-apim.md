# Certificado de cliente de APIM

Cada backend acepta solo llamadas que vienen de APIM. APIM presenta un certificado de
cliente y el backend lo valida. La huella del certificado y el respaldo del certificado se
piden por el canal privado del equipo; no van en este repo.

## Qué configurar en cada microservicio

1. **App Service → Configuración → Certificados de cliente:** modo **Required** y la ruta
   de health en las exclusiones (por ejemplo `/actuator/health` o `/health`). Sin la
   exclusión, el health check de Azure falla.
2. **Variable de entorno** `APIM_CERT_THUMBPRINTS` con la huella. Acepta varias separadas
   por coma, para poder rotar el certificado sin cortar el servicio.
3. **En el código:** App Service termina el TLS antes de la aplicación y reenvía el
   certificado en el encabezado `X-ARR-ClientCert` (DER en base64). Hay que:
   - decodificarlo y leerlo como X.509;
   - revisar que esté vigente;
   - calcular el SHA-1 del DER y compararlo con las huellas, sin importar mayúsculas ni
     `:`;
   - si no coincide, responder 403.

   Si la variable está vacía no se exige nada, así se puede correr en local. Ejemplo en Java:
   [`ApimCertificateFilter`](https://github.com/SoftwareDesignTEC/cvexpert-ms-usuarios/blob/main/src/main/java/cr/ac/tec/cvexpert/usuarios/config/ApimCertificateFilter.java).
4. **Probar:** la URL directa del App Service tiene que responder 403, y la ruta de health
   200.

## Estado (10 nov 2026)

| Servicio | Certificado exigido |
|---|---|
| Usuarios | Sí |
| Brecha y Cursos | Sí |
| Notificaciones | Sí |
| Ofertas y Postulaciones | Sí |
| CVs | Sí |

## Rotarlo

1. Generar el certificado nuevo y subirlo a APIM con otro nombre.
2. Agregar su huella a `APIM_CERT_THUMBPRINTS` de cada servicio, junto a la vieja.
3. Cambiar `authentication-certificate` en las políticas de APIM al certificado nuevo.
4. Quitar la huella vieja de cada servicio.
