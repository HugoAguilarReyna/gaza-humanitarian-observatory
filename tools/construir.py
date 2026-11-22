"""Construcción pública del observatorio «Gaza · Vidas y territorio».

**Recorrido público** (el único que se ejecuta aquí). Trabaja solo con los
agregados versionados en `source/` y publica `app/index.html`:

  1. `source/construir_observatorio.py` (v0.2: reportes, edades, lesiones, cobertura)
  2. `source/construir_redesign.py` (v0.3: rejilla territorial, archivo y respuesta)
  3. `source/construir_territorio_etiquetas.py` (etiquetas de grupo y atributos por sitio)
  4. `source/construir_pronostico.py` (panel de pronóstico agregado ya calculado)

Ninguno de esos pasos lee `source/memoria/personas.json`: la lista nominal de
72 835 personas identificadas **no se redistribuye**, y su vista «Cada punto, una
vida» es una **extensión nominal opcional** que vive en
`source/construir_memoria.py` y se ejecuta solo con `tools/construir_nominal.py`
(ver `source/README.md`).

Todas las rutas se resuelven desde este archivo, así que funciona desde cualquier
clon: raíz `Path(__file__).resolve().parents[1]`, fuentes en `source/`, documento
intermedio en `source/dist/index.html` y salida en `app/index.html`.

Uso:
    python tools/construir.py
    python tools/construir.py --comprobar
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FUENTE = RAIZ / "source"
INTERMEDIO = FUENTE / "dist" / "index.html"
SALIDA = RAIZ / "app" / "index.html"
PERSONAS = FUENTE / "memoria" / "personas.json"

#: Constructores del recorrido público, en el orden de la entrega.
CONSTRUCTORES = (
    "construir_observatorio.py",
    "construir_redesign.py",
    "construir_territorio_etiquetas.py",
    "construir_pronostico.py",
)

#: Marcas que deben seguir presentes en el documento publicado. Son secciones
#: agregadas: si desaparece una, el build falla en vez de publicar menos tablero.
MARCAS = (
    'const DATA={',
    'id="coverage"',
    'id="humano"',
    'id="personas"',
    'id="salud"',
    'id="evolucion"',
    'id="territorio"',
    'id="evidencia"',
    'id="archivo"',
    'id="respuesta"',
    'id="referencias"',
    'id="experimento"',
    'window.GRUPOS_TERRITORIO=',
    'window.SITIOS_TERRITORIO=',
)


def construir() -> Path:
    FUENTE.mkdir(parents=True, exist_ok=True)
    (FUENTE / "dist").mkdir(parents=True, exist_ok=True)
    for constructor in CONSTRUCTORES:
        ruta = FUENTE / constructor
        if not ruta.is_file():
            raise SystemExit(f"falta el constructor {ruta}")
        resultado = subprocess.run(
            [sys.executable, "-X", "utf8", str(ruta)],
            cwd=str(FUENTE),
            capture_output=True,
            text=True,
        )
        if resultado.returncode != 0:
            print(resultado.stdout)
            print(resultado.stderr, file=sys.stderr)
            raise SystemExit(f"falló {constructor}")
        if resultado.stdout.strip():
            print(resultado.stdout.strip().splitlines()[-1])
    if not INTERMEDIO.is_file():
        raise SystemExit(f"el constructor no produjo {INTERMEDIO}")
    return INTERMEDIO


def revisar(documento: bytes) -> None:
    """Comprueba que el build público no trae la lista nominal y sí los agregados."""
    texto = documento.decode("utf-8")
    if PERSONAS.name in texto:
        raise SystemExit("el documento público menciona la lista nominal; revisa los constructores")
    if 'id="memoria"' in texto:
        raise SystemExit("la construcción pública incluye la vista nominal «Cada punto, una vida»")
    faltan = [marca for marca in MARCAS if marca not in texto]
    if faltan:
        raise SystemExit(f"el documento público perdió secciones agregadas: {faltan}")


def principal(argumentos: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Construcción pública del observatorio (sin lista nominal)."
    )
    parser.add_argument(
        "--comprobar",
        action="store_true",
        help="no publica: comprueba que el build reproduce app/index.html",
    )
    args = parser.parse_args(argumentos)

    intermedio = construir()
    documento = intermedio.read_bytes()
    revisar(documento)
    resumen = (
        f"{len(documento):,} bytes · sha256 {hashlib.sha256(documento).hexdigest()[:16]}…"
    )

    if args.comprobar:
        if not SALIDA.is_file():
            print(f"no hay build publicado en {SALIDA}")
            return 1
        if SALIDA.read_bytes() == documento:
            print(f"la construcción pública reproduce app/index.html: {resumen}")
            return 0
        print("la construcción pública NO reproduce app/index.html")
        return 1

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(intermedio, SALIDA)
    print(f"publicado: app/index.html · {resumen} · sin lista nominal")
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
