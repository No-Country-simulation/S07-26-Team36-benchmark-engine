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
     [ JSON / Reporte PDF / Dashboard ]
     [ Persistencia SQLite ]
```

---

## API — Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Formulario web del benchmark |
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/submit` | Enviar respuestas y recibir resultado (JSON) |
| `GET` | `/api/v1/submissions` | Listar todas las respuestas (anónimas) |
| `GET` | `/api/v1/report/{id}` | JSON estructurado para reporte por submission |
| `GET` | `/api/v1/report/{id}/pdf` | **Descargar reporte PDF** |
| `GET` | `/api/v1/dashboard/stats` | Estadísticas agregadas del dataset (JSON) |
| `GET` | `/dashboard` | **Dashboard público** con gráficas y stats |
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
Formulario web en `http://localhost:8000/`
Dashboard en `http://localhost:8000/dashboard`

### Variables de entorno

Copia `.env.example` a `.env` y ajusta:

```bash
cp .env.example .env
```

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Conexión PostgreSQL (producción) | `sqlite:///benchmark.db` |
| `REBALANCING_K` | Parámetro de mezcla (N/(N+K)) | `50` |
| `SECRET_KEY` | Clave secreta para sesiones/JWT | `change-this-in-production` |

---

## Tests automatizados

```bash
# Ejecutar toda la suite
pytest tests/ -v

# Solo tests de scoring
pytest tests/test_scoring.py -v

# Solo tests de API
pytest tests/test_api.py -v
```

**Cobertura actual:** 33 tests (21 scoring + 12 API) — todos pasando.

---

## Deploy en Render

🚀 **API en producción:** https://s07-26-team36-benchmark-engine-565u.onrender.com

| Recurso | URL |
|---------|-----|
| **Formulario web** | https://s07-26-team36-benchmark-engine-565u.onrender.com |
| **Dashboard público** | https://s07-26-team36-benchmark-engine-565u.onrender.com/dashboard |
| Documentación interactiva | https://s07-26-team36-benchmark-engine-565u.onrender.com/docs |
| Enviar benchmark (API) | `POST` https://s07-26-team36-benchmark-engine-565u.onrender.com/api/v1/submit |
| Reporte PDF | `GET` https://s07-26-team36-benchmark-engine-565u.onrender.com/api/v1/report/{id}/pdf |
| Stats dashboard (JSON) | `GET` https://s07-26-team36-benchmark-engine-565u.onrender.com/api/v1/dashboard/stats |

### Instrucciones de deploy propio

1. Crear cuenta en [render.com](https://render.com)
2. **New → Web Service → Connect a repository**
3. Seleccionar este repositorio
4. Render detecta `render.yaml` automáticamente
5. Click en **Deploy**

---

## Estructura del repositorio

```
S07-26-Team36-benchmark-engine/
├── main.py                          # API FastAPI — punto de entrada
├── requirements.txt
├── Procfile                         # Para Railway
├── render.yaml                      # Para Render
├── .env.example                     # Variables de entorno ejemplo
├── data/
│   ├── questions_config.json        # 12 preguntas con dimensiones y ponderaciones
│   ├── public_baseline.json         # Distribución de referencia pública (Uptime/Gartner/LBNL)
│   └── friction_profiles.json       # 5 perfiles cualitativos (Gio)
├── src/scoring/
│   ├── __init__.py
│   ├── scorer.py                    # Módulo 1: puntaje 0-100 por dimensión
│   ├── rebalancer.py                # Módulo 2: distribución mixta pública/primaria
│   ├── percentiles.py               # Módulo 3: posición relativa (CDF normal)
│   └── qualitative.py               # Módulo 4: perfil de fricción + recomendación
├── docs/
│   ├── scoring-rebalancing.md       # Documentación técnica (Gustavo)
│   ├── questions-profiles.md        # Preguntas y perfiles (Gio)
│   └── database-api.md              # BD y API (Marisol)
├── static/
│   ├── index.html                   # Formulario web (dark theme, tooltips, modal instrucciones)
│   └── dashboard.html               # Dashboard público con gráficas
└── tests/
    ├── test_scoring.py              # Tests unitarios del motor de scoring (21 tests)
    └── test_api.py                  # Tests de integración API (12 tests)
```

---

## Documentación del proyecto

| Documento | Descripción | Autor |
|-----------|-------------|-------|
| [README.md](README.md) | Este archivo — visión general, API, deploy, tests | Equipo |
| [docs/scoring-rebalancing.md](docs/scoring-rebalancing.md) | Motor de scoring, percentiles y rebalanceo dinámico | Gustavo |
| [docs/questions-profiles.md](docs/questions-profiles.md) | Diseño de 12 preguntas y 5 perfiles de fricción | Gio |
| [docs/database-api.md](docs/database-api.md) | Schema BD, endpoints, variables de entorno, deploy | Marisol |
| [Instructivo_Usuario.pdf](Instructivo_Usuario.pdf) | Guía paso a paso para operadores (PDF descargable) | Equipo |

---

## Herramientas y tecnologías

| Capa | Tecnología | Enlace |
|------|------------|--------|
| **Frontend** | HTML5 / CSS3 / Vanilla JS (ES6+) | [MDN Web Docs](https://developer.mozilla.org/) |
| **Backend / Motor** | Python 3.12 + FastAPI | [FastAPI](https://fastapi.tiangolo.com/) |
| **Validación** | Pydantic v2 | [Pydantic](https://docs.pydantic.dev/) |
| **Servidor ASGI** | Uvicorn | [Uvicorn](https://www.uvicorn.org/) |
| **Base de datos** | SQLite (MVP) / PostgreSQL (prod) | [SQLite](https://www.sqlite.org/) · [PostgreSQL](https://www.postgresql.org/) |
| **PDF Generation** | fpdf2 | [fpdf2](https://pyfpdf.github.io/fpdf2/) |
| **Testing** | pytest + pytest-asyncio | [pytest](https://docs.pytest.org/) |
| **Deploy** | Render | [Render](https://render.com/) |
| **CI/CD** | GitHub Actions (configurable) | [GitHub Actions](https://github.com/features/actions) |
| **Fuentes de datos públicos** | Uptime Institute, Gartner, LBNL | [Uptime](https://uptimeinstitute.com/) · [Gartner](https://www.gartner.com/) · [LBNL](https://eta.lbl.gov/) |

### Enlaces del proyecto

- **Repositorio:** https://github.com/No-Country-simulation/S07-26-Team36-benchmark-engine.git
- **API Producción:** https://s07-26-team36-benchmark-engine-565u.onrender.com
- **Formulario Web:** https://s07-26-team36-benchmark-engine-565u.onrender.com
- **Dashboard Público:** https://s07-26-team36-benchmark-engine-565u.onrender.com/dashboard
- **Swagger UI:** https://s07-26-team36-benchmark-engine-565u.onrender.com/docs

---

## Equipo

| Nombre | Rol | Módulo |
|--------|-----|--------|
| Gustavo | Data Scientist | Motor de scoring, percentiles y rebalanceo dinámico |
| Gio | Data Analyst | Diseño de preguntas y perfiles cualitativos |
| Marisol | Functional Analyst | Base de datos, API y deploy |

---

## Licencia

Proyecto académico — Sprint 7, TripleTen / No Country Simulation.