/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f5f7fa',
          100: '#e4e8ee',
          200: '#c5d0de',
          300: '#9cb1c7',
          400: '#6d8cab',
          500: '#4b6c8f',
          600: '#3a5473',
          700: '#2f445d',
          800: '#28394e',
          900: '#233042',
          DEFAULT: '#2f445d'
        },
        accent: {
          orange: '#FF8A65',
          green: '#2ecc71',
          red: '#e74c3c',
          yellow: '#f1c40f',
          blue: '#3498db'
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'sans-serif'],
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
}
