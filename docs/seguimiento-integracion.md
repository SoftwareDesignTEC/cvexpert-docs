# Seguimiento de integración

El PR #5 fue fusionado en main mediante 7457ce9b0b2abb22f46654147d745e1eac7347cf. FCM Android desde 0.9.5 ya está descrito correctamente; se retiraron las observaciones que pedían integrar esa documentación. Este archivo sustituye pendientes-samuel.md y conserva únicamente verificaciones vigentes, sin duplicar los hallazgos H-01–H-10 de la [auditoría](auditoria.md).

| Verificación pendiente | Ubicación y evidencia | Acción / responsable |
| --- | --- | --- |
| Autorización real de Ofertas/plantillas | [Seguridad, rol](seguridad.md#de-dónde-sale-el-rol); [informe de Cabrera](seguridad-apim.md) y [APIM](apim.md) informan correcciones del 13 nov. | Cabrera y ensayo: comprobar tokens admin/no admin, sobrescritura de identidad y traza. No tratar el diagnóstico del 8 nov como vigente. |
| Certificado de CVs | [Tabla por servicio](seguridad.md#3-certificado-de-cliente-de-apim-hacia-los-backends); informe Required con /health excluido frente al middleware que solo valida huella. | CVs/Cabrera: verificar vigencia en aplicación y configuración actual, con evidencia autenticada; no equiparar controles de App Service y middleware. |
| Revisión desplegada frente a main | [Estado de entrega](estado-entrega.md), H-08 y jobs fijados en [metadatos](../contratos/revisiones-auditoria.json). | Backends/Cabrera: identificar artefacto activo, especialmente Usuarios y su filtro aún fuera del main del corte original. Un job exitoso no prueba revisión activa actual. |
| Inventario ARM completo y fotografías | [Matriz](matriz-trazabilidad.md), [APIM](apim.md) documenta fotos; informe 401 y exportación ARM son evidencias distintas. | Cabrera: aportar IDs ARM reales, mapeos y trazas autenticadas. Mantener overrides de ensayo hasta confirmarlos. |
| Recepción FCM, identidad y correlación | [E2E-21 y procedimiento](plan-pruebas.md#procedimiento-fcm-en-teléfono-e2e-21); PR #43 Android indica push real pendiente. | Android/Notificaciones: ejecutar en teléfono y registrar resultado; integración 0.9.5 no equivale a entrega E2E. |
| Compatibilidad y productores | H-05/H-06: course.recommended sin productor e interested incompatible con receptor en el corte. | Brecha, Ofertas y Notificaciones: acordar cambios y probar productor → historial → canales. |
| Contratos y fechas | H-01/H-02/H-03/H-09; la sincronización conserva el origen. | Cada servicio: corregir origen y aportar evidencia antes de actualizar copias. |
| Integraciones fuera de main en el corte | PR Web #51/#52 y Brecha develop/#33 registrados con SHA histórico en auditoría. | Sus responsables: verificar integración/revisión vigente antes de presentarlos como terminados. Esta reconciliación no vuelve a auditar esos repositorios. |

Las ubicaciones exactas de las contradicciones corregidas, sus fuentes y las validaciones del merge se registran en [reconciliación del PR #6](../evidencias/reconciliacion-pr6.md).
