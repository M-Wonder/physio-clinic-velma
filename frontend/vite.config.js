import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3030,
    host: '0.0.0.0',
    allowedHosts: [
       'somatologic-misrepresentative-sheba.ngrok-free.dev',
      '.ngrok-free.dev'  // This allows all ngrok-free.dev subdomains
    ],
    proxy: {
      // All /api requests forwarded to Django backend container
      '/api': {
        target: env.VITE_API_URL || 'http://backend:8080',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
     rollupOptions: {
        output: {
          manualChunks: undefined,
        },
  },
}})