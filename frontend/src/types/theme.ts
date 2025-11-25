/**
 * Theme System Type Definitions
 * Week 8: White-Label Platform
 */

export interface ThemeColors {
  brand: {
    primary: string;
    secondary: string;
    accent: string;
  };
  status: {
    success: string;
    warning: string;
    error: string;
    info: string;
  };
  semantic: {
    background: {
      primary: string;
      secondary: string;
      tertiary?: string;
    };
    foreground: {
      primary: string;
      secondary: string;
      tertiary?: string;
    };
    border: {
      default: string;
      subtle?: string;
      strong?: string;
    };
  };
  ami: {
    contextGlow: string;
    predictionPulse: string;
    adaptationFade: string;
  };
}

export interface ThemeTypography {
  fonts: {
    heading: string;
    body: string;
    mono: string;
  };
  sizes: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    '2xl': string;
    '3xl': string;
    '4xl': string;
  };
  weights: {
    normal: number;
    medium: number;
    semibold: number;
    bold: number;
  };
}

export interface ThemeSpacing {
  scale: number[];
  unit: string;
}

export interface ThemeEffects {
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
    full: string;
  };
  shadows: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
}

export interface ThemeAnimations {
  duration: {
    fast: string;
    normal: string;
    slow: string;
  };
  easing: {
    default: string;
    in: string;
    out: string;
    inOut: string;
  };
}

export interface Theme {
  id: string;
  name: string;
  version: string;
  extends?: string;
  colors: ThemeColors;
  typography: ThemeTypography;
  spacing: ThemeSpacing;
  effects: ThemeEffects;
  animations: ThemeAnimations;
}

export interface ThemePreset {
  id: string;
  name: string;
  description: string;
  preview: string; // URL to preview image
  theme: Theme;
}

export type ThemeMode = 'cosmic-industrial' | 'industrial-chrome' | 'light-portal' | 'custom';
