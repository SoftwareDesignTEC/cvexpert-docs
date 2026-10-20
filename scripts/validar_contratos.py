#!/usr/bin/env python3
"""Validación estructural local, sin llamadas a servicios ni ejecución del backend."""
import json
from pathlib import Path
import sys

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SERVICIOS = ("usuarios", "cvs", "ofertas-postulaciones", "brecha-cursos", "notificaciones")
HTTP = ("get", "put", "post", "delete", "patch", "options", "head", "trace")

def resolve_local(pointer, doc):
    if not pointer.startswith("#/"):
        return  # Solo verificar referencias locales; externas requieren herramientas adicionales.
    node = doc
    for part in pointer[2:].split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or key not in node:
            raise ValueError(f"Referencia local no encontrada: {pointer}")
        node = node[key]

def walk_refs(value, doc):
    if isinstance(value, dict):
        if isinstance(value.get("$ref"), str):
            resolve_local(value["$ref"], doc)
        for child in value.values():
            walk_refs(child, doc)
    elif isinstance(value, list):
        for child in value:
            walk_refs(child, doc)

def main():
    errors = []
    total_ops = 0
    for name in SERVICIOS:
        path = ROOT / "contratos" / f"{name}.yaml"
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            assert isinstance(doc, dict), "la raíz debe ser un objeto YAML"
            assert str(doc.get("openapi", "")).startswith("3."), "no declara OpenAPI 3.x"
            assert isinstance(doc.get("info"), dict), "falta info"
            assert isinstance(doc.get("paths"), dict) and doc["paths"], "faltan paths"
            walk_refs(doc, doc)
            ops = []
            operation_ids = set()
            for route, definition in doc["paths"].items():
                assert route.startswith("/"), f"ruta inválida: {route}"
                assert isinstance(definition, dict), f"la ruta {route} no es un objeto"
                for method in HTTP:
                    operation = definition.get(method)
                    if operation is None:
                        continue
                    assert isinstance(operation, dict), f"operación {method} {route} inválida"
                    oid = operation.get("operationId")
                    if oid is not None:
                        assert oid not in operation_ids, f"operationId duplicado: {oid}"
                        operation_ids.add(oid)
                    ops.append(f"{method.upper()} {route}")
            assert ops, "no hay operaciones HTTP"
            total_ops += len(ops)
            print(f"OK  {name}: OpenAPI {doc['openapi']}, {len(ops)} operaciones")
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    event_file = ROOT / "eventos" / "evento-notificacion.schema.json"
    try:
        schema = json.loads(event_file.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        print("OK  evento-notificacion: JSON Schema Draft 2020-12")
    except Exception as exc:
        errors.append(f"evento-notificacion: {exc}")

    if errors:
        for err in errors:
            print(f"ERROR {err}", file=sys.stderr)
        return 1
    print(f"Validación estructural completada: 5 OpenAPI, {total_ops} operaciones y 1 esquema de evento.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
