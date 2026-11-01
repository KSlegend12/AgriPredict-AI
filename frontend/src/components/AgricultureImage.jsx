import React, { useState } from 'react';
import { Sprout } from 'lucide-react';

/**
 * Robust AgricultureImage Component
 *
 * - Tries primary src (e.g. /images/cotton-field.jpg)
 * - Tries fallbackSrc (e.g. /images/cotton-plant.jpg)
 * - If both fail, renders a clean, styled agricultural SVG placeholder
 * - Shows a skeleton loader while loading
 * - Never exposes broken alt text or missing image icons
 */
export default function AgricultureImage({
  src = '/images/cotton-field.jpg',
  fallbackSrc = '/images/cotton-plant.jpg',
  alt = 'Cotton field in Vidarbha, Maharashtra',
  className = '',
  style = {},
  objectFit = 'cover',
  loading: loadingProp = 'eager'
}) {
  const [currentSrc, setCurrentSrc] = useState(src);
  const [hasTriedFallback, setHasTriedFallback] = useState(false);
  const [isError, setIsError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const handleError = () => {
    if (!hasTriedFallback && fallbackSrc && currentSrc !== fallbackSrc) {
      setHasTriedFallback(true);
      setCurrentSrc(fallbackSrc);
    } else {
      setIsError(true);
      setIsLoading(false);
    }
  };

  const handleLoad = () => {
    setIsLoading(false);
  };

  if (isError) {
    return (
      <div
        className={`relative flex flex-col items-center justify-center bg-gradient-to-br from-emerald-800 via-teal-900 to-slate-900 text-white p-6 text-center select-none overflow-hidden ${className}`}
        style={style}
      >
        <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-400/30 flex items-center justify-center mb-2">
          <Sprout className="w-6 h-6 text-emerald-300" />
        </div>
        <span className="font-black text-sm text-white tracking-tight">Cotton Agriculture</span>
        <span className="text-[10px] text-emerald-300/80 font-bold uppercase tracking-widest mt-0.5">Vidarbha Region, Maharashtra</span>
      </div>
    );
  }

  return (
    <div className={`relative overflow-hidden bg-slate-200 ${className}`} style={style}>
      {isLoading && (
        <div className="absolute inset-0 bg-slate-200 animate-pulse flex items-center justify-center">
          <Sprout className="w-6 h-6 text-slate-400 opacity-40" />
        </div>
      )}
      <img
        src={currentSrc}
        alt={alt}
        onError={handleError}
        onLoad={handleLoad}
        loading={loadingProp}
        className={`w-full h-full transition-opacity duration-300 ${isLoading ? 'opacity-0' : 'opacity-100'}`}
        style={{ objectFit, ...style }}
      />
    </div>
  );
}
