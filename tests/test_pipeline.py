import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scoring.scorer import calculate_scores
from scoring.rebalancer import calcular_distribucion_mixta
from scoring.percentiles import calcular_percentiles
from scoring.qualitative import get_qualitative_output

# Operador con madurez baja (todo 1)
RESPUESTAS_BAJAS = {f"P{i}": 1 for i in range(1, 13)}

# Operador con madurez alta (todo 4)
RESPUESTAS_ALTAS = {f"P{i}": 4 for i in range(1, 13)}

# Operador mixto realista
RESPUESTAS_MIXTAS = {
    "P1": 2, "P2": 1, "P3": 3,
    "P4": 1, "P5": 2,
    "P6": 2, "P7": 1, "P8": 2,
    "P9": 1, "P10": 1,
    "P11": 3, "P12": 2,
}


def correr_pipeline(respuestas: dict, n_primario: int = 0, label: str = "") -> dict:
    scores = calculate_scores(respuestas)
    distribucion = calcular_distribucion_mixta(n_primario)
    resultado = calcular_percentiles(scores, distribucion)
    perfil = get_qualitative_output(resultado["dimension_mas_debil"])

    resultado_completo = {**resultado, **perfil}

    print(f"\n{'='*60}")
    print(f"Operador: {label}")
    print(f"Score total:      {resultado_completo['score_total']}")
    print(f"Percentil global: {resultado_completo['percentil_global']}°")
    print(f"Dimensión débil:  {resultado_completo['dimension_mas_debil']}")
    print(f"Perfil:           {resultado_completo['nombre_perfil']}")
    print(f"Peso primario:    {resultado_completo['peso_primario_actual']}")
    print(f"\nDescripción:")
    print(f"  {resultado_completo['descripcion_problema']}")
    print(f"\nQué hace el cuartil superior:")
    print(f"  {resultado_completo['cuartil_superior']}")
    print(f"\nPercentiles por dimensión:")
    for dim, pct in resultado_completo["percentiles_por_dimension"].items():
        score = resultado_completo["scores_por_dimension"][dim]
        print(f"  {dim:<30} score={score:>6}  percentil={pct:>5}°")

    return resultado_completo


if __name__ == "__main__":
    correr_pipeline(RESPUESTAS_BAJAS,  n_primario=0,   label="Madurez baja  (N=0 respuestas en BD)")
    correr_pipeline(RESPUESTAS_ALTAS,  n_primario=0,   label="Madurez alta  (N=0 respuestas en BD)")
    correr_pipeline(RESPUESTAS_MIXTAS, n_primario=0,   label="Mixto         (N=0 respuestas en BD)")
    correr_pipeline(RESPUESTAS_MIXTAS, n_primario=100, label="Mixto         (N=100 respuestas en BD)")
