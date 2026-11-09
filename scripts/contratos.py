"""Acceso a las operaciones y los esquemas de los contratos fijados."""
import json
from pathlib import Path
from urllib.parse import unquote

import yaml
from openapi_schema_validator import OAS30Validator, OAS31Validator

from sincronizar_contratos import ROOT, sources

VERBS = {"get", "put", "post", "delete", "patch", "options", "head", "trace"}


class UniqueKeysLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        result = super().construct_mapping(node, deep=deep)
        if len(result) != len(node.value):
            raise ValueError(f"Clave YAML duplicada en {node.start_mark}")
        return result


def read_yaml(path: Path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeysLoader)


def specifications():
    return {
        service: read_yaml(ROOT / f"contratos/{service}.openapi.yaml")
        for service in sources()["servicios"]
    }


def apim_routes():
    inventory = json.loads((ROOT / "contratos/apim-rutas.json").read_text(encoding="utf-8"))
    return {
        (item["servicio"], item["metodo"], item["ruta_interna"]): {
            **item, "ruta_publica": inventory["prefijo"] + item["ruta_interna"],
        }
        for item in inventory["operaciones"]
    }


def operations(specs):
    return {
        (service, method.upper(), route): (spec, path, operation)
        for service, spec in specs.items()
        for route, path in spec["paths"].items()
        for method, operation in path.items()
        if method in VERBS
    }


def pointer(document, ref):
    if ref == "#":
        return document
    if not ref.startswith("#/"):
        raise ValueError(f"Se requiere una referencia local: {ref}")
    target = document
    for part in unquote(ref[2:]).split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        target = target[int(key)] if isinstance(target, list) else target[key]
    return target


def resolve(spec, value):
    seen = set()
    while "$ref" in value:
        ref = value["$ref"]
        if ref in seen:
            raise ValueError(f"Referencia circular al resolver {ref}")
        seen.add(ref)
        value = pointer(spec, ref)
    return value


def parameters(spec, path, operation):
    merged = {}
    for parameter in path.get("parameters", []) + operation.get("parameters", []):
        parameter = resolve(spec, parameter)
        merged[parameter["in"], parameter["name"]] = parameter
    return merged


def responses(operation):
    return {str(code): response for code, response in operation["responses"].items()}


def json_schema(spec, definition):
    return resolve(spec, definition).get("content", {}).get("application/json", {}).get("schema")


def schema_label(schema):
    if schema is None:
        return "—"
    if "$ref" in schema:
        return schema["$ref"].rsplit("/", 1)[-1]
    if schema.get("type") == "array":
        return f"array de {schema_label(schema['items'])}"
    return str(schema.get("type", "esquema inline"))


def standalone_schema(spec, schema, *, postman=False):
    """Empaqueta los esquemas alcanzables y mantiene referencias para evitar expansiones cíclicas."""
    definitions = {}

    def convert(value):
        if isinstance(value, list):
            return [convert(item) for item in value]
        if not isinstance(value, dict):
            return value
        if "$ref" in value:
            ref = value["$ref"]
            name = ref.rsplit("/", 1)[-1]
            if not ref.startswith("#/components/schemas/"):
                raise ValueError(f"Referencia de esquema no admitida: {ref}")
            if name not in definitions:
                definitions[name] = None
                definitions[name] = convert(pointer(spec, ref))
            sibling = {key: val for key, val in value.items() if key != "$ref"}
            return {**convert(sibling), "$ref": "#/definitions/" + name}
        result = {}
        for key, val in value.items():
            if key in {"example", "examples", "description", "default"}:
                continue
            if key in {"properties", "patternProperties", "dependentSchemas", "definitions", "$defs"}:
                result[key] = {name: convert(child) for name, child in val.items()}
            elif key in {
                "allOf", "anyOf", "oneOf", "not", "if", "then", "else", "prefixItems",
                "items", "contains", "additionalProperties", "propertyNames",
                "unevaluatedProperties", "unevaluatedItems",
            }:
                result[key] = convert(val)
            else:
                result[key] = val
        if postman:
            # Ajv 6 valida JSON Schema Draft 7. Los formatos de OpenAPI no son formatos de Ajv.
            if result.get("format") in {"int32", "int64", "float", "double", "password"}:
                result.pop("format")
            if result.pop("nullable", False):
                result = {"anyOf": [result, {"type": "null"}]}
        return result

    packaged = convert(schema)
    if definitions:
        packaged["definitions"] = definitions
    return packaged


def validate_body(spec, schema, body):
    validator = OAS31Validator if spec["openapi"].startswith("3.1") else OAS30Validator
    validator(standalone_schema(spec, schema), format_checker=validator.FORMAT_CHECKER).validate(body)
