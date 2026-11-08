#!/usr/bin/env python3
"""Materializa Postman desde contratos fijados y escenarios de integración."""
import argparse
import json
import re

from casos_postman import groups
from contratos import apim_routes, json_schema, operations, parameters, responses, specifications, standalone_schema, validate_body
from sincronizar_contratos import ROOT

COLLECTION = ROOT / "postman/cvexpert.postman_collection.json"
VARIABLE = re.compile(r"{{([A-Za-z0-9_]+)}}")
FIXTURES = {
    "templateId": "plantilla-de-prueba",
    "runCvTemplate": "plantilla-de-prueba",
    "fixtureJobId": "1",
    "fixtureDeviceToken": "ejemplo-token-solo-validacion",
    "runDeviceToken": "ejemplo-token-solo-validacion",
}


def script(event, source):
    return {"listen": event, "script": {"type": "text/javascript", "exec": source.strip().splitlines()}}


def name_for(case):
    service, method, route = case["key"]
    name = f"{service} | {method} {route}"
    return name + (" | " + case["title"] if "title" in case else "")


def body_for(case, spec, operation, success):
    schema = json_schema(spec, operation.get("requestBody", {}))
    if schema is None:
        if "body" in case:
            raise ValueError("Se definió un cuerpo para una operación sin JSON")
        return None
    body = json.dumps(case["body"], ensure_ascii=False, indent=2)
    if case["key"][0] == "cvs" and "{{templateId}}" in body:
        body = body.replace("{{templateId}}", "{{runCvTemplate}}")
    if success:
        if not case["body"]:
            raise ValueError("Falta un ejemplo funcional de solicitud")
        resolved = VARIABLE.sub(lambda match: FIXTURES[match[1]], body)
        validate_body(spec, schema, json.loads(resolved))
    return body


def response_schema(service, spec, schema):
    packaged = standalone_schema(spec, schema, postman=True)
    if service == "cvs":
        # FastAPI serializa con null los campos opcionales de estos DTO.
        nullable_fields = {
            "PersonalInfo": ("id", "phone", "address", "photoUrl", "bio", "birthDate"),
            "TemplateSection": ("column", "fields", "source", "itemFields"),
            "Certification": ("issuedAt", "credentialUrl"),
        }
        for name, fields in nullable_fields.items():
            properties = packaged.get("definitions", {}).get(name, {}).get("properties", {})
            for field in fields:
                if field in properties:
                    properties[field] = {"anyOf": [properties[field], {"type": "null"}]}
    return packaged


def make_item(case, specs, published, tests):
    key = case["key"]
    service, method, route = key
    spec, path, operation = specs[key]
    params = parameters(spec, path, operation)
    declared = responses(operation)
    codes = case.get("status", [int(code) for code in declared if re.fullmatch(r"2\d\d", code)])
    if not codes:
        raise ValueError("Operación sin código de éxito")
    if not case.get("status_only") and any(str(code) not in declared for code in codes):
        raise ValueError(f"Códigos fuera del contrato: {codes}")
    body = body_for(case, spec, operation, any(200 <= code < 300 for code in codes))

    path_parameters = {name for location, name in params if location == "path"}
    defaults = {"type": "notificationType", "language": "language"}
    if service == "usuarios":
        defaults["id"] = "profileId"
    path_vars = case.get("path_vars", {name: defaults[name] for name in sorted(path_parameters) if name in defaults})
    if set(path_vars) != path_parameters:
        raise ValueError("Variables de ruta incompletas")
    query = case.get("query", {parameter: value for parameter, value in (("page", "1"), ("pageSize", "10"))
                               if ("query", parameter) in params})
    if any(("query", parameter) not in params for parameter in query):
        raise ValueError("Parámetro de consulta fuera del contrato")
    role = case.get("role", "admin" if ("header", "X-User-Role") in params else "user")
    identity = service != "brecha-cursos" or route.startswith("/skills-gap")
    if route == "/health" or service == "usuarios" and not route.startswith("/profiles/"):
        identity = False
    config = {
        "operation": f"{service} {method} {route}",
        "service": service,
        "path": route,
        "published": key in published,
        "requiresApimJobRole": role == "admin" and route.startswith("/jobs"),
        "bodyVars": sorted(set(VARIABLE.findall(body or ""))),
        "pathVars": path_vars,
        "mode": case.get("mode"),
        "role": role,
        "identity": identity,
        "writes": case.get("writes", method in {"POST", "PUT", "PATCH", "DELETE"} and route != "/notifications/hub/negotiate"),
        "needs": sorted(set(path_vars.values()) | set(VARIABLE.findall(body or "")) | set(case.get("needs", []))),
        "reset": case.get("reset", []),
    }
    assertions = {
        "status": codes,
        "statusOnly": case.get("status_only", False),
        "schemas": {},
        "checks": case.get("checks", {}),
        "template": case.get("template", False),
        "updatedTemplate": case.get("updated_template", False),
        "capture": case.get("capture", {}),
        "captureFirst": case.get("capture_first"),
    }
    if not assertions["statusOnly"]:
        for code in codes:
            schema = json_schema(spec, declared[str(code)])
            if schema is not None:
                assertions["schemas"][code] = response_schema(service, spec, schema)
    request = {
        "method": method,
        "auth": {"type": "noauth"},
        "header": [{"key": "Accept", "value": "application/json"}],
        "url": "{{__base}}{{__route}}" + ("?" + "&".join(f"{k}={v}" for k, v in query.items()) if query else ""),
        "description": f"`{method} {route}` · {operation.get('summary', service)}",
    }
    if body is not None:
        request["header"].append({"key": "Content-Type", "value": "application/json"})
        request["body"] = {"mode": "raw", "raw": body, "options": {"raw": {"language": "json"}}}
    text = tests.replace("CASO", json.dumps(assertions, ensure_ascii=False, separators=(",", ":")), 1)
    return {
        "name": name_for(case),
        "protocolProfileBehavior": {"followRedirects": False, "disableCookies": True},
        "request": request,
        "event": [script("test", text)],
    }, config


def build():
    specs = operations(specifications())
    published = apim_routes()
    collection = {
        "info": {
            "_postman_id": "e6015db4-179b-55fb-8894-50f3ce77a1bd",
            "name": "CVExpert Fase II",
            "description": "Contratos de los cinco servicios. Configurar un entorno y seleccionar las carpetas según postman/README.md.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "auth": {"type": "noauth"},
        "event": [script("prerequest", (ROOT / "postman/preparar-solicitud.js").read_text(encoding="utf-8"))],
        "item": [],
    }
    tests = (ROOT / "postman/verificar-respuesta.js").read_text(encoding="utf-8")
    configs = {}
    covered = set()
    for group, cases in groups().items():
        items = []
        for case in cases:
            try:
                item, config = make_item(case, specs, published, tests)
                if item["name"] in configs:
                    raise ValueError("Nombre de solicitud duplicado")
            except (KeyError, ValueError, AssertionError) as error:
                raise ValueError(f"{name_for(case)}: {error}") from error
            configs[item["name"]] = config
            items.append(item)
            if "status" not in case:
                covered.add(case["key"])
        collection["item"].append({"name": group, "item": items})
    missing = specs.keys() - covered
    if missing:
        raise ValueError(f"Operaciones sin caso principal: {sorted(missing)}")
    collection["variable"] = [{"key": "configuracionCasos", "value": json.dumps(configs, ensure_ascii=False)}]
    return collection


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if COLLECTION.read_text(encoding="utf-8") != content:
            parser.exit(1, "Colección desactualizada. Ejecute scripts/generar_postman_desde_openapi.py.\n")
    else:
        COLLECTION.write_text(content, encoding="utf-8", newline="\n")
    print("OK colección Postman y cuerpos positivos")


if __name__ == "__main__":
    main()
