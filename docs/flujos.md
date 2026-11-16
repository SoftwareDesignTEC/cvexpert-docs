# Flujos principales

Cuatro flujos que cruzan varios servicios. En todos, APIM valida el token, sobrescribe los encabezados `X-User-*` y llama al backend con su certificado de cliente. Cada backend valida ese certificado antes de procesar la llamada. Para no repetirlo en cada diagrama, ese paso se muestra completo en el primero y en los demás se resume como "certificado + X-User-*". El detalle está en [seguridad](seguridad.md).

## 1. Inicio de sesión

La web usa Google Identity Services y Android usa Credential Manager con Google ID. Los dos terminan con el mismo `id_token`, que dura una hora y no se renueva solo.

```mermaid
sequenceDiagram
    autonumber
    actor P as Persona
    participant CL as Cliente web o Android
    participant G as Google Identity
    participant A as APIM
    participant U as Usuarios
    participant N as Notificaciones
    participant SR as Azure SignalR Service

    P->>CL: Iniciar sesión con Google
    CL->>G: Solicitud de credencial
    G-->>CL: id_token JWT con sub y email
    CL->>CL: Guarda solo el id_token en el dispositivo

    CL->>A: GET /profiles/sub con Authorization Bearer id_token
    A->>A: validate-jwt: firma, expiración, audiencia y emisor de Google
    alt Token inválido o vencido
        A-->>CL: 401
        CL->>CL: Cierra la sesión y vuelve al login
    else Token válido
        A->>U: GET /profiles/sub con certificado de cliente y X-User-Id, X-User-Email
        U->>U: Valida la huella del certificado
        U->>U: id debe coincidir con X-User-Id o X-User-Email, si no 403
        U->>U: Crea el perfil si no existe y asigna el rol según ADMIN_EMAILS
        U->>U: Registra el dispositivo en sessions
        U-->>A: 200 perfil con rol
        A-->>CL: 200 perfil
    end

    CL->>A: PUT /notifications/directory/me con language
    A->>N: certificado + X-User-Id, X-User-Email
    N->>N: Guarda correo e idioma en directory
    N-->>CL: 200 userId, email, language

    opt Solo la web
        CL->>A: POST /notifications/hub/negotiate
        A->>N: certificado + X-User-Id
        N-->>CL: url del SignalR Service y accessToken para ese usuario
        CL->>SR: Conexión directa con ese token, sin pasar por APIM
        CL->>A: GET /notifications/templates
        Note over CL,A: 200 muestra el editor de plantillas, 403 lo oculta. Ver flujo 4
    end
```

- El directorio se reenvía al iniciar sesión y cada vez que la persona cambia el idioma. Así Notificaciones sabe a qué correo y en qué idioma escribir, sin preguntarle a Usuarios.
- APIM es de tier Consumption y no soporta WebSockets. Por eso el negotiate pasa por APIM y la conexión en vivo va directo a Azure SignalR Service, con la identidad dentro del token.
- Desde una vista previa de PR, la web redirige el login al dominio de producción, que es el único origen registrado en Google, y vuelve con el token. El destino del retorno se valida contra los dominios del proyecto.

## 2. Cambio de estado de una postulación hasta la notificación

Solo el cambio administrativo publica el evento. Cuando la persona mueve su propia tarjeta (`PUT /applications/{id}`), no se le avisa nada.

```mermaid
sequenceDiagram
    autonumber
    actor AD as Administrador
    participant A as APIM
    participant O as Ofertas y Postulaciones
    participant PG as PostgreSQL
    participant Q as Service Bus notificaciones-eventos
    participant N as Notificaciones
    participant DB as Cosmos DB notificaciones
    participant SR as SignalR Service
    participant F as FCM
    participant E as ACS correo
    actor P as Dueño de la postulación

    AD->>A: PUT /admin/applications/id/status con newStatus
    A->>A: validate-jwt y revisa si el correo es de un administrador
    alt No es administrador
        A-->>AD: 403 sin llegar al backend
    else Es administrador
        A->>O: certificado + X-User-Id, X-User-Email, X-User-Role admin
        O->>O: requireAdmin y transición de estado
        O->>PG: UPDATE job_applications
        O->>Q: Mensaje con messageId igual a eventId y subject application.status_changed
        Note over O,Q: Si el envío falla se registra en el log. La respuesta es 200 igual porque el cambio ya quedó guardado
        O-->>AD: 200 postulación actualizada
    end

    Q->>N: Entrega en modo PeekLock
    N->>N: Valida contra evento-notificacion.schema.json
    alt JSON inválido o fuera del esquema
        N->>Q: Dead-letter con InvalidJson o SchemaValidationFailed
    else Válido
        N->>DB: INSERT en notifications con índice único de eventId
        alt eventId ya existía
            N->>Q: Complete: duplicado, no se reenvía
        else Nuevo
            N->>DB: Lee idioma y correo del directorio y las plantillas, en caché 60 s
            par Canales en paralelo
                N->>SR: notification al usuario
                SR-->>P: Aviso en vivo si tiene la web abierta
            and
                N->>F: Push a los tokens registrados del usuario
                F-->>P: Notificación en Android
            and
                N->>E: Correo con asunto igual al title
                E-->>P: Correo
            end
            N->>Q: Complete
        end
    end

    P->>A: GET /notifications y PATCH /notifications/id/read
    A->>N: certificado + X-User-Id
    N-->>P: Historial con title y body en su idioma
```

- Si Mongo falla, Notificaciones espera 5 s y abandona el mensaje para que Service Bus lo reintente. Al agotar `MaxDeliveryCount`, Service Bus lo pasa a la dead-letter.
- Si un canal falla, se registra con su nombre y los demás siguen. El mensaje se completa igual, porque el aviso ya quedó guardado y se puede consultar por REST.
- El push solo llega si la app registró su token en `POST /notifications/devices`. Android todavía no lo hace en esta fase.
- Si un administrador cambia un estado hacia o desde `interested`, el mensaje no pasa el esquema y termina en la dead-letter (ver [arquitectura](arquitectura.md)).

## 3. Nueva oferta: solo a quien supera su mínimo de compatibilidad

Para recibir avisos, el usuario guarda antes sus alertas. El perfil de emparejamiento lo manda el cliente, porque Ofertas no le pide datos a Usuarios ni a CVs.

```mermaid
sequenceDiagram
    autonumber
    actor P as Usuario
    participant CL as Cliente
    participant A as APIM
    participant O as Ofertas y Postulaciones
    participant J as JSearch externo
    participant PG as PostgreSQL
    participant Q as Service Bus
    participant N as Notificaciones

    P->>CL: Activa alertas
    CL->>A: PUT /alerts con enabled, minMatch y perfil de emparejamiento
    A->>O: certificado + X-User-Id
    O->>PG: UPSERT alert_settings
    O-->>CL: 200

    alt Un administrador crea una oferta
        CL->>A: POST /jobs
        A->>O: certificado + X-User-Role admin
        O->>PG: INSERT job_offers
    else Importación cada dos días a las 6 a. m. o POST /jobs/refresh
        O->>J: 6 búsquedas configuradas
        J-->>O: Ofertas publicadas
        O->>PG: Inserta las nuevas y actualiza las repetidas por título y empresa
    end

    O->>PG: Lee alert_settings con enabled verdadero
    loop Cada usuario con alertas activas
        O->>O: CompatibilityCalculator: habilidades 40, ubicación 20, jornada 20, experiencia 20
        opt Puntaje mayor o igual a su minMatch
            O->>Q: job.new con userId, jobOfferId, title, company, location, modality y matchScore
        end
    end
    Note over O,Q: En la importación solo cuentan las ofertas nuevas de esa corrida, con un máximo de 3 avisos por usuario, las más compatibles

    Q->>N: job.new
    N->>N: Valida, guarda con eventId único y entrega por SignalR y push
    Note over N: job.new no se envía por correo hasta decidir las preferencias por canal
```

- Editar una oferta no vuelve a avisar.
- `POST /jobs/refresh` lo puede pedir cualquier usuario, pero entre una corrida y otra hay que esperar 10 minutos (429 `REFRESH_TOO_SOON`), porque cada corrida gasta 6 consultas del plan de JSearch.

## 4. Edición de plantillas de correo por el administrador

Las plantillas definen el `title` y el `body` de cada tipo de evento en español e inglés: son 8 en total. Se usan para el correo, el push y el historial, porque los textos no se guardan con el aviso, se arman al enviar o al consultar.

```mermaid
sequenceDiagram
    autonumber
    actor AD as Administrador
    participant W as Web
    participant A as APIM
    participant N as Notificaciones
    participant DB as Cosmos DB templates

    W->>A: GET /notifications/templates al montar el layout
    A->>A: validate-jwt y revisa si el correo es de un administrador
    alt No es administrador
        A-->>W: 403 sin llegar al backend
        W->>W: Oculta el menú del editor, sin mostrar error
    else Es administrador
        A->>N: certificado + X-User-Id, X-User-Email, X-User-Role admin
        N->>N: Política Admin: X-User-Role exactamente admin
        N->>DB: Lee las guardadas
        N-->>W: 8 plantillas. Las nunca editadas vienen con texto por defecto y updatedAt 0
        W->>W: Muestra el menú y la ruta /admin/notification-templates
    end

    AD->>W: Edita una plantilla e inserta marcadores del tipo
    W->>A: PUT /notifications/templates/type/language con title y body
    A->>N: certificado + X-User-Email, X-User-Role admin
    N->>N: Valida que cada marcador exista en data de ese tipo de evento
    alt Marcador no permitido
        N-->>W: 400 con errors.title o errors.body
        W->>W: Muestra el error debajo del campo
    else Válida
        N->>DB: Upsert con _id type:language, updatedAt en ms y updatedBy igual al correo
        N->>N: Vacía la caché de plantillas de esta instancia
        N-->>W: 200 plantilla guardada
    end
    Note over N: Los siguientes avisos de ese tipo e idioma usan el texto nuevo. Con varias instancias, las demás tardan hasta 60 s
```

- Marcadores válidos por tipo: `{{newStatus}}`, `{{jobTitle}}` y `{{company}}` en `application.status_changed`, `{{title}}` en `cv.generated`, etc. La lista exacta es `NotificationEventValidator.DataFields`, y una prueba la compara con el esquema del evento.
- Los valores se escapan para HTML al armar el correo. `newStatus`, `previousStatus` y `modality` se traducen al idioma del usuario, e `isPaid` sale como "gratis" o "de pago".
- La web es el único cliente con el editor. Android no lo tiene.
