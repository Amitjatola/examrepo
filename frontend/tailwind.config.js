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
                "primary": "#3858fa", // Landing primary
                "background-light": "#f5f6f8",
                "background-dark": "#0f1323", // Landing bg dark
                "card-dark": "#181d35", // Landing surface
                "border-dark": "#2f396a", // Landing border
                // Keeping landing-* aliases for backward compatibility if needed, but mapping them to the above is cleaner
                "landing-primary": "#3858fa",
                "landing-bg-light": "#f5f6f8",
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
