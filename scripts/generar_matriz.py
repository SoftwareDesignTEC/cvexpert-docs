#!/usr/bin/env python3
"""Vincula las operaciones OpenAPI con código, despliegue y escenarios Postman."""
import argparse
import csv
import io
import json

from contratos import apim_routes, json_schema, operations, parameters, responses, schema_label, specifications
from generar_postman_desde_openapi import build
from sincronizar_contratos import ROOT, sources

# Directorios de evidencia en los commits fijados. Las pruebas de origen son
# referencias de revisión, independientes de la ejecución central.
EVIDENCE = {
    "usuarios": ("src/main/java/cr/ac/tec/cvexpert/usuarios/controller", "src/test/java/cr/ac/tec/cvexpert/usuarios"),
    "cvs": ("app/api/routers", "tests"),
    "ofertas-postulaciones": ("src/main/java/com/cvexpert/ofertas/adapter/in/web", "src/test/java/com/cvexpert/ofertas/adapter/in/web"),
    "brecha-cursos": ("src", "test"),
    "notificaciones": ("src/Notificaciones.Api", "tests/Notificaciones.Tests"),
}
OBSERVED = {
    ("cvs", "GET", "/cvs"): "200 observado desde Android; backend/revisión sin traza",
    ("ofertas-postulaciones", "GET", "/jobs"): "200 observado desde Android; backend/revisión sin traza",
    ("brecha-cursos", "GET", "/skills-gap"): "409 SKILLS_INPUT_REQUIRED observado desde Android; backend/revisión sin traza",
}

# Informe fusionado de Cabrera (PR #3), sin IDs ARM exportados para estas rutas.
REPORTED_APIM = {
    ("cvs", "POST", "/cvs/ai/generate-text"),
    ("cvs", "POST", "/cvs/ai/generate-cv"),
    ("brecha-cursos", "POST", "/skills-gap/evaluate"),
    ("brecha-cursos", "POST", "/skills-gap/recommendations"),
    ("notificaciones", "GET", "/notifications/templates"),
    ("notificaciones", "GET", "/notifications/templates/{type}/{language}"),
    ("notificaciones", "PUT", "/notifications/templates/{type}/{language}"),
}


def access(service, method, route, params):
    headers = [name for (location, name), definition in params.items()
               if location == "header" and definition.get("required")]
    if route == "/health":
        return "Salud directa sin identidad de usuario", "Sonda local"
    if service == "brecha-cursos":
        required = " + X-User-Id" if route.startswith("/skills-gap") else ""
        role = "Usuario autenticado; proyecciones informativas sin verificar titularidad" if route in {"/skills-gap/evaluate", "/skills-gap/recommendations"} else "Dueño de instantánea" if required else "Consulta de catálogo"
        return "Certificado cliente APIM → App Service" + required, role
    if "X-User-Role" in headers:
        role = "Administrador"
    elif route.startswith(("/profiles/", "/applications")) or service == "cvs" and route.startswith("/cvs"):
        role = "Identidad propia y propiedad del recurso cuando aplica"
    elif service == "notificaciones":
        role = "Usuario autenticado con datos propios"
    elif route == "/alerts":
        role = "Usuario autenticado con configuración propia"
    else:
        role = "Consulta general"
    return (" + ".join(headers) or "Sin identidad de usuario en backend"), role


def inventory():
    manifest = sources()
    audit = json.loads((ROOT / "contratos/revisiones-auditoria.json").read_text(encoding="utf-8"))
    deployments = {}
    for repo in audit["repositorios"]:
        for job in repo["jobs_despliegue_consultados"]:
            if job["conclusion"] == "success" and any(
                step["conclusion"] == "success" and step["name"] in {
                    "Deploy to Azure App Service", "Deploy package with Entra token (no publish profile)", "Desplegar en App Service",
                } for step in job["steps"]
            ):
                deployments[repo["repositorio"]] = job["url"]
    collection = build()
    published = apim_routes()
    requests = {
        item["name"]: folder["name"]
        for folder in collection["item"]
        for item in folder["item"]
    }
    for (service, method, route), (spec, path, op) in operations(specifications()).items():
        info = manifest["servicios"][service]
        repo = f"https://github.com/{manifest['organizacion']}/{info['repo']}"
        revision = info["revision"]
        src, tests = EVIDENCE[service]
        params = parameters(spec, path, op)
        auth, role = access(service, method, route, params)
        codes = responses(op)
        successes = [code for code in codes if code.startswith("2")]
        errors = [code for code in codes if code.startswith(("4", "5"))]
        key = service, method, route
        mapping = published.get(key)
        public_route = mapping["ruta_publica"] if mapping else ""
        observation = f"Inventario histórico ARM cv-api/{mapping['operacion_apim']}; destino {mapping['destino']}" if mapping else "Sin ID ARM en el inventario conservado"
        reported = key in REPORTED_APIM
        if reported:
            observation += "; PR #3 informa registro y rechazo 401 sin token; sin traza autenticada ni revisión backend"
        if key in OBSERVED:
            observation += "; antecedente del corte 2026-11-08: " + OBSERVED[key]
        deployment = "Inventario APIM histórico; backend activo no verificado" if mapping else "Registro APIM informado en PR #3; backend activo no verificado" if reported else "Publicación APIM no acreditada"
        if mapping and mapping["rol_apim"] == "delete" and "X-User-Role" in auth:
            observation += "; la política elimina X-User-Role requerido por el backend"
        proof = "No ejecutado en esta actualización; escenario definido"
        if key == ("cvs", "GET", "/cvs"):
            proof += "; histórico corte 2026-11-08: APIM negativo 401"
        if service == "cvs" and (route == "/cvs" and method == "POST" or route == "/cvs/{id}"):
            proof += "; histórico corte 2026-11-08: ciclo local con dobles"
        if key == ("cvs", "GET", "/templates"):
            proof += "; histórico corte 2026-11-08: catálogo local con doble"
        if key in {("brecha-cursos", "GET", "/health"), ("brecha-cursos", "GET", "/skills-gap")}:
            proof += "; histórico corte 2026-11-08: Newman local; ver estado de entrega"
        name = f"{service} | {method} {route}"
        status = "Ruta implementada en main"
        if route.endswith("/negotiate"):
            status = "Implementado por SignalR; redirección Azure requiere configuración"
        if route == "/health":
            observation = "Prueba local directa; publicación APIM sin evidencia"
        if service == "usuarios" and route == "/help":
            observation += "; 401 previo observado antes de iniciar sesión"
        yield {
            "servicio": service,
            "repositorio": repo,
            "revision": revision,
            "sha_blob_openapi": info["sha"],
            "openapi": f"contratos/{service}.openapi.yaml",
            "origen": f"{repo}/blob/{revision}/{info['openapi']}",
            "metodo": method,
            "ruta_interna": route,
            "ruta_apim_confirmada": public_route,
            "ruta_apim_reportada": "/api/v1" + route if reported else "",
            "fuente_apim": "contratos/apim-rutas.json (corte 2026-11-08; incluye refresh del PR #4)" if mapping else "docs/seguridad-apim.md (PR #3, fusionado 2026-11-16)" if reported else "Sin evidencia de publicación",
            "canal": "APIM inventariado" if mapping else "APIM informado; confirmar mapeo en ensayo" if reported else "Backend definido; APIM por confirmar",
            "autenticacion_backend": auth,
            "autenticacion_apim": "Google ID Token; comprobar autorización real en ensayo" if mapping or reported else "Publicación no verificada",
            "permisos": role,
            "parametros": "; ".join(f"{loc}:{name}{'*' if definition.get('required') else ''}" for (loc, name), definition in params.items()),
            "solicitud": "multipart/form-data: file (binary)" if "multipart/form-data" in op.get("requestBody", {}).get("content", {}) else schema_label(json_schema(spec, op.get("requestBody", {}))),
            "respuestas_exito": ", ".join(f"{code} {schema_label(json_schema(spec, codes[code]))}" for code in successes),
            "errores_openapi": ", ".join(f"{code} {schema_label(json_schema(spec, codes[code]))}" for code in errors),
            "carpeta_postman": requests[name],
            "solicitud_postman": name,
            "implementacion": status,
            "despliegue": deployment,
            "evidencia_pipeline_despliegue": deployments.get(info["repo"], "Sin job de despliegue acreditado en la consulta; ver auditoría"),
            "prueba": proof,
            "evidencia_o_bloqueo": observation,
            "codigo": f"{repo}/tree/{revision}/{src}",
            "pruebas_origen": f"{repo}/tree/{revision}/{tests}",
        }


def csv_text(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def markdown(rows):
    manifest = sources()
    lines = [
        "# Matriz de trazabilidad — Fase II",
        "",
        "El [CSV](../contratos/matriz-trazabilidad.csv) vincula cada operación con la revisión, el código, las pruebas de origen, los parámetros, las respuestas de error y la solicitud exacta de Postman.",
        "",
        "Las rutas públicas corresponden al [inventario de APIM](../contratos/apim-rutas.json). Una ruta registrada identifica la configuración del gateway. El [estado de entrega](estado-entrega.md) identifica las llamadas ejecutadas. Los cambios de contrato y de implementación se detallan en la [auditoría](auditoria.md).",
        "",
        "Corte 2026-11-16. El inventario ARM conservado tiene fecha 2026-11-08 e incorpora refresh mediante el PR #4. Las rutas indicadas como «informadas» proceden del informe de Cabrera fusionado en PR #3, sin identificadores ARM nuevos. Un rechazo 401 no verifica el backend. No se ejecutaron E2E de estas revisiones en esta actualización; los resultados anteriores son históricos. El CSV conserva por separado ambas procedencias, el blob y la evidencia por operación.",
        "",
    ]
    for service, info in manifest["servicios"].items():
        subset = [row for row in rows if row["servicio"] == service]
        example = subset[0]
        lines.extend([
            f"## {info['title']} ({len(subset)})",
            "",
            f"[OpenAPI](../{example['openapi']}) · [Origen fijado]({example['origen']}) · [Código]({example['codigo']}) · [Pruebas de origen]({example['pruebas_origen']})",
            "",
            "| Operación interna | Ruta APIM registrada | Permisos | Solicitud | Respuesta de éxito | Carpeta Postman |",
            "| --- | --- | --- | --- | --- | --- |",
        ])
        for row in subset:
            apim = row['ruta_apim_confirmada'] or (row['ruta_apim_reportada'] + ' (informada; sin ID ARM)' if row['ruta_apim_reportada'] else '—')
            lines.append(f"| `{row['metodo']} {row['ruta_interna']}` | {apim} | {row['permisos']} | {row['solicitud']} | {row['respuestas_exito']} | {row['carpeta_postman']} |")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows = list(inventory())
    for name, content in (("contratos/matriz-trazabilidad.csv", csv_text(rows)), ("docs/matriz-trazabilidad.md", markdown(rows))):
        destination = ROOT / name
        if args.check:
            if destination.read_text(encoding="utf-8") != content:
                parser.exit(1, f"{name} desactualizado. Ejecute scripts/generar_matriz.py.\n")
        else:
            destination.write_text(content, encoding="utf-8", newline="\n")
    print(f"OK matriz: {len(rows)} operaciones")


if __name__ == "__main__":
    main()
