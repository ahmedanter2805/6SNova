/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        aura: {
          void: "#07090E",
          dark: "#0B0E17",
          card: "#121624",
          cardHover: "#171D30",
          border: "rgba(255, 255, 255, 0.08)",
          purple: "#8B5CF6",
          cyan: "#06B6D4",
          emerald: "#10B981",
          amber: "#F59E0B",
          rose: "#F43F5E"
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        headline: ['Space Grotesk', 'sans-serif']
      }
    },
  },
  plugins: [],
}
