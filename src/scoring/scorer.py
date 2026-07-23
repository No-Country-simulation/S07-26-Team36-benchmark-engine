import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent.parent / "data" / "questions_config.json"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def calculate_scores(respuestas: dict[str, str]) -> dict:
    config = load_config()
    preguntas = config["preguntas"]
    pesos_dimensiones = config["pesos_dimensiones"]

    dimensiones = list(pesos_dimensiones.keys())
    acumulado = {d: [] for d in dimensiones}

    for pregunta_id, opcion_elegida in respuestas.items():
        if pregunta_id not in preguntas:
            raise ValueError(f"Pregunta desconocida: {pregunta_id}")
        pregunta = preguntas[pregunta_id]
        if opcion_elegida not in pregunta["opciones"]:
            raise ValueError(f"Opción inválida '{opcion_elegida}' para {pregunta_id}")
        peso = pregunta["opciones"][opcion_elegida]["peso"]
        acumulado[pregunta["dimension"]].append(peso)

    scores_por_dimension = {}
    for dimension, pesos in acumulado.items():
        scores_por_dimension[dimension] = round(sum(pesos) / len(pesos), 2) if pesos else 0.0

    score_total = round(
        sum(scores_por_dimension[d] * pesos_dimensiones[d] for d in dimensiones), 2
    )

    return {
        "scores_por_dimension": scores_por_dimension,
        "score_total": score_total,
    }
