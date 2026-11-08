#!/usr/bin/env python3
"""Verifica los artefactos de origen antes de escribir las copias centrales."""
import argparse
import hashlib
import json
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git_blob_sha(data):
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def sources():
    return json.loads((ROOT / "contratos/fuentes.json").read_text(encoding="utf-8"))


def artifacts(manifest):
    for service, info in manifest["servicios"].items():
        yield info, info["openapi"], info["sha"], f"contratos/{service}.openapi.yaml"
        if info.get("postman"):
            yield info, info["postman"], info["postman_sha"], f"postman/originales/{service}.postman_collection.json"
    for key in ("evento_notificacion", "guia_notificaciones"):
        info = manifest[key]
        yield info, info["path"], info["sha"], info["dest"]


def download(org, info, path, clones):
    if clones:
        return subprocess.check_output(["git", "-C", str(clones / info["repo"]), "show", f"{info['revision']}:{path}"])
    url = f"https://raw.githubusercontent.com/{org}/{info['repo']}/{info['revision']}/{urllib.parse.quote(path)}"
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def adapt_guide(data):
    guide = data.decode("utf-8")
    header = (
        "> Referencia del servicio. Consulte [las fuentes fijadas](fuentes.json) y "
        "[el estado de integración](../docs/notificaciones.md) para distinguir el diseño "
        "del código de clientes y del despliegue verificado.\n"
    )
    guide = guide.replace("# Contrato del servicio de Notificaciones\n", "# Contrato del servicio de Notificaciones\n\n" + header, 1)
    guide = guide.replace("](openapi.yaml)", "](notificaciones.openapi.yaml)")
    guide = guide.replace("Justin confirmó `course.recommended` el 2026-11-04.", "El contrato registra la confirmación de los campos de `course.recommended` el 2026-11-04.")
    return guide.encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clones", type=Path, help="Directorio con los repositorios de origen disponibles en Git local")
    parser.add_argument("--check", action="store_true", help="Comprobar la igualdad sin escribir archivos")
    args = parser.parse_args()
    manifest = sources()
    checked = {}
    errors = []
    for info, path, expected, dest in artifacts(manifest):
        try:
            data = download(manifest["organizacion"], info, path, args.clones)
            actual = git_blob_sha(data)
            if actual != expected:
                raise ValueError(f"blob esperado {expected}, encontrado {actual}")
            if info == manifest["guia_notificaciones"]:
                data = adapt_guide(data)
            destination = ROOT / dest
            if args.check and (not destination.exists() or destination.read_bytes() != data):
                raise ValueError("la copia local difiere")
            checked[destination] = data
        except (OSError, ValueError, subprocess.CalledProcessError) as error:
            errors.append(f"{info['repo']} {path}: {error}")

    if errors:
        parser.exit(1, "\n".join(f"ERROR {error}" for error in errors) + "\n")
    for destination, data in checked.items():
        if not args.check and (not destination.exists() or destination.read_bytes() != data):
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        print(f"OK {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
