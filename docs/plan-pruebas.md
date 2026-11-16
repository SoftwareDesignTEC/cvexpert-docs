# Plan de pruebas de punta a punta — 16 de noviembre de 2026

Este plan cubre cinco servicios y ambos clientes. **No se ejecutó ninguna E2E de este corte.** El [registro editable CSV](../evidencias/registro-e2e.csv) contiene una fila por caso con preparación, pasos, esperado, resultado real, entorno, revisión, evidencia y estado. La cobertura Postman es evidencia de diseño de pruebas.

## Preparación y seguridad de ejecución

1. Identificar entorno de ensayo autorizado y aislado, revisión efectiva de cada backend, gateway/políticas, Web y APK; usar los SHAs auditados como referencia, sin sustituir por ellos la revisión desplegada.
2. Preparar cuentas propia, ajena, administradora y sin instantánea; plantillas, ofertas, catálogo y dispositivos sintéticos. Mantener tokens, archivos y configuración privada fuera de Git.
3. Confirmar mapeos APIM nuevos con Cabrera y catálogo/plantilla minimal con responsables. El inventario histórico y el 401 informado no prueban un backend actualizado.
4. Duplicar el [entorno Postman](../postman/README.md). Las escrituras requieren allowWrites y base de ensayo explícita; IA, cargas y refresh además tienen habilitaciones particulares. No ejecutar escrituras contra producción ni autenticación sin ensayo autorizado.
5. Reservar tiempo para limpieza: IDs devueltos, baja de CV/ofertas/postulaciones, restauración de perfiles/alertas/plantillas y eliminación de blobs por su responsable. El evento ya publicado y la recarga externa no se deshacen con DELETE de una entidad.

FCM Android está integrado desde **0.9.5** (PR #43) y se incluye en este plan. Instalar la APK de distribución 0.9.5 o posterior desde Firebase, identificar versión/build/commit y dispositivo; una APK debug sin configuración Firebase no sustituye este ensayo. Plantillas/IA tienen antecedentes de error del 8 nov, pero su estado actual es no verificado. Ver [auditoría](auditoria.md). No se excluyen requisitos obligatorios por falta de implementación o evidencia.

## Casos y orden recomendado

| ID | Flujo | Preparación | Pasos | Resultado esperado |
| --- | --- | --- | --- | --- |
| E2E-01 | Autenticación Web/Android | Clientes main, cuentas de ensayo, audiencia y APK/revisión identificadas | Iniciar sesión en ambos; renovar sesión; cerrar sesión; abrir perfil propio | Acceso propio consistente; sin tokens expuestos; logout elimina acceso |
| E2E-02 | Perfiles y aislamiento | Dos cuentas y perfil sintético; respaldo del perfil | GET/PUT perfil; sesiones/exportación; repetir como cuenta ajena | Persistencia y sesiones válidas; cuenta ajena 403; exportación solo propia |
| E2E-03 | Legales y ayuda es/en | Token de ensayo para APIM | Consultar privacy/terms/help con lang es y en | 200, esquema y textos del idioma solicitado; no atribuir borradores legales como aprobados |
| E2E-04 | CV CRUD y plantillas | Plantilla existente; usuario propietario y ajeno | Listar plantillas; crear, leer, editar y eliminar CV; consultar con otra cuenta | 201/200/204 y 404 tras baja o por ajeno; ninguna pérdida de secciones |
| E2E-05 | Plantillas y PDF en clientes | CV sintético, foto y plantilla disponible | Abrir vista previa y exportar PDF Web/Android; cambiar plantilla | Contenido, saltos, foto y fechas legibles; archivo abre; renderizado en cliente sin endpoint PDF inventado |
| E2E-06 | IA de texto y experiencia | Proveedor habilitado en ensayo; cuota; allowAi | Generar texto es/en, expandir y traducir experiencia; enviar DTO inválido | Texto útil sujeto a revisión humana; 400 inválido; errores proveedor separados; no inventar trayectoria |
| E2E-07 | Generación de CV e IA | Plantilla minimal confirmada; proveedor y BD aislados | POST generate-cv sin title/templateId; verificar contenido y propietario; borrar por ID | 201 y CV persistido; datos del usuario; valores opcionales; ausencia de fechas revisada sin pérdida silenciosa |
| E2E-08 | Fotografías | allowUploads, PNG sintético, TXT y archivo >5 MiB; limpieza acordada | POST multipart válido; tipo inválido; exceso; sin identidad en ensayo | 201 URL pública HTTPS, 415, 413 y 401 según frontera; no usar foto personal; limpieza documentada |
| E2E-09 | Ofertas y recarga | Fuente externa de ensayo, cuota y espera; usuario/admin | Listar con filtros/paginación; crear/editar/borrar como admin; refresh; repetir dentro del intervalo | Esquemas y filtros correctos; no admin rechazado; refresh 200, 429 demasiado pronto o 503 deshabilitado según preparación |
| E2E-10 | Postulaciones propias | Oferta sintética sin postulación previa; dos cuentas | Postular; repetir; consultar con ajeno; cambiar columna propia; retirar | 201, duplicado 409, ajeno 404; transición propia persistida; no asumir evento administrativo |
| E2E-11 | Cambio administrativo y evento | Admin y usuario, cola aislada; acuerdo sobre interested | Cambiar estado por ruta admin; correlacionar eventId; probar hacia/desde interested por separado | Evento application.status_changed compatible; historial/canales; registrar rechazo por incompatibilidad como fallido si se reproduce |
| E2E-12 | Instantáneas y brecha general | Cuenta sin snapshot y otra propia; mercado configurado, certificado válido | GET sin snapshot; PUT input; GET paginado; probar otro usuario y mercado vacío | 409 inicial; 204 guardado; 200 con analysis, aislamiento y unresolved; vacío no prueba ausencia de brechas |
| E2E-13 | Brecha por oferta y niveles | Mapeo APIM confirmado; proyección sintética Python/SQL/Docker | Evaluate con y sin description/requirements; negar/contradecir niveles; oferta sin skills | 66.67% de nombres con fixture; déficit Python 1; sin texto sin extensión; conflicto sin nivel inventado; oferta vacía cobertura null |
| E2E-14 | Validaciones de brecha | Certificado e identidad válidos en ensayo | Enviar jobs vacío/repetido, nivel inválido, extra userId, query y >100 KiB | 400 o 413 según entrada; identidad ausente 401 y certificado inválido 403/handshake; no reflejar datos privados |
| E2E-15 | Recomendaciones y catálogo | Catálogo de ensayo con asociación única, ambigua y ausente; DB controlada | Recommendations con ausencias/sin ausencias; filtros y paginación de courses; caída DB aislada | Máximo 5 cursos por habilidad orden ID; duración null; consulted/not_needed; not_found/ambiguous vacíos; 503 diferenciado |
| E2E-16 | Clientes de brecha y cursos | Android main; Web solo main para flujo general; PR #51 aún pendiente | Android elegir CV/oferta, revisar niveles y catálogo por déficit; Web probar instantánea general; reservar nuevo Web para revisión integrada | IDs conservados; errores no convertidos en vacío; cursos por déficit no prometen nivel educativo; nueva Web no se atribuye a main |
| E2E-17 | Eventos a persistencia | Productor real habilitado, cola/BD de ensayo y correlación | Emitir cv.generated tras IA y guardado; job.new con alertas; status_changed admin; consultar historial | Evento aceptado, documento por destinatario e historial paginado; sin confundir solicitudes REST con entrega |
| E2E-18 | Evento de curso | Productor course.recommended no encontrado en main | Registrar bloqueo de emisión real; tras implementarlo, generar y correlacionar; mensaje de ensayo solo como prueba del consumidor | Productor compatible con contrato, duration textual y disparador acordado; mensaje manual no aprueba productor E2E |
| E2E-19 | Deduplicación y dead-letter | Cola aislada y autorización para publicar mensajes sintéticos | Reenviar mismo eventId; enviar mensaje inválido; consultar historial/DLQ depurados | Un documento por evento; duplicado sin nuevo aviso; inválido a DLQ con razón verificable |
| E2E-20 | Tiempo real Web | Web main, SignalR Azure, cuenta propia y otra | Negotiate; abrir conexión; emitir evento; marcar leído y leer contador; reconectar | Aviso y contador propios actualizados; aislamiento; diferencia entre negociación y entrega real |
| E2E-21 | FCM Android | APK de distribución 0.9.5 o posterior identificada, NOTIFICATIONS_ENABLED=true, google-services.json del mismo proyecto Firebase que el backend, permiso de notificaciones y teléfono de ensayo | Login y comprobar registro propio en devices; renovar y comprobar token; recibir primer/segundo plano; correlacionar notificationId con historial; tocar aviso; logout y comprobar baja antes de borrar sesión; cambiar cuenta | Registro/renovación/baja y aviso/navegación reales; notificationId corresponde al historial del destinatario, sin acceso ajeno; deshabilitado/permiso denegado explícitos |
| E2E-22 | Correo y plantillas | Destinatario de ensayo, ACS, admin y par tipo/idioma descartable | Editar/leer plantilla es/en; evento admitido por EmailTypes; verificar buzón y restaurar plantilla | Título/cuerpo e idioma correctos, HTML escapado; no admin 403; job.new sin correo según política actual |
| E2E-23 | Idiomas y Epoch | CV/eventos sintéticos con fechas conocidas y zona Costa Rica UTC-6 | Cambiar es/en; guardar/releer y exportar; fechas de mes/día e IA a medianoche | Enteros Epoch ms; orden temporal y mes estable; etiquetas correctas; registrar H-09 si cambia día/mes |
| E2E-24 | APIM identidad y roles | Gateway ensayo, cuentas admin/no admin y token de audiencia ajena/vencido | Sin token/inválido/vencido/audiencia ajena; suplantar headers; repetir rutas administrativas con ambos roles | 401 autenticación, 403 autorización; X-User-* derivados de token; traza saneada de ruta/destino/revisión |
| E2E-25 | Certificados y acceso directo | Cabrera provee ensayo mTLS y certificado ajeno, sin exportar claves | Sin certificado, ajeno y válido en frontera APIM→backend; comprobar vigencia/huella y salud | Rechazo acceso directo no autorizado; certificado permitido alcanza backend; sonda según exclusión; configuración por servicio |
| E2E-26 | Almacenamiento SQL Azure | Instancias de ensayo de Ofertas/Brecha; permiso lector de verificación | Crear oferta/snapshot; releer tras nueva sesión y comprobar datos mediante evidencia autorizada | Persistencia SQL, aislamiento y relaciones; no usar solo migraciones como evidencia |
| E2E-27 | Almacenamiento documental Azure | Cosmos API Mongo de ensayo y datos sintéticos | Guardar perfil/CV y consumir aviso; releer tras nueva sesión; correlacionar documento saneado | Persistencia de documentos y propiedad; idempotencia de aviso; revisión y cuenta de recurso registradas sin cadena de conexión |
| E2E-28 | Almacenamiento Blob Azure | Storage de ensayo, imagen sintética, limpieza autorizada | Subir foto; abrir URL devuelta y usar en CV/PDF; responsable elimina fixture | Objeto accesible según contrato público, contenido y tipo; sin PII, sin SAS/secretos publicados; limpieza acreditada |

## Procedimiento FCM en teléfono (E2E-21)

1. Instalar la APK de distribución **0.9.5 o posterior**, con NOTIFICATIONS_ENABLED=true y google-services.json del mismo proyecto Firebase que usa el backend. Identificar versión, build, commit y teléfono; aceptar POST_NOTIFICATIONS en Android 13+ y comprobar el canal de avisos. No guardar el archivo Firebase ni tokens en la evidencia.
2. Iniciar sesión con la cuenta propietaria de ensayo. Comprobar por evidencia privada autorizada que POST /notifications/devices registra el token para esa cuenta; observar directorio e historial de la misma identidad.
3. Provocar una renovación controlada del token y comprobar su nuevo registro. Registrar la acción usada y el resultado sin copiar el token. Al cerrar sesión, verificar la baja antes de eliminar la sesión y que cambiar de cuenta no entregue avisos ajenos.
4. Generar un evento desde un productor implementado y autorizado. Correlacionar eventId → aviso persistido → notificationId del push → historial backend. Un mensaje manual comprueba el consumidor, no acredita el productor.
5. Con la app en **primer plano**, comprobar aviso y campana; repetir con la app en **segundo plano**, abrir el aviso y verificar navegación al centro y pertenencia al usuario. Comprobar lectura/contador y que otra cuenta no acceda al aviso.
6. Registrar esperado/real, permisos, variante, fecha y evidencia en la fila E2E-21. Las pruebas REST de Postman y el código integrado no aprueban recepción real. Mantener el caso no ejecutado/bloqueado si falta cualquier preparación.

## Registro y criterio de resultado

En [registro-e2e.csv](../evidencias/registro-e2e.csv), completar **cada ejecución** con fecha/hora y zona, resultado real, entorno, revisión backend/APIM/clientes, evidencia depurada y ejecutor por alias. Agregar otra fila si se repite un caso en otra revisión o cliente, conservando la anterior.

Estados permitidos:

- **aprobado:** se ejecutaron todos los pasos, coinciden esperado y real y existe evidencia verificable.
- **fallido:** se ejecutó y hubo una diferencia reproducible; incluir incidente y alcance.
- **bloqueado:** una condición concreta impide ejecutar/completar; describir dependencia. E2E-18 está bloqueado por productor ausente, sin simular su aprobación.
- **no ejecutado:** caso preparado, sin corrida ni resultado; nunca convertir omisión de Newman en aprobado.

Los casos actuales están no ejecutados, salvo E2E-18 bloqueado por implementación. No se declara fallida una E2E sin haberla ejecutado. Una prueba de contrato, CI, MockWebServer o local con dobles no acredita Azure ni dispositivo. Si falla una dependencia a mitad del flujo, conservar pasos ejecutados y marcar el resultado según su alcance sin aprobar el flujo completo.

El contenido compartido excluye JWT, tokens de dispositivo, correos, CV completos, certificados privados y cadenas de conexión. Registrar alias de fixtures y correlación técnica depurada. Para eventos, correlacionar productor → cola → documento → canal; para el video, usar solamente casos ensayados con evidencia actual.
