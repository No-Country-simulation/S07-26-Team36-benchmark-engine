# Motor de Scoring, Percentiles y Rebalanceo Dinámico

**Responsable:** Gustavo — Data Scientist  
**Módulos:** `src/scoring/`

---

## Responsabilidad de este módulo

Tomar los puntajes por dimensión que produce el formulario y convertirlos en una posición relativa dentro de la industria, usando una distribución de referencia que se actualiza dinámicamente a medida que crecen las respuestas primarias.

Este módulo **no diseña las preguntas** (responsabilidad de Gio) ni **expone endpoints** (responsabilidad de Marisol). Recibe puntajes, devuelve posición y perfil.

---

## Módulo 1 — Scoring por Dimensión

### Qué hace

Convierte las respuestas del formulario en un puntaje de 0 a 100 por cada una de las cinco dimensiones.

### Cómo funciona

Cada pregunta del formulario tiene opciones con un peso predefinido. El puntaje de una dimensión es la suma ponderada de las respuestas que la componen, normalizada a escala 0-100.

```
puntaje_dimension = Σ (peso_opcion_elegida_i) / puntaje_maximo_posible × 100
```

Los pesos de cada opción los define Gio (Data Analyst) junto con las preguntas. Este módulo los consume como configuración, no los inventa.

### Ejemplo

| Dimensión | Preguntas que la componen | Puntaje resultante |
|-----------|--------------------------|-------------------|
| Visibilidad cross-layer | P1, P2, P3 | 72 / 100 |
| Atribución de fricción | P4, P5 | 45 / 100 |
| Latencia de coordinación | P6, P7, P8 | 60 / 100 |
| Auto-cuantificación | P9, P10 | 30 / 100 |
| Bloqueantes | P11, P12 | 55 / 100 |

**Score total:** promedio ponderado de las cinco dimensiones (los pesos por dimensión también los define Gio).

---

## Módulo 2 — Rebalanceo Dinámico

### Qué hace

Produce la **distribución de referencia** contra la cual se compara al operador. Esa distribución mezcla datos públicos (baseline de la industria) con datos primarios (respuestas acumuladas en nuestra BD), y el peso de cada fuente cambia según cuántas respuestas reales tenemos.

### Por qué es necesario

Al inicio (N = 0 respuestas propias) comparar contra nada es imposible. Se usa un baseline construido de datos públicos: reportes de Uptime Institute, estudios de Gartner, papers sobre stranded capacity. A medida que llegan respuestas reales, la distribución de referencia se va construyendo con datos propios.

### La fórmula de mezcla

```
peso_primario  = N / (N + K)
peso_público   = K / (N + K)

distribución_referencia = peso_primario × distribución_primaria
                        + peso_público  × distribución_pública
```

Donde:
- `N` = número de respuestas reales acumuladas en la BD
- `K` = parámetro de calibración (valor inicial propuesto: **50**)
  - Con K=50: cuando N=50 respuestas reales, el peso es 50/50
  - Con K=50: cuando N=200, el peso primario es 80% y público 20%

`K` es configurable sin tocar código — vive en variables de entorno.

### Comportamiento según N

| N (respuestas reales) | Peso primario | Peso público |
|-----------------------|--------------|-------------|
| 0 | 0% | 100% |
| 25 | 33% | 67% |
| 50 | 50% | 50% |
| 100 | 67% | 33% |
| 200 | 80% | 20% |
| 500 | 91% | 9% |

---

## Módulo 3 — Percentiles

### Qué hace

Posiciona al operador dentro de la distribución de referencia (producida por el Módulo 2) y calcula su percentil global y por dimensión.

### Cómo funciona

```
percentil_operador = porcentaje de operadores en la distribución
                     de referencia que tienen un score MENOR al del operador
```

Se calcula tanto para el score total como para cada dimensión individualmente.

### Output de este módulo

```json
{
  "score_total": 52,
  "percentil_global": 38,
  "scores_por_dimension": {
    "visibilidad_cross_layer": 72,
    "atribucion_friccion": 45,
    "latencia_coordinacion": 60,
    "auto_cuantificacion": 30,
    "bloqueantes": 55
  },
  "percentiles_por_dimension": {
    "visibilidad_cross_layer": 61,
    "atribucion_friccion": 29,
    "latencia_coordinacion": 48,
    "auto_cuantificacion": 15,
    "bloqueantes": 42
  },
  "dimension_mas_debil": "auto_cuantificacion",
  "n_respuestas_usadas": 87,
  "peso_primario_actual": 0.63
}
```

Los campos `perfil_friccion` y `descripcion_cuartil_superior` los agrega el Módulo 4 (Inferencia Cualitativa — responsabilidad de Gio).

---

## Datos públicos usados como baseline

| Fuente | Qué aporta |
|--------|-----------|
| Uptime Institute Annual Global Data Center Survey | Distribución de madurez operacional por región |
| Gartner — Stranded Capacity Studies | Rangos de capacidad desperdiciada por segmento |
| Lawrence Berkeley National Lab — Data Center Energy Reports | Benchmarks de eficiencia energética y coordinación |

El baseline se carga como un archivo de configuración estático (`data/public_baseline.json`) y se actualiza manualmente cuando hay nuevas ediciones de estos reportes.

---

## Archivos de este módulo

```
src/scoring/
├── scorer.py          # Módulo 1: puntaje por dimensión
├── rebalancer.py      # Módulo 2: distribución de referencia dinámica
├── percentiles.py     # Módulo 3: posición relativa
└── config.py          # Pesos, K, umbrales configurables
```

---

## Interfaz con los otros módulos

| Módulo | Lo que necesito de ellos | Lo que les entrego |
|--------|--------------------------|-------------------|
| Gio (Preguntas) | Mapa respuesta → peso por pregunta, pesos por dimensión | — |
| Marisol (BD/API) | N actual de respuestas, scores agregados de la BD | JSON con scores y percentiles |
| Marisol (API) | Recibe mi JSON para exponerlo como endpoint | — |
