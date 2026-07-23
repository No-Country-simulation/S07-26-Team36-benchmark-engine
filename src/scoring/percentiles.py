import math


def _cdf_normal(x: float, media: float, std: float) -> float:
    """CDF de distribución normal — no requiere scipy."""
    if std == 0:
        return 1.0 if x >= media else 0.0
    z = (x - media) / (std * math.sqrt(2))
    return 0.5 * (1 + math.erf(z))


def calcular_percentiles(
    scores: dict,
    distribucion_mixta: dict,
) -> dict:
    """
    Recibe:
      scores: output de scorer.calculate_scores()
      distribucion_mixta: output de rebalancer.calcular_distribucion_mixta()

    Devuelve percentiles globales y por dimensión.
    """
    dist_dim = distribucion_mixta["distribucion_por_dimension"]
    dist_total = distribucion_mixta["distribucion_score_total"]

    percentiles_por_dimension = {}
    for dimension, score in scores["scores_por_dimension"].items():
        dist = dist_dim[dimension]
        percentil = _cdf_normal(score, dist["media"], dist["std"]) * 100
        percentiles_por_dimension[dimension] = round(percentil, 1)

    percentil_global = _cdf_normal(
        scores["score_total"], dist_total["media"], dist_total["std"]
    ) * 100

    dimension_mas_debil = min(
        scores["scores_por_dimension"],
        key=lambda d: scores["scores_por_dimension"][d],
    )

    return {
        "score_total": scores["score_total"],
        "percentil_global": round(percentil_global, 1),
        "scores_por_dimension": scores["scores_por_dimension"],
        "percentiles_por_dimension": percentiles_por_dimension,
        "dimension_mas_debil": dimension_mas_debil,
        "n_respuestas_usadas": distribucion_mixta["n_primario"],
        "peso_primario_actual": distribucion_mixta["peso_primario"],
    }
