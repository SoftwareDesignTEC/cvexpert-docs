# Auditoría inicial de contratos y colecciones — 8 noviembre 2026

## Cobertura documental encontrada

| Servicio | OpenAPI | Operaciones | Colección Postman de origen | Solicitudes existentes |
|---|---|---:|---|---:|
| Usuarios | `openapi.yaml` | 7 | No localizada en `main` | 0 localizadas |
| CVs | `docs/openapi.yaml` | 9 | `docs/postman/cvexpert-ms-cvs.postman_collection.json` | 9 |
| Ofertas y Postulaciones | `docs/openapi.yaml` | 13 | `postman/ofertas-postulaciones.postman_collection.json` | 21 |
| Brecha y Cursos | `openapi.yaml` | 4 | `postman/brecha-cursos.postman_collection.json` | 5 |
| Notificaciones | `docs/contratos/openapi.yaml` | 12 | No localizada en `main` | 0 localizadas |
| **Total** | **5 contratos** | **45** | **3 colecciones** | **35 solicitudes** |

En las tres colecciones existentes se encontraron scripts `test` asociados a las solicitudes. No se ha comprobado que sus aserciones sean correctas o que la ejecución pase en APIM. Las 35 solicitudes NO equivalen a 35 endpoints distintos: existen solicitudes duplicadas para distintos escenarios.

## Evidencias observadas durante diagnóstico Android

- La aplicación `com.cvpro.app.debug` obtuvo un ID token emitido por Google. Con el cliente OAuth antiguo (`aud` diferente al de CI), `/api/v1/cvs`, `/api/v1/jobs` y `/api/v1/skills-gap` devolvían **401**.
- Tras configurar localmente el Google Web Client ID coincidente con CI, `GET /api/v1/cvs` y `GET /api/v1/jobs` devolvieron **200**.
- `GET /api/v1/skills-gap` devolvió **409** con `SKILLS_INPUT_REQUIRED`, informando de la ausencia de una instantánea de habilidades.
- `GET /api/v1/help` devolvió 401 antes de iniciar sesión, por falta de token; no demuestra fallo posterior al login.

Estas observaciones prueban solamente tres solicitudes de una sesión de Android; no acreditan que todos los endpoints estén operativos. **No almacenar los tokens reales en evidencias.**

## Hallazgos por resolver

1. **Brecha**: el texto del `openapi.yaml` describe operaciones con mock en APIM. Se debe actualizar la declaración solo después de confirmar la política y backend efectivos.
2. **Ofertas**: `x-estado` conserva referencias históricas a mocks de Fase I; no interpretarlas como estado operativo actual.
3. **Usuarios y Notificaciones**: falta localizar/recibir colecciones Postman originales en los paths públicos inspeccionados; la colección central incorpora entradas de prueba iniciales.
4. **APIM**: no existe en este paquete una exportación verificable de políticas, certificados, roles, rewrite de rutas o el OpenAPI importado. Solicitar a la persona encargada.
5. **Contratos copiados**: el usuario debe ejecutar `scripts/sincronizar_contratos.py` para obtener los documentos canónicos; hasta entonces la carpeta contiene manifiesto y matriz, NO los cinco YAML completos.
6. **Colección central**: contiene 45 operaciones y scripts de aserción, pero algunos bodies son placeholders `{}` y NO ha pasado un Collection Runner. No confundir cobertura estructural con cobertura funcional.
