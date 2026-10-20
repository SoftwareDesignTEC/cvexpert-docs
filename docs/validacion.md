# Validación automática de la consolidación

Se incluye `scripts/validar_contratos.py` y un GitHub Actions `validar-contratos.yml`.

El validador **solo comprueba**:
1. Presencia de los cinco OpenAPI y lectura YAML.
2. Versión OpenAPI 3.x, `info`, rutas HTTP, unicidad de los `operationId` cuando existen y resolución de `$ref` locales (`#/...`).
3. Que el contrato de eventos es JSON válido y tiene un esquema JSON Schema Draft 2020-12 válido.

No valida la implementación de los endpoints, todos los detalles semánticos de OpenAPI ni la configuración real de APIM. Tampoco sustituye tests de integración o Postman.

Local:
```powershell
py -3 -m pip install -r requirements-contracts.txt
py -3 scripts/validar_contratos.py
```

En GitHub Actions se ejecuta al abrir un PR o al hacer cambios en los archivos de contratos.
