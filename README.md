# CVExpert — Contratos y pruebas de API (Fase II)

**Estado: propuesta preparada para revisión.** Este paquete contiene un inventario de **45 operaciones** obtenido de los cinco OpenAPI revisados el 8 de noviembre de 2026, una colección Postman central de 45 solicitudes con pruebas de código HTTP y un sincronizador de contratos canónicos. **No se han ejecutado las 45 pruebas contra APIM.**

## Uso rápido

La generación de la referencia y el enriquecimiento de Postman requieren Python y `python -m pip install -r requirements-docs.txt`.

1. Ejecutar `python scripts/sincronizar_contratos.py` con Internet para obtener las **cinco especificaciones OpenAPI completas** y el esquema de evento desde sus repositorios de origen. Se verifica la huella Git de cada OpenAPI para evitar cambios silenciosos.
2. Ejecutar `python scripts/generar_referencia_api.py` para extraer de los OpenAPI todos los parámetros, cuerpos, respuestas y seguridad documentados; ejecutar `python scripts/generar_postman_desde_openapi.py` para enriquecer JSON de ejemplo allí donde existan en fuentes originales.
3. Importar en Postman `postman/cvexpert.postman_collection.json` y `postman/apim.postman_environment.json`.
4. Rellenar **localmente**, nunca en Git, el valor `googleIdToken` y los IDs de recursos de prueba; la URL pública base es una referencia observada en Android y debe validarse en APIM.
5. Las escrituras están **deshabilitadas de forma predeterminada** (`allowWrites=false`); habilitarlas solo en entorno de pruebas y después de revisar los JSON requeridos por cada DTO. Rutas administrativas necesitan además `allowAdmin=true` y un usuario autorizado. Las rutas de salud tienen control `allowDirectHealth`.
6. Ejecutar las pruebas con Collection Runner / Newman y guardar el informe redactado en `evidencias/`. Nunca publicar tokens reales ni respuestas con datos personales.

## Repositorios de origen

| Dominio | Repositorio | Contrato | Operaciones |
| --- | --- | --- | ---: |
| Usuarios | [GitHub](https://github.com/SoftwareDesignTEC/cvexpert-ms-usuarios) | `openapi.yaml` | 7 |
| CVs y plantillas | [GitHub](https://github.com/SoftwareDesignTEC/cvexpert-ms-cvs) | `docs/openapi.yaml` | 9 |
| Ofertas y postulaciones | [GitHub](https://github.com/SoftwareDesignTEC/cvexpert-ms-ofertas-postulaciones) | `docs/openapi.yaml` | 13 |
| Brecha y cursos | [GitHub](https://github.com/SoftwareDesignTEC/cvexpert-ms-brecha-cursos) | `openapi.yaml` | 4 |
| Notificaciones | [GitHub](https://github.com/SoftwareDesignTEC/cvexpert-ms-notificaciones) | `docs/contratos/openapi.yaml` | 12 |

**Rutas:** los OpenAPI no comparten el mismo `servers`: algunos documentan el backend interno; otros, APIM. La matriz registra el path canónico del contrato, pero no acredita que cada operación esté expuesta ni reescrita correctamente en el gateway.

**Autenticación:** el cliente presenta `Authorization: Bearer {{googleIdToken}}` a APIM. El gateway valida identidad y agrega encabezados internos como `X-User-Id` / `X-User-Email`; el consumidor no debe enviarlos por su cuenta. La autenticación entre APIM y los backends mediante certificados requiere evidencia de Azure, no se comprueba con una colección JSON por sí sola.

## Índice de entregables

- [`contratos/fuentes.json`](contratos/fuentes.json): procedencia y hash de cada archivo de fuente.
- [`contratos/matriz-trazabilidad.csv`](contratos/matriz-trazabilidad.csv): 45 rutas, verbos, éxito, origen y verificación pendiente.
- [`docs/matriz-trazabilidad.md`](docs/matriz-trazabilidad.md): matriz legible por servicio.
- [`docs/auditoria.md`](docs/auditoria.md): hallazgos, cobertura actual y puntos por resolver.
- [`docs/seguridad-apim.md`](docs/seguridad-apim.md): controles y evidencia requerida.
- [`docs/plan-pruebas.md`](docs/plan-pruebas.md): criterios antes de considerar las pruebas concluidas.
- [`postman/README.md`](postman/README.md): importación, variables, ejecución y precauciones.
- [`scripts/generar_referencia_api.py`](scripts/generar_referencia_api.py): genera referencia detallada de cada operación y sus DTO desde YAML sin inventar campos.
- [`scripts/generar_postman_desde_openapi.py`](scripts/generar_postman_desde_openapi.py): enriquece cuerpos y parámetros a partir de los contratos locales, sin inventar DTO.

## Alcance y propiedad

- Justin: consolidación de OpenAPI, Postman, matriz y evidencia de pruebas E2E.
- Samuel: arquitectura detallada y almacenamiento; incorporar su PR sin sobrescribir autoría.
- Responsable de APIM: rutas desplegadas, políticas, autorización, certificados, trazas y evidencias.

**No usar este estado como certificación de despliegue.** Los tests están definidos, pero siguen siendo necesarias las credenciales de prueba, datos, roles, ejecución y contraste con el gateway.
