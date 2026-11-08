#!/usr/bin/env python3
"""Audita consistencia de matriz, Postman y (si están sincronizados) OpenAPI.

No consulta un servidor; NUNCA atribuye éxito a pruebas E2E no ejecutadas.
"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=json.loads((ROOT/'contratos/fuentes.json').read_text(encoding='utf-8'))
with (ROOT/'contratos/matriz-trazabilidad.csv').open(encoding='utf-8-sig',newline='') as f:
    rows=list(csv.DictReader(f))
collection=json.loads((ROOT/'postman/cvexpert.postman_collection.json').read_text(encoding='utf-8'))
postman=[]
for folder in collection['item']:
    for item in folder['item']:
        assert item['event'] and any(x['listen']=='test' and x['script']['exec'] for x in item['event']),item['name']
        postman.append((folder['name'], item['name']))
assert len(rows)==45,(len(rows),'filas matriz')
assert len(postman)==45,(len(postman),'solicitudes Postman')
assert not any(v!=1 for v in Counter((r['servicio'],r['metodo'],r['ruta_contrato']) for r in rows).values())
assert len(collection['item'])==len(MANIFEST['servicios'])==5
assert set(r['servicio'] for r in rows)==set(MANIFEST['servicios'])
assert Counter(len(f['item']) for f in collection['item'])==Counter([7,9,13,4,12]), 'Cambió distribución por servicio'

# Aserciones más estrictas cuando están presentes las copias completas.
paths=[ROOT/'contratos'/f'{name}.openapi.yaml' for name in MANIFEST['servicios']]
if all(p.exists() for p in paths):
    try:
        import yaml
    except ImportError:
        raise SystemExit('PyYAML requerido cuando existen contratos sincronizados')
    actual=set()
    for name in MANIFEST['servicios']:
        doc=yaml.safe_load((ROOT/'contratos'/f'{name}.openapi.yaml').read_text(encoding='utf-8'))
        for path,pathitem in doc.get('paths',{}).items():
            for verb,operation in pathitem.items():
                if verb.upper() in {'GET','POST','PUT','PATCH','DELETE'}:
                    actual.add((name,verb.upper(),path))
                    row=next((r for r in rows if (r['servicio'],r['metodo'],r['ruta_contrato'])==(name,verb.upper(),path)),None)
                    if row:
                        codes=set(str(code) for code in operation.get('responses',{}))
                        expected=set(row['exito_documentado'].split(','))
                        assert expected.issubset(codes), f'Códigos HTTP no coinciden: {name} {verb} {path} {expected-codes}'
    matrix=set((r['servicio'],r['metodo'],r['ruta_contrato']) for r in rows)
    assert actual==matrix, f'Diferencias OpenAPI vs CSV: falta={matrix-actual}, sobra={actual-matrix}'
    print('OK: OpenAPI sincronizados coinciden con la matriz (operaciones y HTTP de éxito).')
else:
    print('AVISO: los cinco YAML completos aún no están sincronizados; revisión contra contratos de origen pendiente.')
print('OK: 5 servicios, 45 rutas únicas, 45 solicitudes Postman y 45 scripts de pruebas.')
print('NOTA: esto verifica solo cobertura ESTRUCTURAL; NO ha ejecutado llamadas HTTP.')
