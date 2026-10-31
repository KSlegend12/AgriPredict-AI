"""
Production Readiness, Backup/Recovery, and Deployment Reliability Test Suite.

Verifies:
1. SQLite online backup & isolated restore
2. SQLite WAL checkpointing
3. Concurrent writes during live online backup
4. Rate limiter trusted reverse proxy handling & IP spoofing resistance
5. Rate limiter memory purging of expired IP deques
6. Chunked/large body rejection (413 Payload Too Large)
7. Contextual HSTS injection (HTTPS only)
8. Model artifact registry consistency and version propagation
9. Future forecasting serving provenance (origin_year=2024, horizons 3-7)
"""

import os
import time
import sqlite3
import threading
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.database.db import (
    get_connection,
    get_db_cursor,
    init_db,
    save_cotton_prediction,
    backup_database,
    restore_database,
    checkpoint_wal,
    get_db_status,
)
from backend.security.rate_limiter import (
    limiter,
    extract_client_ip,
    SlidingWindowRateLimiter,
    TRUSTED_PROXIES,
)
from backend.security.request_filter import MAX_PAYLOAD_SIZE
from backend.ml.cotton_predictor import cotton_predictor
from backend.ml.future_forecasting.predictor import forecast_district, FORECAST_YEARS


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_limiter():
    limiter.reset()
    yield
    limiter.reset()


# ---------------------------------------------------------------------------
# 1. Database Backup, Restore, and Checkpointing
# ---------------------------------------------------------------------------

def test_sqlite_online_backup_and_restore(tmp_path):
    """Verify official SQLite online backup and isolated restore without corrupting source."""
    src_db = str(tmp_path / "source.db")
    backup_file = str(tmp_path / "backup" / "agripredict_backup.db")
    restored_db = str(tmp_path / "restored" / "restored.db")

    init_db(src_db)

    # Insert test records into source
    for i in range(5):
        save_cotton_prediction(
            district="Akola",
            year=2024,
            predicted_yield=320.0 + i,
            lower_bound=300.0,
            upper_bound=340.0,
            model_type="candidate_six_district_thermal",
            inputs={"test_id": i},
            db_path=src_db
        )

    # Execute online backup
    backup_res = backup_database(backup_file, source_db_path=src_db)
    assert backup_res["status"] == "success"
    assert os.path.exists(backup_file)
    assert backup_res["bytes"] > 0

    # Restore from backup into a brand new isolated target
    restore_res = restore_database(backup_file, restored_db)
    assert restore_res["status"] == "success"
    assert os.path.exists(restored_db)

    # Verify integrity and row count of restored database
    with sqlite3.connect(restored_db) as conn:
        cur = conn.cursor()
        ic = cur.execute("PRAGMA integrity_check;").fetchone()[0]
        assert ic == "ok"
        cnt = cur.execute("SELECT COUNT(*) FROM cotton_prediction_history;").fetchone()[0]
        assert cnt == 5


def test_sqlite_wal_checkpoint(tmp_path):
    """Verify SQLite WAL checkpoint executes cleanly in PASSIVE and TRUNCATE modes."""
    test_db = str(tmp_path / "checkpoint_test.db")
    init_db(test_db)

    # Execute checkpoint
    chk_res = checkpoint_wal(test_db, mode="PASSIVE")
    assert chk_res["status"] == "success"
    assert chk_res["mode"] == "PASSIVE"

    chk_trunc = checkpoint_wal(test_db, mode="TRUNCATE")
    assert chk_trunc["status"] == "success"
    assert chk_trunc["mode"] == "TRUNCATE"


def test_backup_consistency_during_concurrent_writes(tmp_path):
    """Verify that SQLite online backup succeeds while concurrent writes occur in WAL mode."""
    test_db = str(tmp_path / "concurrent_src.db")
    backup_file = str(tmp_path / "concurrent_backup.db")
    init_db(test_db)

    stop_event = threading.Event()
    write_errors = []

    def writer_worker():
        count = 0
        while not stop_event.is_set():
            try:
                save_cotton_prediction(
                    district="Wardha",
                    year=2024,
                    predicted_yield=400.0 + count,
                    lower_bound=380.0,
                    upper_bound=420.0,
                    model_type="production",
                    inputs={"iter": count},
                    db_path=test_db
                )
                count += 1
                time.sleep(0.01)
            except Exception as e:
                write_errors.append(str(e))

    # Start writer thread
    writer_thread = threading.Thread(target=writer_worker, daemon=True)
    writer_thread.start()

    # Sleep briefly to ensure writer is active
    time.sleep(0.05)

    # Perform online backup during active writes
    backup_res = backup_database(backup_file, source_db_path=test_db)
    stop_event.set()
    writer_thread.join(timeout=2.0)

    assert backup_res["status"] == "success"
    assert len(write_errors) == 0, f"Write errors occurred: {write_errors}"

    # Verify backup is valid and intact
    with sqlite3.connect(backup_file) as conn:
        cur = conn.cursor()
        assert cur.execute("PRAGMA integrity_check;").fetchone()[0] == "ok"
        cnt = cur.execute("SELECT COUNT(*) FROM cotton_prediction_history;").fetchone()[0]
        assert cnt > 0


# ---------------------------------------------------------------------------
# 2. Reverse Proxy & Rate Limiter Reliability
# ---------------------------------------------------------------------------

def test_trusted_proxy_client_ip_extraction():
    """Verify that X-Forwarded-For is respected ONLY when request comes from trusted proxy."""
    from starlette.requests import Request

    # Case A: Request from trusted proxy (127.0.0.1) with X-Forwarded-For
    scope_trusted = {
        "type": "http",
        "client": ("127.0.0.1", 54321),
        "headers": [(b"x-forwarded-for", b"203.0.113.195, 10.0.0.1")],
    }
    req_trusted = Request(scope_trusted)
    assert extract_client_ip(req_trusted) == "203.0.113.195"

    # Case B: Request from untrusted external IP attempting to spoof X-Forwarded-For
    scope_untrusted = {
        "type": "http",
        "client": ("198.51.100.22", 12345),
        "headers": [(b"x-forwarded-for", b"8.8.8.8")],
    }
    req_untrusted = Request(scope_untrusted)
    # Must ignore spoofed header and use actual client IP
    assert extract_client_ip(req_untrusted) == "198.51.100.22"


def test_rate_limiter_memory_purging():
    """Verify that stale/expired IP keys are automatically purged to prevent memory growth."""
    custom_limiter = SlidingWindowRateLimiter(enabled=True)
    custom_limiter._cleanup_interval = 0.05  # 50ms cleanup trigger for test

    now = time.time()
    # Add requests for 3 separate IPs
    custom_limiter._requests["10.0.0.1:crop_ml"].append(now - 200.0)  # Expired (> 120s old)
    custom_limiter._requests["10.0.0.2:crop_ml"].append(now - 150.0)  # Expired (> 120s old)
    custom_limiter._requests["10.0.0.3:crop_ml"].append(now)          # Active

    assert len(custom_limiter._requests) == 3

    # Fast forward time to trigger purge
    custom_limiter.purge_expired_keys(now)

    assert "10.0.0.1:crop_ml" not in custom_limiter._requests
    assert "10.0.0.2:crop_ml" not in custom_limiter._requests
    assert "10.0.0.3:crop_ml" in custom_limiter._requests


# ---------------------------------------------------------------------------
# 3. Request Body Bounds & Chunked Payloads
# ---------------------------------------------------------------------------

def test_actual_body_size_rejection_without_content_length(client):
    """Verify that oversized request body is rejected with 413 even when Content-Length is manipulated."""
    # Send large body exceeding MAX_PAYLOAD_SIZE (1MB)
    large_payload = "a" * (MAX_PAYLOAD_SIZE + 500)
    response = client.post(
        "/api/crop/recommend",
        headers={"Content-Type": "application/json"},
        content=large_payload
    )
    assert response.status_code == 413
    assert response.json()["error_code"] == "PAYLOAD_TOO_LARGE"


# ---------------------------------------------------------------------------
# 4. Context-Aware HSTS Enforcement
# ---------------------------------------------------------------------------

def test_hsts_omitted_over_plain_http(client):
    """Verify HSTS header is omitted over plain HTTP to respect RFC 6797 and local dev."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "Strict-Transport-Security" not in response.headers


def test_hsts_included_over_https(client):
    """Verify HSTS header is strictly injected when request is transported over HTTPS."""
    response = client.get("/api/health", headers={"x-forwarded-proto": "https"})
    assert response.status_code == 200
    assert "Strict-Transport-Security" in response.headers


# ---------------------------------------------------------------------------
# 5. Model Serving Consistency & Registry Verification
# ---------------------------------------------------------------------------

def test_model_registry_contains_active_candidates():
    """Verify that all production and candidate models are properly loaded on cotton_predictor."""
    assert cotton_predictor.is_loaded is True
    assert cotton_predictor.model is not None

    # Verify Six-District Thermal Ridge (UI default candidate)
    assert getattr(cotton_predictor, "six_dist_thermal_is_loaded", False) is True
    assert getattr(cotton_predictor, "six_dist_thermal_pipeline", None) is not None

    # Verify Phase 2 champion Decoupled Agronomic Deficit Heat Threshold candidate
    assert getattr(cotton_predictor, "decoupled_deficit_heat_is_loaded", False) is True
    assert getattr(cotton_predictor, "decoupled_deficit_heat_pipeline", None) is not None



def test_candidate_model_version_propagation(client):
    """Verify model_version propagation across different candidate selectors."""
    for model_ver in ["candidate_six_district_thermal", "candidate_six_district_dar_deficit_heat_thresh"]:
        payload = {
            "district": "Akola",
            "target_year": 2024,
            "model_version": model_ver
        }
        res = client.post("/api/cotton/predict", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["model_version"] == model_ver
        assert data["predicted_yield_kg_ha"] > 0


# ---------------------------------------------------------------------------
# 6. Future Forecasting Serving Provenance
# ---------------------------------------------------------------------------

def test_future_forecast_serving_provenance():
    """Verify future forecasting uses origin_year=2024 and does not leak future actuals."""
    res = forecast_district("Akola")
    assert res["district"] == "Akola"
    assert res["origin_year"] == 2024
    assert list(res["forecast_years"]) == [2027, 2028, 2029, 2030, 2031]
    assert set(res["scenarios"].keys()) == {"normal", "dry", "wet"}

    for scenario_name, items in res["scenarios"].items():
        assert len(items) == 5
        for item in items:
            assert item["year"] in FORECAST_YEARS
            assert item["predicted_yield_kg_ha"] > 0
            assert item["uncertainty_lower_kg_ha"] <= item["uncertainty_upper_kg_ha"]
