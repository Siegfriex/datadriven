/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./features/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./App.tsx",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'Noto Sans KR', 'sans-serif'],
        serif: ['Playfair Display', 'Noto Serif KR', 'serif'],
      },
      colors: {
        // Deep Dark Theme (Arario Style)
        bg: {
          DEFAULT: '#050505',
          panel: 'rgba(10, 10, 10, 0.8)',
          overlay: 'rgba(0, 0, 0, 0.7)',
        },
        brand: {
          DEFAULT: '#ffffff', // 미니멀리즘: 화이트가 브랜드 컬러
          accent: '#3b82f6', // 필요시 사용할 포인트 컬러 (파랑)
        },
        border: {
          light: 'rgba(255, 255, 255, 0.1)',
          medium: 'rgba(255, 255, 255, 0.2)',
        },
        text: {
          primary: '#ffffff',
          secondary: '#a1a1aa', // gray-400
          tertiary: '#71717a', // gray-500
        }
      },
      backdropBlur: {
        xs: '2px',
      },
      gridTemplateColumns: {
        '12': 'repeat(12, minmax(0, 1fr))', // 마스터 그리드용
      }
    },
  },
  plugins: [],
}
