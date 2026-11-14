# APIM

Todo el tráfico de la web y de Android entra por **Azure API Management** (plan
Consumption):

```
https://<gateway de APIM>/api/v1/<ruta del contrato>
```

APIM valida el token de Google, agrega la identidad y reenvía la llamada al microservicio
presentando el certificado de cliente. Ningún backend recibe el token de Google. Los
nombres de los recursos de Azure no van aquí porque el repo es público.

## Mapa de rutas

| Ruta pública (`/api/v1/...`) | Backend | API por recurso |
|---|---|---|
| `/profiles/{id}`, `/profiles/{id}/sessions`, `/profiles/{id}/export` | Usuarios | `perfiles` |
| `/legal/terms`, `/legal/privacy` | Usuarios | `legales` |
| `/help` | Usuarios | `ayuda` |
| `/cvs`, `/cvs/{id}`, `/cvs/ai/expand-experience`, `/cvs/ai/translate-experience`, `/cvs/ai/generate-text`, `/cvs/ai/generate-cv`, `/cvs/photos` (multipart) | CVs | `curriculos` |
| `/templates`, `/templates/{id}` | CVs | `plantillas` |
| `/jobs`, `/jobs/{id}`, `/jobs/refresh` | Ofertas y Postulaciones | `ofertas` |
| `/applications`, `/applications/{id}` | Ofertas y Postulaciones | `postulaciones` |
| `/alerts` | Ofertas y Postulaciones | `alertas` |
| `/admin/applications/{id}/status` | Ofertas y Postulaciones | `administracion` |
| `/skills-gap`, `/skills-gap/input`, `/skills-gap/evaluate`, `/skills-gap/recommendations`, `/courses` | Brecha y Cursos | `brecha-habilidades` |
| `/notifications/...` (8 operaciones) | Notificaciones | `notificaciones` |
| `/notifications/templates`, `/notifications/templates/{type}/{language}` (solo admin) | Notificaciones | `notificaciones` |

APIM le quita `/api/v1` a la ruta antes de reenviarla: `/api/v1/cvs/1` llega al backend
como `/cvs/1`.

**Dos lugares por operación.** Los clientes usan la API `cv-api` (sufijo `api/v1`). Cada
operación también está copiada en su API por recurso (sufijo `api/v1/<api>`), que existe
para ordenar el APIM por módulo. Una operación nueva va en los dos.

## Qué hace APIM en cada llamada

1. **CORS.** Permite cualquier origen y los métodos `GET`, `POST`, `PUT`, `DELETE`,
   `PATCH` y `OPTIONS`, con cualquier encabezado. Expone `X-Data-Mode` al navegador.
2. **Token de Google.** `validate-jwt` contra `accounts.google.com`, con el client ID de
   Google como audiencia. Sin token válido responde 401 y la llamada no llega al backend.
   Los `OPTIONS` no se validan.
3. **Identidad.** Pone `X-User-Id` (claim `sub`) y `X-User-Email` (claim `email`). Si el
   cliente los manda, los pisa. El cliente nunca debe mandarlos.
4. **Rol.** Borra cualquier `X-User-Role` que mande el cliente. Solo las rutas de admin
   (`/admin/applications/{id}/status`, `/notifications/templates/...` y las escrituras de
   ofertas `POST /jobs`, `PUT /jobs/{id}` y `DELETE /jobs/{id}`) mandan
   `X-User-Role: admin`, y solo si el correo está en la lista de administradores de APIM; si
   no está, responde 403 sin llamar al backend.
5. **Certificado.** Presenta el certificado de cliente al backend (ver
   [certificado-apim.md](certificado-apim.md)).

APIM no cachea respuestas, no reescribe códigos de estado ni cuerpos de error, y ninguna
política valida el tipo de contenido ni lee el cuerpo: JSON y `multipart/form-data` pasan
igual. El plan Consumption acepta cuerpos de hasta 1 GiB; el tope real lo pone cada
backend. La tabla de límites de Azure indica 30 s de duración total en Consumption, pero el
13 de noviembre de 2026 una petición de prueba de 45 s terminó con 200, así que ese tope no
se está aplicando. El timeout hacia el backend es de 180 s en `/cvs/ai/generate-cv`,
120 s en el resto de `/cvs/ai/*` y en `POST /jobs/refresh` (hace varias búsquedas en
JSearch), 60 s en `POST /cvs/photos`, y el de defecto en las demás.

Las fotos de los currículums no pasan por APIM al leerse: CVs las sube a un contenedor de
Azure Storage con lectura anónima por blob (no se puede listar) y la web las pide directo
a Storage. Ese servicio tiene su propia regla de CORS (solo `GET`, cualquier origen), que el
generador de PDF necesita para leer los bytes de la imagen.

**Errores del gateway.** Cuando el problema es de APIM y no del backend, todas las APIs de
CVExpert responden JSON con un `code` propio (con CORS, para que el navegador lo lea):

| Caso | Respuesta |
|---|---|
| El backend no responde dentro del timeout | `504` `{"code":"GATEWAY_TIMEOUT"}` |
| APIM no puede conectar con el backend | `503` `{"code":"SERVICE_UNAVAILABLE"}` |
| El backend devuelve 502, 503 o 504 sin JSON (por ejemplo, la página de App Service mientras reinicia) | `503` `{"code":"SERVICE_UNAVAILABLE"}` |

Los errores que el backend devuelve en JSON (como el `503` del importador de Ofertas) pasan
sin cambios. Sin esta regla, un timeout salía como `500` `"Internal server error"`.

**Agregar un administrador** implica cambiar dos lugares: `ADMIN_EMAILS` del App Service
de Usuarios y la lista de administradores de APIM (un named value).

## Cómo agregar una operación

1. Si el microservicio es nuevo, crear un **backend** en APIM con la URL del App Service.
2. Crear la operación en `cv-api` con el método y la ruta exactos del contrato.
3. Ponerle esta política (cambiando `backend-id`):

   ```xml
   <policies>
     <inbound>
       <base />
       <set-header name="X-User-Role" exists-action="delete" />
       <set-backend-service backend-id="cvs" />
     </inbound>
     <backend><base /></backend>
     <outbound><base /></outbound>
     <on-error><base /></on-error>
   </policies>
   ```

   `<base />` trae CORS, el token, la identidad y el certificado desde la política de la API.
4. Copiar la operación y su política en la API por recurso que le corresponde.
5. Si usa un método nuevo en el navegador, agregarlo a `allowed-methods` de CORS en la
   política de cada API.
6. Probarla **sin token**: tiene que responder **401**. Un 404 significa que APIM no la
   encontró (ruta mal escrita o choque de sufijos). Los cambios tardan unos segundos en
   aplicarse.

## Regla de sufijos

APIM elige la API con el sufijo más largo que coincide. Por eso **el sufijo de una API por
recurso nunca puede ser igual al primer segmento de una ruta de `cv-api`** (`cvs`, `legal`,
`admin`, `jobs`, `profiles`, `notifications`, etc.).

Del 2 al 7 de noviembre las APIs por recurso de CVs, legales y admin tenían los sufijos
`api/v1/cvs`, `api/v1/legal` y `api/v1/admin`. Se tragaban esas rutas de `cv-api` y
respondían 404. Se renombraron a `curriculos`, `legales` y `administracion`.
