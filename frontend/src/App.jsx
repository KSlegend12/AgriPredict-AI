import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import RecommendationPage from './pages/RecommendationPage';
import CottonYieldPage from './pages/CottonYieldPage';
import FutureCottonForecastPage from './pages/FutureCottonForecastPage';
import ModelInsightsPage from './pages/ModelInsightsPage';
import WeatherPage from './pages/WeatherPage';
import HistoryPage from './pages/HistoryPage';
import AboutPage from './pages/AboutPage';
import SatelliteDataPage from './pages/SatelliteDataPage';
import HowItWorksPage from './pages/HowItWorksPage';
import ErrorBoundary from './components/ErrorBoundary';
import { getHealth } from './services/api';
import { sanitizeDistrict } from './constants/districts';

export default function App() {
  const [selectedDistrict, setSelectedDistrictState] = useState(() => {
    const saved = localStorage.getItem('agripredict-district');
    return sanitizeDistrict(saved);
  });

  const setSelectedDistrict = (dist) => {
    const clean = sanitizeDistrict(dist);
    setSelectedDistrictState(clean);
    localStorage.setItem('agripredict-district', clean);
  };

  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('agripredict-theme');
    if (saved === 'dark' || saved === 'light') return saved;
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });
  const [isRealModel, setIsRealModel] = useState(false);

  useEffect(() => {
    const clean = sanitizeDistrict(selectedDistrict);
    if (clean !== selectedDistrict) {
      setSelectedDistrictState(clean);
    }
  }, [selectedDistrict]);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.body.classList.toggle('dark-theme', theme === 'dark');
    localStorage.setItem('agripredict-theme', theme);
  }, [theme]);

  useEffect(() => {
    getHealth().then((data) => {
      setIsRealModel(Boolean(data?.is_model_loaded || data?.cotton?.loaded));
    });
  }, []);

  return (
    <Router>
      <div className="app-shell min-h-screen bg-[#f4f8f3] text-slate-900 flex flex-col">
        <Navbar
          selectedDistrict={selectedDistrict}
          setSelectedDistrict={setSelectedDistrict}
          isRealModel={isRealModel}
          theme={theme}
          setTheme={setTheme}
        />

        <main className="flex-1 w-full max-w-[1500px] mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/dashboard" element={<Dashboard selectedDistrict={selectedDistrict} setSelectedDistrict={setSelectedDistrict} />} />
              <Route path="/cotton" element={<CottonYieldPage selectedDistrict={selectedDistrict} setSelectedDistrict={setSelectedDistrict} />} />
              <Route path="/yield" element={<CottonYieldPage selectedDistrict={selectedDistrict} setSelectedDistrict={setSelectedDistrict} />} />
              <Route path="/future-forecast" element={<FutureCottonForecastPage selectedDistrict={selectedDistrict} setSelectedDistrict={setSelectedDistrict} />} />
              <Route path="/insights" element={<ModelInsightsPage />} />
              <Route path="/satellite" element={<SatelliteDataPage />} />
              <Route path="/how-it-works" element={<HowItWorksPage />} />
              <Route path="/weather" element={<WeatherPage selectedDistrict={selectedDistrict} setSelectedDistrict={setSelectedDistrict} />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/recommend" element={<RecommendationPage selectedDistrict={selectedDistrict} setSelectedDistrict={setSelectedDistrict} />} />
              <Route path="/about" element={<AboutPage />} />
            </Routes>
          </ErrorBoundary>
        </main>

        <Footer />
      </div>
    </Router>
  );
}
