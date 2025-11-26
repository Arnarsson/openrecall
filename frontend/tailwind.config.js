/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sidebar: {
          DEFAULT: '#1e2235',
          hover: '#2a2f45',
          active: '#3b4261',
          border: '#363c55',
        },
        brand: {
          primary: '#6366f1',
          secondary: '#8b5cf6',
        },
      },
    },
  },
  plugins: [],
}
