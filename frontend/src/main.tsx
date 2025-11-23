import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { registerSW } from 'virtual:pwa-register'

// Initialize monitoring asynchronously to not block app startup
setTimeout(() => {
  try {
    import('./services/sentry').then(({ initSentry }) => {
      initSentry()
    })
  } catch (error) {
    console.warn('Failed to load Sentry:', error)
  }

  try {
    import('./services/logger').then((module) => {
      const logger = module.default
      logger.info('Application started', {
        environment: import.meta.env.MODE,
        version: import.meta.env.VITE_APP_VERSION || '0.1.0',
      })
    })
  } catch (error) {
    console.warn('Failed to load logger:', error)
  }
}, 100)

// Register service worker
const updateSW = registerSW({
  onNeedRefresh() {
    if (confirm('New content available. Reload?')) {
      updateSW(true)
    }
  },
  onOfflineReady() {
    console.log('App ready to work offline')
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
