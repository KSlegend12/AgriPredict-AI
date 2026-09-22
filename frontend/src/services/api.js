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


export const getCottonPredictionInput = async (district, year) => {
  try {
    const res = await api.get(`/cotton/input/${encodeURIComponent(district)}/${year}`);
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


export const getCottonFutureForecast = async (district) => {
  try {
    const res = await api.get(`/cotton/future-forecast/${encodeURIComponent(district)}`);
    return res.data;
  } catch (err) {
    console.error('Cotton future forecast API error:', err);
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

export default api;
