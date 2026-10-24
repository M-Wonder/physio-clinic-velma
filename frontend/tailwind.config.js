/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        // Neuromotion brand palette, taken from the clinic logo.
        // To re-theme the whole site, change these three scales only.
        brand: {   // navy — primary
          50: '#eef3fa', 100: '#dbe5f4', 200: '#b7cbe9', 300: '#8aa9d6', 400: '#5c82bd',
          500: '#3a62a0', 600: '#264b82', 700: '#1b3a68', 800: '#142d52', 900: '#0d1f3a',
        },
        accent: {  // maroon — highlights
          50: '#fbeef0', 100: '#f6d9de', 500: '#a82a40', 600: '#8f1f33', 700: '#761828',
        },
        gold: {    // gold — details on dark backgrounds
          300: '#e3c577', 400: '#d4ab53', 500: '#c4953a', 600: '#a67a28',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn:  { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        slideUp: { '0%': { transform: 'translateY(10px)', opacity: '0' },
                   '100%': { transform: 'translateY(0)', opacity: '1' } },
      },
    },
  },
  plugins: [],
}
