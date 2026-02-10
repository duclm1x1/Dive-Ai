/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'dive-primary': '#00d9ff',
                'dive-secondary': '#7c3aed',
                'dive-accent': '#f59e0b',
                'dive-bg': '#0a0e27',
                'dive-surface': '#151933',
                'dive-surface-light': '#1e2440',
            },
            animation: {
                'glow': 'glow 2s ease-in-out infinite alternate',
                'slide-up': 'slideUp 0.5s ease-out',
                'fade-in': 'fadeIn 0.3s ease-in',
            },
            keyframes: {
                glow: {
                    '0%': { boxShadow: '0 0 5px rgba(0, 217, 255, 0.5), 0 0 10px rgba(0, 217, 255, 0.3)' },
                    '100%': { boxShadow: '0 0 20px rgba(0, 217, 255, 0.8), 0 0 30px rgba(0, 217, 255, 0.5)' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(20px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
            },
        },
    },
    plugins: [],
}
