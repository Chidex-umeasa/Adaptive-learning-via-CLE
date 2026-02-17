import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        load: {
          low: "#22c55e",
          med: "#f59e0b",
          high: "#ef4444",
        },
      },
    },
  },
  plugins: [],
};

export default config;
