# Historial de cambios

## [Sin publicar]

### Corregido

- Los constructores de `source/` y `tools/` resuelven todas las rutas desde el
  clon. Desaparecen `dashboards/gaza-observatorio/fuente`, la lectura de
  `gaza_panel/validacion.json` y la copia lateral `Gaza_Huellas_del_dano_v1.html`.
- `app/index.html` se regenera con la construcción pública y **ya no incrusta la
  lista nominal**: el artefacto publicado pasa de 10 683 401 a 4 699 056 bytes. Los
  agregados no cambian: `DATA` (incluida la serie de cobertura de 14 evaluaciones),
  el pronóstico, la rejilla territorial, las etiquetas por sitio y las diez
  secciones agregadas son idénticos; solo se retira la vista nominal.

### Añadido

- Construcción pública `tools/construir.py` (no lee `personas.json`) y extensión
  nominal opcional `tools/construir_nominal.py`, que escribe en `build/` y no en
  `app/`.
- `source/panel/validacion.json`: agregado de cobertura del panel UNOSAT (198 308
  sitios, 14 evaluaciones), copiado sin cambios y validado contra `visual.json` en
  cada build.
- `source/README.md` con los dos recorridos y lo que falta para el nominal.
- `tests/test_construccion.py`: guardas de que el recorrido público no encadena la
  vista nominal, de que el artefacto publicado no la incrusta y de que conserva las
  secciones agregadas.

## [1.0.0] — 2026-11-26

### Añadido

- Primera publicación como repositorio independiente, con agregados y código.
- Tablero autocontenido: impacto humano, evolución del daño territorial por
  celdas y agrupación de trayectorias observadas.
- Construcción reproducible en `source/` (reportes diarios, rejilla territorial,
  pronóstico agregado, rediseño y memoria).
- Suite de contrato de datos con **guarda de no redistribución**: falla si se
  versiona la lista nominal o cualquier archivo con registros por persona.
- Documentación de fuentes, unidades, cortes y exclusiones.

### Nota

La lista nominal de 72 835 personas identificadas no se redistribuye: son datos
personales de personas fallecidas. Se publica el código que la procesa, no el
registro.
