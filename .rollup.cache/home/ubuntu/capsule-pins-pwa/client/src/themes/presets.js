/**
 * Preset Themes for White-Label Platform
 * Week 8: Three professionally designed themes
 */
/**
 * Theme 1: Industriverse Default (Cosmic-Industrial)
 * Deep space aesthetic with cyan/purple accents
 */
export var cosmicIndustrialTheme = {
    id: 'cosmic-industrial',
    name: 'Cosmic Industrial',
    version: '1.0.0',
    colors: {
        brand: {
            primary: '#0ea5e9', // Cyan
            secondary: '#8b5cf6', // Purple
            accent: '#f59e0b', // Amber
        },
        status: {
            success: '#10b981', // Emerald
            warning: '#f59e0b', // Amber
            error: '#ef4444', // Red
            info: '#3b82f6', // Blue
        },
        semantic: {
            background: {
                primary: '#0f172a', // Deep space black
                secondary: '#1e293b', // Slate 800
                tertiary: '#334155', // Slate 700
            },
            foreground: {
                primary: '#f8fafc', // Slate 50
                secondary: '#cbd5e1', // Slate 300
                tertiary: '#94a3b8', // Slate 400
            },
            border: {
                default: '#334155', // Slate 700
                subtle: '#1e293b', // Slate 800
                strong: '#475569', // Slate 600
            },
        },
        ami: {
            contextGlow: 'rgba(14, 165, 233, 0.3)', // Cyan glow
            predictionPulse: 'rgba(139, 92, 246, 0.4)', // Purple pulse
            adaptationFade: 'rgba(245, 158, 11, 0.2)', // Amber fade
        },
    },
    typography: {
        fonts: {
            heading: "'Inter', sans-serif",
            body: "'Inter', sans-serif",
            mono: "'JetBrains Mono', monospace",
        },
        sizes: {
            xs: '0.75rem',
            sm: '0.875rem',
            base: '1rem',
            lg: '1.125rem',
            xl: '1.25rem',
            '2xl': '1.5rem',
            '3xl': '1.875rem',
            '4xl': '2.25rem',
        },
        weights: {
            normal: 400,
            medium: 500,
            semibold: 600,
            bold: 700,
        },
    },
    spacing: {
        scale: [0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4],
        unit: 'rem',
    },
    effects: {
        borderRadius: {
            sm: '0.25rem',
            md: '0.5rem',
            lg: '0.75rem',
            xl: '1rem',
            full: '9999px',
        },
        shadows: {
            sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
            md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
            lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
            xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
        },
    },
    animations: {
        duration: {
            fast: '150ms',
            normal: '300ms',
            slow: '500ms',
        },
        easing: {
            default: 'cubic-bezier(0.4, 0, 0.2, 1)',
            in: 'cubic-bezier(0.4, 0, 1, 1)',
            out: 'cubic-bezier(0, 0, 0.2, 1)',
            inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
        },
    },
};
/**
 * Theme 2: Industrial Chrome (Neutral-Metallic)
 * Professional slate/steel aesthetic
 */
export var industrialChromeTheme = {
    id: 'industrial-chrome',
    name: 'Industrial Chrome',
    version: '1.0.0',
    colors: {
        brand: {
            primary: '#3b82f6', // Steel blue
            secondary: '#6366f1', // Indigo
            accent: '#f59e0b', // Amber
        },
        status: {
            success: '#10b981', // Emerald
            warning: '#f59e0b', // Amber
            error: '#ef4444', // Red
            info: '#3b82f6', // Blue
        },
        semantic: {
            background: {
                primary: '#475569', // Slate 600
                secondary: '#64748b', // Slate 500
                tertiary: '#94a3b8', // Slate 400
            },
            foreground: {
                primary: '#f8fafc', // Slate 50
                secondary: '#e2e8f0', // Slate 200
                tertiary: '#cbd5e1', // Slate 300
            },
            border: {
                default: '#94a3b8', // Slate 400
                subtle: '#cbd5e1', // Slate 300
                strong: '#64748b', // Slate 500
            },
        },
        ami: {
            contextGlow: 'rgba(59, 130, 246, 0.3)', // Blue glow
            predictionPulse: 'rgba(99, 102, 241, 0.4)', // Indigo pulse
            adaptationFade: 'rgba(245, 158, 11, 0.2)', // Amber fade
        },
    },
    typography: {
        fonts: {
            heading: "'Inter', sans-serif",
            body: "'Inter', sans-serif",
            mono: "'JetBrains Mono', monospace",
        },
        sizes: {
            xs: '0.75rem',
            sm: '0.875rem',
            base: '1rem',
            lg: '1.125rem',
            xl: '1.25rem',
            '2xl': '1.5rem',
            '3xl': '1.875rem',
            '4xl': '2.25rem',
        },
        weights: {
            normal: 400,
            medium: 500,
            semibold: 600,
            bold: 700,
        },
    },
    spacing: {
        scale: [0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4],
        unit: 'rem',
    },
    effects: {
        borderRadius: {
            sm: '0.25rem',
            md: '0.5rem',
            lg: '0.75rem',
            xl: '1rem',
            full: '9999px',
        },
        shadows: {
            sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
            md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
            lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
            xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
        },
    },
    animations: {
        duration: {
            fast: '150ms',
            normal: '300ms',
            slow: '500ms',
        },
        easing: {
            default: 'cubic-bezier(0.4, 0, 0.2, 1)',
            in: 'cubic-bezier(0.4, 0, 1, 1)',
            out: 'cubic-bezier(0, 0, 0.2, 1)',
            inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
        },
    },
};
/**
 * Theme 3: Light Portal (Minimal-Airy)
 * Clean white aesthetic with indigo accents
 */
export var lightPortalTheme = {
    id: 'light-portal',
    name: 'Light Portal',
    version: '1.0.0',
    colors: {
        brand: {
            primary: '#6366f1', // Indigo
            secondary: '#8b5cf6', // Purple
            accent: '#10b981', // Emerald
        },
        status: {
            success: '#10b981', // Emerald
            warning: '#f59e0b', // Amber
            error: '#ef4444', // Red
            info: '#3b82f6', // Blue
        },
        semantic: {
            background: {
                primary: '#ffffff', // White
                secondary: '#f8fafc', // Slate 50
                tertiary: '#f1f5f9', // Slate 100
            },
            foreground: {
                primary: '#0f172a', // Slate 900
                secondary: '#475569', // Slate 600
                tertiary: '#64748b', // Slate 500
            },
            border: {
                default: '#e2e8f0', // Slate 200
                subtle: '#f1f5f9', // Slate 100
                strong: '#cbd5e1', // Slate 300
            },
        },
        ami: {
            contextGlow: 'rgba(99, 102, 241, 0.2)', // Indigo glow
            predictionPulse: 'rgba(139, 92, 246, 0.3)', // Purple pulse
            adaptationFade: 'rgba(16, 185, 129, 0.15)', // Emerald fade
        },
    },
    typography: {
        fonts: {
            heading: "'Inter', sans-serif",
            body: "'Inter', sans-serif",
            mono: "'JetBrains Mono', monospace",
        },
        sizes: {
            xs: '0.75rem',
            sm: '0.875rem',
            base: '1rem',
            lg: '1.125rem',
            xl: '1.25rem',
            '2xl': '1.5rem',
            '3xl': '1.875rem',
            '4xl': '2.25rem',
        },
        weights: {
            normal: 400,
            medium: 500,
            semibold: 600,
            bold: 700,
        },
    },
    spacing: {
        scale: [0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4],
        unit: 'rem',
    },
    effects: {
        borderRadius: {
            sm: '0.25rem',
            md: '0.5rem',
            lg: '0.75rem',
            xl: '1rem',
            full: '9999px',
        },
        shadows: {
            sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
            md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
            lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
            xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
        },
    },
    animations: {
        duration: {
            fast: '150ms',
            normal: '300ms',
            slow: '500ms',
        },
        easing: {
            default: 'cubic-bezier(0.4, 0, 0.2, 1)',
            in: 'cubic-bezier(0.4, 0, 1, 1)',
            out: 'cubic-bezier(0, 0, 0.2, 1)',
            inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
        },
    },
};
/**
 * Theme Presets with metadata
 */
export var themePresets = [
    {
        id: 'cosmic-industrial',
        name: 'Cosmic Industrial',
        description: 'Deep space aesthetic with cyan and purple accents. Perfect for high-tech industrial applications.',
        preview: '/themes/cosmic-industrial-preview.png',
        theme: cosmicIndustrialTheme,
    },
    {
        id: 'industrial-chrome',
        name: 'Industrial Chrome',
        description: 'Professional slate and steel aesthetic. Ideal for enterprise manufacturing environments.',
        preview: '/themes/industrial-chrome-preview.png',
        theme: industrialChromeTheme,
    },
    {
        id: 'light-portal',
        name: 'Light Portal',
        description: 'Clean, minimal white aesthetic with indigo accents. Best for customer-facing portals.',
        preview: '/themes/light-portal-preview.png',
        theme: lightPortalTheme,
    },
];
/**
 * Get theme by ID
 */
export function getThemeById(id) {
    var preset = themePresets.find(function (p) { return p.id === id; });
    return preset === null || preset === void 0 ? void 0 : preset.theme;
}
/**
 * Get all available themes
 */
export function getAllThemes() {
    return themePresets.map(function (p) { return p.theme; });
}
/**
 * Validate theme structure
 */
export function validateTheme(theme) {
    // Basic validation - can be extended with zod or similar
    return !!(theme.id &&
        theme.name &&
        theme.version &&
        theme.colors &&
        theme.typography &&
        theme.spacing &&
        theme.effects &&
        theme.animations);
}
//# sourceMappingURL=presets.js.map