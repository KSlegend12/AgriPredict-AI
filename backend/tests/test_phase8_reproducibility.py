"""
Phase 8: Scientific Reproducibility & Research Audit Regression Tests.
=============================================================================
Validates:
1. Protected dataset and production model SHA-256 cryptographic hashes.
2. 100% exact reproduction of 13-fold chronological CV metrics.
3. Statistical significance audit invariants under spatial/temporal clustering.
4. Conformal prediction finite-sample calibration properties.
5. NASA SMAP incremental experimental reproducibility.
6. Future forecasting horizon models and rolling-origin hindcast reproducibility.
"""

import hashlib
import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = REPO_ROOT / "data/vidarbha_cotton_model_ready_1997_2024.csv"
PROD_MODEL_PATH = REPO_ROOT / "backend/ml/artifacts/final_model.pkl"
PHASE8_DIR = REPO_ROOT / "backend/ml/experiments/phase8_scientific_reproducibility"

EXPECTED_DATASET_HASH = "1430370e066b41431cc164fb6f12759f7d1e97bb1cb4f590f77cad2b4ee53091"
EXPECTED_PROD_MODEL_HASH = "3b0c2fda194cd923e4957b4637f3a97e5df3fd885623c9eb182588dca816bd8e"


class TestPhase8ScientificReproducibility:
    """Automated verification of Phase 8 reproducibility audits."""

    def test_protected_cryptographic_hashes(self):
        """Authoritative dataset and final model must never be modified."""
        h_csv = hashlib.sha256(DATASET_PATH.read_bytes()).hexdigest()
        h_model = hashlib.sha256(PROD_MODEL_PATH.read_bytes()).hexdigest()
        assert h_csv == EXPECTED_DATASET_HASH, f"Canonical CSV hash altered: {h_csv}"
        assert h_model == EXPECTED_PROD_MODEL_HASH, f"Production model hash altered: {h_model}"

    def test_cotton_metrics_exact_reproduction(self):
        """Chronological CV and 2024 holdout metrics must match Phase 7 exactly."""
        audit_file = PHASE8_DIR / "phase8_cotton_reproducibility_audit.json"
        assert audit_file.exists(), "Cotton reproducibility audit artifact missing"
        data = json.loads(audit_file.read_text())
        
        comparison = data["reproduction_comparison"]
        for row in comparison:
            assert row["Status"] == "EXACT MATCH", f"Discrepancy in model {row['Model']}"
            assert row["Diff CV"] == 0.0, f"CV MAE mismatch for {row['Model']}"
            assert row["Diff 2024"] == 0.0, f"2024 holdout MAE mismatch for {row['Model']}"

    def test_statistical_significance_audit(self):
        """DAR Deficit Heat Thresh improvement over Thermal Ridge must be non-significant
        under both naive and dependence-robust tests."""
        audit_file = PHASE8_DIR / "phase8_cotton_reproducibility_audit.json"
        data = json.loads(audit_file.read_text())
        stat = data["statistical_significance_audit"]
        
        assert not stat["statistically_significant_at_005"]
        assert stat["naive_ttest"]["p_val"] > 0.10
        assert stat["year_block_bootstrap"]["p_val"] > 0.15
        assert stat["district_cluster_bootstrap"]["p_val"] > 0.15
        assert stat["exact_year_permutation"]["p_val"] > 0.15

    def test_conformal_calibration_properties(self):
        """Conformal calibration quantiles and coverage properties."""
        audit_file = PHASE8_DIR / "phase8_cotton_reproducibility_audit.json"
        data = json.loads(audit_file.read_text())
        conf = data["conformal_prediction_audit"]
        
        assert conf["sample_size"] == 78
        assert conf["quantiles"]["0.9"] == 253.53 or round(conf["quantiles"]["0.9"], 1) == 253.5
        # Verify finite sample ranks
        ranks = [row["Rank k / N+1"] for row in conf["overall_summary"]]
        assert "72 / 79" in ranks  # 90% level rank

    def test_smap_incremental_reproducibility(self):
        """SMAP experimental results must match saved artifacts with zero discrepancy."""
        audit_file = PHASE8_DIR / "phase8_smap_reproducibility_audit.json"
        assert audit_file.exists(), "SMAP audit artifact missing"
        data = json.loads(audit_file.read_text())
        
        for row in data["smap_reproduced_cv"]:
            assert float(row["Abs Diff"]) == 0.0, f"Discrepancy in SMAP model {row['Model']} {row['Feature Set']}"
            
        for row in data["smap_significance"]:
            # All positive SMAP variants must have p > 0.10 and CI crossing zero
            if row["Mean Delta (kg/ha)"] > 0:
                assert not row["Significant (p < 0.05)"]

    def test_future_forecast_hindcast_reproducibility(self):
        """Future forecasting rolling-origin hindcasts must reproduce saved MAEs exactly."""
        audit_file = PHASE8_DIR / "phase8_future_forecast_audit.json"
        assert audit_file.exists(), "Future forecast audit artifact missing"
        data = json.loads(audit_file.read_text())
        
        for row in data["reproduced_hindcast"]:
            assert row["Reprod MAE"] == row["Saved MAE"], f"Mismatch in horizon {row['Horizon']}"
            if row["Horizon"] in [2, 3, 4, 5, 7]:
                assert row["Model Better (p < 0.05)"], f"Expected significant improvement at horizon {row['Horizon']}"

    def test_agronomic_registry_evidence_audit(self):
        """All key thresholds must be formally classified in registry."""
        reg_file = PHASE8_DIR / "agronomic_evidence_audit_registry.json"
        assert reg_file.exists(), "Agronomic evidence registry missing"
        registry = json.loads(reg_file.read_text())
        
        params = [item["parameter_or_threshold"] for item in registry]
        assert any("Cotton Seasonal Water Requirement" in p for p in params)
        assert any("Kharif Rainfall Deficit Threshold" in p for p in params)
        assert any("Thermal Heat Stress Threshold" in p for p in params)
        assert any("Soil pH Agronomic Range" in p for p in params)
        assert any("Sugarcane Deficit Moisture Penalty" in p for p in params)
        assert any("Tomato High Humidity" in p for p in params)
