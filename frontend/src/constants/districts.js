/**
 * Shared authoritative Vidarbha district constants for AgriPredict-AI frontend.
 * Scope: 6 supported Vidarbha research districts (Akola, Amravati, Buldhana, Nagpur, Wardha, Washim).
 * Yavatmal is strictly excluded from the active prediction and research model scope.
 */

export const SUPPORTED_VIDARBHA_DISTRICTS = [
  'Akola',
  'Amravati',
  'Buldhana',
  'Nagpur',
  'Wardha',
  'Washim',
];

export const VIDARBHA_DISTRICTS = SUPPORTED_VIDARBHA_DISTRICTS;
export const DEFAULT_DISTRICT = 'Akola';

export function isValidDistrict(district) {
  return typeof district === 'string' && SUPPORTED_VIDARBHA_DISTRICTS.includes(district.trim());
}

export function sanitizeDistrict(district, fallback = DEFAULT_DISTRICT) {
  return isValidDistrict(district) ? district.trim() : fallback;
}
