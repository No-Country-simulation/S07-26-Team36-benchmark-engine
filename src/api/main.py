import json
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

# 1. Importaciones exactas de los 3 módulos creados por Data Science
from src.scoring.scorer import calculate_scores
from src.scoring.rebalancer import calcular_distribucion_mixta
from src.scoring.percentiles import calcular_percentiles

app = FastAPI(
    title="Benchmark de Madurez - AI Agents",
    description="API para procesamiento de encuesta y cálculo de percentiles",
    version="1.0.0"
)

DB_PATH = "benchmark.db"

# Esquema para recibir las respuestas desde el Frontend
class AssessmentPayload(BaseModel):
    respuestas: Dict[str, str]

# Función para conectar a la Base de Datos SQLite
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Inicializar tabla de histórico en la base de datos
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            respuestas_json TEXT,
            score_total REAL,
            percentil_global REAL,
            dimension_mas_debil TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Función auxiliar para contar las respuestas en BD (requerido por rebalancer.py)
def count_total_responses() -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM assessment_responses")
    total = cursor.fetchone()[0]
    conn.close()
    return total


@app.post("/api/v1/submit")
def submit_assessment(payload: AssessmentPayload):
    try:
        # PASO 1: Calcular puntuaciones base
        scores = calculate_scores(payload.respuestas)

        # PASO 2: Obtener total de respuestas registradas y calcular distribución mixta
        n_primario = count_total_responses()
        distribucion_mixta = calcular_distribucion_mixta(n_primario=n_primario)

        # PASO 3: Calcular percentiles y dimensión más débil
        resultado_final = calcular_percentiles(scores, distribucion_mixta)

        # PASO 4: Guardar el registro en la base de datos SQLite
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO assessment_responses (
                respuestas_json, score_total, percentil_global, dimension_mas_debil
            )
            VALUES (?, ?, ?, ?)
        """, (
            json.dumps(payload.respuestas),
            resultado_final["score_total"],
            resultado_final["percentil_global"],
            resultado_final["dimension_mas_debil"]
        ))
        conn.commit()
        conn.close()

        # PASO 5: Devolver la respuesta completa al cliente
        return {
            "status": "success",
            "data": resultado_final
        }

    except ValueError as e:
        # Errores de validación de preguntas u opciones
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Errores no controlados del servidor
        raise HTTPException(status_code=500, detail=f"Error interno en la API: {str(e)}")