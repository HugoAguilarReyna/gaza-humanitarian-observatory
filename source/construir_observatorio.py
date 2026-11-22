"""Construye la base del observatorio (v0.2) a partir de los agregados de `source/`.

Todas las rutas se resuelven desde este archivo, así que el constructor funciona
desde cualquier clon y no depende de la carpeta del monorepo donde se armó:

- raíz del clon: `Path(__file__).resolve().parents[1]`
- plantilla, secciones, guiones y JSON: `source/`
- documento intermedio: `source/dist/index.html` (ignorado por git)
- agregado de cobertura del panel: `source/panel/validacion.json`

El agregado del panel son recuentos por evaluación (198 308 sitios, `date_and_class`),
no registros por persona: se valida aquí contra `visual.json` para que la serie de
cobertura del HTML no pueda desviarse en silencio.

Uso:
    python source/construir_observatorio.py
    python source/construir_observatorio.py --panel RUTA --salida RUTA
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FUENTE = RAIZ / "source"
PANEL_POR_DEFECTO = Path(
    os.environ.get("GAZA_PANEL_VALIDACION", FUENTE / "panel" / "validacion.json")
)
SALIDA_POR_DEFECTO = FUENTE / "dist" / "index.html"
SITIOS_DEL_PANEL = 198308

R = FUENTE


def cobertura_del_panel(ruta: Path, visual: dict) -> list[int]:
    """Serie de sitios con fecha y clase por evaluación, validada contra `visual.json`."""
    if not ruta.is_file():
        raise SystemExit(
            f"falta el agregado del panel: {ruta}\n"
            "  se espera source/panel/validacion.json dentro del clon (o --panel RUTA);"
            " ver source/README.md."
        )
    panel = json.loads(ruta.read_text(encoding="utf-8"))
    if panel.get("sites") != SITIOS_DEL_PANEL:
        raise SystemExit(
            f"el agregado del panel declara {panel.get('sites')} sitios y se esperaban"
            f" {SITIOS_DEL_PANEL}: no se publica una cobertura sobre otro universo"
        )
    evaluaciones = panel.get("evaluations") or []
    fechas_visual = visual.get("report", {}).get("dates") or []
    if len(evaluaciones) != len(fechas_visual):
        raise SystemExit(
            f"el panel trae {len(evaluaciones)} evaluaciones y visual.json {len(fechas_visual)}"
        )
    cobertura = []
    for indice, evaluacion in enumerate(evaluaciones):
        estados = evaluacion.get("states") or {}
        fecha_y_clase = estados.get("date_and_class", 0)
        sin_clase = estados.get("date_without_class", 0)
        con_fecha = sum(
            valor for clave, valor in (evaluacion.get("dates") or {}).items() if clave != "missing"
        )
        if con_fecha - sin_clase != fecha_y_clase:
            raise SystemExit(
                f"evaluación {evaluacion.get('evaluation')}: las fechas no reconcilian con"
                f" date_and_class ({con_fecha} - {sin_clase} ≠ {fecha_y_clase})"
            )
        referencia = sum(
            valor for clave, valor in (fechas_visual[indice] or {}).items() if clave != "missing"
        )
        if referencia != con_fecha:
            raise SystemExit(
                f"evaluación {evaluacion.get('evaluation')}: el panel ({con_fecha}) y"
                f" visual.json ({referencia}) no coinciden en sitios con fecha"
            )
        cobertura.append(fecha_y_clase)
    return cobertura


def principal(argumentos: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Construye la base del observatorio (v0.2).")
    parser.add_argument(
        "--panel",
        type=Path,
        default=PANEL_POR_DEFECTO,
        help="agregado de validación del panel UNOSAT (source/panel/validacion.json)",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=SALIDA_POR_DEFECTO,
        help="documento intermedio (source/dist/index.html)",
    )
    args = parser.parse_args(argumentos)

    base=(R/'template.html').read_text(encoding='utf-8')
    base=base.replace('<title>Gaza · Huellas del daño</title>','<title>Gaza · Observatorio del impacto humano y territorial</title>')
    base=base.replace('<h1>Huellas del <em>daño.</em></h1>','<h1>Gaza.<br>Vidas y <em>territorio.</em></h1>').replace('Cómo cambia la clasificación de los sitios observados desde el espacio.','Un observatorio del impacto humano, las lesiones duraderas y la transformación del territorio.').replace('Primera versión · Exploratoria','Versión ampliada · Fuentes trazables').replace('Fuente UNOSAT · producto de octubre de 2025.<br>Experimento generado el 10 nov 2026.<br>No representa la situación actual.','Cada fuente tiene su propio corte.<br>Reportes: 10 nov 2026 · Edades: 7 may 2026.<br>Daño satelital: oct 2025 · OMS: may 2026.')
    newnav=''.join(f'<button role="tab" aria-selected="false" data-tab="{id}">{label}</button>' for id,label in [('humano','Impacto humano'),('personas','Edades y prensa'),('salud','Lesiones'),('evolucion','Mapas y cronología')])
    base=base.replace('<button role="tab" aria-selected="true" data-tab="territorio">Territorio</button>',newnav+'<button role="tab" aria-selected="false" data-tab="territorio">Sitios y trayectorias</button>')
    base=base.replace('<section id="territorio" role="tabpanel">',(R/'expansion/secciones.html').read_text(encoding='utf-8')+'<section id="territorio" role="tabpanel" hidden>')
    base=base.replace('Este módulo aborda clasificaciones de daño territorial. Las series de impacto humano ya auditadas se integrarán como fuentes separadas.','Esta versión integra reportes humanos, edades declaradas, cortes de prensa, estimaciones de lesiones y clasificaciones de daño territorial, con universos y fechas diferentes.')
    css='''
.humanmetrics{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.humanmetrics .card{margin:0;padding:20px}.humanmetrics strong{margin:8px 0;font:36px Georgia}.widechart{width:100%;margin:24px 0}.map-pair{display:grid;grid-template-columns:1fr 1fr;gap:30px}.map-pair h3{font:25px Georgia}.eventkey{display:flex;gap:12px;flex-wrap:wrap;font-size:12px}.eventkey a{border:1px solid #d9dfee;padding:8px 12px;border-radius:6px}.event{display:grid;grid-template-columns:180px 1fr;gap:30px;padding:25px 0;border-bottom:1px solid #d9dfee}.eventdate{color:#69768e;font:13px monospace}.eventdate b{display:block;color:#b2b8d0;font:50px Georgia}#calendar svg{min-width:900px}summary{cursor:pointer;color:#4b55ff;padding:10px 0}.sources-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}#injuryChart svg{min-width:800px}#injuryChart{overflow:auto}@media(max-width:850px){.humanmetrics{grid-template-columns:1fr 1fr}.map-pair,.sources-grid{grid-template-columns:1fr}.event{grid-template-columns:100px 1fr;gap:10px}.humanmetrics strong{font-size:27px}.widechart svg{min-width:650px}.widechart{overflow:auto}.map-pair svg{min-width:0}.eventkey{display:block}.eventkey a{display:block;margin-bottom:5px}}
'''
    css=css+(R/'expansion/impacto-perfiles.css').read_text(encoding='utf-8')
    base=base.replace('</style>',css+(R/'expansion/tooltip.css').read_text(encoding='utf-8')+(R/'expansion/correcciones.css').read_text(encoding='utf-8')+'</style>')
    evidence='''<div class="card"><h2>Fuentes humanas y diseño visual</h2><div class="sources-grid"><div><h3>Datos y universos</h3><p><a href="https://data.techforpalestine.org/docs/casualties-daily/">Tech for Palestine · reportes diarios</a>: 1,131 fechas, 1,077 valores nativos de fallecidos, 1,050 de heridos. No se usan campos ext_ interpolados.</p><p><a href="https://data.techforpalestine.org/docs/killed-in-gaza/">Lista identificada</a>: 72,835 registros, 72,835 IDs distintos; edades declaradas 0–110. El tablero solo incorpora agregados, no nombres ni IDs personales.</p><p><a href="https://www.emro.who.int/images/stories/palestine/Estimating_Trauma_Rehabilitation_Needs_in_Gaza_2026.pdf">OMS, mayo 2026</a>: estimaciones de lesiones y actividad de rehabilitación, con universos separados.</p><p>Niños: 135 cortes nativos; prensa: 176. La disponibilidad de una fila por fecha no implica disponer de desglose demográfico diario.</p></div><div><h3>Referencias de visualización</h3><p><a href="https://www.dataviz-inspiration.com/heatmap">Plastic waste — calendar heatmap</a>: adaptación del calendario de intensidad, con celdas ausentes explícitas.</p><p><a href="https://www.dataviz-inspiration.com/">Paris, building by building</a>: lectura a escala de sitios; aquí mapas pareados del mismo conjunto, no edificios extruidos inventados.</p><p><a href="https://www.dataviz-inspiration.com/">Japan’s population decline</a>: inspiración para explorar estructura por edad; aquí una distribución de fallecidos identificados, no una pirámide de población general.</p><p>Diseño y código propios. Referencias consultadas en Dataviz Inspiration; no se reutiliza su código ni se atribuye a sus autores este observatorio.</p></div></div></div>'''
    base=base.replace('<section id="evidencia" role="tabpanel" hidden>','<section id="evidencia" role="tabpanel" hidden>'+evidence)
    base=base.replace('v0.1 · Datos reales, corte histórico, resultados exploratorios.','v0.2 · Datos reales, cortes propios por fuente, resultados exploratorios.')
    v=json.loads((R/'visual.json').read_text(encoding='utf-8'))
    v['coverage']=cobertura_del_panel(args.panel, v)
    base=base.replace('__DATA__',json.dumps(v,separators=(',',':')).replace('</','<\\/'))
    h=json.loads((R/'expansion/observatorio.json').read_text(encoding='utf-8'));js=(R/'expansion/visualizaciones.js').read_text(encoding='utf-8').replace('__HUMAN__',json.dumps(h,separators=(',',':')).replace('</','<\\/'))
    base+='\n<script>'+(R/'expansion/tooltip.js').read_text(encoding='utf-8')+'</script>\n<script>'+js+'</script>'
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(base, encoding='utf-8', newline='')
    print(f"Construido {len(base)} caracteres -> {args.salida}")
    return 0


if __name__ == '__main__':
    raise SystemExit(principal())

