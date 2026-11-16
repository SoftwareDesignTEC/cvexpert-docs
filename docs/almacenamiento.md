# Almacenamiento

Cada servicio es dueño de sus datos y ningún otro lee su base. Se usan tres tipos de almacenamiento según la forma del dato:

- **Documentos** (Cosmos DB con API de MongoDB): datos que se leen enteros por su dueño y cuya forma varía.
- **Relacional** (PostgreSQL): datos con relaciones, unicidad y restricciones que la base tiene que garantizar.
- **Cola** (Azure Service Bus): mensajes que un servicio produce y otro consume más tarde, sin que el productor tenga que esperarlo.

Además, CVs guarda las fotos en Azure Blob Storage, porque son archivos binarios y no conviene meterlos en la base.

## Resumen

| Servicio | Tipo | Motor | Base o contenedor | Por qué ese tipo |
| --- | --- | --- | --- | --- |
| Usuarios | Documentos | Cosmos DB con API de MongoDB | `cvexpert-usuarios` en local. En Azure, la que indique `Usuarios--MongoDbUri` (**por confirmar**) | El perfil se lee y escribe completo por su `id`, tiene listas de tamaño variable (tipos de jornada, modalidades, sectores) y la actualización es parcial. No hay relaciones con otros datos |
| CVs | Documentos | Cosmos DB con API de MongoDB | `cvexpert` (valor por defecto de `MONGODB_DB`; en Azure **por confirmar**) | Un CV es un documento anidado: experiencias, educación, habilidades, idiomas y certificaciones, cada una con su propia forma. Se guarda y se devuelve entero, y la IA genera ese mismo árbol |
| CVs (fotos) | Objetos | Azure Blob Storage | Contenedor `cv-photos` | Archivos binarios con URL propia. La base solo guarda la URL |
| Ofertas y Postulaciones | Relacional | PostgreSQL 18 (Azure Database for PostgreSQL, Flexible Server) | `ofertas_postulaciones` en `psql-ofertas-andres` | Una postulación apunta a una oferta (llave foránea). Una persona solo puede postularse una vez por oferta, incluso con dos solicitudes simultáneas (`UNIQUE`). Los estados y modalidades se restringen con `CHECK`, y los filtros del listado se resuelven en SQL |
| Brecha y Cursos | Relacional | PostgreSQL (17 en local y en CI; el servidor de Azure está **por confirmar**) | `cvexpert_catalog` en local | Un curso enseña varias habilidades y una habilidad se enseña en varios cursos (muchos a muchos). Hace falta integridad referencial, unicidad de URL y transacciones en las importaciones |
| Notificaciones | Documentos | Cosmos DB con API de MongoDB (Central US, según su README) | `notificaciones` | Se escribe una vez por evento y se lee por usuario y por fecha. El campo `data` cambia según el tipo de evento. Un índice único sobre `eventId` da la idempotencia |
| Eventos | Cola | Azure Service Bus | Cola `notificaciones-eventos` | Desacopla a los productores de Notificaciones: el productor no espera la entrega, y la cola reintenta y separa los mensajes inválidos |

**Por confirmar:** cuántas cuentas de Cosmos DB hay. Usuarios, CVs y Notificaciones reciben cada uno su propia cadena de conexión, así que el código no dice si comparten cuenta.

## Usuarios: colecciones

| Colección | Qué guarda | Índices definidos en el código |
| --- | --- | --- |
| `profiles` | `_id` = `sub`, `fullName`, `email`, `phone`, `address`, `photoUrl`, `bio`, `types[]`, `modalities[]`, `sectors[]`, `role`, `createdAt`, `updatedAt` | `email` único |
| `sessions` | Dispositivos desde los que se usó la cuenta: `userId`, `deviceName`, `platform`, `client`, `lastActiveAt` | `userId` + `lastActiveAt` desc |
| `legal_documents` | Términos y privacidad por idioma y versión: `kind`, `lang`, `version`, `effectiveDate`, `content` | `kind` + `lang` + `effectiveDate` desc |
| `help_contacts` | Contactos del centro de ayuda por idioma | `lang` + `position` |

Los textos legales y de ayuda se cargan desde `src/main/resources/seed` si la colección está vacía.

## CVs: colecciones

| Colección | Qué guarda |
| --- | --- |
| `cvs` | Un documento por CV: `id`, `userId`, `title`, `templateId`, `thumbnailUrl`, `personalInfo`, `workExperiences[]`, `education[]`, `skills[]`, `languages[]`, `certifications[]`, `createdAt` y `updatedAt`. Todas las consultas filtran por `userId` |
| `templates` | Catálogo de plantillas de CV con su `previewUrl` y su diseño |
| `ai_usage` | Una marca por usuario (`userId`, `markedAt`) que dejan las operaciones de IA. La creación del CV la consume y, si existía, publica `cv.generated` |

El código no crea índices. Los índices efectivos en Cosmos DB están **por confirmar**.

## Ofertas y Postulaciones: tablas

Flyway crea el esquema (`V1` a `V5` en `src/main/resources/db/migration`) y Hibernate solo valida el mapeo (`ddl-auto: validate`).

| Tabla | Qué guarda | Restricciones principales |
| --- | --- | --- |
| `job_offers` | Ofertas: título, empresa, ubicación, modalidad, jornada, sector, `skills` y `requirements` como `text[]`, salario, `source`, `external_id`, `apply_url`, `posted_at` y `deleted_at` | Borrado lógico. Índice por `posted_at` desc solo en las no borradas. Salario completo o ausente |
| `job_applications` | Postulaciones, con copia del título, la empresa, el logo, la ubicación y la modalidad de la oferta | FK a `job_offers`. `UNIQUE (job_offer_id, user_id)`. `CHECK` del estado (`interested`, `applied`, `in-progress`, `interview` y `rejected`). Índice por `user_id` + `updated_at` |
| `alert_settings` | Una fila por usuario: si quiere alertas, su `minMatch` y su perfil de emparejamiento | PK `user_id`. Índice parcial de los que tienen alertas activas |

Las fechas son `bigint` en epoch milisegundos UTC, y los ids son `bigint` que viajan como texto en JSON. La app se conecta con el usuario `ofertas`, que solo tiene permisos sobre `public` de su base, y con TLS (`sslmode=require`).

## Brecha y Cursos: tablas

Las migraciones son SQL propios (`db/migrations/001` a `004`), registrados en `schema_migrations` con su SHA-256 y aplicados en una sola transacción.

| Tabla | Qué guarda |
| --- | --- |
| `skills` | Habilidades del catálogo, con nombre único |
| `courses` | Cursos: título, plataforma, `url` única, `is_paid`, `duration_hours` (NULL = desconocida) y `logo_url` |
| `course_skills` | Relación muchos a muchos curso–habilidad, con PK compuesta. `ON DELETE CASCADE` desde el curso y `RESTRICT` desde la habilidad |
| `market_requirements` | Nivel que pide el mercado por habilidad y contexto (`market_key`) |
| `user_skill_snapshots` | Instantánea vigente de las habilidades del usuario. La llave es un hash del sujeto autenticado (`subject_hash`), sin guardar correo, CV ni token |
| `admin_import_runs` | Registro de las importaciones administrativas aprobadas, que solo se ejecutan en local |

El catálogo se consulta con un rol que solo tiene `SELECT` (`cvexpert_brecha_app`), y escribir las instantáneas requiere un permiso de escritura mínimo que se otorga aparte. Las migraciones se corren con otro usuario. Fuera de desarrollo, la conexión exige `DB_SSL_MODE=verify-full`.

## Notificaciones: colecciones

`MongoIndexInitializer` crea los índices al arrancar. En Cosmos DB, un índice único solo se puede crear con la colección vacía.

| Colección | Qué guarda | Índices |
| --- | --- | --- |
| `notifications` | `eventId`, `userId`, `type`, `source`, `data`, `occurredAt`, `createdAt` y `readAt`. Los textos `title` y `body` no se guardan: se arman al consultar o enviar | `eventId` **único**. `userId` + `createdAt` desc. `userId` + `readAt`. `createdAt` desc + `_id` desc |
| `directory` | `_id` = userId, `email`, `language` y `updatedAt` | Solo `_id` |
| `devices` | Tokens de FCM: `token`, `userId`, `platform` y `registeredAt` | `token` único. `userId` |
| `templates` | Plantillas editadas: `_id` = `"{type}:{language}"`, `title`, `body`, `updatedAt` y `updatedBy` | Solo `_id` |

## Cola de Service Bus

| Elemento | Valor |
| --- | --- |
| Cola | `notificaciones-eventos` |
| Productores | Ofertas y Postulaciones (`application.status_changed` y `job.new`) y CVs (`cv.generated`). Brecha (`course.recommended`) todavía no publica |
| Consumidor | Notificaciones, con `ServiceBusProcessor` en modo PeekLock, sin completado automático y hasta 4 mensajes a la vez |
| Permisos | Una política SAS de la cola para cada lado: solo envío para Ofertas y solo escucha para Notificaciones. CVs: **por confirmar** |
| Namespace | **Por confirmar** (no aparece en ningún repositorio) |

Por qué una cola y no una llamada HTTP:

- La regla del sistema prohíbe que un servicio llame a otro. Los productores solo conocen la cola.
- El productor no depende de que Notificaciones esté arriba. Si está caído, los mensajes esperan en la cola.
- Service Bus reintenta los fallos transitorios y separa en la dead-letter lo que no se puede procesar, sin perderlo.
- La cola permite un mensaje por destinatario, así que Ofertas puede emitir un `job.new` distinto para cada usuario compatible.

### Formato del evento

El contrato es [evento-notificacion.schema.json](../contratos/evento-notificacion.schema.json), que es copia de la fuente de verdad en [cvexpert-ms-notificaciones/docs/contratos](https://github.com/SoftwareDesignTEC/cvexpert-ms-notificaciones/tree/main/docs/contratos). Cada mensaje es un JSON con un sobre estricto (no admite campos extra) y un `data` propio de cada tipo, que sí admite campos adicionales.

| Campo del sobre | Contenido |
| --- | --- |
| `schemaVersion` | `1` |
| `eventId` | UUID v4 único por mensaje |
| `type` | `application.status_changed`, `cv.generated`, `job.new` o `course.recommended` |
| `userId` | Destinatario: el mismo valor que APIM manda en `X-User-Id` |
| `occurredAt` | Epoch milisegundos UTC |
| `source` | `ofertas-postulaciones`, `cvs` o `brecha-cursos`. Cada tipo tiene un único publicador permitido |
| `data` | Campos del tipo (abajo) |

| Tipo | Campos obligatorios de `data` | Opcionales |
| --- | --- | --- |
| `application.status_changed` | `applicationId`, `jobOfferId`, `jobTitle`, `company`, `newStatus` | `previousStatus` |
| `cv.generated` | `cvId`, `title` | `templateId` |
| `job.new` | `jobOfferId`, `title`, `company`, `location`, `modality`, `matchScore` (0 a 100) | — |
| `course.recommended` | `title`, `platform`, `url` (http o https), `isPaid` | `duration`, `skill` |

Propiedades del mensaje de Service Bus: `messageId` = `eventId`, `subject` = `type` y `contentType` = `application/json`.

Ejemplo (valores ficticios):

```json
{
  "schemaVersion": 1,
  "eventId": "3f1c2a9e-7b4d-4c1a-9e2f-5a6b7c8d9e0f",
  "type": "application.status_changed",
  "userId": "sub-de-ejemplo",
  "occurredAt": 1794700800000,
  "source": "ofertas-postulaciones",
  "data": {
    "applicationId": "42",
    "jobOfferId": "17",
    "jobTitle": "Desarrollador junior",
    "company": "Empresa de ejemplo",
    "previousStatus": "applied",
    "newStatus": "interview"
  }
}
```

**Diferencia conocida:** el enum de estados del esquema no incluye `interested`, que Ofertas agregó en la Fase II. Un cambio administrativo hacia o desde ese estado produce un mensaje que Notificaciones manda a la dead-letter.

### Idempotencia por `eventId`

Service Bus entrega cada mensaje **al menos una vez**, así que el mismo evento puede llegar dos veces: si el productor reintenta, o si el consumidor falla después de guardar y antes de completar. La protección está en el consumidor:

1. El productor genera el `eventId` una vez y lo usa también como `messageId`. Si reintenta el mismo evento, conserva su identidad.
2. Notificaciones valida el mensaje. Si no es JSON o no cumple el esquema, va a la dead-letter sin reintentar (`InvalidJson` o `SchemaValidationFailed`).
3. Lo inserta en `notifications`, que tiene un índice **único** sobre `eventId`. Si el `eventId` ya existe, es un duplicado: se completa el mensaje sin volver a entregarlo por ningún canal. Se probó en producción el 2026-11-04 reenviando un evento.
4. Si Mongo falla, se abandona el mensaje después de 5 s y Service Bus lo reintenta. Al agotar `MaxDeliveryCount`, lo pasa a la dead-letter.
5. El consumidor no empieza a leer la cola hasta que el índice único existe, porque sin él no hay deduplicación.

Del lado de los productores, el evento se publica **después** de guardar el cambio y un fallo de envío solo se registra en el log: CVs reintenta 3 veces y Ofertas lo intenta una vez. Si el envío falla del todo, el cambio queda guardado sin aviso. Resolverlo del todo exigiría el patrón outbox, que no está implementado. Si la detección de duplicados de Service Bus está activada en la cola: **por confirmar**.
