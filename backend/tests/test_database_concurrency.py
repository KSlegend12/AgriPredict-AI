import pytest
import sqlite3
import concurrent.futures
from pathlib import Path
from backend.database.db import (
    init_db,
    save_prediction,
    save_cotton_prediction,
    get_history,
    get_db_status,
    get_db_cursor,
    get_db_connection,
    DB_PATH
)

@pytest.fixture
def temp_db(tmp_path):
    """Fixture providing an isolated temporary SQLite database configured in WAL mode."""
    db_file = str(tmp_path / "test_concurrency.db")
    status = init_db(db_file)
    assert status["initialized"] is True
    assert status["journal_mode"].lower() == "wal"
    return db_file

def test_repeated_init_db_idempotency(temp_db):
    """Verify that init_db can be called repeatedly without errors or altering existing data."""
    # Write a record
    save_prediction("Akola", "Kharif", "Tomato", 85.0, 70.0, 40.0, 32.5, {"temp": 28}, db_path=temp_db)
    
    # Call init_db 5 times consecutively
    for _ in range(5):
        status = init_db(temp_db)
        assert status["initialized"] is True
        assert status["journal_mode"].lower() == "wal"
    
    # Verify the record still exists
    hist = get_history(10, db_path=temp_db)
    assert len(hist) == 1
    assert hist[0]["district"] == "Akola"

def test_concurrent_crop_recommendation_writes(temp_db):
    """Verify multiple simultaneous crop recommendation history writes succeed under WAL."""
    num_writes = 25

    def write_worker(idx):
        return save_prediction(
            district="Akola",
            season="Kharif",
            recommended_crop="Tomato" if idx % 2 == 0 else "Onion",
            tomato_suitability=80.0 + idx,
            onion_suitability=75.0,
            sugarcane_suitability=50.0,
            predicted_yield=30.0 + idx,
            inputs={"iteration": idx, "nitrogen": 90},
            db_path=temp_db
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        inserted_ids = list(executor.map(write_worker, range(num_writes)))

    assert len(inserted_ids) == num_writes
    assert all(isinstance(id_, int) and id_ > 0 for id_ in inserted_ids)
    assert len(set(inserted_ids)) == num_writes  # All IDs must be unique

    # Verify total in database
    status = get_db_status(temp_db)
    assert status["prediction_history_count"] == num_writes

def test_concurrent_cotton_prediction_writes(temp_db):
    """Verify multiple simultaneous cotton prediction history writes succeed under WAL."""
    num_writes = 25

    def cotton_worker(idx):
        return save_cotton_prediction(
            district="Nagpur",
            year=2024,
            predicted_yield=350.0 + idx,
            lower_bound=320.0,
            upper_bound=380.0,
            model_type="candidate_six_district_dar_deficit_heat_thresh",
            inputs={"rainfall_kharif_mm": 800 + idx},
            db_path=temp_db
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        inserted_ids = list(executor.map(cotton_worker, range(num_writes)))

    assert len(inserted_ids) == num_writes
    assert all(isinstance(id_, int) and id_ > 0 for id_ in inserted_ids)
    assert len(set(inserted_ids)) == num_writes

    status = get_db_status(temp_db)
    assert status["cotton_prediction_history_count"] == num_writes

def test_concurrent_reads_and_writes(temp_db):
    """Verify concurrent reads and writes execute without table locks or deadlocks."""
    # Seed 10 records
    for i in range(10):
        save_prediction("Wardha", "Kharif", "Sugarcane", 60.0, 60.0, 90.0, 85.0, {"i": i}, db_path=temp_db)

    def reader(idx):
        return get_history(limit=20, db_path=temp_db)

    def writer(idx):
        return save_cotton_prediction(
            district="Amravati",
            year=2024,
            predicted_yield=400.0 + idx,
            lower_bound=380.0,
            upper_bound=420.0,
            model_type="candidate_six_district_thermal",
            inputs={"iteration": idx},
            db_path=temp_db
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        read_futures = [executor.submit(reader, i) for i in range(15)]
        write_futures = [executor.submit(writer, i) for i in range(15)]

        # Wait for all
        read_results = [f.result() for f in read_futures]
        write_results = [f.result() for f in write_futures]

    assert len(read_results) == 15
    assert len(write_results) == 15
    assert all(isinstance(r, list) for r in read_results)
    assert all(isinstance(w, int) for w in write_results)

    status = get_db_status(temp_db)
    assert status["prediction_history_count"] == 10
    assert status["cotton_prediction_history_count"] == 15

def test_transaction_rollback_after_simulated_failure(temp_db):
    """Verify that an exception inside a transaction properly triggers rollback."""
    initial_count = get_db_status(temp_db)["prediction_history_count"]

    with pytest.raises(ValueError, match="Simulated application failure during write"):
        with get_db_cursor(temp_db) as cursor:
            cursor.execute("""
                INSERT INTO prediction_history (
                    timestamp, district, season, recommended_crop,
                    tomato_suitability, onion_suitability, sugarcane_suitability,
                    predicted_yield, input_parameters
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("2026-10-30 23:30:00", "Akola", "Kharif", "Tomato", 90, 80, 50, 35, "{}"))
            # Raise exception before transaction block exits
            raise ValueError("Simulated application failure during write")

    # Assert row was rolled back and not persisted
    final_count = get_db_status(temp_db)["prediction_history_count"]
    assert final_count == initial_count

def test_database_busy_timeout_configured(temp_db):
    """Verify that PRAGMA busy_timeout is set to 15000 ms."""
    status = get_db_status(temp_db)
    assert status["busy_timeout"] == 15000
    assert status["journal_mode"].lower() == "wal"
    assert status["foreign_keys"] == 1

def test_persistence_after_connection_restart(temp_db):
    """Verify that data written persists after all connections are closed and reopened."""
    pred_id = save_prediction(
        "Buldhana", "Rabi", "Onion", 50.0, 95.0, 40.0, 24.5,
        {"soil_ph": 6.8}, db_path=temp_db
    )
    assert pred_id is not None

    cotton_id = save_cotton_prediction(
        "Buldhana", 2023, 310.5, 290.0, 330.0,
        "candidate_six_district_dar_deficit_heat_thresh",
        {"target_year": 2023}, db_path=temp_db
    )
    assert cotton_id is not None

    # Fetch in fresh connection
    hist = get_history(10, db_path=temp_db)
    assert len(hist) == 2
    assert any(h["district"] == "Buldhana" and h["crop_type"] == "Onion" for h in hist)
    assert any(h["district"] == "Buldhana" and h["crop_type"] == "Cotton" for h in hist)

def test_existing_production_records_remain_accessible():
    """Verify that the production database retains all original records in WAL mode (READ-ONLY)."""
    assert Path(DB_PATH).exists()
    status = get_db_status(DB_PATH)
    assert status["journal_mode"].lower() == "wal"
    assert status["busy_timeout"] == 15000
    assert status["foreign_keys"] == 1
    # Verify legacy records remain fully present
    assert status["prediction_history_count"] >= 189
    assert status["cotton_prediction_history_count"] >= 2311

    # Read latest history entries from production
    history_items = get_history(limit=5)
    assert len(history_items) == 5
    for item in history_items:
        assert "timestamp" in item
        assert "district" in item
        assert "predicted_yield" in item
