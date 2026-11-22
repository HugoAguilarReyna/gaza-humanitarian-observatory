"""Incorpora la vista «Cada punto, una vida» al HTML del observatorio.

**Recorrido nominal opcional.** No se ejecuta en la construcción pública: necesita
`source/memoria/personas.json` (72 835 registros con nombre y edad declarada), que
el repositorio **no redistribuye** y que hay que obtener de la fuente original.
Ver `source/README.md`.

Se ejecuta después de los constructores v0.2 y v0.3 y aplica cuatro inserciones
sobre el documento ya armado:

  1. la hoja de estilos de la vista, al final del último bloque `<style>`;
  2. el botón de pestaña, justo después de «Edades y prensa» —queda estático, así
     la navegación por teclado de la barra lo incluye desde el arranque—;
  3. la sección `#memoria` antes de `#personas`;
  4. el script de la vista con los 72 835 registros nominales incrustados.

La sección y el guion viven en `source/memoria/`. No se toca ninguna otra vista.
Todas las rutas se resuelven desde este archivo; no hay rutas del monorepo.

Uso:
    python source/construir_memoria.py
    python source/construir_memoria.py --documento RUTA --personas RUTA
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FUENTE = RAIZ / "source"
MEMORIA = FUENTE / "memoria"
DOCUMENTO_POR_DEFECTO = Path(
    os.environ.get("GAZA_DOCUMENTO", FUENTE / "dist" / "index.html")
)
PERSONAS_POR_DEFECTO = Path(
    os.environ.get("GAZA_PERSONAS", MEMORIA / "personas.json")
)
REGISTROS_ESPERADOS = 72835

# Las consultas de medios viven ya en `memoria.css`; aquí solo lo que añade el
# constructor (aviso de alcance bajo la leyenda).
CSS_ADICIONAL = """
.memNotice{margin-top:22px}
"""

BOTON = '<button role="tab" aria-selected="false" data-tab="memoria">Cada punto, una vida</button>'


def principal(argumentos: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extensión nominal opcional: incrusta la lista de personas identificadas."
    )
    parser.add_argument(
        "--documento",
        type=Path,
        default=DOCUMENTO_POR_DEFECTO,
        help="documento construido por la vía pública (source/dist/index.html)",
    )
    parser.add_argument(
        "--personas",
        type=Path,
        default=PERSONAS_POR_DEFECTO,
        help="lista nominal local, no versionada (source/memoria/personas.json)",
    )
    args = parser.parse_args(argumentos)

    if not args.documento.exists():
        raise SystemExit(
            f"falta el documento base: {args.documento}\n"
            "  ejecuta antes `python tools/construir.py` (construcción pública)."
        )
    if not args.personas.exists():
        raise SystemExit(
            f"falta la lista nominal: {args.personas}\n"
            "  es la extensión opcional: descárgala de la fuente original y guárdala"
            " ahí (o usa --personas RUTA / GAZA_PERSONAS). Este repositorio no la"
            " redistribuye; ver source/README.md."
        )

    html = args.documento.read_text(encoding="utf-8")

    personas = json.loads(args.personas.read_text(encoding="utf-8"))
    if len(personas) != REGISTROS_ESPERADOS:
        raise SystemExit(f"se esperaban 72 835 registros nominales, hay {len(personas):,}")

    seccion = (MEMORIA / "seccion.html").read_text(encoding="utf-8").strip()
    guion = (MEMORIA / "memoria.js").read_text(encoding="utf-8")
    estilo = (MEMORIA / "memoria.css").read_text(encoding="utf-8") + CSS_ADICIONAL

    # 1. estilos al final del último bloque <style>
    corte = html.rfind("</style>")
    if corte < 0:
        raise SystemExit("no se encontró un bloque <style> donde insertar los estilos")
    html = html[:corte] + estilo + html[corte:]

    # 2. pestaña después de «Edades y prensa»
    ancla_pestana = '<button role="tab" aria-selected="false" data-tab="personas">Edades y prensa</button>'
    if ancla_pestana not in html:
        raise SystemExit("no se encontró la pestaña «Edades y prensa»")
    html = html.replace(ancla_pestana, ancla_pestana + BOTON, 1)

    # 3. sección antes de #personas
    ancla_seccion = '<section id="personas" role="tabpanel" hidden>'
    if ancla_seccion not in html:
        raise SystemExit("no se encontró la sección «personas»")
    html = html.replace(ancla_seccion, seccion + ancla_seccion, 1)

    # 4. guion con los datos incrustados
    datos = json.dumps(personas, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html += "\n<script>" + guion.replace("__PERSONAS__", datos) + "</script>"

    args.documento.write_text(html, encoding="utf-8", newline="")
    print(
        f"Cada punto, una vida: {len(personas):,} registros · documento {len(html.encode('utf-8')):,} bytes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
