"""
Weather Data Provenance & Observational Infrastructure Service for AgriPredict-AI.

Audits and categorizes meteorological data sources according to authentic provenance:
1. 'historical_observation': IMD gridded observation panels (1997-2024)
2. 'live_telemetry': Open-Meteo / OpenWeatherMap live AWS telemetry
3. 'climatological_average': Long-term 30-year IMD district normals
4. 'satellite_derived': NASA SMAP 9km surface & rootzone soil moisture
5. 'scenario_forecast': IPCC CMIP6 SSP2-4.5 / SSP5-8.5 future climate projections

Includes official assessment of Maharashtra Mahavedh AWS network availability.
"""

from typing import Dict, Any, List
from backend.config import MAHARASHTRA_DISTRICTS

WEATHER_PROVENANCE_CATEGORIES = {
    "historical_observation": {
        "name": "Historical Meteorological Observation Panel",
        "institution": "India Meteorological Department (IMD) Gridded Data (0.25° x 0.25°)",
        "period": "1997-2024 (28 completed seasons)",
        "is_real_data": True,
        "is_forecast": False,
        "resolution": "District-aggregated panel from daily gridded station observations",
        "description": "Ground-truth panel used for cotton yield model training and backtesting."
    },
    "live_telemetry": {
        "name": "Live Ground & Mesoscale Weather Telemetry",
        "institution": "Open-Meteo AWS Mesh / OpenWeatherMap (WMO-calibrated)",
        "period": "Real-time (updated hourly)",
        "is_real_data": True,
        "is_forecast": False,
        "resolution": "Station point coordinates / 2km grid interpolation",
        "description": "Current on-field atmospheric conditions for live advisory."
    },
    "climatological_average": {
        "name": "Climatological Long-Term Normal Baseline",
        "institution": "IMD Climatological Tables & State Agricultural Dept (30-year normal)",
        "period": "Long-term normal (1981-2010)",
        "is_real_data": True,
        "is_forecast": False,
        "resolution": "District normal benchmark",
        "description": "Baseline fallback when live telemetry is temporarily offline."
    },
    "satellite_derived": {
        "name": "Satellite Hydrological Remote Sensing",
        "institution": "NASA JPL / GSFC SMAP L4 Global Radiometer/Radar Assimilation",
        "period": "2018-2024 Kharif growing windows",
        "is_real_data": True,
        "is_forecast": False,
        "resolution": "9 km gridded microwave soil column wetting fraction",
        "description": "Used exclusively in research candidate regularized ensemble."
    },
    "scenario_forecast": {
        "name": "Coupled Model Intercomparison Project (CMIP6) Climate Scenarios",
        "institution": "IPCC WG1 / World Data Center for Climate (SSP2-4.5 & SSP5-8.5)",
        "period": "2027-2031 prospective horizons",
        "is_real_data": False,
        "is_forecast": True,
        "resolution": "Statistically downscaled Vidarbha agro-meteorological projections",
        "description": "Prospective climate stress testing; clearly tagged as non-historical simulation."
    }
}

MAHAVEDH_INTEGRATION_STATUS = {
    "network_name": "Maharashtra Agriculture Weather Information Network (Mahavedh)",
    "operating_authority": "Department of Agriculture & Maha-Agritech, Govt of Maharashtra",
    "station_count": 2065,
    "spatial_resolution": "Revenue Circle / Taluka level",
    "public_api_available": False,
    "integration_state": "credentials_required",
    "access_mechanism": "Requires official department MoU and authenticated state SFTP / API gateway token",
    "current_operational_fallback": "Open-Meteo live mesoscale telemetry + IMD district gridded normals",
    "integrity_guarantee": "AgriPredict-AI explicitly refuses to simulate fake Mahavedh live connections."
}

def get_weather_provenance_meta(provenance_type: str) -> Dict[str, Any]:
    """Retrieve full provenance metadata for a weather data source."""
    return WEATHER_PROVENANCE_CATEGORIES.get(provenance_type, {
        "name": "Unknown Weather Source",
        "institution": "Unspecified",
        "is_real_data": False,
        "is_forecast": False,
        "description": "Unregistered weather source."
    })

def audit_weather_input_provenance(data_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Audit and classify the meteorological input parameters of a prediction request."""
    district = data_payload.get("district", "Pune")
    is_scenario = data_payload.get("is_scenario", False) or "scenario" in data_payload
    is_live = data_payload.get("is_live_api", False)
    provider = data_payload.get("provider", "Unknown")

    if is_scenario:
        cat = "scenario_forecast"
    elif is_live and provider in ["Open-Meteo", "OpenWeatherMap"]:
        cat = "live_telemetry"
    elif provider == "NASA_SMAP":
        cat = "satellite_derived"
    elif "1997" in str(data_payload.get("year", "")) or (data_payload.get("target_year", 2024) <= 2024 and not is_live):
        cat = "historical_observation"
    else:
        cat = "climatological_average"

    meta = get_weather_provenance_meta(cat)
    return {
        "provenance_category": cat,
        "category_title": meta["name"],
        "source_institution": meta["institution"],
        "is_real_observational_data": meta["is_real_data"],
        "is_synthetic_or_forecast": meta["is_forecast"],
        "district": district,
        "mahavedh_status": MAHAVEDH_INTEGRATION_STATUS["integration_state"],
        "mahavedh_network_note": "Mahavedh circles available via government MoU; currently served via Open-Meteo."
    }
