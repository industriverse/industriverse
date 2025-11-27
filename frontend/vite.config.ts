import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@shared": path.resolve(__dirname, "./src/shared"),
    },
  },
  server: {
    proxy: {
      '/api/v1/idf': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/v1\/idf/, ''),
      },
      '/api/v1': {
        target: 'http://localhost:8000', // Fallback or Bridge API if running there
        changeOrigin: true,
      }
    }
  }
})
