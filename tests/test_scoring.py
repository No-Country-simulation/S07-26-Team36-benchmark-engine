import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scoring.scorer import calculate_scores
from scoring.rebalancer import calcular_distribucion_mixta, calcular_pesos
from scoring.percentiles import calcular_percentiles, _cdf_normal
from scoring.qualitative import get_qualitative_output


RESPUESTAS_BAJAS = {f"P{i}": 1 for i in range(1, 13)}
RESPUESTAS_ALTAS = {f"P{i}": 4 for i in range(1, 13)}
RESPUESTAS_MIXTAS = {
    "P1": 2, "P2": 1, "P3": 3,
    "P4": 1, "P5": 2,
    "P6": 2, "P7": 1, "P8": 2,
    "P9": 1, "P10": 1,
    "P11": 3, "P12": 2,
}


class TestScorer:
    def test_scores_bajas_retorna_cero(self):
        result = calculate_scores(RESPUESTAS_BAJAS)
        assert result["score_total"] == 0.0
        for dim_score in result["scores_por_dimension"].values():
            assert dim_score == 0.0

    def test_scores_altas_retorna_cien(self):
        result = calculate_scores(RESPUESTAS_ALTAS)
        assert result["score_total"] == 100.0
        for dim_score in result["scores_por_dimension"].values():
            assert dim_score == 100.0

    def test_scores_mixtas_rango_valido(self):
        result = calculate_scores(RESPUESTAS_MIXTAS)
        assert 0 <= result["score_total"] <= 100
        for dim_score in result["scores_por_dimension"].values():
            assert 0 <= dim_score <= 100

    def test_pregunta_invalida_raise_value_error(self):
        invalid = {**RESPUESTAS_MIXTAS, "P13": 1}
        with pytest.raises(ValueError, match="Pregunta desconocida"):
            calculate_scores(invalid)

    def test_opcion_invalida_raise_value_error(self):
        invalid = {**RESPUESTAS_MIXTAS, "P1": 5}
        with pytest.raises(ValueError, match="Opci.n inv.lida"):
            calculate_scores(invalid)

    def test_estructura_output_correcta(self):
        result = calculate_scores(RESPUESTAS_MIXTAS)
        assert "scores_por_dimension" in result
        assert "score_total" in result
        assert set(result["scores_por_dimension"].keys()) == {
            "visibilidad_cross_layer",
            "atribucion_friccion",
            "latencia_coordinacion",
            "auto_cuantificacion",
            "bloqueantes",
        }


class TestRebalancer:
    def test_calcular_pesos_n_cero(self):
        p_pri, p_pub = calcular_pesos(0)
        assert p_pri == 0.0
        assert p_pub == 1.0

    def test_calcular_pesos_n_igual_k(self):
        p_pri, p_pub = calcular_pesos(50)
        assert p_pri == 0.5
        assert p_pub == 0.5

    def test_calcular_pesos_n_mayor_k(self):
        p_pri, p_pub = calcular_pesos(200)
        assert p_pri == 0.8
        assert p_pub == 0.2

    def test_distribucion_mixta_sin_primarios_usa_publico(self):
        result = calcular_distribucion_mixta(n_primario=0)
        assert result["peso_primario"] == 0.0
        assert result["peso_publico"] == 1.0
        assert "distribucion_por_dimension" in result
        assert "distribucion_score_total" in result

    def test_distribucion_mixta_con_primarios_mezcla(self):
        stats_pri = {
            "distribucion_por_dimension": {
                "visibilidad_cross_layer": {"media": 80, "std": 5},
                "atribucion_friccion": {"media": 70, "std": 5},
                "latencia_coordinacion": {"media": 75, "std": 5},
                "auto_cuantificacion": {"media": 60, "std": 5},
                "bloqueantes": {"media": 85, "std": 5},
            },
            "distribucion_score_total": {"media": 74, "std": 4},
        }
        result = calcular_distribucion_mixta(n_primario=100, stats_primarios=stats_pri)
        assert result["peso_primario"] == pytest.approx(100/150, rel=0.01)
        assert result["peso_publico"] == pytest.approx(50/150, rel=0.01)

        for dim in stats_pri["distribucion_por_dimension"]:
            pub_media = 42.0 if dim == "visibilidad_cross_layer" else (
                35.0 if dim == "atribucion_friccion" else (
                    38.0 if dim == "latencia_coordinacion" else (
                        30.0 if dim == "auto_cuantificacion" else 45.0
                    )
                )
            )
            expected_media = result["peso_publico"] * pub_media + result["peso_primario"] * stats_pri["distribucion_por_dimension"][dim]["media"]
            assert result["distribucion_por_dimension"][dim]["media"] == pytest.approx(expected_media, rel=0.01)


class TestPercentiles:
    def test_cdf_normal_media(self):
        assert _cdf_normal(0, 0, 1) == 0.5

    def test_cdf_normal_desviacion_cero(self):
        assert _cdf_normal(10, 10, 0) == 1.0
        assert _cdf_normal(5, 10, 0) == 0.0

    def test_percentiles_estructura(self):
        scores = calculate_scores(RESPUESTAS_MIXTAS)
        distribucion = calcular_distribucion_mixta(n_primario=0)
        result = calcular_percentiles(scores, distribucion)

        assert "score_total" in result
        assert "percentil_global" in result
        assert "scores_por_dimension" in result
        assert "percentiles_por_dimension" in result
        assert "dimension_mas_debil" in result
        assert "n_respuestas_usadas" in result
        assert "peso_primario_actual" in result

        assert 0 <= result["percentil_global"] <= 100
        for pct in result["percentiles_por_dimension"].values():
            assert 0 <= pct <= 100

        assert result["dimension_mas_debil"] in result["scores_por_dimension"]

    def test_dimension_mas_debil_es_minimo(self):
        scores = calculate_scores(RESPUESTAS_MIXTAS)
        distribucion = calcular_distribucion_mixta(n_primario=0)
        result = calcular_percentiles(scores, distribucion)

        dim_debil = result["dimension_mas_debil"]
        min_score = min(scores["scores_por_dimension"].values())
        assert scores["scores_por_dimension"][dim_debil] == min_score


class TestQualitative:
    def test_perfil_existente_retorna_datos(self):
        perfiles = [
            "visibilidad_cross_layer",
            "atribucion_friccion",
            "latencia_coordinacion",
            "auto_cuantificacion",
            "bloqueantes",
        ]
        for dim in perfiles:
            result = get_qualitative_output(dim)
            assert "nombre_perfil" in result
            assert "descripcion_problema" in result
            assert "cuartil_superior" in result
            assert len(result["nombre_perfil"]) > 0
            assert len(result["descripcion_problema"]) > 0
            assert len(result["cuartil_superior"]) > 0

    def test_perfil_inexistente_retorna_default(self):
        result = get_qualitative_output("dimension_inexistente")
        assert result["nombre_perfil"] == "Perfil no disponible"
        assert result["descripcion_problema"] == ""
        assert result["cuartil_superior"] == ""


class TestPipelineIntegrado:
    def run_pipeline(self, respuestas, n_primario=0):
        scores = calculate_scores(respuestas)
        distribucion = calcular_distribucion_mixta(n_primario)
        resultado = calcular_percentiles(scores, distribucion)
        perfil = get_qualitative_output(resultado["dimension_mas_debil"])
        return {**resultado, **perfil}

    def test_pipeline_bajas(self):
        result = self.run_pipeline(RESPUESTAS_BAJAS, n_primario=0)
        assert result["score_total"] == 0.0
        assert result["percentil_global"] == pytest.approx(0.0, abs=1.0)
        assert result["nombre_perfil"] != "Perfil no disponible"

    def test_pipeline_altas(self):
        result = self.run_pipeline(RESPUESTAS_ALTAS, n_primario=0)
        assert result["score_total"] == 100.0
        assert result["percentil_global"] == pytest.approx(100.0, abs=1.0)
        assert result["nombre_perfil"] != "Perfil no disponible"

    def test_pipeline_mixtas(self):
        result = self.run_pipeline(RESPUESTAS_MIXTAS, n_primario=0)
        assert 0 < result["score_total"] < 100
        assert 0 < result["percentil_global"] < 100
        assert result["nombre_perfil"] != "Perfil no disponible"

    def test_pipeline_rebalanceo_cambia_con_n(self):
        result_0 = self.run_pipeline(RESPUESTAS_MIXTAS, n_primario=0)
        result_100 = self.run_pipeline(RESPUESTAS_MIXTAS, n_primario=100)
        assert result_0["peso_primario_actual"] == 0.0
        assert result_100["peso_primario_actual"] > 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])