# Contratos y fuentes

| Dominio | OpenAPI central |
| --- | --- |
| Usuarios | [usuarios.openapi.yaml](usuarios.openapi.yaml) |
| CVs y plantillas | [cvs.openapi.yaml](cvs.openapi.yaml) |
| Ofertas y postulaciones | [ofertas-postulaciones.openapi.yaml](ofertas-postulaciones.openapi.yaml) |
| Brecha y cursos | [brecha-cursos.openapi.yaml](brecha-cursos.openapi.yaml) |
| Notificaciones | [notificaciones.openapi.yaml](notificaciones.openapi.yaml) |

Las copias son los archivos de origen fijados por revisión y SHA Git blob en [fuentes.json](fuentes.json). Los paths describen el contrato de cada backend. El [CSV de trazabilidad](matriz-trazabilidad.csv) registra por separado las rutas observadas en APIM. Los mensajes se especifican en el [JSON Schema de Notificaciones](evento-notificacion.schema.json) y en su [guía de origen](notificaciones.origen.md).

## Consultar en Swagger

Importe el YAML de un servicio en Swagger Editor con soporte para su versión de OpenAPI. Ofertas usa 3.1 y los demás 3.0. Usuarios conserva una errata conocida en un ejemplo. Para visualizar ese archivo con un editor estricto, aplique en una copia temporal la corrección descrita en la [auditoría](../docs/auditoria.md).

El repositorio de cada servicio documenta su Swagger UI cuando está habilitado. El siguiente comando prepara una referencia Markdown local de parámetros, seguridad y respuestas.

```sh
python scripts/generar_referencia_api.py
```

## Actualizar una fuente

1. Revise el diff del archivo de origen y contraste los cambios con los controladores, DTO y pruebas. Anote el commit de `main` y obtenga el blob con `git rev-parse <commit>:<ruta>` en el repositorio original.
2. Actualice las revisiones y los hashes de los artefactos afectados en [fuentes.json](fuentes.json).
3. Ejecute `python scripts/sincronizar_contratos.py`. Para repositorios privados o trabajo sin red, use `--clones <directorio>` con los repositorios nombrados como en el manifiesto. Agregue `--check` para comparar sin escribir.
4. Ajuste los [escenarios Postman](../scripts/casos_postman.py) y la evidencia de la [matriz](../scripts/generar_matriz.py). Ejecute `python scripts/generar_postman_desde_openapi.py`, `python scripts/generar_matriz.py` y la [validación local](../README.md#validación-local).
5. Registre incompatibilidades en la [auditoría](../docs/auditoria.md) y remita la corrección al servicio responsable.
