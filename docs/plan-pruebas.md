# Plan de pruebas End-to-End y criterios de aceptación

## Condiciones previas

- APIM accesible con las políticas previstas y los backends desplegados.
- Token de Google **válido**, no vencido y emitido para la audiencia permitida por APIM; nunca guardarlo en Git.
- Cuenta de usuario, cuenta de administrador y datos de prueba **aislados** (CV, vacante, postulación, notificación y dispositivo).
- Confirmación del prefijo de rutas y de disponibilidad pública por operación.
- JSON de ejemplo validado contra cada DTO OpenAPI; ejecutar `scripts/generar_postman_desde_openapi.py` tras sincronizar.
- Las llamadas de modificación se ejecutarán sobre un entorno de pruebas bajo control del equipo.

## Ejecución

1. Ejecutar solicitudes GET de catálogo y perfil; comprobar `200`, cuerpo y aislamiento por usuario.
2. Crear y recuperar un CV, editarlo, probar IA según disponibilidad y eliminar el recurso creado.
3. Consultar ofertas; crear/postular con usuario; actualizar postulación y revisar autorización admin antes de borrarla.
4. Guardar instantánea de habilidades (`PUT /skills-gap/input`) y luego consultar brecha; probar `409 SKILLS_INPUT_REQUIRED` por separado cuando falten habilidades.
5. Registrar usuario en directorio y dispositivo; generar/listar/leer notificaciones; validar SignalR, push y correo por flujos E2E donde aplique.
6. Comprobar escenarios negativos `401`, `403`, `404` y `409` sin aceptar un error como resultado de éxito.
7. Guardar informes Newman / Collection Runner redactados y capturas de APIM/Swagger.

## Criterio de aceptación para afirmar «Postman completo»

- Hay al menos una solicitud y una aserción útil por endpoint **expuesto**.
- Todas las pruebas de escenario feliz se ejecutaron y pasaron en el gateway real; cada `skip` tiene justificación documentada.
- Los casos de escritura tienen cuerpos válidos y no alteran datos productivos.
- Existen evidencias de seguridad gateway → backend y permisos de usuario/administrador.
- Los 45 elementos del inventario se reconciliaron con operaciones de APIM; las no expuestas quedaron explícitamente justificadas.

**Estado actual:** cobertura estructural creada, sin ejecución de pruebas E2E en este paquete.
