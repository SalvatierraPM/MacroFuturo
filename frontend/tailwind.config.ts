import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "#090b1a",
        primary: "#4ade80",
        accent: "#60a5fa"
      }
    }
  },
  plugins: []
};

export default config;
