# CVExpert · Documentación técnica de Fase II

Este repositorio reúne los contratos de los cinco microservicios, sus escenarios de prueba y las decisiones de integración para web y Android.

| Entregable | Contenido |
| --- | --- |
| [Contratos OpenAPI](contratos/README.md) | Especificaciones, revisiones de origen, consulta con Swagger y mantenimiento |
| [Matriz de trazabilidad](docs/matriz-trazabilidad.md) | Operaciones, permisos, DTO, Postman y evidencia por ruta |
| [Postman y Newman](postman/README.md) | Colección importable, configuración y ejecución por carpeta |
| [Documentación de arquitectura](docs/README.md) | Índice de repositorios, [arquitectura](docs/arquitectura.md), [flujos](docs/flujos.md), [seguridad](docs/seguridad.md), [almacenamiento](docs/almacenamiento.md) y [despliegue](docs/despliegue.md) |
| [Notificaciones y eventos](docs/notificaciones.md) | Service Bus, SignalR, correo, FCM y adaptación de cursos |
| [Estado de entrega](docs/estado-entrega.md) | Resultados reproducidos y verificaciones pendientes |

## Operación de APIM y Azure

| Documento | Contenido |
| --- | --- |
| [APIM](docs/apim.md) | Mapa de rutas, qué hace APIM en cada llamada y cómo agregar una operación |
| [Certificado de APIM](docs/certificado-apim.md) | Cómo valida cada microservicio que la llamada viene de APIM |
| [Azure](docs/azure.md) | Secretos, Service Bus, permisos y despliegue con OIDC |

## Situación de pruebas E2E — actualización del 16 de noviembre de 2026

La documentación consolida **51 operaciones REST, 98 solicitudes Postman y 28 casos E2E**. FCM Android está integrado desde `0.9.5`; su recepción real debe probarse en un teléfono con APK de distribución 0.9.5 o posterior, configuración Firebase y permisos correctos. Postman solo comprueba las APIs de dispositivos.

El aviso del 8 nov sobre plantillas pendientes y HTTP 500 de IA se conserva como **antecedente histórico**: no hay cierre E2E posterior acreditado para la revisión auditada. Android debug y la APK 0.7.2 tampoco certifican las versiones recientes. El [estado de entrega](docs/estado-entrega.md) distingue implementación, despliegue y resultados; el [registro E2E](evidencias/registro-e2e.csv) conserva 27 casos no ejecutados y uno bloqueado, sin aprobaciones inventadas.

La arquitectura del PR #5 ya está integrada. El PR #6 reconcilia contratos, pruebas y documentación sobre ese main; el [seguimiento](docs/seguimiento-integracion.md) contiene solo verificaciones vigentes.

## Validación local

Ejecute los siguientes comandos desde la raíz con Python 3.12 o posterior y Node.js 22 o posterior.

```sh
python -m pip install -r requirements-docs.txt
python scripts/validar_cobertura.py
node scripts/ejecutar_postman.cjs --sintaxis
```

La [auditoría de integración](docs/auditoria.md) registra diferencias con la implementación. El [plan E2E](docs/plan-pruebas.md) identifica el entorno, los datos y las evidencias requeridas para confirmar el comportamiento en Azure.
