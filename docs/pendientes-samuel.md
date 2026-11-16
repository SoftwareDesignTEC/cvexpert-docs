# Observaciones para integrar después del PR #5

Corte 2026-11-16. Este archivo registra observaciones para Samuel sin modificar README.md, docs/README.md, docs/arquitectura.md, docs/almacenamiento.md, docs/despliegue.md, docs/seguridad.md ni docs/flujos.md. La [auditoría](auditoria.md) y [las revisiones exactas](../contratos/revisiones-auditoria.json) sustentan los hallazgos.

| Documento reservado | Corrección que conviene considerar al resolver PR #5 |
| --- | --- |
| docs/notificaciones.md (también modificado por PR #5) | Corregir la afirmación antigua de FCM Android futuro y la ausencia de clases/registro: main ya contiene PushTokenSync, CvMessagingService y PushNotifications. Actualizar revisión Android y el disparador cv.generated tras cualquiera de las operaciones IA; la recepción real sigue sin acreditar. Este archivo se conserva intacto en esta tarea. |
| Arquitectura y flujos | Android main ya integra evaluate/recommendations, catálogo contextual y FCM. Web por oferta continúa en PR #51/#52. Brecha usa proyecciones CV/oferta del cliente: no consulta directamente otros servicios ni verifica titularidad de esos datos para decisiones de autorización. |
| Flujos | course.recommended tiene consumidor/contrato, sin productor main. Diferenciar evento simulado autorizado y emisión real. cv.generated depende del uso IA registrado y guardado posterior; job.new requiere alertas/umbral; cambio de estado administrativo y movimiento propio no son equivalentes. |
| Almacenamiento | Documentar SQL (Ofertas/Brecha), documentos Mongo/Cosmos (Usuarios/CVs/Notificaciones) y objetos Blob (fotos). La existencia de adaptadores/migraciones no acredita datos ni despliegue actual. Service Bus es mensajería, SignalR tiempo real y ACS correo. |
| Despliegue | Citar jobs de despliegue que sí terminaron y sus SHAs desde la auditoría. Brecha tiene un job de despliegue exitoso aunque se llame disabled by default. La sincronización ampliada de cursos sigue en develop; su PR #33 no está en main. |
| Seguridad | Conservar las correcciones de Cabrera del PR #3: roles de ofertas/plantillas informados desde 13 nov; falta prueba autenticada. Mantener discrepancia entre filtro de Usuarios pendiente de PR #2 y reporte de configuración desplegada. |
| Índices y README | Enlazar matriz de 51 operaciones, plan, registro E2E, guion y checklist; reemplazar cifras antiguas solo después de resolver su PR. |
| Compatibilidad de eventos | El hallazgo interested sigue vigente en esquema y validador del receptor. Acordarlo con Andrés/Samuel antes de proclamar entrega de ese cambio. |
| Requisitos / desviaciones | Registrar que cobertura de nombres y déficit ordinal son medidas distintas; recommendations recomienda ausencias y Android consulta catálogo aparte para déficit. Descubrimiento/importación local no es sincronización productiva programada. No reducir requisitos del enunciado para justificar pendientes. |

La arquitectura definitiva continúa bajo responsabilidad de Samuel; estas observaciones no sustituyen sus diagramas. APIM/certificados permanecen bajo responsabilidad de Cabrera y cada servicio mantiene su documentación técnica.
