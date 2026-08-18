import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scoring.scorer import calculate_scores
from scoring.rebalancer import calcular_distribucion_mixta
from scoring.percentiles import calcular_percentiles
from scoring.qualitative import get_qualitative_output

# --- Datos de prueba ---
RESPUESTAS_BAJAS = {f"P{i}": 1 for i in range(1, 13)}
RESPUESTAS_ALTAS = {f"P{i}": 4 for i in range(1, 13)}
RESPUESTAS_MIXTAS = {
    "P1": 2, "P2": 1, "P3": 3,
    "P4": 1, "P5": 2,
    "P6": 2, "P7": 1, "P8": 2,
    "P9": 1, "P10": 1,
    "P11": 3, "P12": 2,
}

# --- Función auxiliar (no empieza por 'test_', por ende pytest no la ejecuta directamente) ---
def ejecutar_pipeline(respuestas: dict, n_primario: int = 0) -> dict:
    scores = calculate_scores(respuestas)
    distribucion = calcular_distribucion_mixta(n_primario)
    resultado = calcular_percentiles(scores, distribucion)
    perfil = get_qualitative_output(resultado["dimension_mas_debil"])
    return {**resultado, **perfil}


# --- CASOS DE PRUEBA (Suite reconocida por pytest) ---

def test_pipeline_madurez_baja():
    resultado = ejecutar_pipeline(RESPUESTAS_BAJAS, n_primario=0)
    
    # Validaciones (Ajusta los valores esperados a la lógica de tu negocio)
    assert "score_total" in resultado
    assert "percentil_global" in resultado
    assert resultado["score_total"] is not None


def test_pipeline_madurez_alta():
    resultado = ejecutar_pipeline(RESPUESTAS_ALTAS, n_primario=0)
    
    assert "score_total" in resultado
    # Ejemplo: verificar que un operador alto tenga mayor puntaje que uno bajo
    assert resultado["score_total"] > 0


def test_pipeline_mixto_sin_historial():
    resultado = ejecutar_pipeline(RESPUESTAS_MIXTAS, n_primario=0)
    
    assert "dimension_mas_debil" in resultado
    assert "nombre_perfil" in resultado


def test_pipeline_mixto_con_historial():
    resultado = ejecutar_pipeline(RESPUESTAS_MIXTAS, n_primario=100)
    
    assert resultado["peso_primario_actual"] is not None