# MONIPLAG

Sistema de monitoreo y evaluación de plagas en cultivos comerciales de piña.

Prototipo de ingeniería del trabajo de grado *Incidencia y severidad de cochinilla
(Dysmicoccus brevipes) bajo dos regímenes de manejo fitosanitario*, Universidad Ean,
Facultad de Ingenierías, grupo G17.

---

## Qué resuelve

La investigación encontró que la finca cambió de paquete fitosanitario de forma
secuencial: todos los bloques sembrados antes de una fecha recibieron el programa
convencional y todos los posteriores el de base biológica. Los dos regímenes no
comparten ningún lote ni ningún mes de siembra.

Eso hace que el efecto del programa no se pueda separar del efecto del sitio y de la
campaña. La caída de cochinilla observada es real, pero atribuirla al programa no es
defendible con esos datos.

MONIPLAG hace tres cosas con ese problema:

1. **Impide que el error se repita.** Antes de mostrar cualquier comparación entre
   programas corre un diagnóstico de comparabilidad. Si los grupos no comparten sitio
   ni campaña, bloquea el veredicto y lo declara como asociación, no como efecto.
2. **Convierte el monitoreo en decisiones.** Traduce los indicadores en acciones
   concretas por bloque, con el agente, la dosis, la ventana horaria y el costo.
3. **Genera el diseño que sí permitiría atribuir.** Forma pares de bloques del mismo
   lote y rango de semilla, sortea el brazo con semilla reproducible y calcula cuántos
   pares hacen falta para la potencia deseada.

---

## Cómo se usa

1. Abra `index.html` en el navegador, o la dirección publicada del repositorio.
2. Cargue un archivo de Excel con el formato de ocho hojas (ver abajo).
3. Todo el procesamiento ocurre en el navegador. Ningún dato sale del equipo.

En `docs/MONIPLAG_datos.xlsx` está el archivo de carga.

Contiene la geometría real de la finca La Fe: 249 polígonos de bloque con su área
calculada del polígono, la población estimada a 62.500 plantas por hectárea y las
coordenadas de cada vértice. Los dos regímenes se reparten por lote sin compartir
ninguno, de modo que reproduce la estructura del contraste descrita en el artículo.

Las siembras, los monitoreos, las aplicaciones y el muestreo de fruto son sintéticos.
La hoja `Leeme` del archivo detalla qué parte es real y qué parte no.

---

## Formato de carga

| Hoja | Contenido |
|---|---|
| `1.Bloques` | Un bloque por fila: código, programa, fecha de siembra, lote, rango de semilla, área, población y coordenadas. |
| `2.Monitoreo` | Una visita por fila: fecha, bloque, plantas evaluadas y positivas por afectación. |
| `3.Aplicaciones` | Aplicaciones ejecutadas con su ingrediente activo. |
| `4.Paquete` | Calendario programado de cada programa, por día desde la siembra. |
| `5.Afectaciones` | Declara qué columna de la hoja 2 es una plaga, qué agente la controla y sus umbrales. |
| `6.Fruto` | Muestreo de fruto con grados de severidad. |
| `7.Referencias` | Vías, ríos y puntos de referencia para el mapa. Opcional. |
| `8.Parametros` | Constantes de cálculo. |
| `9.Poligonos` | Forma real de cada bloque, un vértice por fila. Opcional. |

Las hojas 7 y 9 son opcionales: sin ellas el mapa usa rectángulos a escala.

### Agregar una plaga nueva

En **fruto** basta escribir su nombre en la columna `afectacion` de la hoja 6.

En **planta** hacen falta dos cosas: una columna nueva en la hoja 2 y su fila
correspondiente en la hoja 5, con el nombre escrito igual. La validación del archivo
avisa si falta una de las dos.

---

## Convertir polígonos desde un KML

`kml_a_formato.py` lee un KML de Google Earth y produce el inventario de bloques con su
área, perímetro, población estimada y centroide, más la hoja de polígonos.

```bash
python3 kml_a_formato.py archivo.kml 62500
```

El segundo argumento es la densidad de siembra en plantas por hectárea. El nombre de
cada polígono se interpreta como lote, bloque y año en seis dígitos: `021626` es lote
02, bloque 16, año 2026. Si un código aparece repetido, cada parcela recibe un sufijo.

---

## Qué hay en cada pestaña

**KPI's** · Estado general, comparación entre programas y comportamiento de la plaga a
lo largo del ciclo.

**Mapa** · Bloques dibujados con su forma real sobre imagen satelital, focos marcados
como puntos, riesgo de contagio hacia bloques limpios y distribución de siembra planta
por planta.

**Calendario** · Línea de tiempo de cada bloque con sus aplicaciones cumplidas,
faltantes y próximas.

**Recomendaciones** · Acciones concretas ordenadas por urgencia, exportables a CSV.

**Validación** · Cada aplicación tratada como un experimento: se compara el cambio del
bloque intervenido contra el de bloques vecinos que no aplicaron.

**Severidad** · Tasa de hallazgos por cien frutos y distribución de grados.

**Bloques** · Ficha individual de cualquier bloque.

**Comparación** · Contraste entre programas, diagnóstico de comparabilidad y las diez
hipótesis sometidas a prueba.

**Protocolo** · Diseño del ensayo prospectivo con asignación aleatoria verificable.

**Umbrales** · Los valores que disparan cada alerta y el catálogo de pruebas
estadísticas que aplica el sistema.

---

## Base estadística

| Qué se pone a prueba | Prueba |
|---|---|
| Diferencia de incidencia entre programas | t de Welch sobre la prevalencia de cada bloque |
| Consistencia de la diferencia con la edad | Homogeneidad de Woolf entre rangos de edad |
| Concentración de la severidad en grado leve | Prueba binomial |
| Homogeneidad de la severidad entre semillas | Chi-cuadrado con V de Cramér |
| Independencia entre severidad e incidencia | Correlación de Pearson por bloque |
| Agrupamiento espacial de la plaga | Índice I de Moran |
| La vecindad anticipa la subida | t de Welch partiendo la historia en dos mitades |
| Capacidad de discriminación por plaga | Área bajo la curva ROC con intervalo de Hanley-McNeil |
| Ajuste por rango de semilla | Odds ratio marginal de Mantel-Haenszel |
| Riesgo de hallazgos falsos | Corrección de Benjamini-Hochberg |

El análisis se hace por bloque y no por planta. El sistema mide la correlación
intraclase entre monitoreos de un mismo bloque y la sobredispersión frente al modelo
binomial, y las reporta para justificar esa decisión.

---

## Límites declarados

- Las comparaciones entre programas son **asociaciones**. Mientras los dos regímenes no
  compartan sitio y campaña, el sistema no emite veredicto de efecto.
- Los umbrales son criterio agronómico de la empresa, no resultados estadísticos.
- El motor no predice cuánto bajará la plaga tras una aplicación: no hay curva
  dosis-respuesta ni causalidad demostrada.
- La distribución de plantas en el mapa se calcula del polígono y la población
  declarada. Las marcadas como afectadas son la proporción estimada repartida al azar,
  no una detección planta por planta.
- El archivo de carga usa datos sintéticos. Solo la geometría de los bloques y el
  paquete biológico de la hoja 4 provienen de la operación real.

---

## Nota metodológica

El diseño conceptual, las reglas de decisión, los criterios estadísticos y la
interpretación de los resultados corresponden a los autores y se derivan de la
investigación. La implementación del código se realizó con asistencia de una
herramienta de inteligencia artificial.

---

## Autores

Duban Felipe Vargas López · Wilson Ernesto García Dután
Director: William López Castrillón
Universidad Ean · Facultad de Ingenierías
