import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

const catalogoServicosPattern =
  /^https?:\/\/[^/]+\/api\/v1\/catalogo-servicos\/?(\?.*)?$/i

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      strategies: 'generateSW',
      registerType: 'prompt',
      injectRegister: false,
      includeAssets: [
        'favicon.png',
        'favicon.ico',
        'robots.txt',
        'pwa-192x192.png',
        'pwa-512x512.png',
        'maskable-icon-512x512.png',
        'apple-touch-icon-180x180.png'
      ],
      manifest: {
        name: 'M.Ouve - Ouvidoria da Prefeitura Municipal de Mogi das Cruzes',
        short_name: 'M.Ouve',
        description: 'Plataforma inteligente de zeladoria e ouvidoria.',
        theme_color: '#0f172a',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/',
        scope: '/',
        lang: 'pt-BR',
        icons: [
          {
            src: '/pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: '/pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: '/maskable-icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable'
          },
          {
            src: '/apple-touch-icon-180x180.png',
            sizes: '180x180',
            type: 'image/png',
            purpose: 'any'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2,webmanifest}'],
        importScripts: ['push-sw.js'],
        navigateFallback: 'index.html',
        cleanupOutdatedCaches: true,
        runtimeCaching: [
          {
            urlPattern: catalogoServicosPattern,
            handler: 'StaleWhileRevalidate',
            method: 'GET',
            options: {
              cacheName: 'api-catalogo-servicos',
              expiration: {
                maxEntries: 4,
                maxAgeSeconds: 60 * 60 * 24 * 30
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      },
      devOptions: {
        enabled: false
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    host: true
  }
})
