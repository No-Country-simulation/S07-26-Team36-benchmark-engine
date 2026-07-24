import json
from pathlib import Path

PROFILES_PATH = Path(__file__).parent.parent.parent / "data" / "friction_profiles.json"


def load_profiles() -> dict:
    with open(PROFILES_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_qualitative_output(dimension_mas_debil: str) -> dict:
    profiles = load_profiles()
    if dimension_mas_debil not in profiles:
        return {
            "nombre_perfil": "Perfil no disponible",
            "descripcion_problema": "",
            "cuartil_superior": "",
        }
    return profiles[dimension_mas_debil]
