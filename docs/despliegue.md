# Despliegue

## Recursos de Azure

Los nombres salen de los pipelines, de las referencias de configuración y de los README de cada repositorio. No se consultó Azure para esta documentación. Lo que no aparece en ningún repositorio está marcado como **por confirmar**.

### Grupo `rg-cvexpert`

| Recurso | Nombre | Notas | Fuente |
| --- | --- | --- | --- |
| Grupo de recursos | `rg-cvexpert` | Grupo compartido del proyecto | `cvexpert-ms-cvs/docs/deploy-setup.md`, preflight de Brecha |
| Plan de App Service | **Por confirmar** (`asp-cvexpert` B1 no aparece en ningún repositorio) | Tiene que ser Basic o superior para admitir certificados de cliente | — |
| App Service | `cvexpert-usuarios` | Java 17. `/actuator/health` excluido del certificado | `cd.yml` de la rama `certificado-swagger-postman` |
| App Service | `cvexpert-ms-cvs` | Linux, Python. Compilación con Oryx en el servidor (`SCM_DO_BUILD_DURING_DEPLOYMENT=true`). Autenticación básica de SCM deshabilitada | `cd.yml`, `deploy-setup.md` |
| App Service | `cvexpert-ms-brecha-cursos` | Linux, `NODE\|24-lts`, inicio `npm start`. Sin exclusiones de certificado | `ci-cd.yml`, `azure-preflight.mjs` |
| App Service | `cvexpert-notificaciones` | Linux, .NET 8, East US. `/health` excluido del certificado | `deploy.yml`, README |
| Key Vault | `kv-cvexpert` | Secretos de ejecución, leídos con identidad administrada (ver [seguridad](seguridad.md)) | README de Usuarios, Ofertas y Notificaciones |
| Service Bus | Namespace **por confirmar**. Cola `notificaciones-eventos` | Políticas SAS de la cola: solo envío y solo escucha | README de Ofertas y Notificaciones |
| Cosmos DB con API de MongoDB | **Por confirmar** (nombre y número de cuentas) | Notificaciones indica que su cuenta está en Central US. La cadena debe llevar `retryWrites=false` | README de Notificaciones |
| Azure SignalR Service | **Por confirmar** (nombre) | Tier Free | README de Notificaciones |
| Azure Communication Services (correo) | **Por confirmar** (nombre) | Dominio verificado. El remitente es `Email__Sender` | README de Notificaciones |
| Storage Account | **Por confirmar** (nombre) | Contenedor `cv-photos` para las fotos de los CV | `app/config.py` de CVs |
| PostgreSQL de Brecha | **Por confirmar** | El CD no ejecuta migraciones. El servidor de Azure no está documentado | README de Brecha |
| Grupo del APIM y de la Static Web App | **Por confirmar** | — | — |

### Fuera de `rg-cvexpert`

| Recurso | Nombre | Notas | Fuente |
| --- | --- | --- | --- |
| API Management | `gabriel-api-management`, API `cv-api`, prefijo `/api/v1` | Tier Consumption (no soporta WebSockets). Certificado `cvexpert-client-cert` | [seguridad-apim.md](seguridad-apim.md), README de Notificaciones |
| Static Web App | Host `victorious-mushroom-0cd000a10.5.azurestaticapps.net` (nombre del recurso **por confirmar**) | Producción desde `main` y un entorno de vista previa por PR | Workflow de `cvexpert-web` |
| Grupo de recursos | `rg-ofertas-postulaciones` (West US, suscripción Azure for Students de Andrés) | Todo lo de Ofertas está aquí | README de Ofertas |
| Plan de App Service | `plan-ofertas` | Basic B1 | README de Ofertas |
| App Service | `app-ofertas-andres` | Linux, Java 17 SE, "siempre activo" y certificado obligatorio salvo `/actuator/health` | README de Ofertas |
| Azure Database for PostgreSQL | `psql-ofertas-andres`, base `ofertas_postulaciones` | Flexible Server, Burstable B1ms, 32 GB, PostgreSQL 18. Solo acepta conexiones desde servicios de Azure | README de Ofertas |

Ofertas vive en otra suscripción y otra región, pero lee sus secretos del mismo `kv-cvexpert`.

### Servicios externos

| Servicio | Quién lo usa | Para qué |
| --- | --- | --- |
| Google Identity | Clientes y APIM | Inicio de sesión y validación del `id_token` |
| Firebase | Notificaciones y Android | FCM para el push. App Distribution para repartir el APK |
| Gemini | CVs | IA de redacción, detrás de un adaptador reemplazable (`LLM_PROVIDER`) |
| JSearch (OpenWeb Ninja, por RapidAPI) | Ofertas | Importación de ofertas reales, con plan gratuito de 200 consultas al mes |

## Pipelines

Todos son de GitHub Actions. Los pipelines de los backends prueban en cada PR y despliegan solo desde `main`.

| Repositorio | Workflow | Cuándo corre | Qué hace | Destino |
| --- | --- | --- | --- | --- |
| cvexpert-web | `azure-static-web-apps-victorious-mushroom-0cd000a10.yml` | Push a `main` y PR hacia `main` (abrir, actualizar o cerrar) | `npm ci`, lint y tipos, compilación con `VITE_APIM_BASE_URL` y `VITE_GOOGLE_CLIENT_ID`, despliegue y `gh release create` con la versión de `package.json`. Al cerrar un PR borra su vista previa | Static Web App (producción o vista previa) |
| cvexpert-mobile | `android-ci-cd.yml` | Push y PR a `main` | Compila el APK de release con JDK 17. Solo en `main`, lo firma y lo sube a Firebase App Distribution | Grupo `testers` |
| cvexpert-ms-usuarios | `ci.yml` y `cd.yml` (rama `certificado-swagger-postman`, sin fusionar) | CI: cada PR y push a `develop` o `main`. CD: push a `main` que cambie `src/`, `pom.xml` o el workflow, o a mano | `mvn -B verify`. El CD vuelve a probar y despliega `target/app.jar` con OIDC | `cvexpert-usuarios` |
| cvexpert-ms-cvs | `ci.yml` y `cd.yml` | CI: PR y push a `main`. CD: push a `main` que cambie `app/`, `requirements*.txt` o el workflow | `ruff check` y `pytest`. El CD vuelve a probar y despliega con OIDC en el environment `production` | `cvexpert-ms-cvs` |
| cvexpert-ms-ofertas-postulaciones | `ci.yml` (jobs `pruebas`, `cambios` y `desplegar`) | PR a `main`, push a `main` o a mano | `./mvnw -B verify` con PostgreSQL 18 en Testcontainers. En `main`, si cambió código, despliega **el mismo jar probado** con OIDC y espera a que `/actuator/health` responda `UP` (hasta 5 min) | Variable `AZURE_WEBAPP_NAME` (`app-ofertas-andres`) |
| cvexpert-ms-brecha-cursos | `ci-cd.yml` y `azure-oidc-check.yml` | PR y push a `develop` y `main`. El CD solo corre en push a `main` con `ENABLE_AZURE_DEPLOY=true` | `npm audit`, compilación, pruebas, pruebas de BD con PostgreSQL 17 desechable, `actionlint` y verificación del ZIP de producción. El CD corre un preflight de la configuración del App Service y despliega con OIDC desde un runner propio (`AZURE_DEPLOY_RUNNER`). Habilitación explícita; [job exitoso de main](https://github.com/SoftwareDesignTEC/cvexpert-ms-brecha-cursos/actions/runs/43138922188/job/130921348838) para fab6c726… el 11 nov (Costa Rica); estado activo actual por verificar | `cvexpert-ms-brecha-cursos` |
| cvexpert-ms-notificaciones | `deploy.yml` | PR a `main`: solo compila y prueba. Push a `main` o a mano (desde cualquier rama): además despliega | `dotnet build` y `dotnet test` en Release, publicación y despliegue con publish profile. Luego comprueba `/health` con 12 reintentos cada 15 s | `cvexpert-notificaciones` |
| cvexpert-docs | `validar-documentacion.yml` | Push a `main` y cada PR | Valida contratos, procedencia, eventos, matriz, Postman y enlaces, y busca credenciales | No despliega |

Detalles comunes:

- **Un despliegue a la vez.** Usuarios, CVs, Ofertas y Notificaciones usan `concurrency` con `cancel-in-progress: false`, para no cortar un despliegue a la mitad.
- **Sin secretos de ejecución en el pipeline.** Las cadenas de conexión viven en el App Service y en Key Vault, y las pruebas no las necesitan. Lo que guarda cada repo en GitHub está en [seguridad](seguridad.md).
- **Prueba de humo.** Ofertas y Notificaciones comprueban el endpoint de salud después de desplegar, porque es la única ruta excluida del certificado de cliente.
- **Por confirmar:** si el CD de Usuarios corre desde `main` (hoy el workflow solo existe en una rama sin fusionar) y qué revisión de Brecha está activa hoy. Existe evidencia del job de despliegue de fab6c726… citado arriba; no constituye una ejecución E2E.
