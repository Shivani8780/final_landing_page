module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js"  // Add if using JavaScript
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6', // blue-500
        secondary: '#6B7280' // gray-500
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'), // If using form styles
    require('@tailwindcss/typography') // If using prose
  ],
}