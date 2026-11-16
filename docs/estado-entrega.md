# Estado de entrega — corte 16 de noviembre de 2026

## Artefactos actuales

Cinco OpenAPI sincronizados desde main y comprobados por commit/blob; tres colecciones originales conservadas con los mismos blobs, esquema de eventos y guía de Notificaciones igualmente fijados. [Fuentes](../contratos/fuentes.json) · [Auditoría de ocho repositorios](auditoria.md).

La [matriz](matriz-trazabilidad.md) contiene **51 operaciones** (7 Usuarios, 12 CVs, 14 Ofertas/Postulaciones, 6 Brecha/Cursos, 12 Notificaciones). La [colección Postman](../postman/README.md) contiene **98 solicitudes**, con caso principal por operación y escenarios adicionales. Se conservan los flujos previos y refresh del PR #4. El inventario ARM conservado tiene 41 entradas; seguridad-apim.md informa otras siete rutas y su rechazo 401, y apim.md documenta además fotografías. Son fuentes documentales separadas, sin IDs ARM nuevos. Reconocimiento/401 no demuestra backend ni resultado E2E.

## Estado por capacidad

| Capacidad | Integrado en main | Evidencia de despliegue / ejecución | Situación actual E2E |
| --- | --- | --- | --- |
| Usuarios | Perfil, sesiones, legales, ayuda; 7 operaciones | No hay runs main en la consulta. Certificado/Swagger/Postman/CI-CD: PR #2 abierto | No verificada; requiere entorno y cuentas de ensayo |
| CVs/plantillas/IA/fotos | Doce operaciones y pruebas con dobles; siembra disponible como script | CD exitoso de 144e0d67… el 14 nov; no acredita catálogo cargado ni respuesta del proveedor | No verificada. Incidente 8 nov conservado como histórico, sin cierre E2E posterior |
| Ofertas/postulaciones | Refresh, filtros, initialStatus/interested, administración y eventos | CI main exitoso; informe APIM conservado, sin SHA de backend activo | No verificada; interested requiere compatibilidad con receptor |
| Brecha/recomendaciones | Seis operaciones, niveles explícitos, catálogo e importadores locales | Job de despliegue de fab6c726… exitoso el 11 nov (Costa Rica); sin traza autenticada actual | No verificada. Sincronización ampliada sigue en develop; course.recommended sin productor |
| Notificaciones | Eventos, persistencia, directorio, dispositivos, SignalR, ACS y plantillas | Deploy y health exitosos de 5ea5ee82… el 12 nov (Costa Rica); README informa pruebas históricas | No verificada en el corte; reportes históricos no equivalen a entrega actual por todos los canales |
| Android | FCM desde 0.9.5 (PR #43), ambos POST por oferta, niveles y catálogo contextual | Release firmada subida a Firebase por pipeline ab51927d… (UTC 16 nov; Costa Rica 16 nov) | Login y recepción push no acreditados en esta revisión |
| Web | CVs/IA/fotos, ofertas, instantáneas y notificaciones | Build/deploy exitoso de 9f024264… el 14 nov | No verificada. Brecha por oferta/catálogo e interfaz nueva: PR #51/#52 abiertos |

Los enlaces a jobs y timestamps UTC originales están en [revisiones-auditoria.json](../contratos/revisiones-auditoria.json). No se consultó la configuración actual de Azure ni se enviaron solicitudes a servicios productivos.

## Validación de esta actualización

Resultados reproducibles en [evidencia documental del 16 nov](../evidencias/validacion-2026-11-16.md). Las validaciones de archivos, esquemas, procedencia, sintaxis y bloqueo Newman acreditan los artefactos documentales; no aprueban flujos E2E. La normalización en memoria del ejemplo YAML de Usuarios sigue acotada al blob original y su corrección corresponde al servicio.

## Resultados anteriores conservados

El [registro histórico](../evidencias/historico-corte-anterior.md) conserva las cifras y el alcance originales de Newman local/APIM y suites de servicios reportadas en el corte anterior. No se reasignan a los SHAs del 16 de noviembre. Las observaciones Android debug de 200 en CVs/Jobs y 409 SKILLS_INPUT_REQUIRED carecen de traza de revisión backend; no certifican APK de distribución.

La comunicación del 8 nov sobre plantillas pendientes, HTTP 500 de IA y Android 0.7.2 es histórica. El código y los pipelines posteriores cambian la clasificación de implementación, pero no aportan una ejecución E2E que cierre esos incidentes. La antigua clasificación de todo FCM Android como trabajo futuro se reemplaza por **integrado desde Android 0.9.5; recepción real no verificada**. La APK 0.7.2 y las pruebas debug anteriores no acreditan 0.9.5 ni una versión posterior; se requiere APK de distribución compatible con Firebase y prueba en un teléfono.

## Pendientes de acreditación

- Entorno aislado autorizado, identidades propietaria/ajena/admin/sin instantánea, revisión activa y datos sintéticos antes de pruebas autenticadas o escrituras.
- Cabrera: inventario ARM actual con IDs reales, política de rol para ofertas/plantillas, trazas autenticadas, mTLS/huellas y configuración efectiva de Ofertas; aclarar Usuarios desplegado frente a PR #2.
- Responsables de servicios: hallazgos H-01–H-09 de la auditoría; confirmar plantillas/IA y catálogo con datos elegibles, sin activar cargas por esta tarea.
- Brecha/Notificaciones: productor course.recommended, transformación del payload e idempotencia. La sincronización de cursos develop/PR #33 requiere su propia integración.
- Android/Notificaciones: registro, renovación, baja, primer/segundo plano y navegación mediante prueba en dispositivo. Web: esperar integración de PR #51/#52 para presentar esos cambios como main.
- Integración documental: PR #5 ya fusionado en 7457ce9b0b2abb22f46654147d745e1eac7347cf; PR #6 integra ese main y conserva [seguimiento vigente](seguimiento-integracion.md).
- Justin: ejecutar y registrar la [matriz E2E](plan-pruebas.md), ensayar el [guion](../video/guion.md) y completar [checklist](../video/checklist.md). El video no está grabado, aprobado ni entregado por esta tarea.
