/**
 * Theme Switcher Component
 * Week 8: White-Label Platform
 * Allows users to switch between preset themes
 */
import { useState, useEffect } from 'react';
import { themePresets } from '../themes/presets';
import { applyTheme } from '../lib/theme-utils';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue, } from './ui/select';
import { Card } from './ui/card';
export function ThemeSwitcher(_a) {
    var onThemeChange = _a.onThemeChange, _b = _a.showPreview, showPreview = _b === void 0 ? true : _b;
    var _c = useState(function () {
        // Load from localStorage or default to cosmic-industrial
        return localStorage.getItem('theme-id') || 'cosmic-industrial';
    }), currentThemeId = _c[0], setCurrentThemeId = _c[1];
    var presets = useState(themePresets)[0];
    useEffect(function () {
        // Apply theme on mount and when changed
        var preset = presets.find(function (p) { return p.id === currentThemeId; });
        if (preset) {
            applyTheme(preset.theme);
            localStorage.setItem('theme-id', currentThemeId);
            onThemeChange === null || onThemeChange === void 0 ? void 0 : onThemeChange(preset.theme);
        }
    }, [currentThemeId, presets, onThemeChange]);
    var handleThemeChange = function (themeId) {
        setCurrentThemeId(themeId);
    };
    var currentPreset = presets.find(function (p) { return p.id === currentThemeId; });
    return (<div className="theme-switcher space-y-4">
      <div className="flex items-center gap-4">
        <label htmlFor="theme-select" className="text-sm font-medium">
          Theme:
        </label>
        <Select value={currentThemeId} onValueChange={handleThemeChange}>
          <SelectTrigger id="theme-select" className="w-[200px]">
            <SelectValue placeholder="Select theme"/>
          </SelectTrigger>
          <SelectContent>
            {presets.map(function (preset) { return (<SelectItem key={preset.id} value={preset.id}>
                {preset.name}
              </SelectItem>); })}
          </SelectContent>
        </Select>
      </div>

      {showPreview && currentPreset && (<Card className="p-4 space-y-3">
          <h3 className="font-semibold">{currentPreset.name}</h3>
          <p className="text-sm text-muted-foreground">{currentPreset.description}</p>
          
          <div className="space-y-2">
            <div className="text-xs font-medium">Brand Colors:</div>
            <div className="flex gap-2">
              <div className="w-12 h-12 rounded border" style={{ backgroundColor: currentPreset.theme.colors.brand.primary }} title="Primary"/>
              <div className="w-12 h-12 rounded border" style={{ backgroundColor: currentPreset.theme.colors.brand.secondary }} title="Secondary"/>
              <div className="w-12 h-12 rounded border" style={{ backgroundColor: currentPreset.theme.colors.brand.accent }} title="Accent"/>
            </div>
          </div>

          <div className="space-y-2">
            <div className="text-xs font-medium">Status Colors:</div>
            <div className="flex gap-2">
              <div className="w-12 h-12 rounded border" style={{ backgroundColor: currentPreset.theme.colors.status.success }} title="Success"/>
              <div className="w-12 h-12 rounded border" style={{ backgroundColor: currentPreset.theme.colors.status.warning }} title="Warning"/>
              <div className="w-12 h-12 rounded border" style={{ backgroundColor: currentPreset.theme.colors.status.error }} title="Error"/>
              <div className="w-12 h-12 rounded border" style={{ backgroundColor: currentPreset.theme.colors.status.info }} title="Info"/>
            </div>
          </div>

          <div className="space-y-2">
            <div className="text-xs font-medium">Background Colors:</div>
            <div className="flex gap-2">
              <div className="w-12 h-12 rounded border" style={{ backgroundColor: currentPreset.theme.colors.semantic.background.primary }} title="Primary BG"/>
              <div className="w-12 h-12 rounded border" style={{ backgroundColor: currentPreset.theme.colors.semantic.background.secondary }} title="Secondary BG"/>
              {currentPreset.theme.colors.semantic.background.tertiary && (<div className="w-12 h-12 rounded border" style={{ backgroundColor: currentPreset.theme.colors.semantic.background.tertiary }} title="Tertiary BG"/>)}
            </div>
          </div>
        </Card>)}
    </div>);
}
/**
 * Compact Theme Switcher for headers/toolbars
 */
export function CompactThemeSwitcher() {
    var _a = useState(function () {
        return localStorage.getItem('theme-id') || 'cosmic-industrial';
    }), currentThemeId = _a[0], setCurrentThemeId = _a[1];
    var handleThemeChange = function (themeId) {
        var preset = themePresets.find(function (p) { return p.id === themeId; });
        if (preset) {
            applyTheme(preset.theme);
            setCurrentThemeId(themeId);
            localStorage.setItem('theme-id', themeId);
        }
    };
    return (<Select value={currentThemeId} onValueChange={handleThemeChange}>
      <SelectTrigger className="w-[180px]">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {themePresets.map(function (preset) { return (<SelectItem key={preset.id} value={preset.id}>
            {preset.name}
          </SelectItem>); })}
      </SelectContent>
    </Select>);
}
export function ThemePreviewCard(_a) {
    var preset = _a.preset, isActive = _a.isActive, onSelect = _a.onSelect;
    return (<Card className={"p-4 cursor-pointer transition-all hover:shadow-lg ".concat(isActive ? 'ring-2 ring-primary' : '')} onClick={onSelect}>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">{preset.name}</h3>
          {isActive && (<span className="text-xs bg-primary text-primary-foreground px-2 py-1 rounded">
              Active
            </span>)}
        </div>

        <p className="text-sm text-muted-foreground">{preset.description}</p>

        {/* Color swatches */}
        <div className="flex gap-1">
          <div className="w-8 h-8 rounded" style={{ backgroundColor: preset.theme.colors.brand.primary }}/>
          <div className="w-8 h-8 rounded" style={{ backgroundColor: preset.theme.colors.brand.secondary }}/>
          <div className="w-8 h-8 rounded" style={{ backgroundColor: preset.theme.colors.brand.accent }}/>
          <div className="w-8 h-8 rounded" style={{ backgroundColor: preset.theme.colors.status.success }}/>
          <div className="w-8 h-8 rounded" style={{ backgroundColor: preset.theme.colors.status.warning }}/>
        </div>

        <Button variant={isActive ? "default" : "outline"} size="sm" className="w-full">
          {isActive ? 'Current Theme' : 'Apply Theme'}
        </Button>
      </div>
    </Card>);
}
//# sourceMappingURL=ThemeSwitcher.jsx.map