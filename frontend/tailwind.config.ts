import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18212f",
        coast: "#0f766e",
        clay: "#a16207",
        mist: "#f6f7f4"
      }
    }
  },
  plugins: []
};

export default config;
