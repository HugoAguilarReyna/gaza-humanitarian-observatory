"""Contrato de la construcción: dos recorridos, y el público sin lista nominal.

La construcción pública trabaja solo con los agregados versionados en `source/` y
publica `app/index.html`. La extensión nominal es opcional, requiere un archivo que
el repositorio no redistribuye y no forma parte del recorrido público.
"""

from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
FUENTE = RAIZ / "source"
APP = RAIZ / "app" / "index.html"


def cargar(relativa: str):
    ruta = RAIZ / relativa
    especificacion = importlib.util.spec_from_file_location(f"gaza_{ruta.stem}", ruta)
    assert especificacion and especificacion.loader
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    return modulo


def json_de_la_pagina(texto: str, aguja: str):
    """Extrae el JSON incrustado justo después de `aguja` usando el decodificador."""
    assert aguja in texto, f"falta {aguja} en el documento"
    inicio = texto.index(aguja) + len(aguja)
    return json.JSONDecoder().raw_decode(texto[inicio:])[0]


def test_el_recorrido_publico_no_encadena_la_vista_nominal() -> None:
    construir = cargar("tools/construir.py")
    assert "construir_memoria.py" not in construir.CONSTRUCTORES
    assert "personas.json" not in construir.CONSTRUCTORES
    assert construir.SALIDA == RAIZ / "app" / "index.html"
    assert construir.INTERMEDIO == FUENTE / "dist" / "index.html"


def test_el_recorrido_nominal_es_un_script_aparte() -> None:
    nominal = cargar("tools/construir_nominal.py")
    assert nominal.PERSONAS == FUENTE / "memoria" / "personas.json"
    # El resultado nominal nunca se escribe en el artefacto publicado.
    assert nominal.DESTINO != nominal.PUBLICO
    assert nominal.DESTINO.parent.parent == RAIZ / "build"


def test_la_lista_nominal_no_esta_versionada() -> None:
    assert not (FUENTE / "memoria" / "personas.json").exists(), (
        "personas.json no debe versionarse: son datos personales"
    )


def test_el_tablero_publicado_no_incrusta_la_lista_nominal() -> None:
    texto = APP.read_text(encoding="utf-8")
    assert 'id="memoria"' not in texto, "el artefacto publicado incluye la vista nominal"
    assert "personas.json" not in texto
    assert "const people = [" not in texto, "el HTML publicado incrusta registros nominales"


def test_el_tablero_publicado_conserva_las_secciones_agregadas() -> None:
    construir = cargar("tools/construir.py")
    texto = APP.read_text(encoding="utf-8")
    faltan = [marca for marca in construir.MARCAS if marca not in texto]
    assert not faltan, f"faltan marcas agregadas en app/index.html: {faltan}"


def test_la_cobertura_del_panel_conserva_sus_catorce_evaluaciones() -> None:
    datos = json.loads((FUENTE / "visual.json").read_text(encoding="utf-8"))
    panel = json.loads((FUENTE / "panel" / "validacion.json").read_text(encoding="utf-8"))
    assert panel["sites"] == 198308
    assert len(panel["evaluations"]) == 14
    assert len(datos["report"]["dates"]) == 14

    observatorio = cargar("source/construir_observatorio.py")
    cobertura = observatorio.cobertura_del_panel(observatorio.PANEL_POR_DEFECTO, datos)
    assert cobertura == [evaluacion["states"]["date_and_class"] for evaluacion in panel["evaluations"]]
    assert len(cobertura) == 14

    publicado = json_de_la_pagina(APP.read_text(encoding="utf-8"), "const DATA=")
    assert publicado["coverage"] == cobertura, "la cobertura publicada cambió"


def test_los_constructores_no_usan_rutas_del_monorepo() -> None:
    prohibidas = ("dashboards/", "gaza_panel", "parents[3]", "parents[2]")
    for script in sorted(FUENTE.glob("*.py")) + sorted((RAIZ / "tools").glob("*.py")):
        texto = script.read_text(encoding="utf-8")
        for prohibida in prohibidas:
            assert prohibida not in texto, f"{script.name} conserva una ruta del monorepo: {prohibida}"


@pytest.mark.parametrize(
    "script",
    [
        "source/construir_observatorio.py",
        "source/construir_redesign.py",
        "source/construir_territorio_etiquetas.py",
        "source/construir_pronostico.py",
        "source/construir_memoria.py",
        "tools/construir.py",
        "tools/construir_nominal.py",
    ],
)
def test_los_constructores_son_python_valido_y_derivan_la_raiz(script: str) -> None:
    ruta = RAIZ / script
    texto = ruta.read_text(encoding="utf-8")
    ast.parse(texto)
    assert "Path(__file__).resolve()" in texto, f"{script} no resuelve rutas desde su archivo"
