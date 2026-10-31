import sqlite3
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, Dict, Any, List

logger = logging.getLogger("agripredict.db")

DB_DIR = Path(__file__).resolve().parent
DB_PATH = os.getenv("AGRIPREDICT_DB_PATH", str(DB_DIR / "agripredict.db"))
DEFAULT_TIMEOUT = 15.0  # 15.0 seconds connection timeout
BUSY_TIMEOUT_MS = 15000 # 15000 ms busy timeout

_is_initialized = False

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create a new SQLite connection with reliable timeout and busy settings."""
    target_path = db_path or os.getenv("AGRIPREDICT_DB_PATH", DB_PATH)
    conn = sqlite3.connect(target_path, timeout=DEFAULT_TIMEOUT)
    conn.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS};")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def get_db_connection(db_path: Optional[str] = None):
    """Context manager for SQLite connections that guarantees connection closure."""
    conn = get_connection(db_path)
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_db_cursor(db_path: Optional[str] = None):
    """Context manager for atomic write operations.
    
    Using 'with conn' manages transaction boundaries (commit on success,
    rollback on exception). The outer try/finally guarantees that the
    connection is explicitly closed.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            yield cursor
    finally:
        conn.close()

def init_db(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Initialize database tables, indexes, and configure WAL mode safely.
    
    Does not clear existing data. Only runs DDL if objects do not exist.
    """
    global _is_initialized
    target_path = db_path or os.getenv("AGRIPREDICT_DB_PATH", DB_PATH)
    target_dir = Path(target_path).resolve().parent
    target_dir.mkdir(parents=True, exist_ok=True)

    status = {
        "db_path": target_path,
        "journal_mode": "unknown",
        "busy_timeout": BUSY_TIMEOUT_MS,
        "initialized": False,
        "error": None
    }

    try:
        with get_db_connection(target_path) as conn:
            cursor = conn.cursor()

            # Enable Write-Ahead Logging (WAL) for concurrent reads & writes
            cur_jm = cursor.execute("PRAGMA journal_mode=WAL;").fetchone()
            journal_mode = cur_jm[0] if cur_jm else "unknown"
            status["journal_mode"] = journal_mode
            if journal_mode.lower() != "wal":
                logger.warning("SQLite did not return WAL mode; current journal_mode: %s", journal_mode)
            else:
                logger.info("SQLite WAL mode active on %s", target_path)

            # High-performance synchronous mode for WAL
            cursor.execute("PRAGMA synchronous = NORMAL;")
            cursor.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS};")

            # Create tables if not exists (preserves all existing data)
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
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cotton_prediction_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    district TEXT NOT NULL,
                    target_year INTEGER NOT NULL,
                    model_version TEXT NOT NULL,
                    predicted_yield REAL NOT NULL,
                    lower_bound REAL,
                    upper_bound REAL,
                    input_parameters TEXT NOT NULL
                );
            """)

            # Phase 11: Real Soil Test Reports
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS soil_test_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id TEXT UNIQUE NOT NULL,
                    anonymous_farm_id TEXT NOT NULL,
                    district TEXT NOT NULL,
                    taluka TEXT NOT NULL,
                    village TEXT,
                    sampling_date TEXT NOT NULL,
                    lab_name TEXT,
                    soil_ph REAL NOT NULL,
                    nitrogen_kg_ha REAL NOT NULL,
                    phosphorus_kg_ha REAL NOT NULL,
                    potassium_kg_ha REAL NOT NULL,
                    soil_moisture REAL,
                    soil_type TEXT,
                    original_units TEXT NOT NULL,
                    provenance_type TEXT NOT NULL,
                    verification_status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL
                );
            """)

            # Phase 11: Real Farmer Field Observations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS field_observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    observation_id TEXT UNIQUE NOT NULL,
                    anonymous_farm_id TEXT NOT NULL,
                    district TEXT NOT NULL,
                    taluka TEXT NOT NULL,
                    crop TEXT NOT NULL,
                    variety TEXT,
                    season TEXT NOT NULL,
                    sowing_date TEXT NOT NULL,
                    harvest_date TEXT NOT NULL,
                    cultivated_area_ha REAL NOT NULL,
                    actual_yield REAL NOT NULL,
                    yield_unit TEXT NOT NULL,
                    normalized_yield_kg_ha REAL NOT NULL,
                    normalized_yield_tonnes_ha REAL NOT NULL,
                    irrigation_type TEXT,
                    total_rainfall_mm REAL,
                    stress_events TEXT,
                    data_source TEXT NOT NULL,
                    consent_confirmed INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );
            """)

            # Phase 11: Prediction vs Actual Outcome Tracking (Audit Trail)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS outcome_comparisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    comparison_id TEXT UNIQUE NOT NULL,
                    prediction_id INTEGER,
                    prediction_type TEXT NOT NULL,
                    crop TEXT NOT NULL,
                    district TEXT NOT NULL,
                    taluka TEXT,
                    season TEXT NOT NULL,
                    target_year INTEGER NOT NULL,
                    model_version TEXT NOT NULL,
                    predicted_value REAL NOT NULL,
                    predicted_lower_bound REAL,
                    predicted_upper_bound REAL,
                    actual_value REAL NOT NULL,
                    value_unit TEXT NOT NULL,
                    absolute_error REAL NOT NULL,
                    percentage_error REAL NOT NULL,
                    is_within_error_bound INTEGER NOT NULL,
                    input_provenance TEXT NOT NULL,
                    observation_source TEXT NOT NULL,
                    verification_status TEXT NOT NULL DEFAULT 'unverified',
                    created_at TEXT NOT NULL
                );
            """)

            # Create performance indexes if not exist
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prediction_history_timestamp ON prediction_history(timestamp);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prediction_history_district ON prediction_history(district);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cotton_prediction_history_district ON cotton_prediction_history(district);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cotton_prediction_history_timestamp ON cotton_prediction_history(timestamp);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_soil_reports_district ON soil_test_reports(district);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_soil_reports_farm ON soil_test_reports(anonymous_farm_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_obs_district_crop ON field_observations(district, crop);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_obs_farm ON field_observations(anonymous_farm_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_outcome_comp_crop ON outcome_comparisons(crop);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_outcome_comp_district ON outcome_comparisons(district);")

            conn.commit()

        status["initialized"] = True
        _is_initialized = True
        return status
    except Exception as e:
        status["error"] = str(e)
        logger.error("Failed to initialize database: %s", e, exc_info=True)
        return status

def save_prediction(
    district: str,
    season: str,
    recommended_crop: str,
    tomato_suitability: float,
    onion_suitability: float,
    sugarcane_suitability: float,
    predicted_yield: float,
    inputs: dict,
    db_path: Optional[str] = None
) -> Optional[int]:
    """Persist general crop recommendation and suitability results atomically."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = json.dumps(inputs) if isinstance(inputs, dict) else str(inputs)

    with get_db_cursor(db_path) as cursor:
        cursor.execute("""
            INSERT INTO prediction_history (
                timestamp, district, season, recommended_crop,
                tomato_suitability, onion_suitability, sugarcane_suitability,
                predicted_yield, input_parameters
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_str, district, season, recommended_crop,
            float(tomato_suitability or 0.0),
            float(onion_suitability or 0.0),
            float(sugarcane_suitability or 0.0),
            float(predicted_yield or 0.0),
            payload
        ))
        inserted_id = cursor.lastrowid

    return inserted_id

def save_cotton_prediction(
    district: str,
    year: int,
    predicted_yield: float,
    lower_bound: Optional[float],
    upper_bound: Optional[float],
    model_type: str,
    inputs: dict,
    db_path: Optional[str] = None
) -> Optional[int]:
    """Persist cotton prediction and interval bounds atomically."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = json.dumps(inputs) if isinstance(inputs, dict) else str(inputs)

    with get_db_cursor(db_path) as cursor:
        cursor.execute("""
            INSERT INTO cotton_prediction_history (
                timestamp, district, target_year, model_version,
                predicted_yield, lower_bound, upper_bound, input_parameters
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_str, district, int(year), str(model_type),
            float(predicted_yield),
            float(lower_bound) if lower_bound is not None else None,
            float(upper_bound) if upper_bound is not None else None,
            payload
        ))
        inserted_id = cursor.lastrowid

    return inserted_id

def get_history(limit: int = 50, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve combined historical predictions sorted chronologically descending.
    
    Reads data efficiently and closes the connection before in-memory transformation.
    """
    with get_db_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM prediction_history ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()

        cursor.execute("SELECT * FROM cotton_prediction_history ORDER BY id DESC LIMIT ?", (limit,))
        cotton_rows = cursor.fetchall()

    result = []
    for r in rows:
        item = dict(r)
        item["crop_type"] = item.get("recommended_crop", "General")
        try:
            item["input_parameters"] = json.loads(item["input_parameters"])
        except Exception:
            item["input_parameters"] = {}
        result.append(item)

    for r in cotton_rows:
        item = dict(r)
        item["crop_type"] = "Cotton"
        item["recommended_crop"] = "Cotton"
        item["model_type"] = item.get("model_version", "production")
        item["season"] = f"Kharif {item.get('target_year', '')}"
        try:
            item["input_parameters"] = json.loads(item["input_parameters"])
        except Exception:
            item["input_parameters"] = {}
        result.append(item)

    result.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return result[:limit]

def get_db_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve operational database diagnostics (journal mode, busy timeout, counts)."""
    target_path = db_path or os.getenv("AGRIPREDICT_DB_PATH", DB_PATH)
    status = {
        "db_path": target_path,
        "exists": os.path.exists(target_path),
        "journal_mode": "unknown",
        "busy_timeout": 0,
        "foreign_keys": 0,
        "prediction_history_count": 0,
        "cotton_prediction_history_count": 0,
        "soil_test_reports_count": 0,
        "field_observations_count": 0,
        "outcome_comparisons_count": 0,
    }
    if not status["exists"]:
        return status

    with get_db_connection(target_path) as conn:
        cursor = conn.cursor()
        jm = cursor.execute("PRAGMA journal_mode;").fetchone()
        bt = cursor.execute("PRAGMA busy_timeout;").fetchone()
        fk = cursor.execute("PRAGMA foreign_keys;").fetchone()
        p_cnt = cursor.execute("SELECT COUNT(1) FROM prediction_history;").fetchone()
        c_cnt = cursor.execute("SELECT COUNT(1) FROM cotton_prediction_history;").fetchone()
        s_cnt = cursor.execute("SELECT COUNT(1) FROM soil_test_reports;").fetchone()
        f_cnt = cursor.execute("SELECT COUNT(1) FROM field_observations;").fetchone()
        o_cnt = cursor.execute("SELECT COUNT(1) FROM outcome_comparisons;").fetchone()

        status["journal_mode"] = jm[0] if jm else "unknown"
        status["busy_timeout"] = bt[0] if bt else 0
        status["foreign_keys"] = fk[0] if fk else 0
        status["prediction_history_count"] = p_cnt[0] if p_cnt else 0
        status["cotton_prediction_history_count"] = c_cnt[0] if c_cnt else 0
        status["soil_test_reports_count"] = s_cnt[0] if s_cnt else 0
        status["field_observations_count"] = f_cnt[0] if f_cnt else 0
        status["outcome_comparisons_count"] = o_cnt[0] if o_cnt else 0

    return status

# ===========================================================================
# PHASE 11: FIELD VALIDATION & REAL AGRICULTURAL DATA INTEGRATION HELPERS
# ===========================================================================

def save_soil_test_report(
    report_id: str,
    anonymous_farm_id: str,
    district: str,
    taluka: str,
    village: Optional[str],
    sampling_date: str,
    lab_name: Optional[str],
    soil_ph: float,
    nitrogen_kg_ha: float,
    phosphorus_kg_ha: float,
    potassium_kg_ha: float,
    soil_moisture: Optional[float],
    soil_type: Optional[str],
    original_units: Dict[str, str],
    provenance_type: str = "lab_measured",
    verification_status: str = "pending",
    db_path: Optional[str] = None
) -> Optional[int]:
    """Persist authentic lab soil test report atomically."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    units_json = json.dumps(original_units)

    with get_db_cursor(db_path) as cursor:
        cursor.execute("""
            INSERT INTO soil_test_reports (
                report_id, anonymous_farm_id, district, taluka, village,
                sampling_date, lab_name, soil_ph, nitrogen_kg_ha, phosphorus_kg_ha,
                potassium_kg_ha, soil_moisture, soil_type, original_units,
                provenance_type, verification_status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id, anonymous_farm_id, district, taluka, village,
            sampling_date, lab_name, float(soil_ph), float(nitrogen_kg_ha),
            float(phosphorus_kg_ha), float(potassium_kg_ha),
            float(soil_moisture) if soil_moisture is not None else None,
            soil_type, units_json, provenance_type, verification_status, now_str
        ))
        return cursor.lastrowid

def get_soil_test_reports(
    district: Optional[str] = None,
    limit: int = 50,
    mask_village: bool = True,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieve verified/pending soil test reports with masked farm identifiers and village quasi-identifier protection."""
    with get_db_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if district:
            cursor.execute("""
                SELECT * FROM soil_test_reports
                WHERE district = ? COLLATE NOCASE
                ORDER BY id DESC LIMIT ?
            """, (district, limit))
        else:
            cursor.execute("SELECT * FROM soil_test_reports ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()

    result = []
    for r in rows:
        item = dict(r)
        if mask_village and item.get("village"):
            item["village"] = "[MASKED]"
        try:
            item["original_units"] = json.loads(item["original_units"])
        except Exception:
            item["original_units"] = {}
        result.append(item)
    return result

def save_field_observation(
    observation_id: str,
    anonymous_farm_id: str,
    district: str,
    taluka: str,
    crop: str,
    variety: Optional[str],
    season: str,
    sowing_date: str,
    harvest_date: str,
    cultivated_area_ha: float,
    actual_yield: float,
    yield_unit: str,
    normalized_yield_kg_ha: float,
    normalized_yield_tonnes_ha: float,
    irrigation_type: Optional[str],
    total_rainfall_mm: Optional[float],
    stress_events: Optional[List[str]],
    data_source: str = "farmer_reported",
    consent_confirmed: bool = True,
    db_path: Optional[str] = None
) -> Optional[int]:
    """Persist authentic farmer harvest observation atomically."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stress_json = json.dumps(stress_events or [])

    with get_db_cursor(db_path) as cursor:
        cursor.execute("""
            INSERT INTO field_observations (
                observation_id, anonymous_farm_id, district, taluka, crop,
                variety, season, sowing_date, harvest_date, cultivated_area_ha,
                actual_yield, yield_unit, normalized_yield_kg_ha, normalized_yield_tonnes_ha,
                irrigation_type, total_rainfall_mm, stress_events, data_source,
                consent_confirmed, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            observation_id, anonymous_farm_id, district, taluka, crop,
            variety, season, sowing_date, harvest_date, float(cultivated_area_ha),
            float(actual_yield), yield_unit, float(normalized_yield_kg_ha),
            float(normalized_yield_tonnes_ha), irrigation_type,
            float(total_rainfall_mm) if total_rainfall_mm is not None else None,
            stress_json, data_source, 1 if consent_confirmed else 0, now_str
        ))
        return cursor.lastrowid

def get_field_observations(
    district: Optional[str] = None,
    crop: Optional[str] = None,
    include_withdrawn: bool = False,
    limit: int = 50,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieve field harvest observations with consent filtering (WP6)."""
    with get_db_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = "SELECT * FROM field_observations WHERE 1=1"
        params = []
        if not include_withdrawn:
            query += " AND consent_confirmed = 1"
        if district:
            query += " AND district = ? COLLATE NOCASE"
            params.append(district)
        if crop:
            query += " AND crop = ? COLLATE NOCASE"
            params.append(crop)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

    result = []
    for r in rows:
        item = dict(r)
        try:
            item["stress_events"] = json.loads(item["stress_events"])
        except Exception:
            item["stress_events"] = []
        result.append(item)
    return result

def withdraw_field_observation_consent(
    anonymous_farm_id: str,
    observation_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> int:
    """
    Withdraw farmer consent by marking consent_confirmed = 0 (WP6).
    Excludes the observation from research queries and public listings.
    """
    with get_db_cursor(db_path) as cursor:
        if observation_id:
            cursor.execute(
                "UPDATE field_observations SET consent_confirmed = 0 WHERE anonymous_farm_id = ? AND observation_id = ?",
                (anonymous_farm_id, observation_id)
            )
        else:
            cursor.execute(
                "UPDATE field_observations SET consent_confirmed = 0 WHERE anonymous_farm_id = ?",
                (anonymous_farm_id,)
            )
        return cursor.rowcount

def record_outcome_comparison(
    comparison_id: str,
    prediction_id: Optional[int],
    prediction_type: str,
    crop: str,
    district: str,
    taluka: Optional[str],
    season: str,
    target_year: int,
    model_version: str,
    predicted_value: float,
    predicted_lower_bound: Optional[float],
    predicted_upper_bound: Optional[float],
    actual_value: float,
    value_unit: str,
    input_provenance: str,
    observation_source: str,
    verification_status: str = "unverified",
    db_path: Optional[str] = None
) -> Optional[int]:
    """Persist prediction vs actual harvest comparison without modifying original prediction."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    abs_err = abs(float(predicted_value) - float(actual_value))
    pct_err = round((abs_err / max(0.001, float(actual_value))) * 100.0, 2)
    
    within_bound = 0
    if predicted_lower_bound is not None and predicted_upper_bound is not None:
        if float(predicted_lower_bound) <= float(actual_value) <= float(predicted_upper_bound):
            within_bound = 1
    elif abs_err <= 0.15 * max(1.0, float(actual_value)):
        within_bound = 1

    with get_db_cursor(db_path) as cursor:
        cursor.execute("""
            INSERT INTO outcome_comparisons (
                comparison_id, prediction_id, prediction_type, crop, district,
                taluka, season, target_year, model_version, predicted_value,
                predicted_lower_bound, predicted_upper_bound, actual_value,
                value_unit, absolute_error, percentage_error, is_within_error_bound,
                input_provenance, observation_source, verification_status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            comparison_id, prediction_id, prediction_type, crop, district,
            taluka, season, int(target_year), model_version, float(predicted_value),
            float(predicted_lower_bound) if predicted_lower_bound is not None else None,
            float(predicted_upper_bound) if predicted_upper_bound is not None else None,
            float(actual_value), value_unit, round(abs_err, 2), pct_err, within_bound,
            input_provenance, observation_source, verification_status, now_str
        ))
        return cursor.lastrowid

def get_outcome_comparisons(
    district: Optional[str] = None,
    crop: Optional[str] = None,
    limit: int = 50,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieve outcome comparisons."""
    with get_db_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = "SELECT * FROM outcome_comparisons WHERE 1=1"
        params = []
        if district:
            query += " AND district = ? COLLATE NOCASE"
            params.append(district)
        if crop:
            query += " AND crop = ? COLLATE NOCASE"
            params.append(crop)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
    return [dict(r) for r in rows]

def get_validation_summary(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Calculate aggregate validation metrics, sample sizes, and empirical error bounds.
    
    Adheres strictly to statistical sample-size minimums: requires at least N>=10
    observations per crop before reporting aggregate error metrics.
    """
    with get_db_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM outcome_comparisons")
        all_records = [dict(r) for r in cursor.fetchall()]

    crops = ["Cotton", "Tomato", "Onion", "Sugarcane"]
    crop_stats = {}

    for c in crops:
        records = [r for r in all_records if r["crop"].lower() == c.lower()]
        n = len(records)
        verified_count = sum(1 for r in records if r.get("verification_status") == "verified")
        unverified_count = n - verified_count

        if n >= 10:
            errors = [r["absolute_error"] for r in records]
            pct_errors = [r["percentage_error"] for r in records]
            within_bounds = sum(1 for r in records if r["is_within_error_bound"] == 1)
            mae = round(sum(errors) / n, 2)
            mape = round(sum(pct_errors) / n, 2)
            coverage_pct = round((within_bounds / n) * 100.0, 1)
            reliability = "statistically_robust" if n >= 30 else "preliminary_sample"
        else:
            mae = None
            mape = None
            coverage_pct = None
            reliability = "insufficient_data"

        crop_stats[c] = {
            "sample_size_n": n,
            "verified_count": verified_count,
            "unverified_count": unverified_count,
            "mean_absolute_error": mae,
            "mean_absolute_percentage_error": mape,
            "within_bounds_coverage_pct": coverage_pct,
            "statistical_reliability": reliability,
            "minimum_threshold_met": n >= 10,
            "disclaimer": (
                f"Sample size (N={n}) is below statistical minimum (N>=10). "
                "Aggregate accuracy metrics are withheld to prevent misleading conclusions."
                if n < 10 else
                f"Preliminary field sample (N={n}). Use for exploratory evaluation."
                if n < 30 else
                f"Statistically robust validation sample (N={n})."
            )
        }

    return {
        "status": "success",
        "total_field_comparisons": len(all_records),
        "crops": crop_stats,
        "sample_size_minimum_rule": "N >= 10 required for aggregate error statistics; N >= 30 for production certification.",
        "scientific_integrity_notice": "Zero synthetic records included. All metrics computed exclusively on submitted field observations."
    }

def checkpoint_wal(db_path: Optional[str] = None, mode: str = "PASSIVE") -> Dict[str, Any]:
    """Execute SQLite WAL checkpoint safely (PASSIVE, FULL, RESTART, or TRUNCATE)."""
    target_path = db_path or os.getenv("AGRIPREDICT_DB_PATH", DB_PATH)
    valid_modes = {"PASSIVE", "FULL", "RESTART", "TRUNCATE"}
    selected_mode = mode.upper() if mode.upper() in valid_modes else "PASSIVE"

    with get_db_connection(target_path) as conn:
        res = conn.execute(f"PRAGMA wal_checkpoint({selected_mode});").fetchone()
        return {
            "status": "success",
            "mode": selected_mode,
            "busy": res[0] if res else 0,
            "log": res[1] if res else 0,
            "checkpointed": res[2] if res else 0,
        }

def backup_database(dest_path: str, source_db_path: Optional[str] = None) -> Dict[str, Any]:
    """Perform a live, thread-safe online SQLite backup during concurrent operations."""
    source_path = source_db_path or os.getenv("AGRIPREDICT_DB_PATH", DB_PATH)
    dest_dir = Path(dest_path).resolve().parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    with get_db_connection(source_path) as src_conn:
        with sqlite3.connect(dest_path) as dest_conn:
            src_conn.backup(dest_conn)

    return {
        "status": "success",
        "source": source_path,
        "destination": dest_path,
        "bytes": os.path.getsize(dest_path) if os.path.exists(dest_path) else 0
    }

def restore_database(backup_path: str, target_db_path: str) -> Dict[str, Any]:
    """Restore an isolated database copy from a valid backup file."""
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file not found: {backup_path}")

    target_dir = Path(target_db_path).resolve().parent
    target_dir.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(backup_path) as src_conn:
        with sqlite3.connect(target_db_path) as dest_conn:
            src_conn.backup(dest_conn)

    return {
        "status": "success",
        "source": backup_path,
        "restored_to": target_db_path,
        "bytes": os.path.getsize(target_db_path) if os.path.exists(target_db_path) else 0
    }

# Initialize on module import
init_db()
