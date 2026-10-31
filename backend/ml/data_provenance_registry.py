"""
AgriPredict-AI Permanent Data Provenance Registry (Phase 13 WP3)

Provides programmatic verification, classification, and separation of:
- authentic_official_observation
- authentic_research_observation
- verified_field_observation
- farmer_reported_unverified
- synthetic_benchmark
- derived_or_transformed
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

PROJECT_ROOT = Path("C:/Users/karta/.gemini/antigravity/scratch/AgriPredict-AI")
REGISTRY_PATH = PROJECT_ROOT / "data" / "provenance_registry.json"

VALID_CLASSIFICATIONS = {
    "authentic_official_observation",
    "authentic_research_observation",
    "verified_field_observation",
    "farmer_reported_unverified",
    "synthetic_benchmark",
    "derived_or_transformed"
}

def load_provenance_registry() -> Dict[str, Any]:
    """Load the permanent provenance registry."""
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Provenance registry not found at {REGISTRY_PATH}")
    with open(REGISTRY_PATH, "r") as f:
        return json.load(f)

def get_datasets_by_classification(classification: str) -> List[Dict[str, Any]]:
    """Retrieve datasets matching a specific provenance classification."""
    if classification not in VALID_CLASSIFICATIONS:
        raise ValueError(f"Unknown classification '{classification}'. Must be one of: {VALID_CLASSIFICATIONS}")
    reg = load_provenance_registry()
    return [d for d in reg.get("datasets", []) if d.get("classification") == classification]

def verify_dataset_integrity(dataset_id: str) -> Dict[str, Any]:
    """Verify SHA-256 integrity of a registered dataset against its stored hash."""
    reg = load_provenance_registry()
    entry = next((d for d in reg.get("datasets", []) if d.get("dataset_id") == dataset_id), None)
    if not entry:
        raise KeyError(f"Dataset '{dataset_id}' not found in provenance registry")
    
    file_rel = entry.get("file_path", "")
    if "Embedded" in entry.get("sha256", "") or "Dynamic" in entry.get("sha256", ""):
        return {
            "dataset_id": dataset_id,
            "status": "skipped_dynamic_or_embedded",
            "message": "Dynamic database table or code-embedded registry"
        }
        
    full_path = PROJECT_ROOT / file_rel
    if not full_path.exists():
        return {
            "dataset_id": dataset_id,
            "status": "file_missing",
            "file_path": str(full_path)
        }
        
    actual_hash = hashlib.sha256(full_path.read_bytes()).hexdigest()
    expected_hash = entry.get("sha256", "").lower()
    
    return {
        "dataset_id": dataset_id,
        "status": "verified_match" if actual_hash == expected_hash else "hash_mismatch",
        "file_path": str(full_path),
        "actual_sha256": actual_hash,
        "expected_sha256": expected_hash,
        "is_synthetic": entry.get("is_synthetic", False)
    }

def is_synthetic_dataset(file_path: str) -> bool:
    """Check if a file path is classified as synthetic benchmark data."""
    path_str = str(file_path).replace("\\", "/").lower()
    reg = load_provenance_registry()
    for d in reg.get("datasets", []):
        entry_path = d.get("file_path", "").replace("\\", "/").lower()
        if entry_path in path_str and d.get("is_synthetic", False):
            return True
    return False
