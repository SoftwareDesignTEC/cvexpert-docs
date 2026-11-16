# Validación documental — 16 de noviembre de 2026

Entorno local Windows, Python **3.14.3** en `.docs-venv`, Node **24.21.0**, Newman **6.2.3**. La CI documental existente usa Python 3.12/Node 22; el resultado local no se atribuye a esos runtimes. La rama parte de main `61039b25ec18681ed8ff5ddfca326806e62c5c88`.

## Comandos y resultados

En esta sesión el alias `python.exe` de WindowsApps no se pudo iniciar. Se usó `py -m venv .docs-venv` y luego el intérprete `.docs-venv/Scripts/python.exe` para los comandos Python siguientes.

| Comprobación ejecutada | Resultado final |
| --- | --- |
| `python -m pip install -r requirements-docs.txt` (con el intérprete del entorno) | Instalación correcta de las dependencias documentadas; sin cambiar requirements. |
| `python scripts/sincronizar_contratos.py --check` | Correcto contra las fuentes remotas fijadas: cinco OpenAPI, tres originales Postman, esquema de eventos y guía (11 artefactos). También se ejecutó con `--clones .docs-venv/audit --check`: correcto. |
| `python scripts/generar_postman_desde_openapi.py --check` | Correcto: materialización reproducible y cuerpos JSON positivos válidos; multipart comprobado por separado. |
| `python scripts/generar_matriz.py --check` | Correcto: CSV y Markdown reproducibles, 51 operaciones. |
| `python scripts/validar_cobertura.py` | Correcto: cinco OpenAPI, referencias/operaciones, 4 ejemplos de eventos y negativas del esquema, 51 operaciones y 98 solicitudes, JSON/YAML, enlaces locales, entorno seguro y búsqueda de credenciales. |
| `node scripts/ejecutar_postman.cjs --sintaxis` | Correcto: scripts JavaScript generados compilables. |
| `node scripts/ejecutar_postman.cjs --comprobar-bloqueo` | Seleccionadas **98**, solicitudes HTTP **0**, omitidas **98**, aserciones **0**, fallos **0**. Es una comprobación de bloqueo, no 98 pruebas funcionales aprobadas. |
| `node scripts/verificar_multipart.cjs` | Servidor efímero **loopback**, archivos y respuestas **sintéticos**: **4 solicitudes, 13 aserciones, 0 fallos**. Comprueba archivo/boundary/MIME y casos 201/401/415/413. No contacta Azure ni ejecuta el backend CVs. |
| `git diff --check` | Sin errores de espacio en blanco. Revisión estructural adicional: 76 solicitudes previas conservadas con sus requests y expectativas anteriores; 22 nuevas. Cinco esquemas de respuesta cambian por el contrato fuente. Los enlaces de código fijados existen. Los 25 archivos del cambio están dentro del alcance; siete documentos reservados y docs/notificaciones.md, inventario APIM, seguridad de Cabrera y validador intactos. Las tres piezas locales no rastreadas preexistentes se excluyen del commit. |

Se ejecutaron los generadores sin `--check` al actualizar los artefactos. El sincronizador verificó SHA Git blob antes de copiar. Los tres Postman originales conservaron sus blobs; Usuarios, Ofertas y Notificaciones mantienen los contratos de main sin cambios de contenido respecto a la base documental.

## Incidencias de la validación resueltas

- La prueba de transporte detectó que `FormParam` de Newman no admite `upsert/update`. Se sustituyó por eliminar/agregar el campo y se repitió con éxito. Se conserva una prueba reproducible.
- El sandbox devolvió EACCES en TCP loopback; la prueba sintética se ejecutó con acceso local autorizado. El check remoto y la instalación también requirieron acceso de red fuera del sandbox. No se requirió ni utilizó un entorno productivo.
- El validador detectó enlaces relativos del histórico trasladado; se corrigieron sus destinos. También detectó como posible credencial una línea de código compacta que unía URL loopback y correo sintético: se formateó el código y se repitió la comprobación sin cambiar patrones ni excepciones del validador.
- Newman emite avisos DEP0176/DEP0044 de dependencias con Node 24. Los resultados indicados arriba no incluyen fallos por esos avisos.

## Excepción preexistente y límites

Se conserva la excepción acotada al blob `e12d3effe912a060c355606e60999c070c57eef7` de Usuarios: el validador normaliza **en memoria** el ejemplo YAML de dirección; el contrato copiado sigue siendo idéntico al original defectuoso. No se añadió ni amplió una excepción. La adaptación de nulos de respuesta CVs también es preexistente y está documentada en [auditoría](../docs/auditoria.md). No se modificó `scripts/validar_cobertura.py`.

No se ejecutaron pruebas autenticadas ni de escritura contra servicios reales: no se proporcionó un entorno aislado autorizado con identidades y fixtures. No se inspeccionó Azure en vivo ni se cambiaron recursos/configuraciones. Los jobs de GitHub se consultaron en lectura y se registraron con sus SHAs; las suites de otros repositorios no se reejecutaron en esta actualización. Los resultados históricos permanecen en [su registro](historico-corte-anterior.md).

[Registro E2E](registro-e2e.csv): 27 casos no ejecutados y uno bloqueado por productor `course.recommended` ausente. Ninguna aprobación E2E actual. [Guion](../video/guion.md): preparado para 4:50; sin grabación, aprobación o entrega acreditadas.
