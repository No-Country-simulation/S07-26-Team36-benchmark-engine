import json
import math
import os
from pathlib import Path

BASELINE_PATH = Path(__file__).parent.parent.parent / "data" / "public_baseline.json"
K = float(os.getenv("REBALANCING_K", "50"))


def load_baseline() -> dict:
    with open(BASELINE_PATH, encoding="utf-8") as f:
        return json.load(f)


def calcular_pesos(n_primario: int) -> tuple[float, float]:
    peso_primario = n_primario / (n_primario + K)
    peso_publico = K / (n_primario + K)
    return round(peso_primario, 4), round(peso_publico, 4)


def calcular_distribucion_mixta(
    n_primario: int,
    stats_primarios: dict | None = None,
) -> dict:
    """
    Devuelve media y std mezcladas para score_total y cada dimensión.

    stats_primarios: dict con la misma estructura que public_baseline,
                     calculado a partir de las respuestas reales en BD.
                     Si es None o n_primario == 0, se usa 100% datos públicos.
    """
    baseline = load_baseline()
    peso_primario, peso_publico = calcular_pesos(n_primario)

    dimensiones = list(baseline["distribucion_por_dimension"].keys())
    resultado = {"distribucion_por_dimension": {}, "distribucion_score_total": {}}

    for dimension in dimensiones:
        pub = baseline["distribucion_por_dimension"][dimension]

        if stats_primarios and n_primario > 0:
            pri = stats_primarios["distribucion_por_dimension"][dimension]
        else:
            pri = pub

        media_mixta = peso_publico * pub["media"] + peso_primario * pri["media"]
        # varianza mezclada (aproximación por suma ponderada de varianzas)
        var_mixta = peso_publico * pub["std"] ** 2 + peso_primario * pri["std"] ** 2
        std_mixta = math.sqrt(var_mixta)

        resultado["distribucion_por_dimension"][dimension] = {
            "media": round(media_mixta, 4),
            "std": round(std_mixta, 4),
        }

    pub_total = baseline["distribucion_score_total"]
    pri_total = stats_primarios["distribucion_score_total"] if stats_primarios and n_primario > 0 else pub_total

    media_total = peso_publico * pub_total["media"] + peso_primario * pri_total["media"]
    var_total = peso_publico * pub_total["std"] ** 2 + peso_primario * pri_total["std"] ** 2

    resultado["distribucion_score_total"] = {
        "media": round(media_total, 4),
        "std": round(math.sqrt(var_total), 4),
    }
    resultado["peso_primario"] = peso_primario
    resultado["peso_publico"] = peso_publico
    resultado["n_primario"] = n_primario

    return resultado
