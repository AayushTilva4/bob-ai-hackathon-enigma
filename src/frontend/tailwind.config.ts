import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        harbor: {
          bg: "#080c16",
          panel: "#0f172a",
          card: "#131e36",
          border: "#1e2d4d",
          accent: "#06b6d4",
          "accent-glow": "#0891b2",
          cyan: "#22d3ee",
          blue: "#3b82f6",
          success: "#10b981",
          warning: "#f59e0b",
          danger: "#ef4444",
          text: "#e2e8f0",
          muted: "#94a3b8",
        },
      },
      fontFamily: {
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          "Liberation Mono",
          "Courier New",
          "monospace",
        ],
      },
    },
  },
  plugins: [],
};
export default config;
