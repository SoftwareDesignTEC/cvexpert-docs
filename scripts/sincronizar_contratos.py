#!/usr/bin/env python3
"""Copia OpenAPI y colecciones originales desde GitHub y verifica SHA Git blob.

Solo usa Python stdlib. NO escribe sobre archivos si fallan verificaciones.
"""
import hashlib
import json
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / 'contratos/fuentes.json').read_text(encoding='utf-8'))


def get_source(repo: str, ref: str, relative_path: str) -> bytes:
    pieces = [urllib.parse.quote(part, safe='') for part in relative_path.split('/')]
    url = f'https://raw.githubusercontent.com/SoftwareDesignTEC/{urllib.parse.quote(repo)}/{urllib.parse.quote(ref)}/' + '/'.join(pieces)
    request = urllib.request.Request(url, headers={'User-Agent': 'CVExpert-docs-source-sync/1.0'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode('ascii') + data).hexdigest()


def write_if_changed(destination: pathlib.Path, data: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.read_bytes() == data:
        print('  sin cambios:', destination.relative_to(ROOT))
        return
    destination.write_bytes(data)
    print('  actualizado:', destination.relative_to(ROOT), f'({len(data)} bytes)')


def main() -> int:
    errors = []
    for service, info in MANIFEST['servicios'].items():
        repo = info['repo']
        print('\n' + service, '←', repo)
        try:
            data = get_source(repo, 'main', info['openapi'])
            actual_sha = git_blob_sha(data)
            expected_sha = info['sha']
            if actual_sha != expected_sha:
                errors.append(f'{service}: fuente cambió: esperado {expected_sha}, actual {actual_sha}. Revisar diff y actualizar fuentes.json tras aprobación.')
                continue
            write_if_changed(ROOT / 'contratos' / f'{service}.openapi.yaml', data)
        except (urllib.error.URLError, OSError) as exc:
            errors.append(f'{service}: no se pudo descargar OpenAPI: {exc}')
        if info.get('postman'):
            try:
                original = get_source(repo, 'main', info['postman'])
                col = json.loads(original)
                if not isinstance(col, dict) or 'item' not in col:
                    raise ValueError('Colección sin item')
                write_if_changed(ROOT / 'postman' / 'originales' / f'{service}.postman_collection.json', original)
            except (urllib.error.URLError, OSError, ValueError) as exc:
                errors.append(f'{service}: no se pudo obtener Postman original: {exc}')
    e = MANIFEST['evento_notificacion']
    try:
        data = get_source(e['repo'], 'main', e['path'])
        json.loads(data)
        write_if_changed(ROOT / e['dest'], data)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        errors.append(f'evento-notificacion: {exc}')
    print('\nSINCRONIZACIÓN:', 'con advertencias' if errors else 'completada')
    for err in errors:
        print('ERROR:', err, file=sys.stderr)
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
