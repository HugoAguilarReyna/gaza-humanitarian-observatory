# Gaza · Vidas y territorio · Observatorio del impacto humano

Observatorio del impacto humano y territorial: impacto humano, evolución del daño
territorial y agrupación de trayectorias observadas, con datos abiertos, fuentes
trazables y las unidades de cada fuente siempre a la vista.

[![Integridad](https://github.com/HugoAguilarReyna/gaza-humanitarian-observatory/actions/workflows/tests.yml/badge.svg)](https://github.com/HugoAguilarReyna/gaza-humanitarian-observatory/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](source)
[![Privacidad](https://img.shields.io/badge/lista%20nominal-no%20redistribuida-b7791f)](#qué-no-se-publica)

> **Advertencia de lectura.** Un reporte publicado no equivale a un periodo de 24
> horas ni a las muertes ocurridas ese día, y **la ausencia de reporte no es un
> cero**. Las categorías de lesiones pueden solaparse y no se suman.

---

## Demo

```bash
git clone https://github.com/HugoAguilarReyna/gaza-humanitarian-observatory.git
cd gaza-humanitarian-observatory
python -m http.server 8000 --directory app
```

Abre <http://127.0.0.1:8000/>. El tablero es un único HTML con los agregados y las
visualizaciones embebidos; no hay compilación ni backend.

![Portada del observatorio](docs/cover.jpg)

## Construir

La construcción tiene **dos recorridos separados**; el detalle de ambos, los
archivos que lee cada paso y lo que falta para el nominal están en
[`source/README.md`](source/README.md).

```bash
python tools/construir.py               # construcción pública → app/index.html
python tools/construir.py --comprobar   # verifica que el build reproduce lo publicado
python -m pytest -q                     # contrato de datos y guardas
```

La construcción pública usa solo los agregados versionados en `source/` y **no lee
`source/memoria/personas.json`**. La vista «Cada punto, una vida» es una extensión
nominal opcional (`python tools/construir_nominal.py`) que exige ese archivo y
escribe en `build/`, que git ignora.

## Qué demuestra

- **Separación de fuentes y unidades**: reportes diarios, estimaciones de
  necesidades de rehabilitación, registros de infraestructura y prensa no se
  mezclan ni se suman.
- **Daño territorial por celdas**: la evolución del daño se agrupa en una rejilla
  con totales y distribución por gobernación, sin interpretar celdas como
  edificios individuales.
- **Faltantes explícitos**: un día sin reporte utilizable se marca como tal, no
  como cero muertes.
- **Trazabilidad editorial**: cada sección declara su fuente, su corte y su nivel
  de detalle.

## Qué no se publica

La **lista nominal de 72 835 personas identificadas** (nombre y edad declarada,
corte al 7 de mayo de 2026) **no se redistribuye en este repositorio**: son datos
personales de personas fallecidas. La sección «Cada punto, una vida» requiere
obtenerla de la fuente original y reconstruirla con `tools/construir_nominal.py`
(ver [`source/README.md`](source/README.md)).

Una prueba de la suite **falla si alguien versiona esa lista** o cualquier archivo
con registros por persona. La regla es ejecutable, no una promesa.

## Estructura

```text
app/index.html              Tablero publicable con agregados embebidos
source/                     Construcción del tablero (Python + JS)
  construir_observatorio.py Reportes diarios y series
  construir_territorio_etiquetas.py  Rejilla territorial y etiquetas
  construir_pronostico.py   Pronóstico agregado de conteos (resultados ya calculados)
  construir_redesign.py     Rejilla de daño por celdas
  construir_memoria.py      Extensión nominal opcional (requiere datos locales, no versionados)
  panel/validacion.json     Agregado de cobertura del panel UNOSAT (14 evaluaciones)
  template.html, visual.json
tools/construir.py          Construcción pública: source/ → app/index.html
tools/construir_nominal.py  Extensión nominal opcional: source/ + personas.json → build/
docs/DATOS.md               Fuentes, unidades, cortes y exclusiones
tools/                      Verificadores de navegador del proyecto
tests/                      Contrato de datos, guardas y contrato de construcción
```

## Datos y atribución

- **Tech for Palestine**: 1 131 reportes diarios de Gaza y 1 131 de Cisjordania,
  730 registros de infraestructura y 263 de prensa; corte al 10 de noviembre de
  2026.
- **Lista identificada de fallecidos**: 72 835 registros, corte al 7 de mayo de
  2026 — **no redistribuida**.
- **OMS (EMRO)**: estimación de necesidades de rehabilitación por politrauma,
  mayo de 2026, con rangos de escenario — no intervalos de confianza.

Detalle completo en [`docs/DATOS.md`](docs/DATOS.md). Este repositorio no incluye
un archivo `LICENSE` propio: se respetan las condiciones de cada fuente.

## Límites

- La lista nominal es incompleta y su corte no coincide con el acumulado diario:
  la diferencia incluye personas no identificadas.
- Los rangos de la OMS son escenarios, no intervalos de confianza, y las prótesis
  colocadas no son personas.
- Un paso o una celda no implica causalidad ni atribución de responsabilidad.
- Los agregados describen lo reportado; no sustituyen la lectura de las fuentes.

## Seguridad y contribución

Sin datos personales en el repositorio. Ver [`SECURITY.md`](SECURITY.md) y
[`CONTRIBUTING.md`](CONTRIBUTING.md).
