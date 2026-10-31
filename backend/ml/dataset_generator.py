"""
SYNTHETIC BENCHMARK DATASET GENERATOR
=====================================
PROVENANCE CLASSIFICATION: synthetic_benchmark

CRITICAL NOTICE (Phase 12/13 Integrity Audit):
This script generates SYNTHETIC benchmark observations using hand-crafted Gaussian centroids
and parameterized equations for Tomato, Onion, and Sugarcane.

STRICT RESEARCH BOUNDARY:
- Outputs of this generator MUST NOT be cited or described as government survey data,
  official university records, or authentic farmer field observations.
- Accuracy metrics computed on datasets produced by this script represent synthetic cluster
  separability, NOT real-world agricultural generalization.
- Preserved strictly for pipeline architecture testing and backward reproducibility.
"""

import os
import sys
import numpy as np
import pandas as pd
from backend.config import MAHARASHTRA_DISTRICTS

# Force UTF-8 output encoding if possible
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def generate_real_maharashtra_dataset(num_samples=3000, seed=42):
    """
    Generate synthetic benchmark dataset for multi-crop classification testing.
    NOTE: Despite the legacy function name, this generates SYNTHETIC Gaussian data.
    """
    np.random.seed(seed)
    districts = list(MAHARASHTRA_DISTRICTS.keys())
    crops = ["Tomato", "Onion", "Sugarcane"]

    data = []

    for i in range(num_samples):
        crop = np.random.choice(crops)
        district = np.random.choice(districts)

        if crop == "Tomato":
            season = np.random.choice(["Rabi", "Kharif", "Summer"], p=[0.6, 0.3, 0.1])
            temp_min = float(np.clip(np.random.normal(16, 3), 5, 25))
            temp_max = float(np.clip(np.random.normal(27, 3), 22, 42))
            
            is_optimal = (district in ["Pune", "Nashik", "Satara", "Ahmednagar"]) and (20 <= temp_max <= 30)
            rainfall = float(np.clip(np.random.normal(190 if is_optimal else 120, 40), 20, 300))
            humidity = float(np.clip(np.random.normal(65, 8), 30, 95))
            wind_speed = float(np.clip(np.random.normal(10, 3), 2, 20))

            soil_nitrogen = float(np.clip(np.random.normal(60 if is_optimal else 40, 10), 10, 100))
            soil_phosphorus = float(np.clip(np.random.normal(30, 8), 5, 50))
            soil_potassium = float(np.clip(np.random.normal(200 if is_optimal else 140, 30), 100, 500))
            soil_ph = float(np.clip(np.random.normal(6.4, 0.3), 5.5, 8.5))
            soil_moisture = float(np.clip(np.random.normal(55, 10), 20, 80))

            base_yield = 40.0
            temp_factor = 1.2 if 20 <= temp_max <= 30 else 0.7
            rain_factor = 1.25 if 150 <= rainfall <= 250 else 0.75
            soil_factor = 1.15 if (50 <= soil_nitrogen <= 75 and 150 <= soil_potassium <= 250) else 0.85
            
            yield_val = base_yield * temp_factor * rain_factor * soil_factor * np.random.normal(1.0, 0.05)
            yield_val = float(np.clip(yield_val, 25.0, 55.0))

        elif crop == "Onion":
            season = np.random.choice(["Kharif", "Rabi", "Summer"], p=[0.55, 0.35, 0.10])
            temp_min = float(np.clip(np.random.normal(14, 3), 5, 23))
            temp_max = float(np.clip(np.random.normal(24, 3), 20, 40))

            is_optimal = (district in ["Nashik", "Ahmednagar", "Dhule", "Jalgaon"])
            rainfall = float(np.clip(np.random.normal(140 if is_optimal else 90, 35), 10, 280))
            humidity = float(np.clip(np.random.normal(60, 8), 30, 90))
            wind_speed = float(np.clip(np.random.normal(11, 3), 2, 20))

            soil_nitrogen = float(np.clip(np.random.normal(50, 10), 10, 100))
            soil_phosphorus = float(np.clip(np.random.normal(25, 8), 5, 50))
            soil_potassium = float(np.clip(np.random.normal(240, 40), 100, 500))
            soil_ph = float(np.clip(np.random.normal(7.0, 0.3), 5.5, 8.5))
            soil_moisture = float(np.clip(np.random.normal(50, 10), 20, 80))

            base_yield = 27.0
            k_factor = 1.3 if soil_potassium > 200 else 0.75
            humidity_factor = 1.2 if humidity < 70 else 0.8
            temp_factor = 1.15 if 15 <= temp_max <= 28 else 0.85

            yield_val = base_yield * k_factor * humidity_factor * temp_factor * np.random.normal(1.0, 0.05)
            yield_val = float(np.clip(yield_val, 15.0, 40.0))

        else: # Sugarcane
            season = np.random.choice(["Kharif", "Rabi"], p=[0.6, 0.4])
            temp_min = float(np.clip(np.random.normal(18, 3), 10, 25))
            temp_max = float(np.clip(np.random.normal(29, 3), 22, 44))

            is_optimal = (district in ["Kolhapur", "Pune", "Satara", "Sangli", "Solapur"])
            rainfall = float(np.clip(np.random.normal(230 if is_optimal else 160, 40), 50, 300))
            humidity = float(np.clip(np.random.normal(75, 8), 35, 95))
            wind_speed = float(np.clip(np.random.normal(12, 3), 2, 20))

            soil_nitrogen = float(np.clip(np.random.normal(80, 12), 10, 100))
            soil_phosphorus = float(np.clip(np.random.normal(35, 8), 5, 50))
            soil_potassium = float(np.clip(np.random.normal(320, 50), 100, 500))
            soil_ph = float(np.clip(np.random.normal(7.2, 0.25), 5.5, 8.5))
            soil_moisture = float(np.clip(np.random.normal(70, 8), 20, 80))

            base_yield = 75.0
            rain_factor = 1.35 if rainfall > 200 else 0.7
            k_factor = 1.3 if soil_potassium > 300 else 0.75
            temp_factor = 1.15 if 20 <= temp_max <= 32 else 0.85

            yield_val = base_yield * rain_factor * k_factor * temp_factor * np.random.normal(1.0, 0.05)
            yield_val = float(np.clip(yield_val, 45.0, 98.0))

        data.append({
            "district": district,
            "season": season,
            "crop": crop,
            "temp_min": round(temp_min, 1),
            "temp_max": round(temp_max, 1),
            "rainfall": round(rainfall, 1),
            "humidity": round(humidity, 1),
            "wind_speed": round(wind_speed, 1),
            "soil_nitrogen": round(soil_nitrogen, 1),
            "soil_phosphorus": round(soil_phosphorus, 1),
            "soil_potassium": round(soil_potassium, 1),
            "soil_ph": round(soil_ph, 2),
            "soil_moisture": round(soil_moisture, 1),
            "yield_tonnes_per_hectare": round(yield_val, 2)
        })

    df = pd.DataFrame(data)
    
    os.makedirs("backend/data", exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("backend/data/maharashtra_agri.csv", index=False)
    df.to_csv("data/raw/maharashtra_agri.csv", index=False)
    
    print(f"[OK] Generated {len(df)} records saved to backend/data/maharashtra_agri.csv")
    verify_dataset(df)
    return df

def verify_dataset(df):
    tomato_mean = df[df['crop']=='Tomato']['yield_tonnes_per_hectare'].mean()
    sugarcane_mean = df[df['crop']=='Sugarcane']['yield_tonnes_per_hectare'].mean()
    
    print(f"Tomato Mean Yield: {tomato_mean:.2f} tonnes/ha")
    print(f"Sugarcane Mean Yield: {sugarcane_mean:.2f} tonnes/ha")
    
    assert tomato_mean > 35, "Tomato mean yield should be > 35 tonnes/ha"
    assert sugarcane_mean > 60, "Sugarcane mean yield should be > 60 tonnes/ha"
    print("[OK] Check 1 PASSED: Data has realistic crop yields")

    corr = df[['rainfall', 'yield_tonnes_per_hectare']].corr()
    rain_corr = abs(corr.iloc[0,1])
    print(f"Rainfall-Yield Correlation: {rain_corr:.3f}")
    assert rain_corr > 0.3, "Rainfall and yield should correlate (> 0.3)"
    print("[OK] Check 2 PASSED: Data has realistic rainfall-yield correlations")

    temp_yield_corr = abs(df[['temp_max', 'yield_tonnes_per_hectare']].corr().iloc[0,1])
    print(f"TempMax-Yield Correlation: {temp_yield_corr:.3f}")
    assert temp_yield_corr > 0.2, "Temperature and yield should correlate (> 0.2)"
    print("[OK] Check 3 PASSED: Temperature affects yield realistically")

if __name__ == "__main__":
    generate_real_maharashtra_dataset()
