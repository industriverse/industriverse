/**
 * Rollup Configuration for Widget Build System
 * Week 8: White-Label Platform - Phase 4 Final
 * 
 * Builds standalone widget bundles for CDN distribution
 * Each widget is bundled separately for optimal loading
 */

import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import typescript from '@rollup/plugin-typescript';
import terser from '@rollup/plugin-terser';
import postcss from 'rollup-plugin-postcss';

const production = !process.env.ROLLUP_WATCH;

// Widget entry points
const widgets = [
  'wallet-orb',
  'proof-ticker',
  'capsule-card',
  'energy-gauge',
  'utid-badge',
  'ami-pulse',
  'shadow-twin',
];

// Base configuration for all widgets
const baseConfig = {
  plugins: [
    resolve({
      browser: true,
      extensions: ['.js', '.ts'],
    }),
    commonjs(),
    typescript({
      tsconfig: './tsconfig.json',
      declaration: false,
      declarationMap: false,
    }),
    postcss({
      extract: false,
      inject: true,
      minimize: production,
    }),
    production && terser({
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
      format: {
        comments: false,
      },
    }),
  ].filter(Boolean),
  external: [],
};

// Generate individual widget bundles
const widgetConfigs = widgets.map((widget) => ({
  ...baseConfig,
  input: `client/src/widgets/${widget}.ts`,
  output: [
    {
      file: `dist/widgets/${widget}.js`,
      format: 'iife',
      name: `IV${widget.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('')}`,
      sourcemap: !production,
    },
    {
      file: `dist/widgets/${widget}.esm.js`,
      format: 'es',
      sourcemap: !production,
    },
  ],
}));

// Main widget loader bundle
const loaderConfig = {
  ...baseConfig,
  input: 'client/src/widgets/loader.ts',
  output: {
    file: 'dist/widgets/iv-widgets.js',
    format: 'iife',
    name: 'IVWidgets',
    sourcemap: !production,
  },
};

export default [...widgetConfigs, loaderConfig];
