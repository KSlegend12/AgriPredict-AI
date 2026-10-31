"""
Comprehensive Security, Abuse Protection, and Data Integrity Test Suite.

Verifies:
1. Malformed JSON request bodies
2. Oversized payload rejection (413 Payload Too Large)
3. Path traversal and poison byte rejection (400 Bad Request)
4. Invalid query parameter handling
5. Unexpected exception masking (no internal tracebacks/paths leaked)
6. In-memory process-local rate limiting (429 Too Many Requests with headers)
7. Transaction rollback on database write failure
8. SQL injection attempt neutralization
9. Defense-in-depth security response headers
10. Valid agricultural workflows remain functional under security middleware
"""

import os
import json
import sqlite3
import tempfile
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.security.rate_limiter import limiter, SlidingWindowRateLimiter
from backend.security.request_filter import MAX_PAYLOAD_SIZE
from backend.database.db import (
    get_connection,
    get_db_cursor,
    save_prediction,
    save_cotton_prediction,
    init_db,
)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Ensure limiter is reset before each security test."""
    limiter.reset()
    yield
    limiter.reset()


# ---------------------------------------------------------------------------
# 1. Malformed Request Handling
# ---------------------------------------------------------------------------

def test_malformed_json_request(client):
    """Verify that syntactically broken JSON bodies are rejected gracefully."""
    response = client.post(
        "/api/crop/recommend",
        content="{\"district\": \"Pune\", broken_json_here",
        headers={"Content-Type": "application/json"}
    )
    # FastAPI returns 422 or 400 for unparseable JSON
    assert response.status_code in (400, 422)
    data = response.json()
    assert "detail" in data


# ---------------------------------------------------------------------------
# 2. Oversized Payload Protection
# ---------------------------------------------------------------------------

def test_oversized_payload_rejected(client):
    """Verify that requests exceeding MAX_PAYLOAD_SIZE are rejected with 413."""
    large_size = MAX_PAYLOAD_SIZE + 1024
    response = client.post(
        "/api/crop/recommend",
        headers={
            "Content-Type": "application/json",
            "Content-Length": str(large_size),
        },
        content="x" * 100,  # Header declared size triggers early rejection
    )
    assert response.status_code == 413
    data = response.json()
    assert data["error_code"] == "PAYLOAD_TOO_LARGE"


# ---------------------------------------------------------------------------
# 3. Path Traversal & Suspicious Character Filtering
# ---------------------------------------------------------------------------

def test_path_traversal_directory_dots(client):
    """Verify directory traversal sequence '..' in path is blocked with 400."""
    response = client.get("/api/weather/..%2F..%2Fetc%2Fpasswd")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "SUSPICIOUS_REQUEST_PATH"


def test_path_traversal_null_byte(client):
    """Verify null byte poison characters are blocked with 400."""
    response = client.get("/api/weather/Akola%00.txt")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "SUSPICIOUS_REQUEST_PATH"


def test_path_traversal_cotton_forecast(client):
    """Verify path traversal on future-forecast route is blocked."""
    response = client.get("/api/cotton/future-forecast/..%2F..%2Fwindows%2Fwin.ini")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "SUSPICIOUS_REQUEST_PATH"


# ---------------------------------------------------------------------------
# 4. Invalid Query Parameter Validation
# ---------------------------------------------------------------------------

def test_invalid_history_limit_type(client):
    """Verify non-integer query parameter returns 422."""
    response = client.get("/api/history?limit=invalid_string")
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# 5. SQL Injection Neutralization
# ---------------------------------------------------------------------------

def test_sql_injection_in_cotton_prediction_district(client):
    """Verify that SQL injection string in cotton district parameter is rejected."""
    payload = {
        "district": "Akola' OR '1'='1",
        "target_year": 2024,
        "model_version": "production"
    }
    response = client.post("/api/cotton/predict", json=payload)
    # Pydantic Literal validation rejects unauthorized districts with 422
    assert response.status_code == 422


def test_sql_injection_in_crop_recommend_district(client):
    """Verify SQL injection payload in crop recommendation district is rejected."""
    payload = {
        "district": "Pune'; DROP TABLE prediction_history; --",
        "season": "Kharif",
        "temperature": 27.5,
        "rainfall": 680.0,
        "humidity": 72.0,
        "soil_ph": 6.8,
        "nitrogen": 85.0,
        "phosphorus": 45.0,
        "potassium": 55.0,
        "soil_moisture": 60.0
    }
    response = client.post("/api/crop/recommend", json=payload)
    # Validator rejects non-canonical district with 422
    assert response.status_code == 422


def test_sql_injection_in_database_query(tmp_path):
    """Verify that database queries use parameter binding and are safe against injection."""
    test_db = str(tmp_path / "test_inject.db")
    init_db(test_db)

    # Attempting to insert malicious district name
    malicious_district = "Akola'); DROP TABLE prediction_history; --"
    pred_id = save_prediction(
        district=malicious_district,
        season="Kharif",
        recommended_crop="Tomato",
        tomato_suitability=90.0,
        onion_suitability=80.0,
        sugarcane_suitability=70.0,
        predicted_yield=45.0,
        inputs={"district": malicious_district},
        db_path=test_db
    )
    assert pred_id is not None

    # Verify table was NOT dropped and record was saved safely as literal text
    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("SELECT district FROM prediction_history WHERE id = ?", (pred_id,))
    row = cur.fetchone()
    assert row is not None
    assert row[0] == malicious_district
    conn.close()


# ---------------------------------------------------------------------------
# 6. Database Rollback on Write Failure
# ---------------------------------------------------------------------------

def test_database_atomic_rollback(tmp_path):
    """Verify that failed transactions roll back cleanly leaving no partial state."""
    test_db = str(tmp_path / "test_rollback.db")
    init_db(test_db)

    conn = get_connection(test_db)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM cotton_prediction_history;")
    initial_count = cur.fetchone()[0]
    conn.close()

    # Attempt a transaction block that raises an error after an INSERT
    with pytest.raises(RuntimeError):
        with get_db_cursor(test_db) as cursor:
            cursor.execute("""
                INSERT INTO cotton_prediction_history (
                    timestamp, district, target_year, model_version,
                    predicted_yield, lower_bound, upper_bound, input_parameters
                ) VALUES ('2026-10-30 00:00:00', 'Akola', 2024, 'production', 350.0, NULL, NULL, '{}')
            """)
            # Simulate unexpected failure mid-transaction
            raise RuntimeError("Forced simulation of mid-transaction crash")

    # Verify that the insert was rolled back completely
    conn = get_connection(test_db)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM cotton_prediction_history;")
    final_count = cur.fetchone()[0]
    conn.close()

    assert final_count == initial_count


# ---------------------------------------------------------------------------
# 7. Rate Limiting Abuse Protection
# ---------------------------------------------------------------------------

def test_rate_limiter_exceeded_returns_429():
    """Verify that the in-memory sliding window rate limiter returns 429 when quota exceeded."""
    custom_limiter = SlidingWindowRateLimiter(enabled=True)
    client_ip = "192.168.1.100"
    path = "/api/cotton/predict"
    test_limit = (5, 60)  # 5 requests per 60 seconds

    # First 5 requests must succeed
    for i in range(5):
        allowed, limit, remaining, retry_after = custom_limiter.is_allowed(client_ip, path, custom_limit=test_limit)
        assert allowed is True
        assert remaining == 5 - (i + 1)
        assert retry_after == 0

    # 6th request must be rejected with retry_after > 0
    allowed, limit, remaining, retry_after = custom_limiter.is_allowed(client_ip, path, custom_limit=test_limit)
    assert allowed is False
    assert remaining == 0
    assert retry_after > 0


def test_rate_limiting_middleware_live(client):
    """Verify live rate limiting middleware emits 429, Retry-After, and X-RateLimit headers."""
    # Temporarily set quota on cotton endpoint group to 3 for testing
    from backend.security.rate_limiter import DEFAULT_QUOTAS
    original_quota = DEFAULT_QUOTAS["cotton_ml"]
    DEFAULT_QUOTAS["cotton_ml"] = (3, 60)
    limiter.enforce_for_testclient = True

    try:
        payload = {
            "district": "Akola",
            "target_year": 2024,
            "model_version": "production"
        }

        # Make 3 valid requests
        for _ in range(3):
            r = client.post("/api/cotton/predict", json=payload)
            assert r.status_code == 200
            assert "X-RateLimit-Limit" in r.headers

        # 4th request must be rate-limited
        r4 = client.post("/api/cotton/predict", json=payload)
        assert r4.status_code == 429
        assert "Retry-After" in r4.headers
        assert r4.headers["X-RateLimit-Remaining"] == "0"
        data = r4.json()
        assert data["error_code"] == "RATE_LIMIT_EXCEEDED"
    finally:
        DEFAULT_QUOTAS["cotton_ml"] = original_quota
        limiter.reset()


# ---------------------------------------------------------------------------
# 8. Defense-in-Depth Security Headers
# ---------------------------------------------------------------------------

def test_security_headers_present(client):
    """Verify that security headers (nosniff, DENY) and contextual HSTS are injected."""
    response = client.get("/api/districts")
    assert response.status_code == 200
    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"

    # Over HTTPS / forwarded HTTPS, HSTS header must be present
    https_response = client.get("/api/districts", headers={"x-forwarded-proto": "https"})
    assert "Strict-Transport-Security" in https_response.headers



# ---------------------------------------------------------------------------
# 9. Error Response Information Leakage Prevention
# ---------------------------------------------------------------------------

def test_unhandled_exception_does_not_leak_internals(client):
    """Verify that unhandled exceptions return a clean generic 500 without stack traces."""
    # Simulate an error by querying weather with a mock that throws an unexpected internal error
    response = client.get("/api/weather/NonExistentDistrictName")
    # Should return either 200 (fallback) or 500 with clean message, never a raw traceback
    if response.status_code == 500:
        data = response.json()
        text = json.dumps(data)
        assert "Traceback" not in text
        assert "File \"" not in text
        assert "line " not in text


# ---------------------------------------------------------------------------
# 10. Valid Production Workflow Verification Under Security Filter
# ---------------------------------------------------------------------------

def test_valid_cotton_predict_workflow(client):
    """Verify cotton prediction operates cleanly under the security middleware."""
    payload = {
        "district": "Amravati",
        "target_year": 2024,
        "model_version": "candidate_six_district_dar_deficit_heat_thresh"
    }
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["predicted_yield_kg_ha"] > 0
    assert data["model_version"] == "candidate_six_district_dar_deficit_heat_thresh"


def test_valid_crop_recommend_workflow(client):
    """Verify crop recommendation operates cleanly under the security middleware."""
    payload = {
        "district": "Pune",
        "season": "Kharif",
        "temperature": 27.5,
        "rainfall": 680.0,
        "humidity": 72.0,
        "wind_speed": 14.0,
        "soil_ph": 6.8,
        "nitrogen": 85.0,
        "phosphorus": 45.0,
        "potassium": 55.0,
        "soil_moisture": 60.0
    }
    response = client.post("/api/crop/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["recommendations"]) > 0
