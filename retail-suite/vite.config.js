// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import svgLoader from 'vite-svg-loader'
import vuetify from 'vite-plugin-vuetify'
import path from 'path'
import Icons from 'unplugin-icons/vite'
import { fileURLToPath } from 'url'
import { dirname } from 'path'
import dotenv from 'dotenv'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)


dotenv.config({ path: path.resolve(__dirname, '.env') })

const BASE_URL  =  process.env.VITE_FRAPPE_URL_LOCAL
const SITE_NAME =  process.env.VITE_SOCKET_URL
const ENVTYPE = process.env.VITE_ENV || 'production'
const SOCKET_URL = process.env.VITE_SOCKET_URL


const isLocalDev = !!(ENVTYPE === 'development')


export default defineConfig({
  optimizeDeps: {
    include: ['feather-icons', 'highlight.js/lib/core', 'interactjs', 'qz-tray'],
    exclude: ['@iconify-json/lucide'],
    esbuildOptions: {
      plugins: [{
        name: 'ignore-icons',
        setup(build) {
          build.onResolve({ filter: /^~icons\// }, args => ({
            path: args.path, namespace: 'ignore-icons',
          }))
          build.onLoad({ filter: /.*/, namespace: 'ignore-icons' }, () => ({
            contents: 'export default {}', loader: 'js',
          }))
        }
      }]
    }
  },

  plugins: [
    vue(),
    vuetify({ autoImport: true }),
    svgLoader(),
    Icons({ compiler: 'vue3', autoInstall: true }),
  ],

  resolve: {
    alias: { '@': resolve(__dirname, 'src') },
  },

  server: {
    allowedHosts: true,
    port: 5173,
    host: '0.0.0.0',
    proxy: isLocalDev ? {
      "^/(app|api|assets|files|printview)": {
        target:              FRAPPE_URL,
        changeOrigin:        true,
        ws:                  true,
        secure:              false,
      },
      '/socket.io': {
        target:          SOCKET_URL,
        ws:              true,
        changeOrigin:    true,
        secure:          false,
        rewriteWsOrigin: true,
        headers:         { 'x-frappe-site-name': SITE_NAME },
      },
    } : undefined,
  },

  build: {
    outDir: path.resolve(__dirname, '../retail/public/retail_suite'),
    emptyOutDir: true,
    assetsDir:   'assets',
    rollupOptions: {
      external: (id) => id.startsWith('~icons/'),
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          utils:  ['idb'],
        }
      }
    }
  }
})
