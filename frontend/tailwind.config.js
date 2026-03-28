/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,jsx}',
    './components/**/*.{js,jsx}',
    './hooks/**/*.{js,jsx}',
    './services/**/*.{js,jsx}',
    './styles/**/*.css'
  ],
  theme: {
    extend: {
      colors: {
        ink: '#0f172a',
        neon: '#22d3ee',
        mint: '#34d399'
      },
      fontFamily: {
        gallaudet: ['Gallaudet', 'ui-sans-serif', 'system-ui', 'sans-serif']
      }
    }
  },
  plugins: []
};