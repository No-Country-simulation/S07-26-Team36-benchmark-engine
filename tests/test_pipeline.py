import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scoring.scorer import calculate_scores
from scoring.rebalancer import calcular_distribucion_mixta
from scoring.percentiles import calcular_percentiles

# Operador con madurez baja
RESPUESTAS_BAJAS = {
    "P1": "A", "P2": "A", "P3": "A",
    "P4": "A", "P5": "A", "P6": "A",
    "P7": "A", "P8": "A", "P9": "A",
    "P10": "A", "P11": "A", "P12": "A",
    "P13": "A", "P14": "A", "P15": "A",
}

# Operador con madurez alta
RESPUESTAS_ALTAS = {
    "P1": "C", "P2": "C", "P3": "C",
    "P4": "C", "P5": "C", "P6": "C",
    "P7": "C", "P8": "C", "P9": "C",
    "P10": "C", "P11": "C", "P12": "C",
    "P13": "C", "P14": "C", "P15": "C",
}

# Operador mixto
RESPUESTAS_MIXTAS = {
    "P1": "B", "P2": "A", "P3": "C",
    "P4": "A", "P5": "B", "P6": "A",
    "P7": "B", "P8": "B", "P9": "A",
    "P10": "A", "P11": "A", "P12": "B",
    "P13": "B", "P14": "B", "P15": "A",
}


def correr_pipeline(respuestas: dict, n_primario: int = 0, label: str = "") -> dict:
    scores = calculate_scores(respuestas)
    distribucion = calcular_distribucion_mixta(n_primario)
    resultado = calcular_percentiles(scores, distribucion)
    print(f"\n{'='*50}")
    print(f"Operador: {label}")
    print(f"Score total:      {resultado['score_total']}")
    print(f"Percentil global: {resultado['percentil_global']}°")
    print(f"Dimensión débil:  {resultado['dimension_mas_debil']}")
    print(f"Peso primario:    {resultado['peso_primario_actual']}")
    print(f"Percentiles por dimensión:")
    for dim, pct in resultado["percentiles_por_dimension"].items():
        score = resultado["scores_por_dimension"][dim]
        print(f"  {dim:<30} score={score:>6}  percentil={pct:>5}°")
    return resultado


if __name__ == "__main__":
    correr_pipeline(RESPUESTAS_BAJAS,  n_primario=0,   label="Madurez baja  (N=0)")
    correr_pipeline(RESPUESTAS_ALTAS,  n_primario=0,   label="Madurez alta  (N=0)")
    correr_pipeline(RESPUESTAS_MIXTAS, n_primario=0,   label="Mixto         (N=0)")
    correr_pipeline(RESPUESTAS_MIXTAS, n_primario=100, label="Mixto         (N=100)")
