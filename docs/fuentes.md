# Fuentes y trazabilidad de los contratos

Las fuentes se descargan como **copias literales** (sin modificar campos, rutas o contratos). 
Cada contrato es propiedad técnica del microservicio correspondiente: todo ajuste funcional se acuerda con su dueño y se incorpora primero al repositorio de origen.

**Fecha de esta consolidación inicial:** 20 de octubre de 2026.

| Contrato / material | Repositorio de origen | Rama consultada | Fuente inmovilizada | Commit | Copia en este repo |
|---|---|---|---|---|---|
| `usuarios` | `cvexpert-ms-usuarios` | `main` | [`openapi.yaml`](https://github.com/SoftwareDesignTEC/cvexpert-ms-usuarios/blob/35adbede8c1492941b0d2cda42460fe45f8ccd2c/openapi.yaml) | `35adbede8c14` | `contratos/usuarios.yaml` |
| `cvs` | `cvexpert-ms-cvs` | `main` | [`docs/openapi.yaml`](https://github.com/SoftwareDesignTEC/cvexpert-ms-cvs/blob/9c5b6fc796c4f1e696dcd4a855a375d6f460b284/docs/openapi.yaml) | `9c5b6fc796c4` | `contratos/cvs.yaml` |
| `ofertas-postulaciones` | `cvexpert-ms-ofertas-postulaciones` | `main` | [`docs/openapi.yaml`](https://github.com/SoftwareDesignTEC/cvexpert-ms-ofertas-postulaciones/blob/c8882f786e9f7daeefaaf8f2c3b208b9a7f72b6f/docs/openapi.yaml) | `c8882f786e9f` | `contratos/ofertas-postulaciones.yaml` |
| `brecha-cursos` | `cvexpert-ms-brecha-cursos` | `develop` | [`openapi.yaml`](https://github.com/SoftwareDesignTEC/cvexpert-ms-brecha-cursos/blob/f85ca1c6ef4ada887d0c5d04b91218a1d26aa49c/openapi.yaml) | `f85ca1c6ef4a` | `contratos/brecha-cursos.yaml` |
| `notificaciones` | `cvexpert-ms-notificaciones` | `docs/contratos` | [`docs/contratos/openapi.yaml`](https://github.com/SoftwareDesignTEC/cvexpert-ms-notificaciones/blob/fb8ded59dfce4091c7687c9e82a6fdac7ce6a3bc/docs/contratos/openapi.yaml) | `fb8ded59dfce` | `contratos/notificaciones.yaml` |
| `evento-notificacion` | `cvexpert-ms-notificaciones` | `docs/contratos` | [`docs/contratos/evento-notificacion.schema.json`](https://github.com/SoftwareDesignTEC/cvexpert-ms-notificaciones/blob/fb8ded59dfce4091c7687c9e82a6fdac7ce6a3bc/docs/contratos/evento-notificacion.schema.json) | `fb8ded59dfce` | `eventos/evento-notificacion.schema.json` |
| `guia-eventos` | `cvexpert-ms-notificaciones` | `docs/contratos` | [`docs/contratos/README.md`](https://github.com/SoftwareDesignTEC/cvexpert-ms-notificaciones/blob/fb8ded59dfce4091c7687c9e82a6fdac7ce6a3bc/docs/contratos/README.md) | `fb8ded59dfce` | `eventos/README-origen-notificaciones.md` |

**Advertencia de versiones:** `cvexpert-ms-notificaciones` procede de la rama `docs/contratos`, no de `main`; este documento no implica aprobación o fusión de dicha rama. El archivo `brecha-cursos.yaml` procede de `develop`, no de `main`. Los archivos conservan el estado propuesto/implementado que declara cada contrato.

Para actualizar una copia, registrar el nuevo commit de origen y abrir un PR en este repositorio. **No modificar las copias aquí de manera independiente**, porque generaríamos dos fuentes incompatibles.
