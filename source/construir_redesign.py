"""Añade al documento del observatorio las vistas del rediseño (v0.3).

Se ejecuta después de `construir_observatorio.py` y trabaja sobre el documento
intermedio `source/dist/index.html`, que es también su salida. Todas las rutas se
resuelven desde este archivo: no hay rutas del monorepo donde se armó el tablero.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

R = pathlib.Path(__file__).resolve().parent
subprocess.run([sys.executable, '-X', 'utf8', str(R/'construir_observatorio.py')], check=True)
s = (R/'dist/index.html').read_text(encoding='utf-8')
s=s.replace('</nav>','<button role="tab" aria-selected="false" data-tab="archivo">Archivo completo</button><button role="tab" aria-selected="false" data-tab="respuesta">Acceso y respuesta</button><button role="tab" aria-selected="false" data-tab="referencias">Diseño y referencias</button></nav>')
s=s.replace('<section id="evidencia"', (R/'redesign/nuevas_vistas.html').read_text(encoding='utf-8')+'<section id="evidencia"',1)
s=s.replace('<section id="referencias"', (R/'redesign/respuesta.html').read_text(encoding='utf-8')+'<section id="referencias"',1)
s=s.replace('v0.2 ·','v0.3 ·')
# Retire previous generic inspiration claims in favor of exact reviewed designs.
start=s.index('<div><h3>Referencias de visualización</h3>');end=s.index('</div></div></div>',start)
s=s[:start]+'<div><h3>Diseño revisado</h3><p>La pestaña «Diseño y referencias» documenta tres fichas exactas revisadas visualmente, sus autores y la adaptación implementada.</p>'+s[end:]
css='''<style>.detailgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:15px 0}.detailgrid small,.detailgrid strong{display:block;overflow-wrap:anywhere}.detailgrid strong{font-size:19px}.refline{font-size:12px;color:#69768e;border-top:1px solid #d9dfee;padding-top:15px}.bigrid{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(280px,1fr);gap:24px}.miniCoverage{display:flex;align-items:end;height:115px;gap:5px}.miniCoverage>div{flex:1;display:flex;flex-direction:column;justify-content:end;height:115px}.miniCoverage i{display:block;background:#4b55ff}.miniCoverage small{font-size:9px}.refgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:25px;margin:25px 0}.refgrid article{border:1px solid #d9dfee;border-radius:10px;padding:22px}.refgrid h3{font:25px Georgia;margin:15px 0}.recordDetail{margin-top:25px;background:#f5f6fb;border:1px solid #d9dfee;padding:20px;border-radius:8px}.recordDetail td:first-child{width:32%}input[type=search]{font:inherit;padding:10px;border:1px solid #d9dfee;border-radius:7px}#fieldChart{overflow:auto}#reportPack svg{min-width:700px}#calendar svg{min-width:980px}#biMap svg{height:auto;max-height:850px}.card>h2{max-width:900px}nav{width:100%}@media(max-width:850px){.bigrid,.refgrid{grid-template-columns:1fr}.detailgrid{grid-template-columns:1fr 1fr}#fieldChart svg{min-width:700px}.refgrid article{padding:16px}}
</style>'''
css=css.replace('</style>',(R/'redesign/correcciones.css').read_text(encoding='utf-8')+'</style>')
s=s.replace('</style>', '</style>'+css,1)
js=(R/'redesign/redesign.js').read_text(encoding='utf-8').replace('__EXPANDED__',json.dumps(json.load(open(R/'redesign/datos.json', encoding='utf-8')),ensure_ascii=False,separators=(',',':')).replace('</','<\\/'))
s+='\n<script>'+(R/'redesign/d3.min.js').read_text(encoding='utf-8')+'</script>\n<script>'+js+'</script>'
s+='\n<style>'+(R/'redesign/respuesta.css').read_text(encoding='utf-8')+'</style>\n<script>'+(R/'redesign/respuesta.js').read_text(encoding='utf-8')+'</script>'
(R/'dist/index.html').write_text(s, encoding='utf-8', newline='');print('v0.3',len(s))
