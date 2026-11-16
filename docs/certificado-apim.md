# Certificado de cliente de APIM

Cada backend acepta solo llamadas que vienen de APIM. APIM presenta un certificado de
cliente y el backend lo valida. La huella del certificado y el respaldo del certificado se
piden por el canal privado del equipo; no van en este repo.

## Qué configurar en cada microservicio

La [tabla por servicio de Seguridad](seguridad.md#3-certificado-de-cliente-de-apim-hacia-los-backends)
identifica el componente, la variable, las validaciones y las exclusiones de cada backend.
La configuración de la aplicación y la de App Service son controles distintos.

1. **App Service → Configuración → Certificados de cliente:** confirmar el modo
   **Required** y las exclusiones efectivas del servicio. No agregar una exclusión de
   health de forma universal: Brecha excluye `/health` en la aplicación, pero el informe
   de App Service no registra exclusiones. Usuarios y Ofertas usan `/actuator/health`;
   CVs y Notificaciones usan `/health`, según los controles indicados en la tabla.
2. **Variable de huella:** Usuarios, CVs y Brecha usan `APIM_CERT_THUMBPRINTS`;
   Ofertas usa `APIM_CERT_THUMBPRINT`, y Notificaciones `Apim__CertificateThumbprint`
   como App Setting. Confirmar el formato y el soporte de varias huellas del servicio
   antes de configurar una rotación; no intercambiar estos nombres.
3. **En el código:** App Service termina el TLS antes de la aplicación y reenvía el
   certificado en el encabezado `X-ARR-ClientCert` (DER en base64). Hay que:
   - decodificarlo y leerlo como X.509;
   - revisar que esté vigente cuando el componente implemente ese control;
   - calcular el SHA-1 del DER y compararlo con las huellas, sin importar mayúsculas ni
     `:`;
   - si no coincide, responder 403.

   El middleware auditado de CVs solo compara la huella, sin comprobar vigencia.
   Brecha falla cerrado si falta configuración; su bypass local explícito no funciona
   en Azure ni autoriza los flujos de identidad. En los demás servicios, una variable
   vacía desactiva el chequeo de la aplicación según el corte documentado: no es una
   configuración válida para proteger producción. Ejemplo en Java:
   [`ApimCertificateFilter`](https://github.com/SoftwareDesignTEC/cvexpert-ms-usuarios/blob/7cb84d9ae5416569adb93d161a4a7b3cd84c1269/src/main/java/cr/ac/tec/cvexpert/usuarios/config/ApimCertificateFilter.java) de la rama del PR #2, pendiente de integrar en el main del corte auditado.
4. **Probar en ensayo autorizado:** comprobar el rechazo de acceso directo sin certificado
   válido (403 o rechazo TLS según la frontera). Esperar 200 en health solo cuando su
   acceso esté permitido por los controles efectivos de aplicación y App Service.

## Estado (10 nov 2026)

Este registro es histórico; no sustituye la comprobación de configuración efectiva actual
ni las diferencias de implementación de la tabla de Seguridad.

| Servicio | Certificado exigido |
|---|---|
| Usuarios | Sí |
| Brecha y Cursos | Sí |
| Notificaciones | Sí |
| Ofertas y Postulaciones | Sí |
| CVs | Sí |

## Rotarlo

1. Generar el certificado nuevo y subirlo a APIM con otro nombre.
2. Configurar su huella con la variable propia de cada servicio indicada en la tabla.
   Mantener ambas huellas solo si su implementación lo admite; en caso contrario,
   planificar un cambio coordinado para evitar interrupciones.
3. Cambiar `authentication-certificate` en las políticas de APIM al certificado nuevo.
4. Quitar la huella vieja de cada servicio.
