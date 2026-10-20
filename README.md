# CVExpert Fase II · Contratos consolidados

Repositorio de integración documental para los **cinco microservicios** de CVExpert. 
**Estado: consolidación preliminar, pendiente de revisión por los responsables de cada servicio.** 
La presencia de una ruta en OpenAPI no equivale a que el endpoint esté implementado o publicado en APIM.

## Contratos REST / OpenAPI

| Dominio | Contrato importado | Origen |
|---|---|---|
| Usuarios | [`contratos/usuarios.yaml`](contratos/usuarios.yaml) | `cvexpert-ms-usuarios` (`main`) |
| CVs e IA | [`contratos/cvs.yaml`](contratos/cvs.yaml) | `cvexpert-ms-cvs` (`main`) |
| Ofertas y postulaciones | [`contratos/ofertas-postulaciones.yaml`](contratos/ofertas-postulaciones.yaml) | `cvexpert-ms-ofertas-postulaciones` (`main`) |
| Brecha de habilidades y cursos | [`contratos/brecha-cursos.yaml`](contratos/brecha-cursos.yaml) | `cvexpert-ms-brecha-cursos` (`develop`) |
| Notificaciones | [`contratos/notificaciones.yaml`](contratos/notificaciones.yaml) | `cvexpert-ms-notificaciones` (`docs/contratos`, aún no fusionada a `main`) |

## Eventos asíncronos

- **JSON Schema:** [`eventos/evento-notificacion.schema.json`](eventos/evento-notificacion.schema.json)
- **Guía original de publicación/consumo, incluida para consulta:** [`eventos/README-origen-notificaciones.md`](eventos/README-origen-notificaciones.md)

Este esquema define los eventos publicados en la cola `notificaciones-eventos`, con `schemaVersion`, `eventId`, `type`, `userId`, `occurredAt`, `source` y `data`. Los eventos contemplados son `application.status_changed`, `cv.generated`, `job.new` y `course.recommended`. **Es un contrato propuesto en una rama de Notificaciones, no una implementación validada extremo a extremo.**

## Lecturas obligatorias para integración

- [Fuentes, ramas, commits y procedimiento de actualización](docs/fuentes.md).
- [Revisión transversal: diferencias, riesgos y decisiones pendientes](docs/revision-integracion.md).
- [Validación automatizada mínima de archivos y referencias locales](docs/validacion.md).

## Qué no demuestra esta consolidación

No certifica que las rutas estén desplegadas, que se haya configurado la autenticación Google/APIM, los certificados cliente, la conexión de SignalR, los eventos Service Bus o los clientes web/Android. Cada responsable debe validar la paridad contrato↔implementación y aprobar los cambios vía PR.

**No guardar tokens, contraseñas, claves, certificados privados, URLs firmadas o conexiones de bases de datos en esta documentación.**

## Contribuir

1. Modificar el contrato original en su microservicio y solicitar revisión a su responsable.
2. Actualizar el commit de origen en [`docs/fuentes.md`](docs/fuentes.md) e importar de nuevo su copia literal.
3. Ejecutar `python scripts/validar_contratos.py` tras instalar `requirements-contracts.txt`.
4. Abrir PR de `cvexpert-docs`; no fusionar cambios de contrato sustanciales sin consenso del equipo.
