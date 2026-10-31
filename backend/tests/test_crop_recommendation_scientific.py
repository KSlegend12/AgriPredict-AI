"""
Scientific validation tests for the crop recommendation engine under
extreme environmental stress, boundary regimes, and agronomic constraint checks.
"""

import pytest
from backend.ml.predictor import predictor_instance as predictor, ALLOWED_CROPS, CROP_AGRONOMY


class TestCropRecommendationScientific:
    """Scientific stress testing for crop recommendation and suitability rules."""

    def test_low_rainfall_drought_stress(self):
        """Under severe drought (<200mm rainfall, no irrigation), rainfed crops
        must receive steep water penalties, and rainfed cotton must be penalized."""
        input_data = {
            "district": "Amravati",
            "season": "Kharif",
            "rainfall": 150.0,
            "is_seasonal": True,
            "temp_max": 32.0,
            "temp_min": 24.0,
            "irrigation": False,
            "soil_ph": 7.5,
            "soil_nitrogen": 50.0,
            "soil_phosphorus": 20.0,
            "soil_potassium": 150.0,
            "humidity": 45.0,
        }
        res = predictor.predict_suitability(input_data)
        assert res["status"] == "success"
        
        # Cotton should receive severe deficit penalty and warning
        cotton_rec = next(r for r in res["recommendations"] if r["crop"] == "Cotton")
        assert cotton_rec["factor_scores"]["rainfall"] < 60
        assert any("rainfall" in adv.lower() or "drought" in adv.lower() or "moisture" in adv.lower() for adv in cotton_rec["advisories"])

    def test_excessive_rainfall_flood_stress(self):
        """Under excessive rainfall (>2500mm), cotton
        must receive excess water penalties."""
        input_data = {
            "district": "Pune",
            "season": "Kharif",
            "rainfall": 2800.0,
            "temp_max": 28.0,
            "temp_min": 20.0,
            "irrigation": True,
            "soil_ph": 6.8,
            "soil_nitrogen": 70.0,
            "soil_phosphorus": 30.0,
            "soil_potassium": 220.0,
            "humidity": 90.0,
        }
        res = predictor.predict_suitability(input_data)
        assert res["status"] == "success"
        
        cotton_rec = next(r for r in res["recommendations"] if r["crop"] == "Cotton")
        # Rainfall score should be penalised due to excess
        assert cotton_rec["factor_scores"]["rainfall"] < 80

    def test_extreme_heat_wave_stress(self):
        """Under heat wave conditions (temp_max = 47°C), temperature scores must
        drop substantially across all crops whose optimal max is 30-35°C."""
        input_data = {
            "district": "Nagpur",
            "season": "Summer",
            "rainfall": 50.0,
            "temp_max": 47.0,
            "temp_min": 32.0,
            "irrigation": True,
            "soil_ph": 7.0,
            "humidity": 30.0,
        }
        res = predictor.predict_suitability(input_data)
        assert res["status"] == "success"
        
        for crop_rec in res["recommendations"]:
            # All crops optimal max <= 35°C, at 47°C temperature score should be low
            assert crop_rec["factor_scores"]["temperature"] <= 40
            assert "sub-optimal temperature" in crop_rec["why_recommendation"]

    def test_acidic_soil_stress(self):
        """Under strongly acidic soil (pH = 4.2), lime amendment advisory must trigger."""
        input_data = {
            "district": "Nagpur",
            "season": "Kharif",
            "rainfall": 800.0,
            "temp_max": 28.0,
            "temp_min": 22.0,
            "irrigation": True,
            "soil_ph": 4.2,
            "humidity": 65.0,
        }
        res = predictor.predict_suitability(input_data)
        assert res["status"] == "success"
        
        for crop_rec in res["recommendations"]:
            assert crop_rec["factor_scores"]["soil"] < 70
            assert any("Acidic soil" in adv and "lime amendment" in adv for adv in crop_rec["advisories"])

    def test_alkaline_soil_stress(self):
        """Under strongly alkaline soil (pH = 8.8), gypsum/micronutrient advisory must trigger."""
        input_data = {
            "district": "Akola",
            "season": "Kharif",
            "rainfall": 800.0,
            "temp_max": 28.0,
            "temp_min": 22.0,
            "irrigation": True,
            "soil_ph": 8.8,
            "humidity": 65.0,
        }
        res = predictor.predict_suitability(input_data)
        assert res["status"] == "success"
        
        for crop_rec in res["recommendations"]:
            assert crop_rec["factor_scores"]["soil"] < 75
            assert any("Alkaline soil" in adv and "Micronutrient uptake" in adv for adv in crop_rec["advisories"])

    def test_irrigation_mitigation_effect(self):
        """With moderate rainfall deficit (400mm), irrigation must provide higher
        rainfall score than rainfed conditions."""
        rainfed_input = {
            "district": "Wardha",
            "season": "Kharif",
            "rainfall": 400.0,
            "temp_max": 28.0,
            "temp_min": 21.0,
            "irrigation": False,
            "soil_ph": 6.8,
            "humidity": 60.0,
        }
        irrigated_input = dict(rainfed_input, irrigation=True)
        
        res_rainfed = predictor.predict_suitability(rainfed_input)
        res_irrigated = predictor.predict_suitability(irrigated_input)
        
        cotton_rainfed = next(r for r in res_rainfed["recommendations"] if r["crop"] == "Cotton")
        cotton_irrigated = next(r for r in res_irrigated["recommendations"] if r["crop"] == "Cotton")
        
        # Irrigation must substantially mitigate rainfall deficit
        assert cotton_irrigated["factor_scores"]["rainfall"] >= cotton_rainfed["factor_scores"]["rainfall"]
        assert cotton_irrigated["suitability_percentage"] >= cotton_rainfed["suitability_percentage"]

    def test_recommendation_ranking_order(self):
        """Suitability rankings must be monotonically ordered by suitability percentage."""
        input_data = {
            "district": "Pune",
            "season": "Kharif",
            "rainfall": 650.0,
            "temp_max": 27.0,
            "temp_min": 19.0,
            "irrigation": True,
            "soil_ph": 6.5,
            "humidity": 70.0,
        }
        res = predictor.predict_suitability(input_data)
        scores = [r["suitability_percentage"] for r in res["recommendations"]]
        assert scores == sorted(scores, reverse=True)
        assert res["recommendations"][0]["rank"] == 1
        assert res["recommended_crop"] == res["recommendations"][0]["crop"]
