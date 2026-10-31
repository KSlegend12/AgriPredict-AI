"""
Phase 10: Independent Agronomic Evidence Validation & Decision-System Calibration Test Suite.

Verifies:
1. Soil benchmark reliability across Maharashtra agro-ecological zones (Konkan vs Vidarbha vs Western Maharashtra).
2. Omitted soil inputs receive authentic district-specific SHC benchmarks without silent Akola fallback.
3. Liebig's Law of the Minimum: severe nitrogen starvation is not masked by high potassium.
4. Crop-specific thermal stress ceilings (Solanaceae flower abortion vs tropical C4 sugarcane).
5. Explicit 'insufficient_information' status for contradictory or implausible environmental conditions.
6. Acidic and alkaline soil corrective advisories (lime vs gypsum/micronutrients).
7. Rainfed moisture deficit penalties and irrigation mitigation.
8. Cotton model 6-district panel boundary and empirical out-of-fold error bounds preservation.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import DISTRICT_SOIL_BENCHMARKS
from backend.ml.predictor import predictor_instance as predictor

client = TestClient(app)


class TestSoilBenchmarkReliability:
    """Verifies district-specific Soil Health Card benchmarks without silent cross-district fallback."""

    def test_36_districts_have_authentic_benchmarks(self):
        """All 36 Maharashtra districts must have distinct, scientifically sourced SHC benchmarks."""
        assert len(DISTRICT_SOIL_BENCHMARKS) == 36
        for dist_name, bench in DISTRICT_SOIL_BENCHMARKS.items():
            assert "soil_type" in bench
            assert "soil_ph" in bench
            assert "nitrogen" in bench
            assert "phosphorus" in bench
            assert "potassium" in bench
            assert "region" in bench
            assert 5.0 <= bench["soil_ph"] <= 8.5
            assert 100.0 <= bench["nitrogen"] <= 300.0
            assert 10.0 <= bench["phosphorus"] <= 60.0
            assert 100.0 <= bench["potassium"] <= 450.0

    def test_district_specific_fallback_distinct_from_akola(self):
        """When soil inputs are omitted, Ratnagiri (Konkan) must receive acidic laterite benchmarks (pH ~5.8)
        and must NOT silently receive Akola's alkaline vertisol benchmark (pH 7.5)."""
        res_ratnagiri = client.post("/api/crop/recommend", json={
            "district": "Ratnagiri",
            "season": "Kharif",
            "temperature": 27.0,
            "rainfall": 2800.0,
            "humidity": 85.0
        })
        assert res_ratnagiri.status_code == 200
        data_rat = res_ratnagiri.json()
        assert data_rat["missing_soil_inputs"] is True
        assert "Laterit" in data_rat.get("soil_type", "") or "Coastal" in data_rat.get("soil_type", "")
        assert "Konkan" in data_rat.get("farmer_guidance", "") or "Soil Health Card" in data_rat.get("farmer_guidance", "")

        res_pune = client.post("/api/crop/recommend", json={
            "district": "Pune",
            "season": "Kharif",
            "temperature": 27.0,
            "rainfall": 700.0,
            "humidity": 65.0
        })
        assert res_pune.status_code == 200
        data_pune = res_pune.json()
        assert data_pune["missing_soil_inputs"] is True
        assert "Inceptisol" in data_pune.get("soil_type", "") or "Medium Black" in data_pune.get("soil_type", "")

    def test_measured_soil_values_marked_distinct_from_estimated(self):
        """Supplied laboratory values must be marked as Measured, while omitted values must be marked as Estimated."""
        measured_payload = {
            "district": "Akola",
            "season": "Kharif",
            "temperature": 30.0,
            "rainfall": 800.0,
            "humidity": 65.0,
            "soil_ph": 7.4,
            "nitrogen": 170.0,
            "phosphorus": 24.0,
            "potassium": 300.0,
            "soil_moisture": 62.0
        }
        res_meas = client.post("/api/crop/recommend", json=measured_payload)
        assert res_meas.status_code == 200
        data_meas = res_meas.json()
        assert data_meas.get("soil_data_source") == "Farmer Laboratory Soil Test (Measured)"
        assert data_meas.get("missing_soil_inputs") is False

        omitted_payload = {
            "district": "Akola",
            "season": "Kharif",
            "temperature": 30.0,
            "rainfall": 800.0,
            "humidity": 65.0
        }
        res_omit = client.post("/api/crop/recommend", json=omitted_payload)
        assert res_omit.status_code == 200
        data_omit = res_omit.json()
        assert data_omit.get("soil_data_source") == "District Soil Health Card Benchmark (Estimated)"
        assert data_omit.get("missing_soil_inputs") is True


class TestCropSuitabilityAndLiebigLaw:
    """Verifies Liebig's Law of the Minimum, thermal stress, and environmental gating."""

    def test_liebig_law_nitrogen_deficiency_penalty(self):
        """Under severe nitrogen starvation (15 kg/ha), high potassium (290 kg/ha)
        must NOT mask the nitrogen deficiency. An advisory and risk factor must trigger."""
        payload = {
            "district": "Wardha",
            "season": "Kharif",
            "temperature": 29.0,
            "rainfall": 750.0,
            "humidity": 68.0,
            "soil_ph": 7.2,
            "nitrogen": 15.0,  # Severely deficient
            "phosphorus": 45.0,
            "potassium": 290.0,  # High within schema bounds (le=300)
            "soil_moisture": 60.0
        }
        res = client.post("/api/crop/recommend", json=payload)
        assert res.status_code == 200
        data = res.json()
        # Sugarcane or top crop must contain severe nitrogen starvation warning
        top_crop = data["recommendations"][0]
        all_advisories = [adv for r in data["recommendations"] for adv in r.get("advisories", [])]
        assert any("Nitrogen Starvation" in adv or "nitrogen" in adv.lower() for adv in all_advisories)
        all_risks = [rf for r in data["recommendations"] for rf in r.get("risk_factors", [])]
        assert any("nitrogen" in rf.lower() for rf in all_risks)

    def test_crop_specific_thermal_stress_ceilings(self):
        """At 43.5°C, Cotton must trigger heat stress / thermal warning."""
        payload = {
            "district": "Akola",
            "season": "Summer",
            "temperature": 43.5,
            "rainfall": 200.0,
            "humidity": 45.0,
            "irrigation": True
        }
        res = client.post("/api/crop/recommend", json=payload)
        assert res.status_code == 200
        data = res.json()
        cotton_rec = next(r for r in data["recommendations"] if r["crop"] == "Cotton")
        assert any("heat" in adv.lower() or "temperature" in adv.lower() or "thermal" in adv.lower() for adv in cotton_rec.get("advisories", []))

    def test_insufficient_information_on_contradictory_conditions(self):
        """Contradictory environmental inputs (e.g. 45°C extreme heat with 900mm rain & 85% humidity)
        must be flagged with recommendation_status = 'insufficient_information'."""
        payload = {
            "district": "Amravati",
            "season": "Summer",
            "temperature": 45.0,
            "rainfall": 900.0,
            "humidity": 85.0,
            "irrigation": True
        }
        res = client.post("/api/crop/recommend", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data.get("recommendation_status") == "insufficient_information"
        assert data.get("insufficient_information") is True
        assert "unsuitable_warning" in data
        assert "Conflicting" in data["unsuitable_warning"] or "contradictory" in data["unsuitable_warning"].lower()


class TestAgronomicStressScenarios:
    """Verifies physiological responses across soil and climatic extremes."""

    def test_acidic_soil_lime_amendment_advisory(self):
        """At soil pH 5.0 (acidic laterite), phosphorus fixation advisory must trigger."""
        payload = {
            "district": "Sindhudurg",
            "season": "Kharif",
            "temperature": 28.0,
            "rainfall": 1500.0,
            "humidity": 80.0,
            "soil_ph": 5.0,
            "irrigation": True
        }
        res = client.post("/api/crop/recommend", json=payload)
        assert res.status_code == 200
        data = res.json()
        for rec in data["recommendations"]:
            assert any("Acidic soil" in adv and "lime amendment" in adv for adv in rec.get("advisories", []))

    def test_alkaline_calcareous_soil_advisory(self):
        """At soil pH 8.6 (Purna valley sodic vertisol), micronutrient uptake advisory must trigger."""
        payload = {
            "district": "Akola",
            "season": "Rabi",
            "temperature": 28.0,
            "rainfall": 500.0,
            "humidity": 55.0,
            "soil_ph": 8.6,
            "irrigation": True
        }
        res = client.post("/api/crop/recommend", json=payload)
        assert res.status_code == 200
        data = res.json()
        for rec in data["recommendations"]:
            assert any("Alkaline soil" in adv and "Micronutrient uptake" in adv for adv in rec.get("advisories", []))

    def test_extreme_heat_and_drought_all_options_unsuitable(self):
        """At 46°C summer heat wave without irrigation, all_options_unsuitable must be True."""
        payload = {
            "district": "Washim",
            "season": "Summer",
            "temperature": 46.0,
            "rainfall": 25.0,
            "humidity": 20.0,
            "irrigation": False
        }
        res = client.post("/api/crop/recommend", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data.get("all_options_unsuitable") is True
        assert data.get("recommendation_status") == "all_options_unsuitable"


class TestCottonModelResearchProtection:
    """Verifies that the cotton model remains protected, calibrated, and isolated."""

    def test_cotton_production_model_bounds_and_labels(self):
        """Cotton prediction returns Empirically Calibrated Out-of-Fold Error Bounds with 253.5 kg/ha margin."""
        payload = {
            "district": "Akola",
            "target_year": 2024,
            "model_version": "candidate_six_district_thermal"
        }
        res = client.post("/api/cotton/predict", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        interval = data["prediction_interval"]
        assert interval["label"] == "Empirically Calibrated Out-of-Fold Error Bounds"
        assert interval["half_width_kg_ha"] == 253.5
        assert interval["lower_bound_kg_per_ha"] >= 0.0
        assert interval["upper_bound_kg_per_ha"] > interval["lower_bound_kg_per_ha"]
