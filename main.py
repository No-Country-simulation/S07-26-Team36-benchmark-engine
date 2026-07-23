import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Data Center Maturity Benchmark API",
    description="API para procesar diagnósticos y guardar respuestas en SQLite.",
    version="1.0.0",
)


# 1. Definición de la estructura de entrada (Las 5 dimensiones, del 1 al 5)
class BenchmarkInput(BaseModel):
  d1_visibility: int = Field(
      ..., ge=1, le=5, description="Visibilidad Cross-layer (1-5)"
  )
  d2_friction: int = Field(
      ..., ge=1, le=5, description="Atribución de Fricción (1-5)"
  )
  d3_latency: int = Field(
      ..., ge=1, le=5, description="Latencia de Coordinación (1-5)"
  )
  d4_quantification: int = Field(
      ..., ge=1, le=5, description="Auto-cuantificación (1-5)"
  )
  d5_blockers: int = Field(..., ge=1, le=5, description="Bloqueantes (1-5)")


# 2. Función para crear la base de datos y la tabla automáticamente
def init_db():
  conn = sqlite3.connect("benchmark.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            d1 INTEGER NOT NULL,
            d2 INTEGER NOT NULL,
            d3 INTEGER NOT NULL,
            d4 INTEGER NOT NULL,
            d5 INTEGER NOT NULL,
            overall_score REAL NOT NULL,
            archetype TEXT NOT NULL
        )
    """)
  conn.commit()
  conn.close()


# Inicializamos la Base de Datos al arrancar el programa
init_db()


@app.get("/")
def home():
  return {
      "status": "ok",
      "message": "API del Benchmark de Data Centers funcionando correctamente.",
  }


# 3. Endpoint principal que recibe las 5 respuestas y calcula el score
@app.post("/api/v1/submit")
def submit_benchmark(data: BenchmarkInput):
  # Cálculo básico de puntuación (Escala 0 a 100)
  scores = [
      data.d1_visibility,
      data.d2_friction,
      data.d3_latency,
      data.d4_quantification,
      data.d5_blockers,
  ]
  overall_score = (sum(scores) / 5.0) * 20.0

  # Arquetipo de diagnóstico
  if overall_score >= 75:
    archetype = "Facilidad Next-Gen (Líder Autónomo)"
  elif overall_score >= 50:
    archetype = "Infraestructura en Transición"
  else:
    archetype = "Operación a Ciegas (El Apagafuegos)"

  # Guardar la respuesta anónima en SQLite
  try:
    conn = sqlite3.connect("benchmark.db")
    cursor = conn.cursor()
    cursor.execute(
        """
            INSERT INTO responses (d1, d2, d3, d4, d5, overall_score, archetype)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
        (
            data.d1_visibility,
            data.d2_friction,
            data.d3_latency,
            data.d4_quantification,
            data.d5_blockers,
            overall_score,
            archetype,
        ),
    )
    conn.commit()
    conn.close()
  except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Error al guardar en la base de datos: {str(e)}",
    )

  return {
      "status": "success",
      "overall_score": overall_score,
      "archetype": archetype,
      "message": "Respuesta guardada con éxito en la base de datos.",
  }


# 4. Endpoint para consultar todas las respuestas guardadas
@app.get("/api/v1/submissions")
def get_submissions():
  """Endpoint para que el equipo consulte todas las evaluaciones guardadas."""
  conn = sqlite3.connect("benchmark.db")
  conn.row_factory = (
      sqlite3.Row
  )  # Permite leer las columnas por su nombre (id, d1, score, etc.)
  cursor = conn.cursor()

  # Consulta a la tabla 'responses'
  cursor.execute("SELECT * FROM responses")
  rows = cursor.fetchall()
  conn.close()

  # Devuelve la cantidad de registros y la lista con todos los datos
  return {"total_records": len(rows), "data": [dict(row) for row in rows]}