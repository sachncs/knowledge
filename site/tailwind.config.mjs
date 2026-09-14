/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{astro,html,js,jsx,ts,tsx,md,mdx,svelte,vue}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        ink: {
          50: "#F7F8FA",
          100: "#EEF0F4",
          200: "#DDE1E9",
          300: "#BCC3D1",
          400: "#8B95A8",
          500: "#5C6678",
          600: "#3F485B",
          700: "#2A3142",
          800: "#1A1F2D",
          900: "#0E121C",
          950: "#070A12",
        },
        canvas: {
          light: "#FAFBFC",
          dark: "#0A0D14",
        },
        accent: {
          50: "#F1F3FF",
          100: "#E1E5FF",
          200: "#C4CCFF",
          300: "#9AA8FF",
          400: "#7C8BFF",
          500: "#5B6BF2",
          600: "#4451D9",
          700: "#3A45B8",
          800: "#2F3895",
          900: "#252C75",
          950: "#161B4D",
        },
        mint: {
          400: "#5EEAD4",
          500: "#14B8A6",
          600: "#0D9488",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
        display: [
          "Inter Display",
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "sans-serif",
        ],
        mono: [
          "JetBrains Mono",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          "monospace",
        ],
      },
      fontSize: {
        "display-xl": ["clamp(3rem, 7vw, 5.5rem)", { lineHeight: "1.02", letterSpacing: "-0.04em", fontWeight: "600" }],
        "display-lg": ["clamp(2.25rem, 5vw, 3.75rem)", { lineHeight: "1.06", letterSpacing: "-0.035em", fontWeight: "600" }],
        "display-md": ["clamp(1.75rem, 3.5vw, 2.5rem)", { lineHeight: "1.1", letterSpacing: "-0.03em", fontWeight: "600" }],
      },
      letterSpacing: {
        tightest: "-0.045em",
        tighter: "-0.035em",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(91,107,242,0.18), 0 12px 48px -16px rgba(91,107,242,0.35)",
        soft: "0 1px 2px rgba(15,17,21,0.04), 0 8px 24px -8px rgba(15,17,21,0.12)",
        elevated: "0 24px 64px -24px rgba(15,17,21,0.25), 0 2px 6px rgba(15,17,21,0.04)",
        ring: "0 0 0 1px rgba(15,17,21,0.06), 0 1px 2px rgba(15,17,21,0.04)",
      },
      backgroundImage: {
        "grid-fade":
          "linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.04) 50%, transparent 100%)",
        "noise":
          "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.045 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>\")",
      },
      animation: {
        "fade-up": "fadeUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) both",
        "fade-in": "fadeIn 0.7s cubic-bezier(0.16, 1, 0.3, 1) both",
        "shimmer": "shimmer 2.4s linear infinite",
        "float": "float 8s ease-in-out infinite",
        "orbit": "orbit 32s linear infinite",
        "pulse-soft": "pulseSoft 3.2s ease-in-out infinite",
        "gradient-x": "gradientX 12s ease infinite",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-8px)" },
        },
        orbit: {
          "0%": { transform: "rotate(0deg)" },
          "100%": { transform: "rotate(360deg)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "0.5" },
          "50%": { opacity: "1" },
        },
        gradientX: {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
      },
      transitionTimingFunction: {
        smooth: "cubic-bezier(0.16, 1, 0.3, 1)",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};