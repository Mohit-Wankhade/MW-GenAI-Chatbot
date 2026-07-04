 /** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: "#171717",
          panel: "#2B2D31",
          accent: "#C8A97E",
          accentHover: "#B7946A",
          cream: "#E2D9CB",
        },
      },
      boxShadow: {
        soft: "0 18px 45px rgba(0, 0, 0, 0.25)",
      },
      borderRadius: {
        "2.5xl": "1.25rem",
      },
    },
  },
  plugins: [],
};