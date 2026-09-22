"""
SMAP SPL4SMGP AppEEARS -> district-year feature extractor
For AgriPredict-AI

Expected input:
  data/satellite/SMAP/*.nc
  vidarbha_7_districts_nwic.geojson

Assumption:
  AppEEARS Area Sample `aid0001` ... `aid0007` follow the
  feature order of the submitted 7-feature GeoJSON. The script
  records this mapping explicitly and validates each NetCDF's
  time range and spatial overlap with the corresponding polygon.

Output:
  data/satellite/features/SMAP_district_year_features_2017_2024.csv
  data/satellite/features/SMAP_file_inventory.csv
  data/satellite/features/SMAP_mapping_validation.csv
"""

from pathlib import Path
import json
import re
import warnings

import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import shape, Point

ROOT = Path(__file__).resolve().parents[4]
SMAP_DIR = ROOT / "data" / "satellite" / "SMAP"
GEOJSON = ROOT / "data" / "satellite" / "vidarbha_7_districts_nwic.geojson"
OUT_DIR = ROOT / "data" / "satellite" / "features"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SURFACE = "Geophysical_Data_sm_surface"
ROOTZONE = "Geophysical_Data_sm_rootzone"

# Existing AgriPredict methodology:
# monsoon = Jun-Sep, kharif = Jun-Oct.
MONSOON_MONTHS = {6, 7, 8, 9}
KHARIF_MONTHS = {6, 7, 8, 9, 10}


def load_districts():
    with open(GEOJSON, "r", encoding="utf-8") as f:
        gj = json.load(f)

    features = gj["features"]
    mapping = {}
    for i, feat in enumerate(features, start=1):
        district = feat["properties"]["district"]
        mapping[i] = {
            "district": district,
            "geometry": shape(feat["geometry"]),
        }
    return mapping


def aid_from_filename(path):
    m = re.search(r"_aid(\d{4})", path.name)
    if not m:
        raise ValueError(f"Could not find aid#### in filename: {path.name}")
    return int(m.group(1))


def nearest_grid_cell_mask(lat_vals, lon_vals, polygon):
    """
    Use grid-cell centers for a conservative district-area mask.
    AppEEARS already spatially subsets the request; this second mask
    prevents the surrounding bounding box from being treated as the
    whole district.
    """
    mask = np.zeros((len(lat_vals), len(lon_vals)), dtype=bool)
    for i, lat in enumerate(lat_vals):
        for j, lon in enumerate(lon_vals):
            mask[i, j] = polygon.contains(Point(float(lon), float(lat))) or polygon.touches(
                Point(float(lon), float(lat))
            )
    return mask


def masked_stats(values, mask):
    a = np.asarray(values, dtype=float)
    a = np.where(mask[None, :, :], a, np.nan)
    valid = a[np.isfinite(a)]
    if valid.size == 0:
        return {
            "mean": np.nan, "min": np.nan, "max": np.nan,
            "std": np.nan, "valid_obs": 0
        }
    return {
        "mean": float(np.nanmean(valid)),
        "min": float(np.nanmin(valid)),
        "max": float(np.nanmax(valid)),
        "std": float(np.nanstd(valid)),
        "valid_obs": int(valid.size),
    }


def seasonal_stats(da, mask, months, prefix):
    sub = da.where(da.time.dt.month.isin(sorted(months)), drop=True)

    if sub.sizes.get("time", 0) == 0:
        return {
            f"{prefix}_mean": np.nan,
            f"{prefix}_min": np.nan,
            f"{prefix}_max": np.nan,
            f"{prefix}_std": np.nan,
            f"{prefix}_valid_obs": 0,
        }

    s = masked_stats(sub.values, mask)

    return {
        f"{prefix}_mean": s["mean"],
        f"{prefix}_min": s["min"],
        f"{prefix}_max": s["max"],
        f"{prefix}_std": s["std"],
        f"{prefix}_valid_obs": s["valid_obs"],
    }


def process_file(path, mapping):
    aid = aid_from_filename(path)
    if aid not in mapping:
        raise ValueError(f"aid{aid:04d} is not one of the 7 expected features")

    district = mapping[aid]["district"]
    polygon = mapping[aid]["geometry"]

    with xr.open_dataset(path) as ds:
        if SURFACE not in ds or ROOTZONE not in ds:
            raise ValueError(f"Missing expected SMAP variables in {path.name}")

        start = ds.time.values[0]
        end = ds.time.values[-1]
        year = int(start.year)

        if int(end.year) != year:
            raise ValueError(f"File spans multiple years: {path.name}")

        lat = np.asarray(ds.lat.values, dtype=float)
        lon = np.asarray(ds.lon.values, dtype=float)
        mask = nearest_grid_cell_mask(lat, lon, polygon)

        if not mask.any():
            warnings.warn(
                f"No grid-cell centers fell inside {district} for {path.name}. "
                "Check CRS/geometry alignment."
            )

        # Remove the declared NoData value. Valid range is 0..0.9 m3/m3.
        surf = ds[SURFACE].where((ds[SURFACE] >= 0) & (ds[SURFACE] <= 0.9))
        root = ds[ROOTZONE].where((ds[ROOTZONE] >= 0) & (ds[ROOTZONE] <= 0.9))

        surf_stats = masked_stats(surf.values, mask)
        root_stats = masked_stats(root.values, mask)

        row = {
            "district": district,
            "year": year,
            "aid": f"aid{aid:04d}",
            "source_file": path.name,
            "time_start": str(start),
            "time_end": str(end),
            "n_grid_cells_in_polygon": int(mask.sum()),

            "sm_surface_annual_mean": surf_stats["mean"],
            "sm_surface_annual_min": surf_stats["min"],
            "sm_surface_annual_max": surf_stats["max"],
            "sm_surface_annual_std": surf_stats["std"],
            "sm_surface_annual_valid_obs": surf_stats["valid_obs"],

            "sm_rootzone_annual_mean": root_stats["mean"],
            "sm_rootzone_annual_min": root_stats["min"],
            "sm_rootzone_annual_max": root_stats["max"],
            "sm_rootzone_annual_std": root_stats["std"],
            "sm_rootzone_annual_valid_obs": root_stats["valid_obs"],
        }

        row.update(
            seasonal_stats(
                surf, mask, MONSOON_MONTHS, "sm_surface_monsoon"
            )
        )
        row.update(
            seasonal_stats(
                surf, mask, KHARIF_MONTHS, "sm_surface_kharif"
            )
        )
        row.update(
            seasonal_stats(
                root, mask, MONSOON_MONTHS, "sm_rootzone_monsoon"
            )
        )
        row.update(
            seasonal_stats(
                root, mask, KHARIF_MONTHS, "sm_rootzone_kharif"
            )
        )

        return row


def main():
    mapping = load_districts()
    files = sorted(SMAP_DIR.glob("*.nc"))

    if len(files) != 56:
        raise RuntimeError(
            f"Expected 56 SMAP files for 2017-2024 x 7 districts; found {len(files)}."
        )

    # Explicit aid -> district mapping based on the submitted GeoJSON feature order.
    mapping_rows = [
        {"aid": f"aid{aid:04d}", "feature_order": aid, "district": info["district"]}
        for aid, info in mapping.items()
    ]
    pd.DataFrame(mapping_rows).to_csv(
        OUT_DIR / "SMAP_aid_district_mapping.csv", index=False
    )

    rows = []
    validation = []

    for path in files:
        aid = aid_from_filename(path)
        district = mapping.get(aid, {}).get("district", "UNKNOWN")

        with xr.open_dataset(path) as ds:
            start = ds.time.values[0]
            end = ds.time.values[-1]

            lat = np.asarray(ds.lat.values, dtype=float)
            lon = np.asarray(ds.lon.values, dtype=float)
            polygon = mapping[aid]["geometry"]
            mask = nearest_grid_cell_mask(lat, lon, polygon)

            validation.append({
                "file": path.name,
                "aid": f"aid{aid:04d}",
                "district_from_geojson_order": district,
                "year": int(start.year),
                "time_start": str(start),
                "time_end": str(end),
                "lat_min": float(lat.min()),
                "lat_max": float(lat.max()),
                "lon_min": float(lon.min()),
                "lon_max": float(lon.max()),
                "grid_cells_inside_polygon": int(mask.sum()),
            })

        rows.append(process_file(path, mapping))
        print(f"[OK] {path.name} -> {district} {rows[-1]['year']}")

    df = pd.DataFrame(rows).sort_values(["district", "year"]).reset_index(drop=True)
    val = pd.DataFrame(validation).sort_values(["year", "aid"]).reset_index(drop=True)

    # Strong structural QA.
    expected_districts = [mapping[i]["district"] for i in sorted(mapping)]
    assert sorted(df["district"].unique()) == sorted(expected_districts)
    assert sorted(df["year"].unique()) == list(range(2017, 2025))
    assert len(df) == 56
    assert not df.duplicated(["district", "year"]).any()

    # Values must remain within physical range or be NaN.
    feature_cols = [c for c in df.columns if c.startswith("sm_") and not c.endswith("valid_obs")]
    for c in feature_cols:
        bad = df[c].dropna().loc[(df[c] < 0) | (df[c] > 0.9)]
        if len(bad):
            raise RuntimeError(f"Out-of-range SMAP values found in {c}")

    df.to_csv(
        OUT_DIR / "SMAP_district_year_features_2017_2024.csv",
        index=False,
        float_format="%.8f",
    )
    val.to_csv(OUT_DIR / "SMAP_mapping_validation.csv", index=False)

    summary = {
        "files": len(files),
        "rows": len(df),
        "districts": sorted(df["district"].unique().tolist()),
        "years": sorted(df["year"].unique().tolist()),
        "duplicates": int(df.duplicated(["district", "year"]).sum()),
        "feature_count": len([c for c in df.columns if c.startswith("sm_")]),
        "aid_mapping": mapping_rows,
    }
    with open(OUT_DIR / "SMAP_extraction_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\nDONE")
    print(f"Output: {OUT_DIR / 'SMAP_district_year_features_2017_2024.csv'}")
    print(f"Rows: {len(df)}")
    print(f"Districts: {df['district'].nunique()}")
    print(f"Years: {df['year'].nunique()}")
    print(f"Duplicates: {df.duplicated(['district','year']).sum()}")


if __name__ == "__main__":
    main()
