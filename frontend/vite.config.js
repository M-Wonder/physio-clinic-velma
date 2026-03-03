import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ command }) => {
  const isDev = command === 'serve'

  return {
    plugins: [react()],

    server: {
      port: 3030,
      host: '0.0.0.0',
      allowedHosts: [
        'localhost',
        '.ngrok-free.dev',
      ],
      // Proxy only runs during local dev (npm run dev)
      // On Render, VITE_API_URL points directly to the backend URL — no proxy needed
      ...(isDev && {
        proxy: {
          '/api': {
            target: 'http://backend:8080',
            changeOrigin: true,
            secure: false,
          },
        },
      }),
    },

    build: {
      outDir: 'dist',
      sourcemap: false,
    },
  }
})