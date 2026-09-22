import sys
import pandas as pd
import joblib
from backend.ml.predictor import RealPredictor

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def test_model_is_real_not_dummy():
    """
    CRITICAL TEST: Verify model actually learned real patterns, not hardcoded/dummy
    """
    predictor = RealPredictor()
    assert predictor.is_loaded, "[FAIL] Model files not loaded correctly!"

    # TEST 1: Predictions change based on input
    print("TEST 1: Predictions should change when input changes...")
    
    input1 = {
        'district': 'Pune',
        'season': 'Kharif',
        'temp_min': 15, 'temp_max': 32,
        'rainfall': 150, 'humidity': 65,
        'wind_speed': 10,
        'soil_nitrogen': 40, 'soil_phosphorus': 25,
        'soil_potassium': 200, 'soil_ph': 6.8, 'soil_moisture': 60
    }
    
    result1 = predictor.recommend_crop(input1)
    
    input2 = input1.copy()
    input2['rainfall'] = 300  # Much higher rainfall
    result2 = predictor.recommend_crop(input2)
    
    # Predictions MUST change (not dummy)
    assert result1 != result2, "[FAIL] DUMMY: Predictions don't change with input!"
    print(f"[OK] Input 1 (rainfall=150): {result1}")
    print(f"[OK] Input 2 (rainfall=300): {result2}")
    print("[OK] TEST 1 PASSED: Predictions change based on input (NOT DUMMY)")

    # TEST 2: Sugarcane suitability should increase with higher rainfall
    print("\nTEST 2: Sugarcane should prefer high rainfall...")
    
    sugarcane_low = input1.copy()
    sugarcane_low['rainfall'] = 100
    sugarcane_high = input1.copy()
    sugarcane_high['rainfall'] = 250
    sugarcane_high['soil_potassium'] = 350

    sugarcane_low_rain = predictor.recommend_crop(sugarcane_low)['Sugarcane']
    sugarcane_high_rain = predictor.recommend_crop(sugarcane_high)['Sugarcane']
    
    assert sugarcane_high_rain > sugarcane_low_rain, "[FAIL] DUMMY: Sugarcane suitability doesn't increase with high rainfall & potassium!"
    print(f"[OK] Sugarcane @ rainfall=100: {sugarcane_low_rain:.1f}%")
    print(f"[OK] Sugarcane @ rainfall=250: {sugarcane_high_rain:.1f}%")
    print("[OK] TEST 2 PASSED: Model learned real agricultural patterns (NOT DUMMY)")

    # TEST 3: Yield prediction makes sense
    print("\nTEST 3: Yield prediction should follow learned patterns...")
    
    input_normal = {
        'district': 'Kolhapur', 'season': 'Kharif', 'crop': 'Sugarcane',
        'temp_min': 18, 'temp_max': 28, 'rainfall': 100, 'humidity': 60, 'wind_speed': 10,
        'soil_nitrogen': 50, 'soil_phosphorus': 25, 'soil_potassium': 150, 'soil_ph': 6.5, 'soil_moisture': 50
    }
    input_optimal = input_normal.copy()
    input_optimal['rainfall'] = 280
    input_optimal['soil_potassium'] = 380

    yield1 = predictor.predict_yield(input_normal)['predicted_yield']
    yield2 = predictor.predict_yield(input_optimal)['predicted_yield']
    
    assert yield2 > yield1, "[FAIL] DUMMY: Yield doesn't increase with optimal sugarcane conditions!"
    print(f"[OK] Yield @ normal conditions: {yield1} tonnes/ha")
    print(f"[OK] Yield @ optimal conditions: {yield2} tonnes/ha")
    print("[OK] TEST 3 PASSED: Yield model learned real patterns (NOT DUMMY)")

    print("\n" + "="*60)
    print("[OK] ALL TESTS PASSED: MODEL IS REAL, NOT DUMMY")
    print("="*60)

if __name__ == "__main__":
    test_model_is_real_not_dummy()
