# Reconciliación del PR #6 — 16 de noviembre de 2026

Se integra main `7457ce9b0b2abb22f46654147d745e1eac7347cf` (merge de PR #5) en la rama existente `docs/actualizacion-contratos-pruebas-fase2`, cuyo head previo era `00b8d5b84d4dfc3627bb66107b354c99a91a3e60`. Ancestro común `61039b25ec18681ed8ff5ddfca326806e62c5c88`. Se usa merge ordinario, sin rebase, force push, PR nuevo ni fusión de PR #6.

## Conflictos reales y criterio

Conflictos de contenido en **docs/auditoria.md**, **docs/estado-entrega.md**, **docs/plan-pruebas.md** y **postman/README.md**. Se compararon ancestro, rama de Justin y main de Samuel. Se mantiene el inventario y estructura de Justin (51 operaciones, 98 solicitudes y 28 casos); se integra la corrección de Samuel de FCM desde 0.9.5, con prueba real aún pendiente.

Los diagramas de arquitectura/flujos y el documento de almacenamiento se conservan. En los demás documentos de Samuel se hacen correcciones de frases concretas con evidencia; no se sustituyen por documentos antiguos. La descripción de FCM de main se conserva y se explicita la diferencia entre manejador implementado y recepción probada.

## Desactualizaciones corregidas y evidencia exacta

Las ubicaciones siguientes identifican las afirmaciones **antes de corregirlas**, en el commit aceptado de Samuel; son enlaces permanentes para revisar el motivo del cambio.

| Ubicación original | Diferencia y resolución | Evidencia |
| --- | --- | --- |
[docs/seguridad.md:44](https://github.com/SoftwareDesignTEC/cvexpert-docs/blob/7457ce9b0b2abb22f46654147d745e1eac7347cf/docs/seguridad.md#L44) | El diagnóstico de eliminación del rol de Ofertas del 8 nov se presentaba como vigente. Se conserva como antecedente y se cita la corrección informada del 13 nov, pendiente de prueba admin/no admin. | [seguridad-apim](../docs/seguridad-apim.md), [APIM](../docs/apim.md) |
[docs/seguridad.md:65](https://github.com/SoftwareDesignTEC/cvexpert-docs/blob/7457ce9b0b2abb22f46654147d745e1eac7347cf/docs/seguridad.md#L65) y [docs/seguridad.md:110](https://github.com/SoftwareDesignTEC/cvexpert-docs/blob/7457ce9b0b2abb22f46654147d745e1eac7347cf/docs/seguridad.md#L110) | CVs figuraba con certificado desactivado/por confirmar, pese al informe Required. Se distingue configuración consultada de App Service, huella del middleware y falta de verificación de vigencia/estado actual. | Tabla CVs de [seguridad-apim](../docs/seguridad-apim.md), [certificado-apim](../docs/certificado-apim.md), código fijado en auditoría |
[docs/despliegue.md:59](https://github.com/SoftwareDesignTEC/cvexpert-docs/blob/7457ce9b0b2abb22f46654147d745e1eac7347cf/docs/despliegue.md#L59) y [docs/arquitectura.md:125](https://github.com/SoftwareDesignTEC/cvexpert-docs/blob/7457ce9b0b2abb22f46654147d745e1eac7347cf/docs/arquitectura.md#L125) | «Hoy está apagado» o falta total de evidencia de despliegue de Brecha contradice un job exitoso. Se cita ese job y SHA, sin afirmar revisión actualmente activa o E2E. | [Job de despliegue de fab6c726…](https://github.com/SoftwareDesignTEC/cvexpert-ms-brecha-cursos/actions/runs/43138922188/job/130921348838) |
[docs/arquitectura.md:144](https://github.com/SoftwareDesignTEC/cvexpert-docs/blob/7457ce9b0b2abb22f46654147d745e1eac7347cf/docs/arquitectura.md#L144) | El inventario conservado ya incluye refresh; otras rutas tienen informes posteriores. Se separan inventario ARM, informe 401 y documentación de fotografías. La matriz añade esta última procedencia sin crear IDs ARM ni habilitar pruebas. | [Inventario](../contratos/apim-rutas.json), [APIM](../docs/apim.md), [matriz](../docs/matriz-trazabilidad.md) |
[docs/notificaciones.md:9](https://github.com/SoftwareDesignTEC/cvexpert-docs/blob/7457ce9b0b2abb22f46654147d745e1eac7347cf/docs/notificaciones.md#L9) | La implementación de 0.9.5 no acredita entrega real. Se mantiene la corrección de Samuel y se añade ensayo en teléfono/correlación. | [PR Android #43](https://github.com/SoftwareDesignTEC/cvexpert-mobile/pull/43), que declara push real pendiente |
| [docs/apim.md](../docs/apim.md) | La frase general «no reescribe códigos» contradecía su propia sección de errores del gateway/no JSON. Se acota a respuestas JSON del backend y se preservan las reglas descritas. | Sección «Errores del gateway» del mismo documento |
| [docs/certificado-apim.md](../docs/certificado-apim.md) | Enlace al filtro de Usuarios en main no coincide con el corte que lo ubica en PR #2. Se enlaza el commit de esa rama y se aclara su alcance. | SHA 7cb84d9ae5416569adb93d161a4a7b3cd84c1269 registrado en auditoría |

El índice y README reflejan esos mismos estados; el incidente de plantillas/HTTP 500 se mantiene histórico, no como fallo actual comprobado. Video conserva guion/checklist y apunta a la arquitectura aceptada. `docs/pendientes-samuel.md` se sustituye por [seguimiento-integracion.md](../docs/seguimiento-integracion.md), que elimina tareas resueltas y solo enumera verificaciones pendientes por referencia a la auditoría.

Los SHA y estados del corte original se mantienen en los metadatos; una sección `reconciliacion` añade el main integrado y estados verificados de PR #1/#3/#4/#5/#6. No se reauditan ni modifican los otros siete repositorios.

## Validación local posterior al merge de contenido

Windows, Python 3.14.3 en `.docs-venv`, Node 24.21.0 y Newman 6.2.3 ya instalados. Se usó el intérprete del entorno para los comandos Python.

| Comando | Resultado |
| --- | --- |
| `python scripts/sincronizar_contratos.py --check` | Correcto contra fuentes remotas: 11 artefactos |
| `python scripts/generar_postman_desde_openapi.py --check` | Correcto; colección y cuerpos positivos reproducibles |
| `python scripts/generar_matriz.py --check` | Correcto: 51 operaciones, CSV/Markdown coherentes |
| `python scripts/validar_cobertura.py` | Correcto: contratos, eventos, cobertura, enlaces y búsqueda de credenciales |
| `node scripts/ejecutar_postman.cjs --sintaxis` | Correcto |
| `node scripts/ejecutar_postman.cjs --comprobar-bloqueo` | 98 seleccionadas/omitidas, **0 HTTP, 0 aserciones y 0 fallos** |
| `node scripts/verificar_multipart.cjs` | Loopback sintético: **4 solicitudes, 13 aserciones y 0 fallos** |
| `git diff --check` | Sin errores de espacios ni marcadores |
| Revisión estructural adicional | 22 artefactos de Justin idénticos al head previo, incluidos cinco OpenAPI, colección, controles, scripts de pruebas y el histórico. Diagramas de arquitectura/flujos y almacenamiento de Samuel conservados. Los tres archivos locales no rastreados coinciden con su respaldo. |

Sin marcadores `<<<<<<<`, `=======` ni `>>>>>>>` como delimitadores en los archivos revisados; referencias locales validadas y sin enlaces al archivo retirado. Las 28 filas E2E conservan sus estados: **27 no ejecutadas y una bloqueada**, sin nuevas aprobaciones. E2E-21 amplía preparación/pasos/esperado y conserva resultado real y evidencia pendientes.

Se mantiene la excepción preexistente de Usuarios para el ejemplo YAML del blob e12d3eff… y la adaptación preexistente de nulos CVs; el validador no se modificó ni debilitó. Newman emite avisos DEP0176/DEP0044 de dependencias con Node 24, sin fallos finales. La sincronización remota y la prueba TCP loopback se ejecutaron con el acceso requerido por el sandbox; no se contactaron APIs productivas ni se usaron credenciales de ensayo.

## Riesgos que permanecen

Pruebas autenticadas de roles/mTLS, revisión activa en Azure, recepción FCM real y correlación, productor course.recommended, compatibilidad interested y correcciones de contratos/fechas permanecen sin acreditar o pendientes en su alcance original. La [auditoría](../docs/auditoria.md) mantiene su evidencia; la CI documental no sustituye E2E.

La mergeabilidad y la nueva CI se comprueban en GitHub después del push; su resultado se registra en la descripción del PR y en el informe de entrega, sin fusionarlo.
