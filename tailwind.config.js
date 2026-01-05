/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./products/**/*.py",
  ],
  darkMode: 'media',
  theme: {
    extend: {
      colors: {
        slate: require('tailwindcss/colors').slate,
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
    },
  },
  plugins: [],
};
