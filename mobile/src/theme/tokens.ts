/**
 * Theme tokens — Android-first, low-end-device-friendly.
 * No hardcoded colors/spacing outside this file.
 */
export const colors = {
  primary: '#1B5E20',      // deep green
  primaryLight: '#E8F5E9',
  accent: '#F9A825',       // harvest amber
  text: '#212121',
  textMuted: '#616161',
  background: '#FAFAFA',
  surface: '#FFFFFF',
  danger: '#C62828',
  border: '#E0E0E0',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
} as const;

/** Farmers on budget phones in sunlight: never go below 16sp for body text. */
export const fontSize = {
  body: 16,
  title: 22,
  small: 14, // captions only
} as const;

export const radius = { md: 12 } as const;
