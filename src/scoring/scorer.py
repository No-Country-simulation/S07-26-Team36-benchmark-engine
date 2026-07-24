import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent.parent / "data" / "questions_config.json"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def normalizar(valor: int) -> float:
    """Convierte escala 1-4 a 0-100."""
    return round((valor - 1) / 3 * 100, 2)


def calculate_scores(respuestas: dict[str, int]) -> dict:
    """
    respuestas: {"P1": 3, "P2": 1, ...} — escala 1 a 4 por pregunta.
    Devuelve scores 0-100 por dimensión y score total ponderado.
    """
    config = load_config()
    preguntas = config["preguntas"]
    pesos_dimensiones = config["pesos_dimensiones"]

    acumulado: dict[str, list[float]] = {d: [] for d in pesos_dimensiones}

    for pregunta_id, opcion in respuestas.items():
        if pregunta_id not in preguntas:
            raise ValueError(f"Pregunta desconocida: {pregunta_id}")
        if opcion not in (1, 2, 3, 4):
            raise ValueError(f"Opción inválida '{opcion}' para {pregunta_id} — usar 1, 2, 3 o 4")
        dimension = preguntas[pregunta_id]["dimension"]
        acumulado[dimension].append(normalizar(opcion))

    scores_por_dimension = {
        d: round(sum(v) / len(v), 2) if v else 0.0
        for d, v in acumulado.items()
    }

    score_total = round(
        sum(scores_por_dimension[d] * pesos_dimensiones[d] for d in pesos_dimensiones), 2
    )

    return {
        "scores_por_dimension": scores_por_dimension,
        "score_total": score_total,
    }
