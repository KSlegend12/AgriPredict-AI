import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 12000,
});

export const getHealth = async () => {
  try {
    const res = await api.get('/health');
    return res.data;
  } catch (err) {
    console.warn('Backend API unreachable:', err);
    return { is_model_loaded: false, status: 'offline' };
  }
};

export const getDistricts = async () => {
  try {
    const res = await api.get('/districts');
    return res.data;
  } catch (err) {
    console.warn('Failed to fetch districts:', err);
    return null;
  }
};

export const getWeather = async (district) => {
  try {
    const res = await api.get(`/weather/${encodeURIComponent(district)}`);
    return res.data;
  } catch (err) {
    console.warn(`Failed to fetch weather for ${district}:`, err);
    return null;
  }
};

export const recommendCrop = async (payload) => {
  try {
    const res = await api.post('/crop/recommend', payload);
    return res.data;
  } catch (err) {
    console.error('Crop recommendation API error:', err);
    throw err;
  }
};

export const predictYield = async (payload) => {
  try {
    const res = await api.post('/yield/predict', payload);
    return res.data;
  } catch (err) {
    console.error('Yield prediction API error:', err);
    throw err;
  }
};

export const getHistory = async (limit = 100) => {
  try {
    const res = await api.get(`/history?limit=${limit}`);
    return res.data;
  } catch (err) {
    console.warn('Failed to fetch history:', err);
    return { history: [] };
  }
};

export const predictCottonYield = async (payload) => {
  try {
    const res = await api.post('/cotton/predict', payload);
    return res.data;
  } catch (err) {
    console.error('Cotton yield prediction API error:', err);
    throw err;
  }
};


export const getCottonPredictionInput = async (district, year, modelVersion = 'candidate_six_district_thermal') => {
  try {
    const res = await api.get(`/cotton/input/${encodeURIComponent(district)}/${year}`, {
      params: { model_version: modelVersion }
    });
    return res.data;
  } catch (err) {
    console.error('Cotton prediction input API error:', err);
    throw err;
  }
};

export const getCottonWeather = async (district, year) => {
  try {
    const res = await api.get(`/cotton/weather/${encodeURIComponent(district)}/${year}`);
    return res.data;
  } catch (err) {
    console.error('Cotton weather API error:', err);
    throw err;
  }
};

export const getCottonHistory = async (district) => {
  try {
    const res = await api.get(`/cotton/history/${encodeURIComponent(district)}`);
    return res.data;
  } catch (err) {
    console.error('Cotton history API error:', err);
    throw err;
  }
};

export const getCottonDistricts = async () => {
  try {
    const res = await api.get('/cotton/districts');
    return res.data;
  } catch (err) {
    console.warn('Failed to fetch cotton districts:', err);
    return null;
  }
};

export const getCottonModelInfo = async () => {
  try {
    const res = await api.get('/cotton/model/info');
    return res.data;
  } catch (err) {
    console.warn('Failed to fetch cotton model info:', err);
    return null;
  }
};

export const getCottonGlobalXAI = async () => {
  try {
    const res = await api.get('/cotton/xai/global');
    return res.data;
  } catch (err) {
    console.warn('Failed to fetch global XAI data:', err);
    return null;
  }
};


export const getCottonFutureForecast = async (district) => {
  try {
    const res = await api.get(`/cotton/future-forecast/${encodeURIComponent(district)}`);
    return res.data;
  } catch (err) {
    console.error('Cotton future forecast API error:', err);
    throw err;
  }
};

export const getCotton2025ExperimentalPrediction = async (district) => {
  try {
    const res = await api.get(
      `/cotton/future-forecast/2025/${encodeURIComponent(district)}`
    );
    return res.data;
  } catch (err) {
    console.error(
      'Cotton 2025 experimental prediction API error:',
      err
    );
    throw err;
  }
};

export const getCotton2026ScenarioPrediction = async (district) => {
  try {
    const res = await api.get(
      `/cotton/future-forecast/2026/${encodeURIComponent(district)}`
    );
    return res.data;
  } catch (err) {
    console.error(
      'Cotton 2026 scenario prediction API error:',
      err
    );
    throw err;
  }
};

export const getCottonFutureForecastDistricts = async () => {
  try {
    const res = await api.get('/cotton/future-forecast/districts');
    return res.data;
  } catch (err) {
    console.error('Cotton future forecast districts API error:', err);
    throw err;
  }
};

// ===========================================================================
// PHASE 11: FIELD VALIDATION & REAL AGRICULTURAL DATA INTEGRATION
// ===========================================================================

export const submitSoilTestReport = async (payload) => {
  try {
    const res = await api.post('/soil/test-report', payload);
    return res.data;
  } catch (err) {
    console.error('Soil test report API error:', err);
    throw err;
  }
};

export const getSoilTestReports = async (district = null, limit = 50) => {
  try {
    const q = district ? `?district=${encodeURIComponent(district)}&limit=${limit}` : `?limit=${limit}`;
    const res = await api.get(`/soil/test-reports${q}`);
    return res.data;
  } catch (err) {
    console.warn('Failed to fetch soil test reports:', err);
    return { reports: [] };
  }
};

export const submitFieldObservation = async (payload) => {
  try {
    const res = await api.post('/field-observations/record', payload);
    return res.data;
  } catch (err) {
    console.error('Field observation submission API error:', err);
    throw err;
  }
};

export const getFieldObservations = async (district = null, crop = null, limit = 50) => {
  try {
    const params = new URLSearchParams();
    if (district) params.append('district', district);
    if (crop) params.append('crop', crop);
    params.append('limit', limit);
    const res = await api.get(`/field-observations?${params.toString()}`);
    return res.data;
  } catch (err) {
    console.warn('Failed to fetch field observations:', err);
    return { observations: [] };
  }
};

export const submitOutcomeComparison = async (payload) => {
  try {
    const res = await api.post('/outcomes/compare', payload);
    return res.data;
  } catch (err) {
    console.error('Outcome comparison API error:', err);
    throw err;
  }
};

export const getOutcomeValidationSummary = async () => {
  try {
    const res = await api.get('/outcomes/summary');
    return res.data;
  } catch (err) {
    console.warn('Failed to fetch outcome validation summary:', err);
    return null;
  }
};

export const getDistrictTalukas = async (district) => {
  try {
    const res = await api.get(`/talukas/${encodeURIComponent(district)}`);
    return res.data;
  } catch (err) {
    console.warn(`Failed to fetch talukas for ${district}:`, err);
    return { talukas: [] };
  }
};

export const getWeatherProvenance = async (district) => {
  try {
    const res = await api.get(`/weather-provenance/${encodeURIComponent(district)}`);
    return res.data;
  } catch (err) {
    console.warn(`Failed to fetch weather provenance for ${district}:`, err);
    return null;
  }
};

export default api;
