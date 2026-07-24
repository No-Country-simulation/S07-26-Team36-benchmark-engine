import sqlite3
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scoring.scorer import calculate_scores
from scoring.rebalancer import calcular_distribucion_mixta
from scoring.percentiles import calcular_percentiles
from scoring.qualitative import get_qualitative_output

app = FastAPI(
    title="Data Center Maturity Benchmark API",
    description="Motor de benchmark de madurez operacional para data centers.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

DB_PATH = "benchmark.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            p1 INTEGER, p2 INTEGER, p3 INTEGER,
            p4 INTEGER, p5 INTEGER,
            p6 INTEGER, p7 INTEGER, p8 INTEGER,
            p9 INTEGER, p10 INTEGER,
            p11 INTEGER, p12 INTEGER,
            score_total REAL,
            percentil_global REAL,
            dimension_mas_debil TEXT,
            nombre_perfil TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


class BenchmarkInput(BaseModel):
    P1:  int = Field(..., ge=1, le=4)
    P2:  int = Field(..., ge=1, le=4)
    P3:  int = Field(..., ge=1, le=4)
    P4:  int = Field(..., ge=1, le=4)
    P5:  int = Field(..., ge=1, le=4)
    P6:  int = Field(..., ge=1, le=4)
    P7:  int = Field(..., ge=1, le=4)
    P8:  int = Field(..., ge=1, le=4)
    P9:  int = Field(..., ge=1, le=4)
    P10: int = Field(..., ge=1, le=4)
    P11: int = Field(..., ge=1, le=4)
    P12: int = Field(..., ge=1, le=4)


def get_n_responses() -> int:
    conn = sqlite3.connect(DB_PATH)
    n = conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
    conn.close()
    return n


@app.get("/")
def home():
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"status": "ok", "message": "Benchmark API funcionando."}

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/submit")
def submit_benchmark(data: BenchmarkInput):
    respuestas = {f"P{i}": getattr(data, f"P{i}") for i in range(1, 13)}

    try:
        scores = calculate_scores(respuestas)
        distribucion = calcular_distribucion_mixta(n_primario=get_n_responses())
        resultado = calcular_percentiles(scores, distribucion)
        perfil = get_qualitative_output(resultado["dimension_mas_debil"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el motor de scoring: {e}")

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO responses
              (p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,
               score_total, percentil_global, dimension_mas_debil, nombre_perfil)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data.P1, data.P2, data.P3, data.P4, data.P5, data.P6,
            data.P7, data.P8, data.P9, data.P10, data.P11, data.P12,
            resultado["score_total"],
            resultado["percentil_global"],
            resultado["dimension_mas_debil"],
            perfil["nombre_perfil"],
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {e}")

    return {
        "status": "success",
        "score_total": resultado["score_total"],
        "percentil_global": resultado["percentil_global"],
        "scores_por_dimension": resultado["scores_por_dimension"],
        "percentiles_por_dimension": resultado["percentiles_por_dimension"],
        "dimension_mas_debil": resultado["dimension_mas_debil"],
        "nombre_perfil": perfil["nombre_perfil"],
        "descripcion_problema": perfil["descripcion_problema"],
        "cuartil_superior": perfil["cuartil_superior"],
        "n_respuestas_usadas": resultado["n_respuestas_usadas"],
        "peso_primario_actual": resultado["peso_primario_actual"],
    }


@app.get("/api/v1/submissions")
def get_submissions():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM responses").fetchall()
    conn.close()
    return {"total_records": len(rows), "data": [dict(r) for r in rows]}


@app.get("/api/v1/report/{submission_id}")
def get_report(submission_id: int):
    """
    Devuelve el JSON estructurado listo para generar el PDF del reporte.
    Incluye scores, percentiles, perfil de fricción y recomendación.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM responses WHERE id = ?", (submission_id,)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Submission {submission_id} no encontrada.")

    row = dict(row)

    respuestas = {f"P{i}": row[f"p{i}"] for i in range(1, 13)}
    scores = calculate_scores(respuestas)
    perfil = get_qualitative_output(row["dimension_mas_debil"])

    LABELS = {
        "visibilidad_cross_layer": "Visibilidad Cross-Layer",
        "atribucion_friccion":     "Atribución de Fricción",
        "latencia_coordinacion":   "Latencia de Coordinación",
        "auto_cuantificacion":     "Auto-Cuantificación",
        "bloqueantes":             "Bloqueantes",
    }

    return {
        "reporte": {
            "submission_id": submission_id,
            "fecha": row["created_at"],
            "score_total": row["score_total"],
            "percentil_global": row["percentil_global"],
            "interpretacion_percentil": (
                f"Tu facility supera al {row['percentil_global']:.0f}% "
                "de los operadores de la industria."
            ),
            "dimensiones": [
                {
                    "nombre": LABELS[d],
                    "clave": d,
                    "score": scores["scores_por_dimension"][d],
                    "es_punto_debil": d == row["dimension_mas_debil"],
                }
                for d in LABELS
            ],
            "perfil_friccion": {
                "nombre": perfil["nombre_perfil"],
                "descripcion": perfil["descripcion_problema"],
                "recomendacion": perfil["cuartil_superior"],
            },
            "contexto_dataset": {
                "total_respuestas": get_n_responses(),
                "nota": (
                    "Tu posición se calcula contra una distribución que combina "
                    "datos de la industria (Uptime Institute, Gartner) con las "
                    "respuestas acumuladas en este benchmark."
                ),
            },
        }
    }
