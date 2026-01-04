/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html", // برای اپلیکیشن‌های جنگو
    "./static/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}