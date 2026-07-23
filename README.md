# Benchmark Engine — S07-26 Team 36

Motor de benchmark de madurez operacional para data centers.

Mide la capacidad de un operador para coordinar las capas físicas y operativas de su facility, calcula su posición relativa en la industria y genera un output personalizado con su perfil de fricción principal.

---

## El problema que resuelve

Los data centers modernos tienen capacidad pagada y encendida que no produce nada porque las capas físicas y operativas no se coordinan entre sí. Este benchmark diagnostica ese problema y posiciona al operador dentro de la industria — un dato que no existe en ningún otro lugar.

---

## Las cinco dimensiones del benchmark

| Dimensión | Qué mide |
|-----------|----------|
| Visibilidad cross-layer | ¿Tiene el operador una vista unificada de energía, cooling y workloads? |
| Atribución de fricción | ¿En qué interfaz entre capas percibe más pérdida de capacidad? |
| Latencia de coordinación | Cuando cambia el workload, ¿qué tan rápido se ajustan cooling y energía? |
| Auto-cuantificación | ¿Sabe el operador cuánta stranded capacity tiene? |
| Bloqueantes | ¿Qué le impediría resolver el problema aunque supiera dónde está? |

---

## Arquitectura del pipeline

```
[ Respuestas del Cuestionario ]
             │
             ▼
┌────────────────────────────────┐
│ 0. Validación e Ingesta        │  Verifica formulario completo, anonimiza y persiste
└───────────────┬────────────────┘
                │
                ├──────────────────────────────────────┐
                ▼                                      ▼
   [ PostgreSQL — respuesta anónima ]    [ Continúa el pipeline ]
                │
                ▼
┌────────────────────────────────┐
│ 1. Módulo de Scoring           │  Opciones del formulario → puntaje 0-100 por dimensión
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ 2. Módulo de Rebalanceo        │  Mezcla datos públicos + primarios según N acumulado
│    Dinámico                    │  Produce la distribución de referencia actualizada
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ 3. Módulo de Percentiles       │  Posiciona al operador contra la distribución
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ 4. Módulo de Inferencia        │  Dimensión más débil → perfil de fricción
│    Cualitativa                 │  Descripción del cuartil superior en esa dimensión
└───────────────┬────────────────┘
                │
                ▼
        [ JSON para PDF ]
```

---

## Estructura del repositorio

```
S07-26-Team36-benchmark-engine/
├── README.md
├── docs/
│   ├── scoring-rebalancing.md      # Motor de scoring, percentiles y rebalanceo (Gustavo)
│   ├── questions-profiles.md       # Diseño de preguntas y perfiles cualitativos (Gio)
│   └── database-api.md             # Base de datos, API y deploy (Marisol)
├── src/
│   ├── scoring/                    # Módulos 1-3: scoring, rebalanceo, percentiles
│   ├── qualitative/                # Módulo 4: inferencia cualitativa
│   ├── api/                        # Endpoints FastAPI
│   └── common/                     # Schemas Pydantic, utilidades compartidas
├── database/
│   └── schema.sql                  # DDL PostgreSQL — fuente de verdad
├── tests/
└── .env.example
```

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend / Motor | Python 3.12 + FastAPI |
| Base de datos | PostgreSQL |
| Package manager | uv |
| Tests | pytest |
| Deploy | Railway / Render |

---

## Equipo

| Nombre | Rol | Módulo |
|--------|-----|--------|
| Gustavo | Data Scientist | Motor de scoring, percentiles y rebalanceo dinámico |
| Gio | Data Analyst | Diseño de preguntas y perfiles cualitativos |
| Marisol | Functional Analyst | Base de datos, API y deploy |
