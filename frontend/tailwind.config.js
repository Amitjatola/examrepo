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
                "primary": "#3858fa",
                "background-light": "#f5f7fb",
                "background-dark": "#0f1323",
                "card-dark": "#181d35",
                "border-dark": "#2f396a",
                "landing-primary": "#3858fa",
                "landing-bg-light": "#f5f7fb",
                "landing-bg-dark": "#0f1323",
                "landing-surface": "#181d35",
                "landing-border": "#2f396a",
            },
            fontFamily: {
                "sans": ["Lexend", "sans-serif"], // Set Lexend as default sans
                "display": ["Lexend", "sans-serif"],
                "lexend": ["Lexend", "sans-serif"],
            },
            backgroundImage: {
                'glow': 'conic-gradient(from 180deg at 50% 50%, #2a8af6 0deg, #a853ba 180deg, #e92a67 360deg)',
            },
            borderRadius: { "DEFAULT": "0.25rem", "lg": "0.5rem", "xl": "0.75rem", "full": "9999px" },
        },
    },
    plugins: [],
}
