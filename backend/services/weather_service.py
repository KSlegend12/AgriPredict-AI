import httpx
from backend.config import WEATHER_API_KEY, WEATHER_API_BASE_URL, MAHARASHTRA_DISTRICTS

def _resolve_district(name: str):
    cleaned = name.strip()
    for d in MAHARASHTRA_DISTRICTS:
        if d.lower() == cleaned.lower():
            return d, MAHARASHTRA_DISTRICTS[d]
    aliases = {
        "aurangabad": "Chhatrapati Sambhajinagar",
        "osmanabad": "Dharashiv",
    }
    if cleaned.lower() in aliases:
        canonical = aliases[cleaned.lower()]
        return canonical, MAHARASHTRA_DISTRICTS[canonical]
    # Default fallback to Pune if unknown
    return "Pune", MAHARASHTRA_DISTRICTS["Pune"]

async def fetch_district_weather(district_name: str):
    canonical_district, dist_info = _resolve_district(district_name)
    lat = dist_info["lat"]
    lon = dist_info["lon"]
    region = dist_info.get("region", "Vidarbha")
    avg_rain = float(dist_info.get("avg_rainfall", 800.0))

    if WEATHER_API_KEY and WEATHER_API_KEY != "demo_weather_key":
        try:
            url = f"{WEATHER_API_BASE_URL}/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    live_precip = float(data.get("rain", {}).get("1h", 0.0))
                    return {
                        "district": canonical_district,
                        "region": region,
                        "temperature": round(data["main"]["temp"], 1),
                        "feels_like": round(data["main"]["feels_like"], 1),
                        "humidity": data["main"]["humidity"],
                        "rainfall": round(avg_rain, 1),
                        "precipitation_live_mm": live_precip,
                        "wind_speed": round(data["wind"]["speed"] * 3.6, 1),  # m/s to km/h
                        "condition": data["weather"][0]["main"],
                        "description": data["weather"][0]["description"].title(),
                        "is_live_api": True,
                        "provider": "OpenWeatherMap"
                    }
        except Exception as e:
            print(f"OpenWeather API call failed: {e}. Trying free Open-Meteo fallback.")

    # High-accuracy live weather fallback via Open-Meteo (no API key required)
    try:
        open_meteo_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m,weather_code"
        )
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.get(open_meteo_url)
            if res.status_code == 200:
                cur = res.json().get("current", {})
                w_code = cur.get("weather_code", 0)
                condition = "Clear" if w_code <= 1 else ("Partly Cloudy" if w_code <= 3 else "Rain")
                live_precip = round(float(cur.get("precipitation", 0.0)), 1)
                return {
                    "district": canonical_district,
                    "region": region,
                    "temperature": round(cur.get("temperature_2m", 28.0), 1),
                    "feels_like": round(cur.get("apparent_temperature", cur.get("temperature_2m", 28.0)), 1),
                    "humidity": int(cur.get("relative_humidity_2m", 60)),
                    "rainfall": round(avg_rain, 1),
                    "precipitation_live_mm": live_precip,
                    "wind_speed": round(cur.get("wind_speed_10m", 10.0), 1),
                    "condition": condition,
                    "description": f"Live telemetry ({condition})",
                    "is_live_api": True,
                    "provider": "Open-Meteo"
                }
    except Exception as e:
        # Gracefully fall back to regional climatology if offline
        pass

    # Deterministic climatological baseline for Maharashtra districts
    base_temp = 28.0 if region == "Vidarbha" else (26.0 if region == "Western Maharashtra" else 29.0)
    base_hum = 68 if region == "Konkan" else (62 if region == "Western Maharashtra" else 58)
    soil_m = 62 if region == "Konkan" else (60 if region == "Vidarbha" else 56)
    soil_p = 6.5 if region == "Western Maharashtra" else (7.4 if region == "Vidarbha" else 7.2)

    return {
        "district": canonical_district,
        "region": region,
        "temperature": round(base_temp, 1),
        "feels_like": round(base_temp + 1.2, 1),
        "humidity": base_hum,
        "rainfall": round(avg_rain, 1),
        "precipitation_live_mm": 0.0,
        "wind_speed": 12.0,
        "soil_moisture": soil_m,
        "soil_ph": soil_p,
        "condition": "Partly Cloudy",
        "description": "Favorable agricultural weather condition (climatological baseline)",
        "is_live_api": False,
        "provider": "Maharashtra Climatology Baseline"
    }
