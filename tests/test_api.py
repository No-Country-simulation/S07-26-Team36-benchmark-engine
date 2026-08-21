import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


class TestAPIEndpoints:
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_home_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_submit_valid_responses(self):
        payload = {f"P{i}": 2 for i in range(1, 13)}
        response = client.post("/api/v1/submit", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "score_total" in data
        assert "percentil_global" in data
        assert "scores_por_dimension" in data
        assert "percentiles_por_dimension" in data
        assert "dimension_mas_debil" in data
        assert "nombre_perfil" in data

    def test_submit_invalid_response_too_high(self):
        payload = {f"P{i}": 2 for i in range(1, 13)}
        payload["P1"] = 5
        response = client.post("/api/v1/submit", json=payload)
        assert response.status_code == 422

    def test_submit_invalid_response_too_low(self):
        payload = {f"P{i}": 2 for i in range(1, 13)}
        payload["P1"] = 0
        response = client.post("/api/v1/submit", json=payload)
        assert response.status_code == 422

    def test_submit_missing_field(self):
        payload = {f"P{i}": 2 for i in range(1, 12)}
        response = client.post("/api/v1/submit", json=payload)
        assert response.status_code == 422

    def test_get_submissions(self):
        response = client.get("/api/v1/submissions")
        assert response.status_code == 200
        data = response.json()
        assert "total_records" in data
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_get_report_not_found(self):
        response = client.get("/api/v1/report/999999")
        assert response.status_code == 404

    def test_get_report_pdf_not_found(self):
        response = client.get("/api/v1/report/999999/pdf")
        assert response.status_code == 404

    def test_dashboard_stats(self):
        response = client.get("/api/v1/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_responses" in data
        assert "score_promedio" in data
        assert "distribucion_scores" in data
        assert "distribucion_perfiles" in data

    def test_dashboard_page(self):
        response = client.get("/dashboard")
        assert response.status_code == 200


class TestAPIIntegration:
    def test_full_flow_submit_and_report(self):
        payload = {f"P{i}": 3 for i in range(1, 13)}
        submit_resp = client.post("/api/v1/submit", json=payload)
        assert submit_resp.status_code == 200
        submit_data = submit_resp.json()

        submission_id = None
        submissions = client.get("/api/v1/submissions").json()
        if submissions["data"]:
            submission_id = submissions["data"][-1]["id"]

        if submission_id:
            report_resp = client.get(f"/api/v1/report/{submission_id}")
            assert report_resp.status_code == 200
            report_data = report_resp.json()
            assert "reporte" in report_data
            assert report_data["reporte"]["submission_id"] == submission_id

            pdf_resp = client.get(f"/api/v1/report/{submission_id}/pdf")
            assert pdf_resp.status_code == 200
            assert pdf_resp.headers["content-type"] == "application/pdf"
            assert len(pdf_resp.content) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])