"""
Phase 9 Agricultural Validation Test Suite.
Validates real-world farmer decision intelligence:
1. Missing soil tests handling (defaults from Soil Health Card, guidance notice, missing_soil_inputs flag).
2. Hostile environmental conditions trigger all_options_unsuitable.
3. Supporting factors, risk factors, and irrigation requirement per crop.
4. Empirically Calibrated Out-of-Fold Error Bounds labeling, disclaimer, and interval bounds.
5. High-yield regime (>500 kg/ha) coverage warning.
6. Amravati district localized variance coverage warning.
7. Cotton model 6-district boundary vs 7th district (Yavatmal) agricultural advisory scope.
8. Request validation bounds for soil and agronomic parameters.
9. SHAP feature attributions and explainability.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestFarmerInputQualityAndSoilHandling:
    """Verifies that missing soil inputs do not crash the API (422) and provide transparent SHC guidance."""

    def test_missing_soil_parameters_succeeds_with_defaults(self):
        """When a farmer cannot provide soil lab reports (N, P, K, pH), default values are applied
        and missing_soil_inputs is flagged with farmer_guidance."""
        payload = {
            "district": "Akola",
            "season": "Kharif",
            "temperature": 32.0,
            "rainfall": 750.0,
            "humidity": 65.0,
            "irrigation": False
        }
        response = client.post("/api/crop/recommend", json=payload)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert data.get("missing_soil_inputs") is True
        assert "farmer_guidance" in data
        assert "Soil Health Card" in data["farmer_guidance"]
        assert len(data["recommendations"]) > 0

    def test_provided_soil_parameters_not_flagged_as_missing(self):
        """When full soil measurements are supplied, missing_soil_inputs is False."""
        payload = {
            "district": "Wardha",
            "season": "Kharif",
            "temperature": 31.0,
            "rainfall": 850.0,
            "humidity": 70.0,
            "irrigation": True,
            "soil_ph": 7.4,
            "nitrogen": 75.0,
            "phosphorus": 35.0,
            "potassium": 210.0,
            "soil_moisture": 62.0
        }
        response = client.post("/api/crop/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data.get("missing_soil_inputs") is False

    def test_invalid_soil_bounds_rejected(self):
        """Negative nitrogen or impossible pH must return 422 Unprocessable Entity."""
        bad_ph_payload = {
            "district": "Nagpur",
            "season": "Kharif",
            "temperature": 32.0,
            "rainfall": 800.0,
            "humidity": 65.0,
            "soil_ph": 15.5  # pH > 14 is invalid
        }
        res_ph = client.post("/api/crop/recommend", json=bad_ph_payload)
        assert res_ph.status_code == 422

        bad_nitrogen_payload = {
            "district": "Nagpur",
            "season": "Kharif",
            "temperature": 32.0,
            "rainfall": 800.0,
            "humidity": 65.0,
            "nitrogen": -10.0  # Negative N is invalid
        }
        res_n = client.post("/api/crop/recommend", json=bad_nitrogen_payload)
        assert res_n.status_code == 422


class TestCropSuitabilityAndAgronomicDecisions:
    """Verifies biophysical suitability checks, supporting/risk factors, and all_options_unsuitable logic."""

    def test_extreme_heat_and_drought_triggers_all_options_unsuitable(self):
        """In a severe heat wave (48°C) and near-zero rain (20mm) without irrigation,
        no crop should be declared suitable. all_options_unsuitable must be True."""
        payload = {
            "district": "Washim",
            "season": "Summer",
            "temperature": 48.0,
            "rainfall": 20.0,
            "humidity": 15.0,
            "irrigation": False,
            "soil_ph": 8.0
        }
        response = client.post("/api/crop/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("all_options_unsuitable") is True
        assert "unsuitable_warning" in data
        assert "hostile" in data["unsuitable_warning"].lower() or "unsuitable" in data["unsuitable_warning"].lower()

    def test_recommendations_contain_supporting_and_risk_factors(self):
        """Every recommended crop must have structured supporting_factors, risk_factors, and irrigation_requirement."""
        payload = {
            "district": "Amravati",
            "season": "Kharif",
            "temperature": 30.0,
            "rainfall": 700.0,
            "humidity": 70.0,
            "irrigation": True
        }
        response = client.post("/api/crop/recommend", json=payload)
        assert response.status_code == 200
        recs = response.json()["recommendations"]
        assert len(recs) > 0
        for rec in recs:
            assert "supporting_factors" in rec
            assert isinstance(rec["supporting_factors"], list)
            assert "risk_factors" in rec
            assert isinstance(rec["risk_factors"], list)
            assert "irrigation_requirement" in rec
            assert "biophysical_suitability_score" in rec
            assert "ml_classifier_probability" in rec


class TestCottonUncertaintyAndCoverageBounds:
    """Verifies uncertainty communication, empirical out-of-fold error bounds, and coverage warnings."""

    def test_error_bounds_label_and_disclaimer(self):
        """Checks that cotton predictions return 'Empirically Calibrated Out-of-Fold Error Bounds'
        with clear disclaimer and finite sample error margins."""
        payload = {
            "district": "Akola",
            "target_year": 2024,
            "model_version": "candidate_six_district_thermal"
        }
        response = client.post("/api/cotton/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "prediction_interval" in data
        interval = data["prediction_interval"]
        assert interval["label"] == "Empirically Calibrated Out-of-Fold Error Bounds"
        assert interval["description"] == "Empirically Calibrated Out-of-Fold Error Bounds"
        assert "disclaimer" in interval
        assert "empirical historical error bounds" in interval["disclaimer"].lower()
        assert interval["half_width_kg_ha"] > 200.0  # 253.5 kg/ha
        assert interval["lower_bound_kg_per_ha"] >= 0.0
        assert interval["upper_bound_kg_per_ha"] > interval["lower_bound_kg_per_ha"]

    def test_amravati_triggers_microclimate_warning(self):
        """Amravati district must trigger micro-climate variance warning due to historical 76.9% coverage."""
        payload = {
            "district": "Amravati",
            "target_year": 2024,
            "model_version": "candidate_six_district_thermal"
        }
        response = client.post("/api/cotton/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        interval = data["prediction_interval"]
        warnings = interval.get("coverage_warnings", [])
        assert any("Amravati" in w and "76.9%" in w for w in warnings)

    def test_high_yield_regime_triggers_undercoverage_warning(self):
        """When predicted yield exceeds 500 kg/ha, high-yield regime warning must trigger
        explaining the empirical 71.4% coverage."""
        payload = {
            "district": "Wardha",
            "target_year": 2020,
            "model_version": "candidate_six_district_thermal"
        }
        response = client.post("/api/cotton/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        interval = data["prediction_interval"]
        warnings = interval.get("coverage_warnings", [])
        if data["predicted_yield_kg_ha"] > 500:
            assert any("71.4%" in w or "bumper" in w.lower() or "500" in w for w in warnings)

    def test_shap_explanation_available_and_directional(self):
        """Local SHAP feature attributions must be computed and returned."""
        payload = {
            "district": "Buldhana",
            "target_year": 2024,
            "model_version": "candidate_six_district_thermal"
        }
        response = client.post("/api/cotton/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
        assert data["explanation"]["available"] is True
        assert len(data["explanation"]["top_influential_features"]) > 0


class TestDistrictBoundaryClarification:
    """Verifies that Yavatmal (7th district) has agricultural advisory intelligence,
    while cotton 6-district model boundaries are properly respected."""

    def test_yavatmal_in_crop_recommendation(self):
        """Crop recommendation supports Yavatmal using Vidarbha regional benchmarks."""
        payload = {
            "district": "Yavatmal",
            "season": "Kharif",
            "temperature": 32.0,
            "rainfall": 850.0,
            "humidity": 65.0,
            "irrigation": True
        }
        response = client.post("/api/crop/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["recommendations"]) > 0

    def test_cotton_prediction_district_validation(self):
        """Cotton research model specifically validates against 6 historical Vidarbha panel districts."""
        valid_districts = ["Akola", "Amravati", "Buldhana", "Nagpur", "Wardha", "Washim"]
        for dist in valid_districts:
            payload = {
                "district": dist,
                "target_year": 2024,
                "model_version": "candidate_six_district_thermal"
            }
            res = client.post("/api/cotton/predict", json=payload)
            assert res.status_code == 200, f"Failed for valid district {dist}: {res.text}"
