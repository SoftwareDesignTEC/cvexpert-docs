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

## Operación de APIM y Azure

| Documento | Contenido |
| --- | --- |
| [APIM](docs/apim.md) | Mapa de rutas, qué hace APIM en cada llamada y cómo agregar una operación |
| [Certificado de APIM](docs/certificado-apim.md) | Cómo valida cada microservicio que la llamada viene de APIM |
| [Azure](docs/azure.md) | Secretos, Service Bus, permisos y despliegue con OIDC |

## Situación de pruebas E2E (8 de noviembre de 2026)

La colección está preparada para iniciar las E2E de **Ofertas, Postulaciones, Brecha y Notificaciones**. Las de **CVs, generación de PDF e IA** están bloqueadas temporalmente por carga de plantillas y un fallo `500` de IA. El ciclo **FCM del cliente Android** es trabajo futuro, no requisito de cierre de Fase II. La versión Android `0.7.2` fue anunciada como disponible en Firebase, sin prueba acreditada de su inicio de sesión en esta versión. Véase [estado de entrega](docs/estado-entrega.md).

## Validación local

Ejecute los siguientes comandos desde la raíz con Python 3.12 o posterior y Node.js 22 o posterior.

```sh
python -m pip install -r requirements-docs.txt
python scripts/validar_cobertura.py
node scripts/ejecutar_postman.cjs --sintaxis
```

La [auditoría de integración](docs/auditoria.md) registra diferencias con la implementación. El [plan E2E](docs/plan-pruebas.md) identifica el entorno, los datos y las evidencias requeridas para confirmar el comportamiento en Azure.
