import os
from dotenv import load_dotenv

from pathlib import Path
load_dotenv()

# Project & Dataset Paths
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"

CANONICAL_COTTON_DATASET_PATH = DATA_DIR / "vidarbha_cotton_model_ready_1997_2024.csv"
CANONICAL_CROP_DATASET_PATH = DATA_DIR / "raw" / "maharashtra_agri.csv"

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

# The ONLY supported crop — strictly Cotton
ALLOWED_CROPS = ["Cotton"]

# Supported Vidarbha Districts (6-district cotton prediction scope, Yavatmal excluded by design)
SUPPORTED_VIDARBHA_DISTRICTS = [
    "Akola",
    "Amravati",
    "Buldhana",
    "Nagpur",
    "Wardha",
    "Washim"
]

# Optimal Crop Parameters (Agronomic Baselines for XAI feature calculations)
CROP_AGRONOMY = {
    "Cotton": {
        "opt_temp_min": 21.0, "opt_temp_max": 35.0, "opt_temp": 28.0,
        "thermal_stress_temp": 38.0, "thermal_lethal_temp": 44.0,
        "opt_rainfall_min": 600.0, "opt_rainfall_max": 1100.0, "opt_rainfall": 800.0,
        "opt_ph_min": 6.5, "opt_ph_max": 8.2, "opt_ph": 7.4,
        "opt_nitrogen": 120.0, "opt_phosphorus": 50.0, "opt_potassium": 60.0,
        "opt_k_soil_available": 280.0,
        "opt_humidity": 65.0, "opt_moisture": 60.0,
        "base_yield_ha": 350.0, # kg per hectare average in Vidarbha
        "icon": "🌱",
        "description": "Thrives in deep black Vertisols (black cotton soil), semi-arid warm climate (21-35°C), and requires 600-1100 mm Kharif rainfall with good root drainage."
    },
    "Tomato": {
        "opt_temp_min": 18, "opt_temp_max": 30, "opt_temp": 24.0,
        "thermal_stress_temp": 38.0, "thermal_lethal_temp": 42.0,
        "opt_rainfall_min": 400, "opt_rainfall_max": 800, "opt_rainfall": 600,
        "opt_ph_min": 6.0, "opt_ph_max": 7.0, "opt_ph": 6.5,
        "opt_nitrogen": 90, "opt_phosphorus": 50, "opt_potassium": 60,
        "opt_k_soil_available": 180.0,
        "opt_humidity": 65, "opt_moisture": 60,
        "base_yield_ha": 35.0, # tonnes per hectare average
        "icon": "🍅",
        "description": "Requires well-drained loamy soil, moderate temperature (18-30°C), and controlled moisture."
    },
    "Onion": {
        "opt_temp_min": 15, "opt_temp_max": 28, "opt_temp": 22.0,
        "thermal_stress_temp": 36.0, "thermal_lethal_temp": 41.0,
        "opt_rainfall_min": 350, "opt_rainfall_max": 700, "opt_rainfall": 500,
        "opt_ph_min": 6.0, "opt_ph_max": 7.5, "opt_ph": 6.8,
        "opt_nitrogen": 70, "opt_phosphorus": 40, "opt_potassium": 50,
        "opt_k_soil_available": 150.0,
        "opt_humidity": 60, "opt_moisture": 55,
        "base_yield_ha": 25.0, # tonnes per hectare average
        "icon": "🧅",
        "description": "Thrives in mild temperatures, sandy-loam soils with good organic content and moderate irrigation."
    },
    "Sugarcane": {
        "opt_temp_min": 22, "opt_temp_max": 38, "opt_temp": 30.0,
        "thermal_stress_temp": 42.0, "thermal_lethal_temp": 45.0,
        "opt_rainfall_min": 1100, "opt_rainfall_max": 2200, "opt_rainfall": 1500,
        "opt_ph_min": 6.0, "opt_ph_max": 8.0, "opt_ph": 7.0,
        "opt_nitrogen": 140, "opt_phosphorus": 65, "opt_potassium": 90,
        "opt_k_soil_available": 260.0,
        "opt_humidity": 75, "opt_moisture": 75,
        "base_yield_ha": 85.0, # tonnes per hectare average
        "icon": "🎋",
        "description": "High water-demand crop, thrives in hot climate (25-35°C), heavy clay-loam soil with deep irrigation."
    }
}

# ===========================================================================
# Official 36-District Soil Health Card (SHC) Benchmarks
# Sourced from ICAR-NBSS&LUP, Nagpur & Department of Agriculture, Maharashtra
# Soil Fertility Atlas rating charts for available N, P2O5, and K2O.
# ===========================================================================
DISTRICT_SOIL_BENCHMARKS = {
    # 1. Vidarbha - Western & Central (Deep & Medium Black Vertisols)
    "Akola": {
        "region": "Vidarbha", "soil_type": "Deep Black Vertisol (Purna Valley)",
        "soil_ph": 7.5, "nitrogen": 160.0, "phosphorus": 22.0, "potassium": 310.0, "soil_moisture": 60.0,
        "temperature": 29.5, "rainfall": 800.0, "humidity": 68.0
    },
    "Amravati": {
        "region": "Vidarbha", "soil_type": "Deep Black Vertisol",
        "soil_ph": 7.4, "nitrogen": 165.0, "phosphorus": 24.0, "potassium": 300.0, "soil_moisture": 62.0,
        "temperature": 29.0, "rainfall": 850.0, "humidity": 70.0
    },
    "Buldhana": {
        "region": "Vidarbha", "soil_type": "Medium to Shallow Black Soil",
        "soil_ph": 7.3, "nitrogen": 150.0, "phosphorus": 20.0, "potassium": 280.0, "soil_moisture": 58.0,
        "temperature": 29.0, "rainfall": 780.0, "humidity": 65.0
    },
    "Nagpur": {
        "region": "Vidarbha", "soil_type": "Medium to Deep Black Vertisol",
        "soil_ph": 6.9, "nitrogen": 185.0, "phosphorus": 26.0, "potassium": 290.0, "soil_moisture": 65.0,
        "temperature": 29.0, "rainfall": 1090.0, "humidity": 74.0
    },
    "Wardha": {
        "region": "Vidarbha", "soil_type": "Medium Deep Black Vertisol",
        "soil_ph": 7.1, "nitrogen": 175.0, "phosphorus": 25.0, "potassium": 295.0, "soil_moisture": 63.0,
        "temperature": 29.0, "rainfall": 1050.0, "humidity": 72.0
    },
    "Washim": {
        "region": "Vidarbha", "soil_type": "Deep Black Vertisol",
        "soil_ph": 7.3, "nitrogen": 160.0, "phosphorus": 22.0, "potassium": 290.0, "soil_moisture": 60.0,
        "temperature": 29.0, "rainfall": 820.0, "humidity": 67.0
    },
    "Yavatmal": {
        "region": "Vidarbha", "soil_type": "Medium to Deep Black Vertisol",
        "soil_ph": 7.4, "nitrogen": 165.0, "phosphorus": 23.0, "potassium": 295.0, "soil_moisture": 60.0,
        "temperature": 29.5, "rainfall": 980.0, "humidity": 69.0
    },
    # 2. Eastern Vidarbha (Wainganga Basin - Mixed Alfisols / Red & Yellow Soils)
    "Bhandara": {
        "region": "Vidarbha", "soil_type": "Mixed Red & Yellow Sandy Loam (Alfisol)",
        "soil_ph": 6.5, "nitrogen": 190.0, "phosphorus": 20.0, "potassium": 190.0, "soil_moisture": 68.0,
        "temperature": 27.0, "rainfall": 1300.0, "humidity": 75.0
    },
    "Chandrapur": {
        "region": "Vidarbha", "soil_type": "Mixed Black & Sandy Loam",
        "soil_ph": 6.6, "nitrogen": 180.0, "phosphorus": 18.0, "potassium": 210.0, "soil_moisture": 65.0,
        "temperature": 30.0, "rainfall": 1250.0, "humidity": 72.0
    },
    "Gadchiroli": {
        "region": "Vidarbha", "soil_type": "Red Sandy Loam to Lateritic (Alfisol)",
        "soil_ph": 6.4, "nitrogen": 195.0, "phosphorus": 16.0, "potassium": 180.0, "soil_moisture": 70.0,
        "temperature": 28.0, "rainfall": 1420.0, "humidity": 76.0
    },
    "Gondia": {
        "region": "Vidarbha", "soil_type": "Red Sandy Loam (Alfisol)",
        "soil_ph": 6.3, "nitrogen": 190.0, "phosphorus": 17.0, "potassium": 185.0, "soil_moisture": 68.0,
        "temperature": 27.0, "rainfall": 1330.0, "humidity": 75.0
    },
    # 3. Konkan (Coastal Acidic Laterites & Red Soils)
    "Mumbai City": {
        "region": "Konkan", "soil_type": "Coastal Alluvium & Reclaimed Urban Soil",
        "soil_ph": 6.2, "nitrogen": 180.0, "phosphorus": 15.0, "potassium": 150.0, "soil_moisture": 72.0,
        "temperature": 28.0, "rainfall": 2200.0, "humidity": 80.0
    },
    "Mumbai Suburban": {
        "region": "Konkan", "soil_type": "Coastal Alluvium & Loam",
        "soil_ph": 6.2, "nitrogen": 180.0, "phosphorus": 15.0, "potassium": 150.0, "soil_moisture": 72.0,
        "temperature": 28.0, "rainfall": 2400.0, "humidity": 82.0
    },
    "Palghar": {
        "region": "Konkan", "soil_type": "Coastal Red Loam & Alluvium",
        "soil_ph": 6.1, "nitrogen": 185.0, "phosphorus": 16.0, "potassium": 155.0, "soil_moisture": 74.0,
        "temperature": 28.0, "rainfall": 2300.0, "humidity": 80.0
    },
    "Raigad": {
        "region": "Konkan", "soil_type": "Coastal Acidic Laterite Soil",
        "soil_ph": 5.9, "nitrogen": 190.0, "phosphorus": 14.0, "potassium": 145.0, "soil_moisture": 76.0,
        "temperature": 27.0, "rainfall": 3000.0, "humidity": 85.0
    },
    "Ratnagiri": {
        "region": "Konkan", "soil_type": "Strongly Acidic Lateritic Soil (Oxisol)",
        "soil_ph": 5.8, "nitrogen": 180.0, "phosphorus": 12.0, "potassium": 140.0, "soil_moisture": 78.0,
        "temperature": 27.0, "rainfall": 3300.0, "humidity": 86.0
    },
    "Sindhudurg": {
        "region": "Konkan", "soil_type": "Strongly Acidic Laterite Soil",
        "soil_ph": 5.7, "nitrogen": 185.0, "phosphorus": 11.0, "potassium": 135.0, "soil_moisture": 80.0,
        "temperature": 27.0, "rainfall": 3200.0, "humidity": 85.0
    },
    "Thane": {
        "region": "Konkan", "soil_type": "Coastal Alluvial Loam & Laterite",
        "soil_ph": 6.2, "nitrogen": 185.0, "phosphorus": 16.0, "potassium": 155.0, "soil_moisture": 74.0,
        "temperature": 28.0, "rainfall": 2500.0, "humidity": 82.0
    },
    # 4. Western Maharashtra (Medium Black & Montane Loams)
    "Ahmednagar": {
        "region": "Western Maharashtra", "soil_type": "Shallow to Medium Black Vertic Soil",
        "soil_ph": 7.2, "nitrogen": 160.0, "phosphorus": 24.0, "potassium": 270.0, "soil_moisture": 54.0,
        "temperature": 28.0, "rainfall": 560.0, "humidity": 60.0
    },
    "Kolhapur": {
        "region": "Western Maharashtra", "soil_type": "Sub-Montane Vertic Loam & Laterite Transition",
        "soil_ph": 6.4, "nitrogen": 210.0, "phosphorus": 28.0, "potassium": 230.0, "soil_moisture": 68.0,
        "temperature": 25.0, "rainfall": 1050.0, "humidity": 76.0
    },
    "Pune": {
        "region": "Western Maharashtra", "soil_type": "Medium Black Inceptisol",
        "soil_ph": 6.5, "nitrogen": 180.0, "phosphorus": 28.0, "potassium": 240.0, "soil_moisture": 58.0,
        "temperature": 27.0, "rainfall": 720.0, "humidity": 68.0
    },
    "Sangli": {
        "region": "Western Maharashtra", "soil_type": "Medium Black to Silt Loam (Krishna Basin)",
        "soil_ph": 7.0, "nitrogen": 175.0, "phosphorus": 26.0, "potassium": 260.0, "soil_moisture": 56.0,
        "temperature": 27.0, "rainfall": 620.0, "humidity": 62.0
    },
    "Satara": {
        "region": "Western Maharashtra", "soil_type": "Medium Black & Plateau Vertic Soil",
        "soil_ph": 6.6, "nitrogen": 190.0, "phosphorus": 27.0, "potassium": 245.0, "soil_moisture": 62.0,
        "temperature": 26.0, "rainfall": 890.0, "humidity": 70.0
    },
    "Solapur": {
        "region": "Western Maharashtra", "soil_type": "Shallow to Medium Calcareous Black Soil",
        "soil_ph": 7.6, "nitrogen": 145.0, "phosphorus": 20.0, "potassium": 290.0, "soil_moisture": 50.0,
        "temperature": 31.0, "rainfall": 540.0, "humidity": 55.0
    },
    # 5. Marathwada (Deep Calcareous Vertisols)
    "Chhatrapati Sambhajinagar": {
        "region": "Marathwada", "soil_type": "Medium to Deep Black Vertisol",
        "soil_ph": 7.3, "nitrogen": 155.0, "phosphorus": 22.0, "potassium": 275.0, "soil_moisture": 56.0,
        "temperature": 28.0, "rainfall": 720.0, "humidity": 64.0
    },
    "Beed": {
        "region": "Marathwada", "soil_type": "Calcareous Black Soil & Shallow Basaltic",
        "soil_ph": 7.6, "nitrogen": 145.0, "phosphorus": 19.0, "potassium": 285.0, "soil_moisture": 52.0,
        "temperature": 29.0, "rainfall": 660.0, "humidity": 58.0
    },
    "Dharashiv": {
        "region": "Marathwada", "soil_type": "Medium Black Vertisol",
        "soil_ph": 7.4, "nitrogen": 150.0, "phosphorus": 21.0, "potassium": 280.0, "soil_moisture": 54.0,
        "temperature": 28.0, "rainfall": 760.0, "humidity": 62.0
    },
    "Hingoli": {
        "region": "Marathwada", "soil_type": "Deep Black Vertisol",
        "soil_ph": 7.2, "nitrogen": 165.0, "phosphorus": 24.0, "potassium": 290.0, "soil_moisture": 60.0,
        "temperature": 28.0, "rainfall": 890.0, "humidity": 68.0
    },
    "Jalna": {
        "region": "Marathwada", "soil_type": "Medium Black Calcareous Vertisol",
        "soil_ph": 7.3, "nitrogen": 155.0, "phosphorus": 21.0, "potassium": 275.0, "soil_moisture": 56.0,
        "temperature": 29.0, "rainfall": 730.0, "humidity": 63.0
    },
    "Latur": {
        "region": "Marathwada", "soil_type": "Deep Black Vertisol",
        "soil_ph": 7.5, "nitrogen": 150.0, "phosphorus": 20.0, "potassium": 290.0, "soil_moisture": 56.0,
        "temperature": 29.0, "rainfall": 800.0, "humidity": 65.0
    },
    "Nanded": {
        "region": "Marathwada", "soil_type": "Deep Black Vertisol (Godavari Basin)",
        "soil_ph": 7.4, "nitrogen": 160.0, "phosphorus": 23.0, "potassium": 300.0, "soil_moisture": 60.0,
        "temperature": 30.0, "rainfall": 900.0, "humidity": 68.0
    },
    "Parbhani": {
        "region": "Marathwada", "soil_type": "Deep Black Vertisol (Godavari Basin)",
        "soil_ph": 7.5, "nitrogen": 155.0, "phosphorus": 22.0, "potassium": 295.0, "soil_moisture": 58.0,
        "temperature": 29.0, "rainfall": 790.0, "humidity": 65.0
    },
    # 6. Khandesh (Tapi Alluvium & Deccan Trap Volcanic Loams)
    "Dhule": {
        "region": "Khandesh", "soil_type": "Medium Black Silt Loam",
        "soil_ph": 7.1, "nitrogen": 160.0, "phosphorus": 23.0, "potassium": 265.0, "soil_moisture": 54.0,
        "temperature": 29.0, "rainfall": 600.0, "humidity": 58.0
    },
    "Jalgaon": {
        "region": "Khandesh", "soil_type": "Tapi Alluvial Deep Black Vertisol",
        "soil_ph": 7.4, "nitrogen": 170.0, "phosphorus": 26.0, "potassium": 310.0, "soil_moisture": 58.0,
        "temperature": 31.0, "rainfall": 690.0, "humidity": 62.0
    },
    "Nandurbar": {
        "region": "Khandesh", "soil_type": "Medium Black & Undulating Hilly Soil",
        "soil_ph": 6.8, "nitrogen": 165.0, "phosphorus": 21.0, "potassium": 240.0, "soil_moisture": 58.0,
        "temperature": 30.0, "rainfall": 860.0, "humidity": 66.0
    },
    "Nashik": {
        "region": "Khandesh", "soil_type": "Deccan Trap Volcanic Loam & River Alluvium",
        "soil_ph": 6.7, "nitrogen": 185.0, "phosphorus": 30.0, "potassium": 255.0, "soil_moisture": 62.0,
        "temperature": 26.0, "rainfall": 810.0, "humidity": 68.0
    }
}

# Authentic Taluka Registry for Maharashtra Districts (Administrative Validation)
DISTRICT_TALUKAS = {
    # Vidarbha Research Districts
    "Akola": ["Akola", "Akot", "Balapur", "Barshitakli", "Murtizapur", "Patur", "Telhara"],
    "Amravati": ["Achalpur", "Amravati", "Anjangaon Surji", "Bhatkuli", "Chandur Railway", "Chandurbazar", "Chikhaldara", "Daryapur", "Dhamangaon Railway", "Morshi", "Nandgaon Khandeshwar", "Teosa", "Warud"],
    "Buldhana": ["Buldhana", "Chikhli", "Deulgaon Raja", "Jalgaon Jamod", "Khamgaon", "Lonar", "Malkapur", "Motala", "Nandura", "Sangrampur", "Shegaon", "Sindkhed Raja"],
    "Nagpur": ["Bhiwapur", "Hingna", "Kalameshwar", "Kamptee", "Katol", "Kuhi", "Mouda", "Nagpur Rural", "Nagpur Urban", "Narkhed", "Parseoni", "Ramtek", "Saoner", "Umred"],
    "Wardha": ["Arvi", "Ashti", "Deoli", "Hinganghat", "Karanja", "Samudrapur", "Seloo", "Wardha"],
    "Washim": ["Karanja", "Malegaon", "Mangrulpir", "Manora", "Risod", "Washim"],
    "Yavatmal": ["Arni", "Babhulgaon", "Darwha", "Digras", "Ghatanji", "Kalamb", "Mahagaon", "Maregaon", "Ner", "Pandharkawada", "Pusad", "Ralegaon", "Umarkhed", "Wani", "Yavatmal", "Zari Jamani"],
    "Bhandara": ["Bhandara", "Mohadi", "Tumsar", "Pauni", "Sakoli", "Lakhani", "Lakhandur"],
    "Chandrapur": ["Chandrapur", "Bhadravati", "Warora", "Chimur", "Nagbhid", "Bramhapuri", "Sindewahi", "Mul", "Saoli", "Pombhurna", "Ballarpur", "Korpana", "Rajura", "Jivati", "Gondpipri"],
    "Gadchiroli": ["Gadchiroli", "Dhanora", "Chamorshi", "Armori", "Kurkheda", "Korchi", "Wadsa", "Aheri", "Etapalli", "Bhamragad", "Sironcha", "Mulchera"],
    "Gondia": ["Gondia", "Tirora", "Goregaon", "Arjuni Morgaon", "Deori", "Salekasa", "Sadak Arjuni", "Amgaon"],

    # Western Maharashtra
    "Pune": ["Ambegaon", "Baramati", "Bhor", "Daund", "Haveli", "Indapur", "Junnar", "Khed", "Maval", "Mulshi", "Pune City", "Purandar", "Shirur", "Velhe"],
    "Ahmednagar": ["Akole", "Jamkhed", "Karjat", "Kopargaon", "Nagar", "Nevasa", "Parner", "Pathardi", "Rahata", "Rahuri", "Sangamner", "Shevgaon", "Shrigonda", "Shrirampur"],
    "Kolhapur": ["Ajra", "Bavda", "Bhudargad", "Chandgad", "Gadhinglaj", "Hatkanangle", "Kagal", "Karvir", "Panhala", "Radhanagari", "Shahuwadi", "Shirol"],
    "Sangli": ["Atpadi", "Jat", "Kadegaon", "Kavathe Mahankal", "Khanapur", "Miraj", "Palus", "Shirala", "Tasgaon", "Walwa"],
    "Satara": ["Jaoli", "Karad", "Khandala", "Khatav", "Koregaon", "Mahabaleshwar", "Man", "Patan", "Phaltan", "Satara", "Wai"],
    "Solapur": ["Akkalkot", "Barshi", "Karmala", "Madha", "Malshiras", "Mangalvedhe", "Mohol", "Pandharpur", "Sangole", "Solapur North", "Solapur South"],

    # Marathwada
    "Chhatrapati Sambhajinagar": ["Aurangabad", "Kannad", "Khuldabad", "Gangapur", "Vaijapur", "Paithan", "Phulambri", "Sillod", "Soegaon"],
    "Beed": ["Ambajogai", "Ashti", "Beed", "Dharur", "Georai", "Kaij", "Majalgaon", "Parli", "Patoda", "Shirur Kasar", "Wadwani"],
    "Dharashiv": ["Bhoom", "Kalamb", "Lohara", "Omerga", "Osmanabad", "Paranda", "Tuljapur", "Washi"],
    "Hingoli": ["Aundha Nagnath", "Basmath", "Hingoli", "Kalamnuri", "Sengaon"],
    "Jalna": ["Ambad", "Badnapur", "Bhokardan", "Ghansawangi", "Jafrabad", "Jalna", "Mantha", "Partur"],
    "Latur": ["Ahmedpur", "Ausa", "Chakur", "Deoni", "Jalkot", "Latur", "Nilanga", "Renapur", "Shirur Anantpal", "Udgir"],
    "Nanded": ["Ardhapur", "Bhokar", "Biloli", "Deglur", "Dharmabad", "Hadgaon", "Himayatnagar", "Kandhar", "Kinwat", "Loha", "Mahur", "Mudkhed", "Mukhed", "Naigaon", "Nanded", "Umri"],
    "Parbhani": ["Gangakhed", "Jintur", "Manwath", "Palam", "Parbhani", "Pathri", "Purna", "Sailu", "Sonpeth"],

    # Khandesh
    "Dhule": ["Dhule", "Sakri", "Shirpur", "Sindkheda"],
    "Jalgaon": ["Amalner", "Bhadgaon", "Bhusawal", "Bodwad", "Chalisgaon", "Chopda", "Dharangaon", "Erandol", "Jalgaon", "Jamner", "Muktainagar", "Pachora", "Parola", "Raver", "Yawal"],
    "Nandurbar": ["Akkalkuwa", "Akrani", "Dhadgaon", "Nandurbar", "Nawapur", "Shahada", "Taloda"],
    "Nashik": ["Baglan", "Chandwad", "Deola", "Dindori", "Igatpuri", "Kalwan", "Malegaon", "Nandgaon", "Nashik", "Niphad", "Peint", "Sinnar", "Surgana", "Trimbakeshwar", "Yevala"],

    # Konkan
    "Mumbai City": ["Mumbai City"],
    "Mumbai Suburban": ["Kurla", "Andheri", "Borivali"],
    "Palghar": ["Dahanu", "Jawhar", "Mokhada", "Palghar", "Talasari", "Vada", "Vikramgad", "Vasai"],
    "Raigad": ["Alibag", "Karjat", "Khalapur", "Mahad", "Mangaon", "Mhasla", "Murud", "Panvel", "Pen", "Poladpur", "Roha", "Shrivardhan", "Sudhagad", "Tala", "Uran"],
    "Ratnagiri": ["Chiplun", "Dapoli", "Guhagar", "Khed", "Lanja", "Mandangad", "Ratnagiri", "Rajapur", "Sangameshwar"],
    "Sindhudurg": ["Devgad", "Dodamarg", "Kankavli", "Kudal", "Malwan", "Sawantwadi", "Vaibhavwadi", "Vengurla"],
    "Thane": ["Ambarnath", "Bhiwandi", "Kalyan", "Murbad", "Shahapur", "Thane", "Ulhasnagar"]
}

# Unit Conversion Factors & Agronomic Constants
# Agronomic note on 2.24 vs 2.00:
# In metric furrow slice (10,000 m2 * 0.15 m depth * 1330 kg/m3 bulk density = 2,000,000 kg soil/ha),
# 1 mg/kg (ppm) corresponds exactly to 2.0 kg/ha.
# The traditional 2.24 multiplier originated from US imperial acre furrow slice (2,000,000 lbs/acre),
# where 1 ppm = 2 lbs/acre = 2.2417 kg/ha.
PPM_TO_KG_PER_HA_METRIC = 2.00
PPM_TO_KG_PER_HA_IMPERIAL = 2.24
PPM_TO_KG_PER_HA = 2.24  # Maintained at 2.24 for backwards-compatibility with existing benchmarks

# Oxide to Elemental conversion factors (ICAR / AOAC standard stoichiometry)
P2O5_TO_P = 0.4364
P_TO_P2O5 = 2.2914
K2O_TO_K = 0.8302
K_TO_K2O = 1.2046

QUINTAL_PER_ACRE_TO_KG_PER_HA = 247.105
QUINTAL_PER_ACRE_TO_TONNES_PER_HA = 0.247105
TONNES_PER_HA_TO_KG_PER_HA = 1000.0

# Crop biological duration limits (in days from sowing/transplanting to final harvest)
# Sourced from ICAR, MPKV Rahuri, PDKV Akola agronomic crop production guides
CROP_GROWTH_DURATION_DAYS = {
    "Cotton": {"min_days": 120, "max_days": 240, "typical_days": 160},
    "Tomato": {"min_days": 70, "max_days": 160, "typical_days": 110},
    "Onion": {"min_days": 80, "max_days": 170, "typical_days": 125},
    "Sugarcane": {"min_days": 270, "max_days": 550, "typical_days": 365}
}

# Secret salt for anonymous HMAC farm ID hashing (prevents rainbow-table inversion of phone/7-12 survey IDs)
FARM_ID_HMAC_SALT = os.getenv("AGRIPREDICT_FARM_SALT", "AgriPredict_MahaAgri_Salt_2026_Secure_Field_Audit")

