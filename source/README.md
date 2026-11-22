# `source/` · construir el observatorio

Aquí están la plantilla, las secciones, los guiones de vista y los **agregados** que
alimentan el observatorio. El tablero publicado es un único HTML con todo
incrustado: no hay servidor ni compilación de JavaScript.

Hay **dos recorridos separados**, y solo el primero es público.

| Recorrido | Necesita | Produce | ¿Se ejecuta por defecto? |
|---|---|---|---|
| **1. Construcción pública** | los agregados versionados en `source/` | `app/index.html` | sí |
| **2. Extensión nominal opcional** | `source/memoria/personas.json`, que **hay que obtener aparte** | `build/nominal/index.html` (no versionado) | no |

Las rutas se resuelven desde cada script (`Path(__file__).resolve()`), así que
funcionan desde cualquier clon y desde cualquier directorio actual: no hay rutas
de la carpeta del monorepo donde se armó el tablero.

---

## 1. Construcción pública (sin la lista nominal)

No lee `source/memoria/personas.json`. Usa solo los agregados que están en `source/`
y escribe `app/index.html`:

```bash
python tools/construir.py               # construye y publica
python tools/construir.py --comprobar   # reconstruye y compara con app/index.html
```

Pasos, en orden:

1. `source/construir_observatorio.py` (v0.2) — reportes diarios, edades y prensa,
   lesiones y cobertura del panel. Lee `template.html`, `visual.json`,
   `expansion/observatorio.json`, `expansion/*.css`, `expansion/*.js` y
   `panel/validacion.json`. Escribe el documento intermedio
   `source/dist/index.html`.
2. `source/construir_redesign.py` (v0.3) — rejilla de daño por celdas, archivo
   completo, acceso y respuesta, diseño y referencias. Vuelve a ejecutar el paso 1
   y amplía el mismo documento intermedio.
3. `source/construir_territorio_etiquetas.py` — etiquetas de grupo
   (`territorio/grupos.json`) y atributos por sitio (`territorio/sitios.json`).
4. `source/construir_pronostico.py` — panel del experimento con el pronóstico
   agregado **ya calculado** (`pronostico/datos.json`); no reentrena nada.

Después, `tools/construir.py` comprueba tres cosas antes de publicar: que el
documento no mencione la lista nominal, que no exista la sección `#memoria` y que
sigan presentes todas las marcas de las secciones agregadas (`#coverage`,
`#humano`, `#personas`, `#salud`, `#evolucion`, `#territorio`, `#evidencia`,
`#archivo`, `#respuesta`, `#referencias`, `#experimento`, `const DATA=`,
`window.GRUPOS_TERRITORIO=` y `window.SITIOS_TERRITORIO=`). Si falta una, el build
falla en vez de publicar menos tablero.

### El agregado de cobertura

`source/panel/validacion.json` son **recuentos por evaluación**, no registros por
persona: 198 308 sitios del producto UNOSAT, `date_and_class` y `date_without_class`
por cada una de las 14 evaluaciones, más las comprobaciones del panel. De ahí sale
la serie `coverage` que dibuja `#coverage`, que antes se leía de
`gaza_panel/validacion.json` —una ruta del monorepo que no existe en el clon—.

`construir_observatorio.py` lo valida en cada build: el universo debe ser 198 308
sitios, `fechas - date_without_class` debe reconciliar con `date_and_class` y los
sitios con fecha deben coincidir con `report.dates` de `visual.json`. Si algo no
cuadra, el build falla; no se publica una cobertura calculada sobre otro universo.
Se puede apuntar a otra copia con `--panel RUTA` o `GAZA_PANEL_VALIDACION`.

### Verificar y servir

```bash
python -m pytest -q                          # contrato de datos y guardas
python -m http.server 8000 --directory app   # abre http://127.0.0.1:8000/
```

`tests/test_construccion.py` comprueba que la construcción pública no depende de la
lista nominal: que `tools/construir.py` no encadena `construir_memoria.py`, que
`personas.json` no está versionada y que `app/index.html` no la incrusta.

---

## 2. Extensión nominal opcional · «Cada punto, una vida»

**No forma parte de la construcción pública y no se puede reconstruir sin obtener
antes el archivo de la fuente.**

```bash
python tools/construir_nominal.py                 # usa source/memoria/personas.json
python tools/construir_nominal.py --personas RUTA
```

Qué hace: ejecuta la construcción pública, copia el documento intermedio a
`build/nominal/index.html` y aplica `source/construir_memoria.py` sobre esa copia
(hoja de estilos, pestaña, sección `#memoria` y guion con los registros
incrustados). El resultado queda en `build/`, que git ignora: **la lista nominal
nunca se escribe en `app/index.html` ni en un archivo versionado**.

Para verlo en local: `python -m http.server 8000 --directory build/nominal`.

### Qué hace falta para el recorrido nominal

1. **La lista nominal de 72 835 personas identificadas** (nombre, nombre en inglés
   y edad declarada; corte al 7 de mayo de 2026). El repositorio no la
   redistribuye: son datos personales de personas fallecidas. Se obtiene de la
   fuente original citada en la sección «Fuentes humanas y diseño visual» del
   tablero (<https://data.techforpalestine.org/docs/killed-in-gaza/>).
2. Guardarla en `source/memoria/personas.json` con la forma que espera el guion:
   una lista de 72 835 listas de tres elementos, `[nombre, nombre_en, edad]`.
   `construir_memoria.py` valida el número de registros (72 835) y falla si el
   archivo no está o no coincide; no completa ni imputa edades.
3. Nada más: la sección, los estilos y el guion ya están versionados en
   `source/memoria/`.

La extensión no se ejecuta en `tools/construir.py`, y la suite falla si aparece un
archivo `personas.json` en el repositorio o cualquier `*.csv`, `*.xls`, `*.xlsx`.

> **Nota de alcance.** La pestaña «Edades y prensa» publica los 263 registros de
> prensa tal como los entrega la fuente (`source/redesign/datos.json`, con el
> nombre original del periodista fallecido). No es la lista nominal de 72 835
> personas y este trabajo no la amplía, recorta ni reinterpreta.

---

## Estado del cálculo (qué es código y qué es resultado)

- **Constructores HTML:** recuperables y ejecutables. Todo lo que hace el tablero a
  partir de los JSON está aquí.
- **Agrupación (MiniBatch K-Means, silueta, estabilidad ARI, sensibilidades):** en
  el repositorio **no hay código de entrenamiento**. Solo están los resultados ya
  calculados en `source/visual.json` (`report.candidates`, `report.stability`,
  `report.sensitivities`, `report.profiles`, `report.dates`, `report.baselines`) y
  el protocolo descrito en `report.protocol`. No se reentrena en el build ni en el
  navegador, y estas notas no reproducen la agrupación desde los microdatos.
- **Pronóstico agregado (walk-forward, métricas de prueba, incertidumbre):** igual:
  **no hay código de cálculo**, solo `source/pronostico/datos.json` con las
  métricas y el protocolo, y `source/pronostico/pronostico.js`, que dibuja lo que
  ya viene calculado.

Reproducir la agrupación o el pronóstico exigiría el GDB original de UNOSAT y la
serie diaria cruda, que no se publican aquí.
