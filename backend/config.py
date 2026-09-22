import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "demo_weather_key")
WEATHER_API_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Maharashtra Districts Metadata (36 Districts)
MAHARASHTRA_DISTRICTS = {
    "Ahmednagar": {"lat": 19.0948, "lon": 74.7480, "region": "Western Maharashtra", "avg_rainfall": 560},
    "Akola": {"lat": 20.7002, "lon": 77.0082, "region": "Vidarbha", "avg_rainfall": 800},
    "Amravati": {"lat": 20.9374, "lon": 77.7796, "region": "Vidarbha", "avg_rainfall": 850},
    "Chhatrapati Sambhajinagar": {"lat": 19.8762, "lon": 75.3433, "region": "Marathwada", "avg_rainfall": 720},
    "Beed": {"lat": 18.9891, "lon": 75.7601, "region": "Marathwada", "avg_rainfall": 660},
    "Bhandara": {"lat": 21.1764, "lon": 79.6547, "region": "Vidarbha", "avg_rainfall": 1300},
    "Buldhana": {"lat": 20.5293, "lon": 76.1844, "region": "Vidarbha", "avg_rainfall": 780},
    "Chandrapur": {"lat": 19.9615, "lon": 79.2961, "region": "Vidarbha", "avg_rainfall": 1250},
    "Dhule": {"lat": 20.9042, "lon": 74.7749, "region": "Khandesh", "avg_rainfall": 600},
    "Gadchiroli": {"lat": 20.1849, "lon": 79.9946, "region": "Vidarbha", "avg_rainfall": 1420},
    "Gondia": {"lat": 21.4624, "lon": 80.1961, "region": "Vidarbha", "avg_rainfall": 1330},
    "Hingoli": {"lat": 19.7196, "lon": 77.1477, "region": "Marathwada", "avg_rainfall": 890},
    "Jalgaon": {"lat": 21.0077, "lon": 75.5626, "region": "Khandesh", "avg_rainfall": 690},
    "Jalna": {"lat": 19.8410, "lon": 75.8864, "region": "Marathwada", "avg_rainfall": 730},
    "Kolhapur": {"lat": 16.7050, "lon": 74.2433, "region": "Western Maharashtra", "avg_rainfall": 1050},
    "Latur": {"lat": 18.4088, "lon": 76.5604, "region": "Marathwada", "avg_rainfall": 800},
    "Mumbai City": {"lat": 18.9388, "lon": 72.8353, "region": "Konkan", "avg_rainfall": 2200},
    "Mumbai Suburban": {"lat": 19.1176, "lon": 72.8481, "region": "Konkan", "avg_rainfall": 2400},
    "Nagpur": {"lat": 21.1458, "lon": 79.0882, "region": "Vidarbha", "avg_rainfall": 1090},
    "Nanded": {"lat": 19.1383, "lon": 77.3210, "region": "Marathwada", "avg_rainfall": 900},
    "Nandurbar": {"lat": 21.3713, "lon": 74.2409, "region": "Khandesh", "avg_rainfall": 860},
    "Nashik": {"lat": 19.9975, "lon": 73.7898, "region": "Khandesh", "avg_rainfall": 810},
    "Dharashiv": {"lat": 18.1861, "lon": 76.0419, "region": "Marathwada", "avg_rainfall": 760},
    "Palghar": {"lat": 19.6967, "lon": 72.7699, "region": "Konkan", "avg_rainfall": 2300},
    "Parbhani": {"lat": 19.2608, "lon": 76.7749, "region": "Marathwada", "avg_rainfall": 790},
    "Pune": {"lat": 18.5204, "lon": 73.8567, "region": "Western Maharashtra", "avg_rainfall": 720},
    "Raigad": {"lat": 18.5158, "lon": 73.1822, "region": "Konkan", "avg_rainfall": 3000},
    "Ratnagiri": {"lat": 16.9902, "lon": 73.3120, "region": "Konkan", "avg_rainfall": 3300},
    "Sangli": {"lat": 16.8524, "lon": 74.5815, "region": "Western Maharashtra", "avg_rainfall": 620},
    "Satara": {"lat": 17.6805, "lon": 74.0183, "region": "Western Maharashtra", "avg_rainfall": 890},
    "Sindhudurg": {"lat": 16.1246, "lon": 73.6669, "region": "Konkan", "avg_rainfall": 3200},
    "Solapur": {"lat": 17.6599, "lon": 75.9064, "region": "Western Maharashtra", "avg_rainfall": 540},
    "Thane": {"lat": 19.2183, "lon": 72.9781, "region": "Konkan", "avg_rainfall": 2500},
    "Wardha": {"lat": 20.7453, "lon": 78.6022, "region": "Vidarbha", "avg_rainfall": 1050},
    "Washim": {"lat": 20.1042, "lon": 77.1332, "region": "Vidarbha", "avg_rainfall": 820},
    "Yavatmal": {"lat": 20.3888, "lon": 78.1311, "region": "Vidarbha", "avg_rainfall": 980}
}

# The ONLY 3 supported crops
ALLOWED_CROPS = ["Tomato", "Onion", "Sugarcane"]

# Optimal Crop Parameters (Agronomic Baselines for XAI feature calculations)
CROP_AGRONOMY = {
    "Tomato": {
        "opt_temp_min": 18, "opt_temp_max": 30, "opt_temp": 24.0,
        "opt_rainfall_min": 400, "opt_rainfall_max": 800, "opt_rainfall": 600,
        "opt_ph_min": 6.0, "opt_ph_max": 7.0, "opt_ph": 6.5,
        "opt_nitrogen": 90, "opt_phosphorus": 50, "opt_potassium": 60,
        "opt_humidity": 65, "opt_moisture": 60,
        "base_yield_ha": 35.0, # tonnes per hectare average
        "icon": "🍅",
        "description": "Requires well-drained loamy soil, moderate temperature (18-30°C), and controlled moisture."
    },
    "Onion": {
        "opt_temp_min": 15, "opt_temp_max": 28, "opt_temp": 22.0,
        "opt_rainfall_min": 350, "opt_rainfall_max": 700, "opt_rainfall": 500,
        "opt_ph_min": 6.0, "opt_ph_max": 7.5, "opt_ph": 6.8,
        "opt_nitrogen": 70, "opt_phosphorus": 40, "opt_potassium": 50,
        "opt_humidity": 60, "opt_moisture": 55,
        "base_yield_ha": 25.0, # tonnes per hectare average
        "icon": "🧅",
        "description": "Thrives in mild temperatures, sandy-loam soils with good organic content and moderate irrigation."
    },
    "Sugarcane": {
        "opt_temp_min": 22, "opt_temp_max": 38, "opt_temp": 30.0,
        "opt_rainfall_min": 1100, "opt_rainfall_max": 2200, "opt_rainfall": 1500,
        "opt_ph_min": 6.0, "opt_ph_max": 8.0, "opt_ph": 7.0,
        "opt_nitrogen": 140, "opt_phosphorus": 65, "opt_potassium": 90,
        "opt_humidity": 75, "opt_moisture": 75,
        "base_yield_ha": 85.0, # tonnes per hectare average
        "icon": "🎋",
        "description": "High water-demand crop, thrives in hot climate (25-35°C), heavy clay-loam soil with deep irrigation."
    }
}
