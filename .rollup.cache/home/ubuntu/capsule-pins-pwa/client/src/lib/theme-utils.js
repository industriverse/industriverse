/**
 * Theme Utility Functions
 * Week 8: Apply themes by setting CSS custom properties
 */
import { __assign } from "tslib";
/**
 * Apply theme to document root
 * Sets all CSS custom properties based on theme configuration
 */
export function applyTheme(theme) {
    var root = document.documentElement;
    // Apply brand colors
    root.style.setProperty('--brand-primary', theme.colors.brand.primary);
    root.style.setProperty('--brand-secondary', theme.colors.brand.secondary);
    root.style.setProperty('--brand-accent', theme.colors.brand.accent);
    // Apply status colors
    root.style.setProperty('--status-success', theme.colors.status.success);
    root.style.setProperty('--status-warning', theme.colors.status.warning);
    root.style.setProperty('--status-error', theme.colors.status.error);
    root.style.setProperty('--status-info', theme.colors.status.info);
    // Apply semantic colors - background
    root.style.setProperty('--bg-primary', theme.colors.semantic.background.primary);
    root.style.setProperty('--bg-secondary', theme.colors.semantic.background.secondary);
    if (theme.colors.semantic.background.tertiary) {
        root.style.setProperty('--bg-tertiary', theme.colors.semantic.background.tertiary);
    }
    // Apply semantic colors - foreground
    root.style.setProperty('--fg-primary', theme.colors.semantic.foreground.primary);
    root.style.setProperty('--fg-secondary', theme.colors.semantic.foreground.secondary);
    if (theme.colors.semantic.foreground.tertiary) {
        root.style.setProperty('--fg-tertiary', theme.colors.semantic.foreground.tertiary);
    }
    // Apply semantic colors - border
    root.style.setProperty('--border-default', theme.colors.semantic.border.default);
    if (theme.colors.semantic.border.subtle) {
        root.style.setProperty('--border-subtle', theme.colors.semantic.border.subtle);
    }
    if (theme.colors.semantic.border.strong) {
        root.style.setProperty('--border-strong', theme.colors.semantic.border.strong);
    }
    // Apply AmI colors
    root.style.setProperty('--ami-context-glow', theme.colors.ami.contextGlow);
    root.style.setProperty('--ami-prediction-pulse', theme.colors.ami.predictionPulse);
    root.style.setProperty('--ami-adaptation-fade', theme.colors.ami.adaptationFade);
    // Apply typography - fonts
    root.style.setProperty('--font-heading', theme.typography.fonts.heading);
    root.style.setProperty('--font-body', theme.typography.fonts.body);
    root.style.setProperty('--font-mono', theme.typography.fonts.mono);
    // Apply typography - sizes
    root.style.setProperty('--text-xs', theme.typography.sizes.xs);
    root.style.setProperty('--text-sm', theme.typography.sizes.sm);
    root.style.setProperty('--text-base', theme.typography.sizes.base);
    root.style.setProperty('--text-lg', theme.typography.sizes.lg);
    root.style.setProperty('--text-xl', theme.typography.sizes.xl);
    root.style.setProperty('--text-2xl', theme.typography.sizes['2xl']);
    root.style.setProperty('--text-3xl', theme.typography.sizes['3xl']);
    root.style.setProperty('--text-4xl', theme.typography.sizes['4xl']);
    // Apply typography - weights
    root.style.setProperty('--font-normal', theme.typography.weights.normal.toString());
    root.style.setProperty('--font-medium', theme.typography.weights.medium.toString());
    root.style.setProperty('--font-semibold', theme.typography.weights.semibold.toString());
    root.style.setProperty('--font-bold', theme.typography.weights.bold.toString());
    // Apply spacing
    theme.spacing.scale.forEach(function (value, index) {
        root.style.setProperty("--space-".concat(index + 1), "".concat(value).concat(theme.spacing.unit));
    });
    // Apply effects - border radius
    root.style.setProperty('--radius-sm', theme.effects.borderRadius.sm);
    root.style.setProperty('--radius-md', theme.effects.borderRadius.md);
    root.style.setProperty('--radius-lg', theme.effects.borderRadius.lg);
    root.style.setProperty('--radius-xl', theme.effects.borderRadius.xl);
    root.style.setProperty('--radius-full', theme.effects.borderRadius.full);
    // Apply effects - shadows
    root.style.setProperty('--shadow-sm', theme.effects.shadows.sm);
    root.style.setProperty('--shadow-md', theme.effects.shadows.md);
    root.style.setProperty('--shadow-lg', theme.effects.shadows.lg);
    root.style.setProperty('--shadow-xl', theme.effects.shadows.xl);
    // Apply animations - duration
    root.style.setProperty('--duration-fast', theme.animations.duration.fast);
    root.style.setProperty('--duration-normal', theme.animations.duration.normal);
    root.style.setProperty('--duration-slow', theme.animations.duration.slow);
    // Apply animations - easing
    root.style.setProperty('--easing-default', theme.animations.easing.default);
    root.style.setProperty('--easing-in', theme.animations.easing.in);
    root.style.setProperty('--easing-out', theme.animations.easing.out);
    root.style.setProperty('--easing-in-out', theme.animations.easing.inOut);
    // Store theme ID for reference
    root.setAttribute('data-theme', theme.id);
}
/**
 * Get current theme ID from document
 */
export function getCurrentThemeId() {
    return document.documentElement.getAttribute('data-theme');
}
/**
 * Export theme as JSON
 */
export function exportTheme(theme) {
    return JSON.stringify(theme, null, 2);
}
/**
 * Import theme from JSON
 */
export function importTheme(json) {
    try {
        var theme = JSON.parse(json);
        // Basic validation
        if (!theme.id || !theme.name || !theme.colors) {
            throw new Error('Invalid theme structure');
        }
        return theme;
    }
    catch (error) {
        throw new Error("Failed to import theme: ".concat(error instanceof Error ? error.message : 'Unknown error'));
    }
}
/**
 * Create theme override by extending base theme
 */
export function createThemeOverride(baseTheme, overrides) {
    var _a, _b, _c, _d, _e, _f, _g, _h, _j;
    return __assign(__assign(__assign({}, baseTheme), overrides), { id: overrides.id || "".concat(baseTheme.id, "-custom"), name: overrides.name || "".concat(baseTheme.name, " (Custom)"), extends: baseTheme.id, colors: __assign(__assign(__assign({}, baseTheme.colors), overrides.colors), { brand: __assign(__assign({}, baseTheme.colors.brand), (_a = overrides.colors) === null || _a === void 0 ? void 0 : _a.brand), status: __assign(__assign({}, baseTheme.colors.status), (_b = overrides.colors) === null || _b === void 0 ? void 0 : _b.status), semantic: {
                background: __assign(__assign({}, baseTheme.colors.semantic.background), (_d = (_c = overrides.colors) === null || _c === void 0 ? void 0 : _c.semantic) === null || _d === void 0 ? void 0 : _d.background),
                foreground: __assign(__assign({}, baseTheme.colors.semantic.foreground), (_f = (_e = overrides.colors) === null || _e === void 0 ? void 0 : _e.semantic) === null || _f === void 0 ? void 0 : _f.foreground),
                border: __assign(__assign({}, baseTheme.colors.semantic.border), (_h = (_g = overrides.colors) === null || _g === void 0 ? void 0 : _g.semantic) === null || _h === void 0 ? void 0 : _h.border),
            }, ami: __assign(__assign({}, baseTheme.colors.ami), (_j = overrides.colors) === null || _j === void 0 ? void 0 : _j.ami) }), typography: __assign(__assign({}, baseTheme.typography), overrides.typography), spacing: __assign(__assign({}, baseTheme.spacing), overrides.spacing), effects: __assign(__assign({}, baseTheme.effects), overrides.effects), animations: __assign(__assign({}, baseTheme.animations), overrides.animations) });
}
/**
 * Generate CSS custom properties string from theme
 * Useful for SSR or static generation
 */
export function generateCSSVariables(theme) {
    var lines = [':root {'];
    // Brand colors
    lines.push("  --brand-primary: ".concat(theme.colors.brand.primary, ";"));
    lines.push("  --brand-secondary: ".concat(theme.colors.brand.secondary, ";"));
    lines.push("  --brand-accent: ".concat(theme.colors.brand.accent, ";"));
    // Status colors
    lines.push("  --status-success: ".concat(theme.colors.status.success, ";"));
    lines.push("  --status-warning: ".concat(theme.colors.status.warning, ";"));
    lines.push("  --status-error: ".concat(theme.colors.status.error, ";"));
    lines.push("  --status-info: ".concat(theme.colors.status.info, ";"));
    // Semantic colors
    lines.push("  --bg-primary: ".concat(theme.colors.semantic.background.primary, ";"));
    lines.push("  --bg-secondary: ".concat(theme.colors.semantic.background.secondary, ";"));
    if (theme.colors.semantic.background.tertiary) {
        lines.push("  --bg-tertiary: ".concat(theme.colors.semantic.background.tertiary, ";"));
    }
    lines.push("  --fg-primary: ".concat(theme.colors.semantic.foreground.primary, ";"));
    lines.push("  --fg-secondary: ".concat(theme.colors.semantic.foreground.secondary, ";"));
    if (theme.colors.semantic.foreground.tertiary) {
        lines.push("  --fg-tertiary: ".concat(theme.colors.semantic.foreground.tertiary, ";"));
    }
    lines.push("  --border-default: ".concat(theme.colors.semantic.border.default, ";"));
    if (theme.colors.semantic.border.subtle) {
        lines.push("  --border-subtle: ".concat(theme.colors.semantic.border.subtle, ";"));
    }
    if (theme.colors.semantic.border.strong) {
        lines.push("  --border-strong: ".concat(theme.colors.semantic.border.strong, ";"));
    }
    // AmI colors
    lines.push("  --ami-context-glow: ".concat(theme.colors.ami.contextGlow, ";"));
    lines.push("  --ami-prediction-pulse: ".concat(theme.colors.ami.predictionPulse, ";"));
    lines.push("  --ami-adaptation-fade: ".concat(theme.colors.ami.adaptationFade, ";"));
    // Typography
    lines.push("  --font-heading: ".concat(theme.typography.fonts.heading, ";"));
    lines.push("  --font-body: ".concat(theme.typography.fonts.body, ";"));
    lines.push("  --font-mono: ".concat(theme.typography.fonts.mono, ";"));
    lines.push("  --text-xs: ".concat(theme.typography.sizes.xs, ";"));
    lines.push("  --text-sm: ".concat(theme.typography.sizes.sm, ";"));
    lines.push("  --text-base: ".concat(theme.typography.sizes.base, ";"));
    lines.push("  --text-lg: ".concat(theme.typography.sizes.lg, ";"));
    lines.push("  --text-xl: ".concat(theme.typography.sizes.xl, ";"));
    lines.push("  --text-2xl: ".concat(theme.typography.sizes['2xl'], ";"));
    lines.push("  --text-3xl: ".concat(theme.typography.sizes['3xl'], ";"));
    lines.push("  --text-4xl: ".concat(theme.typography.sizes['4xl'], ";"));
    // Effects
    lines.push("  --radius-sm: ".concat(theme.effects.borderRadius.sm, ";"));
    lines.push("  --radius-md: ".concat(theme.effects.borderRadius.md, ";"));
    lines.push("  --radius-lg: ".concat(theme.effects.borderRadius.lg, ";"));
    lines.push("  --radius-xl: ".concat(theme.effects.borderRadius.xl, ";"));
    lines.push("  --radius-full: ".concat(theme.effects.borderRadius.full, ";"));
    lines.push("  --shadow-sm: ".concat(theme.effects.shadows.sm, ";"));
    lines.push("  --shadow-md: ".concat(theme.effects.shadows.md, ";"));
    lines.push("  --shadow-lg: ".concat(theme.effects.shadows.lg, ";"));
    lines.push("  --shadow-xl: ".concat(theme.effects.shadows.xl, ";"));
    // Animations
    lines.push("  --duration-fast: ".concat(theme.animations.duration.fast, ";"));
    lines.push("  --duration-normal: ".concat(theme.animations.duration.normal, ";"));
    lines.push("  --duration-slow: ".concat(theme.animations.duration.slow, ";"));
    lines.push("  --easing-default: ".concat(theme.animations.easing.default, ";"));
    lines.push("  --easing-in: ".concat(theme.animations.easing.in, ";"));
    lines.push("  --easing-out: ".concat(theme.animations.easing.out, ";"));
    lines.push("  --easing-in-out: ".concat(theme.animations.easing.inOut, ";"));
    lines.push('}');
    return lines.join('\n');
}
//# sourceMappingURL=theme-utils.js.map