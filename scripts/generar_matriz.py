#!/usr/bin/env python3
"""Vincula las operaciones OpenAPI con código, despliegue y escenarios Postman."""
import argparse
import csv
import io

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


def access(service, method, route, params):
    headers = [name for (location, name), definition in params.items()
               if location == "header" and definition.get("required")]
    if route == "/health":
        return "Salud directa sin identidad de usuario", "Sonda local"
    if service == "brecha-cursos":
        required = " + X-User-Id" if route.startswith("/skills-gap") else ""
        role = "Dueño de instantánea" if required else "Consulta de catálogo"
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
        observation = f"ARM cv-api/{mapping['operacion_apim']}; destino {mapping['destino']}" if mapping else "Sin operación registrada en el inventario APIM"
        if key in OBSERVED:
            observation += "; " + OBSERVED[key]
        deployment = "Registrada en APIM; revisión backend pendiente" if mapping else "Sin publicación registrada"
        if route.startswith("/jobs") and method != "GET" and mapping and mapping["rol_apim"] == "delete":
            observation += "; la política elimina X-User-Role requerido por el backend"
        proof = "Escenario positivo APIM pendiente" if mapping else "Escenario backend definido"
        if key == ("cvs", "GET", "/cvs"):
            proof = "APIM negativo 401 ejecutado; positivo actual pendiente"
        if service == "cvs" and (route == "/cvs" and method == "POST" or route == "/cvs/{id}"):
            proof = "Ciclo local con dobles ejecutado; APIM pendiente"
        if key == ("cvs", "GET", "/templates"):
            proof = "Catálogo local con doble ejecutado; APIM pendiente"
        if key in {("brecha-cursos", "GET", "/health"), ("brecha-cursos", "GET", "/skills-gap")}:
            proof = "Newman local ejecutado; ver estado de entrega"
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
            "openapi": f"contratos/{service}.openapi.yaml",
            "origen": f"{repo}/blob/{revision}/{info['openapi']}",
            "metodo": method,
            "ruta_interna": route,
            "ruta_apim_confirmada": public_route,
            "canal": "APIM" if mapping else "Backend directo",
            "autenticacion_backend": auth,
            "autenticacion_apim": "Google ID Token (política revisada)" if mapping else "—",
            "permisos": role,
            "parametros": "; ".join(f"{loc}:{name}{'*' if definition.get('required') else ''}" for (loc, name), definition in params.items()),
            "solicitud": schema_label(json_schema(spec, op.get("requestBody", {}))),
            "respuestas_exito": ", ".join(f"{code} {schema_label(json_schema(spec, codes[code]))}" for code in successes),
            "errores_openapi": ", ".join(f"{code} {schema_label(json_schema(spec, codes[code]))}" for code in errors),
            "carpeta_postman": requests[name],
            "solicitud_postman": name,
            "implementacion": status,
            "despliegue": deployment,
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
            lines.append(f"| `{row['metodo']} {row['ruta_interna']}` | {row['ruta_apim_confirmada'] or '—'} | {row['permisos']} | {row['solicitud']} | {row['respuestas_exito']} | {row['carpeta_postman']} |")
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
