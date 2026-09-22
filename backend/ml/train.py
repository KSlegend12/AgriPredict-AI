import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, mean_squared_error, r2_score
from backend.ml.dataset_generator import generate_real_maharashtra_dataset

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def train_real_models():
    dataset_path = "backend/data/maharashtra_agri.csv"
    if not os.path.exists(dataset_path):
        data = generate_real_maharashtra_dataset()
    else:
        data = pd.read_csv(dataset_path)

    os.makedirs("backend/models", exist_ok=True)

    # 1. PREPARE CLASSIFIER DATA
    features = ['district_encoded', 'season_encoded', 'temp_min', 'temp_max', 
                'rainfall', 'humidity', 'wind_speed', 'soil_nitrogen', 
                'soil_phosphorus', 'soil_potassium', 'soil_ph', 'soil_moisture']

    le_district = LabelEncoder()
    le_season = LabelEncoder()
    le_crop = LabelEncoder()

    data_cls = data.copy()
    data_cls['district_encoded'] = le_district.fit_transform(data['district'])
    data_cls['season_encoded'] = le_season.fit_transform(data['season'])
    y_encoded = le_crop.fit_transform(data['crop'])

    X_cls = data_cls[features]

    X_train, X_test, y_train, y_test = train_test_split(
        X_cls, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    # 2. TRAIN CLASSIFIER MODEL
    cls_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        random_state=42
    )
    cls_model.fit(X_train, y_train)

    y_pred = cls_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')

    print(f"[OK] CROP CLASSIFIER MODEL TRAINED - NOT DUMMY")
    print(f"Accuracy: {accuracy:.4f} (target: > 0.80)")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")

    assert accuracy > 0.80, "Classifier accuracy must be > 0.80"
    assert precision > 0.75, "Classifier precision must be > 0.75"
    assert recall > 0.75, "Classifier recall must be > 0.75"
    assert f1 > 0.75, "Classifier F1-score must be > 0.75"
    print("[OK] Crop Suitability Model criteria PASSED!")

    # 3. PREPARE YIELD REGRESSOR DATA
    data_reg = data.copy()
    data_reg['district_encoded'] = le_district.transform(data['district'])
    data_reg['season_encoded'] = le_season.transform(data['season'])
    data_reg['crop_encoded'] = le_crop.transform(data['crop'])

    yield_features = ['district_encoded', 'season_encoded', 'crop_encoded', 'temp_min', 'temp_max', 
                      'rainfall', 'humidity', 'wind_speed', 'soil_nitrogen', 
                      'soil_phosphorus', 'soil_potassium', 'soil_ph', 'soil_moisture']

    X_yield = data_reg[yield_features]
    y_yield = data['yield_tonnes_per_hectare']

    X_train_y, X_test_y, y_train_y, y_test_y = train_test_split(
        X_yield, y_yield, test_size=0.2, random_state=42
    )

    regressor = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        random_state=42
    )
    regressor.fit(X_train_y, y_train_y)

    y_pred_y = regressor.predict(X_test_y)
    mae = mean_absolute_error(y_test_y, y_pred_y)
    rmse = np.sqrt(mean_squared_error(y_test_y, y_pred_y))
    r2 = r2_score(y_test_y, y_pred_y)

    print(f"[OK] YIELD REGRESSOR MODEL TRAINED - NOT DUMMY")
    print(f"R2 Score: {r2:.4f} (target: > 0.85)")
    print(f"MAE: {mae:.2f} tonnes/ha (target: < 5.0)")
    print(f"RMSE: {rmse:.2f} tonnes/ha (target: < 7.0)")

    assert r2 > 0.85, "Regressor R2 score must be > 0.85"
    assert mae < 5.0, "Regressor MAE must be < 5.0 tonnes/ha"
    assert rmse < 7.0, "Regressor RMSE must be < 7.0 tonnes/ha"
    print("[OK] Yield Prediction Model criteria PASSED!")

    # 4. SAVE MODELS & ENCODERS
    joblib.dump(cls_model, 'backend/models/suitability_model.pkl')
    joblib.dump(regressor, 'backend/models/yield_model.pkl')
    joblib.dump(le_district, 'backend/models/le_district.pkl')
    joblib.dump(le_season, 'backend/models/le_season.pkl')
    joblib.dump(le_crop, 'backend/models/le_crop.pkl')

    # Also save top-level for direct imports
    joblib.dump(cls_model, 'backend/models/crop_suitability_model.joblib')
    joblib.dump(regressor, 'backend/models/yield_prediction_model.joblib')

    print("[OK] All trained models and encoders saved successfully to backend/models/")
    return {
        "accuracy": accuracy,
        "r2_score": r2,
        "mae": mae,
        "rmse": rmse
    }

if __name__ == "__main__":
    train_real_models()
