import sqlite3
import os
import json
from datetime import datetime

DB_PATH = "backend/database/agripredict.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            district TEXT NOT NULL,
            season TEXT NOT NULL,
            recommended_crop TEXT NOT NULL,
            tomato_suitability REAL,
            onion_suitability REAL,
            sugarcane_suitability REAL,
            predicted_yield REAL,
            input_parameters TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_prediction(district: str, season: str, recommended_crop: str, tomato_suitability: float, onion_suitability: float, sugarcane_suitability: float, predicted_yield: float, inputs: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO prediction_history (timestamp, district, season, recommended_crop, tomato_suitability, onion_suitability, sugarcane_suitability, predicted_yield, input_parameters)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (now_str, district, season, recommended_crop, tomato_suitability, onion_suitability, sugarcane_suitability, predicted_yield, json.dumps(inputs)))
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_history(limit=50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prediction_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        item = dict(r)
        try:
            item["input_parameters"] = json.loads(item["input_parameters"])
        except Exception:
            item["input_parameters"] = {}
        result.append(item)
    return result

init_db()
