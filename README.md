# Benchmark Engine — S07-26 Team 36

Motor de benchmark de madurez operacional para data centers.

Mide la capacidad de un operador para coordinar las capas físicas y operativas de su facility, calcula su posición relativa en la industria y genera un reporte personalizado con su perfil de fricción principal.

---

## El problema que resuelve

Los data centers modernos tienen capacidad pagada y encendida que no produce nada porque las capas físicas y operativas no se coordinan entre sí. Este benchmark diagnostica ese problema y posiciona al operador dentro de la industria — un dato que no existe en ningún otro lugar.

---

## Las cinco dimensiones del benchmark

| Dimensión | Ponderación | Qué mide |
|-----------|:-----------:|----------|
| Visibilidad cross-layer | 25% | Vista unificada de energía, cooling y workloads |
| Latencia de coordinación | 25% | Velocidad de ajuste ante cambios de workload |
| Atribución de fricción | 20% | Identificación de pérdida de capacidad por capa |
| Auto-cuantificación | 15% | Medición de stranded capacity propia |
| Bloqueantes | 15% | Barreras organizacionales y técnicas |

---

## Arquitectura del pipeline

```
[ 12 Respuestas del Cuestionario (escala 1-4) ]
             │
             ▼
┌────────────────────────────────┐
│ 1. Scorer                      │  Puntaje 0-100 por dimensión
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ 2. Rebalanceo Dinámico         │  Mezcla datos públicos + primarios
│                                │  peso = N / (N + K),  K=50 por defecto
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ 3. Percentiles                 │  Posición relativa global y por dimensión
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ 4. Inferencia Cualitativa      │  Perfil de fricción + recomendación
└───────────────┬────────────────┘
                │
                ▼
     [ JSON / Reporte PDF ]
     [ Persistencia SQLite ]
```

---

## API — Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/v1/submit` | Enviar respuestas y recibir resultado |
| `GET` | `/api/v1/submissions` | Listar todas las respuestas (anónimas) |
| `GET` | `/api/v1/report/{id}` | JSON estructurado para PDF por submission |
| `GET` | `/docs` | Documentación interactiva (Swagger UI) |

### Ejemplo — POST `/api/v1/submit`

**Request:**
```json
{
  "P1": 2, "P2": 1, "P3": 3,
  "P4": 1, "P5": 2,
  "P6": 2, "P7": 1, "P8": 2,
  "P9": 1, "P10": 1,
  "P11": 3, "P12": 2
}
```

**Response:**
```json
{
  "status": "success",
  "score_total": 24.72,
  "percentil_global": 18.8,
  "scores_por_dimension": { "visibilidad_cross_layer": 33.33, "..." : "..." },
  "percentiles_por_dimension": { "visibilidad_cross_layer": 31.5, "..." : "..." },
  "dimension_mas_debil": "auto_cuantificacion",
  "nombre_perfil": "Operador a ciegas",
  "descripcion_problema": "Tu facility tiene capacidad ociosa pero no sabes...",
  "cuartil_superior": "Los operadores del cuartil superior miden su capacidad...",
  "n_respuestas_usadas": 42,
  "peso_primario_actual": 0.46
}
```

---

## Correr localmente

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

API disponible en `http://localhost:8000/docs`

---

## Deploy en Render

1. Crear cuenta en [render.com](https://render.com)
2. **New → Web Service → Connect a repository**
3. Seleccionar este repositorio
4. Render detecta `render.yaml` automáticamente
5. Click en **Deploy**

La URL pública queda disponible en el dashboard de Render.

---

## Estructura del repositorio

```
S07-26-Team36-benchmark-engine/
├── main.py                          # API FastAPI — punto de entrada
├── requirements.txt
├── Procfile                         # Para Railway
├── render.yaml                      # Para Render
├── data/
│   ├── questions_config.json        # 12 preguntas con dimensiones y ponderaciones
│   ├── public_baseline.json         # Distribución de referencia pública
│   └── friction_profiles.json       # 5 perfiles cualitativos (Gio)
├── src/scoring/
│   ├── scorer.py                    # Módulo 1: puntaje 0-100 por dimensión
│   ├── rebalancer.py                # Módulo 2: distribución mixta pública/primaria
│   ├── percentiles.py               # Módulo 3: posición relativa
│   └── qualitative.py              # Módulo 4: perfil de fricción
├── docs/
│   ├── scoring-rebalancing.md       # Documentación técnica (Gustavo)
│   ├── questions-profiles.md        # Preguntas y perfiles (Gio)
│   └── database-api.md              # BD y API (Marisol)
└── tests/
    └── test_pipeline.py             # Prueba del pipeline completo
```

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend / Motor | Python 3.12 + FastAPI |
| Base de datos | SQLite (MVP) |
| Deploy | Render / Railway |
| Tests | pytest |

---

## Equipo

| Nombre | Rol | Módulo |
|--------|-----|--------|
| Gustavo | Data Scientist | Motor de scoring, percentiles y rebalanceo dinámico |
| Gio | Data Analyst | Diseño de preguntas y perfiles cualitativos |
| Marisol | Functional Analyst | Base de datos, API y deploy |
