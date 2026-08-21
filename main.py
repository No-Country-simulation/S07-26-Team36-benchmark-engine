import sqlite3
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field
from fpdf import FPDF

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


@app.get("/api/v1/dashboard/stats")
def get_dashboard_stats():
    """Estadísticas agregadas del dataset para el dashboard público."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM responses").fetchall()
    conn.close()

    if not rows:
        return {
            "total_responses": 0,
            "score_promedio": 0,
            "score_mediano": 0,
            "percentil_promedio": 0,
            "dimension_mas_debil_comun": None,
            "perfil_mas_comun": None,
            "distribucion_scores": {},
            "distribucion_perfiles": {},
            "distribucion_dimensiones_debiles": {},
            "peso_primario_actual": 0,
        }

    data = [dict(r) for r in rows]
    total = len(data)

    scores = [r["score_total"] for r in data]
    percentiles = [r["percentil_global"] for r in data]

    score_promedio = round(sum(scores) / total, 1)
    score_mediano = round(sorted(scores)[total // 2], 1)
    percentil_promedio = round(sum(percentiles) / total, 1)

    from collections import Counter
    dim_counter = Counter(r["dimension_mas_debil"] for r in data)
    perfil_counter = Counter(r["nombre_perfil"] for r in data)

    dimension_mas_debil_comun = dim_counter.most_common(1)[0][0] if dim_counter else None
    perfil_mas_comun = perfil_counter.most_common(1)[0][0] if perfil_counter else None

    distribucion_scores = {
        "0-20": sum(1 for s in scores if s < 20),
        "20-40": sum(1 for s in scores if 20 <= s < 40),
        "40-60": sum(1 for s in scores if 40 <= s < 60),
        "60-80": sum(1 for s in scores if 60 <= s < 80),
        "80-100": sum(1 for s in scores if s >= 80),
    }

    LABELS = {
        "visibilidad_cross_layer": "Visibilidad Cross-Layer",
        "atribucion_friccion": "Atribución de Fricción",
        "latencia_coordinacion": "Latencia de Coordinación",
        "auto_cuantificacion": "Auto-Cuantificación",
        "bloqueantes": "Bloqueantes",
    }

    return {
        "total_responses": total,
        "score_promedio": score_promedio,
        "score_mediano": score_mediano,
        "percentil_promedio": percentil_promedio,
        "dimension_mas_debil_comun": {
            "clave": dimension_mas_debil_comun,
            "label": LABELS.get(dimension_mas_debil_comun, dimension_mas_debil_comun),
            "count": dim_counter.get(dimension_mas_debil_comun, 0),
        } if dimension_mas_debil_comun else None,
        "perfil_mas_comun": {
            "nombre": perfil_mas_comun,
            "count": perfil_counter.get(perfil_mas_comun, 0),
        } if perfil_mas_comun else None,
        "distribucion_scores": distribucion_scores,
        "distribucion_perfiles": dict(perfil_counter),
        "distribucion_dimensiones_debiles": {LABELS.get(k, k): v for k, v in dim_counter.items()},
        "peso_primario_actual": round(data[-1].get("peso_primario_actual", 0) if data else 0, 2) if data else 0,
    }


@app.get("/dashboard")
def dashboard():
    index = STATIC_DIR / "dashboard.html"
    if index.exists():
        return FileResponse(str(index))
    return {"status": "ok", "message": "Dashboard no disponible. Crea static/dashboard.html"}


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


class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(249, 115, 22)
        self.cell(0, 12, "Benchmark de Madurez - Data Centers", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(249, 115, 22)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def kv_pair(self, key, value):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(60, 60, 60)
        self.cell(60, 6, key)
        self.set_font("Helvetica", "", 10)
        self.cell(0, 6, str(value), new_x="LMARGIN", new_y="NEXT")

    def score_bar(self, label, score, is_weak=False):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(249, 115, 22) if is_weak else self.set_text_color(60, 60, 60)
        self.cell(70, 6, label)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        bar_width = int(score * 1.2)
        self.cell(bar_width, 6, "", fill=True)
        self.cell(0, 6, f" {score:.1f}", new_x="LMARGIN", new_y="NEXT")
        self.set_fill_color(249, 115, 22)


def generate_pdf_report(row: dict, scores: dict, perfil: dict, submission_id: int) -> bytes:
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()

    LABELS = {
        "visibilidad_cross_layer": "Visibilidad Cross-Layer",
        "atribucion_friccion":     "Atribución de Fricción",
        "latencia_coordinacion":   "Latencia de Coordinación",
        "auto_cuantificacion":     "Auto-Cuantificación",
        "bloqueantes":             "Bloqueantes",
    }

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, "Reporte de Benchmark de Madurez Operacional", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.kv_pair("ID de Submission:", submission_id)
    pdf.kv_pair("Fecha:", row["created_at"])
    pdf.ln(4)

    pdf.section_title("1. Resumen Ejecutivo")
    pdf.kv_pair("Score Total:", f"{row['score_total']:.1f} / 100")
    pdf.kv_pair("Percentil Global:", f"{row['percentil_global']:.1f}%")
    pdf.body_text(f"Tu facility supera al {row['percentil_global']:.0f}% de los operadores de la industria.")
    pdf.ln(2)

    pdf.section_title("2. Desglose por Dimensión")
    for dim_key, label in LABELS.items():
        score = scores["scores_por_dimension"][dim_key]
        is_weak = dim_key == row["dimension_mas_debil"]
        pdf.set_font("Helvetica", "B" if is_weak else "", 10)
        pdf.set_text_color(249, 115, 22) if is_weak else pdf.set_text_color(60, 60, 60)
        pdf.cell(70, 6, f"{label}{' *' if is_weak else ''}")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        bar_width = int(score * 1.2)
        pdf.set_fill_color(249, 115, 22)
        pdf.cell(bar_width, 6, "", fill=True)
        pdf.cell(0, 6, f" {score:.1f}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 5, "* Dimensión más débil (punto de fricción principal)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.section_title("3. Perfil de Fricción Principal")
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, perfil["nombre_perfil"], new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.body_text(perfil["descripcion_problema"])
    pdf.ln(2)

    pdf.section_title("4. Qué Hace Diferente el Cuartil Superior")
    pdf.body_text(perfil["cuartil_superior"])
    pdf.ln(4)

    pdf.section_title("5. Contexto del Dataset")
    n_total = get_n_responses()
    pdf.kv_pair("Total de respuestas en el dataset:", n_total)
    pdf.body_text(
        "Tu posición se calcula contra una distribución que combina "
        "datos de la industria (Uptime Institute, Gartner) con las "
        "respuestas acumuladas en este benchmark. El rebalanceo dinámico "
        "ajusta el peso de los datos propios conforme crece la muestra."
    )

    # fpdf2 output(dest='S') returns bytes/bytearray directly, avoiding temp file issues on Windows
    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin-1')
    elif isinstance(pdf_bytes, bytearray):
        pdf_bytes = bytes(pdf_bytes)
    return pdf_bytes


@app.get("/api/v1/report/{submission_id}/pdf")
def download_report_pdf(submission_id: int):
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

    pdf_bytes = generate_pdf_report(row, scores, perfil, submission_id)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=benchmark_report_{submission_id}.pdf"}
    )
