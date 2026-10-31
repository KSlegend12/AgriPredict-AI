export const MAHARASHTRA_DISTRICTS = [
  { name: "Ahmednagar", region: "Western Maharashtra", avg_rainfall: 560, soil_ph: 7.2, temp: 28 },
  { name: "Akola", region: "Vidarbha", avg_rainfall: 800, soil_ph: 7.5, temp: 30 },
  { name: "Amravati", region: "Vidarbha", avg_rainfall: 850, soil_ph: 7.4, temp: 29 },
  { name: "Chhatrapati Sambhajinagar", region: "Marathwada", avg_rainfall: 720, soil_ph: 7.3, temp: 28 },
  { name: "Beed", region: "Marathwada", avg_rainfall: 660, soil_ph: 7.6, temp: 29 },
  { name: "Bhandara", region: "Vidarbha", avg_rainfall: 1300, soil_ph: 6.5, temp: 27 },
  { name: "Buldhana", region: "Vidarbha", avg_rainfall: 780, soil_ph: 7.3, temp: 29 },
  { name: "Chandrapur", region: "Vidarbha", avg_rainfall: 1250, soil_ph: 6.6, temp: 30 },
  { name: "Dhule", region: "Khandesh", avg_rainfall: 600, soil_ph: 7.1, temp: 29 },
  { name: "Gadchiroli", region: "Vidarbha", avg_rainfall: 1420, soil_ph: 6.4, temp: 28 },
  { name: "Gondia", region: "Vidarbha", avg_rainfall: 1330, soil_ph: 6.3, temp: 27 },
  { name: "Hingoli", region: "Marathwada", avg_rainfall: 890, soil_ph: 7.2, temp: 28 },
  { name: "Jalgaon", region: "Khandesh", avg_rainfall: 690, soil_ph: 7.4, temp: 31 },
  { name: "Jalna", region: "Marathwada", avg_rainfall: 730, soil_ph: 7.3, temp: 29 },
  { name: "Kolhapur", region: "Western Maharashtra", avg_rainfall: 1050, soil_ph: 6.4, temp: 25 },
  { name: "Latur", region: "Marathwada", avg_rainfall: 800, soil_ph: 7.5, temp: 29 },
  { name: "Mumbai City", region: "Konkan", avg_rainfall: 2200, soil_ph: 6.2, temp: 28 },
  { name: "Mumbai Suburban", region: "Konkan", avg_rainfall: 2400, soil_ph: 6.2, temp: 28 },
  { name: "Nagpur", region: "Vidarbha", avg_rainfall: 1090, soil_ph: 6.9, temp: 29 },
  { name: "Nanded", region: "Marathwada", avg_rainfall: 900, soil_ph: 7.4, temp: 30 },
  { name: "Nandurbar", region: "Khandesh", avg_rainfall: 860, soil_ph: 6.8, temp: 30 },
  { name: "Nashik", region: "Khandesh", avg_rainfall: 810, soil_ph: 6.7, temp: 26 },
  { name: "Dharashiv", region: "Marathwada", avg_rainfall: 760, soil_ph: 7.4, temp: 28 },
  { name: "Palghar", region: "Konkan", avg_rainfall: 2300, soil_ph: 6.1, temp: 28 },
  { name: "Parbhani", region: "Marathwada", avg_rainfall: 790, soil_ph: 7.5, temp: 29 },
  { name: "Pune", region: "Western Maharashtra", avg_rainfall: 720, soil_ph: 6.5, temp: 27 },
  { name: "Raigad", region: "Konkan", avg_rainfall: 3000, soil_ph: 5.9, temp: 27 },
  { name: "Ratnagiri", region: "Konkan", avg_rainfall: 3300, soil_ph: 5.8, temp: 27 },
  { name: "Sangli", region: "Western Maharashtra", avg_rainfall: 620, soil_ph: 7.0, temp: 27 },
  { name: "Satara", region: "Western Maharashtra", avg_rainfall: 890, soil_ph: 6.6, temp: 26 },
  { name: "Sindhudurg", region: "Konkan", avg_rainfall: 3200, soil_ph: 5.7, temp: 27 },
  { name: "Solapur", region: "Western Maharashtra", avg_rainfall: 540, soil_ph: 7.6, temp: 31 },
  { name: "Thane", region: "Konkan", avg_rainfall: 2500, soil_ph: 6.2, temp: 28 },
  { name: "Wardha", region: "Vidarbha", avg_rainfall: 1050, soil_ph: 7.1, temp: 29 },
  { name: "Washim", region: "Vidarbha", avg_rainfall: 820, soil_ph: 7.3, temp: 29 },
  { name: "Yavatmal", region: "Vidarbha", avg_rainfall: 980, soil_ph: 7.4, temp: 29.5 }
];

export {
  SUPPORTED_VIDARBHA_DISTRICTS,
  VIDARBHA_DISTRICTS,
  DEFAULT_DISTRICT,
  isValidDistrict,
  sanitizeDistrict,
} from '../constants/districts';

export const ALLOWED_CROPS = [
  { name: "Cotton", icon: "🌱", color: "from-emerald-600 to-teal-700", border: "border-emerald-200", bg: "bg-emerald-50" }
];

export const SEASONS = ["Kharif", "Rabi", "Summer"];

// Comprehensive 36-District Soil Health Card Benchmarks (ICAR-NBSS&LUP & Dept of Agriculture)
export const DISTRICT_SOIL_BENCHMARKS = {
  // 1. Vidarbha - Western & Central (Deep & Medium Black Vertisols)
  Akola: { temperature: 29.5, rainfall: 800.0, humidity: 68.0, soil_ph: 7.5, nitrogen: 160.0, phosphorus: 22.0, potassium: 310.0, soil_moisture: 60.0, soil_type: "Deep Black Vertisol (Purna Valley)", region: "Vidarbha" },
  Amravati: { temperature: 29.0, rainfall: 850.0, humidity: 70.0, soil_ph: 7.4, nitrogen: 165.0, phosphorus: 24.0, potassium: 300.0, soil_moisture: 62.0, soil_type: "Deep Black Vertisol", region: "Vidarbha" },
  Buldhana: { temperature: 29.0, rainfall: 780.0, humidity: 65.0, soil_ph: 7.3, nitrogen: 150.0, phosphorus: 20.0, potassium: 280.0, soil_moisture: 58.0, soil_type: "Medium to Shallow Black Soil", region: "Vidarbha" },
  Nagpur: { temperature: 29.0, rainfall: 1090.0, humidity: 74.0, soil_ph: 6.9, nitrogen: 185.0, phosphorus: 26.0, potassium: 290.0, soil_moisture: 65.0, soil_type: "Medium to Deep Black Vertisol", region: "Vidarbha" },
  Wardha: { temperature: 29.0, rainfall: 1050.0, humidity: 72.0, soil_ph: 7.1, nitrogen: 175.0, phosphorus: 25.0, potassium: 295.0, soil_moisture: 63.0, soil_type: "Medium Deep Black Vertisol", region: "Vidarbha" },
  Washim: { temperature: 29.0, rainfall: 820.0, humidity: 67.0, soil_ph: 7.3, nitrogen: 160.0, phosphorus: 22.0, potassium: 290.0, soil_moisture: 60.0, soil_type: "Deep Black Vertisol", region: "Vidarbha" },
  Yavatmal: { temperature: 29.5, rainfall: 980.0, humidity: 69.0, soil_ph: 7.4, nitrogen: 165.0, phosphorus: 23.0, potassium: 295.0, soil_moisture: 60.0, soil_type: "Medium to Deep Black Vertisol", region: "Vidarbha" },

  // 2. Eastern Vidarbha (Wainganga Basin - Mixed Alfisols / Red & Yellow Soils)
  Bhandara: { temperature: 27.0, rainfall: 1300.0, humidity: 75.0, soil_ph: 6.5, nitrogen: 190.0, phosphorus: 20.0, potassium: 190.0, soil_moisture: 68.0, soil_type: "Mixed Red & Yellow Sandy Loam (Alfisol)", region: "Vidarbha" },
  Chandrapur: { temperature: 30.0, rainfall: 1250.0, humidity: 72.0, soil_ph: 6.6, nitrogen: 180.0, phosphorus: 18.0, potassium: 210.0, soil_moisture: 65.0, soil_type: "Mixed Black & Sandy Loam", region: "Vidarbha" },
  Gadchiroli: { temperature: 28.0, rainfall: 1420.0, humidity: 76.0, soil_ph: 6.4, nitrogen: 195.0, phosphorus: 16.0, potassium: 180.0, soil_moisture: 70.0, soil_type: "Red Sandy Loam to Lateritic (Alfisol)", region: "Vidarbha" },
  Gondia: { temperature: 27.0, rainfall: 1330.0, humidity: 75.0, soil_ph: 6.3, nitrogen: 190.0, phosphorus: 17.0, potassium: 185.0, soil_moisture: 68.0, soil_type: "Red Sandy Loam (Alfisol)", region: "Vidarbha" },

  // 3. Konkan (Coastal Acidic Laterites & Red Soils)
  "Mumbai City": { temperature: 28.0, rainfall: 2200.0, humidity: 80.0, soil_ph: 6.2, nitrogen: 180.0, phosphorus: 15.0, potassium: 150.0, soil_moisture: 72.0, soil_type: "Coastal Alluvium & Reclaimed Urban Soil", region: "Konkan" },
  "Mumbai Suburban": { temperature: 28.0, rainfall: 2400.0, humidity: 82.0, soil_ph: 6.2, nitrogen: 180.0, phosphorus: 15.0, potassium: 150.0, soil_moisture: 72.0, soil_type: "Coastal Alluvium & Loam", region: "Konkan" },
  Palghar: { temperature: 28.0, rainfall: 2300.0, humidity: 80.0, soil_ph: 6.1, nitrogen: 185.0, phosphorus: 16.0, potassium: 155.0, soil_moisture: 74.0, soil_type: "Coastal Red Loam & Alluvium", region: "Konkan" },
  Raigad: { temperature: 27.0, rainfall: 3000.0, humidity: 85.0, soil_ph: 5.9, nitrogen: 190.0, phosphorus: 14.0, potassium: 145.0, soil_moisture: 76.0, soil_type: "Coastal Acidic Laterite Soil", region: "Konkan" },
  Ratnagiri: { temperature: 27.0, rainfall: 3300.0, humidity: 86.0, soil_ph: 5.8, nitrogen: 180.0, phosphorus: 12.0, potassium: 140.0, soil_moisture: 78.0, soil_type: "Strongly Acidic Lateritic Soil (Oxisol)", region: "Konkan" },
  Sindhudurg: { temperature: 27.0, rainfall: 3200.0, humidity: 85.0, soil_ph: 5.7, nitrogen: 185.0, phosphorus: 11.0, potassium: 135.0, soil_moisture: 80.0, soil_type: "Strongly Acidic Laterite Soil", region: "Konkan" },
  Thane: { temperature: 28.0, rainfall: 2500.0, humidity: 82.0, soil_ph: 6.2, nitrogen: 185.0, phosphorus: 16.0, potassium: 155.0, soil_moisture: 74.0, soil_type: "Coastal Alluvial Loam & Laterite", region: "Konkan" },

  // 4. Western Maharashtra (Medium Black & Montane Loams)
  Ahmednagar: { temperature: 28.0, rainfall: 560.0, humidity: 60.0, soil_ph: 7.2, nitrogen: 160.0, phosphorus: 24.0, potassium: 270.0, soil_moisture: 54.0, soil_type: "Shallow to Medium Black Vertic Soil", region: "Western Maharashtra" },
  Kolhapur: { temperature: 25.0, rainfall: 1050.0, humidity: 76.0, soil_ph: 6.4, nitrogen: 210.0, phosphorus: 28.0, potassium: 230.0, soil_moisture: 68.0, soil_type: "Sub-Montane Vertic Loam & Laterite Transition", region: "Western Maharashtra" },
  Pune: { temperature: 27.0, rainfall: 720.0, humidity: 68.0, soil_ph: 6.5, nitrogen: 180.0, phosphorus: 28.0, potassium: 240.0, soil_moisture: 58.0, soil_type: "Medium Black Inceptisol", region: "Western Maharashtra" },
  Sangli: { temperature: 27.0, rainfall: 620.0, humidity: 62.0, soil_ph: 7.0, nitrogen: 175.0, phosphorus: 26.0, potassium: 260.0, soil_moisture: 56.0, soil_type: "Medium Black to Silt Loam (Krishna Basin)", region: "Western Maharashtra" },
  Satara: { temperature: 26.0, rainfall: 890.0, humidity: 70.0, soil_ph: 6.6, nitrogen: 190.0, phosphorus: 27.0, potassium: 245.0, soil_moisture: 62.0, soil_type: "Medium Black & Plateau Vertic Soil", region: "Western Maharashtra" },
  Solapur: { temperature: 31.0, rainfall: 540.0, humidity: 55.0, soil_ph: 7.6, nitrogen: 145.0, phosphorus: 20.0, potassium: 290.0, soil_moisture: 50.0, soil_type: "Shallow to Medium Calcareous Black Soil", region: "Western Maharashtra" },

  // 5. Marathwada (Deep Calcareous Vertisols)
  "Chhatrapati Sambhajinagar": { temperature: 28.0, rainfall: 720.0, humidity: 64.0, soil_ph: 7.3, nitrogen: 155.0, phosphorus: 22.0, potassium: 275.0, soil_moisture: 56.0, soil_type: "Medium to Deep Black Vertisol", region: "Marathwada" },
  Beed: { temperature: 29.0, rainfall: 660.0, humidity: 58.0, soil_ph: 7.6, nitrogen: 145.0, phosphorus: 19.0, potassium: 285.0, soil_moisture: 52.0, soil_type: "Calcareous Black Soil & Shallow Basaltic", region: "Marathwada" },
  Dharashiv: { temperature: 28.0, rainfall: 760.0, humidity: 62.0, soil_ph: 7.4, nitrogen: 150.0, phosphorus: 21.0, potassium: 280.0, soil_moisture: 54.0, soil_type: "Medium Black Vertisol", region: "Marathwada" },
  Hingoli: { temperature: 28.0, rainfall: 890.0, humidity: 68.0, soil_ph: 7.2, nitrogen: 165.0, phosphorus: 24.0, potassium: 290.0, soil_moisture: 60.0, soil_type: "Deep Black Vertisol", region: "Marathwada" },
  Jalna: { temperature: 29.0, rainfall: 730.0, humidity: 63.0, soil_ph: 7.3, nitrogen: 155.0, phosphorus: 21.0, potassium: 275.0, soil_moisture: 56.0, soil_type: "Medium Black Calcareous Vertisol", region: "Marathwada" },
  Latur: { temperature: 29.0, rainfall: 800.0, humidity: 65.0, soil_ph: 7.5, nitrogen: 150.0, phosphorus: 20.0, potassium: 290.0, soil_moisture: 56.0, soil_type: "Deep Black Vertisol", region: "Marathwada" },
  Nanded: { temperature: 30.0, rainfall: 900.0, humidity: 68.0, soil_ph: 7.4, nitrogen: 160.0, phosphorus: 23.0, potassium: 300.0, soil_moisture: 60.0, soil_type: "Deep Black Vertisol (Godavari Basin)", region: "Marathwada" },
  Parbhani: { temperature: 29.0, rainfall: 790.0, humidity: 65.0, soil_ph: 7.5, nitrogen: 155.0, phosphorus: 22.0, potassium: 295.0, soil_moisture: 58.0, soil_type: "Deep Black Vertisol (Godavari Basin)", region: "Marathwada" },

  // 6. Khandesh (Tapi Alluvium & Deccan Trap Volcanic Loams)
  Dhule: { temperature: 29.0, rainfall: 600.0, humidity: 58.0, soil_ph: 7.1, nitrogen: 160.0, phosphorus: 23.0, potassium: 265.0, soil_moisture: 54.0, soil_type: "Medium Black Silt Loam", region: "Khandesh" },
  Jalgaon: { temperature: 31.0, rainfall: 690.0, humidity: 62.0, soil_ph: 7.4, nitrogen: 170.0, phosphorus: 26.0, potassium: 310.0, soil_moisture: 58.0, soil_type: "Tapi Alluvial Deep Black Vertisol", region: "Khandesh" },
  Nandurbar: { temperature: 30.0, rainfall: 860.0, humidity: 66.0, soil_ph: 6.8, nitrogen: 165.0, phosphorus: 21.0, potassium: 240.0, soil_moisture: 58.0, soil_type: "Medium Black & Undulating Hilly Soil", region: "Khandesh" },
  Nashik: { temperature: 26.0, rainfall: 810.0, humidity: 68.0, soil_ph: 6.7, nitrogen: 185.0, phosphorus: 30.0, potassium: 255.0, soil_moisture: 62.0, soil_type: "Deccan Trap Volcanic Loam & River Alluvium", region: "Khandesh" }
};

export const DISTRICT_TALUKAS = {
  Akola: ["Akola", "Akot", "Balapur", "Barshitakli", "Murtizapur", "Patur", "Telhara"],
  Amravati: ["Achalpur", "Amravati", "Anjangaon Surji", "Bhatkuli", "Chandur Railway", "Chandurbazar", "Chikhaldara", "Daryapur", "Dhamangaon Railway", "Morshi", "Nandgaon Khandeshwar", "Teosa", "Warud"],
  Buldhana: ["Buldhana", "Chikhli", "Deulgaon Raja", "Jalgaon Jamod", "Khamgaon", "Lonar", "Malkapur", "Motala", "Nandura", "Sangrampur", "Shegaon", "Sindkhed Raja"],
  Nagpur: ["Bhiwapur", "Hingna", "Kalameshwar", "Kamptee", "Katol", "Kuhi", "Mouda", "Nagpur Rural", "Nagpur Urban", "Narkhed", "Parseoni", "Ramtek", "Saoner", "Umred"],
  Wardha: ["Arvi", "Ashti", "Deoli", "Hinganghat", "Karanja", "Samudrapur", "Seloo", "Wardha"],
  Washim: ["Karanja", "Malegaon", "Mangrulpir", "Manora", "Risod", "Washim"],
  Yavatmal: ["Arni", "Babhulgaon", "Darwha", "Digras", "Ghatanji", "Kalamb", "Mahagaon", "Maregaon", "Ner", "Pandharkawada", "Pusad", "Ralegaon", "Umarkhed", "Wani", "Yavatmal", "Zari Jamani"],
  Bhandara: ["Bhandara", "Mohadi", "Tumsar", "Pauni", "Sakoli", "Lakhani", "Lakhandur"],
  Chandrapur: ["Chandrapur", "Bhadravati", "Warora", "Chimur", "Nagbhid", "Bramhapuri", "Sindewahi", "Mul", "Saoli", "Pombhurna", "Ballarpur", "Korpana", "Rajura", "Jivati", "Gondpipri"],
  Gadchiroli: ["Gadchiroli", "Dhanora", "Chamorshi", "Armori", "Kurkheda", "Korchi", "Wadsa", "Aheri", "Etapalli", "Bhamragad", "Sironcha", "Mulchera"],
  Gondia: ["Gondia", "Tirora", "Goregaon", "Arjuni Morgaon", "Deori", "Salekasa", "Sadak Arjuni", "Amgaon"],
  Pune: ["Ambegaon", "Baramati", "Bhor", "Daund", "Haveli", "Indapur", "Junnar", "Khed", "Maval", "Mulshi", "Pune City", "Purandar", "Shirur", "Velhe"],
  Ahmednagar: ["Akole", "Jamkhed", "Karjat", "Kopargaon", "Nagar", "Nevasa", "Parner", "Pathardi", "Rahata", "Rahuri", "Sangamner", "Shevgaon", "Shrigonda", "Shrirampur"],
  Kolhapur: ["Ajra", "Bavda", "Bhudargad", "Chandgad", "Gadhinglaj", "Hatkanangle", "Kagal", "Karvir", "Panhala", "Radhanagari", "Shahuwadi", "Shirol"],
  Sangli: ["Atpadi", "Jat", "Kadegaon", "Kavathe Mahankal", "Khanapur", "Miraj", "Palus", "Shirala", "Tasgaon", "Walwa"],
  Satara: ["Jaoli", "Karad", "Khandala", "Khatav", "Koregaon", "Mahabaleshwar", "Man", "Patan", "Phaltan", "Satara", "Wai"],
  Solapur: ["Akkalkot", "Barshi", "Karmala", "Madha", "Malshiras", "Mangalvedhe", "Mohol", "Pandharpur", "Sangole", "Solapur North", "Solapur South"],
  "Chhatrapati Sambhajinagar": ["Aurangabad", "Kannad", "Khuldabad", "Gangapur", "Vaijapur", "Paithan", "Phulambri", "Sillod", "Soegaon"],
  Beed: ["Ambajogai", "Ashti", "Beed", "Dharur", "Georai", "Kaij", "Majalgaon", "Parli", "Patoda", "Shirur Kasar", "Wadwani"],
  Dharashiv: ["Bhoom", "Kalamb", "Lohara", "Omerga", "Osmanabad", "Paranda", "Tuljapur", "Washi"],
  Hingoli: ["Aundha Nagnath", "Basmath", "Hingoli", "Kalamnuri", "Sengaon"],
  Jalna: ["Ambad", "Badnapur", "Bhokardan", "Ghansawangi", "Jafrabad", "Jalna", "Mantha", "Partur"],
  Latur: ["Ahmedpur", "Ausa", "Chakur", "Deoni", "Jalkot", "Latur", "Nilanga", "Renapur", "Shirur Anantpal", "Udgir"],
  Nanded: ["Ardhapur", "Bhokar", "Biloli", "Deglur", "Dharmabad", "Hadgaon", "Himayatnagar", "Kandhar", "Kinwat", "Loha", "Mahur", "Mudkhed", "Mukhed", "Naigaon", "Nanded", "Umri"],
  Parbhani: ["Gangakhed", "Jintur", "Manwath", "Palam", "Parbhani", "Pathri", "Purna", "Sailu", "Sonpeth"],
  Dhule: ["Dhule", "Sakri", "Shirpur", "Sindkheda"],
  Jalgaon: ["Amalner", "Bhadgaon", "Bhusawal", "Bodwad", "Chalisgaon", "Chopda", "Dharangaon", "Erandol", "Jalgaon", "Jamner", "Muktainagar", "Pachora", "Parola", "Raver", "Yawal"],
  Nandurbar: ["Akkalkuwa", "Akrani", "Dhadgaon", "Nandurbar", "Nawapur", "Shahada", "Taloda"],
  Nashik: ["Baglan", "Chandwad", "Deola", "Dindori", "Igatpuri", "Kalwan", "Malegaon", "Nandgaon", "Nashik", "Niphad", "Peint", "Sinnar", "Surgana", "Trimbakeshwar", "Yevala"],
  "Mumbai City": ["Mumbai City"],
  "Mumbai Suburban": ["Kurla", "Andheri", "Borivali"],
  Palghar: ["Dahanu", "Jawhar", "Mokhada", "Palghar", "Talasari", "Vada", "Vikramgad", "Vasai"],
  Raigad: ["Alibag", "Karjat", "Khalapur", "Mahad", "Mangaon", "Mhasla", "Murud", "Panvel", "Pen", "Poladpur", "Roha", "Shrivardhan", "Sudhagad", "Tala", "Uran"],
  Ratnagiri: ["Chiplun", "Dapoli", "Guhagar", "Khed", "Lanja", "Mandangad", "Ratnagiri", "Rajapur", "Sangameshwar"],
  Sindhudurg: ["Devgad", "Dodamarg", "Kankavli", "Kudal", "Malwan", "Sawantwadi", "Vaibhavwadi", "Vengurla"],
  Thane: ["Ambarnath", "Bhiwandi", "Kalyan", "Murbad", "Shahapur", "Thane", "Ulhasnagar"]
};
