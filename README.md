# CVExpert · Documentación técnica de Fase II

Este repositorio reúne los contratos de los cinco microservicios, sus escenarios de prueba y las decisiones de integración para web y Android.

| Entregable | Contenido |
| --- | --- |
| [Contratos OpenAPI](contratos/README.md) | Especificaciones, revisiones de origen, consulta con Swagger y mantenimiento |
| [Matriz de trazabilidad](docs/matriz-trazabilidad.md) | Operaciones, permisos, DTO, Postman y evidencia por ruta |
| [Postman y Newman](postman/README.md) | Colección importable, configuración y ejecución por carpeta |
| [Arquitectura](docs/arquitectura.md) y [seguridad](docs/seguridad-apim.md) | Límites de confianza, almacenamiento, enrutamiento y despliegue |
| [Notificaciones y eventos](docs/notificaciones.md) | Service Bus, SignalR, correo, FCM y adaptación de cursos |
| [Estado de entrega](docs/estado-entrega.md) | Resultados reproducidos y verificaciones pendientes |

## Validación local

Ejecute los siguientes comandos desde la raíz con Python 3.12 o posterior y Node.js 22 o posterior.

```sh
python -m pip install -r requirements-docs.txt
python scripts/validar_cobertura.py
node scripts/ejecutar_postman.cjs --sintaxis
```

La [auditoría de integración](docs/auditoria.md) registra diferencias con la implementación. El [plan E2E](docs/plan-pruebas.md) identifica el entorno, los datos y las evidencias requeridas para confirmar el comportamiento en Azure.
