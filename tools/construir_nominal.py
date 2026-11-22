"""Recorrido **nominal opcional**: añade la vista «Cada punto, una vida».

No forma parte de la construcción pública. Requiere la lista nominal de 72 835
personas identificadas (`source/memoria/personas.json`), que este repositorio
**no redistribuye** porque son datos personales de personas fallecidas: hay que
obtenerla de la fuente original (ver `source/README.md`).

Qué hace, en orden y sin tocar la construcción pública:

  1. ejecuta la construcción pública (`tools/construir.py`) → `app/index.html`;
  2. copia el documento intermedio a `build/nominal/index.html`;
  3. aplica `source/construir_memoria.py` sobre esa copia.

El resultado queda en `build/`, que git ignora: la lista nominal nunca se escribe
en un archivo versionado ni en `app/index.html`. Para verlo en local:

    python -m http.server 8000 --directory build/nominal

Uso:
    python tools/construir_nominal.py
    python tools/construir_nominal.py --personas RUTA
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
PUBLICO = RAIZ / "app" / "index.html"
DESTINO = RAIZ / "build" / "nominal" / "index.html"
PERSONAS = FUENTE / "memoria" / "personas.json"


def principal(argumentos: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extensión nominal opcional del observatorio (no se publica)."
    )
    parser.add_argument(
        "--personas",
        type=Path,
        default=PERSONAS,
        help="lista nominal local, no versionada (source/memoria/personas.json)",
    )
    args = parser.parse_args(argumentos)

    if not args.personas.is_file():
        raise SystemExit(
            f"falta la lista nominal: {args.personas}\n"
            "  la extensión nominal es opcional y no se puede reconstruir sin el"
            " archivo de la fuente original; ver source/README.md."
        )

    publico = subprocess.run(
        [sys.executable, "-X", "utf8", str(RAIZ / "tools" / "construir.py")],
        cwd=str(RAIZ),
        capture_output=True,
        text=True,
    )
    if publico.returncode != 0:
        print(publico.stdout)
        print(publico.stderr, file=sys.stderr)
        raise SystemExit("falló la construcción pública previa a la extensión nominal")
    if publico.stdout.strip():
        print(publico.stdout.strip().splitlines()[-1])

    if not INTERMEDIO.is_file():
        raise SystemExit(f"falta el documento intermedio {INTERMEDIO}")

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(INTERMEDIO, DESTINO)

    nominal = subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            str(FUENTE / "construir_memoria.py"),
            "--documento",
            str(DESTINO),
            "--personas",
            str(args.personas),
        ],
        cwd=str(FUENTE),
        capture_output=True,
        text=True,
    )
    if nominal.returncode != 0:
        print(nominal.stdout)
        print(nominal.stderr, file=sys.stderr)
        raise SystemExit("falló la extensión nominal (source/construir_memoria.py)")
    if nominal.stdout.strip():
        print(nominal.stdout.strip().splitlines()[-1])

    documento = DESTINO.read_bytes()
    if 'id="memoria"' not in documento.decode("utf-8"):
        raise SystemExit("la extensión nominal no insertó la vista «Cada punto, una vida»")
    if PUBLICO.read_bytes() == documento:
        raise SystemExit("la extensión nominal sobrescribió la construcción pública")
    print(
        f"build nominal: {DESTINO.relative_to(RAIZ).as_posix()} ·",
        f"{len(documento):,} bytes ·",
        f"sha256 {hashlib.sha256(documento).hexdigest()[:16]}… · no versionado",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
