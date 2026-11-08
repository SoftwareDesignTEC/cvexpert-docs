# Matriz de trazabilidad de contratos — Fase II

Fuente: cinco contratos OpenAPI de los repositorios del equipo, revisados el 8 de noviembre de 2026. **Estado de cada ruta APIM por verificar.**

## Usuarios (7)

| Método | Ruta del contrato | Respuesta de éxito | Prueba |
|---|---|---|---|
| `GET` | `/profiles/{id}` | `200` | Definida; ejecución pendiente |
| `PUT` | `/profiles/{id}` | `200` | Definida; ejecución pendiente |
| `GET` | `/profiles/{id}/sessions` | `200` | Definida; ejecución pendiente |
| `GET` | `/profiles/{id}/export` | `200` | Definida; ejecución pendiente |
| `GET` | `/legal/privacy` | `200` | Definida; ejecución pendiente |
| `GET` | `/legal/terms` | `200` | Definida; ejecución pendiente |
| `GET` | `/help` | `200` | Definida; ejecución pendiente |

## CVs y plantillas (9)

| Método | Ruta del contrato | Respuesta de éxito | Prueba |
|---|---|---|---|
| `GET` | `/cvs` | `200` | Definida; ejecución pendiente |
| `POST` | `/cvs` | `201` | Definida; ejecución pendiente |
| `GET` | `/cvs/{id}` | `200` | Definida; ejecución pendiente |
| `PUT` | `/cvs/{id}` | `200` | Definida; ejecución pendiente |
| `DELETE` | `/cvs/{id}` | `204` | Definida; ejecución pendiente |
| `GET` | `/templates` | `200` | Definida; ejecución pendiente |
| `GET` | `/templates/{id}` | `200` | Definida; ejecución pendiente |
| `POST` | `/cvs/ai/expand-experience` | `200` | Definida; ejecución pendiente |
| `POST` | `/cvs/ai/translate-experience` | `200` | Definida; ejecución pendiente |

## Ofertas y postulaciones (13)

| Método | Ruta del contrato | Respuesta de éxito | Prueba |
|---|---|---|---|
| `GET` | `/jobs` | `200` | Definida; ejecución pendiente |
| `POST` | `/jobs` | `201` | Definida; ejecución pendiente |
| `GET` | `/jobs/{id}` | `200` | Definida; ejecución pendiente |
| `PUT` | `/jobs/{id}` | `200` | Definida; ejecución pendiente |
| `DELETE` | `/jobs/{id}` | `204` | Definida; ejecución pendiente |
| `GET` | `/applications` | `200` | Definida; ejecución pendiente |
| `POST` | `/applications` | `201` | Definida; ejecución pendiente |
| `GET` | `/applications/{id}` | `200` | Definida; ejecución pendiente |
| `PUT` | `/applications/{id}` | `200` | Definida; ejecución pendiente |
| `DELETE` | `/applications/{id}` | `204` | Definida; ejecución pendiente |
| `PUT` | `/admin/applications/{id}/status` | `200` | Definida; ejecución pendiente |
| `GET` | `/alerts` | `200` | Definida; ejecución pendiente |
| `PUT` | `/alerts` | `200` | Definida; ejecución pendiente |

## Brecha y cursos (4)

| Método | Ruta del contrato | Respuesta de éxito | Prueba |
|---|---|---|---|
| `GET` | `/health` | `200` | Definida; ejecución pendiente |
| `GET` | `/skills-gap` | `200` | Definida; ejecución pendiente |
| `GET` | `/courses` | `200` | Definida; ejecución pendiente |
| `PUT` | `/skills-gap/input` | `204` | Definida; ejecución pendiente |

## Notificaciones (12)

| Método | Ruta del contrato | Respuesta de éxito | Prueba |
|---|---|---|---|
| `PUT` | `/notifications/directory/me` | `200` | Definida; ejecución pendiente |
| `POST` | `/notifications/devices` | `200,201` | Definida; ejecución pendiente |
| `DELETE` | `/notifications/devices/{token}` | `204` | Definida; ejecución pendiente |
| `GET` | `/notifications` | `200` | Definida; ejecución pendiente |
| `GET` | `/notifications/unread-count` | `200` | Definida; ejecución pendiente |
| `PATCH` | `/notifications/{id}/read` | `200` | Definida; ejecución pendiente |
| `POST` | `/notifications/read-all` | `204` | Definida; ejecución pendiente |
| `POST` | `/notifications/hub/negotiate` | `200` | Definida; ejecución pendiente |
| `GET` | `/notifications/templates` | `200` | Definida; ejecución pendiente |
| `GET` | `/notifications/templates/{type}/{language}` | `200` | Definida; ejecución pendiente |
| `PUT` | `/notifications/templates/{type}/{language}` | `200` | Definida; ejecución pendiente |
| `GET` | `/health` | `200` | Definida; ejecución pendiente |

## Observaciones críticas

- Los 45 paths son rutas del contrato **sin prefijo público**. En Android se observaron rutas como `/api/v1/jobs` y `/api/v1/cvs`; debe validarse una por una la ruta APIM (incluidas salud/admin).
- `GET /health` aparece en Brecha y Notificaciones, pero **no se presume publicado** en APIM.
- `GET /skills-gap` puede responder `409 SKILLS_INPUT_REQUIRED` si faltan habilidades; esta es una precondición del flujo, no una alternativa de éxito a `200`.
- `GET /cvs` devolvió `200` con lista vacía en la prueba Android observada, que es un resultado normal.
- Los endpoints de administración necesitan validar el rol efectivo en APIM y deben probarse con usuarios autorizados y no autorizados.
- Los cuerpos JSON indicados por la colección inicial son **marcadores de posición**; enriquecedlos con el sincronizador antes de afirmar cobertura funcional.
