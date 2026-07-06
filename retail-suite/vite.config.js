// vite.config.js
import { defineConfig } from 'vite'
import { writeFileSync } from 'fs'
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
const BASE_URL   = process.env.VITE_FRAPPE_URL
const SITE_NAME  = process.env.SITE_NAME
const SOCKET_URL = process.env.VITE_SOCKET_URL
const ENVTYPE    = process.env.MODE || 'production'
console.log("ENVTYPE",ENVTYPE)
console.log("SOCKET_URL",SOCKET_URL)
console.log("BASE_URL",BASE_URL)
console.log("SITE_NAME",SITE_NAME)


const isLocalDev = !!(ENVTYPE === 'development')

function versionPlugin() {
  return {
    name: 'generate-version-file',
    closeBundle() {
      const buildVersion = process.env.RETAIL_BUILD_VERSION || Date.now().toString()
      const versionData = {
        version: buildVersion,
        timestamp: new Date().toISOString(),
        buildDate: new Date().toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        }),
      }

      const outputPath = resolve(__dirname, '../retail/public/retail_suite/version.json')
      writeFileSync(outputPath, JSON.stringify(versionData, null, 2))
      console.log(`✓ Generated version.json: ${buildVersion}`)
    },
  }
}

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
    versionPlugin(),
  ],

  resolve: {
    alias: { '@': resolve(__dirname, 'src') },
  },

  server: {
    allowedHosts: true,
    port: 5173,
    host: BASE_URL,
    proxy: isLocalDev ? {
      "^/(app|api|assets|files|printview)": {
        target:              BASE_URL,
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
