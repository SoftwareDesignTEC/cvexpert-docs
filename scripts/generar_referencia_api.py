#!/usr/bin/env python3
"""Genera documentación detallada de endpoints directamente de los 5 OpenAPI.

No crea campos nuevos ni interpreta ruta APIM. Requiere PyYAML y sincronización previa.
"""
import json
from pathlib import Path
import sys
try:
    import yaml
except ImportError:
    print('Instalar PyYAML: python -m pip install PyYAML', file=sys.stderr)
    raise SystemExit(2)
ROOT=Path(__file__).resolve().parents[1]
SOURCES=json.loads((ROOT/'contratos/fuentes.json').read_text(encoding='utf-8'))
VERBS=('get','post','put','patch','delete','options','head')

def esc(v):
    return str(v if v is not None else '').replace('|','\\|').replace('\n',' ')

def resolve(spec,item, depth=0):
    if depth>12 or not isinstance(item,dict) or '$ref' not in item:return item
    ref=item['$ref']
    if not ref.startswith('#/'):return item
    value=spec
    try:
        for x in ref[2:].split('/'):
            value=value[x.replace('~1','/').replace('~0','~')]
        return resolve(spec,value,depth+1)
    except (KeyError,TypeError):return item

def schema_name(spec, schema):
    if not isinstance(schema,dict):return '(no declarada)'
    if '$ref' in schema:return '`'+schema['$ref'].split('/')[-1]+'`'
    schema=resolve(spec,schema)
    if not isinstance(schema,dict):return '(no declarada)'
    if 'type' in schema:return '`'+str(schema['type'])+'`'
    for k in ('allOf','anyOf','oneOf'):
        if k in schema:return k+'('+', '.join(schema_name(spec,x) for x in schema[k])+')'
    return '(esquema compuesto/sin tipo)'

def body_line(spec, operation):
    body=resolve(spec,operation.get('requestBody',{}))
    if not isinstance(body,dict) or not body:return 'No declara cuerpo.'
    media=[]
    for mt,obj in body.get('content',{}).items():
        media.append(esc(mt)+' → '+schema_name(spec,obj.get('schema',{})))
    return ('Requerido' if body.get('required') else 'Opcional')+'; '+('; '.join(media) if media else 'sin content especificado')+'.'

def get_parameters(spec,operation,pathobj):
    merged={}
    for p in (pathobj.get('parameters',[]) or [])+(operation.get('parameters',[]) or []):
        p=resolve(spec,p)
        if not isinstance(p,dict):continue
        merged[(p.get('name'),p.get('in'))]=p
    return list(merged.values())

def main():
    out=['# Referencia API de CVExpert (generada desde OpenAPI)','',
         '> **Fuente automática:** este documento no sustituye los contratos OpenAPI canónicos ni verifica rutas expuestas por APIM.','']
    count=0
    for svc, info in SOURCES['servicios'].items():
        path=ROOT/'contratos'/f'{svc}.openapi.yaml'
        if not path.exists():
            raise FileNotFoundError(f'Falta {path}. Primero ejecutar scripts/sincronizar_contratos.py')
        spec=yaml.safe_load(path.read_text(encoding='utf-8'))
        out.extend([f"## {info['title']}",'',f"Fuente: [OpenAPI original](https://github.com/SoftwareDesignTEC/{info['repo']}/blob/main/{info['openapi']})",''])
        for uri, pathobj in spec.get('paths',{}).items():
            if not isinstance(pathobj,dict):continue
            for verb,operation in pathobj.items():
                if verb not in VERBS or not isinstance(operation,dict):continue
                count+=1
                out.extend([f'### `{verb.upper()} {uri}`','',f"**Resumen:** {esc(operation.get('summary','(sin resumen)'))}",''])
                description=operation.get('description')
                if description:out.extend([esc(description),''])
                out.extend(['**Parámetros**','', '| Nombre | Ubicación | Requerido | Tipo |','|---|---|---|---|'])
                params=get_parameters(spec,operation,pathobj)
                if params:
                    for p in params:
                        out.append(f"| `{esc(p.get('name'))}` | {esc(p.get('in'))} | {'sí' if p.get('required') else 'no'} | {schema_name(spec,p.get('schema',{}))} |")
                else:out.append('| — | — | — | — |')
                out.extend(['','**Cuerpo de solicitud:** '+body_line(spec,operation),'','**Respuestas**','','| HTTP | Descripción | Esquema |','|---|---|---|'])
                responses=operation.get('responses',{})
                if not responses:out.append('| — | No declarada | — |')
                for code,response in responses.items():
                    response=resolve(spec,response)
                    content=response.get('content',{}) if isinstance(response,dict) else {}
                    schemas='; '.join(schema_name(spec,x.get('schema',{})) for x in content.values() if isinstance(x,dict)) or 'sin cuerpo documentado'
                    out.append(f"| `{esc(code)}` | {esc(response.get('description','') if isinstance(response,dict) else '')} | {schemas} |")
                security=operation.get('security',spec.get('security',[]))
                out.extend(['',f'**Seguridad declarada en OpenAPI:** `{json.dumps(security,ensure_ascii=False)}`.',''])
    dest=ROOT/'docs/referencia-api.md'
    dest.write_text('\n'.join(out)+'\n',encoding='utf-8')
    print(f'Referencia generada: {dest} ({count} operaciones).')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
