/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // 🎨 Bordas Arredondadas Modernas
      borderRadius: {
        'card': '20px',
        'button': '12px',
        'input': '12px',
        'badge': '10px',
        'modal': '24px',
        'avatar': '16px',
      },
      
      // 💎 Sistema de Sombras em Camadas (Elevation)
      boxShadow: {
        // Sombras suaves
        'soft': '0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02)',
        'soft-lg': '0 4px 12px rgba(0, 0, 0, 0.06), 0 2px 4px rgba(0, 0, 0, 0.03)',
        
        // Cards
        'card': '0 4px 20px rgba(0, 0, 0, 0.08), 0 2px 6px rgba(0, 0, 0, 0.04)',
        'card-hover': '0 8px 32px rgba(0, 0, 0, 0.12), 0 4px 12px rgba(0, 0, 0, 0.08)',
        'card-dark': '0 4px 20px rgba(0, 0, 0, 0.3), 0 2px 6px rgba(0, 0, 0, 0.2)',
        
        // Botões
        'button': '0 2px 8px rgba(19, 81, 180, 0.15), 0 1px 3px rgba(19, 81, 180, 0.1)',
        'button-hover': '0 4px 16px rgba(19, 81, 180, 0.25), 0 2px 6px rgba(19, 81, 180, 0.15)',
        
        // Float/Modal
        'float': '0 12px 40px rgba(0, 0, 0, 0.12), 0 6px 16px rgba(0, 0, 0, 0.08)',
        'float-dark': '0 12px 40px rgba(0, 0, 0, 0.6), 0 6px 16px rgba(0, 0, 0, 0.4)',
        
        // Glow effects
        'glow-blue': '0 0 24px rgba(19, 81, 180, 0.3)',
        'glow-green': '0 0 24px rgba(16, 185, 129, 0.3)',
        
        // Inner
        'inner-soft': 'inset 0 2px 4px rgba(0, 0, 0, 0.06)',
        'inner-glow': 'inset 0 0 20px rgba(255, 255, 255, 0.05)',
      },

      // ⚡ Transições Suaves
      transitionDuration: {
        '400': '400ms',
      },
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },

      colors: {
        // Paleta Primary Moderna (Azul sofisticado)
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
          DEFAULT: '#3b82f6'
        },

        // Cores Semânticas Refinadas
        danger: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
          DEFAULT: '#ef4444'
        },
        success: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
          DEFAULT: '#10b981'
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
          DEFAULT: '#f59e0b'
        },
        info: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          DEFAULT: '#3b82f6'
        },

        // Status de Protocolos - Ouvidoria
        ouvidoria: {
          'triagem': '#3b82f6',           // Azul
          'analise': '#8b5cf6',           // Roxo
          'encaminhado': '#f59e0b',       // Âmbar
          'respondido': '#10b981',        // Verde
          'arquivado': '#6b7280',         // Cinza
        },

        // Status de Protocolos - Zeladoria
        zeladoria: {
          'triagem-ia': '#3b82f6',        // Azul
          'validacao': '#8b5cf6',         // Roxo
          'aguardando-equipe': '#f59e0b', // Âmbar
          'em-deslocamento': '#f59e0b',   // Âmbar
          'em-execucao': '#14b8a6',       // Teal
          'concluido': '#10b981',         // Verde
          'nao-procedente': '#6b7280',    // Cinza
        },

        // Tipos de Manifestação
        manifestacao: {
          'denuncia': '#ef4444',          // Vermelho
          'reclamacao': '#f59e0b',        // Âmbar
          'sugestao': '#3b82f6',          // Azul
          'elogio': '#10b981',            // Verde
        },

        // Níveis de Urgência (IA)
        urgencia: {
          'baixa': '#10b981',             // Verde
          'media': '#f59e0b',             // Âmbar
          'alta': '#ef4444',              // Vermelho
          'critica': '#dc2626',           // Vermelho escuro
        },

        // Compatibilidade Gov.br
        'gov-blue': {
          'warm': '#1351B4',
          'vivid': '#155BCB',
          'deep': '#0C326F',
        },
        'gov-green': {
          'cool': '#168821',
          'vivid': '#1B7D28',
        },
        'gov-yellow': {
          'vivid': '#FFCD07',
        },
        'gov-gray': {
          'light': '#F8F8F8',
          'medium': '#E5E5E5',
          'dark': '#333333',
        }
      },
      
      fontFamily: {
        'sans': ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      
      // Backdrop blur para glassmorphism
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [
    function ({ addVariant }) {
      addVariant('high-contrast', '.high-contrast &')
    },
  ],
}
