# Matriz de trazabilidad — Fase II

El [CSV](../contratos/matriz-trazabilidad.csv) vincula cada operación con la revisión, el código, las pruebas de origen, los parámetros, las respuestas de error y la solicitud exacta de Postman.

Las rutas públicas corresponden al [inventario de APIM](../contratos/apim-rutas.json). Una ruta registrada identifica la configuración del gateway. El [estado de entrega](estado-entrega.md) identifica las llamadas ejecutadas. Los cambios de contrato y de implementación se detallan en la [auditoría](auditoria.md).

## Usuarios (7)

[OpenAPI](../contratos/usuarios.openapi.yaml) · [Origen fijado](https://github.com/SoftwareDesignTEC/cvexpert-ms-usuarios/blob/35adbede8c1492941b0d2cda42460fe45f8ccd2c/openapi.yaml) · [Código](https://github.com/SoftwareDesignTEC/cvexpert-ms-usuarios/tree/35adbede8c1492941b0d2cda42460fe45f8ccd2c/src/main/java/cr/ac/tec/cvexpert/usuarios/controller) · [Pruebas de origen](https://github.com/SoftwareDesignTEC/cvexpert-ms-usuarios/tree/35adbede8c1492941b0d2cda42460fe45f8ccd2c/src/test/java/cr/ac/tec/cvexpert/usuarios)

| Operación interna | Ruta APIM registrada | Permisos | Solicitud | Respuesta de éxito | Carpeta Postman |
| --- | --- | --- | --- | --- | --- |
| `GET /profiles/{id}` | /api/v1/profiles/{id} | Identidad propia y propiedad del recurso cuando aplica | — | 200 UserProfile | Perfil y alertas |
| `PUT /profiles/{id}` | /api/v1/profiles/{id} | Identidad propia y propiedad del recurso cuando aplica | UpdateProfileRequest | 200 UserProfile | Perfil y alertas |
| `GET /profiles/{id}/sessions` | /api/v1/profiles/{id}/sessions | Identidad propia y propiedad del recurso cuando aplica | — | 200 SessionPage | Perfil y alertas |
| `GET /profiles/{id}/export` | /api/v1/profiles/{id}/export | Identidad propia y propiedad del recurso cuando aplica | — | 200 DataExport | Perfil y alertas |
| `GET /legal/privacy` | /api/v1/legal/privacy | Consulta general | — | 200 LegalDocument | Lecturas |
| `GET /legal/terms` | /api/v1/legal/terms | Consulta general | — | 200 LegalDocument | Lecturas |
| `GET /help` | /api/v1/help | Consulta general | — | 200 HelpContactsResponse | Lecturas |

## CVs y plantillas (9)

[OpenAPI](../contratos/cvs.openapi.yaml) · [Origen fijado](https://github.com/SoftwareDesignTEC/cvexpert-ms-cvs/blob/db9ce968b7c937b280f9cb07384939499841f60b/docs/openapi.yaml) · [Código](https://github.com/SoftwareDesignTEC/cvexpert-ms-cvs/tree/db9ce968b7c937b280f9cb07384939499841f60b/app/api/routers) · [Pruebas de origen](https://github.com/SoftwareDesignTEC/cvexpert-ms-cvs/tree/db9ce968b7c937b280f9cb07384939499841f60b/tests)

| Operación interna | Ruta APIM registrada | Permisos | Solicitud | Respuesta de éxito | Carpeta Postman |
| --- | --- | --- | --- | --- | --- |
| `GET /cvs` | /api/v1/cvs | Identidad propia y propiedad del recurso cuando aplica | — | 200 PaginatedCvs | Lecturas |
| `POST /cvs` | /api/v1/cvs | Identidad propia y propiedad del recurso cuando aplica | CvInput | 201 Cv | Ciclo de CV |
| `GET /cvs/{id}` | /api/v1/cvs/{id} | Identidad propia y propiedad del recurso cuando aplica | — | 200 Cv | Ciclo de CV |
| `PUT /cvs/{id}` | /api/v1/cvs/{id} | Identidad propia y propiedad del recurso cuando aplica | CvInput | 200 Cv | Ciclo de CV |
| `DELETE /cvs/{id}` | /api/v1/cvs/{id} | Identidad propia y propiedad del recurso cuando aplica | — | 204 — | Ciclo de CV |
| `GET /templates` | /api/v1/templates | Consulta general | — | 200 PaginatedTemplates | Lecturas |
| `GET /templates/{id}` | /api/v1/templates/{id} | Consulta general | — | 200 Template | Lecturas |
| `POST /cvs/ai/expand-experience` | /api/v1/cvs/ai/expand-experience | Identidad propia y propiedad del recurso cuando aplica | ExpandExperienceRequest | 200 ExpandExperienceResponse | Experiencia laboral |
| `POST /cvs/ai/translate-experience` | /api/v1/cvs/ai/translate-experience | Identidad propia y propiedad del recurso cuando aplica | TranslateExperienceRequest | 200 TranslateExperienceResponse | Experiencia laboral |

## Ofertas y postulaciones (13)

[OpenAPI](../contratos/ofertas-postulaciones.openapi.yaml) · [Origen fijado](https://github.com/SoftwareDesignTEC/cvexpert-ms-ofertas-postulaciones/blob/822c9ebe84e3a75671a702a30cd3978c92d0337b/docs/openapi.yaml) · [Código](https://github.com/SoftwareDesignTEC/cvexpert-ms-ofertas-postulaciones/tree/822c9ebe84e3a75671a702a30cd3978c92d0337b/src/main/java/com/cvexpert/ofertas/adapter/in/web) · [Pruebas de origen](https://github.com/SoftwareDesignTEC/cvexpert-ms-ofertas-postulaciones/tree/822c9ebe84e3a75671a702a30cd3978c92d0337b/src/test/java/com/cvexpert/ofertas/adapter/in/web)

| Operación interna | Ruta APIM registrada | Permisos | Solicitud | Respuesta de éxito | Carpeta Postman |
| --- | --- | --- | --- | --- | --- |
| `GET /jobs` | /api/v1/jobs | Consulta general | — | 200 JobOfferPage | Lecturas |
| `POST /jobs` | /api/v1/jobs | Administrador | JobOfferInput | 201 JobOffer | Administración de ofertas |
| `GET /jobs/{id}` | /api/v1/jobs/{id} | Consulta general | — | 200 JobOffer | Lecturas |
| `PUT /jobs/{id}` | /api/v1/jobs/{id} | Administrador | JobOfferInput | 200 JobOffer | Administración de ofertas |
| `DELETE /jobs/{id}` | /api/v1/jobs/{id} | Administrador | — | 204 — | Administración de ofertas |
| `GET /applications` | /api/v1/applications | Identidad propia y propiedad del recurso cuando aplica | — | 200 JobApplicationPage | Lecturas |
| `POST /applications` | /api/v1/applications | Identidad propia y propiedad del recurso cuando aplica | CreateApplicationRequest | 201 JobApplication | Ciclo de postulaciones |
| `GET /applications/{id}` | /api/v1/applications/{id} | Identidad propia y propiedad del recurso cuando aplica | — | 200 JobApplication | Ciclo de postulaciones |
| `PUT /applications/{id}` | /api/v1/applications/{id} | Identidad propia y propiedad del recurso cuando aplica | UpdateStatusRequest | 200 JobApplication | Ciclo de postulaciones |
| `DELETE /applications/{id}` | /api/v1/applications/{id} | Identidad propia y propiedad del recurso cuando aplica | — | 204 — | Ciclo de postulaciones |
| `PUT /admin/applications/{id}/status` | /api/v1/admin/applications/{id}/status | Administrador | UpdateStatusRequest | 200 JobApplication | Ciclo de postulaciones |
| `GET /alerts` | /api/v1/alerts | Usuario autenticado con configuración propia | — | 200 AlertSettings | Lecturas |
| `PUT /alerts` | /api/v1/alerts | Usuario autenticado con configuración propia | AlertSettingsInput | 200 AlertSettings | Perfil y alertas |

## Brecha y cursos (4)

[OpenAPI](../contratos/brecha-cursos.openapi.yaml) · [Origen fijado](https://github.com/SoftwareDesignTEC/cvexpert-ms-brecha-cursos/blob/f08d8a37f33435456849a76b1afac26df77a1865/openapi.yaml) · [Código](https://github.com/SoftwareDesignTEC/cvexpert-ms-brecha-cursos/tree/f08d8a37f33435456849a76b1afac26df77a1865/src) · [Pruebas de origen](https://github.com/SoftwareDesignTEC/cvexpert-ms-brecha-cursos/tree/f08d8a37f33435456849a76b1afac26df77a1865/test)

| Operación interna | Ruta APIM registrada | Permisos | Solicitud | Respuesta de éxito | Carpeta Postman |
| --- | --- | --- | --- | --- | --- |
| `GET /health` | — | Sonda local | — | 200 object | Backend directo - Brecha |
| `GET /skills-gap` | /api/v1/skills-gap | Dueño de instantánea | — | 200 SkillsGapPage | Instantánea y brecha |
| `GET /courses` | /api/v1/courses | Consulta de catálogo | — | 200 CoursesPage | Lecturas |
| `PUT /skills-gap/input` | /api/v1/skills-gap/input | Dueño de instantánea | SkillsGapInput | 204 — | Instantánea y brecha |

## Notificaciones (12)

[OpenAPI](../contratos/notificaciones.openapi.yaml) · [Origen fijado](https://github.com/SoftwareDesignTEC/cvexpert-ms-notificaciones/blob/501cd20d9c0d70ac6baa9340dac669bf527a1295/docs/contratos/openapi.yaml) · [Código](https://github.com/SoftwareDesignTEC/cvexpert-ms-notificaciones/tree/501cd20d9c0d70ac6baa9340dac669bf527a1295/src/Notificaciones.Api) · [Pruebas de origen](https://github.com/SoftwareDesignTEC/cvexpert-ms-notificaciones/tree/501cd20d9c0d70ac6baa9340dac669bf527a1295/tests/Notificaciones.Tests)

| Operación interna | Ruta APIM registrada | Permisos | Solicitud | Respuesta de éxito | Carpeta Postman |
| --- | --- | --- | --- | --- | --- |
| `PUT /notifications/directory/me` | /api/v1/notifications/directory/me | Usuario autenticado con datos propios | DirectoryUpdate | 200 DirectoryEntry | Directorio y dispositivos |
| `POST /notifications/devices` | /api/v1/notifications/devices | Usuario autenticado con datos propios | DeviceRegistration | 201 Device, 200 Device | Directorio y dispositivos |
| `DELETE /notifications/devices/{token}` | /api/v1/notifications/devices/{token} | Usuario autenticado con datos propios | — | 204 — | Directorio y dispositivos |
| `GET /notifications` | /api/v1/notifications | Usuario autenticado con datos propios | — | 200 PagedNotifications | Lecturas |
| `GET /notifications/unread-count` | /api/v1/notifications/unread-count | Usuario autenticado con datos propios | — | 200 UnreadCount | Lecturas |
| `PATCH /notifications/{id}/read` | /api/v1/notifications/{id}/read | Usuario autenticado con datos propios | — | 200 Notification | Lectura de avisos |
| `POST /notifications/read-all` | /api/v1/notifications/read-all | Usuario autenticado con datos propios | — | 204 — | Lectura de avisos |
| `POST /notifications/hub/negotiate` | /api/v1/notifications/hub/negotiate | Usuario autenticado con datos propios | — | 200 SignalRNegotiateResponse | Lecturas |
| `GET /notifications/templates` | — | Administrador | — | 200 array de Template | Administración de plantillas |
| `GET /notifications/templates/{type}/{language}` | — | Administrador | — | 200 Template | Administración de plantillas |
| `PUT /notifications/templates/{type}/{language}` | — | Administrador | TemplateUpdate | 200 Template | Administración de plantillas |
| `GET /health` | — | Sonda local | — | 200 Health | Backend directo - Notificaciones |
