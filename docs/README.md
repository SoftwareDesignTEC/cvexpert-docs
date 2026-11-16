# Documentación de arquitectura de CVExpert (Fase II)

CVExpert son cinco microservicios, cada uno en su repositorio, detrás de Azure API Management (APIM), y dos clientes: una web en React y una app Android. La paridad funcional entre ambos es un objetivo; todavía existen integraciones pendientes en la web, detalladas en la [auditoría](auditoria.md) y el [estado de entrega](estado-entrega.md). Esta carpeta describe cómo encajan esas piezas, cómo se protegen, dónde guarda sus datos cada servicio y cómo se despliegan.

Todo lo que aparece aquí se sacó del código, la configuración, los pipelines y los README de cada repositorio (ramas `main` revisadas el 2026-11-15, salvo donde se indica otra). Lo que no se pudo confirmar en el código está marcado como **por confirmar**.

## Documentos

| Documento | Qué contiene |
| --- | --- |
| [Arquitectura](arquitectura.md) | Diagrama general, reglas del sistema con su evidencia y una ficha por servicio |
| [Flujos](flujos.md) | Diagramas de secuencia: inicio de sesión, cambio de estado de una postulación, nueva oferta y edición de plantillas |
| [Seguridad](seguridad.md) | Token de Google en APIM, certificado de cliente hacia los backends, encabezados de identidad, Key Vault, secretos en pipelines y ramas protegidas |
| [Almacenamiento](almacenamiento.md) | Base de cada servicio y por qué ese tipo, tablas y colecciones, la cola de Service Bus, el formato del evento y la idempotencia |
| [Despliegue](despliegue.md) | Recursos de Azure y el pipeline de cada repositorio |

Documentos anteriores que se conservan como detalle:

- [Seguridad de APIM](seguridad-apim.md): inventario de rutas del gateway y configuración de certificados consultada en Azure.
- [Integración de Notificaciones](notificaciones.md): canales, push en Android y adaptación de `course.recommended`.
- [Matriz de trazabilidad](matriz-trazabilidad.md), [plan de pruebas](plan-pruebas.md), [auditoría](auditoria.md) y [estado de entrega](estado-entrega.md): 51 operaciones, 98 solicitudes Postman y 28 casos E2E definidos.
- [Seguimiento de integración](seguimiento-integracion.md): verificaciones vigentes después del merge del PR #5.

## Repositorios

Todos están en la organización `SoftwareDesignTEC` de GitHub. El dueño sale del README de cada repo y de quién hizo la mayoría de los commits en `main`.

| Repositorio | Qué es | Dueño | Stack | Despliegue |
| --- | --- | --- | --- | --- |
| [cvexpert-web](https://github.com/SoftwareDesignTEC/cvexpert-web) | Cliente web (antes `cv-master`) | Gabriel Pérez | React 19, Vite, TypeScript, Tailwind | Azure Static Web Apps: https://victorious-mushroom-0cd000a10.5.azurestaticapps.net |
| [cvexpert-mobile](https://github.com/SoftwareDesignTEC/cvexpert-mobile) | Cliente Android | Andrés Zumbado | Kotlin, Jetpack Compose, Hilt, Retrofit | APK en Firebase App Distribution, grupo `testers` (sin URL pública) |
| [cvexpert-ms-usuarios](https://github.com/SoftwareDesignTEC/cvexpert-ms-usuarios) | Perfil, rol, sesiones, textos legales y ayuda | Gabriel Cabrera | Java 17, Spring Boot 3.3, MongoDB | App Service `cvexpert-usuarios`, solo por APIM |
| [cvexpert-ms-cvs](https://github.com/SoftwareDesignTEC/cvexpert-ms-cvs) | CVs, plantillas e IA de redacción | Gabriel Pérez | Python 3.12, FastAPI, MongoDB | App Service `cvexpert-ms-cvs`, solo por APIM |
| [cvexpert-ms-ofertas-postulaciones](https://github.com/SoftwareDesignTEC/cvexpert-ms-ofertas-postulaciones) | Ofertas, compatibilidad, alertas y postulaciones | Andrés Zumbado | Java 17, Spring Boot 4.1, PostgreSQL 18 | App Service `app-ofertas-andres`, solo por APIM |
| [cvexpert-ms-brecha-cursos](https://github.com/SoftwareDesignTEC/cvexpert-ms-brecha-cursos) | Brecha de habilidades y catálogo de cursos | Justin Mayorga | Node.js 24, Express 5, TypeScript, PostgreSQL | App Service `cvexpert-ms-brecha-cursos`. Job de despliegue de fab6c726… exitoso (11 nov, Costa Rica); revisión activa y E2E por verificar, ver [despliegue](despliegue.md) |
| [cvexpert-ms-notificaciones](https://github.com/SoftwareDesignTEC/cvexpert-ms-notificaciones) | Consumo de eventos, historial y entrega por SignalR, push y correo | Samuel Fajardo | .NET 8, ASP.NET Core, MongoDB | App Service `cvexpert-notificaciones`, solo por APIM |
| [cvexpert-docs](https://github.com/SoftwareDesignTEC/cvexpert-docs) | Contratos, Postman y esta documentación | Justin Mayorga | Markdown, OpenAPI, Python y Node para validar | No se despliega |

APIM no tiene repositorio propio. Sus políticas viven en el recurso `gabriel-api-management` (API `cv-api`) y no están versionadas. APIM y sus certificados corresponden a Cabrera; la exportación vigente de políticas sigue por verificar.

La URL pública de los cinco backends es la del gateway, `https://gabriel-api-management.azure-api.net/api/v1`. Cada App Service rechaza las llamadas que no traen el certificado de cliente de APIM (ver [seguridad](seguridad.md)).

## Cómo correr cada repositorio en local

Los comandos salen del README de cada repositorio. Ninguno necesita secretos reales para las pruebas. Para llamar a un backend sin APIM hay que mandar a mano los encabezados que APIM agregaría (`X-User-Id`, `X-User-Email` y, en rutas de administración, `X-User-Role: admin`). La validación del certificado se apaga en local cuando no se configura la huella.

### cvexpert-web

Requiere Node.js 20 o superior. Crear `apps/web/.env.local` con `VITE_APIM_BASE_URL` y `VITE_GOOGLE_CLIENT_ID` (se piden al encargado de DevOps).

```bash
cd apps/web
npm install
npm run dev        # http://localhost:5173
```

### cvexpert-mobile (Android)

Requiere JDK 17 y el Android SDK con la plataforma 35. Crear `local.properties` en la raíz con `sdk.dir`, `APIM_BASE_URL` y `GOOGLE_WEB_CLIENT_ID`. `NOTIFICATIONS_ENABLED=true` enciende las llamadas a Notificaciones.

```bash
./gradlew assembleDebug    # APK en app/build/outputs/apk/debug/
./gradlew installDebug     # lo instala en el emulador o el dispositivo
```

### cvexpert-ms-usuarios

Requiere Java 17, Maven 3.9 y un MongoDB local.

```bash
docker run -d --name mongo-usuarios -p 27017:27017 mongo:7
mvn test                   # pruebas, sin MongoDB
mvn spring-boot:run        # http://localhost:8080
```

Si la ruta de la carpeta tiene tildes o eñes, en Windows usar `mvn clean package -DskipTests` y `java -jar target/app.jar`.

### cvexpert-ms-cvs

Requiere Python 3.12 y un MongoDB accesible.

```bash
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env       # completar; nunca se versiona
uvicorn app.main:app --reload
pytest
```

### cvexpert-ms-ofertas-postulaciones

Requiere JDK 17 y Docker.

```bash
cp .env.example .env       # y cambiar la contraseña
docker compose up -d       # PostgreSQL 18 en localhost:5432
set -a; . ./.env; set +a   # Git Bash, Linux o macOS
./mvnw spring-boot:run     # http://localhost:8080
```

En PowerShell, la tercera línea se reemplaza por el comando que trae su README. Las pruebas (`./mvnw test`) levantan PostgreSQL con Testcontainers, así que Docker tiene que estar corriendo.

### cvexpert-ms-brecha-cursos

Requiere Node.js 24 y Docker. En `.env`, `APIM_ALLOW_INSECURE_LOCAL=true` solo funciona con `NODE_ENV=development` o `test`, y en Azure se ignora.

```bash
npm ci
cp .env.example .env       # completar PGPASSWORD con una contraseña local
docker compose up -d --wait postgres
npm run db:migrate
npm run dev                # http://127.0.0.1:3000
npm test
```

### cvexpert-ms-notificaciones

Requiere el SDK de .NET 8. Las cadenas de Mongo y Service Bus se cargan con `dotnet user-secrets` (ver su README). Sin ellas la API arranca igual, pero sin consumir la cola.

```bash
dotnet run --project src/Notificaciones.Api   # http://localhost:5029, Swagger en /swagger
dotnet test
```

### cvexpert-docs

Requiere Python 3.12 y Node.js 22.

```bash
python -m pip install -r requirements-docs.txt
python scripts/validar_cobertura.py
node scripts/ejecutar_postman.cjs --sintaxis
```
