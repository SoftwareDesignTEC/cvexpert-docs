#!/usr/bin/env python3
"""Comprueba contratos, procedencia, cobertura, enlaces y credenciales accidentales."""
import copy
import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

from jsonschema import Draft202012Validator
from openapi_spec_validator import OpenAPIV30SpecValidator, OpenAPIV31SpecValidator

from contratos import apim_routes, operations, pointer, read_yaml, specifications
from generar_matriz import csv_text, inventory, markdown
from generar_postman_desde_openapi import COLLECTION, build
from sincronizar_contratos import ROOT, artifacts, git_blob_sha, sources

LINK = re.compile(r"(?<!!)\]\((<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\)")
SECRET_PATTERNS = {
    "clave privada": r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----",
    "JWT": r"\beyJ[A-Za-z0-9_-]{9,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{16,}\b",
    "token GitHub": r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b",
    "token Google": r"\b(?:ya29\.[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{35}|GOCSPX-[A-Za-z0-9_-]{20,})\b",
    "credencial AWS": r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    "cadena de conexión con credenciales": r"(?:SharedAccessKey|AccountKey)=[A-Za-z0-9+/]{16,}={0,2}|://[^/\s:@]+:[^/\s@]+@[^/\s]+",
    "token FCM": r"\b[A-Za-z0-9_-]{15,}:APA91[A-Za-z0-9_-]{50,}\b",
}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def inspect_refs(value, root):
    if isinstance(value, dict):
        if "$ref" in value:
            pointer(root, value["$ref"])
        for child in value.values():
            inspect_refs(child, root)
    elif isinstance(value, list):
        for child in value:
            inspect_refs(child, root)


def validate_sources(manifest):
    for info, path, expected, dest in artifacts(manifest):
        if info == manifest["guia_notificaciones"]:
            continue  # El README incorpora enlaces centrales y se verifica con el sincronizador.
        check(git_blob_sha((ROOT / dest).read_bytes()) == expected, f"{dest}: blob distinto de {info['revision']}:{path}")


def validate_openapi(service, spec, manifest):
    inspect_refs(spec, spec)
    ids = [op["operationId"] for _, _, op in operations({service: spec}).values() if "operationId" in op]
    duplicated = [name for name, count in Counter(ids).items() if count > 1]
    check(not duplicated, f"operationId duplicado: {duplicated}")
    validator = OpenAPIV31SpecValidator if spec["openapi"].startswith("3.1") else OpenAPIV30SpecValidator
    if service == "usuarios" and manifest["servicios"][service]["sha"] == "e12d3effe912a060c355606e60999c070c57eef7":
        # Excepción acotada al blob de origen. Al actualizarlo, se vuelve a validar directamente.
        spec = copy.deepcopy(spec)
        address = spec["components"]["schemas"]["UserProfile"]["properties"]["address"]
        check(address.get("example") == "Ciudad Quesada" and "Alajuela" in address and address["Alajuela"] is None,
              "La excepción de ejemplo de dirección ya no coincide")
        address.pop("Alajuela")
        address["example"] += ", Alajuela"
        print("AVISO usuarios: se normaliza en memoria el ejemplo de dirección del blob fijado; corrección pendiente en origen")
    validator(spec).validate()


def validate_event():
    schema = json.loads((ROOT / "contratos/evento-notificacion.schema.json").read_text(encoding="utf-8"))
    inspect_refs(schema, schema)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
    guide = (ROOT / "contratos/notificaciones.origen.md").read_text(encoding="utf-8")
    examples = [json.loads(example) for example in re.findall(r"```json\s*\n(.*?)```", guide, flags=re.S)]
    examples = {event["type"]: event for event in examples if "schemaVersion" in event}
    check(set(examples) == set(schema["properties"]["type"]["enum"]), "La guía debe incluir un ejemplo de cada tipo de evento")
    for event in examples.values():
        validator.validate(event)
    course = examples["course.recommended"]
    for field in ("schemaVersion", "eventId", "type", "userId", "occurredAt", "source", "data"):
        invalid = dict(course)
        invalid.pop(field)
        check(not validator.is_valid(invalid), f"El sobre debe requerir {field}")
    for alteration in ({"source": "cvs"}, {"eventId": "no-es-uuid-v4"}, {"schemaVersion": 2}, {"extra": True}):
        check(not validator.is_valid({**course, **alteration}), "El sobre acepta un valor inválido")
    required = ("title", "platform", "url", "isPaid")
    for field in required:
        invalid = copy.deepcopy(course)
        invalid["data"].pop(field)
        check(not validator.is_valid(invalid), f"course.recommended debe requerir {field}")
    for field, value in (("url", "ftp://example.com/curso"), ("isPaid", "true")):
        invalid = copy.deepcopy(course)
        invalid["data"][field] = value
        check(not validator.is_valid(invalid), f"course.recommended acepta un valor inválido en {field}")
    minimal = {**course, "data": {field: course["data"][field] for field in required}}
    validator.validate(minimal)
    validator.validate({**minimal, "data": {**minimal["data"], "duration": None, "skill": None}})
    print(f"OK esquema de evento y {len(examples)} ejemplos; casos inválidos de curso rechazados")


def git_files():
    return subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT).decode("utf-8").split("\0")


def headings(text):
    slugs = set()
    for heading in re.findall(r"^#{1,6}\s+(.+)$", text, re.M):
        value = unicodedata.normalize("NFC", heading).strip().lower()
        slug = re.sub(r"[^\w\- ]", "", value).replace(" ", "-")
        unique = slug
        index = 1
        while unique in slugs:
            unique = f"{slug}-{index}"
            index += 1
        slugs.add(unique)
    return slugs


def validate_links(path, text):
    markdown = re.sub(r"```[^\n]*\n.*?^\s*```", "", text, flags=re.M | re.S)
    for raw in LINK.findall(markdown):
        link = urlsplit(raw.strip("<>"))
        if link.scheme or link.netloc:
            continue
        target = (path.parent / unquote(link.path)).resolve() if link.path else path
        check(target.is_relative_to(ROOT) and target.exists(), f"enlace local roto: {raw}")
        if link.fragment and target.suffix == ".md":
            check(unquote(link.fragment) in headings(target.read_text(encoding="utf-8")), f"ancla local no encontrada: {raw}")


def validate_files():
    for name in sorted(set(git_files()) - {""}):
        path = ROOT / name
        if not path.is_file() or path.suffix not in {".json", ".yaml", ".yml", ".md", ".js", ".cjs", ".py", ".csv", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
            for label, pattern in SECRET_PATTERNS.items():
                match = re.search(pattern, text)
                check(not match, f"posible {label} (línea {text.count(chr(10), 0, match.start()) + 1 if match else '—'})")
            if path.suffix == ".json":
                json.loads(text)
            if path.suffix in {".yaml", ".yml"}:
                read_yaml(path)
            if path.suffix == ".md":
                validate_links(path, text)
        except (OSError, ValueError) as error:
            raise ValueError(f"{name}: {error}") from error
    environment = json.loads((ROOT / "postman/apim.postman_environment.json").read_text(encoding="utf-8"))
    values = {entry["key"]: entry["value"] for entry in environment["values"]}
    for key, value in values.items():
        if key.endswith("Token") or key.endswith("Email"):
            check(value == "", f"El entorno de ejemplo debe dejar vacío {key}")
    for flag in ("allowWrites", "allowAdmin", "allowDirect", "enableApim", "localSignalR", "allowApimJobAdmin"):
        check(values[flag] == "false", f"El entorno de ejemplo debe desactivar {flag}")
    print("OK JSON/YAML, enlaces locales, entorno seguro y búsqueda de credenciales")


def validate_coverage():
    snapshot = json.loads((ROOT / "contratos/apim-rutas.json").read_text(encoding="utf-8"))
    published = apim_routes()
    check(len(published) == len(snapshot["operaciones"]), "Rutas APIM duplicadas")
    check(published.keys() <= operations(specifications()).keys(), "El inventario APIM refiere operaciones fuera de los contratos")
    actual = json.loads(COLLECTION.read_text(encoding="utf-8"))
    check(actual == build(), "La colección difiere de los escenarios. Ejecute scripts/generar_postman_desde_openapi.py")
    count = 0
    for folder in actual["item"]:
        for item in folder["item"]:
            check(any(event["listen"] == "test" and event["script"]["exec"] for event in item["event"]),
                  f"Sin prueba: {item['name']}")
            count += 1
    rows = list(inventory())
    for path, expected in (("contratos/matriz-trazabilidad.csv", csv_text(rows)), ("docs/matriz-trazabilidad.md", markdown(rows))):
        check((ROOT / path).read_text(encoding="utf-8") == expected, f"{path}: ejecute scripts/generar_matriz.py")
    print(f"OK correspondencia: {len(rows)} operaciones y {count} solicitudes Postman con aserciones")


def main():
    try:
        manifest = sources()
        validate_files()
        validate_sources(manifest)
        for service, spec in specifications().items():
            try:
                validate_openapi(service, spec, manifest)
            except Exception as error:
                raise ValueError(f"OpenAPI {service}: {error}") from error
            print(f"OK OpenAPI {service} {spec['openapi']}")
        validate_event()
        validate_coverage()
    except Exception as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
