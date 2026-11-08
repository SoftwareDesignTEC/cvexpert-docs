#!/usr/bin/env python3
"""Enriquece la colección global usando requestBody.example(s) REALES de OpenAPI.

No fabrica payloads: si el contrato no incluye un example explícito, deja {}.
Requiere `pip install PyYAML` y contratos previamente sincronizados.
"""
import json
import re
from pathlib import Path
import sys
try:
    import yaml
except ImportError:
    print('Instalar PyYAML: python -m pip install PyYAML', file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / 'contratos/fuentes.json').read_text(encoding='utf-8'))
COLLECTION = ROOT / 'postman/cvexpert.postman_collection.json'


def resolve(spec, obj, depth=0):
    if not isinstance(obj, dict) or '$ref' not in obj or depth > 12:
        return obj
    ref = obj['$ref']
    if not ref.startswith('#/'):
        return obj
    target = spec
    try:
        for part in ref[2:].split('/'):
            target = target[part.replace('~1', '/').replace('~0', '~')]
        return resolve(spec, target, depth + 1)
    except (KeyError, TypeError):
        return obj


def find_example(spec, operation):
    body = resolve(spec, operation.get('requestBody', {}))
    if not isinstance(body, dict):
        return None
    content = body.get('content', {})
    for typ in ('application/json', 'application/*+json'):
        media = content.get(typ)
        if not isinstance(media, dict):
            continue
        if 'example' in media:
            return media['example']
        for element in media.get('examples', {}).values():
            item = resolve(spec, element)
            if isinstance(item, dict) and 'value' in item:
                return item['value']
        schema = resolve(spec, media.get('schema', {}))
        if isinstance(schema, dict) and 'example' in schema:
            return schema['example']
    return None


def main():
    c = json.loads(COLLECTION.read_text(encoding='utf-8'))
    service_folders = list(c['item'])
    if len(service_folders) != len(MANIFEST['servicios']):
        raise ValueError('No coinciden las carpetas de la colección y el manifiesto')
    changed = 0
    no_examples = []
    def originals_by_method_and_path(service):
        original = ROOT / 'postman' / 'originales' / f'{service}.postman_collection.json'
        if not original.exists():
            return {}
        source = json.loads(original.read_text(encoding='utf-8'))
        found = {}
        def crawl(items):
            for item in items:
                if 'item' in item:
                    crawl(item['item'])
                    continue
                req = item.get('request', {})
                raw = req.get('url', {})
                raw = raw.get('raw', '') if isinstance(raw, dict) else raw
                raw = re.sub(r'^\{\{baseUrl\}\}', '', raw)
                # Variables de path documentadas por el servicio de Brecha
                for k,v in {'healthPath':'/health','coursesPath':'/courses','skillsGapPath':'/skills-gap','skillsGapInputPath':'/skills-gap/input'}.items():
                    raw=raw.replace('{{'+k+'}}',v)
                raw=raw.split('?',1)[0]
                raw=re.sub(r'\{\{[^}]+\}\}', '{id}', raw)
                body=req.get('body',{}).get('raw')
                if body and 'eyJ' not in body:
                    found.setdefault((req.get('method','').upper(),raw),body)
        crawl(source.get('item',[]))
        return found
    for folder, (key, info) in zip(service_folders, MANIFEST['servicios'].items()):
        spec_path = ROOT / 'contratos' / f'{key}.openapi.yaml'
        if not spec_path.exists():
            raise FileNotFoundError(f'Falta {spec_path}; ejecutar scripts/sincronizar_contratos.py')
        spec = yaml.safe_load(spec_path.read_text(encoding='utf-8'))
        source_bodies = originals_by_method_and_path(key)
        for req in folder['item']:
            method, path = req['name'].split(' ', 1)
            operation = spec.get('paths', {}).get(path, {}).get(method.lower())
            if not isinstance(operation, dict):
                raise ValueError(f'No está en OpenAPI: {key} {method} {path}')
            body = req['request'].get('body')
            if body is None:
                continue
            example = find_example(spec, operation)
            if example is not None:
                body['raw'] = json.dumps(example, ensure_ascii=False, indent=2)
                changed += 1
                continue
            keypath = re.sub(r'\{[^{}]+\}', '{id}', path)
            source_body = source_bodies.get((method,keypath))
            if source_body:
                body['raw'] = source_body
                changed += 1
            else:
                no_examples.append(f'{key}: {method} {path}')
    COLLECTION.write_text(json.dumps(c, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Ejemplos OpenAPI / Postman de origen incorporados: {changed}. Operaciones con body sin ejemplo: {len(no_examples)}')
    for missing in no_examples:
        print('  REVISAR BODY:', missing)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
